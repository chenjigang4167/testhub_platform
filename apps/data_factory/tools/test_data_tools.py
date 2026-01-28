# -*- coding: utf-8 -*-
# -----------------------------
# @Author    : 影子
# @Time      : 2026/1/19
# @Software  : PyCharm
# @FileName  : test_data_tools.py
# -----------------------------
"""
测试数据生成工具 - 使用fakerx库生成真实测试数据
"""
import logging
import random
import string

from fakerx import FakerX
from typing import Dict, Any, List

from .china_bank_card import bank_card
from .unified_credit_code import business_license

logger = logging.getLogger(__name__)


class TestDataTools:
    """测试数据工具类 - 使用fakerx生成真实数据"""

    @staticmethod
    def generate_chinese_name(gender: str = 'random', count: int = 1) -> Dict[str, Any]:
        """生成中文姓名"""
        try:
            fake = FakerX(locale='zh_CN')

            def generate_one():
                if gender == 'male':
                    return fake.name_male()
                elif gender == 'female':
                    return fake.name_female()
                else:
                    return fake.name()

            if count == 1:
                return {'result': generate_one()}
            else:
                result = [generate_one() for _ in range(count)]
                return {'result': result, 'count': len(result)}
        except Exception as e:
            return {'error': f'中文姓名生成失败: {str(e)}'}

    @staticmethod
    def generate_chinese_phone(region: str = 'all', count: int = 1) -> Dict[str, Any]:
        """生成中国手机号"""
        try:
            fake = FakerX(locale='zh_CN')

            def generate_one():
                phone = fake.phone_number()
                phone = phone.replace(' ', '').replace('-', '')
                return phone

            if count == 1:
                return {'result': generate_one()}
            else:
                result = [generate_one() for _ in range(count)]
                return {'result': result, 'count': len(result)}
        except Exception as e:
            return {'error': f'手机号生成失败: {str(e)}'}

    @staticmethod
    def generate_chinese_email(domain: str = 'random', count: int = 1) -> Dict[str, Any]:
        """生成中国邮箱"""
        try:
            fake = FakerX(locale='zh_CN')

            def generate_one():
                email = fake.email()
                if domain != 'random':
                    username = email.split('@')[0]
                    email = f'{username}@{domain}'
                return email

            if count == 1:
                return {'result': generate_one()}
            else:
                result = [generate_one() for _ in range(count)]
                return {'result': result, 'count': len(result)}
        except Exception as e:
            return {'error': f'邮箱生成失败: {str(e)}'}

    @staticmethod
    def generate_chinese_address(full_address: bool = True, count: int = 1) -> Dict[str, Any]:
        """生成中国地址"""
        try:
            fake = FakerX(locale='zh_CN')

            def generate_one():
                if full_address:
                    return fake.address()
                else:
                    return fake.city()

            if count == 1:
                return {'result': generate_one()}
            else:
                result = [generate_one() for _ in range(count)]
                return {'result': result, 'count': len(result)}
        except Exception as e:
            return {'error': f'地址生成失败: {str(e)}'}

    @staticmethod
    def generate_id_card(count: int = 1) -> Dict[str, Any]:
        """生成身份证号"""
        try:
            fake = FakerX(locale='zh_CN')

            def generate_one():
                ssn = fake.ssn()
                return ssn

            if count == 1:
                return {'result': generate_one()}
            else:
                result = [generate_one() for _ in range(count)]
                return {'result': result, 'count': len(result)}
        except Exception as e:
            logging.error(f'身份证号生成失败: {str(e)}')
            return {'error': f'身份证号生成失败: {str(e)}'}

    @staticmethod
    def generate_company_name(company_type: str = 'all', count: int = 1) -> Dict[str, Any]:
        """生成公司名称"""
        try:
            fake = FakerX(locale='zh_CN')

            def generate_one():
                company = fake.company()
                if company_type != 'all':
                    company = company.replace('有限公司', company_type)
                return company

            if count == 1:
                return {'result': generate_one()}
            else:
                result = [generate_one() for _ in range(count)]
                return {'result': result, 'count': len(result)}
        except Exception as e:
            logging.error(f'公司名称生成失败: {str(e)}')
            return {'error': f'公司名称生成失败: {str(e)}'}

    @staticmethod
    def generate_bank_card(count: int = 1) -> Dict[str, Any]:
        """生成银行卡号"""
        try:
            def generate_one():
                card = bank_card()
                return card

            if count == 1:
                return {'result': generate_one()}
            else:
                result = [generate_one() for _ in range(count)]
                return {'result': result, 'count': len(result)}
        except Exception as e:
            return {'error': f'银行卡号生成失败: {str(e)}'}

    @staticmethod
    def generate_user_profile(count: int = 1) -> Dict[str, Any]:
        """生成完整的用户档案"""
        try:
            fake = FakerX(locale='zh_CN')

            def generate_one():
                return {
                    'name': fake.name(),
                    'phone': fake.phone_number().replace(' ', '').replace('-', ''),
                    'email': fake.email(),
                    'address': fake.address(),
                    'id_card': fake.ssn(),
                    'company': fake.company(),
                    'job': fake.job(),
                    'age': fake.random_int(min=18, max=65),
                    'gender': fake.random_element(elements=['男', '女']),
                    'birthday': fake.date_of_birth(minimum_age=18, maximum_age=65).strftime('%Y-%m-%d')
                }

            if count == 1:
                return {'result': generate_one()}
            else:
                result = [generate_one() for _ in range(count)]
                return {'result': result, 'count': len(result)}
        except Exception as e:
            return {'error': f'用户档案生成失败: {str(e)}'}

    @staticmethod
    def generate_hk_id_card(count: int = 1) -> Dict[str, Any]:
        """生成香港身份证号"""
        try:
            import random

            def generate_one():
                letters = random.sample(string.ascii_uppercase, random.randint(1, 1))
                numbers = ''.join(random.choices(string.digits, k=6))

                # 计算校验码
                letter_value = (ord(letters[0]) - ord('A') + 1) * 8
                number_values = sum(int(num) * [7, 6, 5, 4, 3, 2][i] for i, num in enumerate(numbers))
                total = letter_value + number_values
                remainder = total % 11

                if remainder == 0:
                    check_code = '0'
                elif remainder == 1:
                    check_code = 'A'
                else:
                    check_code = str(11 - remainder)
                id_card = ''.join(letters) + numbers + '(' + check_code + ')'
                return id_card

            if count == 1:
                return {'result': generate_one()}
            else:
                result = [generate_one() for _ in range(count)]
                return {'result': result, 'count': len(result)}
        except Exception as e:
            logging.error(f'香港身份证号生成失败: {str(e)}')
            return {'error': '香港身份证号生成失败！'}

    @staticmethod
    def generate_business_license(count: int = 1) -> Dict[str, Any]:
        """生成营业执照号"""
        try:
            def generate_one():
                return business_license()

            if count == 1:
                return {'result': generate_one()}
            else:
                result = [generate_one() for _ in range(count)]
                return {'result': result, 'count': len(result)}
        except Exception as e:
            logging.error(f'营业执照号生成失败: {str(e)}')
            return {'error': '营业执照号生成失败，请联系管理员！'}

    @staticmethod
    def generate_coordinates(count: int = 1) -> Dict[str, Any]:
        """生成经纬度"""
        try:
            def generate_one():
                # 中国范围: 经度 73-135, 纬度 18-54
                longitude = round(random.uniform(73.0, 135.0), 6)
                latitude = round(random.uniform(18.0, 54.0), 6)

                return {
                    'longitude': longitude,
                    'latitude': latitude,
                    'longitude_formatted': f'{longitude:.6f}°',
                    'latitude_formatted': f'{latitude:.6f}°'
                }

            if count == 1:
                return {'result': generate_one()}
            else:
                result = [generate_one() for _ in range(count)]
                return {'result': result, 'count': len(result)}
        except Exception as e:
            return {'error': f'经纬度生成失败: {str(e)}'}
