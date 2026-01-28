# -*- coding: utf-8 -*-
"""
图片Base64转换工具
"""
import base64
import re
from typing import Dict, Any, Optional
from pathlib import Path
import hashlib
import time


class ImageTools:
    """图片工具类"""

    SUPPORTED_FORMATS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg', 'ico']
    MAX_SIZE_MB = 10
    MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024

    @staticmethod
    def image_to_base64(image_data: bytes | str, image_format: str, include_prefix: bool = True) -> Dict[str, Any]:
        """图片转Base64"""
        try:
            if isinstance(image_data, str):
                try:
                    image_data = base64.b64decode(image_data)
                except Exception:
                    return {'error': '图片数据格式错误，无法解码Base64'}
            
            if len(image_data) > ImageTools.MAX_SIZE_BYTES:
                return {
                    'success': False,
                    'error': f'图片大小超过限制（最大{ImageTools.MAX_SIZE_MB}MB）',
                    'actual_size': len(image_data),
                    'max_size': ImageTools.MAX_SIZE_BYTES
                }
            
            base64_data = base64.b64encode(image_data).decode('utf-8')
            
            mime_type = ImageTools._get_mime_type(image_format)
            
            if include_prefix:
                result = f"data:{mime_type};base64,{base64_data}"
            else:
                result = base64_data
            
            return {
                'success': True,
                'result': result,
                'base64_data': base64_data,
                'mime_type': mime_type,
                'format': image_format,
                'size': len(image_data),
                'size_mb': round(len(image_data) / (1024 * 1024), 2),
                'base64_length': len(base64_data),
                'include_prefix': include_prefix
            }
        except Exception as e:
            return {'error': f'图片转Base64失败: {str(e)}'}

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
    def base64_to_image(base64_str: str) -> Dict[str, Any]:
        """Base64转图片"""
        try:
            data = base64_str.strip()
            
            mime_type = None
            if data.startswith('data:image'):
                match = re.match(r'data:image/(\w+);base64,', data)
                if match:
                    mime_type = match.group(1)
                    base64_data = data.split(',', 1)[1]
                else:
                    return {'error': 'Base64格式错误，无法识别MIME类型'}
            else:
                base64_data = data
            
            try:
                image_data = base64.b64decode(base64_data)
            except Exception as e:
                return {'error': f'Base64解码失败: {str(e)}'}
            
            if len(image_data) > ImageTools.MAX_SIZE_BYTES:
                return {
                    'success': False,
                    'error': f'图片大小超过限制（最大{ImageTools.MAX_SIZE_MB}MB）',
                    'actual_size': len(image_data),
                    'max_size': ImageTools.MAX_SIZE_BYTES
                }
            
            # 生成唯一的文件名
            file_ext = mime_type if mime_type else 'png'
            timestamp = int(time.time())
            hash_obj = hashlib.md5(base64_data.encode('utf-8'))
            hash_str = hash_obj.hexdigest()[:8]
            filename = f"base64_{timestamp}_{hash_str}.{file_ext}"
            
            # 保存图片到 static_files/img 目录
            static_img_path = Path(ImageTools.get_static_img_path())
            file_path = static_img_path / filename
            
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            return {
                'success': True,
                'filename': filename,
                'file_path': str(file_path),
                'url': f"/static_files/img/{filename}",
                'mime_type': mime_type,
                'format': mime_type if mime_type else 'unknown',
                'size': len(image_data),
                'size_mb': round(len(image_data) / (1024 * 1024), 2),
                'base64_length': len(base64_data)
            }
        except Exception as e:
            return {'error': f'Base64转图片失败: {str(e)}'}

    @staticmethod
    def get_image_info(image_data: bytes) -> Dict[str, Any]:
        """获取图片信息"""
        try:
            import io
            from PIL import Image
            
            image = Image.open(io.BytesIO(image_data))
            
            info = {
                'success': True,
                'format': image.format,
                'mode': image.mode,
                'size': image.size,
                'width': image.width,
                'height': image.height,
                'size_bytes': len(image_data),
                'size_mb': round(len(image_data) / (1024 * 1024), 2),
                'has_transparency': image.mode in ('RGBA', 'LA', 'P')
            }
            
            if image.mode == 'P':
                info['has_transparency'] = 'transparency' in image.info
            
            return info
        except ImportError:
            return {
                'success': True,
                'format': 'unknown',
                'size_bytes': len(image_data),
                'size_mb': round(len(image_data) / (1024 * 1024), 2),
                'note': 'PIL模块未安装，无法获取详细信息'
            }
        except Exception as e:
            return {'error': f'获取图片信息失败: {str(e)}'}

    @staticmethod
    def _get_mime_type(format_name: str) -> str:
        """获取MIME类型"""
        mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'bmp': 'image/bmp',
            'svg': 'image/svg+xml',
            'ico': 'image/x-icon'
        }
        return mime_types.get(format_name.lower(), 'image/jpeg')

    @staticmethod
    def validate_image_format(format_name: str) -> Dict[str, Any]:
        """验证图片格式"""
        if format_name.lower() in ImageTools.SUPPORTED_FORMATS:
            return {
                'success': True,
                'valid': True,
                'format': format_name,
                'mime_type': ImageTools._get_mime_type(format_name)
            }
        else:
            return {
                'success': False,
                'valid': False,
                'error': f'不支持的图片格式: {format_name}',
                'supported_formats': ImageTools.SUPPORTED_FORMATS
            }

    @staticmethod
    def get_supported_formats() -> Dict[str, Any]:
        """获取支持的图片格式"""
        return {
            'success': True,
            'formats': ImageTools.SUPPORTED_FORMATS,
            'max_size_mb': ImageTools.MAX_SIZE_MB,
            'max_size_bytes': ImageTools.MAX_SIZE_BYTES
        }

    @staticmethod
    def resize_image(image_data: bytes, max_width: Optional[int] = None, 
                     max_height: Optional[int] = None, quality: int = 85) -> Dict[str, Any]:
        """调整图片大小"""
        try:
            import io
            from PIL import Image
            
            image = Image.open(io.BytesIO(image_data))
            
            original_width, original_height = image.size
            
            if max_width and max_height:
                ratio = min(max_width / original_width, max_height / original_height)
                if ratio < 1:
                    new_width = int(original_width * ratio)
                    new_height = int(original_height * ratio)
                    image = image.resize((new_width, new_height), Image.LANCZOS)
            elif max_width:
                if original_width > max_width:
                    ratio = max_width / original_width
                    new_width = max_width
                    new_height = int(original_height * ratio)
                    image = image.resize((new_width, new_height), Image.LANCZOS)
            elif max_height:
                if original_height > max_height:
                    ratio = max_height / original_height
                    new_height = max_height
                    new_width = int(original_width * ratio)
                    image = image.resize((new_width, new_height), Image.LANCZOS)
            
            output = io.BytesIO()
            image.save(output, format=image.format, quality=quality)
            resized_data = output.getvalue()
            
            return {
                'success': True,
                'resized_data': resized_data,
                'original_size': len(image_data),
                'resized_size': len(resized_data),
                'original_dimensions': (original_width, original_height),
                'resized_dimensions': image.size,
                'compression_ratio': f"{(1 - len(resized_data) / len(image_data)) * 100:.2f}%"
            }
        except ImportError:
            return {'error': 'PIL模块未安装，无法调整图片大小'}
        except Exception as e:
            return {'error': f'调整图片大小失败: {str(e)}'}
