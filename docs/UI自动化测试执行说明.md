# UI自动化测试执行说明

## 功能概述

现在UI自动化测试套件支持真实的浏览器自动化执行，可以使用Playwright或Selenium引擎在真实浏览器中运行测试用例。

## 执行流程

### 1. 准备工作

确保已安装必要的依赖：
```bash
source .venv/bin/activate
pip install playwright selenium
playwright install chromium firefox webkit
```

### 2. 创建测试用例

在"测试用例管理"页面创建测试用例，添加测试步骤：
- 点击操作
- 填写表单
- 断言验证
- 截图等

### 3. 创建测试套件

在"套件管理"页面：
1. 点击"新增套件"
2. 输入套件名称和描述
3. 从左侧列表选择测试用例，添加到右侧
4. 调整用例执行顺序
5. 保存套件

### 4. 执行测试

点击套件的"运行"按钮：
1. 选择测试引擎：Playwright（推荐）或 Selenium
2. 选择浏览器：Chrome、Firefox、Safari、Edge
3. 选择执行模式：
   - 有头模式：可以看到浏览器窗口和执行过程
   - 无头模式：后台执行，不显示浏览器窗口
4. 点击"开始执行"

### 5. 查看报告

执行完成后，在"测试报告"页面查看：
- 执行状态
- 通过/失败统计
- 执行时长
- 详细的步骤执行结果

## 支持的操作类型

### 基本操作
- **click**: 点击元素
- **fill**: 填写输入框
- **getText**: 获取文本内容
- **waitFor**: 等待元素出现
- **hover**: 鼠标悬停
- **scroll**: 滚动到元素
- **screenshot**: 截图
- **wait**: 等待指定时间

### 变量占位符支持

测试步骤的输入值支持使用动态函数占位符，语法为 `${function_name(args)}`。

#### 随机数函数
```javascript
${random_int(1000, 9999)}        // 生成随机整数
${random_float(0, 100, 2)}       // 生成随机浮点数
${random_digits(6)}              // 生成随机数字字符串
```

#### 随机字符串函数
```javascript
${random_string(8)}              // 生成随机字母数字字符串
${random_letters(8)}             // 生成随机字母字符串
${random_chinese(2)}             // 生成随机中文字符
```

#### 业务数据函数
```javascript
${random_phone()}                // 生成随机手机号
${random_email()}                // 生成随机邮箱
${random_id_card()}              // 生成随机身份证号
${random_name()}                 // 生成随机中文姓名
${random_company()}              // 生成随机公司名称
${random_address()}              // 生成随机地址
```

#### 时间日期函数
```javascript
${timestamp()}                  // 生成当前时间戳（毫秒）
${timestamp_sec()}              // 生成当前时间戳（秒）
${datetime()}                   // 生成当前日期时间
${date()}                      // 生成当前日期
${time()}                      // 生成当前时间
${date_offset(1)}              // 生成偏移后的日期时间
```

#### 加密和标识符函数
```javascript
${uuid()}                      // 生成UUID
${guid()}                      // 生成GUID
${base64(test123)}             // Base64编码
${md5(test123)}                // MD5加密
${sha1(test123)}               // SHA1加密
${sha256(test123)}             // SHA256加密
${random_mac()}                // 生成MAC地址
${random_ip()}                 // 生成IP地址
${random_password(16)}          // 生成随机密码
```

#### 使用示例

**在输入框中填写随机数据：**
```
操作类型: fill
元素定位器: #username
输入值: user_${random_string(8)}
```

**使用随机手机号：**
```
操作类型: fill
元素定位器: #phone
输入值: ${random_phone()}
```

**使用随机邮箱：**
```
操作类型: fill
元素定位器: #email
输入值: ${random_email()}
```

**组合使用多个占位符：**
```
操作类型: fill
元素定位器: #address
输入值: ${random_address()}，联系人：${random_name()}，电话：${random_phone()}
```

**使用加密函数：**
```
操作类型: fill
元素定位器: #password
输入值: ${random_password(16)}
```

**使用时间戳：**
```
操作类型: fill
元素定位器: #timestamp
输入值: ${timestamp()}
```

**变量解析顺序：**
1. 先解析动态函数占位符（如 `${random_int(1000, 9999)}`）
2. 再替换环境变量（如 `{{base_url}}`）

这样可以确保动态函数生成的值也可以被环境变量引用。

### 断言操作
- **textContains**: 文本包含
- **textEquals**: 文本相等
- **isVisible**: 元素可见
- **exists**: 元素存在
- **hasAttribute**: 属性验证

## 执行原理

1. **后台线程执行**: 测试在后台线程中执行，不阻塞API响应
2. **实时记录**: 每个用例和步骤的执行结果实时记录到数据库
3. **错误处理**: 遇到错误时捕获异常，记录错误信息，继续执行后续用例
4. **统计汇总**: 执行完成后自动计算通过率、执行时长等统计信息

## 引擎对比

### Playwright（推荐）
- ✅ 速度快，API现代化
- ✅ 支持多浏览器（Chromium、Firefox、WebKit）
- ✅ 更好的等待机制
- ✅ 内置截图、录屏功能
- ❌ 需要单独安装浏览器驱动

### Selenium
- ✅ 成熟稳定，社区庞大
- ✅ 支持更多浏览器
- ✅ 可使用系统已安装的浏览器
- ❌ API相对老旧
- ❌ 需要配置WebDriver

## 注意事项

1. **浏览器驱动**:
   - Playwright需要先运行 `playwright install` 安装浏览器
   - Selenium需要确保系统中有对应浏览器和WebDriver

2. **执行环境**:
   - 有头模式需要图形界面环境
   - 服务器部署建议使用无头模式

3. **性能考虑**:
   - 并发执行多个套件可能消耗较多资源
   - 建议根据服务器性能控制并发数

4. **元素定位**:
   - 确保元素定位器准确
   - 建议使用CSS或XPath定位器
   - 可设置备用定位器提高稳定性

## 故障排查

### 问题1: 浏览器未启动
- 检查是否安装了playwright浏览器: `playwright install`
- 检查Selenium WebDriver是否正确配置

### 问题2: 元素定位失败
- 检查元素定位器是否正确
- 增加等待时间
- 使用更稳定的定位策略

### 问题3: 执行超时
- 调整步骤的wait_time参数
- 检查网络连接
- 检查页面加载速度

## 📅 更新日志

### v1.3.0 (2026-01-26)
- 🐛 修复 JSONPath 解析问题，支持 `..` 操作符（如 `$..args`）
- ✨ 扩展代码生成语言选项，支持 30+ 种编程语言
- ✨ 实现完整的 curl 命令导入功能，支持所有 255 个 curl 参数
- 🐛 修复 cURL 命令导出格式问题
- 🔧 改进代码生成器，使用 curlconverter 库提高准确性
- 🔧 改进 curl 命令解析，正确处理 HAR 格式的 queryString、headers、cookies、postData
- 🐛 解决 npm 依赖冲突，修复 Sass 弃用警告和 WebAssembly 加载错误
- 📝 完善文档说明

---

**文档版本**：v1.3.0  
**最后更新**：2026年1月26日
