# https://newpanjing.github.io/simpleui_docs/config.html#%E5%9B%BE%E6%A0%87%E8%AF%B4%E6%98%8E

from pathlib import Path
from decouple import config
from django.core.exceptions import ImproperlyConfigured
import json
import os

BASE_DIR = Path(__file__).resolve().parent.parent


def parse_csv(value):
    return [item.strip() for item in value.split(',') if item.strip()]

SECRET_KEY = config('SECRET_KEY', default='django-insecure-your-secret-key-here')

DEBUG = config('DEBUG', default=True, cast=bool)

# 根据DEBUG模式设置ALLOWED_HOSTS，生产环境不应使用通配符
if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1',
                           cast=parse_csv)

DJANGO_APPS = [
    'simpleui',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',  # 添加JWT支持
    'rest_framework_simplejwt.token_blacklist',  # JWT token黑名单
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'channels',
]

ANALYTICS_ENABLED = config('ANALYTICS_ENABLED', default=False, cast=bool)
ANALYTICS_MAX_BATCH_SIZE = config('ANALYTICS_MAX_BATCH_SIZE', default=20, cast=int)
REGISTRATION_STATS_ENABLED = config('REGISTRATION_STATS_ENABLED', default=False, cast=bool)
REGISTRATION_STATS_VISIBLE_USERNAMES = config(
    'REGISTRATION_STATS_VISIBLE_USERNAMES',
    default='',
    cast=parse_csv,
)
APP_USE_HTTPS = config('APP_USE_HTTPS', default=not DEBUG, cast=bool)
TRUST_PROXY_SSL_HEADER = config('TRUST_PROXY_SSL_HEADER', default=APP_USE_HTTPS, cast=bool)

# MCP Server 总开关（协议端点 /api/mcp/，需 Daphne/ASGI 部署）
MCP_ENABLED = config('MCP_ENABLED', default=True, cast=bool)
# MCP 危险操作人工审批模式：开启后 confirm_* 不再直接执行，
# 转为等待 MCP 控制台人工批准（Agent 轮询 get_approval_status 取结果）
MCP_HUMAN_APPROVAL = config('MCP_HUMAN_APPROVAL', default=False, cast=bool)
# MCP 协议端点 Host 白名单追加项（逗号分隔）：SDK 的 DNS Rebinding 防护
MCP_ALLOWED_HOSTS = config('MCP_ALLOWED_HOSTS', default='')

# ---------- 监控中心（monitor）全局默认 ----------
# 自动监测持续 DOWN 时的重提醒周期、手动检测的冷却，均可在 .env 调整基线
MONITOR_DEFAULT_ALERT_REPEAT_INTERVAL = config(
    'MONITOR_DEFAULT_ALERT_REPEAT_INTERVAL', default=30, cast=int)
MONITOR_DEFAULT_MANUAL_ALERT_COOLDOWN = config(
    'MONITOR_DEFAULT_MANUAL_ALERT_COOLDOWN', default=5, cast=int)

LOCAL_APPS = [
    'apps.users',
    'apps.projects',
    'apps.testcases',
    'apps.testsuites',
    'apps.executions',
    'apps.reports',
    'apps.reviews',
    'apps.versions',
    'apps.defects',
    'apps.assistant',
    'apps.requirement_analysis',
    'apps.api_testing',
    'apps.ui_automation.apps.UiAutomationConfig',
    'apps.app_automation.apps.AppAutomationConfig',  # APP自动化测试
    'apps.core',
    'apps.data_factory',
    'apps.llm_judge',
    'apps.monitor',  # 监控中心
    'apps.perf_testing.apps.PerfTestingConfig',  # 性能测试
    'apps.mcp.apps.McpConfig',  # MCP Server（外部 Agent 驱动）
]

if ANALYTICS_ENABLED or REGISTRATION_STATS_ENABLED:
    LOCAL_APPS.append('apps.analytics')

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'backend.middleware.DisableCSRFMiddleware',  # 添加CSRF禁用中间件
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'
ASGI_APPLICATION = 'backend.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='testhub'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD', default=''),  # 移除硬编码默认密码
        'HOST': config('DB_HOST', default='127.0.0.1'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
# Supported language codes: 'en-us' (English), 'zh-hans' (Simplified Chinese), 'ja' (Japanese), 'ko' (Korean), etc.
# See: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for timezone list
LANGUAGE_CODE = config('LANGUAGE_CODE', default='zh-hans')
TIME_ZONE = config('TIME_ZONE', default='Asia/Shanghai')
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_files')

# 数据工厂的静态文件目录
STATIC_FILES_URL = '/static_files/'
STATIC_FILES_ROOT = os.path.join(BASE_DIR, 'static_files')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# DRF Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # JWT认证（优先）
        'rest_framework.authentication.TokenAuthentication',  # 保留Token认证（兼容）
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # access_token 60分钟
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),  # refresh_token 7天
    'ROTATE_REFRESH_TOKENS': True,  # 刷新时轮换refresh_token
    'BLACKLIST_AFTER_ROTATION': True,  # 旧的refresh_token加入黑名单
    'UPDATE_LAST_LOGIN': True,  # 更新最后登录时间

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# CSRF / Session Settings - 支持通过 .env 控制 HTTP/HTTPS
CSRF_USE_SESSIONS = config('CSRF_USE_SESSIONS', default=False, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=APP_USE_HTTPS, cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=APP_USE_HTTPS, cast=bool)
CSRF_COOKIE_HTTPONLY = config('CSRF_COOKIE_HTTPONLY', default=not DEBUG, cast=bool)
CSRF_COOKIE_SAMESITE = config('CSRF_COOKIE_SAMESITE', default='Lax')
SESSION_COOKIE_SAMESITE = config('SESSION_COOKIE_SAMESITE', default='Lax')

if TRUST_PROXY_SSL_HEADER:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# CORS Settings
cors_origins_str = config('CORS_ALLOWED_ORIGINS', default='')
parsed_cors_origins = parse_csv(cors_origins_str)

if DEBUG:
    # 开发环境默认允许本地地址，同时合并环境变量里的配置
    # 优先使用环境变量配置的地址，确保服务器IP优先级最高
    CORS_ALLOWED_ORIGINS = [
        *parsed_cors_origins,  # 环境变量配置的地址优先
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]
    CORS_ALLOW_CREDENTIALS = True
    # 支持EventSource (SSE) 的额外CORS头部
    CORS_ALLOW_HEADERS = [
        'accept',
        'accept-encoding',
        'authorization',
        'content-type',
        'dnt',
        'origin',
        'user-agent',
        'x-csrftoken',
        'x-requested-with',
        'cache-control',  # 添加 SSE 需要的头部
    ]
else:
    # 生产环境 CORS 配置
    if parsed_cors_origins:
        # 如果配置了 CORS_ALLOWED_ORIGINS，使用配置的值
        CORS_ALLOWED_ORIGINS = parsed_cors_origins
    else:
        # 如果未配置，允许所有来源（可根据需求调整）
        CORS_ALLOW_ALL_ORIGINS = True

    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_HEADERS = [
        'accept',
        'accept-encoding',
        'authorization',
        'content-type',
        'dnt',
        'origin',
        'user-agent',
        'x-csrftoken',
        'x-requested-with',
        'cache-control',  # 添加 SSE 需要的头部
    ]
    # SSE 需要的额外配置
    CORS_EXPOSE_HEADERS = ['Content-Type', 'Cache-Control']

# CSRF Settings
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000',
    cast=parse_csv,
)

# Spectacular Settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'TestHub API',
    'DESCRIPTION': 'Test Case Management Platform API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Redis URL (used across celery, channels, and SMS verification)
REDIS_URL = config('REDIS_URL', default='redis://:1234@127.0.0.1:6379/0')

# Celery Configuration
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Channels Configuration
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
        },
    },
}

# SMS Configuration (阿里云验证码短信，双通道)
# SMS_PROVIDER: dypns=号码认证服务「短信认证」(个人) | dysms=短信服务(企业签名)
# 两套 AccessKey/签名/模板互不通用；改 SMS_PROVIDER 需重启进程生效
SMS_PROVIDER = config('SMS_PROVIDER', default='dypns')

# 短信服务 dysms (SendSms)
SMS_ACCESS_KEY_ID = config('SMS_ACCESS_KEY_ID', default='')
SMS_ACCESS_KEY_SECRET = config('SMS_ACCESS_KEY_SECRET', default='')
SMS_SIGN_NAME = config('SMS_SIGN_NAME', default='杭州智穹云启科技')
SMS_REGISTER_TEMPLATE_CODE = config('SMS_REGISTER_TEMPLATE_CODE', default='SMS_133001115')

# 号码认证服务 dypns (SendSmsVerifyCode)
DYPNS_ACCESS_KEY_ID = config('DYPNS_ACCESS_KEY_ID', default='')
DYPNS_ACCESS_KEY_SECRET = config('DYPNS_ACCESS_KEY_SECRET', default='')
DYPNS_SIGN_NAME = config('DYPNS_SIGN_NAME', default='')
DYPNS_TEMPLATE_CODE = config('DYPNS_TEMPLATE_CODE', default='')

# 模板中除 code 之外的占位符，如时长占位 {"min":"5"}；以控制台模板内容为准
_DYPNS_EXTRA_RAW = config('DYPNS_TEMPLATE_PARAM_EXTRA', default='{}')
try:
    DYPNS_TEMPLATE_PARAM_EXTRA = json.loads(_DYPNS_EXTRA_RAW)
except ValueError:
    raise ImproperlyConfigured(
        f'DYPNS_TEMPLATE_PARAM_EXTRA 需是 JSON 对象字符串，如 {{"min":"5"}}，当前为 {_DYPNS_EXTRA_RAW!r}'
    )
if not isinstance(DYPNS_TEMPLATE_PARAM_EXTRA, dict):
    raise ImproperlyConfigured(
        f'DYPNS_TEMPLATE_PARAM_EXTRA 需是 JSON 对象，当前为 {_DYPNS_EXTRA_RAW!r}'
    )

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 默认缓存超时5分钟
    }
}

# Email Configuration
EMAIL_BACKEND = 'apps.api_testing.custom_email_backend.CustomEmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='webmaster@localhost')

# For 163 email with SSL, you might need this setting
EMAIL_TIMEOUT = 30

# 确保日志目录存在
log_dir = os.path.join(BASE_DIR, 'logs')
os.makedirs(log_dir, exist_ok=True)

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'app.log'),
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'error.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        # 其他具体模块的 logger 配置
        'django': {
            'handlers': ['file', 'error_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps.api_testing.views': {
            'handlers': ['file', 'error_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps.data_factory.tools.json_tools': {
            'handlers': ['file', 'error_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.data_factory.tools.encoding_tools': {
            'handlers': ['file', 'error_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.data_factory.tools': {
            'handlers': ['file', 'error_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps.analytics': {
            'handlers': ['file', 'error_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['file', 'error_file', 'console'],
        'level': 'INFO',
        # 'propagate': True,
    },
}

# 指定simpleui默认的主题,指定一个文件名，相对路径就从simpleui的theme目录读取
SIMPLEUI_DEFAULT_THEME = 'admin.lte.css'
# 是否显示图标
SIMPLEUI_DEFAULT_ICON = True
# 是否关闭登录页粒子效果
SIMPLEUI_LOGIN_PARTICLES = True
# 后台管理首页，可以是url或者html文件
# SIMPLEUI_HOME_PAGE = 'https://www.baidu.com/'  # 后面可以扩展为大屏显示做统计
# 自定义首页标题
# SIMPLEUI_HOME_TITLE = 'Dashboard'
# # 自定义首页图标 首页图标,支持element-ui和fontawesome的图标，参考https://fontawesome.com/icons图标
# SIMPLEUI_HOME_ICON = 'fa fa-gauge'
# 设置simpleui 点击首页图标跳转的地址
SIMPLEUI_INDEX = 'http://localhost:3000'
# 自定义后台的Logo
SIMPLEUI_LOGO = 'https://static.djangoproject.com/img/favicon.6dbf28c0650e.ico'
# 是否显示首页信息
SIMPLEUI_HOME_INFO = False
# 是否显示快捷入口
SIMPLEUI_HOME_QUICK = True
# 是否显示最近动作
SIMPLEUI_HOME_ACTION = True
# 使用分析
SIMPLEUI_ANALYSIS = False
# 离线模式
SIMPLEUI_STATIC_OFFLINE = True
# True或None 默认显示加载遮罩层，指定为False 不显示遮罩层。默认显示
SIMPLEUI_LOADING = True
# 设置菜单icon，参考https://element.eleme.cn/#/zh-CN/component/icon
SIMPLEUI_ICON = {
    # 一级菜单项
    '测试执行管理': 'el-icon-s-tools',
    '用户管理': 'el-icon-user-solid',
    '令牌黑名单': 'el-icon-warning-outline',
    '接口测试': 'el-icon-s-platform',
    '智能助手': 'el-icon-chat-dot-round',
    '用例评审管理': 'el-icon-edit-outline',
    '认证令牌': 'el-icon-key',
    '认证和授权': 'el-icon-s-check',
    '需求分析': 'el-icon-notebook-2',

    # 二级菜单项
    '测试执行': 'el-icon-s-operation',
    '测试执行历史': 'el-icon-time',
    '测试执行用例': 'el-icon-document',
    '测试计划': 'el-icon-document-checked',
    '用户': 'el-icon-user',
    '用户配置': 'el-icon-setting',
    'Blacklisted Tokens': 'el-icon-warning-outline',
    'Outstanding Tokens': 'el-icon-s-custom',
    'API请求': 'el-icon-s-promotion',
    'API集合': 'el-icon-s-grid',
    'API项目': 'el-icon-s-custom',
    '任务执行日志': 'el-icon-s-data',
    '定时任务': 'el-icon-time',
    '测试套件': 'el-icon-suitcase',
    '环境变量': 'el-icon-school',
    '请求历史': 'el-icon-odometer',
    '智能助手会话': 'el-icon-chat-dot-round',
    '智能助手消息': 'el-icon-message',
    '测试用例评审': 'el-icon-check',
    '评审分配': 'el-icon-guide',
    '评审意见': 'el-icon-s-custom',
    '评审模板': 'el-icon-document',
    'Tokens': 'el-icon-key',
    '组': 'el-icon-s-custom',
    '业务需求': 'el-icon-document-checked',
    '分析任务': 'el-icon-stopwatch',
    '生成的测试用例': 'el-icon-document',
    '需求文档': 'el-icon-document',
}

# 开发环境，暂时禁用迁移历史检查
# SILENCED_SYSTEM_CHECKS = ['django.db.migrations.InconsistentMigrationHistory']

# ==================== LLM 智能评分器配置 ====================
# 评分器 OpenAI 兼容配置（与平台既有 LLM 配置共用）
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
OPENAI_BASE_URL = config('OPENAI_BASE_URL', default=None)
# Judge 评分模型
JUDGE_MODEL = config('JUDGE_MODEL', default='deepseek-chat')
JUDGE_MOCK = config('JUDGE_MOCK', default=False, cast=bool)
JUDGE_N_RUNS = config('JUDGE_N_RUNS', default=3, cast=int)
JUDGE_CACHE_TIMEOUT = config('JUDGE_CACHE_TIMEOUT', default=3600, cast=int)
JUDGE_RULE_LLM_FALLBACK = config('JUDGE_RULE_LLM_FALLBACK', default=False, cast=bool)
# Rubric / KB 目录（放 MEDIA_ROOT 下）
JUDGE_RUBRIC_DIR = os.path.join(MEDIA_ROOT, 'judge_rubrics')
JUDGE_KB_DIR = os.path.join(MEDIA_ROOT, 'judge_kb')
os.makedirs(JUDGE_RUBRIC_DIR, exist_ok=True)
os.makedirs(JUDGE_KB_DIR, exist_ok=True)

# ==================== 性能测试模块配置 ====================
# 容量护栏：超过阈值时预检拦截，避免压力机自身成为瓶颈导致数据失真
PERF_MAX_CONCURRENCY = config('PERF_MAX_CONCURRENCY', default=1000, cast=int)
PERF_MAX_TARGET_RPS = config('PERF_MAX_TARGET_RPS', default=5000, cast=int)
PERF_MAX_DURATION = config('PERF_MAX_DURATION', default=7200, cast=int)  # 单次压测最长 2 小时
PERF_MAX_CONCURRENT_EXECUTIONS = config('PERF_MAX_CONCURRENT_EXECUTIONS', default=2, cast=int)

# 生产环境黑名单：base_url 命中则预检直接拦截，逗号分隔（支持后缀匹配）
PERF_FORBIDDEN_HOSTS = [
    h.strip() for h in config('PERF_FORBIDDEN_HOSTS', default='').split(',') if h.strip()
]

# 数据保留策略
PERF_RETENTION_DAYS = config('PERF_RETENTION_DAYS', default=90, cast=int)        # 执行记录
PERF_ARTIFACT_RETENTION_DAYS = config('PERF_ARTIFACT_RETENTION_DAYS', default=30, cast=int)  # 产物文件

# 压力机自监控告警阈值
PERF_LOAD_GEN_CPU_WARN = config('PERF_LOAD_GEN_CPU_WARN', default=85.0, cast=float)
