"""MCP 工具实现（首批 12 类，危险工具拆为 preview/confirm 两段）。

性能约定（与 BrickCore 落地设计对齐）：
- list_* 只查轻量字段（only/values）+ limit/offset 分页 + 60s 缓存（命中 < 20ms）
- 读工具同步即时返回；写工具 preview 同步、confirm 后异步执行返回 ID
- 每次调用写 McpCallLog（写失败不阻断响应），7 天日志节流清理
"""
import json
import logging
import time

from django.core.cache import cache
from django.db import close_old_connections, connection

from mcp.server.fastmcp import Context
from mcp.server.fastmcp.exceptions import ToolError

from . import actions as act
from .actions import args_digest
from .auth import authenticate_headers, current_user_id
from .confirm import (ConfirmError, consume_pending, create_preview,
                      query_approval_status, verify_pending)
from .models import McpCallLog

logger = logging.getLogger(__name__)

#: list 类工具缓存 TTL（秒）：短 TTL 兼顾性能与数据新鲜度
LIST_CACHE_TTL = 60
#: 分页上限，防止 Agent 拉全表
MAX_LIMIT = 100


# --------------------------------------------------------------------- #
# 公共辅助
# --------------------------------------------------------------------- #

def _resolve_user(ctx: Context):
    """从 MCP 请求头解析当前用户（中间件已强制鉴权，此处落到具体用户）。"""
    try:
        request = ctx.request_context.request
        if request is not None:
            headers = {k.lower(): v for k, v in request.headers.items()}
            user = authenticate_headers(headers)
            if user is not None:
                return user
    except Exception:  # noqa: BLE001 - 兜底走 contextvar
        pass
    user_id = current_user_id.get()
    if user_id:
        from django.contrib.auth import get_user_model
        user = get_user_model().objects.filter(id=user_id, is_active=True).first()
        if user:
            return user
    raise ToolError('未认证：请携带 Authorization: Bearer <JWT> 或 x-mcp-api-key 头')


def _resolve_client_name(ctx: Context) -> str:
    """从请求头提取客户端标识（User-Agent），失败返回空串。"""
    try:
        request = ctx.request_context.request
        if request is not None:
            headers = {k.lower(): v for k, v in request.headers.items()}
            return (headers.get('user-agent') or '')[:100]
    except Exception:  # noqa: BLE001
        pass
    return ''


def _clamp_page(limit: int, offset: int):
    limit = max(1, min(int(limit or 20), MAX_LIMIT))
    offset = max(0, int(offset or 0))
    return limit, offset


def _cache_get_or_set(key: str, builder):
    """60s 缓存包装；缓存不可用时直接回源，不影响正确性。"""
    try:
        hit = cache.get(key)
        if hit is not None:
            return json.loads(hit)
    except Exception:  # noqa: BLE001
        pass
    data = builder()
    try:
        cache.set(key, json.dumps(data, ensure_ascii=False, default=str), LIST_CACHE_TTL)
    except Exception:  # noqa: BLE001
        pass
    return data


def _log_call(user, tool_name: str, arguments: dict, started: float,
              error: str = '', status: str = 'success', client_name: str = ''):
    """写调用日志（含耗时/脱敏参数/客户端）；失败不阻断响应，并节流清理 7 天前日志。"""
    try:
        McpCallLog.objects.create(
            user=user if user and getattr(user, 'pk', None) else None,
            tool_name=tool_name[:100],
            args_digest=args_digest(arguments or {}),
            args_brief=act.mask_sensitive_args(arguments or {}),
            client_name=client_name[:100],
            status=status,
            duration_ms=int((time.perf_counter() - started) * 1000),
            error=(error or '')[:2000],
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug('MCP 调用日志写入失败: %s', exc)
    try:
        if cache.get('mcp:log_cleanup_at') is None:
            from datetime import timedelta
            from django.utils import timezone
            McpCallLog.objects.filter(
                created_at__lt=timezone.now() - timedelta(days=7)).delete()
            cache.set('mcp:log_cleanup_at', '1', 3600)
    except Exception:  # noqa: BLE001
        pass


def _run_tool(ctx: Context, tool_name: str, arguments: dict, fn):
    """统一包装：鉴权 → 计时 → 执行 → 日志；错误转 ToolError。

    仅在非事务上下文中关闭旧连接：Django TestCase 的 atomic 块内关闭连接会
    破坏测试事务，使后续 ORM 查询失败被 _verify_jwt 吞掉而误判为「未认证」。
    """
    started = time.perf_counter()
    if not connection.in_atomic_block:
        close_old_connections()
    user = _resolve_user(ctx)
    client_name = _resolve_client_name(ctx)
    try:
        result = fn(user)
        _log_call(user, tool_name, arguments, started, client_name=client_name)
        return result
    except ToolError:
        raise
    except ConfirmError as e:
        _log_call(user, tool_name, arguments, started, error=str(e),
                  status='denied', client_name=client_name)
        raise ToolError(str(e)) from e
    except act.McpActionError as e:
        _log_call(user, tool_name, arguments, started, error=str(e),
                  status='error', client_name=client_name)
        raise ToolError(str(e)) from e
    except Exception as e:  # noqa: BLE001
        logger.exception('MCP 工具 %s 执行异常', tool_name)
        _log_call(user, tool_name, arguments, started, error=str(e),
                  status='error', client_name=client_name)
        raise ToolError(f'{tool_name} 执行失败: {e}') from e
    finally:
        if not connection.in_atomic_block:
            close_old_connections()


# --------------------------------------------------------------------- #
# 读工具（同步即时返回，轻量字段 + 分页 + 60s 缓存）
# --------------------------------------------------------------------- #

def list_projects(ctx: Context, limit: int = 20, offset: int = 0) -> dict:
    """列出当前用户拥有或参与的测试项目（测试用例域）。

    返回 {total, items: [{id, name, status, created_at}]}，
    支持 limit/offset 分页（limit 上限 100），结果带 60 秒缓存。
    API/UI/压测项目请分别使用 list_api_requests/list_ui_cases/list_perf_scenes 的 project_id 来源工具。
    """
    limit, offset = _clamp_page(limit, offset)

    def run(user):
        key = f'mcp:tool:list_projects:{user.id}:{limit}:{offset}'

        def build():
            qs = act.accessible_projects(user).order_by('-created_at')
            total = qs.count()
            rows = list(qs[offset:offset + limit].values('id', 'name', 'status', 'created_at'))
            return {'total': total, 'items': rows}
        return _cache_get_or_set(key, build)

    return _run_tool(ctx, 'list_projects', {'limit': limit, 'offset': offset}, run)


def list_testcases(ctx: Context, project_id: int, limit: int = 20, offset: int = 0) -> dict:
    """列出指定项目下的功能测试用例（仅轻量字段，不含步骤与描述大字段）。

    返回 {total, items: [{id, title, priority, status, test_type, created_at}]}，
    需对该项目有访问权限，支持 limit/offset 分页（上限 100），60 秒缓存。
    """
    limit, offset = _clamp_page(limit, offset)

    def run(user):
        from apps.testcases.models import TestCase
        if not act.accessible_projects(user).filter(id=project_id).exists():
            raise ToolError(f'项目 {project_id} 不存在或无权限')
        key = f'mcp:tool:list_testcases:{user.id}:{project_id}:{limit}:{offset}'

        def build():
            qs = TestCase.objects.filter(project_id=project_id).order_by('-created_at')
            total = qs.count()
            rows = list(qs.defer('description', 'preconditions', 'steps', 'expected_result')
                        [offset:offset + limit].values(
                            'id', 'title', 'priority', 'status', 'test_type', 'created_at'))
            return {'total': total, 'items': rows}
        return _cache_get_or_set(key, build)

    return _run_tool(ctx, 'list_testcases',
                     {'project_id': project_id, 'limit': limit, 'offset': offset}, run)


def list_api_requests(ctx: Context, project_id: int, limit: int = 20, offset: int = 0) -> dict:
    """列出指定 API 测试项目下的接口请求。

    返回 {total, items: [{id, name, method, url, request_type}]}，
    按目录顺序排序，需对该 API 项目有访问权限，支持 limit/offset 分页（上限 100），60 秒缓存。
    """
    limit, offset = _clamp_page(limit, offset)

    def run(user):
        from apps.api_testing.models import ApiRequest
        if not act.accessible_api_projects(user).filter(id=project_id).exists():
            raise ToolError(f'API 项目 {project_id} 不存在或无权限')
        key = f'mcp:tool:list_api_requests:{user.id}:{project_id}:{limit}:{offset}'

        def build():
            qs = ApiRequest.objects.filter(collection__project_id=project_id).order_by('order', 'id')
            total = qs.count()
            rows = list(qs.only('id', 'name', 'method', 'url', 'request_type')
                        [offset:offset + limit].values('id', 'name', 'method', 'url', 'request_type'))
            return {'total': total, 'items': rows}
        return _cache_get_or_set(key, build)

    return _run_tool(ctx, 'list_api_requests',
                     {'project_id': project_id, 'limit': limit, 'offset': offset}, run)


def list_ui_cases(ctx: Context, project_id: int, limit: int = 20, offset: int = 0) -> dict:
    """列出指定 UI 自动化项目下的测试用例。

    返回 {total, items: [{id, name, status, priority, created_at}]}，
    需对该 UI 项目有访问权限，支持 limit/offset 分页（上限 100），60 秒缓存。
    """
    limit, offset = _clamp_page(limit, offset)

    def run(user):
        from apps.ui_automation.models import TestCase as UiCase
        if not act.accessible_ui_projects(user).filter(id=project_id).exists():
            raise ToolError(f'UI 项目 {project_id} 不存在或无权限')
        key = f'mcp:tool:list_ui_cases:{user.id}:{project_id}:{limit}:{offset}'

        def build():
            qs = UiCase.objects.filter(project_id=project_id).order_by('-created_at')
            total = qs.count()
            rows = list(qs.only('id', 'name', 'status', 'priority', 'created_at')
                        [offset:offset + limit].values('id', 'name', 'status', 'priority', 'created_at'))
            return {'total': total, 'items': rows}
        return _cache_get_or_set(key, build)

    return _run_tool(ctx, 'list_ui_cases',
                     {'project_id': project_id, 'limit': limit, 'offset': offset}, run)


def list_perf_scenes(ctx: Context, project_id: int, limit: int = 20, offset: int = 0) -> dict:
    """列出指定压测项目下的压测场景。

    返回 {total, items: [{id, name, engine, enabled, created_at}]}，
    需对该压测项目有访问权限，支持 limit/offset 分页（上限 100），60 秒缓存。
    """
    limit, offset = _clamp_page(limit, offset)

    def run(user):
        from apps.perf_testing.models import PerfScenario
        if not act.accessible_perf_projects(user).filter(id=project_id).exists():
            raise ToolError(f'压测项目 {project_id} 不存在或无权限')
        key = f'mcp:tool:list_perf_scenes:{user.id}:{project_id}:{limit}:{offset}'

        def build():
            qs = PerfScenario.objects.filter(project_id=project_id).order_by('-created_at')
            total = qs.count()
            rows = list(qs.only('id', 'name', 'engine', 'enabled', 'created_at')
                        [offset:offset + limit].values('id', 'name', 'engine', 'enabled', 'created_at'))
            return {'total': total, 'items': rows}
        return _cache_get_or_set(key, build)

    return _run_tool(ctx, 'list_perf_scenes',
                     {'project_id': project_id, 'limit': limit, 'offset': offset}, run)


def get_report(ctx: Context, execution_id: int) -> dict:
    """获取指定压测执行的报告摘要（复用执行落库指标，不重新计算）。

    返回状态、SLA 结果、结论（verdict）及明细、汇总指标、时长，
    以及按请求维度的统计（总量/失败/错误率/平均响应/P95/TPS）。
    需对该压测执行所属项目有访问权限。
    """

    def run(user):
        from apps.perf_testing.models import PerfExecution, PerfRequestStat
        execution = PerfExecution.objects.filter(
            id=execution_id, project__in=act.accessible_perf_projects(user)
        ).first()
        if not execution:
            raise ToolError(f'压测执行 {execution_id} 不存在或无权限')
        stats = list(PerfRequestStat.objects.filter(execution_id=execution.id).values(
            'step_name', 'total', 'failed', 'error_rate',
            'avg_response_time', 'p95', 'tps'))
        return {
            'execution_id': execution.id,
            'execution_no': execution.execution_no,
            'status': execution.status,
            'sla_result': execution.sla_result,
            'verdict': execution.verdict,
            'verdict_details': execution.verdict_details or [],
            'summary': execution.summary or {},
            'duration': execution.duration,
            'report_url': execution.report_url or '',
            'stats': stats,
        }

    return _run_tool(ctx, 'get_report', {'execution_id': execution_id}, run)


def analyze_failure(ctx: Context, execution_id: int) -> dict:
    """压测失败 AI 分析：命中缓存即时返回，否则触发 Celery 异步分析。

    命中缓存返回 {status: 'completed', ...分析结果}；未命中时投递异步任务
    返回 {status: 'accepted', hint}，约 30 秒后再次调用本工具获取结果。
    依赖 Celery，不可用时报错并提示改用平台页面 SSE 分析入口。
    """

    def run(user):
        from apps.perf_testing.models import PerfExecution
        execution = PerfExecution.objects.filter(
            id=execution_id, project__in=act.accessible_perf_projects(user)
        ).first()
        if not execution:
            raise ToolError(f'压测执行 {execution_id} 不存在或无权限')

        cache_key = f'perf:ai_analysis:{execution.id}'
        cached = cache.get(cache_key)
        if cached:
            try:
                data = json.loads(cached)
                return {'status': 'completed', 'execution_id': execution.id, **data}
            except (TypeError, ValueError):
                pass

        from apps.perf_testing.tasks import analyze_perf_execution_task
        try:
            analyze_perf_execution_task.delay(execution.id)
        except Exception as e:  # noqa: BLE001 - Celery 不可用时给出明确指引
            raise ToolError(
                f'AI 分析任务投递失败（Celery 不可用: {e}），'
                f'可稍后重试或使用平台页面 SSE 分析入口') from e
        return {
            'status': 'accepted',
            'execution_id': execution.id,
            'hint': '分析已异步启动（约 30s），稍后再次调用本工具获取结果',
        }

    return _run_tool(ctx, 'analyze_failure', {'execution_id': execution_id}, run)


# --------------------------------------------------------------------- #
# 危险工具：preview 同步返回预览 + confirm_token；confirm 校验后异步执行
# --------------------------------------------------------------------- #

def preview_run_api_suite(ctx: Context, suite_id: int) -> dict:
    """预览执行 API 测试套件（危险操作第一步）。

    生成影响预览并返回 confirm_token（5 分钟有效），本步骤不执行任何套件。
    确认执行请调用 confirm_run_api_suite；开启人工审批时还需轮询 get_approval_status。
    """
    arguments = {'suite_id': suite_id}
    return _run_tool(ctx, 'preview_run_api_suite', arguments,
                     lambda user: create_preview('confirm_run_api_suite', arguments, user))


def confirm_run_api_suite(ctx: Context, confirm_token: str) -> dict:
    """确认执行 API 测试套件（危险操作第二步）。

    校验 preview_run_api_suite 返回的 confirm_token 后异步执行套件，返回执行 ID。
    令牌一次性消费且 5 分钟内有效；人工审批模式下返回 awaiting_approval，
    需轮询 get_approval_status 直至 approved/rejected/expired。
    """
    return _run_tool(ctx, 'confirm_run_api_suite', {'confirm_token': '<token>'},
                     lambda user: consume_pending(verify_pending(confirm_token, user), user))


def preview_run_ui_case(ctx: Context, case_id: int, engine: str = 'playwright',
                        browser: str = 'chrome', headless: bool = True) -> dict:
    """预览执行 UI 自动化用例（危险操作第一步）。

    生成影响预览并返回 confirm_token（5 分钟有效），本步骤不执行任何用例。
    可选执行引擎（playwright/selenium）、浏览器与 headless 模式；
    确认执行请调用 confirm_run_ui_case。
    """
    arguments = {'case_id': case_id, 'engine': engine, 'browser': browser, 'headless': headless}
    return _run_tool(ctx, 'preview_run_ui_case', arguments,
                     lambda user: create_preview('confirm_run_ui_case', arguments, user))


def confirm_run_ui_case(ctx: Context, confirm_token: str) -> dict:
    """确认执行 UI 自动化用例（危险操作第二步）。

    校验 preview_run_ui_case 返回的 confirm_token 后异步执行用例，返回执行 ID。
    令牌一次性消费且 5 分钟内有效；人工审批模式下返回 awaiting_approval，
    需轮询 get_approval_status。
    """
    return _run_tool(ctx, 'confirm_run_ui_case', {'confirm_token': '<token>'},
                     lambda user: consume_pending(verify_pending(confirm_token, user), user))


def preview_run_perf_scene(ctx: Context, scene_id: int) -> dict:
    """预览发起压测（危险操作第一步）。

    生成影响预览并返回 confirm_token（5 分钟有效），本步骤不产生任何压测流量；
    确认执行请调用 confirm_run_perf_scene。
    """
    arguments = {'scene_id': scene_id}
    return _run_tool(ctx, 'preview_run_perf_scene', arguments,
                     lambda user: create_preview('confirm_run_perf_scene', arguments, user))


def confirm_run_perf_scene(ctx: Context, confirm_token: str) -> dict:
    """确认发起压测（危险操作第二步）。

    校验 preview_run_perf_scene 返回的 confirm_token 后异步发起压测，返回执行 ID。
    令牌一次性消费且 5 分钟内有效；人工审批模式下返回 awaiting_approval，
    需轮询 get_approval_status。
    """
    return _run_tool(ctx, 'confirm_run_perf_scene', {'confirm_token': '<token>'},
                     lambda user: consume_pending(verify_pending(confirm_token, user), user))


def preview_create_testcase(ctx: Context, project_id: int, data: dict) -> dict:
    """预览创建功能测试用例（危险操作第一步）。

    生成影响预览并返回 confirm_token（5 分钟有效），本步骤不落库；
    确认创建请调用 confirm_create_testcase。

    data 结构：{title, description?, preconditions?, expected_result?,
    priority?, test_type?, steps?: [{action, expected}]}
    """
    arguments = {'project_id': project_id, 'data': data or {}}
    return _run_tool(ctx, 'preview_create_testcase', arguments,
                     lambda user: create_preview('confirm_create_testcase', arguments, user))


def confirm_create_testcase(ctx: Context, confirm_token: str) -> dict:
    """确认创建功能测试用例（危险操作第二步）。

    校验 preview_create_testcase 返回的 confirm_token 后创建用例，返回 testcase_id。
    令牌一次性消费且 5 分钟内有效；人工审批模式下返回 awaiting_approval，
    需轮询 get_approval_status。
    """
    return _run_tool(ctx, 'confirm_create_testcase', {'confirm_token': '<token>'},
                     lambda user: consume_pending(verify_pending(confirm_token, user), user))


def get_approval_status(ctx: Context, confirm_token: str) -> dict:
    """查询危险操作的人工审批状态（只读，供 Agent 轮询）

    人工审批模式下 confirm_* 返回 awaiting_approval 后，用同一
    confirm_token 反复调用本工具，直至返回 approved（附执行结果）/
    rejected / expired。
    """
    return _run_tool(ctx, 'get_approval_status', {'confirm_token': '<token>'},
                     lambda user: query_approval_status(confirm_token, user))


def get_ui_execution(ctx: Context, execution_id: int) -> dict:
    """查询 UI 自动化用例执行结果（confirm_run_ui_case 返回执行 ID 后轮询本工具）。

    返回执行状态（pending/running/passed/failed/error）、错误信息、逐步骤结果、
    耗时与截图元数据（不含 base64 图片数据，截图请通过平台页面查看）。
    状态为 running/pending 时请间隔数秒后再次调用。需对执行所属 UI 项目有访问权限。
    """

    def run(user):
        from apps.ui_automation.models import TestCaseExecution
        execution = TestCaseExecution.objects.filter(
            id=execution_id, project__in=act.accessible_ui_projects(user)
        ).select_related('test_case').first()
        if not execution:
            raise ToolError(f'UI 执行 {execution_id} 不存在或无权限')

        # execution_logs 落库为步骤结果 JSON（与 views.run 保存格式一致）；
        # 历史文本日志或异常数据降级为 raw_logs 返回
        steps = []
        raw_logs = ''
        logs = execution.execution_logs or ''
        if logs:
            try:
                parsed = json.loads(logs)
                if isinstance(parsed, list):
                    steps = parsed
                else:
                    raw_logs = logs
            except (TypeError, ValueError):
                raw_logs = logs

        result = {
            'execution_id': execution.id,
            'case_id': execution.test_case_id,
            'case_name': execution.test_case.name if execution.test_case else '',
            'status': execution.status,
            'engine': execution.engine,
            'browser': execution.browser,
            'headless': execution.headless,
            'error_message': execution.error_message or '',
            'steps': steps,
            'execution_time': execution.execution_time,
            'started_at': execution.started_at,
            'finished_at': execution.finished_at,
            # 截图只返回元数据，base64 原图体积过大不适合 MCP 通道传输
            'screenshots': [
                {k: v for k, v in shot.items() if k != 'url'}
                for shot in (execution.screenshots or []) if isinstance(shot, dict)
            ],
        }
        if raw_logs:
            result['raw_logs'] = raw_logs[:2000]
        if execution.status in ('running', 'pending'):
            result['hint'] = '执行尚未结束，请数秒后再次调用本工具'
        return result

    return _run_tool(ctx, 'get_ui_execution', {'execution_id': execution_id}, run)


#: 所有工具（供 server.py 批量注册）
ALL_TOOLS = [
    list_projects, list_testcases, list_api_requests, list_ui_cases, list_perf_scenes,
    get_report, analyze_failure, get_ui_execution,
    preview_run_api_suite, confirm_run_api_suite,
    preview_run_ui_case, confirm_run_ui_case,
    preview_run_perf_scene, confirm_run_perf_scene,
    preview_create_testcase, confirm_create_testcase,
    get_approval_status,
]
