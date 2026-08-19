"""
mcp_runner.py - MCP 场景的单用例异步执行器

apps.mcp.actions.run_ui_case_action 依赖本模块的 start_case_execution()。
与 TestCaseViewSet.run 的 Web 端同步执行不同，MCP 契约要求「立即返回执行记录、
后台异步执行、Agent 轮询执行 ID 查结果」，故此处创建 TestCaseExecution 后
在后台线程执行，不阻塞 MCP 工具调用。

执行流程与 views.TestCaseViewSet.run 对齐，复用同一套引擎：
  - PlaywrightTestEngine（异步 API，线程内新建事件循环）
  - SeleniumTestEngine（同步 API）
"""
import asyncio
import json
import logging
import threading
import time

from django.db import connection
from django.utils import timezone

from .models import TestCaseExecution

logger = logging.getLogger(__name__)


def _collect_steps_data(case):
    """预加载步骤与元素数据（与 views.run 相同的快照结构）。"""
    steps_data = []
    for step in case.steps.all().order_by('step_number'):
        step_data = {
            'step': step,
            'action_type': step.action_type,
            'description': step.description,
        }
        if step.element:
            step_data['element_data'] = {
                'locator_strategy': (step.element.locator_strategy.name
                                     if step.element.locator_strategy else 'css'),
                'locator_value': step.element.locator_value,
                'name': step.element.name,
                'wait_timeout': step.element.wait_timeout,
                'force_action': step.element.force_action,
            }
        else:
            step_data['element_data'] = None
        steps_data.append(step_data)
    return steps_data


def _finish_execution(execution, status, step_results, screenshots,
                      error_message, start_time):
    """落库执行结果（字段含义与 views.run 的保存逻辑一致）。"""
    try:
        execution.status = status
        execution.error_message = error_message or ''
        execution.execution_logs = json.dumps(step_results, ensure_ascii=False)
        execution.execution_time = round(time.time() - start_time, 2)
        execution.screenshots = screenshots
        execution.finished_at = timezone.now()
        execution.save()
    except Exception:
        logger.exception('[McpRunner] 保存执行结果失败 execution_id=%s', execution.id)


async def _run_playwright_async(execution, case, steps_data, browser, headless):
    from .playwright_engine import PlaywrightTestEngine

    engine = PlaywrightTestEngine(browser_type=browser, headless=headless)
    screenshots = []
    step_results = []
    result = {'status': 'passed', 'error_message': None}
    try:
        await engine.start()
        if case.project.base_url:
            success, nav_log = await engine.navigate(case.project.base_url)
            if not success:
                result['status'] = 'failed'
                result['error_message'] = f'导航到测试页面失败: {nav_log}'
                return result, step_results, screenshots
        for i, info in enumerate(steps_data, 1):
            try:
                success, step_log, shot = await engine.execute_step(
                    info['step'], info['element_data'] or {})
            except Exception as e:
                success, step_log, shot = False, f'步骤执行异常: {e}', None
            step_results.append({
                'step_number': i,
                'action_type': info['action_type'],
                'description': info['description'] or '',
                'success': success,
                'error': None if success else step_log,
            })
            if not success:
                result['status'] = 'failed'
                result['error_message'] = f'步骤 {i} 执行失败: {step_log}'
                shot = shot or await _safe_screenshot(engine, is_async=True)
                if shot:
                    screenshots.append({
                        'url': shot,
                        'description': f'步骤 {i} 失败截图',
                        'step_number': i,
                        'timestamp': timezone.now().isoformat(),
                    })
                break
            if info['action_type'] == 'screenshot' and shot:
                screenshots.append({
                    'url': shot,
                    'description': f'步骤 {i}: {info["description"] or "手动截图"}',
                    'step_number': i,
                    'timestamp': timezone.now().isoformat(),
                })
    finally:
        try:
            await engine.stop()
        except Exception:
            logger.warning('[McpRunner] Playwright 引擎关闭异常', exc_info=True)
    return result, step_results, screenshots


async def _safe_screenshot(engine, is_async=False):
    try:
        if is_async:
            return await engine.capture_screenshot()
        return engine.capture_screenshot()
    except Exception:
        return None


def _run_selenium_sync(execution, case, steps_data, browser, headless):
    from .selenium_engine import SeleniumTestEngine

    engine = SeleniumTestEngine(browser_type=browser, headless=headless)
    screenshots = []
    step_results = []
    result = {'status': 'passed', 'error_message': None}
    try:
        engine.start()
        if case.project.base_url:
            success, nav_log = engine.navigate(case.project.base_url)
            if not success:
                result['status'] = 'failed'
                result['error_message'] = f'导航到测试页面失败: {nav_log}'
                return result, step_results, screenshots
        for i, info in enumerate(steps_data, 1):
            try:
                success, step_log, shot = engine.execute_step(
                    info['step'], info['element_data'] or {})
            except Exception as e:
                success, step_log, shot = False, f'步骤执行异常: {e}', None
            step_results.append({
                'step_number': i,
                'action_type': info['action_type'],
                'description': info['description'] or '',
                'success': success,
                'error': None if success else step_log,
            })
            if not success:
                result['status'] = 'failed'
                result['error_message'] = f'步骤 {i} 执行失败: {step_log}'
                shot = shot or _safe_screenshot(engine)
                if shot:
                    screenshots.append({
                        'url': shot,
                        'description': f'步骤 {i} 失败截图',
                        'step_number': i,
                        'timestamp': timezone.now().isoformat(),
                    })
                break
            if info['action_type'] == 'screenshot' and shot:
                screenshots.append({
                    'url': shot,
                    'description': f'步骤 {i}: {info["description"] or "手动截图"}',
                    'step_number': i,
                    'timestamp': timezone.now().isoformat(),
                })
    finally:
        try:
            engine.stop()
        except Exception:
            logger.warning('[McpRunner] Selenium 引擎关闭异常', exc_info=True)
    return result, step_results, screenshots


def _worker_playwright(execution, case, steps_data, browser, headless):
    start_time = time.time()
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result, step_results, screenshots = loop.run_until_complete(
                _run_playwright_async(execution, case, steps_data, browser, headless))
        finally:
            loop.close()
        _finish_execution(execution, result['status'], step_results, screenshots,
                          result['error_message'], start_time)
    except Exception as e:
        logger.exception('[McpRunner] Playwright 执行异常 execution_id=%s', execution.id)
        _finish_execution(execution, 'error', [], [], f'执行异常: {e}', start_time)
    finally:
        connection.close()


def _worker_selenium(execution, case, steps_data, browser, headless):
    start_time = time.time()
    try:
        result, step_results, screenshots = _run_selenium_sync(
            execution, case, steps_data, browser, headless)
        _finish_execution(execution, result['status'], step_results, screenshots,
                          result['error_message'], start_time)
    except Exception as e:
        logger.exception('[McpRunner] Selenium 执行异常 execution_id=%s', execution.id)
        _finish_execution(execution, 'error', [], [], f'执行异常: {e}', start_time)
    finally:
        connection.close()


def start_case_execution(case, user, engine='playwright', browser='chrome',
                         headless=True):
    """异步启动单个 UI 用例执行，立即返回 TestCaseExecution。

    Args:
        case: TestCase 实例（调用方已完成权限校验）
        user: 触发执行的用户
        engine: 'playwright' | 'selenium'
        browser: 浏览器类型（chrome/firefox/edge/safari）
        headless: 是否无头模式（MCP 服务端场景默认无头）

    Returns:
        TestCaseExecution（status='running'）

    Raises:
        ValueError: 执行环境检查失败（浏览器/驱动缺失等）
    """
    from .playwright_engine import PlaywrightTestEngine
    from .selenium_engine import SeleniumTestEngine

    if engine == 'selenium':
        is_ready, error_msg = SeleniumTestEngine.check_execution_environment(browser)
        worker = _worker_selenium
    else:
        is_ready, error_msg = PlaywrightTestEngine.check_execution_environment_sync(browser)
        worker = _worker_playwright
    if not is_ready:
        raise ValueError(f'{engine} 执行环境检查失败: {error_msg}')

    steps_data = _collect_steps_data(case)
    if not steps_data:
        raise ValueError(f"用例 '{case.name}' 没有定义任何步骤")

    execution = TestCaseExecution.objects.create(
        test_case=case,
        project=case.project,
        execution_source='manual',
        status='running',
        engine=engine,
        browser=browser,
        headless=headless,
        created_by=user,
        started_at=timezone.now(),
    )

    thread = threading.Thread(
        target=worker,
        args=(execution, case, steps_data, browser, headless),
        name=f'mcp-ui-case-{execution.id}',
        daemon=False,
    )
    thread.start()
    logger.info('[McpRunner] 用例 %s (id=%s) 已异步启动, engine=%s, execution_id=%s',
                case.name, case.id, engine, execution.id)
    return execution
