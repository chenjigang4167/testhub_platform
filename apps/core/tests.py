from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.core.models import UnifiedNotificationConfig
from apps.users.models import User


class NotificationConfigApiTests(APITestCase):
    """Core 模块 - 统一通知配置 API 冒烟测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='core_tester', password='pass123456')
        self.client.force_authenticate(self.user)
        self.list_url = reverse('unified-notification-config-list')

    def test_list_requires_authentication(self):
        """未认证用户无法访问通知配置列表"""
        anon_client = APIClient()
        response = anon_client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_notification_config(self):
        """创建飞书通知配置"""
        payload = {
            'name': '飞书通知',
            'config_type': 'webhook_feishu',
            'webhook_bots': {
                'feishu': {
                    'name': '测试机器人',
                    'webhook_url': 'https://open.feishu.cn/hook/test',
                    'enabled': True,
                }
            },
            'is_default': False,
            'is_active': True,
        }
        response = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], '飞书通知')
        self.assertEqual(response.data['config_type'], 'webhook_feishu')
        self.assertEqual(response.data['created_by'], self.user.id)

    def test_list_and_filter_configs(self):
        """列表查询与按 config_type 过滤"""
        UnifiedNotificationConfig.objects.create(
            name='飞书配置', config_type='webhook_feishu', created_by=self.user, is_active=True,
        )
        UnifiedNotificationConfig.objects.create(
            name='钉钉配置', config_type='webhook_dingtalk', created_by=self.user, is_active=True,
        )

        # 全量列表
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

        # 按类型过滤
        response = self.client.get(self.list_url, {'config_type': 'webhook_feishu'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], '飞书配置')

    def test_update_config(self):
        """更新通知配置名称"""
        config = UnifiedNotificationConfig.objects.create(
            name='旧名称', config_type='webhook_wechat', created_by=self.user,
        )
        detail_url = reverse('unified-notification-config-detail', args=[config.id])
        response = self.client.patch(detail_url, {'name': '新名称'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        config.refresh_from_db()
        self.assertEqual(config.name, '新名称')

    def test_delete_config(self):
        """删除通知配置"""
        config = UnifiedNotificationConfig.objects.create(
            name='待删除', config_type='webhook_feishu', created_by=self.user,
        )
        detail_url = reverse('unified-notification-config-detail', args=[config.id])
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(UnifiedNotificationConfig.objects.count(), 0)

    def test_set_default_action(self):
        """set_default 动作：设置默认配置并取消其他默认"""
        config_a = UnifiedNotificationConfig.objects.create(
            name='A', config_type='webhook_feishu', created_by=self.user, is_default=True,
        )
        config_b = UnifiedNotificationConfig.objects.create(
            name='B', config_type='webhook_feishu', created_by=self.user, is_default=False,
        )
        set_default_url = reverse('unified-notification-config-set-default', args=[config_b.id])
        response = self.client.post(set_default_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        config_a.refresh_from_db()
        config_b.refresh_from_db()
        self.assertFalse(config_a.is_default)
        self.assertTrue(config_b.is_default)

    def test_active_configs_action(self):
        """active_configs 动作：仅返回启用的配置"""
        UnifiedNotificationConfig.objects.create(
            name='启用', config_type='webhook_feishu', created_by=self.user, is_active=True,
        )
        UnifiedNotificationConfig.objects.create(
            name='禁用', config_type='webhook_feishu', created_by=self.user, is_active=False,
        )
        active_url = reverse('unified-notification-config-active-configs')
        response = self.client.get(active_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], '启用')
