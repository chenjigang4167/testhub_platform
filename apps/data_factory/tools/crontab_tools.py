# -*- coding: utf-8 -*-
"""
Crontab表达式生成器
"""
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List


class CrontabTools:
    """Crontab工具类"""

    @staticmethod
    def generate_expression(minute: str, hour: str, day: str, month: str, weekday: str) -> Dict[str, Any]:
        """生成Crontab表达式"""
        try:
            expression = f"{minute} {hour} {day} {month} {weekday}"
            
            return {
                'success': True,
                'expression': expression,
                'minute': minute,
                'hour': hour,
                'day': day,
                'month': month,
                'weekday': weekday
            }
        except Exception as e:
            return {'error': f'生成Crontab表达式失败: {str(e)}'}

    @staticmethod
    def parse_expression(expression: str) -> Dict[str, Any]:
        """解析Crontab表达式"""
        try:
            parts = expression.strip().split()
            if len(parts) != 5:
                return {'error': 'Crontab表达式格式错误，必须包含5个字段'}
            
            minute, hour, day, month, weekday = parts
            
            return {
                'success': True,
                'minute': minute,
                'hour': hour,
                'day': day,
                'month': month,
                'weekday': weekday
            }
        except Exception as e:
            return {'error': f'解析Crontab表达式失败: {str(e)}'}

    @staticmethod
    def get_next_runs(expression: str, count: int = 10) -> Dict[str, Any]:
        """获取Crontab表达式的下次执行时间"""
        try:
            from croniter import croniter
            
            base = datetime.now()
            cron = croniter(expression, base)
            
            next_runs = []
            for _ in range(count):
                next_run = cron.get_next(datetime)
                next_runs.append(next_run.strftime('%Y-%m-%d %H:%M:%S'))
            
            return {
                'success': True,
                'expression': expression,
                'next_runs': next_runs,
                'count': count
            }
        except ImportError:
            return {'error': 'croniter模块未安装，请先安装: pip install croniter'}
        except Exception as e:
            return {'error': f'获取下次执行时间失败: {str(e)}'}

    @staticmethod
    def validate_expression(expression: str) -> Dict[str, Any]:
        """验证Crontab表达式"""
        try:
            parts = expression.strip().split()
            if len(parts) != 5:
                return {
                    'success': False,
                    'valid': False,
                    'error': 'Crontab表达式格式错误，必须包含5个字段'
                }
            
            minute, hour, day, month, weekday = parts
            
            def validate_field(field_value, min_val, max_val, name):
                if field_value == '*':
                    return True
                
                parts = field_value.split(',')
                for part in parts:
                    if '/' in part:
                        base, step = part.split('/')
                        if base != '*' and not base.isdigit():
                            return False
                        if not step.isdigit():
                            return False
                        if base != '*':
                            base_val = int(base)
                            if base_val < min_val or base_val > max_val:
                                return False
                    elif '-' in part:
                        start, end = part.split('-')
                        if not start.isdigit() or not end.isdigit():
                            return False
                        start_val = int(start)
                        end_val = int(end)
                        if start_val < min_val or start_val > max_val:
                            return False
                        if end_val < min_val or end_val > max_val:
                            return False
                    else:
                        if not part.isdigit():
                            return False
                        val = int(part)
                        if val < min_val or val > max_val:
                            return False
                
                return True
            
            if not validate_field(minute, 0, 59, '分钟'):
                return {
                    'success': False,
                    'valid': False,
                    'error': '分钟字段值无效，范围应为0-59'
                }
            
            if not validate_field(hour, 0, 23, '小时'):
                return {
                    'success': False,
                    'valid': False,
                    'error': '小时字段值无效，范围应为0-23'
                }
            
            if not validate_field(day, 1, 31, '日'):
                return {
                    'success': False,
                    'valid': False,
                    'error': '日字段值无效，范围应为1-31'
                }
            
            if not validate_field(month, 1, 12, '月'):
                return {
                    'success': False,
                    'valid': False,
                    'error': '月字段值无效，范围应为1-12'
                }
            
            if not validate_field(weekday, 0, 6, '星期'):
                return {
                    'success': False,
                    'valid': False,
                    'error': '星期字段值无效，范围应为0-6（0是周日）'
                }
            
            return {
                'success': True,
                'valid': True,
                'message': 'Crontab表达式格式正确'
            }
        except Exception as e:
            return {
                'success': False,
                'valid': False,
                'error': f'验证Crontab表达式失败: {str(e)}'
            }

    @staticmethod
    def get_field_description(field: str) -> Dict[str, Any]:
        """获取字段描述"""
        descriptions = {
            'minute': {
                'name': '分钟',
                'range': '0-59',
                'description': '每小时的第几分钟执行',
                'examples': ['5', '*/5', '0,15,30,45', '10-20']
            },
            'hour': {
                'name': '小时',
                'range': '0-23',
                'description': '每天的第几小时执行',
                'examples': ['0', '*/2', '9,18', '8-18']
            },
            'day': {
                'name': '日',
                'range': '1-31',
                'description': '每月的第几天执行',
                'examples': ['1', '*/7', '1,15', '1-10']
            },
            'month': {
                'name': '月',
                'range': '1-12',
                'description': '每年的第几个月执行',
                'examples': ['1', '*/3', '1,4,7,10', '6-9']
            },
            'weekday': {
                'name': '星期',
                'range': '0-6',
                'description': '每周的第几天执行（0是周日）',
                'examples': ['0', '1-5', '1,3,5', '*/2']
            }
        }
        
        return descriptions.get(field, {})

    @staticmethod
    def get_special_symbols() -> Dict[str, Any]:
        """获取特殊符号说明"""
        return {
            'success': True,
            'symbols': [
                {
                    'symbol': '*',
                    'name': '所有值',
                    'description': '代表所有可能的值'
                },
                {
                    'symbol': ',',
                    'name': '列表',
                    'description': '用于列出多个值，如 1,3,5 表示第1、3、5个单位'
                },
                {
                    'symbol': '-',
                    'name': '范围',
                    'description': '用于指定范围，如 1-5 表示从1到5'
                },
                {
                    'symbol': '/',
                    'name': '步长',
                    'description': '用于指定步长，如 */5 表示每5个单位'
                }
            ]
        }
