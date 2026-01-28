"""
接口测试变量解析器
支持在接口测试中使用动态函数表达式
语法：${function_name(args)}
"""
import re
import sys
import json
from datetime import datetime, timedelta

# 设置标准输出编码为 UTF-8，避免 Windows 系统上的编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 导入数据工厂的工具类
from apps.data_factory.tools.random_tools import RandomTools
from apps.data_factory.tools.test_data_tools import TestDataTools
from apps.data_factory.tools.string_tools import StringTools
from apps.data_factory.tools.encoding_tools import EncodingTools
from apps.data_factory.tools.encryption_tools import EncryptionTools
from apps.data_factory.tools.crontab_tools import CrontabTools
from apps.data_factory.tools.image_tools import ImageTools


class VariableResolver:
    """接口测试变量解析器 - 使用数据工厂工具"""
    
    def __init__(self):
        # 注册所有内置函数，映射到数据工厂的工具
        self.functions = {
            # 随机工具
            'random_int': self._call_random_tool,
            'random_float': self._call_random_tool,
            'random_digits': self._call_random_tool,
            'random_string': self._call_random_tool,
            'random_letters': self._call_random_tool,
            'random_chinese': self._call_random_tool,
            'random_uuid': self._call_random_tool,
            'random_guid': self._call_random_tool,
            'random_mac': self._call_random_tool,
            'random_mac_address': self._call_random_tool,
            'random_ip': self._call_random_tool,
            'random_ip_address': self._call_random_tool,
            'random_boolean': self._call_random_tool,
            'random_color': self._call_random_tool,
            'random_password': self._call_random_tool,
            'random_sequence': self._call_random_tool,
            'random_date': self._call_random_tool,
            
            # 测试数据工具
            'random_phone': self._call_test_data_tool,
            'random_email': self._call_test_data_tool,
            'random_id_card': self._call_test_data_tool,
            'random_name': self._call_test_data_tool,
            'random_company': self._call_test_data_tool,
            'random_address': self._call_test_data_tool,
            'generate_chinese_name': self._call_test_data_tool,
            'generate_chinese_phone': self._call_test_data_tool,
            'generate_chinese_email': self._call_test_data_tool,
            'generate_chinese_address': self._call_test_data_tool,
            'generate_id_card': self._call_test_data_tool,
            'generate_company_name': self._call_test_data_tool,
            'generate_bank_card': self._call_test_data_tool,
            'generate_hk_id_card': self._call_test_data_tool,
            'generate_business_license': self._call_test_data_tool,
            'generate_user_profile': self._call_test_data_tool,
            'generate_coordinates': self._call_test_data_tool,
            
            # 字符工具
            'remove_whitespace': self._call_string_tool,
            'replace_string': self._call_string_tool,
            'word_count': self._call_string_tool,
            'regex_test': self._call_string_tool,
            'case_convert': self._call_string_tool,
            
            # 编码工具
            'timestamp_convert': self._call_encoding_tool,
            'base64_encode': self._call_encoding_tool,
            'base64_decode': self._call_encoding_tool,
            'url_encode': self._call_encoding_tool,
            'url_decode': self._call_encoding_tool,
            'unicode_convert': self._call_encoding_tool,
            'ascii_convert': self._call_encoding_tool,
            'color_convert': self._call_encoding_tool,
            'base_convert': self._call_encoding_tool,
            'generate_barcode': self._call_encoding_tool,
            'generate_qrcode': self._call_encoding_tool,
            'image_to_base64': self._call_encoding_tool,
            'base64_to_image': self._call_encoding_tool,
            
            # 加密工具
            'base64': self._call_encryption_tool,
            'md5': self._call_encryption_tool,
            'sha1': self._call_encryption_tool,
            'sha256': self._call_encryption_tool,
            'md5_hash': self._call_encryption_tool,
            'sha1_hash': self._call_encryption_tool,
            'sha256_hash': self._call_encryption_tool,
            'sha512_hash': self._call_encryption_tool,
            'hash_comparison': self._call_encryption_tool,
            'aes_encrypt': self._call_encryption_tool,
            'aes_decrypt': self._call_encryption_tool,
            
            # Crontab工具
            'generate_expression': self._call_crontab_tool,
            'parse_expression': self._call_crontab_tool,
            'get_next_runs': self._call_crontab_tool,
            'validate_expression': self._call_crontab_tool,
            
            # 时间日期函数
            'timestamp': self._timestamp,
            'timestamp_sec': self._timestamp_sec,
            'datetime': self._datetime,
            'date': self._date,
            'time': self._time,
            'date_offset': self._date_offset,
        }
    
    def resolve(self, text):
        """解析文本中的动态函数占位符
        
        Args:
            text: 包含动态函数的文本，如 "Hello ${random_string(8)}"
            
        Returns:
            解析后的文本
        """
        if not isinstance(text, str):
            return text
        
        # 匹配 ${function_name(args)} 模式
        pattern = r'\$\{([^}]+)\}'
        
        def replace_func(match):
            expression = match.group(1)
            try:
                return str(self._evaluate_expression(expression))
            except Exception as e:
                if isinstance(e, UnicodeEncodeError):
                    return match.group(0)
                try:
                    print(f"[WARNING] Variable resolution failed: ${{{expression}}} - {str(e)}")
                except UnicodeEncodeError:
                    print(f"[WARNING] Variable resolution failed: ${{{expression}}}")
                return match.group(0)
        
        return re.sub(pattern, replace_func, text)
    
    def _evaluate_expression(self, expression):
        """评估单个表达式
        
        Args:
            expression: 函数表达式，如 "random_int(100, 200)" 或 "timestamp()"
            
        Returns:
            函数执行结果
        """
        # 解析函数名和参数
        match = re.match(r'(\w+)\((.*)\)', expression.strip())
        if not match:
            # 无参数函数
            func_name = expression.strip()
            args = []
        else:
            func_name = match.group(1)
            args_str = match.group(2)
            args = self._parse_args(args_str)
        
        # 调用对应函数
        if func_name in self.functions:
            return self.functions[func_name](func_name, args)
        else:
            raise ValueError(f"未知函数: {func_name}")
    
    def _parse_args(self, args_str):
        """解析函数参数
        
        Args:
            args_str: 参数字符串，如 "100, 200" 或 "YYYY-MM-DD"
            
        Returns:
            参数列表
        """
        if not args_str.strip():
            return []
        
        args = []
        current_arg = []
        in_brackets = False
        in_quotes = False
        quote_char = None
        
        for char in args_str:
            if char == '[' and not in_quotes:
                in_brackets = True
                current_arg.append(char)
            elif char == ']' and not in_quotes:
                in_brackets = False
                current_arg.append(char)
            elif char == '"' and not in_quotes:
                in_quotes = True
                quote_char = '"'
                current_arg.append(char)
            elif char == "'" and not in_quotes:
                in_quotes = True
                quote_char = "'"
                current_arg.append(char)
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
                current_arg.append(char)
            elif char == ',' and not in_brackets and not in_quotes:
                # 分隔参数
                arg = ''.join(current_arg).strip()
                args.append(self._parse_single_arg(arg))
                current_arg = []
            else:
                current_arg.append(char)
        
        # 添加最后一个参数
        if current_arg:
            arg = ''.join(current_arg).strip()
            args.append(self._parse_single_arg(arg))
        
        return args
    
    def _parse_single_arg(self, arg):
        """解析单个参数
        
        Args:
            arg: 单个参数字符串
            
        Returns:
            解析后的参数值
        """
        if not arg:
            return None
        
        # 尝试转换为布尔值
        if arg.lower() == 'true':
            return True
        elif arg.lower() == 'false':
            return False
        # 尝试转换为数字
        try:
            if '.' in arg:
                return float(arg)
            else:
                return int(arg)
        except ValueError:
            # 尝试解析JSON
            if arg.startswith('[') and arg.endswith(']'):
                try:
                    return json.loads(arg)
                except:
                    pass
            # 移除引号
            return arg.strip('\'"')
    
    def _call_random_tool(self, func_name, args):
        """调用随机工具"""
        tool_mapping = {
            'random_int': RandomTools.random_int,
            'random_float': RandomTools.random_float,
            'random_string': RandomTools.random_string,
            'random_uuid': RandomTools.random_uuid,
            'random_guid': RandomTools.random_uuid,
            'random_mac': RandomTools.random_mac_address,
            'random_mac_address': RandomTools.random_mac_address,
            'random_ip': RandomTools.random_ip_address,
            'random_ip_address': RandomTools.random_ip_address,
            'random_date': RandomTools.random_date,
            'random_boolean': RandomTools.random_boolean,
            'random_color': RandomTools.random_color,
            'random_password': RandomTools.random_password,
            'random_sequence': RandomTools.random_sequence,
        }
        
        # 特殊处理 random_digits 和 random_letters
        if func_name == 'random_digits':
            result = RandomTools.random_string(length=args[0] if args else 6, char_type='digits', count=args[1] if len(args) > 1 else 1)
        elif func_name == 'random_letters':
            result = RandomTools.random_string(length=args[0] if args else 8, char_type='letters', count=args[1] if len(args) > 1 else 1)
        elif func_name == 'random_chinese':
            result = RandomTools.random_string(length=args[0] if args else 2, char_type='chinese', count=args[1] if len(args) > 1 else 1)
        elif func_name in tool_mapping:
            # 根据函数名设置默认参数
            kwargs = {}
            if func_name == 'random_int':
                kwargs = {'min_val': args[0] if len(args) > 0 else 0, 'max_val': args[1] if len(args) > 1 else 100, 'count': args[2] if len(args) > 2 else 1}
            elif func_name == 'random_float':
                kwargs = {'min_val': args[0] if len(args) > 0 else 0.0, 'max_val': args[1] if len(args) > 1 else 1.0, 'precision': args[2] if len(args) > 2 else 2, 'count': args[3] if len(args) > 3 else 1}
            elif func_name == 'random_string':
                kwargs = {'length': args[0] if len(args) > 0 else 8, 'char_type': args[1] if len(args) > 1 else 'all', 'count': args[2] if len(args) > 2 else 1}
            elif func_name in ['random_uuid', 'random_guid']:
                kwargs = {'version': args[0] if len(args) > 0 else 4, 'count': args[1] if len(args) > 1 else 1}
            elif func_name in ['random_mac', 'random_mac_address']:
                kwargs = {'separator': args[0] if len(args) > 0 else ':', 'count': args[1] if len(args) > 1 else 1}
            elif func_name in ['random_ip', 'random_ip_address']:
                kwargs = {'ip_version': args[0] if len(args) > 0 else 4, 'count': args[1] if len(args) > 1 else 1}
            elif func_name == 'random_date':
                kwargs = {'start_date': args[0] if len(args) > 0 else '2024-01-01', 'end_date': args[1] if len(args) > 1 else '2024-12-31', 'count': args[2] if len(args) > 2 else 1, 'date_format': args[3] if len(args) > 3 else '%Y-%m-%d'}
            elif func_name == 'random_boolean':
                kwargs = {'count': args[0] if len(args) > 0 else 1}
            elif func_name == 'random_color':
                kwargs = {'format': args[0] if len(args) > 0 else 'hex', 'count': args[1] if len(args) > 1 else 1}
            elif func_name == 'random_password':
                kwargs = {'length': args[0] if len(args) > 0 else 12, 'include_uppercase': True, 'include_lowercase': True, 'include_digits': True, 'include_special': True, 'count': args[1] if len(args) > 1 else 1}
            elif func_name == 'random_sequence':
                # 处理序列参数，支持字符串和列表格式
                sequence_arg = args[0] if len(args) > 0 else []
                if isinstance(sequence_arg, str):
                    # 尝试解析字符串为列表
                    if sequence_arg.startswith('[') and sequence_arg.endswith(']'):
                        # JSON格式: ["a","b","c"]
                        try:
                            sequence_arg = json.loads(sequence_arg)
                        except:
                            # 如果JSON解析失败，尝试手动解析
                            sequence_arg = [item.strip().strip('"\'') for item in sequence_arg[1:-1].split(',')]
                    else:
                        # 逗号分隔格式: a,b,c
                        sequence_arg = [item.strip().strip('"\'') for item in sequence_arg.split(',')]
                kwargs = {'sequence': sequence_arg, 'count': args[1] if len(args) > 1 else 1, 'unique': args[2] if len(args) > 2 else False}
            
            result = tool_mapping[func_name](**kwargs)
        
        # 提取 result 字段
        if isinstance(result, dict) and 'result' in result:
            return result['result']
        return result
    
    def _call_test_data_tool(self, func_name, args):
        """调用测试数据工具"""
        tool_mapping = {
            'random_phone': TestDataTools.generate_chinese_phone,
            'random_email': TestDataTools.generate_chinese_email,
            'random_id_card': TestDataTools.generate_id_card,
            'random_name': TestDataTools.generate_chinese_name,
            'random_company': TestDataTools.generate_company_name,
            'random_address': TestDataTools.generate_chinese_address,
            'generate_chinese_name': TestDataTools.generate_chinese_name,
            'generate_chinese_phone': TestDataTools.generate_chinese_phone,
            'generate_chinese_email': TestDataTools.generate_chinese_email,
            'generate_chinese_address': TestDataTools.generate_chinese_address,
            'generate_id_card': TestDataTools.generate_id_card,
            'generate_company_name': TestDataTools.generate_company_name,
            'generate_bank_card': TestDataTools.generate_bank_card,
            'generate_hk_id_card': TestDataTools.generate_hk_id_card,
            'generate_business_license': TestDataTools.generate_business_license,
            'generate_user_profile': TestDataTools.generate_user_profile,
            'generate_coordinates': TestDataTools.generate_coordinates,
        }
        
        # 设置默认参数
        kwargs = {}
        if func_name in ['generate_chinese_name', 'random_name']:
            kwargs = {'gender': args[0] if len(args) > 0 else 'random', 'count': args[1] if len(args) > 1 else 1}
        elif func_name == 'generate_chinese_address':
            kwargs = {'full_address': args[0] if len(args) > 0 else True, 'count': args[1] if len(args) > 1 else 1}
        else:
            kwargs = {'count': args[0] if len(args) > 0 else 1}
        
        if func_name in tool_mapping:
            result = tool_mapping[func_name](**kwargs)
        
        # 提取 result 字段
        if isinstance(result, dict) and 'result' in result:
            return result['result']
        return result
    
    def _call_string_tool(self, func_name, args):
        """调用字符工具"""
        tool_mapping = {
            'remove_whitespace': StringTools.remove_whitespace,
            'replace_string': StringTools.replace_string,
            'word_count': StringTools.word_count,
            'regex_test': StringTools.regex_test,
            'case_convert': StringTools.case_convert,
        }
        
        # 设置默认参数
        kwargs = {}
        if func_name == 'remove_whitespace':
            kwargs = {'text': args[0] if len(args) > 0 else ''}
        elif func_name == 'replace_string':
            kwargs = {'text': args[0] if len(args) > 0 else '', 'old_str': args[1] if len(args) > 1 else '', 'new_str': args[2] if len(args) > 2 else '', 'is_regex': False}
        elif func_name == 'word_count':
            kwargs = {'text': args[0] if len(args) > 0 else ''}
        elif func_name == 'regex_test':
            kwargs = {'pattern': args[0] if len(args) > 0 else '', 'text': args[1] if len(args) > 1 else '', 'flags': args[2] if len(args) > 2 else ''}
        elif func_name == 'case_convert':
            kwargs = {'text': args[0] if len(args) > 0 else '', 'convert_type': args[1] if len(args) > 1 else 'upper'}
        
        if func_name in tool_mapping:
            result = tool_mapping[func_name](**kwargs)
        
        # 提取 result 字段
        if isinstance(result, dict) and 'result' in result:
            return result['result']
        return result
    
    def _call_encoding_tool(self, func_name, args):
        """调用编码工具"""
        tool_mapping = {
            'timestamp_convert': EncodingTools.timestamp_convert,
            'base64_encode': EncodingTools.base64_encode,
            'base64_decode': EncodingTools.base64_decode,
            'url_encode': EncodingTools.url_encode,
            'url_decode': EncodingTools.url_decode,
            'unicode_convert': EncodingTools.unicode_convert,
            'ascii_convert': EncodingTools.ascii_convert,
            'color_convert': EncodingTools.color_convert,
            'base_convert': EncodingTools.base_convert,
            'generate_barcode': EncodingTools.generate_barcode,
            'generate_qrcode': EncodingTools.generate_qrcode,
            'image_to_base64': ImageTools.image_to_base64,
            'base64_to_image': ImageTools.base64_to_image,
        }
        
        # 设置默认参数
        kwargs = {}
        if func_name == 'timestamp_convert':
            kwargs = {'timestamp': args[0] if len(args) > 0 else '', 'convert_type': args[1] if len(args) > 1 else 'to_datetime'}
        elif func_name == 'base64_encode':
            kwargs = {'text': args[0] if len(args) > 0 else '', 'encoding': args[1] if len(args) > 1 else 'utf-8'}
        elif func_name == 'base64_decode':
            kwargs = {'text': args[0] if len(args) > 0 else '', 'encoding': args[1] if len(args) > 1 else 'utf-8'}
        elif func_name == 'url_encode':
            kwargs = {'data': args[0] if len(args) > 0 else '', 'encoding': args[1] if len(args) > 1 else 'utf-8'}
        elif func_name == 'url_decode':
            kwargs = {'data': args[0] if len(args) > 0 else '', 'encoding': args[1] if len(args) > 1 else 'utf-8'}
        elif func_name == 'unicode_convert':
            kwargs = {'text': args[0] if len(args) > 0 else '', 'convert_type': args[1] if len(args) > 1 else 'to_unicode'}
        elif func_name == 'ascii_convert':
            kwargs = {'text': args[0] if len(args) > 0 else '', 'convert_type': args[1] if len(args) > 1 else 'to_ascii'}
        elif func_name == 'color_convert':
            kwargs = {'color': args[0] if len(args) > 0 else '', 'from_type': args[1] if len(args) > 1 else 'hex', 'to_type': args[2] if len(args) > 2 else 'rgb'}
        elif func_name == 'base_convert':
            kwargs = {'number': args[0] if len(args) > 0 else 0, 'from_base': args[1] if len(args) > 1 else 10, 'to_base': args[2] if len(args) > 2 else 16}
        elif func_name == 'generate_barcode':
            kwargs = {'data': args[0] if len(args) > 0 else '', 'barcode_type': args[1] if len(args) > 1 else 'code128'}
        elif func_name == 'generate_qrcode':
            kwargs = {'data': args[0] if len(args) > 0 else ''}
        elif func_name == 'image_to_base64':
            kwargs = {'image_data': args[0] if len(args) > 0 else '', 'image_format': args[1] if len(args) > 1 else 'png', 'include_prefix': True}
        elif func_name == 'base64_to_image':
            kwargs = {'base64_str': args[0] if len(args) > 0 else ''}
        
        if func_name in tool_mapping:
            result = tool_mapping[func_name](**kwargs)
            
            # 提取 result 字段
            if isinstance(result, dict) and 'result' in result:
                return result['result']
            return result
        
        return None
    
    def _call_encryption_tool(self, func_name, args):
        """调用加密工具"""
        tool_mapping = {
            'base64': EncryptionTools.base64_encode,
            'md5': EncryptionTools.md5_hash,
            'sha1': EncryptionTools.sha1_hash,
            'sha256': EncryptionTools.sha256_hash,
            'md5_hash': EncryptionTools.md5_hash,
            'sha1_hash': EncryptionTools.sha1_hash,
            'sha256_hash': EncryptionTools.sha256_hash,
            'sha512_hash': EncryptionTools.sha512_hash,
            'hash_comparison': EncryptionTools.hash_comparison,
            'aes_encrypt': EncryptionTools.aes_encrypt,
            'aes_decrypt': EncryptionTools.aes_decrypt,
        }
        
        # 设置默认参数
        kwargs = {}
        if func_name in ['base64', 'md5', 'sha1', 'sha256', 'md5_hash', 'sha1_hash', 'sha256_hash', 'sha512_hash']:
            kwargs = {'text': args[0] if len(args) > 0 else ''}
        elif func_name == 'hash_comparison':
            kwargs = {'text': args[0] if len(args) > 0 else '', 'hash_value': args[1] if len(args) > 1 else '', 'algorithm': args[2] if len(args) > 2 else 'md5'}
        elif func_name == 'aes_encrypt':
            kwargs = {'text': args[0] if len(args) > 0 else '', 'password': args[1] if len(args) > 1 else '', 'mode': args[2] if len(args) > 2 else 'CBC'}
        elif func_name == 'aes_decrypt':
            kwargs = {'encrypted_text': args[0] if len(args) > 0 else '', 'password': args[1] if len(args) > 1 else '', 'mode': args[2] if len(args) > 2 else 'CBC'}
        
        if func_name in tool_mapping:
            result = tool_mapping[func_name](**kwargs)
        
        # 提取 result 字段
        if isinstance(result, dict) and 'result' in result:
            return result['result']
        return result
    
    def _call_crontab_tool(self, func_name, args):
        """调用Crontab工具"""
        tool_mapping = {
            'generate_expression': CrontabTools.generate_expression,
            'parse_expression': CrontabTools.parse_expression,
            'get_next_runs': CrontabTools.get_next_runs,
            'validate_expression': CrontabTools.validate_expression,
        }
        
        # 设置默认参数
        kwargs = {}
        if func_name == 'generate_expression':
            kwargs = {
                'minute': args[0] if len(args) > 0 else '*',
                'hour': args[1] if len(args) > 1 else '*',
                'day': args[2] if len(args) > 2 else '*',
                'month': args[3] if len(args) > 3 else '*',
                'weekday': args[4] if len(args) > 4 else '*'
            }
        elif func_name == 'parse_expression':
            kwargs = {'expression': args[0] if len(args) > 0 else '* * * * *'}
        elif func_name == 'get_next_runs':
            kwargs = {'expression': args[0] if len(args) > 0 else '* * * * *', 'count': args[1] if len(args) > 1 else 5}
        elif func_name == 'validate_expression':
            kwargs = {'expression': args[0] if len(args) > 0 else '* * * * *'}
        
        if func_name in tool_mapping:
            result = tool_mapping[func_name](**kwargs)
            
            # 提取 result 字段
            if isinstance(result, dict) and 'result' in result:
                return result['result']
            # 对于Crontab工具，可能返回expression字段
            if isinstance(result, dict) and 'expression' in result:
                return result['expression']
            return result
        
        return None
    
    # ========== 时间日期函数 ==========
    
    def _timestamp(self):
        """生成当前时间戳（毫秒）
        
        Returns:
            时间戳（毫秒）
            
        Example:
            ${timestamp()} -> 1704067200000
        """
        return int(datetime.now().timestamp() * 1000)
    
    def _timestamp_sec(self):
        """生成当前时间戳（秒）
        
        Returns:
            时间戳（秒）
            
        Example:
            ${timestamp_sec()} -> 1704067200
        """
        return int(datetime.now().timestamp())
    
    def _datetime(self, format_str='%Y-%m-%d %H:%M:%S'):
        """生成当前日期时间
        
        Args:
            format_str: 日期时间格式
            
        Returns:
            格式化的日期时间字符串
            
        Example:
            ${datetime()} -> "2024-01-01 12:00:00"
            ${datetime(%Y-%m-%d)} -> "2024-01-01"
        """
        return datetime.now().strftime(format_str)
    
    def _date(self, format_str='%Y-%m-%d'):
        """生成当前日期
        
        Args:
            format_str: 日期格式
            
        Returns:
            格式化的日期字符串
            
        Example:
            ${date()} -> "2024-01-01"
        """
        return datetime.now().strftime(format_str)
    
    def _time(self, format_str='%H:%M:%S'):
        """生成当前时间
        
        Args:
            format_str: 时间格式
            
        Returns:
            格式化的时间字符串
            
        Example:
            ${time()} -> "12:00:00"
        """
        return datetime.now().strftime(format_str)
    
    def _date_offset(self, days=0, hours=0, minutes=0, format_str='%Y-%m-%d %H:%M:%S'):
        """生成偏移后的日期时间
        
        Args:
            days: 天数偏移
            hours: 小时偏移
            minutes: 分钟偏移
            format_str: 日期时间格式
            
        Returns:
            格式化的日期时间字符串
            
        Example:
            ${date_offset(1)} -> "2024-01-02 12:00:00"
            ${date_offset(0, 1)} -> "2024-01-01 13:00:00"
        """
        dt = datetime.now() + timedelta(days=days, hours=hours, minutes=minutes)
        return dt.strftime(format_str)
