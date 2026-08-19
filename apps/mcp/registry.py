"""MCP 工具注册表：工具元数据的唯一事实源。

协议 annotations（server.py）、目录 API（views.py）、前端工具目录页
均由本注册表派生，新增/修改工具时只需在此登记一次。
tests/test_registry 会校验 TOOL_REGISTRY 与 tools.ALL_TOOLS 的一致性。
"""
from dataclasses import dataclass

# --------------------------------------------------------------------- #
# 分类常量（前端筛选与汇总共用）
# --------------------------------------------------------------------- #
CATEGORY_READ = 'read'        # 只读工具：即时返回
CATEGORY_PREVIEW = 'preview'  # 危险操作第一步：返回预览 + confirm_token
CATEGORY_CONFIRM = 'confirm'  # 危险操作第二步：校验令牌后执行
CATEGORY_APPROVAL = 'approval'  # 人工审批状态查询

#: 分类显示顺序
CATEGORY_ORDER = [CATEGORY_READ, CATEGORY_PREVIEW, CATEGORY_CONFIRM, CATEGORY_APPROVAL]


@dataclass(frozen=True)
class ToolMeta:
    """单个工具的声明式元数据。"""
    name: str                    # 工具名（与 tools.py 函数名一致）
    title: str                   # 中文显示名
    category: str                # read / preview / confirm / approval
    domain: str                  # 业务域：project / testcases / api-testing 等
    summary: str                 # 一句话用途（列表展示）
    description: str             # 详细说明（详情展示，与 docstring 对齐）
    read_only: bool = True       # MCP annotations: readOnlyHint
    destructive: bool = False    # MCP annotations: destructiveHint
    idempotent: bool = True      # MCP annotations: idempotentHint
    open_world: bool = False     # MCP annotations: openWorldHint
    paired_with: str = ''        # preview <-> confirm 配对工具名
    examples: tuple = ()         # 调用参数示例（dict 元组）

    def to_mcp_annotations(self):
        """转换为 MCP 规范的 ToolAnnotations（供协议 tools/list 返回）。"""
        from mcp.types import ToolAnnotations
        return ToolAnnotations(
            title=self.title,
            readOnlyHint=self.read_only,
            destructiveHint=self.destructive,
            idempotentHint=self.idempotent,
            openWorldHint=self.open_world,
        )

    @property
    def annotations_dict(self):
        """普通 dict 形式（目录 API 序列化用）。"""
        return {
            'title': self.title,
            'readOnlyHint': self.read_only,
            'destructiveHint': self.destructive,
            'idempotentHint': self.idempotent,
            'openWorldHint': self.open_world,
        }


# --------------------------------------------------------------------- #
# 工具登记（与 tools.ALL_TOOLS 一一对应，共 17 个）
# --------------------------------------------------------------------- #

_TOOLS = [
    # ------------------------- 只读工具（8） ------------------------- #
    ToolMeta(
        name='list_projects', title='项目列表', category=CATEGORY_READ,
        domain='project',
        summary='列出当前用户可访问的测试项目',
        description='列出当前用户拥有或参与的测试项目（测试用例域）。'
                    '返回 id/name/status/created_at 轻量字段，支持 limit/offset 分页（上限 100），'
                    '结果带 60 秒缓存。其他域的项目请分别使用对应 list_* 工具。',
        examples=({'limit': 20, 'offset': 0},),
    ),
    ToolMeta(
        name='list_testcases', title='功能用例列表', category=CATEGORY_READ,
        domain='testcases',
        summary='列出项目下的功能测试用例',
        description='列出指定项目下的功能测试用例（仅 id/title/priority/status/test_type/created_at '
                    '轻量字段，不含步骤与描述大字段）。需对该项目有访问权限，'
                    '支持 limit/offset 分页（上限 100），结果带 60 秒缓存。',
        examples=({'project_id': 1, 'limit': 20, 'offset': 0},),
    ),
    ToolMeta(
        name='list_api_requests', title='接口请求列表', category=CATEGORY_READ,
        domain='api-testing',
        summary='列出 API 项目下的接口请求',
        description='列出指定 API 测试项目下的接口请求（id/name/method/url/request_type）。'
                    '需对该 API 项目有访问权限，按目录顺序排序，'
                    '支持 limit/offset 分页（上限 100），结果带 60 秒缓存。',
        examples=({'project_id': 1, 'limit': 20, 'offset': 0},),
    ),
    ToolMeta(
        name='list_ui_cases', title='UI 用例列表', category=CATEGORY_READ,
        domain='ui-automation',
        summary='列出 UI 自动化项目下的测试用例',
        description='列出指定 UI 自动化项目下的测试用例（id/name/status/priority/created_at）。'
                    '需对该 UI 项目有访问权限，支持 limit/offset 分页（上限 100），'
                    '结果带 60 秒缓存。',
        examples=({'project_id': 1, 'limit': 20, 'offset': 0},),
    ),
    ToolMeta(
        name='list_perf_scenes', title='压测场景列表', category=CATEGORY_READ,
        domain='perf-testing',
        summary='列出压测项目下的压测场景',
        description='列出指定压测项目下的压测场景（id/name/engine/enabled/created_at）。'
                    '需对该压测项目有访问权限，支持 limit/offset 分页（上限 100），'
                    '结果带 60 秒缓存。',
        examples=({'project_id': 1, 'limit': 20, 'offset': 0},),
    ),
    ToolMeta(
        name='get_report', title='压测报告摘要', category=CATEGORY_READ,
        domain='perf-testing',
        summary='获取压测执行报告摘要',
        description='获取指定压测执行的报告摘要：状态、SLA 结果、结论（verdict）及明细、'
                    '汇总指标、时长与按请求维度的统计（总量/失败/错误率/平均响应/P95/TPS）。'
                    '直接复用执行落库指标，不重新计算。',
        examples=({'execution_id': 42},),
    ),
    ToolMeta(
        name='analyze_failure', title='压测失败 AI 分析', category=CATEGORY_READ,
        domain='perf-testing',
        summary='触发或获取压测失败的 AI 分析',
        description='压测失败 AI 分析：命中缓存时即时返回分析结果（status=completed）；'
                    '未命中时投递 Celery 异步分析任务并返回 status=accepted，'
                    '约 30 秒后再次调用本工具获取结果。依赖 Celery，不可用时报错并提示改用页面 SSE 入口。',
        read_only=False, idempotent=False, open_world=True,
        examples=({'execution_id': 42},),
    ),

    ToolMeta(
        name='get_ui_execution', title='UI 执行结果查询', category=CATEGORY_READ,
        domain='ui-automation',
        summary='查询 UI 自动化用例执行结果',
        description='查询 UI 自动化用例执行结果：confirm_run_ui_case 返回执行 ID 后用本工具轮询。'
                    '返回状态（pending/running/passed/failed/error）、错误信息、逐步骤结果、'
                    '耗时与截图元数据（不含 base64 图片数据）。'
                    '状态为 running/pending 时请间隔数秒后再次调用。',
        examples=({'execution_id': 42},),
    ),

    # ------------------- 危险工具：preview/confirm 两段（8） ------------------- #
    ToolMeta(
        name='preview_run_api_suite', title='预览执行 API 套件', category=CATEGORY_PREVIEW,
        domain='api-testing',
        summary='预览执行 API 测试套件（危险操作第一步）',
        description='危险操作第一步：生成执行 API 测试套件的影响预览并返回 confirm_token（5 分钟有效）。'
                    '本步骤不执行任何套件。确认执行请调用 confirm_run_api_suite；'
                    '开启人工审批时还需轮询 get_approval_status。',
        read_only=False, idempotent=False, paired_with='confirm_run_api_suite',
        examples=({'suite_id': 12},),
    ),
    ToolMeta(
        name='confirm_run_api_suite', title='确认执行 API 套件', category=CATEGORY_CONFIRM,
        domain='api-testing',
        summary='确认执行 API 测试套件（危险操作第二步）',
        description='危险操作第二步：校验 preview_run_api_suite 返回的 confirm_token 后异步执行套件，'
                    '返回执行 ID。令牌一次性消费且 5 分钟内有效；'
                    '人工审批模式下返回 awaiting_approval，需轮询 get_approval_status。',
        read_only=False, idempotent=False, paired_with='preview_run_api_suite',
        examples=({'confirm_token': 'cf_xxxxxxxx'},),
    ),
    ToolMeta(
        name='preview_run_ui_case', title='预览执行 UI 用例', category=CATEGORY_PREVIEW,
        domain='ui-automation',
        summary='预览执行 UI 自动化用例（危险操作第一步）',
        description='危险操作第一步：生成执行 UI 自动化用例的影响预览并返回 confirm_token（5 分钟有效）。'
                    '可选执行引擎（playwright/selenium）、浏览器与 headless 模式。'
                    '本步骤不执行任何用例，确认执行请调用 confirm_run_ui_case。',
        read_only=False, idempotent=False, paired_with='confirm_run_ui_case',
        examples=({'case_id': 8, 'engine': 'playwright', 'browser': 'chrome', 'headless': True},),
    ),
    ToolMeta(
        name='confirm_run_ui_case', title='确认执行 UI 用例', category=CATEGORY_CONFIRM,
        domain='ui-automation',
        summary='确认执行 UI 自动化用例（危险操作第二步）',
        description='危险操作第二步：校验 preview_run_ui_case 返回的 confirm_token 后异步执行用例，'
                    '返回执行 ID。令牌一次性消费且 5 分钟内有效；'
                    '人工审批模式下返回 awaiting_approval，需轮询 get_approval_status。',
        read_only=False, idempotent=False, paired_with='preview_run_ui_case',
        examples=({'confirm_token': 'cf_xxxxxxxx'},),
    ),
    ToolMeta(
        name='preview_run_perf_scene', title='预览发起压测', category=CATEGORY_PREVIEW,
        domain='perf-testing',
        summary='预览发起压测（危险操作第一步）',
        description='危险操作第一步：生成发起压测的影响预览并返回 confirm_token（5 分钟有效）。'
                    '本步骤不产生任何压测流量，确认执行请调用 confirm_run_perf_scene。',
        read_only=False, idempotent=False, paired_with='confirm_run_perf_scene',
        examples=({'scene_id': 3},),
    ),
    ToolMeta(
        name='confirm_run_perf_scene', title='确认发起压测', category=CATEGORY_CONFIRM,
        domain='perf-testing',
        summary='确认发起压测（危险操作第二步）',
        description='危险操作第二步：校验 preview_run_perf_scene 返回的 confirm_token 后异步发起压测，'
                    '返回执行 ID。令牌一次性消费且 5 分钟内有效；'
                    '人工审批模式下返回 awaiting_approval，需轮询 get_approval_status。',
        read_only=False, idempotent=False, paired_with='preview_run_perf_scene',
        examples=({'confirm_token': 'cf_xxxxxxxx'},),
    ),
    ToolMeta(
        name='preview_create_testcase', title='预览创建用例', category=CATEGORY_PREVIEW,
        domain='testcases',
        summary='预览创建功能测试用例（危险操作第一步）',
        description='危险操作第一步：生成创建功能测试用例的影响预览并返回 confirm_token（5 分钟有效）。'
                    'data 结构：{title, description?, preconditions?, expected_result?, '
                    'priority?, test_type?, steps?: [{action, expected}]}。'
                    '本步骤不落库，确认创建请调用 confirm_create_testcase。',
        read_only=False, idempotent=False, paired_with='confirm_create_testcase',
        examples=({'project_id': 1,
                   'data': {'title': '登录成功', 'expected_result': '跳转到首页', 'priority': 'P1',
                            'steps': [{'action': '输入账号密码并点击登录', 'expected': '登录成功'}]}},),
    ),
    ToolMeta(
        name='confirm_create_testcase', title='确认创建用例', category=CATEGORY_CONFIRM,
        domain='testcases',
        summary='确认创建功能测试用例（危险操作第二步）',
        description='危险操作第二步：校验 preview_create_testcase 返回的 confirm_token 后创建用例，'
                    '返回 testcase_id。令牌一次性消费且 5 分钟内有效；'
                    '人工审批模式下返回 awaiting_approval，需轮询 get_approval_status。',
        read_only=False, idempotent=False, paired_with='preview_create_testcase',
        examples=({'confirm_token': 'cf_xxxxxxxx'},),
    ),

    # ------------------------- 审批查询（1） ------------------------- #
    ToolMeta(
        name='get_approval_status', title='审批状态查询', category=CATEGORY_APPROVAL,
        domain='platform',
        summary='查询危险操作的人工审批状态',
        description='只读查询危险操作的人工审批状态，供 Agent 轮询：confirm_* 返回 awaiting_approval 后，'
                    '用同一 confirm_token 反复调用本工具，直至返回 approved（附执行结果）/ '
                    'rejected / expired。',
        examples=({'confirm_token': 'cf_xxxxxxxx'},),
    ),
]

#: 工具注册表：name -> ToolMeta
TOOL_REGISTRY = {meta.name: meta for meta in _TOOLS}


def get_tool_meta(name: str):
    """按工具名获取元数据，未登记返回 None。"""
    return TOOL_REGISTRY.get(name)


def catalog_summary() -> dict:
    """目录汇总：总数 + 分类计数。"""
    by_category = {c: 0 for c in CATEGORY_ORDER}
    for meta in _TOOLS:
        by_category[meta.category] = by_category.get(meta.category, 0) + 1
    return {
        'total': len(_TOOLS),
        'by_category': by_category,
    }
