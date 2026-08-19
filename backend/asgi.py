"""
ASGI config for backend project.
支持 Daphne (WebSocket) 和 runserver (仅 HTTP) 两种模式
"""

import os
import logging

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

django_asgi_app = get_asgi_application()

logger = logging.getLogger(__name__)


class _HttpRouter:
    """HTTP 分流：MCP 协议端点精确路径走 MCP 桥，其余交给 Django。

    懒导入 mcp_bridge：import apps.mcp.server 不会初始化 MCP 实例，
    仅在首个 MCP 请求到达时才构建 FastMCP，避免拖慢启动。
    MCP_ENABLED=False 时不分流，请求落到 Django 兜底视图返回 403。
    """

    def __init__(self, django_app):
        self.django_app = django_app

    async def __call__(self, scope, receive, send):
        from django.conf import settings as django_settings
        if (
            scope.get('type') == 'http'
            and scope.get('path') in ('/api/mcp', '/api/mcp/')
            and getattr(django_settings, 'MCP_ENABLED', True)
        ):
            from apps.mcp.server import mcp_bridge
            await mcp_bridge(scope, receive, send)
            return
        await self.django_app(scope, receive, send)


try:
    from channels.auth import AuthMiddlewareStack
    from channels.routing import ProtocolTypeRouter, URLRouter
    from apps.app_automation import routing as app_automation_routing

    application = ProtocolTypeRouter({
        "http": _HttpRouter(django_asgi_app),
        "websocket": AuthMiddlewareStack(
            URLRouter(app_automation_routing.websocket_urlpatterns)
        ),
    })
    logger.info("ASGI 已启用 WebSocket 支持 (需通过 Daphne 启动)")
except ImportError:
    application = django_asgi_app
    logger.warning("channels 未安装，WebSocket 不可用，仅支持 HTTP")
except Exception as e:
    application = django_asgi_app
    logger.warning(f"WebSocket 初始化失败: {e}，降级为仅 HTTP 模式")

# 无 channels 降级时也要保证 MCP 协议端点分流可用
if application is django_asgi_app:
    application = _HttpRouter(django_asgi_app)