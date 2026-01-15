from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render
import requests
from .models import AssistantSession, AssistantMessage, ChatMessage, DifyConfig
from .serializers import (
    AssistantSessionSerializer,
    AssistantSessionCreateSerializer,
    AssistantMessageSerializer,
    ChatMessageSerializer
)
from ..requirement_analysis.models import AIModelConfig


class AssistantSessionViewSet(viewsets.ModelViewSet):
    """智能助手会话视图集"""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AssistantSessionCreateSerializer
        return AssistantSessionSerializer

    def get_queryset(self):
        return AssistantSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def add_message(self, request, pk=None):
        """添加消息到会话"""
        session = self.get_object()
        serializer = AssistantMessageSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(session=session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """获取会话的聊天消息"""
        session = self.get_object()
        messages = session.chat_messages.all()
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)


class ChatViewSet(viewsets.ViewSet):
    """聊天功能ViewSet"""
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """发送消息到Dify API或指定的LLM模型"""
        session_id = request.data.get('session_id')
        message = request.data.get('message')
        model_id = request.data.get('model_id')
        dify_config_id = request.data.get('dify_config_id')

        if not session_id or not message:
            return Response(
                {'error': 'session_id和message都是必填项'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 获取会话
        try:
            session = AssistantSession.objects.get(
                session_id=session_id,
                user=request.user
            )
        except AssistantSession.DoesNotExist:
            return Response(
                {'error': '会话不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 确定要使用的配置
        ai_config = None
        dify_config = None

        # 优先检查用户指定的 AI 模型 (model_id)
        if model_id:
            try:
                ai_config = AIModelConfig.objects.get(id=model_id, is_active=True)
            except (AIModelConfig.DoesNotExist, ValueError):
                pass

        # 如果没有指定 AI 模型，检查是否指定了 Dify 配置 (dify_config_id)
        if not ai_config and dify_config_id:
            try:
                dify_config = DifyConfig.objects.get(id=dify_config_id)
            except (DifyConfig.DoesNotExist, ValueError):
                pass

        # 如果都没有指定，检查默认的 Active Dify 配置
        if not ai_config and not dify_config:
            dify_config = DifyConfig.get_active_config()

        # 如果既没有指定也能找到 Dify，尝试默认 AI 模型作为降级
        if not ai_config and not dify_config:
            try:
                ai_config = AIModelConfig.objects.filter(is_active=True).first()
            except ImportError:
                pass

        # 使用 AIModelConfig (指定的 或 默认的)
        if ai_config:
            # 保存用户消息
            user_message_obj = ChatMessage.objects.create(
                session=session,
                role='user',
                content=message,
                conversation_id=session.conversation_id
            )

            try:
                # 构建消息历史 (保持上下文) - 取最近10条
                # Django queryset不支持负索引，先按时间倒序取前10条，再反转
                history_messages = list(
                    session.chat_messages.all().order_by('-created_at').exclude(id=user_message_obj.id)[:10])
                history_messages.reverse()  # 恢复正序 (旧 -> 新)

                messages_payload = [{
                    "role": "system",
                    "content": "你是一个专业的软件测试助手(AI评测师)，可以协助用户进行测试用例分析、编写、评审以及回答一般的测试相关问题。"
                }]

                # History
                for msg in history_messages:
                    role = 'assistant' if msg.role == 'assistant' else 'user'
                    messages_payload.append({
                        "role": role,
                        "content": msg.content
                    })

                # Current Message
                messages_payload.append({
                    "role": "user",
                    "content": message
                })

                # 准备请求参数
                headers = {
                    'Authorization': f'Bearer {ai_config.api_key}',
                    'Content-Type': 'application/json'
                }

                # 确保base_url正确
                base_url = ai_config.base_url.rstrip('/')
                if not base_url.endswith('/chat/completions'):
                    if base_url.endswith('/v1'):
                        url = f"{base_url}/chat/completions"
                    else:
                        url = f"{base_url}/v1/chat/completions"
                else:
                    url = base_url

                payload = {
                    "model": ai_config.model_name,
                    "messages": messages_payload,
                    "temperature": ai_config.temperature,
                    "max_tokens": ai_config.max_tokens,
                    "stream": False
                }

                # 调用 LLM API
                response = requests.post(url, headers=headers, json=payload, timeout=60)

                if response.status_code == 200:
                    api_data = response.json()
                    answer_content = ""
                    if 'choices' in api_data and len(api_data['choices']) > 0:
                        answer_content = api_data['choices'][0]['message']['content']

                    # 保存助手回复
                    assistant_message = ChatMessage.objects.create(
                        session=session,
                        role='assistant',
                        content=answer_content,
                        conversation_id=session.conversation_id,
                        message_id=api_data.get('id')
                    )

                    return Response({
                        'user_message': ChatMessageSerializer(user_message_obj).data,
                        'assistant_message': ChatMessageSerializer(assistant_message).data,
                        'conversation_id': session.conversation_id,
                        'used_model': ai_config.name  # 返回使用的模型名称，便于前端展示
                    })
                else:
                    return Response({
                        'error': f'AI Model API错误: {response.status_code}',
                        'detail': response.text
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            except Exception as e:
                return Response({
                    'error': f'AI请求失败: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 使用 Dify 配置
        elif dify_config:
            # 保存用户消息
            user_message = ChatMessage.objects.create(
                session=session,
                role='user',
                content=message,
                conversation_id=session.conversation_id
            )

            try:
                # 调用Dify API
                headers = {
                    'Authorization': f'Bearer {dify_config.api_key}',
                    'Content-Type': 'application/json'
                }

                payload = {
                    'inputs': {},
                    'query': message,
                    'user': str(request.user.id),
                    'response_mode': 'blocking'
                }

                # 如果有conversation_id，添加到请求中以保持会话连续性
                if session.conversation_id:
                    payload['conversation_id'] = session.conversation_id

                # 去除URL末尾的斜杠
                api_url = dify_config.api_url.rstrip('/')

                response = requests.post(
                    f'{api_url}/chat-messages',
                    headers=headers,
                    json=payload,
                    timeout=60
                )

                if response.status_code == 200:
                    data = response.json()

                    # 更新会话的conversation_id
                    if 'conversation_id' in data and not session.conversation_id:
                        session.conversation_id = data['conversation_id']
                        session.save()

                    # 保存助手回复
                    assistant_message = ChatMessage.objects.create(
                        session=session,
                        role='assistant',
                        content=data.get('answer', ''),
                        conversation_id=data.get('conversation_id'),
                        message_id=data.get('message_id')
                    )

                    return Response({
                        'user_message': ChatMessageSerializer(user_message).data,
                        'assistant_message': ChatMessageSerializer(assistant_message).data,
                        'conversation_id': data.get('conversation_id'),
                        'used_model': 'Dify Knowledge Base'
                    })
                else:
                    return Response({
                        'error': f'Dify API错误: {response.status_code}',
                        'detail': response.text
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            except requests.exceptions.Timeout:
                return Response({
                    'error': 'API请求超时'
                }, status=status.HTTP_408_REQUEST_TIMEOUT)
            except requests.exceptions.RequestException as e:
                return Response({
                    'error': f'API请求失败: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 无可用配置
        else:
            return Response(
                {'error': '未配置Dify API，也未配置LLM模型，请先在配置中心配置'},
                status=status.HTTP_400_BAD_REQUEST
            )


def assistant_view(request):
    """智能助手页面视图 - 用于iframe内嵌"""
    return render(request, 'assistant/assistant.html')
