"""
数据工厂工具列表定义
"""

TOOL_LIST = [
    {'name': 'generate_chinese_name', 'display_name': '生成中文姓名', 'description': '生成随机中文姓名', 'scenario': 'test_data', 'icon': 'user'},
    {'name': 'generate_chinese_phone', 'display_name': '生成手机号', 'description': '生成随机中国手机号', 'scenario': 'test_data', 'icon': 'phone'},
    {'name': 'generate_chinese_email', 'display_name': '生成邮箱', 'description': '生成随机邮箱地址', 'scenario': 'test_data', 'icon': 'message'},
    {'name': 'generate_chinese_address', 'display_name': '生成地址', 'description': '生成随机中文地址', 'scenario': 'test_data', 'icon': 'location'},
    {'name': 'generate_id_card', 'display_name': '生成身份证号', 'description': '生成随机身份证号', 'scenario': 'test_data', 'icon': 'ticket'},
    {'name': 'generate_company_name', 'display_name': '生成公司名称', 'description': '生成随机公司名称', 'scenario': 'test_data', 'icon': 'office-building'},
    {'name': 'generate_bank_card', 'display_name': '生成银行卡号', 'description': '生成随机银行卡号', 'scenario': 'test_data', 'icon': 'credit-card'},
    {'name': 'generate_hk_id_card', 'display_name': '生成香港身份证号', 'description': '生成随机香港身份证号', 'scenario': 'test_data', 'icon': 'ticket'},
    {'name': 'generate_business_license', 'display_name': '生成营业执照号', 'description': '生成随机营业执照号', 'scenario': 'test_data', 'icon': 'document'},
    {'name': 'generate_coordinates', 'display_name': '生成经纬度', 'description': '生成随机经纬度数据', 'scenario': 'test_data', 'icon': 'location'},
    {'name': 'generate_user_profile', 'display_name': '生成用户档案', 'description': '生成完整用户档案', 'scenario': 'test_data', 'icon': 'user'},
    {'name': 'format_json', 'display_name': 'JSON格式化', 'description': '格式化或压缩JSON数据', 'scenario': 'json', 'icon': 'list'},
    {'name': 'validate_json', 'display_name': 'JSON校验', 'description': '验证JSON格式的正确性', 'scenario': 'json', 'icon': 'circle-check'},
    {'name': 'json_diff_enhanced', 'display_name': 'JSON对比', 'description': '对比两个JSON数据的差异', 'scenario': 'json', 'icon': 'document-copy'},
    {'name': 'jsonpath_query', 'display_name': 'JSONPath查询', 'description': '使用JSONPath表达式查询JSON数据', 'scenario': 'json', 'icon': 'search'},
    {'name': 'json_flatten', 'display_name': '扁平化JSON', 'description': '将嵌套JSON扁平化', 'scenario': 'json', 'icon': 'grid'},
    {'name': 'json_path_list', 'display_name': 'JSON路径', 'description': '列出JSON的所有路径', 'scenario': 'json', 'icon': 'list'},
    {'name': 'json_to_xml', 'display_name': 'JSON转XML', 'description': '将JSON转换为XML格式', 'scenario': 'json', 'icon': 'share'},
    {'name': 'xml_to_json', 'display_name': 'XML转JSON', 'description': '将XML转换为JSON格式', 'scenario': 'json', 'icon': 'share'},
    {'name': 'json_to_yaml', 'display_name': 'JSON转YAML', 'description': '将JSON转换为YAML格式', 'scenario': 'json', 'icon': 'document'},
    {'name': 'yaml_to_json', 'display_name': 'YAML转JSON', 'description': '将YAML转换为JSON格式', 'scenario': 'json', 'icon': 'document'},
    {'name': 'text_diff', 'display_name': '文本对比', 'description': '对比两段文本的差异', 'scenario': 'string', 'icon': 'document-copy'},
    {'name': 'regex_test', 'display_name': '正则测试', 'description': '测试正则表达式的匹配结果', 'scenario': 'string', 'icon': 'search'},
    {'name': 'remove_whitespace', 'display_name': '去除空格换行', 'description': '去除字符串中的空格和换行符', 'scenario': 'string', 'icon': 'delete'},
    {'name': 'replace_string', 'display_name': '字符串替换', 'description': '替换字符串中的内容', 'scenario': 'string', 'icon': 'edit'},
    {'name': 'escape_string', 'display_name': '字符串转义', 'description': '将字符串进行转义处理', 'scenario': 'string', 'icon': 'lock'},
    {'name': 'unescape_string', 'display_name': '字符串反转义', 'description': '将转义字符串还原', 'scenario': 'string', 'icon': 'unlock'},
    {'name': 'word_count', 'display_name': '字数统计', 'description': '统计字符串的字数和字符数', 'scenario': 'string', 'icon': 'data-line'},
    {'name': 'case_convert', 'display_name': '大小写转换', 'description': '转换字符串的大小写', 'scenario': 'string', 'icon': 'sort'},
    {'name': 'string_format', 'display_name': '字符串格式化', 'description': '格式化字符串', 'scenario': 'string', 'icon': 'edit'},
    {'name': 'generate_barcode', 'display_name': '生成条形码', 'description': '生成各种格式的条形码', 'scenario': 'encoding', 'icon': 'grid'},
    {'name': 'generate_qrcode', 'display_name': '生成二维码', 'description': '生成二维码', 'scenario': 'encoding', 'icon': 'grid'},
    {'name': 'decode_qrcode', 'display_name': '二维码解析', 'description': '解析二维码图片中的内容', 'scenario': 'encoding', 'icon': 'view'},
    {'name': 'timestamp_convert', 'display_name': '时间戳转换', 'description': '时间戳与日期时间相互转换', 'scenario': 'encoding', 'icon': 'clock'},
    {'name': 'base_convert', 'display_name': '进制转换', 'description': '不同进制之间的转换', 'scenario': 'encoding', 'icon': 'sort'},
    {'name': 'unicode_convert', 'display_name': 'Unicode转换', 'description': '中文与Unicode相互转换', 'scenario': 'encoding', 'icon': 'sort'},
    {'name': 'ascii_convert', 'display_name': 'ASCII转换', 'description': '字符与ASCII码相互转换', 'scenario': 'encoding', 'icon': 'sort'},
    {'name': 'color_convert', 'display_name': '颜色值转换', 'description': '不同颜色格式之间的转换', 'scenario': 'encoding', 'icon': 'picture'},
    {'name': 'url_encode', 'display_name': 'URL编码', 'description': '使用URL算法加密数据', 'scenario': 'encoding', 'icon': 'lock'},
    {'name': 'url_decode', 'display_name': 'URL解码', 'description': '使用URL算法解密数据', 'scenario': 'encoding', 'icon': 'unlock'},
    {'name': 'jwt_decode', 'display_name': 'JWT解码', 'description': '解码JWT令牌', 'scenario': 'encoding', 'icon': 'view'},
    {'name': 'image_to_base64', 'display_name': '图片转Base64', 'description': '将图片转换为Base64编码', 'scenario': 'encoding', 'icon': 'picture'},
    {'name': 'base64_to_image', 'display_name': 'Base64转图片', 'description': '将Base64编码转换为图片', 'scenario': 'encoding', 'icon': 'picture'},
    {'name': 'base64_encode', 'display_name': 'Base64编码', 'description': '使用Base64算法加密数据', 'scenario': 'encoding', 'icon': 'lock'},
    {'name': 'base64_decode', 'display_name': 'Base64解码', 'description': '使用Base64算法解密数据', 'scenario': 'encoding', 'icon': 'unlock'},
    {'name': 'random_int', 'display_name': '随机整数', 'description': '生成指定范围的随机整数', 'scenario': 'random', 'icon': 'sort'},
    {'name': 'random_float', 'display_name': '随机浮点数', 'description': '生成指定范围的随机浮点数', 'scenario': 'random', 'icon': 'sort'},
    {'name': 'random_string', 'display_name': '随机字符串', 'description': '生成指定长度的随机字符串', 'scenario': 'random', 'icon': 'sort'},
    {'name': 'random_uuid', 'display_name': '随机UUID', 'description': '生成随机UUID(GUID)', 'scenario': 'random', 'icon': 'sort'},
    {'name': 'random_boolean', 'display_name': '随机布尔值', 'description': '生成随机布尔值', 'scenario': 'random', 'icon': 'sort'},
    {'name': 'random_mac_address', 'display_name': '随机MAC地址', 'description': '生成随机MAC地址', 'scenario': 'random', 'icon': 'sort'},
    {'name': 'random_ip_address', 'display_name': '随机IP地址', 'description': '生成随机IP地址(IPv4/IPv6)', 'scenario': 'random', 'icon': 'sort'},
    {'name': 'random_date', 'display_name': '随机日期', 'description': '生成指定范围内的随机日期', 'scenario': 'random', 'icon': 'clock'},
    {'name': 'random_password', 'display_name': '随机密码', 'description': '生成随机密码(包含大小写、数字、特殊字符)', 'scenario': 'random', 'icon': 'lock'},
    {'name': 'random_color', 'display_name': '随机颜色', 'description': '生成随机颜色数据', 'scenario': 'random', 'icon': 'picture'},
    {'name': 'random_sequence', 'display_name': '随机序列数据', 'description': '生成随机序列数据', 'scenario': 'random', 'icon': 'sort'},
    {'name': 'md5_hash', 'display_name': 'MD5加密', 'description': '生成MD5哈希值', 'scenario': 'encryption', 'icon': 'lock'},
    {'name': 'sha1_hash', 'display_name': 'SHA1加密', 'description': '生成SHA1哈希值', 'scenario': 'encryption', 'icon': 'lock'},
    {'name': 'sha256_hash', 'display_name': 'SHA256加密', 'description': '生成SHA256哈希值', 'scenario': 'encryption', 'icon': 'lock'},
    {'name': 'sha512_hash', 'display_name': 'SHA512加密', 'description': '生成SHA512哈希值', 'scenario': 'encryption', 'icon': 'lock'},
    {'name': 'hash_comparison', 'display_name': '哈希值比对', 'description': '比对两个哈希值是否相同', 'scenario': 'encryption', 'icon': 'sort'},
    {'name': 'aes_encrypt', 'display_name': 'AES加密', 'description': '使用AES算法加密数据', 'scenario': 'encryption', 'icon': 'lock'},
    {'name': 'aes_decrypt', 'display_name': 'AES解密', 'description': '使用AES算法解密数据', 'scenario': 'encryption', 'icon': 'unlock'},
    {'name': 'password_strength', 'display_name': '密码强度分析', 'description': '分析密码的强度', 'scenario': 'encryption', 'icon': 'view'},
    {'name': 'generate_salt', 'display_name': '随机盐值', 'description': '生成随机盐值数据', 'scenario': 'encryption', 'icon': 'sort'},
    {'name': 'generate_expression', 'display_name': '生成Crontab表达式', 'description': '生成Crontab定时任务表达式', 'scenario': 'crontab', 'icon': 'clock'},
    {'name': 'parse_expression', 'display_name': '解析Crontab表达式', 'description': '解析Crontab表达式并显示执行时间', 'scenario': 'crontab', 'icon': 'clock'},
    {'name': 'get_next_runs', 'display_name': '获取下次执行时间', 'description': '获取Crontab表达式的下次执行时间', 'scenario': 'crontab', 'icon': 'clock'},
    {'name': 'validate_expression', 'display_name': '验证Crontab表达式', 'description': '验证Crontab表达式的正确性', 'scenario': 'crontab', 'icon': 'circle-check'}
]

TOOL_CATEGORIES = [
    {
        'category': 'test_data',
        'name': '测试数据',
        'scenario': 'test_data',
        'icon': 'user'
    },
    {
        'category': 'json',
        'name': 'JSON工具',
        'scenario': 'json',
        'icon': 'edit'
    },
    {
        'category': 'string',
        'name': '字符工具',
        'scenario': 'string',
        'icon': 'document'
    },
    {
        'category': 'encoding',
        'name': '编码工具',
        'scenario': 'encoding',
        'icon': 'code'
    },
    {
        'category': 'random',
        'name': '随机工具',
        'scenario': 'random',
        'icon': 'distribute'
    },
    {
        'category': 'encryption',
        'name': '加密工具',
        'scenario': 'encryption',
        'icon': 'lock'
    },
    {
        'category': 'crontab',
        'name': 'Crontab工具',
        'scenario': 'crontab',
        'icon': 'clock'
    }
]

def get_tool_list():
    """获取所有工具列表"""
    return TOOL_LIST

def get_categories():
    """获取所有工具分类"""
    return TOOL_CATEGORIES
