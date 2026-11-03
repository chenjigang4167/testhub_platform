"""短信通道连通性测试：python manage.py send_test_sms 13800000000 [--provider dypns] [--check]

用于验证 SMS_PROVIDER 之外的另一条通道是否仍能发送（切换前先测，避免非默认分支悄悄腐烂）。
--check 只打印解析到的配置，不消耗短信条数。
注意：个人号码认证服务在签名/模板走完审核前处于测试模式，只有控制台绑定的测试手机号能收到短信。
"""
import random

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.users.sms import SMS_PROVIDERS, resolve_provider, send_sms

# 每个通道对应的配置项名（报错时直接给出可粘贴到 .env 的键名）
PROVIDER_CONFIG_KEYS = {
    'dysms': ('SMS_ACCESS_KEY_ID', 'SMS_ACCESS_KEY_SECRET',
              'SMS_SIGN_NAME', 'SMS_REGISTER_TEMPLATE_CODE'),
    'dypns': ('DYPNS_ACCESS_KEY_ID', 'DYPNS_ACCESS_KEY_SECRET',
              'DYPNS_SIGN_NAME', 'DYPNS_TEMPLATE_CODE'),
}


class Command(BaseCommand):
    help = '测试阿里云短信通道（dysms 短信服务 / dypns 号码认证服务）配置与发送是否可用'

    def add_arguments(self, parser):
        parser.add_argument('phone', nargs='?', help='接收测试短信的手机号')
        parser.add_argument('--provider', default=None, choices=sorted(SMS_PROVIDERS),
                            help='短信通道，默认取 settings.SMS_PROVIDER')
        parser.add_argument('--check', action='store_true', help='只检查配置，不发送短信')

    def handle(self, *args, **options):
        try:
            provider = resolve_provider(options['provider'])
        except ValueError as exc:
            raise CommandError(str(exc))

        api = SMS_PROVIDERS[provider]
        config_keys = PROVIDER_CONFIG_KEYS[provider]
        values = {key: getattr(settings, key, '') for key in config_keys}
        missing = [key for key, value in values.items() if not value]

        self.stdout.write(f'通道      : {provider}')
        self.stdout.write(f'接入点    : {api["endpoint"]} (Action={api["action"]})')
        self.stdout.write(f'签名      : {values[config_keys[2]] or "(未配置)"}')
        self.stdout.write(f'模板      : {values[config_keys[3]] or "(未配置)"}')
        self.stdout.write(f'AccessKey : {"已配置" if values[config_keys[0]] else "(未配置)"}')

        if provider == 'dypns':
            extra = settings.DYPNS_TEMPLATE_PARAM_EXTRA
            if extra:
                self.stdout.write(f'模板附加参数: {extra}')

        if missing:
            raise CommandError(f'{provider} 通道配置缺失: {", ".join(missing)}')

        if options['check']:
            self.stdout.write(self.style.SUCCESS('配置完整，未发送短信'))
            return

        if not options['phone']:
            raise CommandError('请提供手机号，或用 --check 只检查配置')

        code = f'{random.randint(0, 999999):06d}'
        success, result = send_sms(phone_number=options['phone'], verify_code=code,
                                   provider=provider)
        if success:
            self.stdout.write(self.style.SUCCESS(
                f'发送成功：{provider} 通道可用（本次验证码 {code}，仅供连通性测试）'))
        else:
            raise CommandError(
                f'发送失败：{result.get("Code", "")} {result.get("Message", "未知错误")}')
