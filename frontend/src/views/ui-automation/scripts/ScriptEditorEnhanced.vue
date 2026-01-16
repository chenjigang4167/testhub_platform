<template>
  <div class="script-editor-enhanced">
    <div class="page-header">
      <h1 class="page-title">{{ $t('uiAutomation.scriptEditor.title') }}</h1>
      <div class="header-actions">
        <el-select v-model="projectId" :placeholder="$t('uiAutomation.common.selectProject')" style="width: 200px; margin-right: 15px" @change="onProjectChange">
          <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
        </el-select>
      </div>
    </div>

    <div class="main-content">
      <!-- 左侧:���素库(页面树形式) -->
      <div class="left-panel">
        <div class="panel-header">
          <h3>{{ $t('uiAutomation.scriptEditor.elementLibrary') }}</h3>
          <el-input
            v-model="elementFilter"
            :placeholder="$t('uiAutomation.scriptEditor.searchElement')"
            clearable
            size="small"
            style="margin-top: 10px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <div class="panel-content">
          <el-tree
            :data="elementTree"
            :filter-node-method="filterElementNode"
            :props="{ children: 'children', label: 'name' }"
            node-key="id"
            default-expand-all
            @node-click="handleElementClick"
          >
            <template #default="{ data }">
              <div class="tree-node">
                <el-icon class="node-icon">
                  <component :is="getTreeNodeIcon(data.type)" />
                </el-icon>
                <span class="node-label">{{ data.name }}</span>
                <div class="node-actions" v-if="data.type === 'element'">
                  <el-button size="small" text @click.stop="insertElementCode(data)" :title="$t('uiAutomation.scriptEditor.clickToInsert')">
                    <el-icon><Plus /></el-icon>
                  </el-button>
                  <el-button size="small" text @click.stop="showElementDetail(data)">
                    <el-icon><View /></el-icon>
                  </el-button>
                </div>
              </div>
            </template>
          </el-tree>
        </div>
      </div>

      <!-- 中间:代码编辑器 -->
      <div class="center-panel">
        <div class="editor-toolbar">
          <div class="toolbar-left">
            <el-select v-model="scriptLanguage" size="small" style="width: 120px">
              <el-option label="JavaScript" value="javascript" />
              <el-option label="Python" value="python" />
            </el-select>
            <el-select v-model="scriptFramework" size="small" style="width: 120px; margin-left: 10px">
              <el-option label="Playwright" value="playwright" />
              <el-option label="Selenium" value="selenium" />
            </el-select>
          </div>
          <div class="toolbar-right">
            <el-button size="small" @click="formatCode">
              <el-icon><Operation /></el-icon>
              {{ $t('uiAutomation.scriptEditor.format') }}
            </el-button>
            <el-button size="small" @click="clearCode">
              <el-icon><Delete /></el-icon>
              {{ $t('uiAutomation.scriptEditor.clear') }}
            </el-button>
            <el-button size="small" type="primary" @click="saveScript" :loading="saving">
              <el-icon><Check /></el-icon>
              {{ $t('uiAutomation.scriptEditor.saveScript') }}
            </el-button>
          </div>
        </div>

        <div class="code-editor-container">
          <textarea
            ref="codeEditor"
            v-model="scriptContent"
            class="code-editor"
            :placeholder="$t('uiAutomation.scriptEditor.editorPlaceholder')"
            @focus="handleEditorFocus"
            @blur="handleEditorBlur"
            @input="handleContentChange"
          />
        </div>

        <div class="editor-status">
          <span>{{ $t('uiAutomation.scriptEditor.line') }}: {{ cursorPosition.line }}, {{ $t('uiAutomation.scriptEditor.column') }}: {{ cursorPosition.column }}</span>
          <span>{{ $t('uiAutomation.scriptEditor.characters') }}: {{ scriptContent.length }}</span>
          <span>{{ $t('uiAutomation.scriptEditor.language') }}: {{ scriptLanguage }}</span>
        </div>
      </div>

      <!-- 右侧:执行日志和元素详情 -->
      <div class="right-panel">
        <el-tabs v-model="rightActiveTab" type="border-card">
          <!-- 执行日志 -->
          <el-tab-pane :label="$t('uiAutomation.scriptEditor.executionLogs')" name="logs">
            <div class="panel-content">
              <div class="log-controls">
                <el-button size="small" @click="clearLogs">
                  <el-icon><Delete /></el-icon>
                  {{ $t('uiAutomation.scriptEditor.clearLogs') }}
                </el-button>
              </div>
              <div class="log-output">
                <div
                  v-for="(log, index) in executionLogs"
                  :key="index"
                  class="log-entry"
                  :class="log.level"
                >
                  <span class="log-time">{{ formatTime(log.timestamp) }}</span>
                  <span class="log-level">{{ log.level.toUpperCase() }}</span>
                  <span class="log-message">{{ log.message }}</span>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 元素详情 -->
          <el-tab-pane :label="$t('uiAutomation.scriptEditor.elementDetail')" name="elementDetail" v-if="selectedElementDetail">
            <div class="panel-content">
              <div class="element-detail">
                <h4>{{ selectedElementDetail.name }}</h4>
                <el-descriptions :column="1" border size="small">
                  <el-descriptions-item :label="$t('uiAutomation.scriptEditor.type')">
                    {{ getElementTypeText(selectedElementDetail.element_type) }}
                  </el-descriptions-item>
                  <el-descriptions-item :label="$t('uiAutomation.scriptEditor.page')">
                    {{ selectedElementDetail.page || $t('uiAutomation.element.notSpecified') }}
                  </el-descriptions-item>
                  <el-descriptions-item :label="$t('uiAutomation.scriptEditor.locatorStrategy')">
                    {{ selectedElementDetail.locator_strategy?.name || selectedElementDetail.locator_strategy }}
                  </el-descriptions-item>
                  <el-descriptions-item :label="$t('uiAutomation.scriptEditor.locatorExpression')">
                    <code>{{ selectedElementDetail.locator_value }}</code>
                  </el-descriptions-item>
                  <el-descriptions-item :label="$t('uiAutomation.scriptEditor.usageCount')">
                    {{ selectedElementDetail.usage_count || 0 }}
                  </el-descriptions-item>
                </el-descriptions>

                <div class="element-actions" style="margin-top: 15px">
                  <el-button size="small" type="primary" @click="insertElementCode(selectedElementDetail)">
                    {{ $t('uiAutomation.scriptEditor.insertCode') }}
                  </el-button>
                  <el-button size="small" @click="validateElement(selectedElementDetail)">
                    {{ $t('uiAutomation.scriptEditor.validateElement') }}
                  </el-button>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Plus, View, Document, Check, Delete, Operation, Folder
} from '@element-plus/icons-vue'

import {
  getUiProjects,
  createTestScript,
  getElementTree,
  getElementGroupTree,
  validateElementLocator
} from '@/api/ui_automation'

// i18n
const { t } = useI18n()

// 响应式数据
const projects = ref([])
const projectId = ref('')
const scriptContent = ref('')
const scriptLanguage = ref('python')
const scriptFramework = ref('playwright')

const elementTree = ref([])
const elementFilter = ref('')
const selectedElementDetail = ref(null)
const executionLogs = ref([])

const cursorPosition = reactive({ line: 1, column: 1 })
const saving = ref(false)

// 标签页控制
const rightActiveTab = ref('logs')

// Monaco编辑器实例
const codeEditor = ref(null)

// 方法定义
const loadProjects = async () => {
  try {
    const response = await getUiProjects({ page_size: 100 })
    projects.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error(t('uiAutomation.scriptEditor.messages.loadProjectsFailed'))
    console.error('获取项目列表失败:', error)
  }
}

const loadElementTree = async () => {
  if (!projectId.value) {
    elementTree.value = []
    return
  }

  try {
    // 并行加载页面树和元素
    const [pageGroupResponse, elementsResponse] = await Promise.all([
      getElementGroupTree({ project: projectId.value }),
      getElementTree({ project: projectId.value })
    ])

    // 构建页面节点
    const buildTree = (groups) => {
      return groups.map(group => ({
        ...group,
        type: 'page',
        children: group.children ? buildTree(group.children) : []
      }))
    }

    const pageNodes = buildTree(pageGroupResponse.data || [])

    // 获取所有元素
    const elements = elementsResponse.data?.results || elementsResponse.data || []

    console.log('=== 智能脚本生成 - 加载元素树 ===')
    console.log('页面节点数:', pageNodes.length)
    console.log('元素总数:', elements.length)

    // 将元素添加到对应页面下
    const attachElementsToPages = (pages) => {
      pages.forEach(page => {
        // 找到属于当前页面的元素
        const pageElements = elements.filter(element => element.group_id === page.id)
        console.log(`页面 ${page.name} (ID: ${page.id}) 找到 ${pageElements.length} 个元素`)

        const elementNodes = pageElements.map(element => ({
          ...element,
          type: 'element'
        }))

        // 将元素添加到页面的子节点中
        page.children = page.children ? [...page.children, ...elementNodes] : [...elementNodes]

        // 递归处理子页面
        if (page.children) {
          attachElementsToPages(page.children.filter(child => child.type === 'page'))
        }
      })
    }

    attachElementsToPages(pageNodes)
    elementTree.value = pageNodes

    addLog('info', t('uiAutomation.scriptEditor.messages.elementsLoaded', { count: countElements(elementTree.value) }))
  } catch (error) {
    console.error('获取元素树失败:', error)
    addLog('error', t('uiAutomation.scriptEditor.messages.loadElementTreeFailed'))
  }
}

// 统计元素数量
const countElements = (tree) => {
  let count = 0
  const traverse = (nodes) => {
    nodes.forEach(node => {
      if (node.type === 'element') count++
      if (node.children) traverse(node.children)
    })
  }
  traverse(tree)
  return count
}

const handleEditorFocus = () => {
  // 编辑器获得焦点时的处理
}

const handleEditorBlur = () => {
  // 编辑器失去焦点时的处理
}

const handleContentChange = () => {
  // 内容变化时更新状态
  updateCursorPosition()
}

const updateCursorPosition = () => {
  if (codeEditor.value) {
    const textarea = codeEditor.value
    const text = textarea.value
    const selectionStart = textarea.selectionStart

    // 计算行号和列号
    const lines = text.substring(0, selectionStart).split('\n')
    cursorPosition.line = lines.length
    cursorPosition.column = lines[lines.length - 1].length + 1
  }
}

const onProjectChange = async () => {
  selectedElementDetail.value = null
  executionLogs.value = []
  scriptContent.value = ''

  await loadElementTree()

  // 代码编辑器已更新(使用 textarea)
}

const filterElementNode = (value, data) => {
  if (!value) return true
  return data.name.indexOf(value) !== -1
}

const handleElementClick = (data) => {
  if (data.type === 'element') {
    selectedElementDetail.value = data
    rightActiveTab.value = 'elementDetail'
  }
}

const showElementDetail = (element) => {
  selectedElementDetail.value = element
  rightActiveTab.value = 'elementDetail'
}

const insertElementCode = (element) => {
  if (element.type !== 'element') return

  const code = generateElementCode(element)
  insertCodeAtCursor(code + '\n')  // 自动换行

  addLog('info', `${t('uiAutomation.scriptEditor.messages.insertCode')}: ${element.name}`)
}

const insertCodeAtCursor = (code) => {
  if (!codeEditor.value) return

  const textarea = codeEditor.value
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const text = textarea.value

  // 在光标位置插入代码
  const newText = text.substring(0, start) + code + text.substring(end)
  scriptContent.value = newText

  // 更新光标位置
  setTimeout(() => {
    textarea.focus()
    textarea.setSelectionRange(start + code.length, start + code.length)
    updateCursorPosition()
  }, 0)
}

const generateElementCode = (element) => {
  const locatorValue = element.locator_value || ''
  const locatorStrategy = element.locator_strategy?.name || element.locator_strategy || 'css'

  if (scriptLanguage.value === 'javascript') {
    switch (scriptFramework.value) {
      case 'playwright':
        return `await page.locator('${locatorValue}').click();`
      case 'selenium':
        return `await driver.findElement(By.${locatorStrategy.toUpperCase()}('${locatorValue}')).click();`
      default:
        return `await page.locator('${locatorValue}').click();`
    }
  } else {
    switch (scriptFramework.value) {
      case 'playwright':
        return `page.locator('${locatorValue}').click()`
      case 'selenium':
        return `driver.find_element(By.${locatorStrategy.toUpperCase()}, '${locatorValue}').click()`
      default:
        return `page.locator('${locatorValue}').click()`
    }
  }
}

// 生成脚本文件名
const generateScriptName = () => {
  const currentProject = projects.value.find(p => p.id === projectId.value)
  const projectName = currentProject?.name || 'Script'
  const language = scriptLanguage.value === 'javascript' ? 'JS' : 'Python'
  const framework = scriptFramework.value === 'playwright' ? 'Playwright' : 'Selenium'
  const date = new Date()
  const dateStr = `${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, '0')}${String(date.getDate()).padStart(2, '0')}`

  // 获取自增数字 - 简单实现，实际应从后端获取
  const timestamp = Date.now() % 1000

  const extension = scriptLanguage.value === 'javascript' ? 'js' : 'py'

  return `${projectName}_${language}_${framework}_${dateStr}_${timestamp}.${extension}`
}

const saveScript = async () => {
  if (!projectId.value) {
    ElMessage.warning(t('uiAutomation.scriptEditor.messages.selectProject'))
    return
  }

  if (!scriptContent.value.trim()) {
    ElMessage.warning(t('uiAutomation.scriptEditor.messages.emptyScript'))
    return
  }

  try {
    saving.value = true

    const scriptName = generateScriptName()

    await createTestScript({
      name: scriptName,
      project: projectId.value,
      script_type: 'CODE',
      content: scriptContent.value,
      language: scriptLanguage.value,
      framework: scriptFramework.value
    })

    ElMessage.success(`${t('uiAutomation.scriptEditor.messages.saveSuccess')}: ${scriptName}`)
    addLog('success', `${t('uiAutomation.scriptEditor.messages.saveSuccess')}: ${scriptName}`)
  } catch (error) {
    console.error('保存脚本失败:', error)
    ElMessage.error(t('uiAutomation.scriptEditor.messages.saveFailed'))
    addLog('error', t('uiAutomation.scriptEditor.messages.saveFailed'))
  } finally {
    saving.value = false
  }
}

const validateElement = async (element) => {
  try {
    const response = await validateElementLocator(element.id)
    const result = response.data

    if (result.is_valid) {
      ElMessage.success(t('uiAutomation.scriptEditor.messages.validatePassed'))
      addLog('info', `${t('uiAutomation.scriptEditor.messages.validatePassed')}: ${element.name}`)
    } else {
      ElMessage.error(`${t('uiAutomation.scriptEditor.messages.validateFailed')}: ${result.validation_message}`)
      addLog('error', `${t('uiAutomation.scriptEditor.messages.validateFailed')}: ${element.name} - ${result.validation_message}`)
    }
  } catch (error) {
    console.error('验证元素失败:', error)
    ElMessage.error(t('uiAutomation.scriptEditor.messages.validateFailed'))
    addLog('error', `${t('uiAutomation.scriptEditor.messages.validateFailed')}: ${element.name}`)
  }
}

const formatCode = () => {
  // 简单的代码格式化
  try {
    if (scriptLanguage.value === 'javascript') {
      let formatted = scriptContent.value
        .replace(/;/g, ';\n')
        .replace(/\{/g, ' {\n')
        .replace(/\}/g, '\n}')
        .replace(/\n\s*\n/g, '\n')

      scriptContent.value = formatted
      addLog('info', t('uiAutomation.scriptEditor.messages.codeFormatted'))
    } else {
      addLog('info', t('uiAutomation.scriptEditor.messages.formatInProgress'))
    }
  } catch (error) {
    addLog('error', t('uiAutomation.scriptEditor.messages.formatFailed'))
  }
}

const clearCode = () => {
  scriptContent.value = ''
  addLog('info', t('uiAutomation.scriptEditor.messages.codeCleared'))
}

const clearLogs = () => {
  executionLogs.value = []
}

const addLog = (level, message) => {
  executionLogs.value.push({
    level,
    message,
    timestamp: new Date()
  })

  // 保持最多100条日志
  if (executionLogs.value.length > 100) {
    executionLogs.value = executionLogs.value.slice(-100)
  }
}

// 辅助方法
const getTreeNodeIcon = (type) => {
  return type === 'page' ? Folder : Document
}

const getElementTypeText = (type) => {
  const typeMap = {
    'BUTTON': t('uiAutomation.element.elementTypes.button'),
    'INPUT': t('uiAutomation.element.elementTypes.input'),
    'LINK': t('uiAutomation.element.elementTypes.link'),
    'DROPDOWN': t('uiAutomation.element.elementTypes.dropdown'),
    'CHECKBOX': t('uiAutomation.element.elementTypes.checkbox'),
    'RADIO': t('uiAutomation.element.elementTypes.radio'),
    'TEXT': t('uiAutomation.element.elementTypes.text'),
    'IMAGE': t('uiAutomation.element.elementTypes.image'),
    'CONTAINER': t('uiAutomation.element.elementTypes.container'),
    'TABLE': t('uiAutomation.element.elementTypes.table'),
    'FORM': t('uiAutomation.element.elementTypes.form'),
    'MODAL': t('uiAutomation.element.elementTypes.modal')
  }
  return typeMap[type] || type
}

const formatTime = (timestamp) => {
  return timestamp.toLocaleTimeString()
}

// 监听器
watch(elementFilter, (val) => {
  // 树形筛选会自动处理
})

watch(scriptLanguage, (newLang) => {
  addLog('info', t('uiAutomation.scriptEditor.messages.switchLanguage', { lang: newLang }))
})

// 组件挂载
onMounted(async () => {
  await loadProjects()

  if (projects.value.length > 0) {
    projectId.value = projects.value[0].id
    await onProjectChange()
  }

  // 为textarea添加事件监听
  if (codeEditor.value) {
    codeEditor.value.addEventListener('click', updateCursorPosition)
    codeEditor.value.addEventListener('keyup', updateCursorPosition)
  }
})
</script>

<style scoped>
.script-editor-enhanced {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e6e6e6;
  background: white;
}

.page-title {
  margin: 0;
  font-size: 24px;
}

.header-actions {
  display: flex;
  align-items: center;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.left-panel {
  width: 300px;
  border-right: 1px solid #e6e6e6;
  display: flex;
  flex-direction: column;
  background: white;
}

.panel-header {
  padding: 15px;
  border-bottom: 1px solid #e6e6e6;
}

.panel-header h3 {
  margin: 0 0 10px 0;
}

.center-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #e6e6e6;
}

.right-panel {
  width: 350px;
}

.panel-content {
  padding: 15px;
  flex: 1;
  overflow-y: auto;
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  border-bottom: 1px solid #e6e6e6;
  background-color: #fafafa;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.code-editor-container {
  flex: 1;
  position: relative;
}

.code-editor {
  width: 100%;
  height: 100%;
  border: none;
  outline: none;
  resize: none;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.5;
  padding: 15px;
  background-color: #1e1e1e;
  color: #d4d4d4;
  tab-size: 2;
}

.editor-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 15px;
  border-top: 1px solid #e6e6e6;
  background-color: #fafafa;
  font-size: 12px;
  color: #666;
}

.tree-node {
  display: flex;
  align-items: center;
  flex: 1;
  justify-content: space-between;
  font-size: 14px;
  padding-right: 8px;
}

.node-icon {
  margin-right: 5px;
  font-size: 16px;
}

.node-label {
  flex: 1;
}

.node-actions {
  display: flex;
  gap: 5px;
}

.log-controls {
  margin-bottom: 10px;
}

.log-output {
  height: 400px;
  overflow-y: auto;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  padding: 10px;
  background-color: #1e1e1e;
  color: #fff;
  font-family: monospace;
  font-size: 12px;
}

.log-entry {
  margin-bottom: 5px;
  display: flex;
  gap: 10px;
}

.log-time {
  color: #888;
}

.log-level {
  font-weight: bold;
  min-width: 60px;
}

.log-entry.info .log-level {
  color: #67c23a;
}

.log-entry.error .log-level {
  color: #f56c6c;
}

.log-entry.success .log-level {
  color: #67c23a;
}

.element-detail {
  padding: 10px;
}

.element-detail h4 {
  margin: 0 0 15px 0;
  color: #333;
}

.element-actions {
  display: flex;
  gap: 10px;
}
</style>
