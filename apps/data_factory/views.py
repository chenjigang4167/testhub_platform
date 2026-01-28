"""
数据工厂API视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse

from pathlib import Path

from .models import DataFactoryRecord
from .serializers import DataFactoryRecordSerializer, ToolExecuteSerializer
from .tool_list import get_categories
from .tools.string_tools import StringTools
from .tools.encoding_tools import EncodingTools
from .tools.random_tools import RandomTools
from .tools.encryption_tools import EncryptionTools
from .tools.test_data_tools import TestDataTools
from .tools.json_tools import JsonTools
from .tools.crontab_tools import CrontabTools
from .tools.image_tools import ImageTools


class DataFactoryPagination(PageNumberPagination):
    """数据工厂自定义分页"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class DataFactoryViewSet(viewsets.ModelViewSet):
    """数据工厂视图集"""
    queryset = DataFactoryRecord.objects.all()
    serializer_class = DataFactoryRecordSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DataFactoryPagination

    def get_queryset(self):
        """获取当前用户的记录"""
        queryset = super().get_queryset()
        # 只选择必要的字段，减少内存使用
        return queryset.filter(user=self.request.user).only(
            'id', 'user', 'tool_name', 'tool_category', 'tool_scenario',
            'input_data', 'output_data', 'is_saved', 'tags', 'created_at', 'updated_at'
        ).order_by('-created_at')

    def filter_queryset(self, queryset):
        """自定义过滤逻辑，支持JSONField的过滤"""
        queryset = super().filter_queryset(queryset)

        # 支持tags字段的过滤（JSONField）
        tags_contains = self.request.query_params.get('tags__contains')
        if tags_contains:
            # 使用JSON查询过滤包含指定标签的记录
            queryset = queryset.filter(tags__contains=tags_contains)

        # 支持tool_name的模糊查询
        tool_name_icontains = self.request.query_params.get('tool_name__icontains')
        if tool_name_icontains:
            queryset = queryset.filter(tool_name__icontains=tool_name_icontains)

        # 支持tool_category的精确过滤
        tool_category = self.request.query_params.get('tool_category')
        if tool_category:
            queryset = queryset.filter(tool_category=tool_category)

        return queryset

    def list(self, request, *args, **kwargs):
        """重写list方法以正确处理分页"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Error in list method: {str(e)}', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        """执行工具并保存结果"""
        serializer = ToolExecuteSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            result = self.execute_tool(
                data['tool_name'],
                data['tool_category'],
                data['input_data']
            )

            if 'error' in result:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            if data.get('is_saved', True):
                try:
                    record = DataFactoryRecord.objects.create(
                        user=request.user,
                        tool_name=data['tool_name'],
                        tool_category=data['tool_category'],
                        tool_scenario=data['tool_scenario'],
                        input_data=data['input_data'],
                        output_data=result,
                        is_saved=data.get('is_saved', True),
                        tags=data.get('tags', None)
                    )
                    result['record_id'] = str(record.id)
                    result['created_at'] = record.created_at.isoformat()
                except Exception as e:
                    return Response({'error': f'保存记录失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response(result, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def execute_tool(self, tool_name: str, tool_category: str, input_data: dict):
        """执行工具"""
        try:
            # 字符工具
            if tool_category == 'string':
                return self.execute_string_tool(tool_name, input_data)
            # 编码工具
            elif tool_category == 'encoding':
                return self.execute_encoding_tool(tool_name, input_data)
            # 随机工具
            elif tool_category == 'random':
                return self.execute_random_tool(tool_name, input_data)
            # 加密工具
            elif tool_category == 'encryption':
                return self.execute_encryption_tool(tool_name, input_data)
            # 测试数据（包含测试数据和Mock数据）
            elif tool_category == 'test_data':
                if tool_name.startswith('mock_'):
                    return self.execute_mock_tool(tool_name, input_data)
                else:
                    return self.execute_test_data_tool(tool_name, input_data)
            # JSON工具
            elif tool_category == 'json':
                return self.execute_json_tool(tool_name, input_data)
            # Crontab工具
            elif tool_category == 'crontab':
                return self.execute_crontab_tool(tool_name, input_data)
            else:
                return {'error': f'不支持的工具分类: {tool_category}'}
        except Exception as e:
            return {'error': f'工具执行失败: {str(e)}'}

    def execute_string_tool(self, tool_name: str, input_data: dict | str):
        """执行字符工具"""
        tool_mapping = {
            'remove_whitespace': StringTools.remove_whitespace,
            'replace_string': StringTools.replace_string,
            'escape_string': StringTools.escape_string,
            'unescape_string': StringTools.unescape_string,
            'word_count': StringTools.word_count,
            'text_diff': StringTools.text_diff,
            'regex_test': StringTools.regex_test,
            'case_convert': StringTools.case_convert,
            'string_format': StringTools.string_format
        }

        if tool_name not in tool_mapping:
            return {'error': f'不支持的字符工具: {tool_name}'}
        # 如果 input_data 是字符串，包装为 {'text': input_data}
        if isinstance(input_data, str):
            if tool_name in ['remove_whitespace', 'word_count', 'text_diff', 'string_format']:
                input_data = {'text': input_data}
            elif tool_name == 'regex_test':
                # 需要pattern和text，尝试解析
                input_data = {'pattern': input_data, 'text': ''}
            elif tool_name in ['case_convert']:
                input_data = {'text': input_data, 'convert_type': 'upper'}
            else:
                input_data = {'text': input_data}

        return tool_mapping[tool_name](**input_data)

    def execute_encoding_tool(self, tool_name: str, input_data: dict | str):
        """执行编码工具"""
        tool_mapping = {
            'generate_barcode': EncodingTools.generate_barcode,
            'generate_qrcode': EncodingTools.generate_qrcode,
            'decode_qrcode': EncodingTools.decode_qrcode,
            'timestamp_convert': EncodingTools.timestamp_convert,
            'base_convert': EncodingTools.base_convert,
            'unicode_convert': EncodingTools.unicode_convert,
            'ascii_convert': EncodingTools.ascii_convert,
            'color_convert': EncodingTools.color_convert,
            'base64_encode': EncodingTools.base64_encode,
            'base64_decode': EncodingTools.base64_decode,
            'url_encode': EncodingTools.url_encode,
            'url_decode': EncodingTools.url_decode,
            'jwt_decode': EncodingTools.jwt_decode,
            'image_to_base64': ImageTools.image_to_base64,
            'base64_to_image': ImageTools.base64_to_image
        }

        if tool_name not in tool_mapping:
            return {'error': f'不支持的编码工具: {tool_name}'}

        # 处理字符串输入
        if isinstance(input_data, str):
            if tool_name == 'timestamp_convert':
                input_data = {'timestamp': input_data, 'convert_type': 'to_datetime'}
            elif tool_name in ['base_convert', 'unicode_convert', 'ascii_convert', 'color_convert']:
                input_data = {'text': input_data}
            elif tool_name in ['base64_encode', 'base64_decode']:
                input_data = {'text': input_data, 'encoding': 'utf-8'}
            elif tool_name in ['url_encode', 'url_decode']:
                input_data = {'data': input_data, 'encoding': 'utf-8'}
            elif tool_name == 'jwt_decode':
                input_data = {'token': input_data, 'verify': False}
            elif tool_name in ['generate_barcode', 'generate_qrcode']:
                input_data = {'data': input_data}
            elif tool_name == 'decode_qrcode':
                input_data = {'image_data': input_data, 'image_format': 'png'}
            elif tool_name == 'image_to_base64':
                input_data = {'image_data': input_data, 'image_format': 'png', 'include_prefix': True}
            elif tool_name == 'base64_to_image':
                input_data = {'base64_str': input_data}
            else:
                input_data = {'text': input_data}
        return tool_mapping[tool_name](**input_data)

    def execute_random_tool(self, tool_name: str, input_data: dict | str):
        """执行随机工具"""
        tool_mapping = {
            'random_int': RandomTools.random_int,
            'random_float': RandomTools.random_float,
            'random_string': RandomTools.random_string,
            'random_uuid': RandomTools.random_uuid,
            'random_mac_address': RandomTools.random_mac_address,
            'random_ip_address': RandomTools.random_ip_address,
            'random_date': RandomTools.random_date,
            'random_boolean': RandomTools.random_boolean,
            'random_color': RandomTools.random_color,
            'random_password': RandomTools.random_password,
            'random_sequence': RandomTools.random_sequence
        }

        if tool_name not in tool_mapping:
            return {'error': f'不支持的随机工具: {tool_name}'}
        # 处理字符串输入 - 大部分随机工具不需要输入，直接返回空字典
        if isinstance(input_data, str):
            if tool_name == 'random_int':
                input_data = {'min_val': 1, 'max_val': 100, 'count': 1}
            elif tool_name == 'random_float':
                input_data = {'min_val': 0.0, 'max_val': 1.0, 'precision': 2, 'count': 1}
            elif tool_name == 'random_string':
                input_data = {'length': 8, 'char_type': 'all', 'count': 1}
            elif tool_name == 'random_uuid':
                input_data = {'version': 4, 'count': 1}
            elif tool_name == 'random_mac_address':
                input_data = {'separator': ':', 'count': 1}
            elif tool_name == 'random_ip_address':
                input_data = {'ip_version': 4, 'count': 1}
            elif tool_name == 'random_date':
                input_data = {'start_date': '2024-01-01', 'end_date': '2024-12-31', 'count': 1}
            elif tool_name == 'random_boolean':
                input_data = {'count': 1}
            elif tool_name == 'random_color':
                input_data = {'format': 'hex', 'count': 1}
            elif tool_name == 'random_password':
                input_data = {'length': 12, 'include_uppercase': True, 'include_lowercase': True,
                              'include_digits': True, 'include_special': True}
            elif tool_name == 'random_sequence':
                input_data = {'sequence': [], 'count': 1, 'unique': False}
            else:
                input_data = {'count': 1}
        return tool_mapping[tool_name](**input_data)

    def execute_encryption_tool(self, tool_name: str, input_data: dict | str):
        """执行加密工具"""
        tool_mapping = {
            'md5_hash': EncryptionTools.md5_hash,
            'sha1_hash': EncryptionTools.sha1_hash,
            'sha256_hash': EncryptionTools.sha256_hash,
            'sha512_hash': EncryptionTools.sha512_hash,
            'hash_comparison': EncryptionTools.hash_comparison,
            'aes_encrypt': EncryptionTools.aes_encrypt,
            'aes_decrypt': EncryptionTools.aes_decrypt,
            'password_strength': EncryptionTools.password_strength,
            'generate_salt': EncryptionTools.generate_salt
        }

        if tool_name not in tool_mapping:
            return {'error': f'不支持的加密工具: {tool_name}'}
        # 处理字符串输入
        if isinstance(input_data, str):
            if tool_name in ['md5_hash', 'sha1_hash', 'sha256_hash', 'sha512_hash',
                             'password_strength', 'generate_salt']:
                input_data = {'text': input_data}
            elif tool_name == 'hash_comparison':
                input_data = {'text': input_data, 'hash_value': ''}
            elif tool_name in ['aes_encrypt', 'aes_decrypt']:
                input_data = {'text': input_data, 'password': 'default_password', 'mode': 'CBC'}
            else:
                input_data = {'text': input_data}
        return tool_mapping[tool_name](**input_data)

    def execute_test_data_tool(self, tool_name: str, input_data: dict | str):
        """执行测试数据工具"""
        tool_mapping = {
            'generate_chinese_name': TestDataTools.generate_chinese_name,
            'generate_chinese_phone': TestDataTools.generate_chinese_phone,
            'generate_chinese_email': TestDataTools.generate_chinese_email,
            'generate_chinese_address': TestDataTools.generate_chinese_address,
            'generate_id_card': TestDataTools.generate_id_card,
            'generate_company_name': TestDataTools.generate_company_name,
            'generate_bank_card': TestDataTools.generate_bank_card,
            'generate_user_profile': TestDataTools.generate_user_profile,
            'generate_hk_id_card': TestDataTools.generate_hk_id_card,
            'generate_business_license': TestDataTools.generate_business_license,
            'generate_coordinates': TestDataTools.generate_coordinates
        }

        if tool_name not in tool_mapping:
            return {'error': f'不支持的测试数据工具: {tool_name}'}
        # 处理字符串输入 - 测试数据工具大部分不需要输入参数
        if isinstance(input_data, str):
            if tool_name in ['generate_chinese_name', 'generate_chinese_phone', 'generate_chinese_email',
                             'generate_chinese_address', 'generate_id_card', 'generate_company_name',
                             'generate_bank_card', 'generate_hk_id_card', 'generate_business_license',
                             'generate_coordinates']:
                input_data = {'count': 1}
            elif tool_name == 'generate_user_profile':
                input_data = {'count': 1}
            else:
                input_data = {'count': 1}
        return tool_mapping[tool_name](**input_data)

    def execute_json_tool(self, tool_name: str, input_data: dict | str):
        """执行JSON工具"""
        tool_mapping = {
            'format_json': JsonTools.format_json,
            'validate_json': JsonTools.validate_json,
            'json_to_xml': JsonTools.json_to_xml,
            'xml_to_json': JsonTools.xml_to_json,
            'json_to_yaml': JsonTools.json_to_yaml,
            'yaml_to_json': JsonTools.yaml_to_json,
            'json_diff_enhanced': JsonTools.json_diff_enhanced,
            'jsonpath_query': JsonTools.jsonpath_query,
            'json_path_list': JsonTools.json_path_list,
            'json_flatten': JsonTools.json_flatten
        }

        if tool_name not in tool_mapping:
            return {'error': f'不支持的JSON工具: {tool_name}'}

        # 处理字符串输入
        if isinstance(input_data, str):
            if tool_name in ['format_json', 'validate_json', 'json_to_xml', 'json_to_yaml', 'json_path_list',
                             'json_flatten']:
                input_data = {'json_str': input_data}
            elif tool_name == 'xml_to_json':
                input_data = {'xml_str': input_data}
            elif tool_name == 'yaml_to_json':
                input_data = {'yaml_str': input_data}
            elif tool_name == 'json_diff_enhanced':
                input_data = {'json_str1': input_data, 'json_str2': ''}
            elif tool_name == 'jsonpath_query':
                input_data = {'json_str': input_data, 'jsonpath_expr': ''}
            else:
                input_data = {'json_str': input_data}
        return tool_mapping[tool_name](**input_data)

    # def execute_mock_tool(self, tool_name: str, input_data: dict | str):
    #     """执行Mock数据工具"""
    #     tool_mapping = {
    #         'mock_string': JsonTools.mock_data,
    #         'mock_number': JsonTools.mock_data,
    #         'mock_boolean': JsonTools.mock_data,
    #         'mock_email': JsonTools.mock_data,
    #         'mock_phone': JsonTools.mock_data,
    #         'mock_date': JsonTools.mock_data,
    #         'mock_datetime': JsonTools.mock_data,
    #         'mock_name': JsonTools.mock_data,
    #         'mock_address': JsonTools.mock_data,
    #         'mock_url': JsonTools.mock_data,
    #         'mock_uuid': JsonTools.mock_data,
    #         'mock_ip': JsonTools.mock_data
    #     }
    #
    #     if tool_name not in tool_mapping:
    #         return {'error': f'不支持的Mock工具: {tool_name}'}
    #
    #     data_type = tool_name.replace('mock_', '')
    #
    #     if isinstance(input_data, str):
    #         input_data = {'data_type': data_type, 'count': 1}
    #     else:
    #         input_data['data_type'] = data_type
    #
    #     return tool_mapping[tool_name](**input_data)

    def execute_crontab_tool(self, tool_name: str, input_data: dict | str):
        """执行Crontab工具"""
        tool_mapping = {
            'generate_expression': CrontabTools.generate_expression,
            'parse_expression': CrontabTools.parse_expression,
            'get_next_runs': CrontabTools.get_next_runs,
            'validate_expression': CrontabTools.validate_expression
        }

        if tool_name not in tool_mapping:
            return {'error': f'不支持的Crontab工具: {tool_name}'}

        if isinstance(input_data, str):
            if tool_name == 'generate_expression':
                input_data = {'minute': '*', 'hour': '*', 'day': '*', 'month': '*', 'weekday': '*'}
            elif tool_name == 'parse_expression':
                input_data = {'expression': input_data}
            elif tool_name == 'get_next_runs':
                input_data = {'expression': input_data, 'count': 10}
            elif tool_name == 'validate_expression':
                input_data = {'expression': input_data}
            else:
                input_data = {'expression': input_data}
        return tool_mapping[tool_name](**input_data)

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """获取所有工具分类"""
        from .tool_list import get_categories, get_tool_list

        categories = get_categories()

        # 为每个分类添加工具列表
        tool_list = get_tool_list()
        for category in categories:
            category['tools'] = [tool for tool in tool_list if tool['scenario'] == category['scenario']]

        return Response({
            'categories': categories,
            'total_tools': sum(len(cat['tools']) for cat in categories)
        })

    @action(detail=False, methods=['get'])
    def tags(self, request):
        """获取所有标签列表"""
        try:
            from django.db.models import Q

            # 获取当前用户的所有记录
            queryset = DataFactoryRecord.objects.filter(user=request.user)

            # 获取所有唯一的标签
            tag_set = set()
            for record in queryset:
                if record.tags and isinstance(record.tags, list):
                    tag_set.update(record.tags)

            tags = sorted(list(tag_set))

            return Response({
                'tags': tags,
                'count': len(tags)
            })
        except Exception as e:
            return Response(
                {'error': f'获取标签列表失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def batch_generate(self, request):
        """批量生成数据"""
        tool_name = request.data.get('tool_name')
        tool_category = request.data.get('tool_category')
        tool_scenario = request.data.get('tool_scenario')
        count = request.data.get('count', 10)
        input_data = request.data.get('input_data', {})

        if not tool_name or not tool_category:
            return Response(
                {'error': '缺少必要参数: tool_name 或 tool_category'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 批量生成
        results = []
        for i in range(count):
            result = self.execute_tool(tool_name, tool_category, input_data)
            if 'error' not in result:
                results.append(result)

        # 保存记录
        if request.data.get('is_saved', True):
            record = DataFactoryRecord.objects.create(
                user=request.user,
                tool_name=tool_name,
                tool_category=tool_category,
                tool_scenario=tool_scenario,
                input_data=input_data,
                output_data={'results': results, 'count': len(results)},
                is_saved=True
            )

        return Response({
            'results': results,
            'count': len(results),
            'total_requested': count
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取使用统计"""
        user_records = self.get_queryset()

        # 按分类统计
        category_stats = {}
        for cat_name, cat_display in DataFactoryRecord.TOOL_CATEGORIES:
            count = user_records.filter(tool_category=cat_name).count()
            category_stats[cat_display] = count

        # 按场景统计
        scenario_stats = {}
        for sce_name, sce_display in DataFactoryRecord.TOOL_SCENARIOS:
            count = user_records.filter(tool_scenario=sce_name).count()
            scenario_stats[sce_display] = count

        # 最近使用
        recent_tools = []
        for record in user_records[:10]:
            recent_tools.append({
                'tool_name': record.tool_name,
                'tool_category_display': record.get_tool_category_display(),
                'tool_scenario_display': record.get_tool_scenario_display(),
                'created_at': record.created_at
            })

        return Response({
            'total_records': user_records.count(),
            'category_stats': category_stats,
            'scenario_stats': scenario_stats,
            'recent_tools': recent_tools
        })

    @action(detail=False, methods=['get'])
    def download_static_file(self, request):
        """
        下载static_files/img目录下的文件
        用于条形码和二维码的下载和预览
        """
        filename = request.query_params.get('filename')

        if not filename:
            return Response(
                {'error': '缺少必要参数: filename'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 调用工具类验证文件
        result = EncodingTools.download_static_file(filename)

        if 'error' in result:
            return Response(
                {'error': result['error']},
                status=status.HTTP_404_NOT_FOUND
            )

        # 读取文件内容
        file_path = Path(result['file_path'])

        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()

            # 根据文件扩展名确定MIME类型
            mime_types = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.svg': 'image/svg+xml',
                '.bmp': 'image/bmp',
                '.webp': 'image/webp'
            }

            file_ext = file_path.suffix.lower()
            content_type = mime_types.get(file_ext, 'application/octet-stream')

            # 返回文件内容
            response = HttpResponse(file_content, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response['Content-Length'] = str(len(file_content))

            return response
        except Exception as e:
            return Response(
                {'error': f'文件读取失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
