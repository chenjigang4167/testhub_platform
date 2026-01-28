# 数据工厂API接口文档

## 📖 概述

数据工厂模块提供完整的RESTful API接口，支持工具执行、历史记录管理、数据引用等功能。目前提供60个实用工具，涵盖字符处理、编码转换、随机数据生成、加密解密、测试数据生成、JSON处理和Crontab表达式管理等多个场景。

## 🔐 认证

所有API接口都需要JWT认证，请求头需要包含：

```
Authorization: Bearer <access_token>
```

## 📡 API接口列表

### 1. 执行工具

**接口**：`POST /api/data-factory/`

**描述**：执行指定的数据工厂工具

**请求体**：

```json
{
  "tool_name": "format_json",
  "tool_category": "json",
  "tool_scenario": "data_validation",
  "input_data": {
    "json_str": "{\"name\":\"test\"}",
    "indent": 2,
    "sort_keys": false,
    "compress": false
  },
  "is_saved": true,
  "tags": ["test_data", "json"]
}
```

**请求参数说明**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| tool_name | string | 是 | 工具名称，如：format_json, base64_encode, random_int等 |
| tool_category | string | 是 | 工具分类：string/encoding/random/encryption/test_data/json/crontab |
| tool_scenario | string | 是 | 使用场景：data_generate/format_convert/data_validation/encrypt |
| input_data | object | 是 | 工具输入参数，具体参数取决于工具 |
| is_saved | boolean | 否 | 是否保存记录，默认true |
| tags | array | 否 | 标签数组，如：["test_data", "json"] |

**响应示例**：

```json
{
  "id": 1,
  "tool_name": "format_json",
  "tool_category": "json",
  "tool_category_display": "JSON工具",
  "tool_scenario": "data_validation",
  "tool_scenario_display": "数据验证",
  "input_data": {
    "json_str": "{\"name\":\"test\"}",
    "indent": 2,
    "sort_keys": false,
    "compress": false
  },
  "output_data": {
    "success": true,
    "result": "{\n  \"name\": \"test\"\n}",
    "mode": "format",
    "indent": 2,
    "sort_keys": false,
    "original_length": 16,
    "formatted_length": 20,
    "original_lines": 1,
    "formatted_lines": 3
  },
  "is_saved": true,
  "tags": ["test_data", "json"],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**错误响应**：

```json
{
  "error": "工具执行失败: 无效的JSON格式"
}
```

### 2. 获取历史记录列表

**接口**：`GET /api/data-factory/`

**描述**：获取数据工厂使用历史记录

**查询参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| page_size | integer | 否 | 每页数量，默认10 |
| tool_category | string | 否 | 工具分类筛选 |
| tool_name__icontains | string | 否 | 工具名称模糊查询 |
| tags__contains | string | 否 | 标签模糊查询 |
| ordering | string | 否 | 排序字段，如：-created_at（倒序） |

**请求示例**：

```
GET /api/data-factory/?page=1&page_size=20&tool_category=json&tags__contains=test_data
```

**响应示例**：

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/data-factory/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "tool_name": "format_json",
      "tool_category": "json",
      "tool_category_display": "JSON工具",
      "tool_scenario": "data_validation",
      "tool_scenario_display": "数据验证",
      "input_data": {
        "json_str": "{\"name\":\"test\"}"
      },
      "output_data": {
        "result": "{\n  \"name\": \"test\"\n}"
      },
      "is_saved": true,
      "tags": ["test_data", "json"],
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### 3. 获取单条记录详情

**接口**：`GET /api/data-factory/{id}/`

**描述**：获取指定ID的数据工厂记录详情

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | integer | 是 | 记录ID |

**请求示例**：

```
GET /api/data-factory/1/
```

**响应示例**：

```json
{
  "id": 1,
  "tool_name": "format_json",
  "tool_category": "json",
  "tool_category_display": "JSON工具",
  "tool_scenario": "data_validation",
  "tool_scenario_display": "数据验证",
  "input_data": {
    "json_str": "{\"name\":\"test\"}"
  },
  "output_data": {
    "result": "{\n  \"name\": \"test\"\n}"
  },
  "is_saved": true,
  "tags": ["test_data", "json"],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 4. 更新记录

**接口**：`PUT /api/data-factory/{id}/`

**描述**：更新指定ID的数据工厂记录

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | integer | 是 | 记录ID |

**请求体**：

```json
{
  "tags": ["updated_tag", "new_tag"]
}
```

**注意**：通常只允许更新tags字段，其他字段不允许修改。

**响应示例**：

```json
{
  "id": 1,
  "tool_name": "format_json",
  "tool_category": "json",
  "tool_category_display": "JSON工具",
  "tool_scenario": "data_validation",
  "tool_scenario_display": "数据验证",
  "input_data": {
    "json_str": "{\"name\":\"test\"}"
  },
  "output_data": {
    "result": "{\n  \"name\": \"test\"\n}"
  },
  "is_saved": true,
  "tags": ["updated_tag", "new_tag"],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

### 5. 删除记录

**接口**：`DELETE /api/data-factory/{id}/`

**描述**：删除指定ID的数据工厂记录

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | integer | 是 | 记录ID |

**请求示例**：

```
DELETE /api/data-factory/1/
```

**响应示例**：

```json
{
  "message": "记录删除成功"
}
```

### 6. 批量删除记录

**接口**：`POST /api/data-factory/batch-delete/`

**描述**：批量删除数据工厂记录

**请求体**：

```json
{
  "ids": [1, 2, 3, 4, 5]
}
```

**请求参数说明**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| ids | array | 是 | 要删除的记录ID列表 |

**响应示例**：

```json
{
  "message": "成功删除5条记录",
  "deleted_count": 5
}
```

### 7. 下载生成的文件

**接口**：`GET /api/data-factory/download_static_file/{filename}/`

**描述**：下载数据工厂生成的文件（如条形码、二维码图片）

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| filename | string | 是 | 文件名 |

**请求示例**：

```
GET /api/data-factory/download_static_file/qrcode_1704067200_abc123_300px.png
```

**响应**：
- 成功：返回文件二进制数据
- 失败：返回JSON错误信息

**错误响应示例**：

```json
{
  "error": "文件不存在: qrcode_1704067200_abc123_300px.png"
}
```

### 8. 获取标签列表

**接口**：`GET /api/data-factory/tags/`

**描述**：获取所有使用的标签列表

**查询参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| search | string | 否 | 标签名称搜索 |

**请求示例**：

```
GET /api/data-factory/tags/?search=test
```

**响应示例**：

```json
{
  "count": 10,
  "tags": [
    {"name": "test_data", "count": 25},
    {"name": "user_data", "count": 15},
    {"name": "api_data", "count": 10}
  ]
}
```

### 9. 获取统计信息

**接口**：`GET /api/data-factory/statistics/`

**描述**：获取数据工厂使用统计信息

**响应示例**：

```json
{
  "total_records": 1000,
  "category_stats": [
    {"category": "json", "category_display": "JSON工具", "count": 250},
    {"category": "random", "category_display": "随机工具", "count": 200},
    {"category": "test_data", "category_display": "测试数据", "count": 180},
    {"category": "encoding", "category_display": "编码工具", "count": 150},
    {"category": "encryption", "category_display": "加密工具", "count": 100},
    {"category": "string", "category_display": "字符工具", "count": 80},
    {"category": "crontab", "category_display": "Crontab工具", "count": 40}
  ],
  "scenario_stats": [
    {"scenario": "data_generate", "scenario_display": "数据生成", "count": 400},
    {"scenario": "format_convert", "scenario_display": "格式转换", "count": 300},
    {"scenario": "data_validation", "scenario_display": "数据验证", "count": 200},
    {"scenario": "encrypt", "scenario_display": "加密解密", "count": 100}
  ],
  "recent_tools": [
    {"tool_name": "format_json", "count": 50},
    {"tool_name": "random_int", "count": 40},
    {"tool_name": "generate_chinese_name", "count": 30}
  ]
}
```

## 🛠️ 工具列表

### 字符工具（9个）

| 工具名称 | tool_name | 说明 |
|---------|-----------|------|
| 去除空格和换行 | remove_whitespace | 去除文本中的所有空白字符 |
| 字符串替换 | replace_string | 替换文本中的指定字符串 |
| 字符串转义 | escape_string | 将字符串转义为特定格式 |
| 字符串反转义 | unescape_string | 将转义后的字符串还原 |
| 字数统计 | word_count | 统计文本的详细信息（中英文、数字、标点、行数、段落数） |
| 文本对比 | text_diff | 对比两段文本的差异 |
| 正则表达式测试 | regex_test | 测试正则表达式的匹配效果 |
| 大小写转换 | case_convert | 转换文本的大小写 |
| 字符串格式化 | string_format | 对字符串进行格式化处理 |

### 编码工具（12个）

| 工具名称 | tool_name | 说明 |
|---------|-----------|------|
| 生成条形码 | generate_barcode | 生成各种类型的条形码 |
| 生成二维码 | generate_qrcode | 生成二维码图片 |
| 时间戳转换 | timestamp_convert | 时间戳与日期时间互转 |
| 进制转换 | base_convert | 不同进制之间的转换 |
| 中文Unicode转换 | unicode_convert | 中文与Unicode互转 |
| ASCII码转换 | ascii_convert | 字符与ASCII码互转 |
| 颜色值转换 | color_convert | 不同颜色格式之间的转换 |
| Base64编码 | base64_encode | Base64编码 |
| Base64解码 | base64_decode | Base64解码 |
| URL编码 | url_encode | URL编码 |
| URL解码 | url_decode | URL解码 |
| JWT解码 | jwt_decode | 解码JWT令牌 |
| 图片转Base64 | image_to_base64 | 将图片转换为Base64编码 |
| Base64转图片 | base64_to_image | 将Base64编码转换为图片 |

### 随机工具（10个）

| 工具名称 | tool_name | 说明 |
|---------|-----------|------|
| 生成随机整数 | random_int | 生成指定范围内的随机整数 |
| 生成随机浮点数 | random_float | 生成指定范围内的随机浮点数 |
| 生成随机字符串 | random_string | 生成指定长度和类型的随机字符串 |
| 生成UUID | random_uuid | 生成UUID |
| 生成随机布尔值 | random_boolean | 生成随机布尔值 |
| 生成随机MAC地址 | random_mac | 生成随机MAC地址 |
| 生成随机IP地址 | random_ip | 生成随机IP地址（IPv4/IPv6） |
| 生成随机日期 | random_date | 生成指定范围内的随机日期 |
| 生成随机密码 | random_password | 生成随机密码（包含大小写、数字、特殊字符） |
| 生成随机颜色 | random_color | 生成随机颜色数据 |
| 生成随机序列数据 | random_list_element | 从序列中随机选择元素 |

### 加密工具（9个）

| 工具名称 | tool_name | 说明 |
|---------|-----------|------|
| MD5加密 | md5_hash | 使用MD5算法加密文本 |
| SHA1加密 | sha1_hash | 使用SHA1算法加密文本 |
| SHA256加密 | sha256_hash | 使用SHA256算法加密文本 |
| SHA512加密 | sha512_hash | 使用SHA512算法加密文本 |
| 哈希值比对 | hash_compare | 比对两个哈希值是否相同 |
| AES加密 | aes_encrypt | 使用AES算法加密文本 |
| AES解密 | aes_decrypt | 使用AES算法解密文本 |
| 密码强度分析 | password_strength | 分析密码的强度 |
| 生成随机盐值 | generate_salt | 生成随机盐值数据 |

### 测试数据工具（11个）

| 工具名称 | tool_name | 说明 |
|---------|-----------|------|
| 生成中文姓名 | generate_chinese_name | 生成中文姓名 |
| 生成中国手机号 | generate_chinese_phone | 生成中国手机号 |
| 生成中国邮箱 | generate_chinese_email | 生成中国邮箱 |
| 生成中国地址 | generate_chinese_address | 生成中国地址 |
| 生成身份证号 | generate_id_card | 生成随机身份证号（符合校验规则） |
| 生成公司名称 | generate_company | 生成随机公司名称 |
| 生成银行卡号 | generate_bank_card | 生成随机银行卡号（符合Luhn算法） |
| 生成香港身份证号 | generate_hk_id_card | 生成香港身份证号 |
| 生成营业执照号 | generate_business_license | 生成营业执照号 |
| 生成用户档案 | generate_user_profile | 生成完整用户档案 |
| 生成经纬度 | generate_coordinates | 生成随机经纬度数据 |

### JSON工具（10个）

| 工具名称 | tool_name | 说明 |
|---------|-----------|------|
| JSON格式化 | format_json | 格式化JSON字符串（支持缩进、排序键、树形展示） |
| JSON压缩 | compress_json | 压缩JSON字符串 |
| JSON校验 | validate_json | 校验JSON格式是否正确 |
| JSONPath查询 | jsonpath_query | 使用JSONPath表达式查询JSON数据 |
| JSON对比 | json_diff | 对比两个JSON对象的差异 |
| JSON扁平化 | flatten_json | 将嵌套JSON扁平化 |
| JSON路径列表 | list_json_paths | 列出JSON的所有路径 |
| JSON转XML | json_to_xml | 将JSON转换为XML格式 |
| JSON转YAML | json_to_yaml | 将JSON转换为YAML格式 |
| YAML转JSON | yaml_to_json | 将YAML转换为JSON格式 |
| XML转JSON | xml_to_json | 将XML转换为JSON格式 |

### Crontab工具（4个）

| 工具名称 | tool_name | 说明 |
|---------|-----------|------|
| 生成Crontab表达式 | generate_crontab | 生成Crontab定时表达式 |
| 解析Crontab表达式 | parse_crontab | 解析Crontab表达式并显示执行时间 |
| 获取下次执行时间 | get_next_runs | 计算Crontab表达式的下次执行时间 |
| 验证Crontab表达式 | validate_crontab | 验证Crontab表达式是否有效 |

## 📊 工具分类

| 分类值 | 分类名称 | 工具数量 | 说明 |
|--------|---------|---------|------|
| string | 字符工具 | 9 | 字符串处理、文本对比、正则表达式测试等 |
| encoding | 编码工具 | 12 | Base64编解码、时间戳转换、Unicode转换等 |
| random | 随机工具 | 10 | 随机数、随机字符串、UUID、MAC地址、IP地址等 |
| encryption | 加密工具 | 9 | MD5/SHA哈希、AES加密解密、密码强度分析等 |
| test_data | 测试数据 | 11 | 身份证、手机号、邮箱、姓名、地址、公司名称等 |
| json | JSON工具 | 10 | JSON格式化、校验、转换、扁平化、路径列表等 |
| crontab | Crontab工具 | 4 | 生成/解析Crontab表达式、获取下次执行时间等 |

## 🎯 使用场景

| 场景值 | 场景名称 | 说明 |
|--------|---------|------|
| data_generate | 数据生成 | 生成随机数据、测试数据等 |
| format_convert | 格式转换 | 各种格式之间的转换 |
| data_validation | 数据验证 | JSON校验、正则测试等 |
| encrypt | 加密解密 | 各种加密算法 |

## 🔍 常见查询示例

### 查询所有JSON工具的历史记录

```
GET /api/data-factory/?tool_category=json
```

### 查询包含"test"标签的记录

```
GET /api/data-factory/?tags__contains=test
```

### 查询工具名称包含"json"的记录

```
GET /api/data-factory/?tool_name__icontains=json
```

### 查询最近10条记录

```
GET /api/data-factory/?page=1&page_size=10&ordering=-created_at
```

### 组合查询：JSON工具且包含"test"标签

```
GET /api/data-factory/?tool_category=json&tags__contains=test
```

### 查询测试数据工具的记录

```
GET /api/data-factory/?tool_category=test_data
```

### 查询随机工具的记录

```
GET /api/data-factory/?tool_category=random
```

## ⚠️ 错误码

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未认证或Token无效 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 📝 示例代码

### Python示例

```python
import requests

# 配置
BASE_URL = "http://localhost:8000"
ACCESS_TOKEN = "your_access_token_here"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# 执行JSON格式化工具
data = {
    "tool_name": "format_json",
    "tool_category": "json",
    "tool_scenario": "data_validation",
    "input_data": {
        "json_str": '{"name":"test"}',
        "indent": 2
    },
    "is_saved": True,
    "tags": ["test_data"]
}

response = requests.post(
    f"{BASE_URL}/api/data-factory/",
    json=data,
    headers=headers
)

result = response.json()
print(result)

# 获取历史记录
response = requests.get(
    f"{BASE_URL}/api/data-factory/",
    headers=headers
)

records = response.json()
print(records)

# 生成随机身份证号
data = {
    "tool_name": "generate_id_card",
    "tool_category": "test_data",
    "tool_scenario": "data_generate",
    "input_data": {},
    "is_saved": True,
    "tags": ["id_card_data"]
}

response = requests.post(
    f"{BASE_URL}/api/data-factory/",
    json=data,
    headers=headers
)

result = response.json()
print(result)
```

### JavaScript示例

```javascript
// 配置
const BASE_URL = "http://localhost:8000";
const ACCESS_TOKEN = "your_access_token_here";

// 执行JSON格式化工具
const data = {
  tool_name: "format_json",
  tool_category: "json",
  tool_scenario: "data_validation",
  input_data: {
    json_str: '{"name":"test"}',
    indent: 2
  },
  is_saved: true,
  tags: ["test_data"]
};

fetch(`${BASE_URL}/api/data-factory/`, {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${ACCESS_TOKEN}`,
    "Content-Type": "application/json"
  },
  body: JSON.stringify(data)
})
  .then(response => response.json())
  .then(result => console.log(result));

// 获取历史记录
fetch(`${BASE_URL}/api/data-factory/`, {
  headers: {
    "Authorization": `Bearer ${ACCESS_TOKEN}`
  }
})
  .then(response => response.json())
  .then(records => console.log(records));

// 生成随机身份证号
const idCardData = {
  tool_name: "generate_id_card",
  tool_category: "test_data",
  tool_scenario: "data_generate",
  input_data: {},
  is_saved: true,
  tags: ["id_card_data"]
};

fetch(`${BASE_URL}/api/data-factory/`, {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${ACCESS_TOKEN}`,
    "Content-Type": "application/json"
  },
  body: JSON.stringify(idCardData)
})
  .then(response => response.json())
  .then(result => console.log(result));
```

### cURL示例

```bash
# 执行JSON格式化工具
curl -X POST http://localhost:8000/api/data-factory/ \
  -H "Authorization: Bearer your_access_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "format_json",
    "tool_category": "json",
    "tool_scenario": "data_validation",
    "input_data": {
      "json_str": "{\"name\":\"test\"}",
      "indent": 2
    },
    "is_saved": true,
    "tags": ["test_data"]
  }'

# 获取历史记录
curl -X GET http://localhost:8000/api/data-factory/ \
  -H "Authorization: Bearer your_access_token_here"

# 生成随机身份证号
curl -X POST http://localhost:8000/api/data-factory/ \
  -H "Authorization: Bearer your_access_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "generate_id_card",
    "tool_category": "test_data",
    "tool_scenario": "data_generate",
    "input_data": {},
    "is_saved": true,
    "tags": ["id_card_data"]
  }'

# 批量删除记录
curl -X POST http://localhost:8000/api/data-factory/batch-delete/ \
  -H "Authorization: Bearer your_access_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "ids": [1, 2, 3, 4, 5]
  }'
```

## 📚 相关文档

- [数据工厂使用说明.md](./数据工厂使用说明.md) - 完整的功能介绍和使用技巧
- [数据工厂快速开始.md](./数据工厂快速开始.md) - 快速上手指南
- [数据工厂功能说明.md](./数据工厂功能说明.md) - 详细功能说明
- [README.md](../README.md) - 项目整体介绍

## 🔄 版本历史

### v1.3.0 (2026-01-26)
- 🐛 修复 JSONPath 解析问题，支持 `..` 操作符（如 `$..args`）
- ✨ 扩展代码生成语言选项，支持 30+ 种编程语言
- ✨ 实现完整的 curl 命令导入功能，支持所有 255 个 curl 参数
- 🐛 修复 cURL 命令导出格式问题
- 🔧 改进代码生成器，使用 curlconverter 库提高准确性
- 🔧 改进 curl 命令解析，正确处理 HAR 格式的 queryString、headers、cookies、postData
- 🐛 解决 npm 依赖冲突，修复 Sass 弃用警告和 WebAssembly 加载错误
- 📝 完善文档说明

### v1.2.0 (2026-01-22)
- 新增测试数据工具：生成身份证号、生成公司名称、生成银行卡号、生成香港身份证号、生成营业执照号、生成用户档案、生成经纬度
- 新增JSON工具：JSON扁平化、JSON路径列表、YAML转JSON、XML转JSON
- 新增随机工具：生成随机MAC地址、生成随机IP地址、生成随机日期、生成随机密码、生成随机颜色、生成随机序列数据
- 新增加密工具：哈希值比对、密码强度分析、生成随机盐值
- 新增批量删除接口
- 新增标签列表接口
- 更新统计信息接口

### v1.1.0 (2026-01-20)
- 初始版本发布
- 提供50个实用工具
- 支持标签系统
- 支持历史记录管理
- 支持与接口测试和UI测试集成

---

**更新时间**：2026年1月22日
