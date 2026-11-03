"""
阿里云验证码短信发送模块

支持两条互不通用的通道，由 settings.SMS_PROVIDER 选择：
- dysms: 短信服务，Action=SendSms，参数为 PhoneNumbers（复数）
- dypns: 号码认证服务「短信认证」，Action=SendSmsVerifyCode，参数为 PhoneNumber（单数）

两条通道都只作发送通道：验证码由本地生成、存 Redis、本地校验，
切换 provider 不影响已发出的验证码。包含发送频率限制（同一手机号 60 秒内只能发一次）。
"""
import json
import hmac
import hashlib
import base64
import uuid
import time
from datetime import datetime
from urllib.parse import quote
import requests
from django.conf import settings
from .redis_client import get_redis


def _sign(access_key_secret, string_to_sign):
    """阿里云签名 V1 算法"""
    h = hmac.new(
        access_key_secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha1
    )
    return base64.b64encode(h.digest()).decode('utf-8')


def _percent_encode(s):
    """URL 编码（阿里云特殊规则）"""
    return quote(s, safe='-_.~')


def _build_signature(params, access_key_secret):
    """构建阿里云请求签名"""
    sorted_keys = sorted(params.keys())
    canonicalized_query = '&'.join([
        f"{_percent_encode(k)}={_percent_encode(str(params[k]))}"
        for k in sorted_keys
    ])
    string_to_sign = 'POST&%2F&' + _percent_encode(canonicalized_query)
    return _sign(access_key_secret + '&', string_to_sign)


# 两条通道的 RPC 接入点差异：域名 / Action / 手机号参数名（签名算法同为 V1 HMAC-SHA1）
SMS_PROVIDERS = {
    'dysms': {
        'endpoint': 'https://dysmsapi.aliyuncs.com/',
        'action': 'SendSms',
        'version': '2017-05-25',
        'phone_param': 'PhoneNumbers',
    },
    'dypns': {
        'endpoint': 'https://dypnsapi.aliyuncs.com/',
        'action': 'SendSmsVerifyCode',
        'version': '2017-05-25',
        'phone_param': 'PhoneNumber',
    },
}


def resolve_provider(provider=None):
    """解析短信通道名，未指定时使用 settings.SMS_PROVIDER"""
    name = (provider or settings.SMS_PROVIDER or '').strip().lower()
    if name not in SMS_PROVIDERS:
        raise ValueError(
            f'未知的短信通道 {name or "(空)"}，可选 {" / ".join(sorted(SMS_PROVIDERS))}'
        )
    return name


def _provider_config(provider):
    """取该通道的 AccessKey、签名、模板与模板附加占位符"""
    if provider == 'dypns':
        return {
            'access_key_id': settings.DYPNS_ACCESS_KEY_ID,
            'access_key_secret': settings.DYPNS_ACCESS_KEY_SECRET,
            'sign_name': settings.DYPNS_SIGN_NAME,
            'template_code': settings.DYPNS_TEMPLATE_CODE,
            'template_extra': settings.DYPNS_TEMPLATE_PARAM_EXTRA,
        }
    return {
        'access_key_id': settings.SMS_ACCESS_KEY_ID,
        'access_key_secret': settings.SMS_ACCESS_KEY_SECRET,
        'sign_name': settings.SMS_SIGN_NAME,
        'template_code': settings.SMS_REGISTER_TEMPLATE_CODE,
        'template_extra': {},
    }


def send_sms(phone_number, verify_code, provider=None):
    """
    通过阿里云发送验证码短信（验证码本地生成，阿里云只作通道）

    Args:
        phone_number: 手机号
        verify_code: 本地生成的验证码
        provider: 短信通道 dysms | dypns，默认取 settings.SMS_PROVIDER

    Returns:
        (success: bool, result: dict)
    """
    provider = resolve_provider(provider)
    api = SMS_PROVIDERS[provider]
    cfg = _provider_config(provider)

    missing = [key for key in ('access_key_id', 'access_key_secret', 'sign_name', 'template_code')
               if not cfg[key]]
    if missing:
        return False, {'Message': f'{provider} 通道配置缺失: {", ".join(missing)}'}

    template_param = {'code': verify_code}
    template_param.update(cfg['template_extra'])

    params = {
        'AccessKeyId': cfg['access_key_id'],
        'Action': api['action'],
        'Format': 'JSON',
        api['phone_param']: phone_number,
        'SignName': cfg['sign_name'],
        'SignatureMethod': 'HMAC-SHA1',
        'SignatureNonce': str(uuid.uuid4()),
        'SignatureVersion': '1.0',
        'TemplateCode': cfg['template_code'],
        'TemplateParam': json.dumps(template_param, ensure_ascii=False),
        'Timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'Version': api['version'],
    }

    params['Signature'] = _build_signature(params, cfg['access_key_secret'])

    response = requests.post(api['endpoint'], data=params, timeout=10)
    result = response.json()
    return result.get('Code') == 'OK', result


# ========== 验证码相关业务逻辑 ==========

VERIFY_CODE_LENGTH = 6
VERIFY_CODE_TTL = 300        # 验证码 5 分钟有效
SMS_RATE_LIMIT_TTL = 60      # 同一手机号 60 秒内只能发一次


def _generate_verify_code():
    """生成 6 位数字验证码"""
    import random
    return ''.join([str(random.randint(0, 9)) for _ in range(VERIFY_CODE_LENGTH)])


def check_rate_limit(phone_number):
    """检查发送频率限制，返回 (allowed: bool, remaining_seconds: int)"""
    redis_client = get_redis()
    key = f"sms:limit:{phone_number}"
    ttl = redis_client.ttl(key)
    if ttl > 0:
        return False, ttl
    return True, 0


def send_register_verify_code(phone_number, captcha_token, captcha_code):
    """
    发送注册验证码流程：
    1. 校验图形验证码
    2. 校验发送频率限制
    3. 生成 6 位验证码存 Redis
    4. 调用阿里云发送短信
    """
    from apps.users.captcha import validate_captcha

    # 校验图形验证码
    if not validate_captcha(captcha_token, captcha_code):
        return {'success': False, 'error': '图形验证码错误或已过期'}

    # 通道配置错误要早于 Redis 写入失败返回，否则会给该手机号留下 60 秒频控锁
    try:
        provider = resolve_provider()
    except ValueError as exc:
        return {'success': False, 'error': str(exc)}

    # 校验发送频率
    allowed, remaining = check_rate_limit(phone_number)
    if not allowed:
        return {'success': False, 'error': f'发送过于频繁，请 {remaining} 秒后再试'}

    # 生成验证码
    code = _generate_verify_code()
    token = str(uuid.uuid4())

    # 存储到 Redis
    redis_client = get_redis()
    redis_client.setex(f"sms:verify_code:{token}", VERIFY_CODE_TTL, code)
    redis_client.setex(f"sms:limit:{phone_number}", SMS_RATE_LIMIT_TTL, '1')
    # 存储手机号，注册时需要校验手机号与验证码的对应关系
    redis_client.setex(f"sms:phone:{token}", VERIFY_CODE_TTL, phone_number)

    # 发送短信
    success, result = send_sms(
        phone_number=phone_number,
        verify_code=code,
        provider=provider,
    )

    if not success:
        # 发送失败时清理 Redis
        redis_client.delete(f"sms:verify_code:{token}")
        redis_client.delete(f"sms:limit:{phone_number}")
        redis_client.delete(f"sms:phone:{token}")
        return {'success': False, 'error': f'短信发送失败: {result.get("Message", "未知错误")}'}

    return {
        'success': True,
        'verify_code_token': token,
        'message': '验证码已发送',
    }


def validate_verify_code(phone_number, verify_code_token, verify_code):
    """校验短信验证码，返回 (valid: bool, error: str)"""
    redis_client = get_redis()

    # 校验验证码
    code_key = f"sms:verify_code:{verify_code_token}"
    stored_code = redis_client.get(code_key)
    if stored_code is None:
        return False, '验证码已过期，请重新获取'

    stored_code = stored_code.decode('utf-8') if isinstance(stored_code, bytes) else stored_code
    if stored_code != verify_code:
        return False, '验证码错误'

    # 校验手机号是否匹配
    phone_key = f"sms:phone:{verify_code_token}"
    stored_phone = redis_client.get(phone_key)
    stored_phone = stored_phone.decode('utf-8') if isinstance(stored_phone, bytes) else stored_phone
    if stored_phone != phone_number:
        return False, '手机号与验证码不匹配'

    # 校验通过，清理验证码
    redis_client.delete(code_key)
    redis_client.delete(phone_key)

    return True, ''
