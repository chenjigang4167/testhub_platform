<template>
  <div class="page-object-manager">
    <div class="page-header">
      <h1 class="page-title">{{ $t('uiAutomation.pageObject.title') }}</h1>
      <div class="header-actions">
        <el-select v-model="projectId" :placeholder="$t('uiAutomation.common.selectProject')" style="width: 200px; margin-right: 15px" @change="onProjectChange">
          <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
        </el-select>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          {{ $t('uiAutomation.pageObject.newPageObject') }}
        </el-button>
      </div>
    </div>

    <div class="main-content">
      <!-- 页面对象列表 -->
      <div class="left-panel">
        <div class="panel-header">
          <h3>{{ $t('uiAutomation.pageObject.pageObjectList') }}</h3>
          <el-input
            v-model="searchText"
            :placeholder="$t('uiAutomation.pageObject.searchPlaceholder')"
            clearable
            size="small"
            style="width: 200px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <div class="page-object-list">
          <div
            v-for="pageObject in filteredPageObjects"
            :key="pageObject.id"
            class="page-object-item"
            :class="{ active: selectedPageObject?.id === pageObject.id }"
            @click="selectPageObject(pageObject)"
          >
            <div class="item-header">
              <h4>{{ pageObject.name }}</h4>
              <div class="item-actions">
                <el-button size="small" text @click.stop="editPageObject(pageObject)">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button size="small" text type="danger" @click.stop="deletePageObject(pageObject.id)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
            <div class="item-meta">
              <span class="class-name">{{ pageObject.class_name }}</span>
              <el-tag size="small" type="info">{{ pageObject.elements_count || 0 }} {{ $t('uiAutomation.pageObject.elementsCount') }}</el-tag>
            </div>
            <div class="item-description" v-if="pageObject.description">
              {{ pageObject.description }}
            </div>
          </div>
        </div>
      </div>

      <!-- 页面对象详情和设计器 -->
      <div class="right-panel">
        <div v-if="selectedPageObject" class="page-object-detail">
          <div class="detail-header">
            <h3>{{ selectedPageObject.name }}</h3>
            <div class="header-actions">
              <el-button size="small" @click="showAddElementDialog = true">
                <el-icon><Plus /></el-icon>
                {{ $t('uiAutomation.pageObject.addElement') }}
              </el-button>
              <el-button size="small" type="success" @click="generateCode">
                <el-icon><Document /></el-icon>
                {{ $t('uiAutomation.pageObject.generateCode') }}
              </el-button>
            </div>
          </div>

          <el-tabs v-model="activeTab" type="border-card">
            <!-- 元素设计 -->
            <el-tab-pane :label="$t('uiAutomation.pageObject.elementsDesign')" name="design">
              <div class="design-area">
                <div class="element-library">
                  <h4>{{ $t('uiAutomation.pageObject.availableElements') }}</h4>
                  <el-input
                    v-model="elementFilter"
                    :placeholder="$t('uiAutomation.pageObject.searchElements')"
                    clearable
                    size="small"
                    style="margin-bottom: 10px"
                  >
                    <template #prefix>
                      <el-icon><Search /></el-icon>
                    </template>
                  </el-input>

                  <div class="element-list">
                    <div
                      v-for="element in filteredElements"
                      :key="element.id"
                      class="element-item"
                      draggable
                      @dragstart="handleDragStart($event, element)"
                    >
                      <el-icon class="element-icon">
                        <component :is="getElementIcon(element.element_type)" />
                      </el-icon>
                      <span class="element-name">{{ element.name }}</span>
                      <el-tag size="small" :type="getElementTypeTag(element.element_type)">
                        {{ getElementTypeText(element.element_type) }}
                      </el-tag>
                    </div>
                  </div>
                </div>

                <div class="design-canvas">
                  <h4>{{ $t('uiAutomation.pageObject.pageObjectElements') }}</h4>
                  <div
                    class="canvas-drop-zone"
                    @drop="handleDrop"
                    @dragover.prevent
                    @dragenter.prevent
                  >
                    <div v-if="pageObjectElements.length === 0" class="empty-canvas">
                      <el-empty :description="$t('uiAutomation.pageObject.dragElementHint')" />
                    </div>
                    <div v-else class="element-canvas">
                      <div
                        v-for="(poElement, index) in pageObjectElements"
                        :key="poElement.id"
                        class="canvas-element"
                        @click="selectCanvasElement(poElement)"
                      >
                        <div class="element-header">
                          <el-icon>
                            <component :is="getElementIcon(poElement.element.element_type)" />
                          </el-icon>
                          <span class="method-name">{{ poElement.method_name }}</span>
                          <div class="element-actions">
                            <el-button size="small" text @click="editCanvasElement(poElement)">
                              <el-icon><Edit /></el-icon>
                            </el-button>
                            <el-button size="small" text type="danger" @click="removeCanvasElement(poElement.id)">
                              <el-icon><Delete /></el-icon>
                            </el-button>
                          </div>
                        </div>
                        <div class="element-meta">
                          <span class="element-name">{{ poElement.element.name }}</span>
                          <el-tag size="small" :type="poElement.is_property ? 'success' : 'primary'">
                            {{ poElement.is_property ? $t('uiAutomation.pageObject.property') : $t('uiAutomation.pageObject.method') }}
                          </el-tag>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <!-- 代码预览 -->
            <el-tab-pane :label="$t('uiAutomation.pageObject.codePreview')" name="code">
              <div class="code-preview">
                <div class="code-controls">
                  <el-select v-model="codeLanguage" size="small" style="width: 120px">
                    <el-option label="JavaScript" value="javascript" />
                    <el-option label="Python" value="python" />
                  </el-select>
                  <el-button size="small" type="primary" @click="generateCode">
                    {{ $t('uiAutomation.pageObject.refreshCode') }}
                  </el-button>
                  <el-button size="small" @click="copyCode">
                    {{ $t('uiAutomation.pageObject.copyCode') }}
                  </el-button>
                </div>
                <div class="code-display">
                  <el-input
                    v-model="generatedCode"
                    type="textarea"
                    :rows="20"
                    readonly
                    class="code-textarea"
                  />
                </div>
              </div>
            </el-tab-pane>

            <!-- 属性配置 -->
            <el-tab-pane :label="$t('uiAutomation.pageObject.propertiesConfig')" name="properties">
              <div class="properties-panel" v-if="selectedCanvasElement">
                <h4>{{ $t('uiAutomation.pageObject.elementPropertiesConfig') }}</h4>
                <el-form :model="selectedCanvasElement" label-width="100px">
                  <el-form-item :label="$t('uiAutomation.pageObject.methodName')">
                    <el-input v-model="selectedCanvasElement.method_name" @change="updateCanvasElement" />
                  </el-form-item>
                  <el-form-item :label="$t('uiAutomation.pageObject.type')">
                    <el-radio-group v-model="selectedCanvasElement.is_property" @change="updateCanvasElement">
                      <el-radio :label="true">{{ $t('uiAutomation.pageObject.property') }}</el-radio>
                      <el-radio :label="false">{{ $t('uiAutomation.pageObject.method') }}</el-radio>
                    </el-radio-group>
                  </el-form-item>
                  <el-form-item :label="$t('uiAutomation.pageObject.order')">
                    <el-input-number v-model="selectedCanvasElement.order" @change="updateCanvasElement" />
                  </el-form-item>
                </el-form>

                <h4>{{ $t('uiAutomation.pageObject.elementInfo') }}</h4>
                <el-descriptions :column="1" border>
                  <el-descriptions-item :label="$t('uiAutomation.pageObject.elementName')">
                    {{ selectedCanvasElement.element.name }}
                  </el-descriptions-item>
                  <el-descriptions-item :label="$t('uiAutomation.pageObject.elementType')">
                    {{ getElementTypeText(selectedCanvasElement.element.element_type) }}
                  </el-descriptions-item>
                  <el-descriptions-item :label="$t('uiAutomation.pageObject.locator')">
                    {{ selectedCanvasElement.element.locator_value }}
                  </el-descriptions-item>
                </el-descriptions>
              </div>
              <div v-else class="no-selection">
                <el-empty :description="$t('uiAutomation.pageObject.selectElementToConfig')" />
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>

        <div v-else class="no-page-object">
          <el-empty :description="$t('uiAutomation.pageObject.selectPageObjectToEdit')" />
        </div>
      </div>
    </div>

    <!-- 新增页面对象对话框 -->
    <el-dialog v-model="showCreateDialog" :title="$t('uiAutomation.pageObject.createPageObject')" width="600px">
      <el-form ref="createFormRef" :model="createForm" :rules="formRules" label-width="120px">
        <el-form-item :label="$t('uiAutomation.pageObject.pageObjectName')" prop="name">
          <el-input v-model="createForm.name" :placeholder="$t('uiAutomation.pageObject.rules.nameRequired')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.pageObject.className')" prop="class_name">
          <el-input v-model="createForm.class_name" :placeholder="$t('uiAutomation.pageObject.rules.classNameRequired')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.pageObject.urlPattern')">
          <el-input v-model="createForm.url_pattern" :placeholder="$t('uiAutomation.pageObject.urlPatternPlaceholder')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.common.description')">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :placeholder="$t('uiAutomation.common.description')"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">{{ $t('uiAutomation.common.cancel') }}</el-button>
          <el-button type="primary" @click="handleCreate">{{ $t('uiAutomation.common.confirm') }}</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 添加元素对话框 -->
    <el-dialog v-model="showAddElementDialog" :title="$t('uiAutomation.pageObject.addElementToPageObject')" width="600px">
      <el-form ref="addElementFormRef" :model="addElementForm" :rules="addElementRules" label-width="120px">
        <el-form-item :label="$t('uiAutomation.pageObject.selectElement')" prop="element_id">
          <el-select v-model="addElementForm.element_id" :placeholder="$t('uiAutomation.pageObject.selectElement')" filterable>
            <el-option
              v-for="element in availableElements"
              :key="element.id"
              :label="`${element.name} (${element.page || $t('uiAutomation.pageObject.uncategorized')})`"
              :value="element.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.pageObject.methodName')" prop="method_name">
          <el-input v-model="addElementForm.method_name" :placeholder="$t('uiAutomation.pageObject.rules.methodNameRequired')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.pageObject.type')">
          <el-radio-group v-model="addElementForm.is_property">
            <el-radio :label="true">{{ $t('uiAutomation.pageObject.property') }}</el-radio>
            <el-radio :label="false">{{ $t('uiAutomation.pageObject.method') }}</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.pageObject.order')">
          <el-input-number v-model="addElementForm.order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddElementDialog = false">{{ $t('uiAutomation.common.cancel') }}</el-button>
          <el-button type="primary" @click="handleAddElement">{{ $t('uiAutomation.common.confirm') }}</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, Edit, Delete, Document,
  Operation, Folder, Warning
} from '@element-plus/icons-vue'

import {
  getUiProjects,
  getPageObjects,
  createPageObject,
  updatePageObject,
  deletePageObject as deletePageObjectAPI,
  generatePageObjectCode,
  getPageObjectElements,
  createPageObjectElement,
  updatePageObjectElement,
  deletePageObjectElement,
  getElements
} from '@/api/ui_automation'

const { t } = useI18n()

// 响应式数据
const projects = ref([])
const projectId = ref('')
const pageObjects = ref([])
const selectedPageObject = ref(null)
const selectedCanvasElement = ref(null)
const pageObjectElements = ref([])
const availableElements = ref([])
const searchText = ref('')
const elementFilter = ref('')
const generatedCode = ref('')
const codeLanguage = ref('javascript')
const activeTab = ref('design')

// 对话框控制
const showCreateDialog = ref(false)
const showAddElementDialog = ref(false)

// 表单数据
const createForm = reactive({
  project: '',
  name: '',
  class_name: '',
  url_pattern: '',
  description: ''
})

const addElementForm = reactive({
  element_id: '',
  method_name: '',
  is_property: true,
  order: 0
})

// 表单引用
const createFormRef = ref(null)
const addElementFormRef = ref(null)

// 表单验证规则 - 使用computed使其响应式
const formRules = computed(() => ({
  name: [
    { required: true, message: t('uiAutomation.pageObject.rules.nameRequired'), trigger: 'blur' }
  ],
  class_name: [
    { required: true, message: t('uiAutomation.pageObject.rules.classNameRequired'), trigger: 'blur' },
    { pattern: /^[A-Z][a-zA-Z0-9]*$/, message: t('uiAutomation.pageObject.rules.classNamePattern'), trigger: 'blur' }
  ]
}))

const addElementRules = computed(() => ({
  element_id: [
    { required: true, message: t('uiAutomation.pageObject.rules.elementRequired'), trigger: 'change' }
  ],
  method_name: [
    { required: true, message: t('uiAutomation.pageObject.rules.methodNameRequired'), trigger: 'blur' },
    { pattern: /^[a-zA-Z_][a-zA-Z0-9_]*$/, message: t('uiAutomation.pageObject.rules.methodNamePattern'), trigger: 'blur' }
  ]
}))

// 计算属性
const filteredPageObjects = computed(() => {
  if (!searchText.value) return pageObjects.value
  return pageObjects.value.filter(po =>
    po.name.includes(searchText.value) ||
    po.class_name.includes(searchText.value) ||
    (po.description && po.description.includes(searchText.value))
  )
})

const filteredElements = computed(() => {
  if (!elementFilter.value) return availableElements.value
  return availableElements.value.filter(element =>
    element.name.includes(elementFilter.value) ||
    (element.page && element.page.includes(elementFilter.value))
  )
})

// 方法定义
const loadProjects = async () => {
  try {
    const response = await getUiProjects({ page_size: 100 })
    projects.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error(t('uiAutomation.pageObject.messages.loadProjectsFailed'))
    console.error('获取项目列表失败:', error)
  }
}

const loadPageObjects = async () => {
  if (!projectId.value) {
    pageObjects.value = []
    return
  }

  try {
    const response = await getPageObjects({ project: projectId.value })
    pageObjects.value = response.data.results || response.data
  } catch (error) {
    console.error('获取页面对象列表失败:', error)
  }
}

const loadAvailableElements = async () => {
  if (!projectId.value) {
    availableElements.value = []
    return
  }

  try {
    const response = await getElements({ project: projectId.value })
    availableElements.value = response.data.results || response.data
  } catch (error) {
    console.error('获取可用元素失败:', error)
  }
}

const onProjectChange = () => {
  selectedPageObject.value = null
  selectedCanvasElement.value = null
  pageObjectElements.value = []

  createForm.project = projectId.value

  loadPageObjects()
  loadAvailableElements()
}

const selectPageObject = async (pageObject) => {
  selectedPageObject.value = pageObject
  selectedCanvasElement.value = null

  try {
    const response = await getPageObjectElements(pageObject.id)
    pageObjectElements.value = response.data
  } catch (error) {
    console.error('获取页面对象元素失败:', error)
    pageObjectElements.value = []
  }
}

const selectCanvasElement = (poElement) => {
  selectedCanvasElement.value = poElement
}

const handleDragStart = (event, element) => {
  event.dataTransfer.setData('element', JSON.stringify(element))
}

const handleDrop = (event) => {
  event.preventDefault()
  if (!selectedPageObject.value) {
    ElMessage.warning(t('uiAutomation.pageObject.messages.selectPageObjectFirst'))
    return
  }

  const elementData = JSON.parse(event.dataTransfer.getData('element'))

  // 检查元素是否已经存在
  const exists = pageObjectElements.value.some(pe => pe.element.id === elementData.id)
  if (exists) {
    ElMessage.warning(t('uiAutomation.pageObject.messages.elementAlreadyExists'))
    return
  }

  // 自动生成方法名称
  const methodName = elementData.name.replace(/[\s\-]/g, '')
    .replace(/^./, elementData.name.charAt(0).toLowerCase())

  // 添加元素到页面对象
  addElementToPageObjectFn({
    element_id: elementData.id,
    method_name: methodName,
    is_property: true,
    order: pageObjectElements.value.length
  })
}

const addElementToPageObjectFn = async (elementData) => {
  try {
    const response = await createPageObjectElement({
      page_object_id: selectedPageObject.value.id,
      ...elementData
    })

    // 重新加载页面对象元素
    await selectPageObject(selectedPageObject.value)
    ElMessage.success(t('uiAutomation.pageObject.messages.addElementSuccess'))
  } catch (error) {
    console.error('添加元素失败:', error)
    ElMessage.error(t('uiAutomation.pageObject.messages.addElementFailed'))
  }
}

const editCanvasElement = (poElement) => {
  selectedCanvasElement.value = poElement
  activeTab.value = 'properties'
}

const updateCanvasElement = async () => {
  if (!selectedCanvasElement.value) return

  try {
    await updatePageObjectElement(selectedCanvasElement.value.id, {
      method_name: selectedCanvasElement.value.method_name,
      is_property: selectedCanvasElement.value.is_property,
      order: selectedCanvasElement.value.order
    })

    ElMessage.success(t('uiAutomation.pageObject.messages.updateConfigSuccess'))
  } catch (error) {
    console.error('更新元素配置失败:', error)
    ElMessage.error(t('uiAutomation.pageObject.messages.updateConfigFailed'))
  }
}

const removeCanvasElement = async (elementId) => {
  try {
    await ElMessageBox.confirm(
      t('uiAutomation.pageObject.messages.removeElementConfirm'),
      t('uiAutomation.pageObject.messages.confirmRemove'),
      {
        confirmButtonText: t('uiAutomation.common.confirm'),
        cancelButtonText: t('uiAutomation.common.cancel'),
        type: 'warning'
      }
    )

    await deletePageObjectElement(elementId)

    // 重新加载页面对象元素
    await selectPageObject(selectedPageObject.value)

    // 如果删除的是当前选中的元素，清空选择
    if (selectedCanvasElement.value?.id === elementId) {
      selectedCanvasElement.value = null
    }

    ElMessage.success(t('uiAutomation.pageObject.messages.removeElementSuccess'))
  } catch (error) {
    if (error === 'cancel') return
    console.error('移除元素失败:', error)
    ElMessage.error(t('uiAutomation.pageObject.messages.removeElementFailed'))
  }
}

const generateCode = async () => {
  if (!selectedPageObject.value) {
    ElMessage.warning(t('uiAutomation.pageObject.messages.selectPageObjectFirst'))
    return
  }

  try {
    const response = await generatePageObjectCode(selectedPageObject.value.id, {
      language: codeLanguage.value,
      framework: 'playwright',
      include_comments: true
    })

    generatedCode.value = response.data.code
    activeTab.value = 'code'
    ElMessage.success(t('uiAutomation.pageObject.messages.generateCodeSuccess'))
  } catch (error) {
    console.error('生成代码失败:', error)
    ElMessage.error(t('uiAutomation.pageObject.messages.generateCodeFailed'))
  }
}

const copyCode = () => {
  if (!generatedCode.value) {
    ElMessage.warning(t('uiAutomation.pageObject.messages.noCodeToCopy'))
    return
  }

  navigator.clipboard.writeText(generatedCode.value).then(() => {
    ElMessage.success(t('uiAutomation.pageObject.messages.codeCopied'))
  }).catch(() => {
    ElMessage.error(t('uiAutomation.pageObject.messages.copyFailed'))
  })
}

const editPageObject = (pageObject) => {
  // TODO: 实现页面对象编辑功能
  ElMessage.info(t('uiAutomation.pageObject.messages.editFeatureComingSoon'))
}

const deletePageObject = async (id) => {
  try {
    await ElMessageBox.confirm(
      t('uiAutomation.pageObject.messages.deletePageObjectConfirm'),
      t('uiAutomation.pageObject.messages.confirmDelete'),
      {
        confirmButtonText: t('uiAutomation.common.confirm'),
        cancelButtonText: t('uiAutomation.common.cancel'),
        type: 'warning'
      }
    )

    await deletePageObjectAPI(id)

    // 如果删除的是当前选中的页面对象，清空选择
    if (selectedPageObject.value?.id === id) {
      selectedPageObject.value = null
      selectedCanvasElement.value = null
      pageObjectElements.value = []
    }

    await loadPageObjects()
    ElMessage.success(t('uiAutomation.pageObject.messages.deletePageObjectSuccess'))
  } catch (error) {
    if (error === 'cancel') return
    console.error('删除页面对象失败:', error)
    ElMessage.error(t('uiAutomation.pageObject.messages.deletePageObjectFailed'))
  }
}

const handleCreate = async () => {
  const validate = await createFormRef.value.validate()
  if (!validate) return

  try {
    await createPageObject(createForm)
    ElMessage.success(t('uiAutomation.pageObject.messages.createPageObjectSuccess'))
    showCreateDialog.value = false

    // 重置表单
    Object.assign(createForm, {
      name: '',
      class_name: '',
      url_pattern: '',
      description: ''
    })

    await loadPageObjects()
  } catch (error) {
    console.error('创建页面对象失败:', error)
    ElMessage.error(t('uiAutomation.pageObject.messages.createPageObjectFailed'))
  }
}

const handleAddElement = async () => {
  const validate = await addElementFormRef.value.validate()
  if (!validate) return

  try {
    await createPageObjectElement({
      page_object_id: selectedPageObject.value.id,
      ...addElementForm
    })

    ElMessage.success(t('uiAutomation.pageObject.messages.addElementSuccess'))
    showAddElementDialog.value = false

    // 重置表单
    Object.assign(addElementForm, {
      element_id: '',
      method_name: '',
      is_property: true,
      order: 0
    })

    // 重新加载页面对象元素
    await selectPageObject(selectedPageObject.value)
  } catch (error) {
    console.error('添加元素失败:', error)
    ElMessage.error(t('uiAutomation.pageObject.messages.addElementFailed'))
  }
}

// 辅助方法
const getElementIcon = (elementType) => {
  switch (elementType) {
    case 'BUTTON': return Operation
    case 'INPUT': return Edit
    case 'DROPDOWN': return Folder
    default: return Operation
  }
}

const getElementTypeTag = (type) => {
  const typeMap = {
    'BUTTON': 'primary',
    'INPUT': 'success',
    'LINK': 'info',
    'DROPDOWN': 'warning'
  }
  return typeMap[type] || 'default'
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

// 组件挂载
onMounted(async () => {
  await loadProjects()

  if (projects.value.length > 0) {
    projectId.value = projects.value[0].id
    await onProjectChange()
  }
})
</script>

<style scoped>
.page-object-manager {
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
  width: 350px;
  border-right: 1px solid #e6e6e6;
  display: flex;
  flex-direction: column;
}

.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #e6e6e6;
  background-color: #fafafa;
}

.page-object-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.page-object-item {
  border: 1px solid #e6e6e6;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s;
}

.page-object-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.page-object-item.active {
  border-color: #409eff;
  background-color: #f0f8ff;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.item-header h4 {
  margin: 0;
  font-size: 16px;
}

.item-actions {
  display: flex;
  gap: 5px;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.class-name {
  font-family: monospace;
  background-color: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
}

.item-description {
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}

.page-object-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #e6e6e6;
  background-color: #fafafa;
}

.design-area {
  display: flex;
  height: 100%;
}

.element-library {
  width: 250px;
  border-right: 1px solid #e6e6e6;
  padding: 15px;
  overflow-y: auto;
}

.element-library h4 {
  margin: 0 0 15px 0;
}

.element-list {
  max-height: 400px;
  overflow-y: auto;
}

.element-item {
  display: flex;
  align-items: center;
  padding: 8px;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  margin-bottom: 8px;
  cursor: grab;
  transition: all 0.3s;
}

.element-item:hover {
  border-color: #409eff;
  background-color: #f0f8ff;
}

.element-item:active {
  cursor: grabbing;
}

.element-icon {
  margin-right: 8px;
  font-size: 16px;
}

.element-name {
  flex: 1;
  margin-right: 8px;
  font-size: 14px;
}

.design-canvas {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
}

.design-canvas h4 {
  margin: 0 0 15px 0;
}

.canvas-drop-zone {
  min-height: 300px;
  border: 2px dashed #ccc;
  border-radius: 6px;
  padding: 20px;
}

.empty-canvas {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.element-canvas {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.canvas-element {
  border: 1px solid #e6e6e6;
  border-radius: 6px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.canvas-element:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.element-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.method-name {
  flex: 1;
  margin-left: 8px;
  font-weight: bold;
}

.element-actions {
  display: flex;
  gap: 5px;
}

.element-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #666;
}

.code-preview {
  padding: 20px;
}

.code-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.code-display {
  height: 500px;
}

.code-textarea {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
}

.properties-panel {
  padding: 20px;
}

.properties-panel h4 {
  margin: 0 0 15px 0;
  color: #333;
}

.no-page-object,
.no-selection {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
