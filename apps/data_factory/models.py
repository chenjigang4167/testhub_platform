from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class DataFactoryRecord(models.Model):
    """数据工厂使用记录"""

    TOOL_CATEGORIES = (
        ('test_data', '测试数据'),
        ('json', 'JSON工具'),
        ('string', '字符工具'),
        ('encoding', '编码工具'),
        ('random', '随机工具'),
        ('encryption', '加密工具'),
        ('crontab', 'Crontab工具'),
    )

    TOOL_SCENARIOS = (
        ('test_data', '测试数据'),
        ('json', 'JSON工具'),
        ('string', '字符工具'),
        ('encoding', '编码工具'),
        ('random', '随机工具'),
        ('encryption', '加密工具'),
        ('crontab', 'Crontab工具'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    tool_name = models.CharField(max_length=100, verbose_name='工具名称')
    tool_category = models.CharField(max_length=20, choices=TOOL_CATEGORIES, verbose_name='工具分类')
    tool_scenario = models.CharField(max_length=20, choices=TOOL_SCENARIOS, verbose_name='使用场景')
    input_data = models.JSONField(verbose_name='输入数据', null=True, blank=True)
    output_data = models.JSONField(verbose_name='输出数据')
    is_saved = models.BooleanField(default=True, verbose_name='是否保存')
    tags = models.JSONField(verbose_name='标签', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'data_factory_record'
        verbose_name = '数据工厂记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['tool_category']),
            models.Index(fields=['tool_scenario']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.tool_name}"
