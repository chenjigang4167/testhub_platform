# TestHub 前端国际化方案

## 概述

本项目使用 **vue-i18n** 实现中英文双语切换，采用模块化语言包组织方式，支持日期、数字格式化。

---

## 目录结构

```
frontend/src/locales/
├── index.js                 # i18n 主配置
├── datetimeFormats.js       # 日期格式化配置
├── numberFormats.js         # 数字格式化配置
├── pluralRules.js           # 复数规则配置
└── lang/
    ├── zh-cn/               # 中文语言包
    │   ├── index.js         # 入口，合并所有模块
    │   ├── common.js        # 通用翻译
    │   ├── nav.js           # 导航菜单
    │   ├── auth.js          # 认证模块
    │   ├── project.js       # 项目管理
    │   ├── testcase.js      # 测试用例
    │   ├── execution.js     # 测试执行
    │   ├── report.js        # 测试报告
    │   ├── review.js        # 评审模块
    │   ├── version.js       # 版本管理
    │   ├── requirement.js   # 需求分析
    │   ├── api-testing.js   # API 测试
    │   ├── ui-automation.js # UI 自动化
    │   ├── configuration.js # 配置中心
    │   └── assistant.js     # AI 助手
    └── en/                  # 英文语言包（同上结构）
```

---

## 使用方法

### 1. 模板中使用

```vue
<template>
  <!-- 基础用法 -->
  <h1>{{ $t('moduleName.title') }}</h1>

  <!-- 属性绑定 -->
  <el-button :title="$t('common.save')">{{ $t('common.save') }}</el-button>

  <!-- 表格列 -->
  <el-table-column :label="$t('project.name')" prop="name" />

  <!-- 带变量 -->
  <span>{{ $t('common.totalItems', { count: total }) }}</span>
</template>
```

### 2. Script 中使用

```vue
<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// 消息提示
ElMessage.success(t('common.saveSuccess'))

// 确认对话框
ElMessageBox.confirm(
  t('common.deleteConfirm'),
  t('common.warning'),
  {
    confirmButtonText: t('common.confirm'),
    cancelButtonText: t('common.cancel'),
    type: 'warning'
  }
)
</script>
```

### 3. 表单验证规则

```javascript
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// 使用 computed 确保响应式
const rules = {
  name: [
    {
      required: true,
      message: computed(() => t('project.nameRequired')),
      trigger: 'blur'
    }
  ]
}
```

### 4. 日期格式化

```vue
<template>
  <!-- 短格式: 2024-01-15 -->
  <span>{{ $d(new Date(item.created_at), 'short') }}</span>

  <!-- 长格式: 2024-01-15 10:30 -->
  <span>{{ $d(new Date(item.created_at), 'long') }}</span>
</template>
```

### 5. 数字格式化

```vue
<template>
  <!-- 百分比: 85.5% -->
  <span>{{ $n(0.855, 'percent') }}</span>

  <!-- 货币: ¥1,234.56 -->
  <span>{{ $n(1234.56, 'currency') }}</span>
</template>
```

---

## 新页面国际化适配

### 步骤 1: 确定模块归属

根据页面功能，确定属于哪个语言包模块：

| 功能 | 语言包文件 |
|------|-----------|
| 项目管理 | `project.js` |
| 测试用例 | `testcase.js` |
| API 测试 | `api-testing.js` |
| UI 自动化 | `ui-automation.js` |
| 配置中心 | `configuration.js` |
| 通用文案 | `common.js` |

### 步骤 2: 添加翻译 key

**中文 (`lang/zh-cn/xxx.js`):**
```javascript
export default {
  // 页面标题
  pageTitle: '页面标题',

  // 表格列
  table: {
    name: '名称',
    status: '状态',
    createdAt: '创建时间',
    actions: '操作'
  },

  // 按钮
  createBtn: '新建',

  // 表单
  form: {
    name: '名称',
    namePlaceholder: '请输入名称',
    nameRequired: '请输入名称'
  },

  // 消息
  createSuccess: '创建成功',
  deleteConfirm: '确定要删除吗？'
}
```

**英文 (`lang/en/xxx.js`):**
```javascript
export default {
  pageTitle: 'Page Title',

  table: {
    name: 'Name',
    status: 'Status',
    createdAt: 'Created At',
    actions: 'Actions'
  },

  createBtn: 'Create',

  form: {
    name: 'Name',
    namePlaceholder: 'Please enter name',
    nameRequired: 'Name is required'
  },

  createSuccess: 'Created successfully',
  deleteConfirm: 'Are you sure to delete?'
}
```

### 步骤 3: 修改 Vue 组件

```vue
<template>
  <div class="page-container">
    <h1>{{ $t('moduleName.pageTitle') }}</h1>

    <el-button type="primary" @click="handleCreate">
      {{ $t('moduleName.createBtn') }}
    </el-button>

    <el-table :data="tableData">
      <el-table-column :label="$t('moduleName.table.name')" prop="name" />
      <el-table-column :label="$t('moduleName.table.status')" prop="status" />
      <el-table-column :label="$t('moduleName.table.createdAt')" prop="created_at">
        <template #default="{ row }">
          {{ $d(new Date(row.created_at), 'long') }}
        </template>
      </el-table-column>
      <el-table-column :label="$t('moduleName.table.actions')">
        <template #default="{ row }">
          <el-button link @click="handleEdit(row)">{{ $t('common.edit') }}</el-button>
          <el-button link type="danger" @click="handleDelete(row)">{{ $t('common.delete') }}</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog :title="$t('moduleName.createBtn')" v-model="dialogVisible">
      <el-form :model="form" :rules="rules">
        <el-form-item :label="$t('moduleName.form.name')" prop="name">
          <el-input v-model="form.name" :placeholder="$t('moduleName.form.namePlaceholder')" />
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'

const { t } = useI18n()

const rules = {
  name: [
    { required: true, message: computed(() => t('moduleName.form.nameRequired')), trigger: 'blur' }
  ]
}

const handleCreate = () => {
  // ...
  ElMessage.success(t('moduleName.createSuccess'))
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm(
    t('moduleName.deleteConfirm'),
    t('common.warning'),
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      type: 'warning'
    }
  )
  // 删除逻辑...
}
</script>
```

---

## 通用翻译 key 参考

以下 key 已在 `common.js` 中定义，可直接使用：

```javascript
// 操作按钮
$t('common.confirm')      // 确定 / OK
$t('common.cancel')       // 取消 / Cancel
$t('common.save')         // 保存 / Save
$t('common.edit')         // 编辑 / Edit
$t('common.delete')       // 删除 / Delete
$t('common.create')       // 创建 / Create
$t('common.search')       // 搜索 / Search
$t('common.reset')        // 重置 / Reset
$t('common.refresh')      // 刷新 / Refresh
$t('common.export')       // 导出 / Export
$t('common.import')       // 导入 / Import

// 提示消息
$t('common.success')      // 操作成功 / Success
$t('common.failed')       // 操作失败 / Failed
$t('common.warning')      // 警告 / Warning
$t('common.loading')      // 加载中 / Loading

// 状态
$t('common.enable')       // 启用 / Enable
$t('common.disable')      // 禁用 / Disable
$t('common.yes')          // 是 / Yes
$t('common.no')           // 否 / No
```

---

## 命名规范

### Key 命名

- 使用 **camelCase** 命名
- 按功能分组（table、form、dialog、message 等）
- 语义化命名，见名知意

```javascript
// 推荐
{
  pageTitle: '页面标题',
  table: {
    name: '名称',
    status: '状态'
  },
  form: {
    nameRequired: '请输入名称'
  }
}

// 不推荐
{
  title1: '页面标题',
  col_name: '名称',
  err1: '请输入名称'
}
```

### 变量插值

使用 `{variableName}` 格式：

```javascript
// 语言包
{
  selectedCount: '已选择 {count} 项',
  deleteConfirmWithName: '确定要删除 {name} 吗？'
}

// 使用
$t('common.selectedCount', { count: 5 })
$t('common.deleteConfirmWithName', { name: item.name })
```

---

## 维护指南

### 添加新语言

1. 在 `lang/` 下创建新目录（如 `ja/`）
2. 复制 `zh-cn/` 下所有文件到新目录
3. 翻译所有文本
4. 在 `locales/index.js` 注册新语言：

```javascript
import ja from './lang/ja'

const i18n = createI18n({
  messages: {
    'zh-cn': zhCN,
    'en': en,
    'ja': ja  // 新增
  }
})
```

5. 在语言切换组件中添加选项

### 检查缺失翻译

开发环境下，控制台会显示缺失的翻译 key 警告。

### IDE 支持

推荐安装 VS Code 插件 **i18n Ally**：
- 显示翻译预览
- 快速跳转到翻译文件
- 检测缺失翻译

---

## 注意事项

1. **不要硬编码文本** - 所有用户可见文本都使用 `$t()`
2. **验证规则用 computed** - 确保语言切换后规则消息也更新
3. **保持中英文 key 一致** - 两个语言包的 key 结构必须相同
4. **测试语言切换** - 开发完成后切换语言测试显示效果
5. **避免过长文本** - 英文通常比中文长，注意 UI 布局

---

## 相关文件

| 文件 | 说明 |
|------|------|
| `frontend/src/locales/index.js` | i18n 主配置 |
| `frontend/src/main.js` | i18n 插件注册 |
| `frontend/src/layout/index.vue` | 语言切换组件 |
| `frontend/src/stores/app.js` | 语言状态管理 |

---

## 参考文档

- [vue-i18n 官方文档](https://vue-i18n.intlify.dev/)
- [Element Plus 国际化](https://element-plus.org/zh-CN/guide/i18n.html)
