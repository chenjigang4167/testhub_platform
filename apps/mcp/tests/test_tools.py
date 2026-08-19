# -*- coding: utf-8 -*-
"""MCP 工具层单测：权限过滤 / 分页 / 缓存 / 调用日志。

运行: python manage.py test apps.mcp.tests.test_tools
"""
import json

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings

from apps.mcp.confirm import approve_pending
from apps.mcp.models import McpCallLog, McpPendingConfirm
from apps.mcp.tests.utils import FakeContext, ctx_with_jwt
from apps.mcp import tools as mcp_tools
from apps.projects.models import Project
from apps.testcases.models import TestCase as FunctionalTestCase

from mcp.server.fastmcp.exceptions import ToolError

User = get_user_model()


class ToolBase(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create(username='mcp_tools_user', email='t@a.com')
        self.other = User.objects.create(username='mcp_tools_other', email='t@b.com')
        self.project = Project.objects.create(name='工具项目', owner=self.user)
        self.ctx, _ = ctx_with_jwt(self.user)

    def tearDown(self):
        cache.clear()


class ListProjectsToolTest(ToolBase):
    def test_returns_only_accessible_projects(self):
        Project.objects.create(name='别人项目', owner=self.other)
        result = mcp_tools.list_projects(self.ctx)
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['items'][0]['name'], '工具项目')

    def test_pagination_limit_offset(self):
        for i in range(5):
            Project.objects.create(name=f'项目{i}', owner=self.user)
        page = mcp_tools.list_projects(self.ctx, limit=2, offset=0)
        self.assertEqual(page['total'], 6)
        self.assertEqual(len(page['items']), 2)
        page2 = mcp_tools.list_projects(self.ctx, limit=2, offset=2)
        self.assertNotEqual(page['items'][0]['id'], page2['items'][0]['id'])

    def test_limit_clamped_to_max(self):
        limit, offset = mcp_tools._clamp_page(99999, -5)
        self.assertEqual(limit, mcp_tools.MAX_LIMIT)
        self.assertEqual(offset, 0)

    def test_result_cached_within_ttl(self):
        mcp_tools.list_projects(self.ctx)
        key = f'mcp:tool:list_projects:{self.user.id}:20:0'
        self.assertIsNotNone(cache.get(key))

    def test_cache_isolated_per_user(self):
        mcp_tools.list_projects(self.ctx)
        other_ctx, _ = ctx_with_jwt(self.other)
        result = mcp_tools.list_projects(other_ctx)
        # 另一个用户不读当前用户的缓存，结果为空
        self.assertEqual(result['total'], 0)

    def test_call_log_written(self):
        mcp_tools.list_projects(self.ctx)
        log = McpCallLog.objects.filter(tool_name='list_projects').first()
        self.assertIsNotNone(log)
        self.assertEqual(log.user_id, self.user.id)
        self.assertEqual(log.status, 'success')
        self.assertGreaterEqual(log.duration_ms, 0)


class ListTestcasesToolTest(ToolBase):
    def test_permission_denied_for_foreign_project(self):
        foreign = Project.objects.create(name='别人项目', owner=self.other)
        with self.assertRaises(ToolError):
            mcp_tools.list_testcases(self.ctx, project_id=foreign.id)

    def test_returns_light_fields(self):
        FunctionalTestCase.objects.create(
            project=self.project, title='用例A',
            expected_result='ok', author=self.user)
        result = mcp_tools.list_testcases(self.ctx, project_id=self.project.id)
        self.assertEqual(result['total'], 1)
        item = result['items'][0]
        self.assertIn('id', item)
        self.assertIn('title', item)
        self.assertNotIn('description', item)


class UnauthenticatedToolTest(TestCase):
    def test_tool_without_credentials_raises(self):
        cache.clear()
        empty_ctx = FakeContext({})
        with self.assertRaises(ToolError):
            mcp_tools.list_projects(empty_ctx)


class PreviewConfirmToolTest(ToolBase):
    def test_preview_and_confirm_create_testcase(self):
        preview = mcp_tools.preview_create_testcase(
            self.ctx, project_id=self.project.id,
            data={'title': '工具创建', 'expected_result': 'ok'})
        self.assertIn('confirm_token', preview)

        result = mcp_tools.confirm_create_testcase(self.ctx, preview['confirm_token'])
        self.assertIn('testcase_id', result)
        self.assertTrue(FunctionalTestCase.objects.filter(
            project=self.project, title='工具创建').exists())

    def test_confirm_with_invalid_token_raises(self):
        with self.assertRaises(ToolError):
            mcp_tools.confirm_run_api_suite(self.ctx, confirm_token='bad-token')


class ArgsBriefMaskingTest(ToolBase):
    def test_args_brief_masks_sensitive_fields(self):
        mcp_tools.preview_create_testcase(
            self.ctx, project_id=self.project.id,
            data={'title': '脱敏用例', 'expected_result': 'ok',
                  'password': 'p@ssw0rd', 'api_token': 'tk-123'})
        log = McpCallLog.objects.filter(tool_name='preview_create_testcase').first()
        self.assertIsNotNone(log)
        self.assertIn('***', log.args_brief)
        self.assertNotIn('p@ssw0rd', log.args_brief)
        self.assertNotIn('tk-123', log.args_brief)
        # 非敏感字段保留原文
        self.assertIn('脱敏用例', log.args_brief)


class ApprovalStatusToolTest(ToolBase):
    def _preview(self, title='轮询用例'):
        return mcp_tools.preview_create_testcase(
            self.ctx, project_id=self.project.id,
            data={'title': title, 'expected_result': 'ok'})

    def test_poll_flow_after_confirm(self):
        token = self._preview()['confirm_token']
        # confirm 前：pending
        info = mcp_tools.get_approval_status(self.ctx, token)
        self.assertEqual(info['status'], 'pending')
        # 默认模式 confirm 直接执行 → 轮询返回 approved 与结果
        mcp_tools.confirm_create_testcase(self.ctx, token)
        info = mcp_tools.get_approval_status(self.ctx, token)
        self.assertEqual(info['status'], 'approved')
        self.assertIn('testcase_id', info['result'])

    def test_invalid_token_raises(self):
        with self.assertRaises(ToolError):
            mcp_tools.get_approval_status(self.ctx, confirm_token='bad-token')


class HumanApprovalToolTest(ToolBase):
    def _preview(self, title='轮询用例'):
        return mcp_tools.preview_create_testcase(
            self.ctx, project_id=self.project.id,
            data={'title': title, 'expected_result': 'ok'})

    @override_settings(MCP_HUMAN_APPROVAL=True)
    def test_confirm_blocks_until_console_approves(self):
        token = self._preview('人审用例')['confirm_token']

        out = mcp_tools.confirm_create_testcase(self.ctx, token)
        self.assertEqual(out['status'], 'awaiting_approval')
        self.assertFalse(FunctionalTestCase.objects.filter(
            project=self.project, title='人审用例').exists())

        # 轮询：等待人工审批
        info = mcp_tools.get_approval_status(self.ctx, token)
        self.assertEqual(info['status'], 'awaiting_approval')

        # 控制台批准 → 轮询可取执行结果
        approve_pending(McpPendingConfirm.objects.get(), self.user)
        info = mcp_tools.get_approval_status(self.ctx, token)
        self.assertEqual(info['status'], 'approved')
        self.assertIn('testcase_id', info['result'])

class GetUiExecutionToolTest(ToolBase):
    """get_ui_execution：UI 执行结果查询"""

    def setUp(self):
        super().setUp()
        from apps.ui_automation.models import UiProject, TestCase as UiCase
        self.ui_project = UiProject.objects.create(
            name='UI 项目', base_url='http://example.com', owner=self.user)
        self.ui_case = UiCase.objects.create(
            name='登录用例', project=self.ui_project, created_by=self.user)

    def _create_execution(self, status='passed', logs=None, project=None,
                          screenshots=None):
        from apps.ui_automation.models import TestCaseExecution
        return TestCaseExecution.objects.create(
            test_case=self.ui_case,
            project=project or self.ui_project,
            status=status,
            engine='playwright',
            browser='chrome',
            headless=True,
            execution_logs=logs or '',
            screenshots=screenshots or [],
            created_by=self.user,
        )

    def test_returns_passed_result_with_steps(self):
        steps = [{'step_number': 1, 'action_type': 'click',
                  'description': '点击登录', 'success': True, 'error': None}]
        execution = self._create_execution(
            logs=json.dumps(steps, ensure_ascii=False),
            screenshots=[{'url': 'data:image/png;base64,AAA',
                          'description': '步骤 1 截图', 'step_number': 1}],
        )
        result = mcp_tools.get_ui_execution(self.ctx, execution_id=execution.id)
        self.assertEqual(result['status'], 'passed')
        self.assertEqual(result['case_name'], '登录用例')
        self.assertEqual(result['steps'], steps)
        # 截图元数据返回，但不含 base64 原图
        self.assertEqual(result['screenshots'][0]['description'], '步骤 1 截图')
        self.assertNotIn('url', result['screenshots'][0])
        self.assertNotIn('hint', result)

    def test_running_returns_polling_hint(self):
        execution = self._create_execution(status='running')
        result = mcp_tools.get_ui_execution(self.ctx, execution_id=execution.id)
        self.assertEqual(result['status'], 'running')
        self.assertIn('hint', result)

    def test_legacy_text_logs_fallback_to_raw(self):
        execution = self._create_execution(logs='纯文本历史日志')
        result = mcp_tools.get_ui_execution(self.ctx, execution_id=execution.id)
        self.assertEqual(result['steps'], [])
        self.assertEqual(result['raw_logs'], '纯文本历史日志')

    def test_permission_denied_for_foreign_project(self):
        from apps.ui_automation.models import UiProject
        foreign = UiProject.objects.create(
            name='别人项目', base_url='http://b.com', owner=self.other)
        execution = self._create_execution(project=foreign)
        with self.assertRaises(ToolError):
            mcp_tools.get_ui_execution(self.ctx, execution_id=execution.id)

    def test_not_found(self):
        with self.assertRaises(ToolError):
            mcp_tools.get_ui_execution(self.ctx, execution_id=999999)
