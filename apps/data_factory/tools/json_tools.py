# -*- coding: utf-8 -*-
# -----------------------------
# @Author    : 影子
# @Time      : 2026/1/19
# @Software  : PyCharm
# @FileName  : json_tools.py
# -----------------------------
"""
JSON工具
"""
import json
import yaml
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
from difflib import SequenceMatcher, unified_diff
import logging

logger = logging.getLogger(__name__)

try:
    import jsonpath_ng as jsonpath
    JSONPATH_AVAILABLE = True
except ImportError:
    JSONPATH_AVAILABLE = False


class JsonTools:
    """JSON工具类"""

    @staticmethod
    def format_json(json_str: str, indent: int = 2, sort_keys: bool = False, compress: bool = False) -> Dict[str, Any]:
        """JSON格式化/压缩"""
        try:
            data = json.loads(json_str)
            
            original_chars = len(json_str)
            original_lines = json_str.count('\n') + 1
            
            if compress:
                result = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
                compressed_chars = len(result)
                compressed_lines = result.count('\n') + 1
                
                return {
                    'success': True,
                    'result': result,
                    'mode': 'compress',
                    'original_length': original_chars,
                    'compressed_length': compressed_chars,
                    'original_lines': original_lines,
                    'compressed_lines': compressed_lines,
                    'compression_ratio': f"{(1 - compressed_chars / original_chars) * 100:.2f}%"
                }
            else:
                result = json.dumps(data, ensure_ascii=False, indent=indent, sort_keys=sort_keys)
                formatted_chars = len(result)
                formatted_lines = result.count('\n') + 1
                
                return {
                    'success': True,
                    'result': result,
                    'mode': 'format',
                    'indent': indent,
                    'sort_keys': sort_keys,
                    'original_length': original_chars,
                    'formatted_length': formatted_chars,
                    'original_lines': original_lines,
                    'formatted_lines': formatted_lines
                }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'JSON格式错误: {str(e)}',
                'line': e.lineno,
                'column': e.colno
            }
        except Exception as e:
            logger.error(f'JSON格式化失败: {str(e)}')
            return {'error': 'JSON格式化失败，请检查输入或联系管理员！'}

    @staticmethod
    def validate_json(json_str: str) -> Dict[str, Any]:
        """JSON校验"""
        try:
            data = json.loads(json_str)
            return {
                'success': True,
                'valid': True,
                'message': 'JSON格式正确',
                'data_type': type(data).__name__,
                'size': len(json_str)
            }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'valid': False,
                'error': f'JSON格式错误: {str(e)}',
                'line': e.lineno,
                'column': e.colno,
                'position': e.pos
            }
        except Exception as e:
            logger.error(f'JSON校验失败: {str(e)}')
            return {'error': 'JSON校验失败，请检查输入数据！'}

    @staticmethod
    def json_to_xml(json_str: str, root_tag: str = 'root') -> Dict[str, Any]:
        """JSON转XML"""
        try:
            data = json.loads(json_str)
            
            def dict_to_xml(d, parent):
                for key, value in d.items():
                    if isinstance(value, dict):
                        elem = ET.SubElement(parent, key)
                        dict_to_xml(value, elem)
                    elif isinstance(value, list):
                        for item in value:
                            elem = ET.SubElement(parent, key)
                            if isinstance(item, dict):
                                dict_to_xml(item, elem)
                            else:
                                elem.text = str(item)
                    else:
                        elem = ET.SubElement(parent, key)
                        elem.text = str(value)
            
            root = ET.Element(root_tag)
            dict_to_xml(data, root)
            xml_str = ET.tostring(root, encoding='unicode', method='xml')
            
            return {
                'success': True,
                'result': xml_str,
                'root_tag': root_tag
            }
        except json.JSONDecodeError as e:
            return {'error': f'JSON格式错误: {str(e)}'}
        except Exception as e:
            return {'error': f'JSON转XML失败: {str(e)}'}

    @staticmethod
    def xml_to_json(xml_str: str) -> Dict[str, Any]:
        """XML转JSON"""
        try:
            def xml_to_dict(element):
                result = {}
                for child in element:
                    if len(child) == 0:
                        result[child.tag] = child.text
                    else:
                        result[child.tag] = xml_to_dict(child)
                return result
            
            root = ET.fromstring(xml_str)
            data = xml_to_dict(root)
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            
            return {
                'success': True,
                'result': json_str
            }
        except ET.ParseError as e:
            return {'error': f'XML格式错误: {str(e)}'}
        except Exception as e:
            return {'error': f'XML转JSON失败: {str(e)}'}

    @staticmethod
    def json_to_yaml(json_str: str) -> Dict[str, Any]:
        """JSON转YAML"""
        try:
            data = json.loads(json_str)
            yaml_str = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
            
            return {
                'success': True,
                'result': yaml_str
            }
        except json.JSONDecodeError as e:
            return {'error': f'JSON格式错误: {str(e)}'}
        except Exception as e:
            return {'error': f'JSON转YAML失败: {str(e)}'}

    @staticmethod
    def yaml_to_json(yaml_str: str) -> Dict[str, Any]:
        """YAML转JSON"""
        try:
            data = yaml.safe_load(yaml_str)
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            
            return {
                'success': True,
                'result': json_str
            }
        except yaml.YAMLError as e:
            return {'error': f'YAML格式错误: {str(e)}'}
        except Exception as e:
            return {'error': f'YAML转JSON失败: {str(e)}'}

    @staticmethod
    def json_to_csv(json_str: str, separator: str = ',') -> Dict[str, Any]:
        """JSON转CSV"""
        try:
            data = json.loads(json_str)
            
            if not isinstance(data, list):
                return {'error': 'JSON必须是数组格式才能转换为CSV'}
            
            if not data:
                return {'error': 'JSON数组为空'}
            
            headers = list(data[0].keys())
            csv_lines = [separator.join(headers)]
            
            for item in data:
                row = []
                for header in headers:
                    value = item.get(header, '')
                    if isinstance(value, (list, dict)):
                        value = json.dumps(value, ensure_ascii=False)
                    row.append(str(value))
                csv_lines.append(separator.join(row))
            
            csv_str = '\n'.join(csv_lines)
            
            return {
                'success': True,
                'result': csv_str,
                'row_count': len(data),
                'column_count': len(headers)
            }
        except json.JSONDecodeError as e:
            return {'error': f'JSON格式错误: {str(e)}'}
        except Exception as e:
            return {'error': f'JSON转CSV失败: {str(e)}'}

    @staticmethod
    def csv_to_json(csv_str: str, separator: str = ',', has_header: bool = True) -> Dict[str, Any]:
        """CSV转JSON"""
        try:
            lines = csv_str.strip().split('\n')
            if not lines:
                return {'error': 'CSV内容为空'}
            
            if has_header:
                headers = [h.strip() for h in lines[0].split(separator)]
                data = []
                for line in lines[1:]:
                    values = [v.strip() for v in line.split(separator)]
                    row = dict(zip(headers, values))
                    data.append(row)
            else:
                data = [[v.strip() for v in line.split(separator)] for line in lines]
            
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            
            return {
                'success': True,
                'result': json_str,
                'row_count': len(data) if isinstance(data, list) else len(data),
                'has_header': has_header
            }
        except Exception as e:
            return {'error': f'CSV转JSON失败: {str(e)}'}

    @staticmethod
    def json_diff(json_str1: str, json_str2: str, ignore_whitespace: bool = True) -> Dict[str, Any]:
        """JSON对比"""
        try:
            data1 = json.loads(json_str1)
            data2 = json.loads(json_str2)
            
            str1 = json.dumps(data1, ensure_ascii=False, sort_keys=True)
            str2 = json.dumps(data2, ensure_ascii=False, sort_keys=True)
            
            if ignore_whitespace:
                str1 = ''.join(str1.split())
                str2 = ''.join(str2.split())
            
            similarity = SequenceMatcher(None, str1, str2).ratio()
            
            diff_lines = list(unified_diff(
                str1.splitlines(keepends=True),
                str2.splitlines(keepends=True),
                fromfile='JSON 1',
                tofile='JSON 2',
                lineterm=''
            ))
            
            diff_result = ''.join(diff_lines) if diff_lines else '无差异'
            
            return {
                'success': True,
                'similarity': f"{similarity * 100:.2f}%",
                'identical': similarity == 1.0,
                'diff': diff_result,
                'size1': len(json_str1),
                'size2': len(json_str2)
            }
        except json.JSONDecodeError as e:
            logger.error(f'JSON格式错误: {str(e)}')
            return {'error': 'JSON格式错误，请检查输入数据！'}
        except Exception as e:
            return {'error': f'JSON对比失败: {str(e)}'}

    @staticmethod
    def jsonpath_query(json_str: str, jsonpath_expr: str) -> Dict[str, Any]:
        """JSONPath查询"""
        if not JSONPATH_AVAILABLE:
            return {'error': 'jsonpath_ng模块未安装，请先安装！'}
        
        try:
            data = json.loads(json_str)
            
            parse_expr = jsonpath.parse(jsonpath_expr)
            matches = [match.value for match in parse_expr.find(data)]
            
            return {
                'success': True,
                'expression': jsonpath_expr,
                'matches': matches,
                'count': len(matches)
            }
        except json.JSONDecodeError as e:
            return {'error': f'JSON格式错误: {str(e)}'}
        except Exception as e:
            return {'error': f'JSONPath查询失败: {str(e)}'}

    @staticmethod
    def json_path_list(json_str: str) -> Dict[str, Any]:
        """列出JSON所有路径"""
        try:
            data = json.loads(json_str)
            paths = []
            
            def get_paths(obj, current_path=''):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        new_path = f"{current_path}.{key}" if current_path else key
                        paths.append(new_path)
                        get_paths(value, new_path)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        new_path = f"{current_path}[{i}]"
                        paths.append(new_path)
                        get_paths(item, new_path)
            
            get_paths(data)
            
            return {
                'success': True,
                'paths': paths,
                'count': len(paths)
            }
        except json.JSONDecodeError as e:
            return {'error': f'JSON格式错误: {str(e)}'}
        except Exception as e:
            return {'error': f'获取JSON路径失败: {str(e)}'}

    @staticmethod
    def json_flatten(json_str: str, separator: str = '.') -> Dict[str, Any]:
        """扁平化JSON"""
        try:
            data = json.loads(json_str)
            result = {}
            
            def flatten(obj, parent_key=''):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        new_key = f"{parent_key}{separator}{key}" if parent_key else key
                        flatten(value, new_key)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        new_key = f"{parent_key}[{i}]"
                        flatten(item, new_key)
                else:
                    result[parent_key] = obj
            
            flatten(data)
            
            return {
                'success': True,
                'result': result,
                'count': len(result)
            }
        except json.JSONDecodeError as e:
            return {'error': f'JSON格式错误: {str(e)}'}
        except Exception as e:
            return {'error': f'JSON扁平化失败: {str(e)}'}

    @staticmethod
    def mock_data(data_type: str, count: int = 1, **kwargs) -> Dict[str, Any]:
        """生成测试数据"""
        try:
            import random
            import string
            from datetime import datetime, timedelta
            
            result = []
            
            for _ in range(count):
                if data_type == 'string':
                    length = kwargs.get('length', 10)
                    char_type = kwargs.get('char_type', 'all')
                    if char_type == 'letters':
                        chars = string.ascii_letters
                    elif char_type == 'digits':
                        chars = string.digits
                    elif char_type == 'alphanumeric':
                        chars = string.ascii_letters + string.digits
                    else:
                        chars = string.ascii_letters + string.digits + string.punctuation
                    value = ''.join(random.choice(chars) for _ in range(length))
                    
                elif data_type == 'number':
                    min_val = kwargs.get('min_val', 0)
                    max_val = kwargs.get('max_val', 100)
                    decimals = kwargs.get('decimals', 0)
                    value = round(random.uniform(min_val, max_val), decimals)
                    
                elif data_type == 'boolean':
                    value = random.choice([True, False])
                    
                elif data_type == 'email':
                    domains = ['qq.com', '163.com', '126.com', 'gmail.com', 'outlook.com']
                    username = ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
                    value = f"{username}@{random.choice(domains)}"
                    
                elif data_type == 'phone':
                    prefixes = ['130', '131', '132', '133', '135', '136', '137', '138', '139',
                               '150', '151', '152', '153', '155', '156', '157', '158', '159',
                               '180', '181', '182', '183', '184', '185', '186', '187', '188', '189']
                    value = f"{random.choice(prefixes)}{random.randint(10000000, 99999999)}"
                    
                elif data_type == 'date':
                    start_date = kwargs.get('start_date', datetime(2020, 1, 1))
                    end_date = kwargs.get('end_date', datetime(2025, 12, 31))
                    days_between = (end_date - start_date).days
                    random_days = random.randint(0, days_between)
                    value = (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')
                    
                elif data_type == 'datetime':
                    start_date = kwargs.get('start_date', datetime(2020, 1, 1))
                    end_date = kwargs.get('end_date', datetime(2025, 12, 31))
                    days_between = (end_date - start_date).days
                    random_days = random.randint(0, days_between)
                    random_seconds = random.randint(0, 86400)
                    value = (start_date + timedelta(days=random_days, seconds=random_seconds)).strftime('%Y-%m-%d %H:%M:%S')
                    
                elif data_type == 'name':
                    first_names = ['张', '王', '李', '赵', '刘', '陈', '杨', '黄', '周', '吴', '徐']
                    last_names = ['伟', '芳', '娜', '敏', '静', '强', '磊', '洋', '勇', '杰', '婷']
                    value = f"{random.choice(first_names)}{random.choice(last_names)}"
                    
                elif data_type == 'address':
                    provinces = ['北京市', '上海市', '广东省', '浙江省', '江苏省', '四川省']
                    districts = ['朝阳区', '海淀区', '浦东新区', '天河区', '西湖区', '鼓楼区']
                    streets = ['中山路', '人民路', '建设路', '解放路', '和平路', '胜利路']
                    value = f"{random.choice(provinces)}{random.choice(districts)}{random.choice(streets)}{random.randint(1, 999)}号"
                    
                elif data_type == 'url':
                    domains = ['com', 'cn', 'net', 'org', 'io']
                    paths = ['api', 'web', 'app', 'service', 'data']
                    subdomains = ['www', 'api', 'test', 'dev', 'staging']
                    value = f"https://{random.choice(subdomains)}.example.{random.choice(domains)}/{random.choice(paths)}"
                    
                elif data_type == 'uuid':
                    import uuid as uuid_module
                    value = str(uuid_module.uuid4())
                    
                elif data_type == 'ip':
                    value = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
                    
                elif data_type == 'array':
                    item_type = kwargs.get('item_type', 'string')
                    array_length = kwargs.get('array_length', 5)
                    mock_result = JsonTools.mock_data(item_type, array_length, **kwargs)
                    value = mock_result.get('data', []) if isinstance(mock_result, dict) and 'data' in mock_result else []
                    
                elif data_type == 'object':
                    keys = kwargs.get('keys', ['id', 'name', 'value'])
                    value_type = kwargs.get('value_type', 'string')
                    mock_result = JsonTools.mock_data(value_type, len(keys), **kwargs)
                    values = mock_result.get('data', []) if isinstance(mock_result, dict) and 'data' in mock_result else []
                    value = dict(zip(keys, values)) if len(values) == len(keys) else {}
                    
                else:
                    value = None
                
                if data_type in ['array', 'object']:
                    result.append(value)
                else:
                    result.append({'type': data_type, 'value': value})
            
            return {
                'success': True,
                'data_type': data_type,
                'count': count,
                'data': result
            }
        except Exception as e:
            return {'error': f'生成测试数据失败: {str(e)}'}

    @staticmethod
    def json_diff_enhanced(json_str1: str, json_str2: str, ignore_whitespace: bool = True, 
                           show_only_diff: bool = False) -> Dict[str, Any]:
        """增强的JSON对比工具"""
        try:
            data1 = json.loads(json_str1)
            data2 = json.loads(json_str2)
            
            str1 = json.dumps(data1, ensure_ascii=False, sort_keys=True, indent=2)
            str2 = json.dumps(data2, ensure_ascii=False, sort_keys=True, indent=2)
            
            if ignore_whitespace:
                str1 = ''.join(str1.split())
                str2 = ''.join(str2.split())
            
            similarity = SequenceMatcher(None, str1, str2).ratio()
            
            diff_lines = list(unified_diff(
                str1.splitlines(keepends=True),
                str2.splitlines(keepends=True),
                fromfile='JSON 1',
                tofile='JSON 2',
                lineterm=''
            ))
            
            diff_result = ''.join(diff_lines) if diff_lines else '无差异'
            
            key_diffs = []
            value_diffs = []
            
            def compare_objects(obj1, obj2, path=''):
                if isinstance(obj1, dict) and isinstance(obj2, dict):
                    keys1 = set(obj1.keys())
                    keys2 = set(obj2.keys())
                    
                    for key in keys1 | keys2:
                        current_path = f"{path}.{key}" if path else key
                        if key in keys1 and key in keys2:
                            if obj1[key] != obj2[key]:
                                key_diffs.append({
                                    'path': current_path,
                                    'key': key,
                                    'value1': obj1[key],
                                    'value2': obj2[key],
                                    'type': 'value_diff'
                                })
                                compare_objects(obj1[key], obj2[key], current_path)
                        elif key in keys1:
                            key_diffs.append({
                                'path': current_path,
                                'key': key,
                                'value1': obj1[key],
                                'value2': None,
                                'type': 'key_only_in_1'
                            })
                        elif key in keys2:
                            key_diffs.append({
                                'path': current_path,
                                'key': key,
                                'value1': None,
                                'value2': obj2[key],
                                'type': 'key_only_in_2'
                            })
                elif isinstance(obj1, list) and isinstance(obj2, list):
                    min_len = min(len(obj1), len(obj2))
                    for i in range(min_len):
                        if obj1[i] != obj2[i]:
                            current_path = f"{path}[{i}]"
                            key_diffs.append({
                                'path': current_path,
                                'index': i,
                                'value1': obj1[i],
                                'value2': obj2[i],
                                'type': 'array_diff'
                            })
            
            compare_objects(data1, data2)
            
            return {
                'success': True,
                'similarity': f"{similarity * 100:.2f}%",
                'identical': similarity == 1.0,
                'diff': diff_result,
                'detailed_diffs': key_diffs,
                'diff_count': len(key_diffs),
                'size1': len(json_str1),
                'size2': len(json_str2),
                'show_only_diff': show_only_diff
            }
        except json.JSONDecodeError as e:
            return {'error': f'JSON格式错误: {str(e)}'}
        except Exception as e:
            return {'error': f'JSON对比失败: {str(e)}'}
