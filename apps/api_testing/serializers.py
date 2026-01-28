from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime


class NullableDateField(serializers.DateField):
    """允许空字符串的日期字段"""
    def to_internal_value(self, value):
        # 如果是空字符串，返回 None
        if value == '' or value is None:
            return None
        # 否则使用父类的正常处理
        return super().to_internal_value(value)
from .models import (
    ApiProject, ApiCollection, ApiRequest, Environment,
    RequestHistory, TestSuite, TestExecution, TestSuiteRequest,
    ScheduledTask, TaskExecutionLog, NotificationLog,
    TaskNotificationSetting, OperationLog, AIServiceConfig,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class ApiProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)
    member_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    start_date = NullableDateField(required=False, allow_null=True)
    end_date = NullableDateField(required=False, allow_null=True)

    class Meta:
        model = ApiProject
        fields = [
            'id', 'name', 'description', 'project_type', 'status',
            'owner', 'members', 'member_ids', 'start_date', 'end_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, attrs):
        # 将空字符串转换为 None
        if 'start_date' in attrs and attrs['start_date'] == '':
            attrs['start_date'] = None
        if 'end_date' in attrs and attrs['end_date'] == '':
            attrs['end_date'] = None
        return attrs

    def create(self, validated_data):
        member_ids = validated_data.pop('member_ids', [])
        validated_data['owner'] = self.context['request'].user
        project = super().create(validated_data)

        if member_ids:
            members = User.objects.filter(id__in=member_ids)
            project.members.set(members)

        return project

    def update(self, instance, validated_data):
        member_ids = validated_data.pop('member_ids', None)
        project = super().update(instance, validated_data)

        if member_ids is not None:
            members = User.objects.filter(id__in=member_ids)
            project.members.set(members)

        return project


class ApiCollectionSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = ApiCollection
        fields = [
            'id', 'name', 'description', 'project', 'parent',
            'order', 'children', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_children(self, obj):
        children = obj.children.all()
        return ApiCollectionSerializer(children, many=True).data


class ApiRequestSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = ApiRequest
        fields = [
            'id', 'name', 'description', 'request_type', 'method', 'url',
            'headers', 'params', 'body', 'auth', 'pre_request_script',
            'post_request_script', 'assertions', 'collection', 'order', 'created_by',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user

        # 根据集合所属项目的类型设置接口类型
        collection = validated_data.get('collection')
        if collection and collection.project:
            if collection.project.project_type == 'WEBSOCKET':
                validated_data['request_type'] = 'WEBSOCKET'
            else:
                validated_data['request_type'] = 'HTTP'

        return super().create(validated_data)


class EnvironmentSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    project = serializers.PrimaryKeyRelatedField(
        queryset=ApiProject.objects.all(),
        required=False,
        allow_null=True
    )
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Environment
        fields = [
            'id', 'name', 'scope', 'project', 'project_name', 'variables', 'is_active',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'project_name']

    def validate(self, attrs):
        if attrs.get('scope') == 'GLOBAL':
            attrs['project'] = None
        elif attrs.get('scope') == 'LOCAL' and not attrs.get('project'):
            raise serializers.ValidationError({'project': '局部环境变量必须关联项目'})
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class RequestHistorySerializer(serializers.ModelSerializer):
    request = ApiRequestSerializer(read_only=True)
    environment = EnvironmentSerializer(read_only=True)
    executed_by = UserSerializer(read_only=True)

    class Meta:
        model = RequestHistory
        fields = [
            'id', 'request', 'environment', 'request_data', 'response_data',
            'status_code', 'response_time', 'error_message', 'assertions_results',
            'executed_by', 'executed_at'
        ]


class TestSuiteRequestSerializer(serializers.ModelSerializer):
    request = ApiRequestSerializer(read_only=True)

    class Meta:
        model = TestSuiteRequest
        fields = ['id', 'request', 'order', 'assertions', 'enabled']


class TestSuiteSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    suite_requests = TestSuiteRequestSerializer(source='testsuiterequest_set', many=True, read_only=True)

    class Meta:
        model = TestSuite
        fields = [
            'id', 'name', 'description', 'project', 'environment',
            'suite_requests', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TestExecutionSerializer(serializers.ModelSerializer):
    test_suite = TestSuiteSerializer(read_only=True)
    executed_by = UserSerializer(read_only=True)

    class Meta:
        model = TestExecution
        fields = [
            'id', 'test_suite', 'status', 'start_time', 'end_time',
            'total_requests', 'passed_requests', 'failed_requests',
            'results', 'executed_by', 'created_at'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # 添加项目名称信息
        if instance.test_suite and instance.test_suite.project:
            data['project_name'] = instance.test_suite.project.name
            data['test_suite_name'] = instance.test_suite.name
        return data


class ScheduledTaskSerializer(serializers.ModelSerializer):
    """定时任务序列化器"""
    created_by = UserSerializer(read_only=True)
    test_suite_name = serializers.CharField(source='test_suite.name', read_only=True)
    api_request_name = serializers.CharField(source='api_request.name', read_only=True)
    environment_name = serializers.CharField(source='environment.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    notification_type = serializers.SerializerMethodField(read_only=True)
    notification_type_display = serializers.SerializerMethodField()
    notification_type_input = serializers.CharField(write_only=True, required=False, default='email')

    class Meta:
        model = ScheduledTask
        fields = [
            'id', 'name', 'description', 'task_type', 'trigger_type',
            'cron_expression', 'interval_seconds', 'execute_at',
            'test_suite', 'test_suite_name', 'api_request', 'api_request_name',
            'environment', 'environment_name', 'status', 'last_run_time',
            'next_run_time', 'total_runs', 'successful_runs', 'failed_runs',
            'last_result', 'error_message', 'notify_on_success', 'notify_on_failure',
            'notify_emails', 'notification_type', 'notification_type_display', 'notification_type_input', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'last_run_time', 'next_run_time', 'total_runs', 'successful_runs',
            'failed_runs', 'last_result', 'error_message', 'created_at', 'updated_at'
        ]

    def get_notification_type_display(self, obj):
        """获取通知类型显示"""
        try:
            notification_setting = obj.notification_settings.first()
            if notification_setting:
                return notification_setting.get_notification_type_display()
        except:
            pass
        return "-"

    def get_notification_type(self, obj):
        """获取通知类型原始值"""
        try:
            notification_setting = obj.notification_settings.first()
            if notification_setting:
                return notification_setting.notification_type
        except:
            pass
        return "email"  # 默认值

    def validate(self, attrs):
        """验证定时任务配置"""
        trigger_type = attrs.get('trigger_type')

        if trigger_type == 'CRON':
            if not attrs.get('cron_expression'):
                raise serializers.ValidationError("Cron表达式不能为空")
            # 这里可以添加Cron表达式的格式验证

        elif trigger_type == 'INTERVAL':
            if not attrs.get('interval_seconds'):
                raise serializers.ValidationError("间隔秒数不能为空")
            if attrs['interval_seconds'] < 60:
                raise serializers.ValidationError("间隔秒数不能小于60秒")

        elif trigger_type == 'ONCE':
            if not attrs.get('execute_at'):
                raise serializers.ValidationError("执行时间不能为空")
            if attrs['execute_at'] <= timezone.now():
                raise serializers.ValidationError("执行时间必须大于当前时间")

        # 验证任务类型配置
        task_type = attrs.get('task_type')
        if task_type == 'TEST_SUITE' and not attrs.get('test_suite'):
            raise serializers.ValidationError("测试套件不能为空")
        elif task_type == 'API_REQUEST' and not attrs.get('api_request'):
            raise serializers.ValidationError("API请求不能为空")

        return attrs

    def create(self, validated_data):
        """创建定时任务"""
        # 提取通知相关数据
        notification_type = validated_data.pop('notification_type_input', 'email')

        validated_data['created_by'] = self.context['request'].user
        task = super().create(validated_data)

        # 计算下次运行时间
        task.next_run_time = task.calculate_next_run()
        task.save()

        # 创建对应的通知设置
        from .models import TaskNotificationSetting
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"=== 开始创建通知设置 ===")
        logger.info(
            f"任务ID: {task.id}, 通知类型: {notification_type}, 成功通知: {task.notify_on_success}, 失败通知: {task.notify_on_failure}")

        try:
            # 根据通知类型选择合适的通知配置
            from apps.core.models import UnifiedNotificationConfig
            notification_config = None
            if notification_type in ['webhook', 'both']:
                # 如果需要Webhook通知，优先选择Webhook配置
                notification_config = UnifiedNotificationConfig.objects.filter(
                    config_type__in=['webhook_wechat', 'webhook_feishu', 'webhook_dingtalk'],
                    is_active=True
                ).first()
                if not notification_config:
                    logger.warning("没有找到可用的Webhook通知配置，使用默认邮件配置")
                    notification_config = UnifiedNotificationConfig.objects.filter(is_default=True, is_active=True).first()
            else:
                # 邮件通知使用默认配置
                notification_config = UnifiedNotificationConfig.objects.filter(is_default=True, is_active=True).first()

            logger.info(f"选择的通知配置: {notification_config.name if notification_config else 'None'}")

            notification_setting, created = TaskNotificationSetting.objects.get_or_create(
                task=task,
                defaults={
                    'notification_type': notification_type,
                    'is_enabled': task.notify_on_success or task.notify_on_failure,
                    'notify_on_success': task.notify_on_success,
                    'notify_on_failure': task.notify_on_failure,
                    'notification_config': notification_config,
                }
            )

            logger.info(f"通知设置创建结果 - ID: {notification_setting.id}, 是否新创建: {created}")
            logger.info(
                f"通知设置详情 - 类型: {notification_setting.notification_type}, 启用: {notification_setting.is_enabled}")
        except Exception as e:
            logger.error(f"创建通知设置时出错: {e}")
            import traceback
            traceback.print_exc()

        logger.info("=== 结束创建通知设置 ===")

        return task

    def update(self, instance, validated_data):
        """更新定时任务"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info("=== 开始更新定时任务 ===")

        # 提取通知相关数据
        notification_type = validated_data.pop('notification_type_input', None)
        logger.info(f"任务ID: {instance.id}, 收到的通知类型: {notification_type}")

        # 更新任务基本信息
        task = super().update(instance, validated_data)

        # 重新计算下次运行时间
        task.next_run_time = task.calculate_next_run()
        task.save()

        # 更新通知设置
        if notification_type is not None:
            from .models import TaskNotificationSetting
            from apps.core.models import UnifiedNotificationConfig
            try:
                # 根据通知类型选择合适的通知配置
                notification_config = None
                if notification_type in ['webhook', 'both']:
                    # 如果需要Webhook通知，优先选择Webhook配置
                    notification_config = UnifiedNotificationConfig.objects.filter(
                        config_type__in=['webhook_wechat', 'webhook_feishu', 'webhook_dingtalk'],
                        is_active=True
                    ).first()
                    if not notification_config:
                        logger.warning("没有找到可用的Webhook通知配置，使用默认邮件配置")
                        notification_config = UnifiedNotificationConfig.objects.filter(is_default=True, is_active=True).first()
                else:
                    # 邮件通知使用默认配置
                    notification_config = UnifiedNotificationConfig.objects.filter(is_default=True, is_active=True).first()

                logger.info(f"选择的通知配置: {notification_config.name if notification_config else 'None'}")

                notification_setting, created = TaskNotificationSetting.objects.get_or_create(
                    task=task,
                    defaults={
                        'notification_type': notification_type,
                        'is_enabled': task.notify_on_success or task.notify_on_failure,
                        'notify_on_success': task.notify_on_success,
                        'notify_on_failure': task.notify_on_failure,
                        'notification_config': notification_config,
                    }
                )

                # 如果通知设置已存在，更新它
                if not created:
                    notification_setting.notification_type = notification_type
                    notification_setting.is_enabled = task.notify_on_success or task.notify_on_failure
                    notification_setting.notify_on_success = task.notify_on_success
                    notification_setting.notify_on_failure = task.notify_on_failure
                    notification_setting.notification_config = notification_config
                    notification_setting.save()
                    logger.info(f"通知设置已更新 - 类型: {notification_setting.notification_type}, 配置: {notification_config.name}")
                else:
                    logger.info(f"通知设置已创建 - 类型: {notification_setting.notification_type}, 配置: {notification_config.name}")

            except Exception as e:
                logger.error(f"更新通知设置时出错: {e}")
                import traceback
                traceback.print_exc()

        logger.info("=== 结束更新定时任务 ===")
        return task


class TaskExecutionLogSerializer(serializers.ModelSerializer):
    """任务执行日志序列化器"""
    task_name = serializers.CharField(source='task.name', read_only=True)
    executed_by_name = serializers.CharField(source='executed_by.username', read_only=True)

    class Meta:
        model = TaskExecutionLog
        fields = [
            'id', 'task', 'task_name', 'status', 'start_time', 'end_time',
            'result', 'error_message', 'executed_by', 'executed_by_name',
            'created_at'
        ]
        read_only_fields = ['created_at']


# ================ 通知管理序列化器 ================


class NotificationLogSerializer(serializers.ModelSerializer):
    """通知日志序列化器"""
    recipient_names = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    notification_type_display = serializers.SerializerMethodField()
    task_type_display = serializers.SerializerMethodField()
    retry_status = serializers.SerializerMethodField()
    notification_target_display = serializers.SerializerMethodField()

    class Meta:
        model = NotificationLog
        fields = ['id', 'task_name', 'task_type_display', 'notification_type_display', 'sender_name',
                  'recipient_names', 'notification_target_display', 'status_display', 'created_at', 'sent_at', 'retry_status']
        read_only_fields = ['created_at', 'sent_at']

    def get_recipient_names(self, obj):
        """获取收件人姓名列表"""
        return obj.get_recipient_names()

    def get_status_display(self, obj):
        """获取状态显示"""
        return obj.get_status_display()

    def get_notification_type_display(self, obj):
        """获取通知类型显示 - 从任务的通知设置中获取"""
        if obj.task:
            try:
                notification_setting = obj.task.notification_settings.first()
                if notification_setting:
                    return notification_setting.get_notification_type_display()
            except:
                pass
        # 回退到原始的通知类型显示
        return obj.get_notification_type_display()

    def get_task_type_display(self, obj):
        """获取任务类型显示 - 使用保存的快照值"""
        if obj.task_type:
            # 使用保存的任务类型快照
            for choice_value, choice_label in ScheduledTask.TASK_TYPE_CHOICES:
                if choice_value == obj.task_type:
                    return choice_label
            return obj.task_type
        # 如果 task_type 为空，返回未记录，不要从 task 对象获取（避免显示修改后的值）
        return "未记录"

    def get_retry_status(self, obj):
        """获取重试状态"""
        return obj.get_retry_status()

    def get_notification_target_display(self, obj):
        """获取通知对象显示"""
        targets = []

        # 检查是否有webhook机器人信息
        if obj.webhook_bot_info:
            bot_type = obj.webhook_bot_info.get('bot_type', '')
            bot_name = obj.webhook_bot_info.get('bot_name', '')

            # 根据机器人类型返回友好名称
            type_map = {
                'wechat': '企微机器人',
                'feishu': '飞书机器人',
                'dingtalk': '钉钉机器人'
            }
            bot_display = type_map.get(bot_type, 'Webhook机器人')
            if bot_name:
                targets.append(f"{bot_display}（{bot_name}）")
            else:
                targets.append(bot_display)

        # 检查是否有邮箱收件人
        if obj.recipient_info:
            if isinstance(obj.recipient_info, list) and len(obj.recipient_info) > 0:
                targets.append('邮箱')
            elif isinstance(obj.recipient_info, dict) and obj.recipient_info.get('email'):
                targets.append('邮箱')

        return ', '.join(targets) if targets else '-'


class TaskNotificationSettingSerializer(serializers.ModelSerializer):
    """定时任务通知设置序列化器"""
    notification_type_display = serializers.SerializerMethodField()
    notification_config_info = serializers.SerializerMethodField()
    active_types = serializers.SerializerMethodField()

    class Meta:
        model = TaskNotificationSetting
        fields = ['id', 'task', 'notification_type_display', 'notification_config_info',
                  'is_enabled', 'notify_on_success', 'notify_on_failure',
                  'notify_on_timeout', 'notify_on_error', 'active_types']
        read_only_fields = ['created_at', 'updated_at']

    def get_notification_type_display(self, obj):
        """获取通知类型显示"""
        return obj.get_notification_type_display()

    def get_notification_config_info(self, obj):
        """获取通知配置信息"""
        config = obj.get_notification_config()
        return f"{config.name}" if config else "未配置通知"

    def get_active_types(self, obj):
        """获取激活的通知类型"""
        types = obj.get_active_notification_types()
        type_names = []
        if 'email' in types:
            type_names.append('邮箱')
        if 'webhook' in types:
            type_names.append('Webhook机器人')
        return ', '.join(type_names) if type_names else "无"


class NotificationLogDetailSerializer(serializers.ModelSerializer):
    """通知日志详情序列化器"""
    notification_type_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    task_type_display = serializers.SerializerMethodField()
    formatted_recipients = serializers.SerializerMethodField()
    webhook_bot_info_display = serializers.SerializerMethodField()
    notification_target_display = serializers.SerializerMethodField()

    class Meta:
        model = NotificationLog
        fields = ['id', 'task_name', 'task_type_display', 'notification_type_display', 'sender_name',
                  'sender_email', 'formatted_recipients', 'webhook_bot_info_display', 'notification_target_display',
                  'notification_content', 'status_display', 'error_message',
                  'created_at', 'sent_at', 'retry_count', 'is_retried']
        read_only_fields = ['created_at', 'sent_at']

    def get_notification_type_display(self, obj):
        """获取通知类型显示 - 从任务的通知设置中获取"""
        if obj.task:
            try:
                notification_setting = obj.task.notification_settings.first()
                if notification_setting:
                    return notification_setting.get_notification_type_display()
            except:
                pass
        # 回退到原始的通知类型显示
        return obj.get_notification_type_display()

    def get_status_display(self, obj):
        """获取状态显示"""
        return obj.get_status_display()

    def get_task_type_display(self, obj):
        """获取任务类型显示 - 使用保存的快照值"""
        if obj.task_type:
            # 使用保存的任务类型快照
            for choice_value, choice_label in ScheduledTask.TASK_TYPE_CHOICES:
                if choice_value == obj.task_type:
                    return choice_label
            return obj.task_type
        # 如果 task_type 为空，返回未记录，不要从 task 对象获取（避免显示修改后的值）
        return "未记录"

    def get_formatted_recipients(self, obj):
        """获取格式化的收件人信息"""
        if not obj.recipient_info:
            return []

        recipients = []
        if isinstance(obj.recipient_info, list):
            for rec in obj.recipient_info:
                email = rec.get('email', '')
                # 尝试从数据库获取用户的中文姓名
                if email:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    try:
                        user = User.objects.get(email=email)
                        name = user.first_name or user.username
                        recipients.append({
                            'name': name,
                            'email': email,
                            'display': f"{name}（{email}）"
                        })
                    except User.DoesNotExist:
                        recipients.append({
                            'name': email,
                            'email': email,
                            'display': email
                        })
        elif isinstance(obj.recipient_info, dict):
            email = obj.recipient_info.get('email', '')
            if email:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    user = User.objects.get(email=email)
                    name = user.first_name or user.username
                    recipients.append({
                        'name': name,
                        'email': email,
                        'display': f"{name}（{email}）"
                    })
                except User.DoesNotExist:
                    recipients.append({
                        'name': email,
                        'email': email,
                        'display': email
                    })
        return recipients

    def get_webhook_bot_info_display(self, obj):
        """获取Webhook机器人信息显示"""
        # 检查任务的通知类型是否包含webhook
        if obj.task:
            try:
                notification_setting = obj.task.notification_settings.first()
                if notification_setting and notification_setting.notification_type in ['webhook', 'both']:
                    return obj.webhook_bot_info or {}
            except:
                pass
        return None

    def get_notification_target_display(self, obj):
        """获取通知对象显示 - 返回详细信息"""
        targets = []

        # 检查是否有webhook机器人信息
        if obj.webhook_bot_info:
            bot_type = obj.webhook_bot_info.get('bot_type', '')
            bot_name = obj.webhook_bot_info.get('bot_name', '')

            # 根据机器人类型返回友好名称
            type_map = {
                'wechat': '企微机器人',
                'feishu': '飞书机器人',
                'dingtalk': '钉钉机器人'
            }
            bot_display = type_map.get(bot_type, 'Webhook机器人')
            targets.append({
                'type': bot_type,
                'display': bot_display,
                'name': bot_name or bot_display
            })

        # 检查是否有邮箱收件人
        if obj.recipient_info:
            if isinstance(obj.recipient_info, list) and len(obj.recipient_info) > 0:
                # 获取所有邮箱地址
                emails = [rec.get('email', '') for rec in obj.recipient_info if rec.get('email')]
                if emails:
                    targets.append({
                        'type': 'email',
                        'display': '邮箱',
                        'name': ', '.join(emails)
                    })
            elif isinstance(obj.recipient_info, dict) and obj.recipient_info.get('email'):
                targets.append({
                    'type': 'email',
                    'display': '邮箱',
                    'name': obj.recipient_info.get('email')
                })

        return targets


class TaskNotificationSettingDetailSerializer(serializers.ModelSerializer):
    """定时任务通知设置详情序列化器"""
    notification_type_display = serializers.SerializerMethodField()
    webhook_bots_display = serializers.SerializerMethodField()
    recipients_detail = serializers.SerializerMethodField()
    notification_config_detail = serializers.SerializerMethodField()

    class Meta:
        model = TaskNotificationSetting
        fields = ['id', 'task', 'notification_type', 'notification_type_display', 'notification_config', 'notification_config_detail',
                  'is_enabled', 'notify_on_success', 'notify_on_failure',
                  'notify_on_timeout', 'notify_on_error', 'custom_webhook_bots',
                  'custom_recipients', 'webhook_bots_display', 'recipients_detail', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_notification_type_display(self, obj):
        """获取通知类型显示"""
        return obj.get_notification_type_display()

    def get_notification_config_detail(self, obj):
        """获取通知配置详情"""
        config = obj.get_notification_config()
        if config:
            return {
                'id': config.id,
                'name': config.name,
                'config_type': config.config_type
            }
        return None

    def get_webhook_bots_display(self, obj):
        """获取自定义webhook机器人显示"""
        custom_bots = obj.custom_webhook_bots or {}
        config_bots = []

        if obj.notification_config:
            config_bots = obj.notification_config.get_webhook_bots()

        # 合并自定义机器人和配置机器人
        all_bots = []
        bot_types = ['feishu', 'wechat', 'dingtalk']

        for bot_type in bot_types:
            # 检查自定义机器人
            if bot_type in custom_bots:
                all_bots.append({
                    'type': bot_type,
                    'name': custom_bots[bot_type].get('name', f'{bot_type}机器人'),
                    'webhook_url': custom_bots[bot_type].get('webhook_url'),
                    'enabled': custom_bots[bot_type].get('enabled', True),
                    'source': 'custom'
                })

            # 检查配置机器人
            for config_bot in config_bots:
                if config_bot['type'] == bot_type:
                    all_bots.append({
                        'type': bot_type,
                        'name': config_bot['name'],
                        'webhook_url': config_bot['webhook_url'],
                        'enabled': config_bot['enabled'],
                        'source': 'config'
                    })

        return all_bots

    def get_recipients_detail(self, obj):
        """获取收件人详情"""
        recipients = []

        # 只使用自定义收件人，因为通知配置不再有recipients字段
        custom_users = list(obj.custom_recipients.all())
        if custom_users:
            recipients = [{
                'id': user.id,
                'name': user.username,
                'email': user.email,
                'full_name': f"{user.first_name} {user.last_name}".strip(),
                'selected': True
            } for user in custom_users]

        return recipients


class OperationLogSerializer(serializers.ModelSerializer):
    """操作日志序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    operation_type_display = serializers.CharField(source='get_operation_type_display', read_only=True)
    resource_type_display = serializers.CharField(source='get_resource_type_display', read_only=True)

    class Meta:
        model = OperationLog
        fields = [
            'id', 'operation_type', 'operation_type_display',
            'resource_type', 'resource_type_display', 'resource_id',
            'resource_name', 'description', 'user', 'user_name', 'created_at'
        ]
        read_only_fields = ['created_at']


class AIServiceConfigSerializer(serializers.ModelSerializer):
    """AI服务配置序列化器"""
    service_type_display = serializers.CharField(source='get_service_type_display', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = AIServiceConfig
        fields = [
            'id', 'name', 'service_type', 'service_type_display',
            'role', 'role_display', 'api_key', 'base_url', 'model_name',
            'max_tokens', 'temperature', 'is_active', 'created_by',
            'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
