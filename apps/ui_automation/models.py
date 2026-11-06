from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()


class UiProject(models.Model):
    """UI自动化测试项目模型"""
    STATUS_CHOICES = [
        ('NOT_STARTED', '未开始'),
        ('IN_PROGRESS', '进行中'),
        ('COMPLETED', '已结束'),
    ]

    name = models.CharField(max_length=200, verbose_name='项目名称')
    description = models.TextField(blank=True, verbose_name='项目描述')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='项目状态', default='IN_PROGRESS')
    base_url = models.URLField(verbose_name='基础URL')
    start_date = models.DateField(null=True, blank=True, verbose_name='开始日期')
    end_date = models.DateField(null=True, blank=True, verbose_name='结束日期')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_ui_projects', verbose_name='负责人')
    members = models.ManyToManyField(User, blank=True, related_name='ui_projects', verbose_name='团队成员')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'ui_projects'
        verbose_name = 'UI自动化项目'
        verbose_name_plural = 'UI自动化项目'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class LocatorStrategy(models.Model):
    """元素定位策略模型"""
    name = models.CharField(max_length=50, verbose_name='策略名称')
    description = models.TextField(blank=True, verbose_name='策略描述')

    class Meta:
        db_table = 'locator_strategies'
        verbose_name = '定位策略'
        verbose_name_plural = '定位策略'

    def __str__(self):
        return self.name


class ElementGroup(models.Model):
    """元素分组模型"""
    name = models.CharField(max_length=200, verbose_name='分组名称')
    description = models.TextField(blank=True, verbose_name='分组描述')
    project = models.ForeignKey(UiProject, on_delete=models.CASCADE, related_name='element_groups', verbose_name='所属项目')
    parent_group = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name='父分组')
    order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'ui_element_groups'
        verbose_name = '元素分组'
        verbose_name_plural = '元素分组'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Element(models.Model):
    """UI元素模型"""
    ELEMENT_TYPE_CHOICES = [
        ('INPUT', '输入框'),
        ('BUTTON', '按钮'),
        ('LINK', '链接'),
        ('DROPDOWN', '下拉框'),
        ('CHECKBOX', '复选框'),
        ('RADIO', '单选框'),
        ('TEXT', '文本'),
        ('IMAGE', '图片'),
        ('CONTAINER', '容器'),
        ('TABLE', '表格'),
        ('FORM', '表单'),
        ('MODAL', '弹窗'),
    ]

    VALIDATION_STATUS_CHOICES = [
        ('VALID', '有效'),
        ('INVALID', '无效'),
        ('UNKNOWN', '未知'),
        ('PENDING', '待验证'),
    ]

    project = models.ForeignKey(UiProject, on_delete=models.CASCADE, related_name='elements', verbose_name='所属项目')
    group = models.ForeignKey(ElementGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='elements', verbose_name='所属分组')
    name = models.CharField(max_length=200, verbose_name='元素名称')
    description = models.TextField(blank=True, verbose_name='元素描述')
    element_type = models.CharField(max_length=50, choices=ELEMENT_TYPE_CHOICES, verbose_name='元素类型', default='BUTTON')

    # 主要定位策略
    locator_strategy = models.ForeignKey(LocatorStrategy, on_delete=models.PROTECT, verbose_name='定位策略')
    locator_value = models.CharField(max_length=500, verbose_name='定位表达式')

    # 备用定位策略
    backup_locators = models.JSONField(
        blank=True,
        null=True,
        verbose_name='备用定位器',
        help_text='多个定位策略的JSON数组，格式：[{"strategy": "css", "value": ".button"}, ...]'
    )

    page = models.CharField(max_length=200, verbose_name='所属页面', blank=True)
    component_name = models.CharField(max_length=100, blank=True, verbose_name='组件名称', help_text='所属UI组件名称')
    order = models.IntegerField(default=0, verbose_name='排序')

    # 元素层次关系
    parent_element = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='父元素', help_text='用于构建元素层次结构')

    # 元素属性
    is_unique = models.BooleanField(default=False, verbose_name='是否唯一')
    wait_timeout = models.IntegerField(default=5, verbose_name='等待超时(秒)')
    is_visible = models.BooleanField(default=True, verbose_name='是否可见')
    is_enabled = models.BooleanField(default=True, verbose_name='是否启用')
    force_action = models.BooleanField(default=False, verbose_name='强制操作', help_text='对visibility:hidden的元素使用force选项')

    # 统计信息
    usage_count = models.IntegerField(default=0, verbose_name='使用次数', help_text='在脚本中被引用的次数')
    last_validated = models.DateTimeField(null=True, blank=True, verbose_name='最后验证时间')
    validation_status = models.CharField(max_length=20, choices=VALIDATION_STATUS_CHOICES, default='UNKNOWN', verbose_name='验证状态')
    validation_message = models.TextField(blank=True, verbose_name='验证消息')

    # 基础字段
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'ui_elements'
        verbose_name = 'UI元素'
        verbose_name_plural = 'UI元素'
        ordering = ['page', 'order', 'name']
        indexes = [
            models.Index(fields=['project', 'page']),
            models.Index(fields=['project', 'element_type']),
            models.Index(fields=['validation_status']),
        ]

    def __str__(self):
        return f'{self.page}: {self.name}' if self.page else self.name

    def increment_usage_count(self):
        """增加使用次数"""
        self.usage_count = models.F('usage_count') + 1
        self.save(update_fields=['usage_count'])

    def get_all_locators(self):
        """获取所有定位器（主要+备用）"""
        locators = [{
            'strategy': self.locator_strategy.name,
            'value': self.locator_value,
            'is_primary': True
        }]

        if self.backup_locators:
            for backup in self.backup_locators:
                locators.append({
                    'strategy': backup.get('strategy'),
                    'value': backup.get('value'),
                    'is_primary': False
                })

        return locators


class TestScript(models.Model):
    """测试脚本模型"""
    SCRIPT_TYPE_CHOICES = [
        ('CODE', '代码'),
        ('LOW_CODE', '低代码'),
        ('NO_CODE', '无代码'),
    ]

    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
    ]

    FRAMEWORK_CHOICES = [
        ('playwright', 'Playwright'),
        ('selenium', 'Selenium'),
    ]

    project = models.ForeignKey(UiProject, on_delete=models.CASCADE, related_name='test_scripts', verbose_name='所属项目')
    name = models.CharField(max_length=200, verbose_name='脚本名称')
    description = models.TextField(blank=True, verbose_name='脚本描述')
    script_type = models.CharField(max_length=20, choices=SCRIPT_TYPE_CHOICES, verbose_name='脚本类型', default='LOW_CODE')
    content = models.TextField(verbose_name='脚本内容')  # 可以是代码或JSON格式的低代码配置
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, verbose_name='脚本语言', default='python', blank=True)
    framework = models.CharField(max_length=20, choices=FRAMEWORK_CHOICES, verbose_name='执行框架', default='playwright', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'ui_test_scripts'
        verbose_name = 'UI测试脚本'
        verbose_name_plural = 'UI测试脚本'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class PageObject(models.Model):
    """页面对象模型"""
    name = models.CharField(max_length=200, verbose_name='页面对象名称')
    class_name = models.CharField(max_length=200, verbose_name='类名')
    url_pattern = models.CharField(max_length=500, blank=True, verbose_name='URL模式', help_text='页面URL模式，支持正则表达式')
    project = models.ForeignKey(UiProject, on_delete=models.CASCADE, related_name='page_objects', verbose_name='所属项目')
    description = models.TextField(blank=True, verbose_name='描述')
    template_code = models.TextField(blank=True, verbose_name='模板代码', help_text='生成的页面对象代码模板')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'ui_page_objects'
        verbose_name = '页面对象'
        verbose_name_plural = '页面对象'
        ordering = ['name']
        unique_together = ['project', 'name']

    def __str__(self):
        return self.name

    def generate_code(self, language='javascript'):
        """生成页面对象代码"""
        if language == 'javascript':
            return self._generate_javascript_code()
        elif language == 'python':
            return self._generate_python_code()
        else:
            raise ValueError(f"Unsupported language: {language}")

    def _generate_javascript_code(self):
        """生成JavaScript页面对象代码"""
        elements = self.page_object_elements.all()

        # 生成元素属性
        element_props = []
        methods = []

        for po_element in elements:
            element = po_element.element
            if po_element.is_property:
                element_props.append(
                    f"        this.{po_element.method_name} = page.locator('{element.locator_value}');"
                )
            else:
                methods.append(f"""
    async {po_element.method_name}() {{
        return this.page.locator('{element.locator_value}');
    }}""")

        template = f"""
class {self.class_name} {{
    constructor(page) {{
        this.page = page;
{chr(10).join(element_props)}
    }}
{chr(10).join(methods)}
}}
        """.strip()

        return template

    def _generate_python_code(self):
        """生成Python页面对象代码"""
        elements = self.page_object_elements.all()

        methods = []
        for po_element in elements:
            element = po_element.element
            methods.append(f"""
    def {po_element.method_name}(self):
        return self.page.locator('{element.locator_value}')""")

        template = f"""
class {self.class_name}:
    def __init__(self, page):
        self.page = page
{chr(10).join(methods)}
        """.strip()

        return template


class PageObjectElement(models.Model):
    """页面对象与元素的关联"""
    page_object = models.ForeignKey(PageObject, on_delete=models.CASCADE, related_name='page_object_elements', verbose_name='页面对象')
    element = models.ForeignKey(Element, on_delete=models.CASCADE, verbose_name='元素')
    method_name = models.CharField(max_length=100, verbose_name='方法名称', help_text='在页面对象中的方法/属性名称')
    is_property = models.BooleanField(default=True, verbose_name='是否为属性', help_text='True为属性，False为方法')
    order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'ui_page_object_elements'
        verbose_name = '页面对象元素关联'
        verbose_name_plural = '页面对象元素关联'
        unique_together = ['page_object', 'method_name']
        ordering = ['order', 'method_name']

    def __str__(self):
        return f'{self.page_object.name}.{self.method_name}'


class ScriptStep(models.Model):
    """脚本步骤模型"""
    ACTION_TYPE_CHOICES = [
        ('CLICK', '点击'),
        ('INPUT', '输入'),
        ('SELECT', '选择'),
        ('VERIFY', '验证'),
        ('WAIT', '等待'),
        ('HOVER', '悬停'),
        ('SCROLL', '滚动'),
        ('NAVIGATE', '导航'),
        ('SCREENSHOT', '截图'),
        ('SWITCH_TAB', '切换标签页'),
        ('CUSTOM', '自定义'),
    ]

    script = models.ForeignKey(TestScript, on_delete=models.CASCADE, related_name='steps', verbose_name='所属脚本')
    step_order = models.IntegerField(verbose_name='步骤顺序')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPE_CHOICES, verbose_name='操作类型')
    target_element = models.ForeignKey(Element, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='目标元素')
    page_object = models.ForeignKey(PageObject, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='页面对象')

    # 操作参数
    action_params = models.JSONField(blank=True, null=True, verbose_name='操作参数', help_text='JSON格式的操作参数')

    # 步骤描述
    description = models.CharField(max_length=500, verbose_name='步骤描述')
    expected_result = models.CharField(max_length=500, blank=True, verbose_name='预期结果')

    # 执行配置
    wait_before = models.IntegerField(default=0, verbose_name='执行前等待(毫秒)')
    wait_after = models.IntegerField(default=0, verbose_name='执行后等待(毫秒)')
    retry_count = models.IntegerField(default=0, verbose_name='重试次数')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'ui_script_steps'
        verbose_name = '脚本步骤'
        verbose_name_plural = '脚本步骤'
        ordering = ['step_order']
        unique_together = ['script', 'step_order']

    def __str__(self):
        return f'{self.script.name} - Step {self.step_order}: {self.action_type}'


class ScriptElementUsage(models.Model):
    """脚本元素使用记录"""
    USAGE_TYPE_CHOICES = [
        ('CLICK', '点击'),
        ('INPUT', '输入'),
        ('VERIFY', '验证'),
        ('WAIT', '等待'),
        ('HOVER', '悬停'),
        ('SELECT', '选择'),
        ('SCROLL', '滚动'),
        ('ATTRIBUTE', '属性获取'),
        ('TEXT', '文本获取'),
    ]

    script = models.ForeignKey(TestScript, on_delete=models.CASCADE, related_name='element_usages', verbose_name='脚本')
    element = models.ForeignKey(Element, on_delete=models.CASCADE, related_name='script_usages', verbose_name='元素')
    usage_type = models.CharField(max_length=50, choices=USAGE_TYPE_CHOICES, verbose_name='使用类型')
    line_number = models.IntegerField(verbose_name='行号', help_text='在脚本中的行号')
    context = models.TextField(blank=True, verbose_name='上下文代码', help_text='使用元素的代码上下文')
    frequency = models.IntegerField(default=1, verbose_name='使用频次', help_text='在脚本中使用的次数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'ui_script_element_usages'
        verbose_name = '脚本元素使用记录'
        verbose_name_plural = '脚本元素使用记录'
        unique_together = ['script', 'element', 'line_number']
        ordering = ['script', 'line_number']

    def __str__(self):
        return f'{self.script.name} uses {self.element.name} ({self.usage_type})'


class TestSuite(models.Model):
    """测试套件模型"""
    EXECUTION_STATUS_CHOICES = [
        ('not_run', '未执行'),
        ('passed', '通过'),
        ('failed', '失败'),
        ('running', '执行中'),
    ]

    project = models.ForeignKey(UiProject, on_delete=models.CASCADE, related_name='test_suites', verbose_name='所属项目')
    name = models.CharField(max_length=200, verbose_name='套件名称')
    description = models.TextField(blank=True, verbose_name='套件描述')
    scripts = models.ManyToManyField(TestScript, through='TestSuiteScript', verbose_name='测试脚本')
    test_cases = models.ManyToManyField('TestCase', through='TestSuiteTestCase', verbose_name='测试用例', blank=True)

    # 执行统计字段
    execution_status = models.CharField(max_length=20, choices=EXECUTION_STATUS_CHOICES, default='not_run', verbose_name='执行状态')
    passed_count = models.IntegerField(default=0, verbose_name='通过数')
    failed_count = models.IntegerField(default=0, verbose_name='失败数')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'ui_test_suites'
        verbose_name = 'UI测试套件'
        verbose_name_plural = 'UI测试套件'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class TestSuiteScript(models.Model):
    """测试套件与测试脚本的关联模型"""
    test_suite = models.ForeignKey(TestSuite, on_delete=models.CASCADE, related_name='suite_scripts', verbose_name='测试套件')
    test_script = models.ForeignKey(TestScript, on_delete=models.CASCADE, verbose_name='测试脚本')
    order = models.IntegerField(default=0, verbose_name='执行顺序')

    class Meta:
        db_table = 'ui_test_suite_scripts'
        verbose_name = '测试套件脚本关联'
        verbose_name_plural = '测试套件脚本关联'
        ordering = ['order']


class TestSuiteTestCase(models.Model):
    """测试套件与测试用例的关联模型"""
    test_suite = models.ForeignKey(TestSuite, on_delete=models.CASCADE, related_name='suite_test_cases', verbose_name='测试套件')
    test_case = models.ForeignKey('TestCase', on_delete=models.CASCADE, verbose_name='测试用例')
    order = models.IntegerField(default=0, verbose_name='执行顺序')

    class Meta:
        db_table = 'ui_test_suite_test_cases'
        verbose_name = '测试套件用例关联'
        verbose_name_plural = '测试套件用例关联'
        ordering = ['order']
        unique_together = ['test_suite', 'test_case']

    def __str__(self):
        return f'{self.test_suite.name} - {self.test_case.name}'


class TestExecution(models.Model):
    """测试执行记录模型"""
    STATUS_CHOICES = [
        ('PENDING', '待执行'),
        ('RUNNING', '运行中'),
        ('SUCCESS', '成功'),
        ('FAILED', '失败'),
        ('ABORTED', '中止'),
    ]

    ENVIRONMENT_CHOICES = [
        ('CHROME', 'Chrome'),
        ('FIREFOX', 'Firefox'),
        ('SAFARI', 'Safari'),
        ('EDGE', 'Edge'),
        ('IE', 'IE'),
    ]

    project = models.ForeignKey(UiProject, on_delete=models.CASCADE, related_name='executions', verbose_name='所属项目')
    test_suite = models.ForeignKey(TestSuite, on_delete=models.CASCADE, related_name='executions', null=True, blank=True, verbose_name='测试套件')
    test_script = models.ForeignKey(TestScript, on_delete=models.CASCADE, related_name='executions', null=True, blank=True, verbose_name='测试脚本')
    environment = models.CharField(max_length=20, choices=ENVIRONMENT_CHOICES, verbose_name='执行环境', default='CHROME')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='执行状态', default='PENDING')

    # 执行统计
    total_cases = models.IntegerField(default=0, verbose_name='总用例数')
    passed_cases = models.IntegerField(default=0, verbose_name='通过用例数')
    failed_cases = models.IntegerField(default=0, verbose_name='失败用例数')
    skipped_cases = models.IntegerField(default=0, verbose_name='跳过用例数')

    # 时间信息
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    duration = models.FloatField(default=0, verbose_name='执行时长(秒)')

    # 执行人员和配置
    executed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ui_test_executions', verbose_name='执行人员')
    engine = models.CharField(max_length=20, default='playwright', verbose_name='测试引擎')
    browser = models.CharField(max_length=20, default='chrome', verbose_name='浏览器')
    headless = models.BooleanField(default=False, verbose_name='无头模式')

    # 结果数据
    result_data = models.JSONField(blank=True, null=True, verbose_name='执行结果数据')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    report_url = models.CharField(max_length=500, blank=True, verbose_name='报告URL')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'ui_test_executions'
        verbose_name = 'UI测试执行记录'
        verbose_name_plural = 'UI测试执行记录'
        ordering = ['-created_at']

    def __str__(self):
        if self.test_suite:
            return f'Suite: {self.test_suite.name} - {self.get_status_display()}'
        elif self.test_script:
            return f'Script: {self.test_script.name} - {self.get_status_display()}'
        return f'Execution #{self.id}'

    @property
    def pass_rate(self):
        """计算通过率"""
        if self.total_cases == 0:
            return 0
        return round((self.passed_cases / self.total_cases) * 100, 2)


class TestEnvironment(models.Model):
    """测试环境配置模型"""
    name = models.CharField(max_length=100, verbose_name='环境名称')
    description = models.TextField(blank=True, verbose_name='环境描述')
    browser_type = models.CharField(max_length=50, verbose_name='浏览器类型')
    browser_version = models.CharField(max_length=50, blank=True, verbose_name='浏览器版本')
    resolution = models.CharField(max_length=50, blank=True, verbose_name='屏幕分辨率')
    os_type = models.CharField(max_length=50, blank=True, verbose_name='操作系统')
    os_version = models.CharField(max_length=50, blank=True, verbose_name='操作系统版本')
    capabilities = models.JSONField(blank=True, null=True, verbose_name='浏览器能力配置')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'ui_test_environments'
        verbose_name = 'UI测试环境'
        verbose_name_plural = 'UI测试环境'
        ordering = ['name']

    def __str__(self):
        return self.name


class Screenshot(models.Model):
    """截图模型"""
    execution = models.ForeignKey(TestExecution, on_delete=models.CASCADE, related_name='screenshots', verbose_name='测试执行')
    name = models.CharField(max_length=200, verbose_name='截图名称')
    image = models.ImageField(upload_to='ui_screenshots/', verbose_name='截图文件')
    description = models.TextField(blank=True, verbose_name='截图描述')
    captured_at = models.DateTimeField(auto_now_add=True, verbose_name='捕获时间')

    class Meta:
        db_table = 'ui_screenshots'
        verbose_name = 'UI截图'
        verbose_name_plural = 'UI截图'
        ordering = ['-captured_at']

    def __str__(self):
        return self.name


class TestCase(models.Model):
    """UI自动化测试用例模型"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('ready', '就绪'),
        ('running', '执行中'),
        ('passed', '通过'),
        ('failed', '失败'),
    ]

    PRIORITY_CHOICES = [
        ('high', '高'),
        ('medium', '中'),
        ('low', '低'),
    ]

    name = models.CharField(max_length=200, verbose_name='用例名称')
    description = models.TextField(blank=True, verbose_name='用例描述')
    project = models.ForeignKey(UiProject, on_delete=models.CASCADE, related_name='test_cases', verbose_name='所属项目')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name='优先级')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_test_cases', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'ui_test_cases'
        verbose_name = 'UI测试用例'
        verbose_name_plural = 'UI测试用例'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class TestCaseStep(models.Model):
    """测试用例步骤模型"""
    ACTION_TYPE_CHOICES = [
        ('click', '点击'),
        ('fill', '输入文本'),
        ('getText', '获取文本'),
        ('waitFor', '等待元素'),
        ('hover', '悬停'),
        ('scroll', '滚动'),
        ('screenshot', '截图'),
        ('assert', '断言'),
        ('wait', '等待'),
        ('switchTab', '切换标签页'),
        ('navigate', '页面导航'),
    ]

    ASSERT_TYPE_CHOICES = [
        ('textContains', '文本包含'),
        ('textEquals', '文本等于'),
        ('isVisible', '元素可见'),
        ('exists', '元素存在'),
        ('hasAttribute', '属性值'),
    ]

    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE, related_name='steps', verbose_name='测试用例')
    step_number = models.IntegerField(verbose_name='步骤序号')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPE_CHOICES, verbose_name='操作类型')
    element = models.ForeignKey(Element, on_delete=models.CASCADE, null=True, blank=True, verbose_name='目标元素')
    input_value = models.TextField(blank=True, verbose_name='输入值')
    wait_time = models.IntegerField(default=1000, verbose_name='等待时间(毫秒)')
    assert_type = models.CharField(max_length=20, choices=ASSERT_TYPE_CHOICES, blank=True, verbose_name='断言类型')
    assert_value = models.TextField(blank=True, verbose_name='断言期望值')
    description = models.TextField(blank=True, verbose_name='步骤描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'ui_test_case_steps'
        verbose_name = 'UI测试用例步骤'
        verbose_name_plural = 'UI测试用例步骤'
        ordering = ['step_number']
        unique_together = ['test_case', 'step_number']

    def __str__(self):
        return f"{self.test_case.name} - 步骤{self.step_number}"


class TestCaseExecution(models.Model):
    """测试用例执行记录模型"""
    STATUS_CHOICES = [
        ('pending', '待执行'),
        ('running', '执行中'),
        ('passed', '通过'),
        ('failed', '失败'),
        ('error', '错误'),
    ]

    ENGINE_CHOICES = [
        ('playwright', 'Playwright'),
        ('selenium', 'Selenium'),
    ]

    SOURCE_CHOICES = [
        ('manual', '单用例执行'),
        ('suite', '套件执行'),
        ('scheduled', '定时任务执行'),
    ]

    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE, related_name='executions', verbose_name='测试用例')
    project = models.ForeignKey(UiProject, on_delete=models.CASCADE, related_name='test_case_executions', verbose_name='项目')
    test_suite = models.ForeignKey('TestSuite', on_delete=models.CASCADE, null=True, blank=True, related_name='case_executions', verbose_name='所属测试套件')
    execution_source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='manual', verbose_name='执行来源')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='执行状态')
    engine = models.CharField(max_length=20, choices=ENGINE_CHOICES, default='playwright', verbose_name='测试引擎')
    browser = models.CharField(max_length=50, default='chrome', verbose_name='浏览器')
    headless = models.BooleanField(default=False, verbose_name='无头模式')
    execution_logs = models.TextField(blank=True, verbose_name='执行日志')
    error_message = models.TextField(null=True, blank=True, verbose_name='错误信息')
    screenshots = models.JSONField(default=list, blank=True, verbose_name='截图列表')
    execution_time = models.FloatField(null=True, blank=True, verbose_name='执行时长(秒)')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_case_executions', verbose_name='执行人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'ui_test_case_executions'
        verbose_name = 'UI测试用例执行记录'
        verbose_name_plural = 'UI测试用例执行记录'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.test_case.name} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


class OperationRecord(models.Model):
    """操作记录模型"""
    OPERATION_TYPE_CHOICES = [
        ('create', '新增'),
        ('edit', '编辑'),
        ('delete', '删除'),
        ('run', '运行'),
        ('rerun', '重新运行'),
        ('save', '保存'),
        ('rename', '重命名'),
    ]

    RESOURCE_TYPE_CHOICES = [
        ('project', '项目'),
        ('element', '元素'),
        ('test_case', '测试用例'),
        ('script', '脚本'),
        ('suite', '套件'),
        ('execution', '执行记录'),
        ('report', '测试报告'),
    ]

    operation_type = models.CharField(max_length=20, choices=OPERATION_TYPE_CHOICES, verbose_name='操作类型')
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES, verbose_name='资源类型')
    resource_id = models.IntegerField(verbose_name='资源ID')
    resource_name = models.CharField(max_length=200, verbose_name='资源名称')
    description = models.TextField(verbose_name='操作描述')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='操作用户')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'ui_operation_record'
        verbose_name = 'UI操作记录'
        verbose_name_plural = 'UI操作记录'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.get_operation_type_display()} - {self.resource_name}"


class UiScheduledTask(models.Model):
    """UI自动化定时任务模型"""
    TASK_TYPE_CHOICES = [
        ('TEST_SUITE', '测试套件执行'),
        ('TEST_CASE', '测试用例执行'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', '激活'),
        ('PAUSED', '暂停'),
        ('COMPLETED', '已完成'),
        ('FAILED', '失败'),
    ]

    TRIGGER_TYPE_CHOICES = [
        ('CRON', 'Cron表达式'),
        ('INTERVAL', '固定间隔'),
        ('ONCE', '单次执行'),
    ]

    name = models.CharField(max_length=200, verbose_name='任务名称')
    description = models.TextField(blank=True, verbose_name='任务描述')
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, verbose_name='任务类型')
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_TYPE_CHOICES, verbose_name='触发器类型')

    # Cron表达式配置
    cron_expression = models.CharField(max_length=100, blank=True, verbose_name='Cron表达式')

    # 固定间隔配置（秒）
    interval_seconds = models.IntegerField(null=True, blank=True, verbose_name='间隔秒数')

    # 单次执行时间
    execute_at = models.DateTimeField(null=True, blank=True, verbose_name='执行时间')

    # 任务配置
    project = models.ForeignKey('UiProject', on_delete=models.CASCADE, verbose_name='关联项目')
    test_suite = models.ForeignKey('TestSuite', on_delete=models.CASCADE, null=True, blank=True,
                                   verbose_name='测试套件')
    test_cases = models.JSONField(default=list, blank=True, verbose_name='测试用例列表',
                                 help_text='测试用例ID列表，用于TEST_CASE类型任务')

    # 执行配置
    engine = models.CharField(max_length=20, default='playwright', verbose_name='执行引擎',
                             help_text='playwright或selenium')
    browser = models.CharField(max_length=20, default='chrome', verbose_name='浏览器类型')
    headless = models.BooleanField(default=False, verbose_name='无头模式')

    # 通知配置
    NOTIFICATION_TYPE_CHOICES = [
        ('email', '邮箱通知'),
        ('webhook', 'Webhook机器人'),
        ('both', '两者都发送'),
    ]
    
    notify_on_success = models.BooleanField(default=False, verbose_name='成功时通知')
    notify_on_failure = models.BooleanField(default=False, verbose_name='失败时通知')
    notification_type = models.CharField(max_length=20, blank=True, choices=NOTIFICATION_TYPE_CHOICES, 
                                        verbose_name='通知类型')
    notify_emails = models.JSONField(default=list, blank=True, verbose_name='通知邮箱列表')

    # 状态管理
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE', verbose_name='任务状态')
    last_run_time = models.DateTimeField(null=True, blank=True, verbose_name='最后运行时间')
    next_run_time = models.DateTimeField(null=True, blank=True, verbose_name='下次运行时间')
    total_runs = models.IntegerField(default=0, verbose_name='总运行次数')
    successful_runs = models.IntegerField(default=0, verbose_name='成功运行次数')
    failed_runs = models.IntegerField(default=0, verbose_name='失败运行次数')

    # 执行结果
    last_result = models.JSONField(default=dict, verbose_name='最后执行结果')
    error_message = models.TextField(blank=True, verbose_name='错误信息')

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'ui_scheduled_tasks'
        verbose_name = 'UI定时任务'
        verbose_name_plural = 'UI定时任务'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_task_type_display()})"

    def calculate_next_run(self):
        """计算下次运行时间"""
        from datetime import datetime, timedelta
        from croniter import croniter

        now = timezone.now()

        if self.trigger_type == 'CRON' and self.cron_expression:
            try:
                iter = croniter(self.cron_expression, now)
                return iter.get_next(datetime)
            except Exception:
                return None

        elif self.trigger_type == 'INTERVAL' and self.interval_seconds:
            return now + timedelta(seconds=self.interval_seconds)

        elif self.trigger_type == 'ONCE' and self.execute_at:
            return self.execute_at if self.execute_at > now else None

        return None

    def should_run_now(self):
        """检查是否应该现在运行"""
        if self.status != 'ACTIVE':
            return False

        if not self.next_run_time:
            return False

        return timezone.now() >= self.next_run_time


class UiNotificationLog(models.Model):
    """UI自动化通知日志模型"""
    NOTIFICATION_TYPES = [
        ('task_execution', '定时任务执行'),
        ('test_suite_execution', '测试套件执行'),
        ('test_case_execution', '测试用例执行'),
        ('system_alert', '系统警告'),
        ('manual', '手动通知'),
    ]

    STATUS_CHOICES = [
        ('pending', '待发送'),
        ('sending', '发送中'),
        ('success', '发送成功'),
        ('failed', '发送失败'),
        ('cancelled', '已取消'),
    ]

    task = models.ForeignKey(UiScheduledTask, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联任务')
    task_name = models.CharField(max_length=200, verbose_name='任务名称', help_text='相关任务的名称')
    task_type = models.CharField(max_length=20, blank=True, null=True, verbose_name='任务类型快照', help_text='发送通知时的任务类型')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, verbose_name='通知类型')
    sender_name = models.CharField(max_length=100, verbose_name='发件人姓名')
    sender_email = models.EmailField(verbose_name='发件人邮箱')
    recipient_info = models.JSONField(verbose_name='收件人信息', help_text='接收通知的用户信息')
    webhook_bot_info = models.JSONField(default=dict, blank=True, null=True, verbose_name='Webhook机器人信息')
    notification_content = models.TextField(verbose_name='通知内容', help_text='发送的通知内容')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='发送状态')
    error_message = models.TextField(blank=True, null=True, verbose_name='错误信息', help_text='发送失败时的错误信息')
    response_info = models.JSONField(default=dict, blank=True, null=True, verbose_name='响应信息',
                                     help_text='接收方返回的响应信息')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='发送时间')
    retry_count = models.IntegerField(default=0, verbose_name='重试次数', help_text='已重试的次数')
    is_retried = models.BooleanField(default=False, verbose_name='是否已重试')

    class Meta:
        db_table = 'ui_notification_logs'
        verbose_name = 'UI通知日志'
        verbose_name_plural = 'UI通知日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        task_name = self.task.name if self.task else self.task_name
        return f"{task_name} - {self.get_notification_type_display()} - {self.status}"

    def get_recipient_names(self):
        """获取收件人姓名列表"""
        if self.recipient_info:
            if isinstance(self.recipient_info, list):
                recipient_list = []
                for rec in self.recipient_info:
                    email = rec.get('email', '')
                    name = rec.get('name', '')
                    if name and email:
                        recipient_list.append(f"{name}({email})")
                    elif email:
                        recipient_list.append(email)
                    else:
                        recipient_list.append('未知用户')
                return ', '.join(recipient_list)
            elif isinstance(self.recipient_info, dict):
                email = self.recipient_info.get('email', '')
                name = self.recipient_info.get('name', '')
                if name and email:
                    return f"{name}({email})"
                elif email:
                    return email
                else:
                    return '未知用户'
        return "未知收件人"

    def get_retry_status(self):
        """获取重试状态"""
        if self.is_retried:
            return f"已重试 {self.retry_count} 次"
        return "未重试"


class UiTaskNotificationSetting(models.Model):
    """UI定时任务通知设置模型"""
    NOTIFICATION_TYPES = [
        ('email', '邮箱通知'),
        ('webhook', 'Webhook机器人'),
        ('both', '两种都发送'),
    ]

    task = models.ForeignKey(UiScheduledTask, on_delete=models.CASCADE, related_name='notification_settings',
                             verbose_name='关联任务')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='webhook',
                                         verbose_name='通知类型')
    notification_config = models.ForeignKey('core.UnifiedNotificationConfig', on_delete=models.SET_NULL,
                                            null=True, blank=True, related_name='ui_task_notification_settings',
                                            verbose_name='通知配置')
    is_enabled = models.BooleanField(default=False, verbose_name='是否启用通知')
    notify_on_success = models.BooleanField(default=True, verbose_name='成功时通知')
    notify_on_failure = models.BooleanField(default=True, verbose_name='失败时通知')
    notify_on_timeout = models.BooleanField(default=False, verbose_name='超时时通知')
    notify_on_error = models.BooleanField(default=True, verbose_name='错误时通知')
    custom_webhook_bots = models.JSONField(default=dict, blank=True, null=True, verbose_name='自定义Webhook机器人',
                                           help_text='临时覆盖通知配置中的Webhook机器人设置')
    custom_recipients = models.ManyToManyField(User, blank=True,
                                               related_name='ui_task_notification_settings_as_custom_recipient',
                                               verbose_name='自定义收件人', help_text='临时覆盖通知配置中的收件人设置')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'ui_task_notification_settings'
        verbose_name = 'UI任务通知设置'
        verbose_name_plural = 'UI任务通知设置'
        unique_together = ['task']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.task.name} - {self.get_notification_type_display()}"

    def get_active_notification_types(self):
        """获取当前激活的通知类型"""
        active_types = []
        if self.notification_type in ['email', 'both']:
            active_types.append('email')
        if self.notification_type in ['webhook', 'both']:
            active_types.append('webhook')
        return active_types

    def get_notification_config(self):
        """获取通知配置，优先使用任务自定义配置"""
        if self.notification_config:
            return self.notification_config
        # 如果没有指定配置，使用默认配置
        # 使用字符串引用避免循环导入
        from apps.core.models import UnifiedNotificationConfig
        return UnifiedNotificationConfig.objects.filter(is_default=True, is_active=True).first()


class AICase(models.Model):
    """AI测试用例"""
    project = models.ForeignKey(UiProject, on_delete=models.CASCADE, null=True, blank=True, verbose_name='所属项目')
    name = models.CharField(max_length=200, verbose_name='用例名称')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    task_description = models.TextField(verbose_name='任务描述', help_text='自然语言任务描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建者')

    class Meta:
        db_table = 'ui_ai_cases'
        verbose_name = 'AI测试用例'
        verbose_name_plural = 'AI测试用例'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class AIExecutionRecord(models.Model):
    """AI执行记录"""
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('running', '执行中'),
        ('passed', '成功'),
        ('failed', '失败'),
        ('stopped', '已停止'),
    ]

    project = models.ForeignKey(UiProject, on_delete=models.CASCADE, null=True, blank=True, verbose_name='所属项目')
    ai_case = models.ForeignKey(AICase, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联AI用例')
    case_name = models.CharField(max_length=200, verbose_name='用例名称快照')
    task_description = models.TextField(blank=True, default='', verbose_name='任务描述', help_text='用户输入的原始任务描述')
    execution_mode = models.CharField(max_length=20, choices=[('text', '文本模式')], default='text', verbose_name='执行模式')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='执行状态')
    start_time = models.DateTimeField(auto_now_add=True, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    duration = models.FloatField(null=True, blank=True, verbose_name='执行时长(秒)')
    logs = models.TextField(blank=True, default='', verbose_name='执行日志')
    steps_completed = models.JSONField(default=list, verbose_name='已完成步骤')
    planned_tasks = models.JSONField(default=list, verbose_name='规划任务') # 规划的任务列表 [{'id': 1, 'description': '...', 'status': 'pending'}]
    executed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='执行人')
    gif_path = models.CharField(max_length=500, null=True, blank=True, verbose_name='GIF录制路径')
    screenshots_sequence = models.JSONField(default=list, verbose_name='截图序列')

    class Meta:
        db_table = 'ui_ai_execution_records'
        verbose_name = 'AI测试报告'
        verbose_name_plural = 'AI测试报告'
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.case_name} - {self.get_status_display()}"
