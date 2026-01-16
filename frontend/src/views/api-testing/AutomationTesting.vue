<template>
  <div class="automation-testing">
    <div class="header">
      <h3>{{ $t('apiTesting.automation.title') }}</h3>
      <el-button type="primary" @click="showCreateSuiteDialog = true">
        <el-icon><Plus /></el-icon>
        {{ $t('apiTesting.automation.createSuite') }}
      </el-button>
    </div>

    <div class="content-layout">
      <!-- 左侧项目选择和测试套件列表 -->
      <div class="sidebar">
        <div class="project-selector">
          <el-select
            v-model="selectedProject"
            :placeholder="$t('apiTesting.common.selectProject')"
            @change="onProjectChange"
            style="width: 100%;"
          >
            <el-option
              v-for="project in httpProjects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </div>
        
        <div class="suite-list">
          <div class="list-header">
            <span>{{ $t('apiTesting.automation.testSuites') }}</span>
            <el-button size="small" text @click="loadTestSuites">
              <el-icon><Refresh /></el-icon>
            </el-button>
          </div>
          
          <el-scrollbar height="400px">
            <div
              v-for="suite in testSuites"
              :key="suite.id"
              class="suite-item"
              :class="{ active: selectedSuite?.id === suite.id }"
              @click="selectSuite(suite)"
            >
              <div class="suite-info">
                <div class="suite-name">{{ suite.name }}</div>
                <div class="suite-meta">
                  {{ $t('apiTesting.automation.requestCount', { n: suite.suite_requests?.length || 0 }) }}
                </div>
              </div>
              <el-dropdown @command="handleSuiteAction" trigger="click">
                <el-button size="small" text>
                  <el-icon><MoreFilled /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item :command="{ action: 'run', suite }">{{ $t('apiTesting.automation.run') }}</el-dropdown-item>
                    <el-dropdown-item :command="{ action: 'edit', suite }">{{ $t('apiTesting.common.edit') }}</el-dropdown-item>
                    <el-dropdown-item :command="{ action: 'duplicate', suite }">{{ $t('apiTesting.common.copy') }}</el-dropdown-item>
                    <el-dropdown-item :command="{ action: 'delete', suite }" divided>{{ $t('apiTesting.common.delete') }}</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </el-scrollbar>
        </div>
      </div>

      <!-- 右侧测试套件详情 -->
      <div class="main-content">
        <div v-if="!selectedSuite" class="empty-state">
          <el-empty :description="$t('apiTesting.automation.selectSuiteHint')" />
        </div>
        
        <div v-else class="suite-detail">
          <!-- 套件信息 -->
          <div class="suite-header">
            <div class="suite-title">
              <h4>{{ selectedSuite.name }}</h4>
              <div class="suite-actions">
                <el-button type="success" @click="runTestSuite(selectedSuite)" :loading="running">
                  <el-icon><VideoPlay /></el-icon>
                  {{ $t('apiTesting.automation.runTest') }}
                </el-button>
                <el-button @click="editSuite(selectedSuite)">
                  <el-icon><Edit /></el-icon>
                  {{ $t('apiTesting.common.edit') }}
                </el-button>
              </div>
            </div>
            <div class="suite-description">
              {{ selectedSuite.description || $t('apiTesting.automation.noDescription') }}
            </div>
            <div class="suite-meta">
              <el-tag size="small">{{ getEnvironmentName(selectedSuite.environment) }}</el-tag>
              <span class="meta-text">{{ $t('apiTesting.automation.creator') }}{{ selectedSuite.created_by?.username }}</span>
              <span class="meta-text">{{ $t('apiTesting.automation.createTime') }}{{ formatDate(selectedSuite.created_at) }}</span>
            </div>
          </div>

          <!-- 请求列表 -->
          <div class="requests-section">
            <div class="section-header">
              <h5>{{ $t('apiTesting.automation.testRequests') }}</h5>
              <el-button size="small" @click="showAddRequest">
                <el-icon><Plus /></el-icon>
                {{ $t('apiTesting.automation.addRequest') }}
              </el-button>
            </div>
            
            <el-table :data="selectedSuite.suite_requests" style="width: 100%">
              <el-table-column type="index" width="50" />
              <el-table-column prop="request.name" :label="$t('apiTesting.automation.requestName')" min-width="200" />
              <el-table-column prop="request.method" :label="$t('apiTesting.automation.method')" width="80">
                <template #default="scope">
                  <el-tag :type="getMethodType(scope.row.request.method)" size="small">
                    {{ scope.row.request.method }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="request.url" label="URL" min-width="300" show-overflow-tooltip />
              <el-table-column prop="enabled" :label="$t('apiTesting.automation.enabled')" width="80">
                <template #default="scope">
                  <el-switch
                    v-model="scope.row.enabled"
                    @change="updateRequestEnabled(scope.row)"
                  />
                </template>
              </el-table-column>
              <el-table-column :label="$t('apiTesting.automation.assertions')" width="100">
                <template #default="scope">
                  {{ $t('apiTesting.automation.assertionCount', { n: scope.row.assertions?.length || 0 }) }}
                </template>
              </el-table-column>
              <el-table-column :label="$t('apiTesting.common.operation')" width="150">
                <template #default="scope">
                  <el-button link type="primary" @click="editAssertions(scope.row)" size="small">
                    {{ $t('apiTesting.automation.editAssertions') }}
                  </el-button>
                  <el-button link type="danger" @click="removeRequest(scope.row)" size="small">
                    {{ $t('apiTesting.automation.remove') }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 执行历史 -->
          <div class="executions-section">
            <div class="section-header">
              <h5>{{ $t('apiTesting.automation.executionHistory') }}</h5>
              <el-button size="small" @click="loadExecutions">
                <el-icon><Refresh /></el-icon>
                {{ $t('apiTesting.automation.refresh') }}
              </el-button>
            </div>

            <el-table :data="executions" v-loading="executionsLoading">
              <el-table-column prop="status" :label="$t('apiTesting.common.status')" width="100">
                <template #default="scope">
                  <el-tag :type="getStatusType(scope.row.status)">
                    {{ getStatusText(scope.row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="total_requests" :label="$t('apiTesting.automation.totalRequests')" width="100" />
              <el-table-column prop="passed_requests" :label="$t('apiTesting.automation.passedCount')" width="100">
                <template #default="scope">
                  <span style="color: #67c23a">{{ scope.row.passed_requests }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="failed_requests" :label="$t('apiTesting.automation.failedCount')" width="100">
                <template #default="scope">
                  <span style="color: #f56c6c">{{ scope.row.failed_requests }}</span>
                </template>
              </el-table-column>
              <el-table-column :label="$t('apiTesting.automation.averageTime')" width="120">
                <template #default="scope">
                  {{ getAverageExecutionTime(scope.row) }}
                </template>
              </el-table-column>
              <el-table-column prop="executed_by.username" :label="$t('apiTesting.automation.executor')" width="120" />
              <el-table-column prop="created_at" :label="$t('apiTesting.automation.executionTime')" width="160">
                <template #default="scope">
                  {{ formatDate(scope.row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column :label="$t('apiTesting.common.operation')" width="120">
                <template #default="scope">
                  <el-button link type="primary" @click="viewExecutionDetail(scope.row)" size="small">
                    {{ $t('apiTesting.automation.viewDetails') }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建/编辑测试套件对话框 -->
    <el-dialog
      v-model="showCreateSuiteDialog"
      :title="editingSuite ? $t('apiTesting.automation.editSuite') : $t('apiTesting.automation.createSuite')"
      width="600px"
      @close="resetSuiteForm"
    >
      <el-form
        ref="suiteFormRef"
        :model="suiteForm"
        :rules="suiteRules"
        label-width="100px"
      >
        <el-form-item :label="$t('apiTesting.automation.suiteName')" prop="name">
          <el-input v-model="suiteForm.name" :placeholder="$t('apiTesting.automation.inputSuiteName')" />
        </el-form-item>

        <el-form-item :label="$t('apiTesting.automation.suiteDescription')" prop="description">
          <el-input
            v-model="suiteForm.description"
            type="textarea"
            :rows="3"
            :placeholder="$t('apiTesting.automation.inputSuiteDescription')"
          />
        </el-form-item>

        <el-form-item :label="$t('apiTesting.automation.belongProject')" prop="project">
          <el-select v-model="suiteForm.project" :placeholder="$t('apiTesting.automation.selectProject')">
            <el-option
              v-for="project in httpProjects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('apiTesting.automation.executionEnvironment')" prop="environment">
          <el-select v-model="suiteForm.environment" :placeholder="$t('apiTesting.automation.selectEnvironment')" clearable>
            <el-option
              v-for="env in environments"
              :key="env.id"
              :label="env.name"
              :value="env.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateSuiteDialog = false">{{ $t('apiTesting.common.cancel') }}</el-button>
        <el-button type="primary" @click="submitSuiteForm" :loading="submittingSuite">
          {{ editingSuite ? $t('apiTesting.common.update') : $t('apiTesting.common.create') }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 添加请求对话框 -->
    <el-dialog
      v-model="showAddRequestDialog"
      :title="$t('apiTesting.automation.addRequestToSuite')"
      width="800px"
    >
      <div class="add-request-content">
        <div class="request-selector">
          <el-tree
            ref="requestTreeRef"
            :data="requestTree"
            :props="requestTreeProps"
            show-checkbox
            node-key="id"
            :check-on-click-node="false"
            @check="onRequestCheck"
          >
            <template #default="{ node, data }">
              <div class="request-tree-node">
                <el-icon v-if="data.type === 'collection'">
                  <Folder />
                </el-icon>
                <el-icon v-else>
                  <Document />
                </el-icon>
                <span>{{ data.name }}</span>
                <span v-if="data.type === 'request'" class="method-tag" :class="data.method?.toLowerCase()">
                  {{ data.method }}
                </span>
              </div>
            </template>
          </el-tree>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showAddRequestDialog = false">{{ $t('apiTesting.common.cancel') }}</el-button>
        <el-button type="primary" @click="addSelectedRequests" :loading="addingRequests">
          {{ $t('apiTesting.automation.addSelectedRequests') }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 执行结果对话框 -->
    <el-dialog
      v-model="showExecutionDialog"
      :title="$t('apiTesting.automation.testExecutionResult')"
      width="80%"
      :top="'5vh'"
    >
      <div v-if="currentExecution" class="execution-detail">
        <div class="execution-summary">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-statistic :title="$t('apiTesting.automation.totalRequests')" :value="currentExecution.total_requests" />
            </el-col>
            <el-col :span="6">
              <el-statistic :title="$t('apiTesting.automation.passedCount')" :value="currentExecution.passed_requests" />
            </el-col>
            <el-col :span="6">
              <el-statistic :title="$t('apiTesting.automation.failedCount')" :value="currentExecution.failed_requests" />
            </el-col>
            <el-col :span="6">
              <el-statistic :title="$t('apiTesting.automation.passRate')" :value="getPassRate(currentExecution)" suffix="%" />
            </el-col>
          </el-row>
        </div>

        <div class="execution-results">
          <h4>{{ $t('apiTesting.automation.detailedResults') }}</h4>
          <el-table :data="formatExecutionResults(currentExecution.results)">
            <el-table-column prop="name" :label="$t('apiTesting.automation.requestName')" min-width="200" />
            <el-table-column prop="method" :label="$t('apiTesting.automation.method')" width="80">
              <template #default="scope">
                <el-tag :type="getMethodType(scope.row.method)" size="small">
                  {{ scope.row.method }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" :label="$t('apiTesting.automation.result')" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.passed ? 'success' : 'danger'" size="small">
                  {{ scope.row.passed ? $t('apiTesting.automation.status.passed') : $t('apiTesting.automation.status.failed') }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status_code" :label="$t('apiTesting.automation.statusCode')" width="100" />
            <el-table-column prop="response_time" :label="$t('apiTesting.automation.responseTime')" width="120">
              <template #default="scope">
                {{ scope.row.response_time?.toFixed(0) }}ms
              </template>
            </el-table-column>
            <el-table-column prop="error" :label="$t('apiTesting.automation.errorMessage')" min-width="200" show-overflow-tooltip />
          </el-table>
        </div>
      </div>

      <template #footer>
        <el-button @click="showExecutionDialog = false">{{ $t('apiTesting.common.close') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import {
  Plus, Refresh, MoreFilled, VideoPlay, Edit,
  Folder, Document
} from '@element-plus/icons-vue'
import api from '@/utils/api'
import dayjs from 'dayjs'

const { t } = useI18n()

const projects = ref([])
const selectedProject = ref(null)
const testSuites = ref([])
const selectedSuite = ref(null)
const executions = ref([])
const environments = ref([])
const requestTree = ref([])
const running = ref(false)
const executionsLoading = ref(false)
const showCreateSuiteDialog = ref(false)
const showAddRequestDialog = ref(false)
const showExecutionDialog = ref(false)
const editingSuite = ref(null)
const submittingSuite = ref(false)
const addingRequests = ref(false)
const currentExecution = ref(null)
const suiteFormRef = ref()
const requestTreeRef = ref()

const suiteForm = reactive({
  name: '',
  description: '',
  project: null,
  environment: null
})

const suiteRules = computed(() => ({
  name: [{ required: true, message: t('apiTesting.automation.inputSuiteName'), trigger: 'blur' }],
  project: [{ required: true, message: t('apiTesting.automation.selectProject'), trigger: 'change' }]
}))

const requestTreeProps = {
  children: 'children',
  label: 'name'
}

const httpProjects = computed(() => {
  return projects.value.filter(project => project.project_type !== 'WEBSOCKET')
})

const getMethodType = (method) => {
  const typeMap = {
    'GET': 'success',
    'POST': 'primary',
    'PUT': 'warning', 
    'DELETE': 'danger',
    'PATCH': 'info'
  }
  return typeMap[method] || 'info'
}

const getStatusType = (status) => {
  const typeMap = {
    'PENDING': 'info',
    'RUNNING': 'warning',
    'COMPLETED': 'success',
    'FAILED': 'danger',
    'CANCELLED': 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusKey = {
    'PENDING': 'pending',
    'RUNNING': 'running',
    'COMPLETED': 'completed',
    'FAILED': 'failed',
    'CANCELLED': 'cancelled'
  }[status]
  return statusKey ? t(`apiTesting.automation.status.${statusKey}`) : status
}

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm:ss')
}

const getExecutionTime = (execution) => {
  if (!execution.start_time || !execution.end_time) return '-'
  const start = dayjs(execution.start_time)
  const end = dayjs(execution.end_time)
  return `${end.diff(start, 'second')}s`
}

const getAverageExecutionTime = (execution) => {
  if (!execution.results || !Array.isArray(execution.results) || execution.results.length === 0) {
    return '-'
  }
  
  // 计算所有请求的平均响应时间
  const totalResponseTime = execution.results.reduce((sum, result) => sum + (result.response_time || 0), 0)
  const averageTime = totalResponseTime / execution.results.length
  
  if (averageTime < 1000) {
    return `${Math.round(averageTime)}ms`
  } else {
    return `${(averageTime / 1000).toFixed(1)}s`
  }
}

const getPassRate = (execution) => {
  if (execution.total_requests === 0) return 0
  return ((execution.passed_requests / execution.total_requests) * 100).toFixed(1)
}

const getEnvironmentName = (environmentId) => {
  if (!environmentId) return t('apiTesting.automation.noEnvironment')
  const env = environments.value.find(e => e.id === environmentId)
  return env ? env.name : t('apiTesting.automation.noEnvironment')
}

const loadProjects = async () => {
  try {
    const response = await api.get('/api-testing/projects/')
    projects.value = response.data.results || response.data

    // 过滤出HTTP项目
    const httpProjects = projects.value.filter(project => project.project_type !== 'WEBSOCKET')

    if (httpProjects.length > 0 && !selectedProject.value) {
      selectedProject.value = httpProjects[0].id
      await onProjectChange()
    } else if (httpProjects.length === 0) {
      // 如果没有HTTP项目，清空选择
      selectedProject.value = null
    }
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.loadProjects'))
  }
}

const loadTestSuites = async () => {
  if (!selectedProject.value) return

  try {
    const response = await api.get('/api-testing/test-suites/', {
      params: { project: selectedProject.value }
    })
    testSuites.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.loadTestSuites'))
  }
}

const loadEnvironments = async () => {
  try {
    // 获取全局环境 + 当前项目环境
    const response = await api.get('/api-testing/environments/', {
      // 不传递project参数，让后端返回所有可访问的环境（全局+当前项目）
    })
    const allEnvironments = response.data.results || response.data

    // 过滤当前项目相关或全局环境
    environments.value = allEnvironments.filter(env =>
      env.scope === 'GLOBAL' ||
      (env.scope === 'LOCAL' && (!selectedProject.value || env.project === selectedProject.value))
    )
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.loadEnvironments'))
  }
}

const loadRequestTree = async () => {
  if (!selectedProject.value) return

  try {
    // 加载集合
    const collectionsRes = await api.get('/api-testing/collections/', {
      params: { project: selectedProject.value }
    })
    const collections = collectionsRes.data.results || collectionsRes.data

    // 加载请求
    const requestsRes = await api.get('/api-testing/requests/')
    const requests = requestsRes.data.results || requestsRes.data

    // 构建树形结构
    requestTree.value = buildRequestTree(collections, requests)
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.loadRequestTree'))
  }
}

const buildRequestTree = (collections, requests) => {
  const map = {}
  const roots = []
  
  // 创建集合节点
  collections.forEach(collection => {
    map[collection.id] = {
      ...collection,
      type: 'collection',
      children: []
    }
  })
  
  // 构建集合层级关系
  collections.forEach(collection => {
    if (collection.parent && map[collection.parent]) {
      map[collection.parent].children.push(map[collection.id])
    } else {
      roots.push(map[collection.id])
    }
  })
  
  // 添加请求到对应集合
  requests.forEach(request => {
    if (map[request.collection]) {
      map[request.collection].children.push({
        ...request,
        type: 'request',
        id: `request_${request.id}`
      })
    }
  })
  
  return roots
}

const loadExecutions = async () => {
  if (!selectedSuite.value) return

  executionsLoading.value = true
  try {
    const response = await api.get('/api-testing/test-executions/', {
      params: { test_suite: selectedSuite.value.id }
    })
    executions.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.loadExecutionHistory'))
  } finally {
    executionsLoading.value = false
  }
}

const onProjectChange = async () => {
  // 检查选中的项目是否为HTTP项目
  const selectedProjectData = projects.value.find(p => p.id === selectedProject.value)
  if (selectedProjectData && selectedProjectData.project_type === 'WEBSOCKET') {
    ElMessage.warning(t('apiTesting.messages.warning.websocketNotSupported'))
    // 重置为第一个HTTP项目或清空选择
    const httpProjects = projects.value.filter(project => project.project_type !== 'WEBSOCKET')
    if (httpProjects.length > 0) {
      selectedProject.value = httpProjects[0].id
    } else {
      selectedProject.value = null
    }
    return
  }

  selectedSuite.value = null
  await Promise.all([
    loadTestSuites(),
    loadEnvironments(),
    loadRequestTree()
  ])
}

const selectSuite = (suite) => {
  selectedSuite.value = suite
  loadExecutions()
}

const handleSuiteAction = async ({ action, suite }) => {
  switch (action) {
    case 'run':
      await runTestSuite(suite)
      break
    case 'edit':
      editSuite(suite)
      break
    case 'duplicate':
      await duplicateSuite(suite)
      break
    case 'delete':
      await deleteSuite(suite)
      break
  }
}

const runTestSuite = async (suite) => {
  running.value = true
  try {
    const response = await api.post(`/api-testing/test-suites/${suite.id}/execute/`)
    currentExecution.value = response.data
    showExecutionDialog.value = true
    await loadExecutions()
    ElMessage.success(t('apiTesting.messages.success.suiteExecuted'))
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.executeSuite'))
  } finally {
    running.value = false
  }
}

const editSuite = (suite) => {
  editingSuite.value = suite
  suiteForm.name = suite.name
  suiteForm.description = suite.description
  suiteForm.project = suite.project
  // 修复：environment字段直接是ID，不需要?.id
  suiteForm.environment = suite.environment || null
  showCreateSuiteDialog.value = true
}

const duplicateSuite = async (suite) => {
  try {
    const newSuite = {
      name: `${suite.name} - ${t('apiTesting.common.copyText')}`,
      description: suite.description,
      project: suite.project,
      environment: suite.environment || null  // 修复：直接使用environment ID
    }
    await api.post('/api-testing/test-suites/', newSuite)
    ElMessage.success(t('apiTesting.messages.success.copy'))
    await loadTestSuites()
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.copyFailed'))
  }
}

const deleteSuite = async (suite) => {
  try {
    await ElMessageBox.confirm(
      t('apiTesting.automation.confirmDeleteSuite', { name: suite.name }),
      t('apiTesting.messages.confirm.deleteTitle'),
      {
        confirmButtonText: t('apiTesting.common.confirm'),
        cancelButtonText: t('apiTesting.common.cancel'),
        type: 'warning'
      }
    )

    await api.delete(`/api-testing/test-suites/${suite.id}/`)
    ElMessage.success(t('apiTesting.messages.success.delete'))

    if (selectedSuite.value?.id === suite.id) {
      selectedSuite.value = null
    }
    await loadTestSuites()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('apiTesting.messages.error.deleteFailed'))
    }
  }
}

const submitSuiteForm = async () => {
  if (!suiteFormRef.value) return

  const valid = await suiteFormRef.value.validate().catch(() => false)
  if (!valid) return

  submittingSuite.value = true
  try {
    if (editingSuite.value) {
      await api.put(`/api-testing/test-suites/${editingSuite.value.id}/`, suiteForm)
      ElMessage.success(t('apiTesting.messages.success.suiteUpdated'))
    } else {
      await api.post('/api-testing/test-suites/', suiteForm)
      ElMessage.success(t('apiTesting.messages.success.suiteCreated'))
    }

    showCreateSuiteDialog.value = false
    await loadTestSuites()
  } catch (error) {
    ElMessage.error(editingSuite.value ? t('apiTesting.messages.error.updateFailed') : t('apiTesting.messages.error.createFailed'))
  } finally {
    submittingSuite.value = false
  }
}

const resetSuiteForm = () => {
  editingSuite.value = null
  Object.assign(suiteForm, {
    name: '',
    description: '',
    project: selectedProject.value,
    environment: null
  })
  suiteFormRef.value?.resetFields()
}

const showAddRequest = async () => {
  await loadRequestTree()
  showAddRequestDialog.value = true
  
  // 等待对话框显示完成后再设置勾选状态
  nextTick(() => {
    setTimeout(() => {
      if (requestTreeRef.value && selectedSuite.value) {
        // 获取当前已关联的请求ID
        const existingRequestIds = selectedSuite.value.suite_requests?.map(sr => 
          `request_${sr.request.id}`
        ) || []
        
        // 设置已关联接口为已勾选状态
        requestTreeRef.value.setCheckedKeys(existingRequestIds, false)
        console.log('设置已关联接口ID:', existingRequestIds)
      }
    }, 200)
  })
}

const onRequestCheck = () => {
  // 请求选择变化处理
}

const addSelectedRequests = async () => {
  const checkedNodes = requestTreeRef.value.getCheckedNodes()
  const requestIds = checkedNodes
    .filter(node => node.type === 'request')
    .map(node => node.id.replace('request_', ''))

  if (requestIds.length === 0) {
    ElMessage.warning(t('apiTesting.messages.warning.selectAtLeastOneRequest'))
    return
  }

  addingRequests.value = true
  try {
    // 这里需要调用添加请求到套件的API
    await api.post(`/api-testing/test-suites/${selectedSuite.value.id}/add-requests/`, {
      request_ids: requestIds
    })

    ElMessage.success(t('apiTesting.messages.success.addSuccess'))
    showAddRequestDialog.value = false
    // 重新加载当前测试套件详情
    await reloadCurrentSuite()
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.addFailed'))
  } finally {
    addingRequests.value = false
  }
}

const updateRequestEnabled = async (suiteRequest) => {
  try {
    await api.put(`/api-testing/test-suite-requests/${suiteRequest.id}/`, {
      enabled: suiteRequest.enabled
    })
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.updateFailed'))
    suiteRequest.enabled = !suiteRequest.enabled
  }
}

const editAssertions = (suiteRequest) => {
  ElMessage.info(t('apiTesting.messages.info.featureInDevelopment'))
}

const removeRequest = async (suiteRequest) => {
  try {
    await ElMessageBox.confirm(t('apiTesting.automation.confirmRemoveRequest'), t('apiTesting.automation.confirmRemove'), {
      confirmButtonText: t('apiTesting.common.confirm'),
      cancelButtonText: t('apiTesting.common.cancel'),
      type: 'warning'
    })

    await api.delete(`/api-testing/test-suite-requests/${suiteRequest.id}/`)
    ElMessage.success(t('apiTesting.messages.success.removeSuccess'))
    // 重新加载当前测试套件详情
    await reloadCurrentSuite()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('apiTesting.messages.error.removeFailed'))
    }
  }
}

const reloadCurrentSuite = async () => {
  if (!selectedSuite.value) return

  try {
    // 重新加载当前测试套件的详细信息
    const response = await api.get(`/api-testing/test-suites/${selectedSuite.value.id}/`)
    const updatedSuite = response.data

    // 强制重新设置响应式数据
    selectedSuite.value = { ...updatedSuite }

    // 同时更新测试套件列表中对应的套件
    const index = testSuites.value.findIndex(suite => suite.id === updatedSuite.id)
    if (index !== -1) {
      testSuites.value[index] = { ...updatedSuite }
    }
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.refreshSuiteFailed'))
  }
}

const viewExecutionDetail = (execution) => {
  currentExecution.value = execution
  showExecutionDialog.value = true
}

const formatExecutionResults = (results) => {
  if (!results || !Array.isArray(results)) return []
  return results
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped>
.automation-testing {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h3 {
  margin: 0;
  color: #303133;
}

.content-layout {
  display: flex;
  flex: 1;
  gap: 20px;
  overflow: hidden;
}

.sidebar {
  width: 300px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.project-selector {
  background: white;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.suite-list {
  background: white;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  overflow: hidden;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  font-weight: 500;
}

.suite-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  border-bottom: 1px solid #f5f7fa;
  cursor: pointer;
  transition: background-color 0.3s;
}

.suite-item:hover {
  background: #f5f7fa;
}

.suite-item.active {
  background: #e1f3d8;
  border-color: #67c23a;
}

.suite-info {
  flex: 1;
}

.suite-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.suite-meta {
  font-size: 12px;
  color: #909399;
}

.main-content {
  flex: 1;
  background: white;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.suite-detail {
  flex: 1;
  padding: 20px;
  overflow: auto;
}

.suite-header {
  margin-bottom: 30px;
}

.suite-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.suite-title h4 {
  margin: 0;
  color: #303133;
}

.suite-actions {
  display: flex;
  gap: 10px;
}

.suite-description {
  color: #606266;
  margin-bottom: 10px;
}

.suite-meta {
  display: flex;
  gap: 15px;
  align-items: center;
}

.meta-text {
  font-size: 12px;
  color: #909399;
}

.requests-section,
.executions-section {
  margin-bottom: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h5 {
  margin: 0;
  color: #303133;
  font-size: 16px;
}

.add-request-content {
  max-height: 400px;
  overflow-y: auto;
}

.request-tree-node {
  display: flex;
  align-items: center;
  gap: 5px;
  flex: 1;
}

.method-tag {
  font-size: 10px;
  padding: 1px 4px;
  border-radius: 2px;
  color: white;
  font-weight: bold;
  margin-left: auto;
}

.method-tag.get { background: #67c23a; }
.method-tag.post { background: #409eff; }
.method-tag.put { background: #e6a23c; }
.method-tag.delete { background: #f56c6c; }
.method-tag.patch { background: #909399; }

.execution-detail {
  max-height: 70vh;
  overflow-y: auto;
}

.execution-summary {
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 6px;
}

.execution-results h4 {
  margin: 0 0 15px 0;
  color: #303133;
}
</style>