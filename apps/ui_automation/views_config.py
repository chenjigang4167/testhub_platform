from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import shutil
import subprocess
import platform
import os
import json
import logging

logger = logging.getLogger(__name__)

class EnvironmentConfigViewSet(viewsets.ViewSet):
    """
    UI自动化环境配置视图集
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def check_environment(self, request):
        """
        检测环境状态 (系统浏览器和Playwright浏览器)
        """
        import sys
        
        # 1. 检测系统浏览器 (Selenium常用)
        system_browsers_list = ['chrome', 'firefox', 'edge'] # Safari not on Windows usually
        if platform.system() == 'Darwin':
             system_browsers_list.append('safari')
             
        system_results = []

        is_windows = platform.system() == 'Windows'

        for browser in system_browsers_list:
            installed = False
            version = None
            install_cmd = ""
            
            if browser == 'chrome':
                if is_windows:
                    paths = [
                        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
                    ]
                    for p in paths:
                        if os.path.exists(p):
                            installed = True
                            break
                    install_cmd = "请下载 Chrome 安装包安装"
                else: # macOS
                    if os.path.exists('/Applications/Google Chrome.app'):
                        installed = True
                    install_cmd = "brew install --cask google-chrome"
                    
            elif browser == 'firefox':
                if is_windows:
                    paths = [
                        r"C:\Program Files\Mozilla Firefox\firefox.exe",
                        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
                    ]
                    for p in paths:
                        if os.path.exists(p):
                            installed = True
                            break
                    install_cmd = "请下载 Firefox 安装包安装"
                else:
                    if os.path.exists('/Applications/Firefox.app'):
                        installed = True
                    install_cmd = "brew install --cask firefox"
                    
            elif browser == 'safari':
                if not is_windows and os.path.exists('/Applications/Safari.app'):
                    installed = True
                install_cmd = "系统自带"
                
            elif browser == 'edge':
                if is_windows:
                    paths = [
                         r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                         r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
                    ]
                    for p in paths:
                        if os.path.exists(p):
                            installed = True
                            break
                    install_cmd = "请下载 Edge 安装包安装"
                else:
                    if os.path.exists('/Applications/Microsoft Edge.app'):
                        installed = True
                    install_cmd = "brew install --cask microsoft-edge"

            system_results.append({
                'name': browser,
                'installed': installed,
                'version': version, # Version check omitted for simplicity/performance
                'install_cmd': install_cmd
            })

        # 2. 检测Playwright浏览器
        playwright_browsers_list = ['chromium', 'firefox', 'webkit']
        playwright_results = []
        
        # Playwright 缓存路径
        if is_windows:
            playwright_cache_dir = os.path.join(os.environ.get('LOCALAPPDATA'), 'ms-playwright')
        else:
            playwright_cache_dir = os.path.expanduser('~/Library/Caches/ms-playwright')
        
        # 调试信息：打印缓存路径
        print(f"Playwright cache dir: {playwright_cache_dir}")

        for browser in playwright_browsers_list:
            installed = False
            version = None
            install_cmd = f"playwright install {browser}"
            
            # 检查缓存目录中是否有对应的浏览器文件夹
            if os.path.exists(playwright_cache_dir):
                for dirname in os.listdir(playwright_cache_dir):
                    # 匹配规则: chromium-123456, firefox-1234, webkit-1234
                    # 注意: 有时候是 chromium-vxxxx
                    if dirname.startswith(browser + '-'):
                        installed = True
                        version = dirname.split('-')[-1]
                        break
            
            playwright_results.append({
                'name': browser,
                'installed': installed,
                'version': version,
                'install_cmd': install_cmd
            })

        return Response({
            'os': platform.system(),
            'system_browsers': system_results,
            'playwright_browsers': playwright_results
        })

    @action(detail=False, methods=['post'])
    def install_driver(self, request):
        """
        安装浏览器驱动
        """
        browser = request.data.get('browser')
        if not browser:
            return Response({'error': 'Browser name is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 使用当前 Python 环境执行模块安装命令
            import sys
            subprocess.run([sys.executable, '-m', 'playwright', 'install', browser], check=True)
            return Response({'message': f'Successfully installed driver for {browser}'})
        except subprocess.CalledProcessError as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


import requests
from apps.requirement_analysis.models import AIModelConfig

class AIIntelligentModeConfigViewSet(viewsets.ViewSet):
    """
    AI智能模式配置视图集 (Browser-use) - 使用ModelViewSet支持标准CRUD
    """
    permission_classes = [IsAuthenticated]
    queryset = AIModelConfig.objects.filter(role='browser_use_text')

    def list(self, request):
        """
        获取所有AI智能模式配置列表
        """
        configs = self.queryset.order_by('-created_at')
        serializer_data = [{
            'id': config.id,
            'name': config.name,
            'model_type': config.model_type,
            'model_name': config.model_name,
            'base_url': config.base_url,
            'is_active': config.is_active,
            'api_key_length': len(config.api_key) if config.api_key else 0,  # 返回API Key长度用于生成掩码
            'created_at': config.created_at,
            'updated_at': config.updated_at
        } for config in configs]
        return Response(serializer_data)

    def create(self, request):
        """
        创建新的AI智能模式配置
        """
        data = request.data
        user = request.user

        # 验证必填字段
        required_fields = ['name', 'model_type', 'model_name', 'api_key']
        for field in required_fields:
            if not data.get(field):
                return Response(
                    {'error': f'{field} is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 如果创建时启用，先禁用其他所有配置
        if data.get('is_active', True):
            self.queryset.filter(is_active=True).update(is_active=False)

        # 创建新配置
        config = AIModelConfig.objects.create(
            name=data['name'],
            model_type=data['model_type'],
            role='browser_use_text',
            model_name=data['model_name'],
            api_key=data['api_key'],
            base_url=data.get('base_url', ''),
            is_active=data.get('is_active', True),
            created_by=user
        )

        return Response({
            'id': config.id,
            'name': config.name,
            'model_type': config.model_type,
            'model_name': config.model_name,
            'base_url': config.base_url,
            'is_active': config.is_active,
            'created_at': config.created_at
        }, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """
        获取单个配置详情
        """
        try:
            config = self.queryset.get(pk=pk)
            return Response({
                'id': config.id,
                'name': config.name,
                'model_type': config.model_type,
                'model_name': config.model_name,
                'base_url': config.base_url,
                'is_active': config.is_active,
                'created_at': config.created_at,
                'updated_at': config.updated_at
            })
        except AIModelConfig.DoesNotExist:
            return Response(
                {'error': 'Config not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request, pk=None):
        """
        更新配置 (PUT)
        """
        try:
            config = self.queryset.get(pk=pk)
            data = request.data

            # 如果启用此配置，先禁用其他所有配置
            new_is_active = data.get('is_active', config.is_active)
            disabled_config_names = []
            if new_is_active:
                # 查找将被禁用的配置
                active_configs = self.queryset.exclude(pk=pk).filter(is_active=True)
                disabled_config_names = [c.name for c in active_configs]
                # 先禁用其他所有配置（不包括当前配置），避免唯一约束冲突
                active_configs.update(is_active=False)

            # 更新字段
            if 'name' in data:
                config.name = data['name']
            if 'model_type' in data:
                config.model_type = data['model_type']
            if 'model_name' in data:
                config.model_name = data['model_name']
            if 'api_key' in data and data['api_key']:
                config.api_key = data['api_key']
            if 'base_url' in data:
                config.base_url = data['base_url']
            if 'is_active' in data:
                config.is_active = data['is_active']

            config.save()

            response_data = {
                'id': config.id,
                'name': config.name,
                'model_type': config.model_type,
                'model_name': config.model_name,
                'base_url': config.base_url,
                'is_active': config.is_active,
                'created_at': config.created_at,
                'updated_at': config.updated_at
            }

            # 如果禁用了其他配置,返回被禁用的配置名称
            if disabled_config_names:
                response_data['disabled_configs'] = disabled_config_names

            return Response(response_data)
        except AIModelConfig.DoesNotExist:
            return Response(
                {'error': 'Config not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def partial_update(self, request, pk=None):
        """
        部分更新配置 (PATCH)
        """
        return self.update(request, pk)

    def destroy(self, request, pk=None):
        """
        删除配置
        """
        try:
            config = self.queryset.get(pk=pk)
            config.delete()
            return Response(
                {'message': 'Config deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except AIModelConfig.DoesNotExist:
            return Response(
                {'error': 'Config not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'], url_path='test_connection')
    def test_connection_preview(self, request):
        """
        测试模型连接 (在保存前测试，不保存配置)
        """
        provider = request.data.get('provider')
        base_url = request.data.get('base_url')
        api_key = request.data.get('api_key')
        model_name = request.data.get('model_name')

        if not api_key:
            return Response(
                {'error': 'API Key is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 默认Base URL处理
        if not base_url:
            if provider == 'openai':
                base_url = 'https://api.openai.com/v1'
            elif provider == 'siliconflow':
                base_url = 'https://api.siliconflow.cn/v1'
            elif provider == 'deepseek':
                base_url = 'https://api.deepseek.com'
            elif provider == 'anthropic':
                base_url = 'https://api.anthropic.com'

        if not base_url:
             return Response(
                 {'error': 'Base URL is required for this provider'},
                 status=status.HTTP_400_BAD_REQUEST
             )

        base_url = base_url.rstrip('/')

        try:
            # 尝试调用 chat completions 接口 (OpenAI Compatible)
            url = f"{base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": model_name,
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 1
            }

            logger.info(f"AI智能模式预览 - 发送POST请求到: {url}")
            # 增加超时时间：连接超时60秒，读取超时900秒
            response = requests.post(url, headers=headers, json=data, timeout=(60, 900))

            logger.info(f"AI智能模式预览 - 收到响应: status_code={response.status_code}")

            if response.status_code == 200:
                return Response({'message': '连接成功'})
            else:
                logger.error(f"AI智能模式 - API调用返回错误: Status={response.status_code}, Body={response.text}")
                return Response(
                    {'error': f'连接失败: {response.status_code} - {response.text}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except requests.exceptions.Timeout as e:
            logger.error(f"AI智能模式 - API连接测试超时: {repr(e)}")
            return Response(
                {'error': '连接测试超时: 请检查网络连接或API地址是否正确'},
                status=status.HTTP_408_REQUEST_TIMEOUT
            )
        except Exception as e:
            logger.error(f"AI智能模式 - API连接测试异常: {repr(e)}")
            return Response(
                {'error': f'连接异常: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """
        测试已保存配置的连接
        """
        try:
            config = self.queryset.get(pk=pk)
        except AIModelConfig.DoesNotExist:
            return Response(
                {'error': 'Config not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        logger.info(f"=== AI智能模式 - 开始测试模型连接 ===")
        logger.info(f"模型类型: {config.model_type}")
        logger.info(f"模型名称: {config.model_name}")
        logger.info(f"API URL: {config.base_url}")
        logger.info(f"API Key前缀: {config.api_key[:10]}..." if len(config.api_key) > 10 else f"API Key: {config.api_key}")

        base_url = config.base_url
        if not base_url:
            # 使用默认Base URL
            provider = config.model_type
            if provider == 'openai':
                base_url = 'https://api.openai.com/v1'
            elif provider == 'siliconflow':
                base_url = 'https://api.siliconflow.cn/v1'
            elif provider == 'deepseek':
                base_url = 'https://api.deepseek.com'
            elif provider == 'anthropic':
                base_url = 'https://api.anthropic.com'

        if not base_url:
            return Response(
                {'error': 'Base URL is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        base_url = base_url.rstrip('/')

        try:
            url = f"{base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": config.model_name,
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 1
            }

            logger.info(f"AI智能模式 - 发送POST请求到: {url}")
            # 增加超时时间：连接超时60秒，读取超时900秒
            response = requests.post(url, headers=headers, json=data, timeout=(60, 900))

            logger.info(f"AI智能模式 - 收到响应: status_code={response.status_code}")

            if response.status_code == 200:
                logger.info("AI智能模式 - API连接测试成功")
                return Response({'message': '连接成功'})
            else:
                logger.error(f"AI智能模式 - API调用返回错误: Status={response.status_code}, Body={response.text}")
                return Response(
                    {'error': f'连接失败: {response.status_code} - {response.text}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except requests.exceptions.Timeout as e:
            logger.error(f"AI智能模式 - API连接测试超时: {repr(e)}")
            return Response(
                {'error': '连接测试超时: 请检查网络连接或API地址是否正确'},
                status=status.HTTP_408_REQUEST_TIMEOUT
            )
        except Exception as e:
            logger.error(f"AI智能模式 - API连接测试异常: {repr(e)}")
            return Response(
                {'error': f'连接异常: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
