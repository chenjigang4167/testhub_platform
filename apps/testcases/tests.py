from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.projects.models import Project, ProjectMember
from apps.testcases.models import TestCase as TCModel, TestCaseStep, TestCaseComment
from apps.users.models import User

# 注意：testcase-list / testcase-detail URL name 与 ui_automation 模块的 router 冲突，
# 这里直接使用路径常量以避免 reverse() 解析到错误的路由。
TC_LIST_URL = '/api/testcases/'


def tc_detail_url(pk):
    return f'/api/testcases/{pk}/'


class TestCaseApiTests(APITestCase):
    """Testcases 模块 - 测试用例 API 冒烟测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='tc_tester', password='pass123456')
        self.other_user = User.objects.create_user(username='tc_other', password='pass123456')
        self.project = Project.objects.create(name='用例测试项目', owner=self.user)
        ProjectMember.objects.create(project=self.project, user=self.user, role='tester')
        self.client.force_authenticate(self.user)
        self.list_url = TC_LIST_URL

    def test_list_requires_authentication(self):
        """未认证用户无法访问用例列表"""
        anon_client = APIClient()
        response = anon_client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_testcase(self):
        """创建测试用例"""
        payload = {
            'title': '登录功能验证',
            'description': '验证正常登录流程',
            'preconditions': '用户已注册',
            'steps': '1. 打开登录页\n2. 输入账号密码\n3. 点击登录',
            'expected_result': '登录成功进入首页',
            'priority': 'high',
            'test_type': 'functional',
            'project_id': self.project.id,
        }
        response = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], '登录功能验证')
        self.assertEqual(TCModel.objects.count(), 1)

    def test_list_testcases_with_pagination(self):
        """列表查询支持分页"""
        for i in range(15):
            TCModel.objects.create(
                title=f'用例{i}', expected_result='通过', project=self.project, author=self.user,
            )

        response = self.client.get(self.list_url, {'page': 1, 'page_size': 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
        self.assertEqual(response.data['count'], 15)

    def test_retrieve_testcase_detail(self):
        """获取用例详情"""
        tc = TCModel.objects.create(
            title='详情测试', expected_result='通过', project=self.project, author=self.user,
        )
        TestCaseStep.objects.create(testcase=tc, step_number=1, action='点击按钮', expected='跳转')
        detail_url = tc_detail_url(tc.id)
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], '详情测试')
        self.assertEqual(len(response.data['step_details']), 1)

    def test_update_testcase(self):
        """更新测试用例"""
        tc = TCModel.objects.create(
            title='旧标题', expected_result='通过', project=self.project, author=self.user,
        )
        detail_url = tc_detail_url(tc.id)
        response = self.client.patch(detail_url, {'title': '新标题'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tc.refresh_from_db()
        self.assertEqual(tc.title, '新标题')

    def test_delete_testcase(self):
        """删除测试用例"""
        tc = TCModel.objects.create(
            title='待删除', expected_result='通过', project=self.project, author=self.user,
        )
        detail_url = tc_detail_url(tc.id)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TCModel.objects.count(), 0)

    def test_search_testcase_by_title(self):
        """按标题搜索用例"""
        TCModel.objects.create(
            title='支付流程验证', expected_result='通过', project=self.project, author=self.user,
        )
        TCModel.objects.create(
            title='登录流程验证', expected_result='通过', project=self.project, author=self.user,
        )
        response = self.client.get(self.list_url, {'search': '支付'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertIn('支付', response.data['results'][0]['title'])

    def test_filter_by_priority(self):
        """按优先级过滤用例"""
        TCModel.objects.create(
            title='高优用例', expected_result='通过', project=self.project, author=self.user, priority='high',
        )
        TCModel.objects.create(
            title='低优用例', expected_result='通过', project=self.project, author=self.user, priority='low',
        )
        response = self.client.get(self.list_url, {'priority': 'high'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['priority'], 'high')

    def test_only_project_members_see_testcases(self):
        """非项目成员无法看到用例"""
        TCModel.objects.create(
            title='内部用例', expected_result='通过', project=self.project, author=self.user,
        )
        self.client.force_authenticate(self.other_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
