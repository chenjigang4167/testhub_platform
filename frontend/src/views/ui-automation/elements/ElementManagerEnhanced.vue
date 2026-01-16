<template>
  <div class="element-manager">
    <div class="element-layout">
      <!-- 左侧页面树 -->
      <div class="sidebar">
        <div class="sidebar-header">
          <el-select v-model="selectedProject" :placeholder="$t('common.selectProject')" @change="onProjectChange">
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
          <div class="header-actions">
            <el-button type="primary" size="small" @click="showCreatePageDialog = true" :title="$t('uiAutomation.element.createPage')">
              <el-icon><Folder /></el-icon>
            </el-button>
            <el-button type="success" size="small" @click="createEmptyElement" :title="$t('uiAutomation.element.addElement')">
              <el-icon><Plus /></el-icon>
            </el-button>
          </div>
        </div>

        <div class="page-tree">
          <el-tree
            ref="treeRef"
            :key="treeKey"
            :data="treeData"
            :props="treeProps"
            node-key="id"
            :expand-on-click-node="false"
            :default-expanded-keys="expandedKeys"
            @node-click="onNodeClick"
            @node-contextmenu="onNodeRightClick"
            @node-expand="onNodeExpand"
            @node-collapse="onNodeCollapse"
          >
            <template #default="{ node, data }">
              <div class="tree-node">
                <el-icon v-if="data.type === 'page'">
                  <Folder />
                </el-icon>
                <el-icon v-else>
                  <Document />
                </el-icon>

                <!-- 页面名称编辑 -->
                <div v-if="data.type === 'page' && editingNodeId === data.id" class="node-edit">
                  <el-input
                    v-model="editingNodeName"
                    size="small"
                    @blur="savePageName"
                    @keyup.enter="savePageName"
                    @keyup.esc="cancelEdit"
                    ref="editInputRef"
                  />
                </div>

                <!-- 普通显示模式 -->
                <span v-else class="node-label">{{ node.label }}</span>

                <span v-if="data.type === 'element'" class="element-type-tag" :class="data.element_type?.toLowerCase()">
                  {{ getElementTypeLabel(data.element_type) }}
                </span>
              </div>
            </template>
          </el-tree>
        </div>
      </div>

      <!-- 右侧元素详情 -->
      <div class="main-content">
        <div v-if="!selectedElement" class="empty-state">
          <el-empty :description="$t('uiAutomation.element.emptyElementTip')">
            <el-button type="primary" @click="createEmptyElement">{{ $t('uiAutomation.element.createNewElement') }}</el-button>
          </el-empty>
        </div>

        <div v-else class="element-detail">
          <!-- 元素基本信息 -->
          <div class="element-header">
            <div class="element-info">
              <el-input
                v-model="selectedElement.name"
                :placeholder="$t('uiAutomation.element.elementNamePlaceholder')"
                size="small"
                style="width: 300px; margin-right: 10px"
              />
              <el-select v-model="selectedElement.element_type" :placeholder="$t('uiAutomation.element.elementType')" size="small" style="width: 120px;">
                <el-option :label="$t('uiAutomation.element.elementTypes.button')" value="BUTTON" />
                <el-option :label="$t('uiAutomation.element.elementTypes.input')" value="INPUT" />
                <el-option :label="$t('uiAutomation.element.elementTypes.link')" value="LINK" />
                <el-option :label="$t('uiAutomation.element.elementTypes.dropdown')" value="DROPDOWN" />
                <el-option :label="$t('uiAutomation.element.elementTypes.checkbox')" value="CHECKBOX" />
                <el-option :label="$t('uiAutomation.element.elementTypes.radio')" value="RADIO" />
                <el-option :label="$t('uiAutomation.element.elementTypes.text')" value="TEXT" />
                <el-option :label="$t('uiAutomation.element.elementTypes.image')" value="IMAGE" />
                <el-option :label="$t('uiAutomation.element.elementTypes.table')" value="TABLE" />
                <el-option :label="$t('uiAutomation.element.elementTypes.form')" value="FORM" />
                <el-option :label="$t('uiAutomation.element.elementTypes.modal')" value="MODAL" />
              </el-select>
              <el-button size="small" @click="saveElement" :loading="saving" ref="saveButtonRef">
                {{ $t('uiAutomation.common.save') }}
              </el-button>
            </div>
          </div>

          <!-- 元素配置 -->
          <div class="element-form">
            <el-form :key="formKey" :model="selectedElement" label-width="100px" size="small">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item :label="$t('uiAutomation.element.page')">
                    <el-select v-model="selectedElement.page" :placeholder="$t('uiAutomation.element.selectPage')">
                      <el-option
                        v-for="page in pages"
                        :key="page.id"
                        :label="page.name"
                        :value="page.name"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item :label="$t('uiAutomation.element.componentName')">
                    <el-input v-model="selectedElement.component_name" :placeholder="$t('uiAutomation.element.componentNamePlaceholder')" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item :label="$t('uiAutomation.element.locatorStrategy')" prop="locator_strategy_id">
                    <el-select
                      v-model="selectedElement.locator_strategy_id"
                      :key="`strategy-${formKey}-${selectedElement.locator_strategy_id || 'null'}`"
                      :placeholder="$t('uiAutomation.element.rules.strategyRequired')"
                      value-key="id"
                    >
                      <el-option
                        v-for="strategy in locatorStrategies"
                        :key="strategy.id"
                        :label="strategy.name"
                        :value="strategy.id"
                      />
                    </el-select>
                    <!-- 调试信息 -->
                    <div style="font-size: 10px; color: #666; margin-top: 2px;">
                      {{ $t('uiAutomation.element.debugInfo') }}: {{ $t('uiAutomation.element.currentValue') }}={{selectedElement.locator_strategy_id}} ({{typeof selectedElement.locator_strategy_id}})
                    </div>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item :label="$t('uiAutomation.element.waitTimeout') + '(' + $t('uiAutomation.element.waitTimeoutUnit') + ')'">
                    <el-input-number v-model="selectedElement.wait_timeout" :min="1" :max="60" style="width: 100%" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item :label="$t('uiAutomation.element.forceAction')">
                    <el-switch
                      v-model="selectedElement.force_action"
                      :active-text="$t('uiAutomation.element.forceActionEnabled')"
                      :inactive-text="$t('uiAutomation.element.forceActionDisabled')"
                    />
                    <div class="form-help-text" style="margin-top: 5px;">
                      {{ $t('uiAutomation.element.forceActionTip') }}
                    </div>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item :label="$t('uiAutomation.element.locatorExpression')" prop="locator_value">
                <el-input v-model="selectedElement.locator_value" :placeholder="$t('uiAutomation.element.locatorExpressionPlaceholder')" />
                <div class="form-help-text">
                  {{ $t('uiAutomation.element.locatorTip.title') }}<br>
                  - {{ $t('uiAutomation.element.locatorTip.id') }}<br>
                  - {{ $t('uiAutomation.element.locatorTip.css') }}<br>
                  - {{ $t('uiAutomation.element.locatorTip.xpath') }}<br>
                  - {{ $t('uiAutomation.element.locatorTip.other') }}
                </div>
              </el-form-item>

              <el-form-item :label="$t('uiAutomation.common.description')">
                <el-input v-model="selectedElement.description" type="textarea" :rows="3" :placeholder="$t('uiAutomation.element.descriptionPlaceholder')" />
              </el-form-item>
            </el-form>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建页面对话框 -->
    <el-dialog v-model="showCreatePageDialog" :title="$t('uiAutomation.element.createPageTitle')" width="500px">
      <el-form ref="pageFormRef" :model="pageForm" :rules="pageRules" label-width="100px">
        <el-form-item :label="$t('uiAutomation.element.pageName')" prop="name">
          <el-input v-model="pageForm.name" :placeholder="$t('uiAutomation.element.pageNamePlaceholder')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.element.parentPage')">
          <el-select v-model="pageForm.parent_page" :placeholder="$t('uiAutomation.element.selectParentPage')" clearable>
            <el-option
              v-for="page in getAllPages()"
              :key="page.id"
              :label="page.name"
              :value="page.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.common.description')" prop="description">
          <el-input v-model="pageForm.description" type="textarea" :rows="3" :placeholder="$t('uiAutomation.element.descriptionPlaceholder')" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreatePageDialog = false">{{ $t('uiAutomation.common.cancel') }}</el-button>
        <el-button type="primary" @click="createPage">{{ $t('uiAutomation.common.confirm') }}</el-button>
      </template>
    </el-dialog>

    <!-- 右键菜单 -->
    <ul v-show="showContextMenu" class="context-menu" :style="{ left: contextMenuX + 'px', top: contextMenuY + 'px' }">
      <li @click="addContextElement">{{ $t('uiAutomation.element.contextMenu.addElement') }}</li>
      <li @click="addSubPage">{{ $t('uiAutomation.element.contextMenu.addSubPage') }}</li>
      <li @click="editNode">{{ $t('uiAutomation.element.contextMenu.edit') }}</li>
      <li @click="deleteNode">{{ $t('uiAutomation.element.contextMenu.delete') }}</li>
    </ul>

    <!-- 编辑页面对话框 -->
    <el-dialog v-model="showEditPageDialog" :title="$t('uiAutomation.element.editPageTitle')" width="500px">
      <el-form ref="editPageFormRef" :model="editPageForm" :rules="pageRules" label-width="100px">
        <el-form-item :label="$t('uiAutomation.element.pageName')" prop="name">
          <el-input v-model="editPageForm.name" :placeholder="$t('uiAutomation.element.pageNamePlaceholder')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.element.parentPage')">
          <el-select v-model="editPageForm.parent_page" :placeholder="$t('uiAutomation.element.selectParentPage')" clearable>
            <el-option
              v-for="page in getAllPagesExceptCurrent(editPageForm.id)"
              :key="page.id"
              :label="page.name"
              :value="page.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.common.description')" prop="description">
          <el-input v-model="editPageForm.description" type="textarea" :rows="3" :placeholder="$t('uiAutomation.element.descriptionPlaceholder')" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showEditPageDialog = false">{{ $t('uiAutomation.common.cancel') }}</el-button>
        <el-button type="primary" @click="updatePage">{{ $t('uiAutomation.common.save') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, FolderAdd, Document, Search, Edit, Delete,
  Folder, Document as DocumentIcon, Operation, DocumentCopy, ArrowDown
} from '@element-plus/icons-vue'
import {
  getUiProjects,
  getElements,
  createElement,
  getElementDetail,
  updateElement,
  deleteElement,
  getElementTree,
  getElementGroupTree,
  getElementGroups,
  createElementGroup,
  updateElementGroup,
  deleteElementGroup,
  getLocatorStrategies,
  validateElementLocator,
  generateElementSuggestions
} from '@/api/ui_automation'

// 国际化
const { t } = useI18n()

// 响应式数据
const projects = ref([])
const selectedProject = ref('')
const pages = ref([])
const locatorStrategies = ref([])
const treeData = ref([])
const selectedElement = ref(null)
const expandedKeys = ref([])
const treeKey = ref(0) // 用于强制重新渲染树组件
const formKey = ref(0) // 用于强制重新渲染表单组件

// 表单引用
const treeRef = ref(null)
const pageFormRef = ref(null)
const editPageFormRef = ref(null)

// 对话框控制
const showCreatePageDialog = ref(false)
const showEditPageDialog = ref(false)

// 右键菜单
const showContextMenu = ref(false)
const contextMenuX = ref(0)
const contextMenuY = ref(0)
const rightClickedNode = ref(null)

// 表单数据
const pageForm = reactive({
  name: '',
  description: '',
  parent_page: null
})

const editPageForm = reactive({
  id: null,
  name: '',
  description: '',
  parent_page: null
})

// 树形组件配置
const treeProps = {
  children: 'children',
  label: 'name'
}

// 表单验证规则
const pageRules = computed(() => ({
  name: [
    { required: true, message: t('uiAutomation.element.rules.pageNameRequired'), trigger: 'blur' }
  ]
}))

// 获取元素类型标签
const getElementTypeLabel = (type) => {
  const typeKey = type?.toLowerCase()
  const typeMap = {
    'button': t('uiAutomation.element.elementTypes.button'),
    'input': t('uiAutomation.element.elementTypes.input'),
    'link': t('uiAutomation.element.elementTypes.link'),
    'dropdown': t('uiAutomation.element.elementTypes.dropdown'),
    'checkbox': t('uiAutomation.element.elementTypes.checkbox'),
    'radio': t('uiAutomation.element.elementTypes.radio'),
    'text': t('uiAutomation.element.elementTypes.text'),
    'image': t('uiAutomation.element.elementTypes.image'),
    'table': t('uiAutomation.element.elementTypes.table'),
    'form': t('uiAutomation.element.elementTypes.form'),
    'modal': t('uiAutomation.element.elementTypes.modal')
  }
  return typeMap[typeKey] || type
}

// 获取所有页面
const getAllPages = () => {
  const allPages = []

  const traverse = (nodes) => {
    nodes.forEach(node => {
      if (node.type === 'page') {
        allPages.push({
          id: node.id,
          name: node.name
        })
      }
      if (node.children) {
        traverse(node.children)
      }
    })
  }

  traverse(treeData.value)
  return allPages
}

// 获取所有页面（除了指定ID的页面）
const getAllPagesExceptCurrent = (currentId) => {
  const allPages = []

  const traverse = (nodes) => {
    nodes.forEach(node => {
      if (node.type === 'page' && node.id !== currentId) {
        allPages.push({
          id: node.id,
          name: node.name
        })
      }
      if (node.children) {
        traverse(node.children)
      }
    })
  }

  traverse(treeData.value)
  return allPages
}

// 页面名称编辑相关
const editingNodeId = ref(null)
const editingNodeName = ref('')
const editInputRef = ref(null)

// 状态
const saving = ref(false)
const validating = ref(false)
const generating = ref(false)
const suggestions = ref([])


// 将关键变量暴露到window对象，方便在控制台调试
const exposeToWindow = () => {
  if (typeof window !== 'undefined') {
    window.ELEMENTS_DEBUG = {
      treeData,
      projects,
      selectedElement,
      loadElementTree,
      treeRef: typeof treeRef !== 'undefined' ? treeRef : null,
      expandedKeys,
      pages,
      $vm: { // 当前组件实例
        treeData: treeData.value,
        projects: projects.value,
        pages: pages.value,
        expandedKeys: expandedKeys.value
      }
    }
    console.log('=== Vue组件调试信息已暴露 ===')
    console.log('Window可用调试变量已设置')
    console.log('控制台可直接访问:')
    console.log('  window.ELEMENTS_DEBUG.treeData')
    console.log('  window.ELEMENTS_DEBUG.projects')
    console.log('  window.ELEMENTS_DEBUG.selectedElement')
    console.log('==============================')
  }
}

// 组件挂载
onMounted(async () => {
  console.log('=== 组件挂载开始 ===')

  await loadProjects()
  await loadLocatorStrategies()

  console.log('项目数量:', projects.value.length)
  console.log('定位策略:', locatorStrategies.value.length)

  if (projects.value.length > 0) {
    console.log('设置初始项目为:', projects.value[0].id)
    selectedProject.value = projects.value[0].id
    await onProjectChange()
    console.log('onProjectChange完成')
  }

  // 暴露调试信息
  exposeToWindow()

  console.log('=== 组件挂载完成 ===')
})

// 加载项目列表
const loadProjects = async () => {
  try {
    const response = await getUiProjects()
    projects.value = response.data?.results || response.data || []
  } catch (error) {
    console.error('获取项目列表失败:', error)
  }
}

// 提供控制台调试帮助函数
const debugTree = () => {
  if (typeof window !== 'undefined') {
    console.log('=== 树数据调试 ===')
    console.log('treeData:', treeData.value)
    console.log('页面对象:',
      treeData.value.map(p => ({
        id: p.id,
        name: p.name,
        type: p.type,
        children: p.children?.length || 0,
        elementChildren: p.children?.filter(c => c.type === 'element').map(e => e.name) || []
      }))
    )

    // 找出所有元素
    const allElements = []
    const findElements = (nodes, parent) => {
      nodes.forEach(node => {
        if (node.type === 'element') {
          allElements.push({
            name: node.name,
            id: node.id,
            parent: parent
          })
        } else if (node.type === 'page' && node.children) {
          findElements(node.children, node.name)
        }
      })
    }
    findElements(treeData.value, null)
    console.log('所有元素:', allElements)

    // 暴露到window
    window.debugTreeData = debugTree
    console.log('调试函数已挂载到 window.debugTreeData()')
    console.log('===============================')
  }
}

// 加载定位策略
const loadLocatorStrategies = async () => {
  try {
    const response = await getLocatorStrategies()
    locatorStrategies.value = response.data?.results || response.data || []
  } catch (error) {
    console.error('获取定位策略失败:', error)
  }
}

// 加载页面（分组）
const loadPages = async () => {
  if (!selectedProject.value) return

  try {
    const response = await getElementGroups({ project: selectedProject.value })
    pages.value = response.data?.results || response.data || []
  } catch (error) {
    console.error('获取页面失败:', error)
  }
}

// 加载页面树结构
const loadPageTree = async () => {
  if (!selectedProject.value) return

  try {
    const response = await getElementGroupTree({ project: selectedProject.value })
    // 构建完整的树形结构
    const buildTree = (groups) => {
      return groups.map(group => ({
        ...group,
        type: 'page',
        children: group.children ? buildTree(group.children) : []
      }))
    }

    treeData.value = buildTree(response.data || [])
  } catch (error) {
    console.error('获取页面树失败:', error)
    treeData.value = []
  }
}

// 加载元素树
const loadElementTree = async () => {
  if (!selectedProject.value) {
    treeData.value = []
    return
  }

  try {
    // 并行加载页面树和元素
    const [pageTreeResponse, elementsResponse] = await Promise.all([
      getElementGroupTree({ project: selectedProject.value }),
      getElementTree({ project: selectedProject.value })
    ])

    // 构建完整的树形结构
    const buildTree = (groups) => {
      return groups.map(group => ({
        ...group,
        type: 'page',
        children: group.children ? buildTree(group.children) : []
      }))
    }

    const pageNodes = buildTree(pageTreeResponse.data || [])

    // 调试信息 - 检查API返回的完整响应结构
    console.log('=== 加载元素树调试 ===')
    console.log('页面树响应:', pageTreeResponse)
    console.log('元素响应:', elementsResponse)

    // 打印原始数据进行分析
    console.log('页面树原始数据:', JSON.parse(JSON.stringify(pageTreeResponse.data || []), null, 2))

    const elements = elementsResponse.data?.results || elementsResponse.data || []
    console.log('提取的元素列表:', elements)

    // 获取所有页面的ID，用于调试
    const pageIds = pageNodes.map(page => page.id)
    console.log('页面ID列表:', pageIds)

    // 将元素添加到对应页面下
    const attachElementsToPages = (pages) => {
      pages.forEach(page => {
        // 找到属于当前页面的元素
        const pageElements = elements.filter(element => element.group_id === page.id)
        console.log(`页面 ${page.name} (ID: ${page.id}) 找到 ${pageElements.length} 个关联元素`, pageElements)

        const elementNodes = pageElements.map(element => ({
          ...element,
          type: 'element'
        }))

        // 将元素添加到页面的子节点中
        page.children = page.children ? [...page.children, ...elementNodes] : [...elementNodes]
        console.log(`页面 ${page.name} 现在有 ${page.children.filter(c => c.type === 'element').length} 个子元素`)

        // 递归处理子页面
        if (page.children) {
          attachElementsToPages(page.children.filter(child => child.type === 'page'))
        }
      })
    }

    attachElementsToPages(pageNodes)
    console.log('最终treeData:', pageNodes)
    treeData.value = pageNodes

    // 将treeData暴露到window，方便在控制台调试
    if (typeof window !== 'undefined') {
      window.vue_treeData = treeData.value
      console.log('treeData已挂载到window.vue_treeData，可在控制台查看')
      console.log('当前treeData结构:', JSON.parse(JSON.stringify(treeData.value)).map(p => ({
        name: p.name,
        id: p.id,
        children: p.children?.filter(c => c.type === 'element').length || 0
      })))
    }
  } catch (error) {
    console.error('获取元素树失败:', error)
    treeData.value = []
  }
}

// 项目切换
const onProjectChange = async () => {
  selectedElement.value = null
  suggestions.value = []

  console.log('=== 项目切换调试 ===')
  console.log('当前项目ID:', selectedProject.value)

  await Promise.all([
    loadPages(),
    loadElementTree()
  ])

  console.log('项目切换完成，检查treeData:', treeData.value)
  console.log('treeData长度:', treeData.value.length)
  if (treeData.value.length > 0) {
    console.log('第一页信息:', {
      id: treeData.value[0].id,
      name: treeData.value[0].name,
      type: treeData.value[0].type,
      children: treeData.value[0].children?.length || 0
    })
  }

  // 项目切换时强制刷新树
  treeKey.value += 1
}

// 创建空元素
const createEmptyElement = () => {
  selectedElement.value = {
    name: '',
    element_type: 'BUTTON',
    page: '',
    component_name: '',
    locator_strategy_id: null, // 使用null而不是空字符串
    locator_value: '',
    wait_timeout: 5,
    force_action: false,  // 强制操作选项，默认禁用
    description: ''
  }
}

// 创建页面
const createPage = async () => {
  const validate = await pageFormRef.value.validate()
  if (!validate) return

  try {
    // 构建创建页面的参数，正确处理父页面参数
    const pageData = {
      name: pageForm.name,
      description: pageForm.description,
      project: selectedProject.value
    }

    // 只有当父页面ID存在且不为空时才添加parent_group字段
    if (pageForm.parent_page) {
      pageData.parent_group = pageForm.parent_page
    }

    await createElementGroup(pageData)

    ElMessage.success(t('uiAutomation.element.messages.pageCreateSuccess'))
    showCreatePageDialog.value = false

    // 重置表单
    Object.assign(pageForm, {
      name: '',
      description: '',
      parent_page: null
    })

    // 重新加载页面和树
    await Promise.all([
      loadPages(),
      loadElementTree()
    ])

    // 强制刷新树组件
    treeKey.value += 1
  } catch (error) {
    console.error('创建页面失败:', error)
    ElMessage.error(t('uiAutomation.element.messages.pageCreateFailed'))
  }
}

// 节点点击
const onNodeClick = async (data) => {
  if (data.type === 'element') {
    try {
      const response = await getElementDetail(data.id)
      selectedElement.value = response.data

      // 强制刷新表单，确保下拉框正确显示
      formKey.value += 1
      console.log('点击节点时formKey更新为:', formKey.value)
    } catch (error) {
      console.error('获取元素详情失败:', error)
    }
  }
}

// 节点右键点击
const onNodeRightClick = (event, data) => {
  console.log('Node right click event:', event, 'Data:', data)
  event.preventDefault()

  // 隐藏现有菜单
  showContextMenu.value = false

  // 设置右键点击的节点
  rightClickedNode.value = data
  console.log('Set right clicked node:', data)

  // 设置菜单位置
  contextMenuX.value = event.clientX
  contextMenuY.value = event.clientY

  // 显示菜单
  showContextMenu.value = true
  console.log('Show context menu at:', contextMenuX.value, contextMenuY.value)

  // 添加全局点击监听器以隐藏菜单
  const hideMenu = () => {
    console.log('Hide context menu')
    showContextMenu.value = false
    document.removeEventListener('click', hideMenu)
  }

  // 延迟添加监听器，避免立即触发
  setTimeout(() => {
    document.addEventListener('click', hideMenu)
  }, 100)
}

// 节点展开
const onNodeExpand = (data) => {
  if (!expandedKeys.value.includes(data.id)) {
    expandedKeys.value.push(data.id)
  }
}

// 节点收起
const onNodeCollapse = (data) => {
  const index = expandedKeys.value.indexOf(data.id)
  if (index > -1) {
    expandedKeys.value.splice(index, 1)
  }
}

// 保存元素
const saveElement = async () => {
  if (!selectedElement.value) return

  try {
    saving.value = true
    console.log('=== 保存元素调试 ===')
    console.log('当前选中的元素:', selectedElement.value)

    if (selectedElement.value.id) {
      // 更新元素 - 构建正确的API数据格式
      const elementUpdateData = {
        name: selectedElement.value.name,
        element_type: selectedElement.value.element_type,
        page: selectedElement.value.page,
        component_name: selectedElement.value.component_name,
        description: selectedElement.value.description,
        locator_strategy_id: selectedElement.value.locator_strategy_id,
        locator_value: selectedElement.value.locator_value,
        wait_timeout: selectedElement.value.wait_timeout,
        force_action: selectedElement.value.force_action,
        project_id: selectedProject.value
      }

      // 如果元素有分组（页面），确保传递正确的 group_id
      if (selectedElement.value.page) {
        console.log('更新元素 - 元素关联页面名称:', selectedElement.value.page)

        // 通过遍历树形结构查找对应的页面ID
        const findPageIdByName = (nodes, pageName) => {
          for (const node of nodes) {
            if (node.type === 'page' && node.name === pageName) {
              return node.id
            }
            if (node.children) {
              const foundId = findPageIdByName(node.children, pageName)
              if (foundId) return foundId
            }
          }
          return null
        }

        const pageId = findPageIdByName(treeData.value, selectedElement.value.page)
        if (pageId) {
          elementUpdateData.group_id = pageId
        }
      }

      console.log('更新元素数据:', elementUpdateData)
      await updateElement(selectedElement.value.id, elementUpdateData)

      // 重新获取完整的元素详情以确保所有关联字段正确显示
      const detailResponse = await getElementDetail(selectedElement.value.id)
      selectedElement.value = detailResponse.data
      console.log('更新后获取到完整元素详情:', selectedElement.value)
      console.log('locator_strategy_id值:', selectedElement.value.locator_strategy_id, '类型:', typeof selectedElement.value.locator_strategy_id)
      console.log('locator_strategy对象:', selectedElement.value.locator_strategy)
      console.log('当前locatorStrategies:', locatorStrategies.value)
      console.log('locatorStrategies中是否包含id=' + selectedElement.value.locator_strategy_id + ':',
        locatorStrategies.value.find(s => s.id === selectedElement.value.locator_strategy_id))

      // 强制刷新表单，确保下拉框正确显示
      formKey.value += 1
      console.log('formKey更新为:', formKey.value)

      // 使用nextTick确保DOM更新
      await nextTick()
      console.log('DOM已更新，当前下拉框绑定值:', selectedElement.value.locator_strategy_id)

      ElMessage.success(t('uiAutomation.element.messages.saveSuccess'))
    } else {
      // 创建元素
      // 确保传递正确的字段名 project_id 而不是 project
      const elementData = {
        ...selectedElement.value,
        project_id: selectedProject.value
      }

      // 如果元素有分组（页面），确保传递 group_id
      if (selectedElement.value.page) {
        console.log('元素关联页面名称:', selectedElement.value.page)
        console.log('当前treeData结构:', treeData.value)

        // 通过遍历树形结构查找对应的页面ID
        const findPageIdByName = (nodes, pageName) => {
          console.log(`在 ${nodes.length} 个节点中查找页面名称: ${pageName}`)
          for (const node of nodes) {
            console.log(`检查节点: ${node.name} (ID: ${node.id}, type: ${node.type})`)
            if (node.type === 'page' && node.name === pageName) {
              console.log(`找到页面! ID: ${node.id}`)
              return node.id
            }
            if (node.children) {
              console.log(`检查子节点:`, node.children.map(c => c.name))
              const foundId = findPageIdByName(node.children, pageName)
              if (foundId) return foundId
            }
          }
          console.log('未找到页面')
          return null
        }

        const pageId = findPageIdByName(treeData.value, selectedElement.value.page)
        console.log('找到的页面ID:', pageId)

        if (pageId) {
          elementData.group_id = pageId
          console.log('设置group_id为:', pageId)
        }
      }

      console.log('创建元素的数据:', elementData)
      const response = await createElement(elementData)
      console.log('创建响应:', response)

      // 重新获取完整的元素详情以确保所有关联字段正确显示
      const detailResponse = await getElementDetail(response.data.id)
      selectedElement.value = detailResponse.data
      console.log('获取到完整元素详情:', selectedElement.value)
      console.log('locator_strategy_id值:', selectedElement.value.locator_strategy_id, '类型:', typeof selectedElement.value.locator_strategy_id)
      console.log('locator_strategy对象:', selectedElement.value.locator_strategy)
      console.log('当前locatorStrategies:', locatorStrategies.value)
      console.log('locatorStrategies中是否包含id=' + selectedElement.value.locator_strategy_id + ':',
        locatorStrategies.value.find(s => s.id === selectedElement.value.locator_strategy_id))
      console.log('el-select绑定的值:', selectedElement.value.locator_strategy_id)

      // 强制刷新表单，确保下拉框正确显示
      formKey.value += 1
      console.log('formKey更新为:', formKey.value)

      // 使用nextTick确保DOM更新
      await nextTick()
      console.log('DOM已更新，当前下拉框绑定值:', selectedElement.value.locator_strategy_id)

      ElMessage.success(t('uiAutomation.element.messages.createSuccess'))
    }

    // 重新加载树
    console.log('开始重新加载元素树...')
    await loadElementTree()
    console.log('元素树重新加载完成')

    // 强制重新渲染树组件
    treeKey.value += 1
    console.log('树组件key更新为:', treeKey.value)

    // 强制触发Vue更新和树组件刷新
    nextTick(() => {
      console.log('nextTick - 检查treeData:', treeData.value)
      console.log('treeRef:', treeRef.value)

      // 展开新创建元素所在的页面节点
      if (selectedElement.value && selectedElement.value.group_id) {
        console.log('展开元素所在页面:', selectedElement.value.group_id)
        if (!expandedKeys.value.includes(selectedElement.value.group_id)) {
          expandedKeys.value.push(selectedElement.value.group_id)
        }
      }

      console.log('树数据更新完成，当前expandedKeys:', expandedKeys.value)
    })
  } catch (error) {
    console.error('保存元素失败:', error)
    ElMessage.error(t('uiAutomation.element.messages.saveFailed') + ': ' + (error.response?.data?.message || error.message || t('uiAutomation.messages.error.unknown')))
  } finally {
    saving.value = false
  }
}

// 验证元素
const validateElement = async () => {
  if (!selectedElement.value) return

  try {
    validating.value = true
    const response = await validateElementLocator(selectedElement.value.id)
    const result = response.data

    if (result.is_valid) {
      ElMessage.success(t('uiAutomation.element.messages.validateSuccess'))
    } else {
      ElMessage.error(`${t('uiAutomation.element.messages.validateFailed')}: ${result.validation_message}`)
    }
  } catch (error) {
    ElMessage.error(t('uiAutomation.element.messages.validateFailed'))
    console.error('验证元素失败:', error)
  } finally {
    validating.value = false
  }
}

// 生成建议
const generateSuggestions = async () => {
  if (!selectedElement.value) return

  try {
    generating.value = true
    const response = await generateElementSuggestions(selectedElement.value.id)
    suggestions.value = response.data.suggestions
  } catch (error) {
    console.error('生成建议失败:', error)
  } finally {
    generating.value = false
  }
}

// 保存页面名称
const savePageName = () => {
  // TODO: 实现页面名称保存
  editingNodeId.value = null
}

// 取消编辑
const cancelEdit = () => {
  editingNodeId.value = null
}

// 右键菜单操作函数
// 新增元素
const addContextElement = () => {
  console.log('Add context element clicked')
  showContextMenu.value = false
  createEmptyElement()

  // 如果右键点击的是页面节点，设置元素的页面
  if (rightClickedNode.value && rightClickedNode.value.type === 'page') {
    if (selectedElement.value) {
      selectedElement.value.page = rightClickedNode.value.name
      // 同时设置group_id，确保元素能正确关联到页面
      selectedElement.value.group_id = rightClickedNode.value.id
    }
  }
}

// 新增子页面
const addSubPage = () => {
  console.log('Add sub page clicked')
  showContextMenu.value = false
  showCreatePageDialog.value = true

  // 如果右键点击的是页面节点，设置父页面
  if (rightClickedNode.value && rightClickedNode.value.type === 'page') {
    pageForm.parent_page = rightClickedNode.value.id
  }
}

// 编辑节点
const editNode = async () => {
  console.log('Edit node clicked, rightClickedNode:', rightClickedNode.value)
  showContextMenu.value = false

  if (!rightClickedNode.value) {
    console.log('No right clicked node')
    return
  }

  console.log('Editing node:', rightClickedNode.value)
  console.log('Node type:', rightClickedNode.value.type)

  if (rightClickedNode.value.type === 'page') {
    // 编辑页面
    console.log('Editing page node')
    editPageForm.id = rightClickedNode.value.id
    editPageForm.name = rightClickedNode.value.name
    editPageForm.description = rightClickedNode.value.description || ''
    editPageForm.parent_page = rightClickedNode.value.parent_group || null
    console.log('Set edit page form data:', editPageForm)
    console.log('Setting showEditPageDialog to true')
    showEditPageDialog.value = true
    console.log('showEditPageDialog value:', showEditPageDialog.value)
  } else if (rightClickedNode.value.type === 'element') {
    console.log('Editing element node')
    // 编辑元素 - 通过API获取完整的元素详情，避免使用树节点的复杂数据
    try {
      const response = await getElementDetail(rightClickedNode.value.id)
      selectedElement.value = response.data
      console.log('Set selected element for editing via API:', selectedElement.value)

      // 强制刷新表单，确保下拉框正确显示
      formKey.value += 1
      console.log('编辑时formKey更新为:', formKey.value)
    } catch (error) {
      console.error('获取元素详情失败:', error)
      ElMessage.error(t('uiAutomation.element.messages.getDetailFailed'))
    }
  } else {
    console.log('Unknown node type:', rightClickedNode.value.type)
  }
}

// 删除节点
const deleteNode = async () => {
  console.log('Delete node clicked, rightClickedNode:', rightClickedNode.value)
  showContextMenu.value = false

  if (!rightClickedNode.value) return

  try {
    await ElMessageBox.confirm(
      t('uiAutomation.element.messages.confirmDeleteNode', { name: rightClickedNode.value.name }),
      t('uiAutomation.common.confirmDelete'),
      {
        type: 'warning',
        confirmButtonText: t('uiAutomation.common.confirm'),
        cancelButtonText: t('uiAutomation.common.cancel')
      }
    )

    console.log('Deleting node:', rightClickedNode.value)

    if (rightClickedNode.value.type === 'page') {
      // 删除页面（分组）
      console.log('Calling deleteElementGroup with id:', rightClickedNode.value.id)
      await deleteElementGroup(rightClickedNode.value.id)
      ElMessage.success(t('uiAutomation.element.messages.pageDeleteSuccess'))
    } else if (rightClickedNode.value.type === 'element') {
      // 删除元素
      console.log('Calling deleteElement with id:', rightClickedNode.value.id)
      await deleteElement(rightClickedNode.value.id)
      ElMessage.success(t('uiAutomation.element.messages.deleteSuccess'))
      // 如果当前选中的是被删除的元素，清空选中
      if (selectedElement.value && selectedElement.value.id === rightClickedNode.value.id) {
        selectedElement.value = null
      }
    }

    console.log('Reload data after deletion')

    // 重新加载数据
    await Promise.all([
      loadPages(),
      loadElementTree()
    ])

    // 强制刷新树组件
    treeKey.value += 1
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(t('uiAutomation.element.messages.deleteFailed'))
    }
  }
}

// 更新页面
const updatePage = async () => {
  console.log('Update page function called')
  console.log('Edit page form ref:', editPageFormRef.value)

  if (!editPageFormRef.value) {
    console.log('No edit page form ref')
    return
  }

  const validate = await editPageFormRef.value.validate()
  console.log('Validation result:', validate)
  if (!validate) {
    console.log('Validation failed')
    return
  }

  console.log('Updating page with data:', editPageForm)

  try {
    // 构建更新页面的参数，正确处理父页面参数
    const pageData = {
      name: editPageForm.name,
      description: editPageForm.description,
      project: selectedProject.value
    }

    // 只有当父页面ID存在且不为空时才添加parent_group字段
    // 如果父页面ID为null，表示取消父页面关联
    if (editPageForm.parent_page !== undefined) {
      pageData.parent_group = editPageForm.parent_page
    }

    await updateElementGroup(editPageForm.id, pageData)

    ElMessage.success(t('uiAutomation.element.messages.pageUpdateSuccess'))
    showEditPageDialog.value = false

    // 重新加载页面和树
    await Promise.all([
      loadPages(),
      loadElementTree()
    ])

    // 强制刷新树组件
    treeKey.value += 1
  } catch (error) {
    console.error('更新页面失败:', error)
    ElMessage.error(t('uiAutomation.element.messages.pageUpdateFailed'))
  }
}
</script>

<style scoped>
.element-manager {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.element-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 300px;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.sidebar-header {
  padding: 15px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-actions {
  display: flex;
  gap: 5px;
  margin-left: auto;
}

.page-tree {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 0;
}

.node-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.element-type-tag {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  background-color: #ecf5ff;
  color: #409eff;
}

.main-content {
  flex: 1;
  overflow: auto;
  padding: 20px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.element-header {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.element-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.element-form {
  margin-top: 20px;
}

.form-help-text {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

/* 右键菜单样式 */
.context-menu {
  position: fixed;
  z-index: 9999;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 5px 0;
  margin: 0;
  list-style: none;
  min-width: 120px;
}

.context-menu li {
  padding: 8px 15px;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
}

.context-menu li:hover {
  background-color: #f5f7fa;
  color: #409eff;
}
</style>