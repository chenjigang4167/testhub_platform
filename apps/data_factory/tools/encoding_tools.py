# -*- coding: utf-8 -*-
# -----------------------------
# @Author    : 影子
# @Time      : 2026/1/14 20:06
# @Software  : PyCharm
# @FileName  : encoding_tools.py
# -----------------------------
"""
编码工具
"""
import time
import base64
import binascii
import logging
from typing import Dict, Any
from datetime import datetime
from pathlib import Path
import os

try:
    from urllib.parse import quote, unquote, quote_plus, unquote_plus

    URLLIB_AVAILABLE = True
except ImportError:
    URLLIB_AVAILABLE = False

try:
    import jwt

    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

try:
    import barcode
    from barcode.writer import ImageWriter

    BARCODE_AVAILABLE = True
except ImportError:
    BARCODE_AVAILABLE = False

try:
    import qrcode

    QR_CODE_AVAILABLE = True
except ImportError:
    QR_CODE_AVAILABLE = False

try:
    from pyzbar.pyzbar import decode
    from PIL import Image

    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False

logger = logging.getLogger(__name__)


class EncodingTools:
    """编码工具类"""

    @staticmethod
    def download_static_file(filename: str) -> Dict[str, Any]:
        """
        下载 static_files/img 目录下的文件
        :param filename: 要下载的文件名
        :return: 包含文件下载结果的字典
        """
        try:
            # 安全检查：防止路径遍历
            if '..' in filename or filename.startswith('/') or '../' in filename:
                return {'error': '非法文件路径，不允许访问上级目录'}
            static_img_path = Path(EncodingTools.get_static_img_path())
            file_path = static_img_path / filename

            # 验证文件是否在目标目录内（进一步防止路径遍历）
            try:
                file_path.resolve().relative_to(static_img_path.resolve())
            except ValueError:
                return {'error': '非法文件路径，不允许访问其他目录'}

            # 检查文件是否存在
            if not file_path.exists():
                return {'error': f'文件不存在: {filename}'}

            # 检查是否为文件（而非目录）
            if not file_path.is_file():
                return {'error': f'路径不是一个文件: {filename}'}

            # 返回文件信息，实际下载需要框架层实现
            return {
                'success': True,
                'filename': filename,
                'file_path': str(file_path),
                'file_size': file_path.stat().st_size,
                'exists': True
            }
        except Exception as e:
            logger.error(f'文件下载检查失败: {str(e)}')
            return {'error': f'文件下载检查失败: {str(e)}'}

    @staticmethod
    def get_static_img_path() -> str:
        """
        获取 static_files/img 文件夹的路径
        """
        current_file_dir = Path(__file__).parent.parent
        static_img_path = current_file_dir.parent.parent / "static_files" / "img"
        static_img_path.mkdir(parents=True, exist_ok=True)
        return str(static_img_path.resolve())

    @staticmethod
    def generate_barcode(data: str, barcode_type: str = 'code128', save_to_static: bool = True) -> Dict[str, Any]:
        """生成条形码"""
        if not BARCODE_AVAILABLE:
            return {'error': 'barcode模块未安装，请先安装！'}

        barcode_types = ['ean8', 'ean13', 'upc', 'code39', 'code128', 'isbn10', 'isbn13']
        if barcode_type not in barcode_types:
            return {'error': f'不支持的条形码类型: {barcode_type}，支持类型: {", ".join(barcode_types)}'}

        # 验证输入数据
        data = str(data).strip()
        if not data:
            return {'error': '请输入要编码的数据'}

        # 验证EAN13需要12位数字
        if barcode_type == 'ean13':
            if not data.isdigit():
                return {'error': 'EAN13条形码只能包含数字'}
            if len(data) != 12:
                return {'error': f'EAN13条形码需要12位数字，当前输入了{len(data)}位数字'}

        # 验证EAN8需要7位数字
        if barcode_type == 'ean8':
            if not data.isdigit():
                return {'error': 'EAN8条形码只能包含数字'}
            if len(data) != 7:
                return {'error': f'EAN8条形码需要7位数字，当前输入了{len(data)}位数字'}

        # 验证UPC需要11位数字
        if barcode_type == 'upc':
            if not data.isdigit():
                return {'error': 'UPC条形码只能包含数字'}
            if len(data) != 11:
                return {'error': f'UPC条形码需要11位数字，当前输入了{len(data)}位数字'}

        try:
            barcode_class = barcode.get_barcode_class(barcode_type)
            my_barcode = barcode_class(data, writer=ImageWriter())

            if save_to_static:
                # 生成带时间戳的文件名
                import uuid
                timestamp = int(time.time())
                filename = f'barcode_{timestamp}_{uuid.uuid4().hex[:8]}_{barcode_type}'
                static_img_path = Path(EncodingTools.get_static_img_path())
                full_path = static_img_path / filename
                saved_filename = my_barcode.save(str(full_path))
                filepath = str(full_path)
            else:
                filename = f'temp_barcode_{barcode_type}'
                saved_filename = my_barcode.save(filename)
                filepath = filename

            return {
                'success': True,
                'data': data,
                'barcode_type': barcode_type,
                'filename': os.path.basename(saved_filename),
                'filepath': filepath,
                'url': f'/static_files/img/{os.path.basename(saved_filename)}' if save_to_static else None
            }
        except Exception as e:
            logger.error(f'条形码生成失败: {str(e)}')
            return {'error': f'条形码生成失败: {str(e)}'}

    @staticmethod
    def generate_qrcode(data: str, image_size: int = 300, border: int = 4, save_to_static: bool = True) -> Dict[
        str, Any]:
        """生成二维码"""
        if not QR_CODE_AVAILABLE:
            return {'error': 'qrcode模块未安装，请先安装！'}

        try:
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=border,
            )
            qr.add_data(data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # 调整图片大小
            if image_size > 0:
                img = img.resize((image_size, image_size))

            if save_to_static:
                # 生成带时间戳的文件名
                import uuid
                timestamp = int(time.time())
                filename = f'qrcode_{timestamp}_{uuid.uuid4().hex[:8]}_{image_size}px.png'
                static_img_path = Path(EncodingTools.get_static_img_path())
                full_path = static_img_path / filename
                img.save(full_path)
                filepath = str(full_path)
                url = f'/static_files/img/{filename}'
            else:
                filename = f'temp_qrcode_{image_size}px.png'
                img.save(filename)
                filepath = filename
                url = None

            return {
                'success': True,
                'data': data,
                'image_size': image_size,
                'filename': filename,
                'filepath': filepath,
                'url': url
            }

        except Exception as e:
            logger.error(f"二维码生成失败: {str(e)}")
            return {'error': f'二维码生成失败: {str(e)}'}

    @staticmethod
    def decode_qrcode(image_data: str, image_format: str = 'png') -> Dict[str, Any]:
        """解析二维码图片"""
        if not PYZBAR_AVAILABLE:
            return {'error': 'pyzbar模块未安装，请先安装！'}

        try:
            from io import BytesIO
            import base64

            # 处理Base64编码的图片数据
            if image_data.startswith('data:image'):
                # 移除数据URL前缀
                image_data = image_data.split(',')[1]

            # 解码Base64数据
            image_bytes = base64.b64decode(image_data)

            # 创建PIL Image对象
            image = Image.open(BytesIO(image_bytes))

            # 解码二维码
            decoded_objects = decode(image)

            if not decoded_objects:
                return {
                    'success': False,
                    'message': '未检测到二维码',
                    'result': None
                }

            # 提取所有解码结果
            results = []
            for obj in decoded_objects:
                result = {
                    'data': obj.data.decode('utf-8'),
                    'type': obj.type,
                    'rect': {
                        'left': obj.rect.left,
                        'top': obj.rect.top,
                        'width': obj.rect.width,
                        'height': obj.rect.height
                    },
                    'quality': obj.quality
                }
                results.append(result)

            return {
                'success': True,
                'result': results[0]['data'] if len(results) == 1 else results,
                'count': len(results),
                'results': results
            }

        except Exception as e:
            logger.error(f"二维码解析失败: {str(e)}")
            return {'error': f'二维码解析失败: {str(e)}'}

    @staticmethod
    def timestamp_convert(timestamp: Any, convert_type: str = 'to_datetime', timestamp_unit: str = 'auto') -> Dict[
        str, Any]:
        """时间戳转换"""
        try:
            if convert_type == 'to_datetime':
                # 时间戳转日期时间
                timestamp_str = str(timestamp).strip()
                timestamp_float = float(timestamp_str)

                # 自动检测时间戳单位
                if timestamp_unit == 'auto':
                    # 如果时间戳大于 10^11，认为是毫秒
                    if timestamp_float > 1e11:
                        timestamp_unit = 'millisecond'
                    else:
                        timestamp_unit = 'second'

                # 转换为秒
                if timestamp_unit == 'millisecond':
                    timestamp_float = timestamp_float / 1000

                dt = datetime.fromtimestamp(timestamp_float)
                return {
                    'result': dt.strftime('%Y-%m-%d %H:%M:%S'),
                    'iso_format': dt.isoformat(),
                    'date': dt.strftime('%Y-%m-%d'),
                    'time': dt.strftime('%H:%M:%S'),
                    'timezone': dt.tzname(),
                    'timestamp_unit': timestamp_unit
                }
            elif convert_type == 'to_timestamp':
                # 日期时间转时间戳
                dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                timestamp_float = dt.timestamp()
                return {
                    'result': int(timestamp_float),
                    'result_millisecond': int(timestamp_float * 1000),
                    'float_result': timestamp_float
                }
            elif convert_type == 'current_timestamp':
                # 获取当前时间戳
                current_timestamp = time.time()
                dt = datetime.fromtimestamp(current_timestamp)
                return {
                    'timestamp': int(current_timestamp),
                    'timestamp_millisecond': int(current_timestamp * 1000),
                    'datetime': dt.strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                return {'error': f'不支持的转换类型: {convert_type}'}
        except Exception as e:
            logger.error(f'时间戳转换失败: {str(e)}')
            return {'error': f'时间戳转换失败: {str(e)}'}

    @staticmethod
    def base_convert(number: Any, from_base: int = 10, to_base: int = 16) -> Dict[str, Any]:
        """进制转换"""
        try:
            # 将输入转换为字符串
            num_str = str(number).strip()

            # 转换为10进制
            if from_base != 10:
                decimal_num = int(num_str, from_base)
            else:
                decimal_num = int(num_str)

            # 从10进制转换为目标进制
            if to_base == 10:
                result = str(decimal_num)
            elif to_base == 2:
                result = bin(decimal_num)[2:]
            elif to_base == 8:
                result = oct(decimal_num)[2:]
            elif to_base == 16:
                result = hex(decimal_num)[2:].upper()
            else:
                # 自定义进制转换
                digits = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                if to_base > len(digits) or to_base < 2:
                    return {'error': f'不支持的进制: {to_base}'}

                is_negative = decimal_num < 0
                decimal_num = abs(decimal_num)
                result = ''

                while decimal_num > 0:
                    result = digits[decimal_num % to_base] + result
                    decimal_num //= to_base

                if is_negative:
                    result = '-' + result

                result = result or '0'

            return {
                'result': result,
                'from_base': from_base,
                'to_base': to_base,
                'decimal_value': decimal_num
            }
        except Exception as e:
            logger.error(f'进制转换失败: {str(e)}')
            return {'error': f'进制转换失败: {str(e)}'}

    @staticmethod
    def unicode_convert(text: str, convert_type: str = 'to_unicode') -> Dict[str, Any]:
        """中文转Unicode"""
        try:
            if convert_type == 'to_unicode':
                # 中文转Unicode
                result = ''.join([f'\\u{ord(char):04x}' for char in text])
                return {
                    'result': result,
                    'original': text
                }
            elif convert_type == 'from_unicode':
                # Unicode转中文，处理双反斜杠的情况（如 \\u6587）
                text = text.replace('\\\\u', '\\u')
                result = text.encode('utf-8').decode('unicode-escape')
                return {
                    'result': result,
                    'original': text
                }
            else:
                return {'error': f'不支持的转换类型: {convert_type}'}
        except Exception as e:
            logger.error(f'Unicode转换失败: {str(e)}')
            return {'error': f'Unicode转换失败: {str(e)}'}

    @staticmethod
    def ascii_convert(text: str, convert_type: str = 'to_ascii') -> Dict[str, Any]:
        """ASCII码转换"""
        try:
            if convert_type == 'to_ascii':
                # 字符转ASCII
                ascii_codes = [ord(char) for char in text]
                return {
                    'result': ascii_codes,
                    'original': text,
                    'hex': [f'{code:02x}' for code in ascii_codes]
                }
            elif convert_type == 'from_ascii':
                # ASCII转字符，支持逗号分隔或空格分隔的ASCII码
                codes = [int(c.strip()) for c in text.replace(',', ' ').split() if c.strip()]
                result = ''.join([chr(code) for code in codes])
                return {
                    'result': result,
                    'codes': codes
                }
            else:
                return {'error': f'不支持的转换类型: {convert_type}'}
        except Exception as e:
            logger.error(f'ASCII转换失败: {str(e)}')
            return {'error': f'ASCII转换失败: {str(e)}'}

    @staticmethod
    def color_convert(color: str, from_type: str = 'hex', to_type: str = 'rgb') -> Dict[str, Any]:
        """颜色值转换"""
        try:
            # 转换为RGB
            if from_type == 'hex':
                hex_color = color.lstrip('#')
                rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
            elif from_type == 'rgb':
                rgb = tuple(map(int, color.replace('rgb(', '').replace(')', '').split(',')))
            else:
                return {'error': f'不支持的颜色类型: {from_type}'}

            # 转换为目标格式
            if to_type == 'hex':
                result = f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
            elif to_type == 'rgb':
                result = f'rgb({rgb[0]}, {rgb[1]}, {rgb[2]})'
            elif to_type == 'rgba':
                result = f'rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 1.0)'
            elif to_type == 'hsl':
                # RGB转HSL
                r, g, b = [x / 255.0 for x in rgb]
                max_val = max(r, g, b)
                min_val = min(r, g, b)
                l = (max_val + min_val) / 2

                if max_val == min_val:
                    h = s = 0
                else:
                    d = max_val - min_val
                    s = d / (2 - max_val - min_val) if l > 0.5 else d / (max_val + min_val)
                    if max_val == r:
                        h = (g - b) / d + (6 if g < b else 0)
                    elif max_val == g:
                        h = (b - r) / d + 2
                    else:
                        h = (r - g) / d + 4
                    h /= 6

                result = f'hsl({h * 360:.1f}, {s * 100:.1f}%, {l * 100:.1f}%)'
            else:
                return {'error': f'不支持的转换类型: {to_type}'}

            return {
                'result': result,
                'from_type': from_type,
                'to_type': to_type,
                'rgb': rgb
            }
        except Exception as e:
            logger.error(f'颜色转换失败: {str(e)}')
            return {'error': f'颜色转换失败: {str(e)}'}

    @staticmethod
    def base64_encode(text: str, encoding: str = 'utf-8') -> Dict[str, Any]:
        """Base64编码"""
        try:
            encoded = base64.b64encode(text.encode(encoding)).decode(encoding)
            return {
                'result': encoded,
                'original_length': len(text),
                'encoded_length': len(encoded)
            }
        except Exception as e:
            logger.error(f'Base64编码失败: {str(e)}')
            return {'error': f'Base64编码失败: {str(e)}'}

    @staticmethod
    def base64_decode(text: str, encoding: str = 'utf-8') -> Dict[str, Any]:
        """Base64解码"""
        try:
            decoded = base64.b64decode(text.encode(encoding)).decode(encoding)
            return {
                'result': decoded,
                'encoded_length': len(text),
                'decoded_length': len(decoded)
            }
        except binascii.Error:
            return {'error': '无效的Base64数据'}
        except Exception as e:
            logger.error(f'Base64解码失败: {str(e)}')
            return {'error': f'Base64解码失败: {str(e)}'}

    @staticmethod
    def url_encode(data: str, encoding: str = 'utf-8', safe: str = '', plus: bool = False) -> Dict[str, Any]:
        """URL编码"""
        if not URLLIB_AVAILABLE:
            return {'error': 'urllib模块不可用'}
        try:
            if plus:
                encoded = quote_plus(data, encoding=encoding, safe=safe)
            else:
                encoded = quote(data, encoding=encoding, safe=safe)
            return {
                'result': encoded,
                'original_length': len(data),
                'encoded_length': len(encoded)
            }
        except Exception as e:
            logger.error(f'URL编码失败: {str(e)}')
            return {'error': f'URL编码失败: {str(e)}'}

    @staticmethod
    def url_decode(data: str, encoding: str = 'utf-8', plus: bool = False) -> Dict[str, Any]:
        """URL解码"""
        if not URLLIB_AVAILABLE:
            return {'error': 'urllib模块不可用'}
        try:
            if plus:
                decoded = unquote_plus(data, encoding=encoding)
            else:
                decoded = unquote(data, encoding=encoding)
            return {
                'result': decoded,
                'encoded_length': len(data),
                'decoded_length': len(decoded)
            }
        except Exception as e:
            logger.error(f'URL解码失败: {str(e)}')
            return {'error': f'URL解码失败: {str(e)}'}

    @staticmethod
    def jwt_decode(token: str, verify: bool = False, secret: str = '') -> Dict[str, Any]:
        """JWT解码"""
        if not JWT_AVAILABLE:
            return {'error': 'PyJWT模块未安装，请先安装！'}
        try:
            if verify and secret:
                decoded = jwt.decode(token, secret, algorithms=['HS256'])
            else:
                decoded = jwt.decode(token, options={'verify_signature': False})

            header = jwt.get_unverified_header(token)

            return {
                'result': decoded,
                'header': header,
                'payload': decoded,
                'token': token
            }
        except jwt.ExpiredSignatureError:
            return {'error': 'JWT令牌已过期'}
        except jwt.InvalidTokenError as e:
            logger.error(f'无效的JWT令牌: {str(e)}')
            return {'error': f'无效的JWT令牌，请去掉Bearer 后重试'}
        except Exception as e:
            logger.error(f'JWT解码失败: {str(e)}')
            return {'error': f'JWT解码失败: {str(e)}'}
