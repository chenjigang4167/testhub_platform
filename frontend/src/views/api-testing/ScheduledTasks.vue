<template>
  <div class="scheduled-tasks">
    <div class="header">
      <h3>{{ $t('apiTesting.scheduledTask.title') }}</h3>
      <el-button type="primary" @click="handleCreateClick">
        <el-icon><Plus /></el-icon>
        {{ $t('apiTesting.scheduledTask.createTask') }}
      </el-button>
    </div>

    <!-- 筛选条件 -->
    <div class="filters">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-select v-model="filters.task_type" :placeholder="$t('apiTesting.scheduledTask.taskType')" clearable>
            <el-option :label="$t('apiTesting.scheduledTask.taskTypes.testSuite')" value="TEST_SUITE" />
            <el-option :label="$t('apiTesting.scheduledTask.taskTypes.apiRequest')" value="API_REQUEST" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="filters.trigger_type" :placeholder="$t('apiTesting.scheduledTask.triggerType')" clearable>
            <el-option :label="$t('apiTesting.scheduledTask.triggerTypes.cron')" value="CRON" />
            <el-option :label="$t('apiTesting.scheduledTask.triggerTypes.interval')" value="INTERVAL" />
            <el-option :label="$t('apiTesting.scheduledTask.triggerTypes.once')" value="ONCE" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="filters.status" :placeholder="$t('apiTesting.scheduledTask.taskStatus')" clearable>
            <el-option :label="$t('apiTesting.scheduledTask.status.active')" value="ACTIVE" />
            <el-option :label="$t('apiTesting.scheduledTask.status.paused')" value="PAUSED" />
            <el-option :label="$t('apiTesting.scheduledTask.status.completed')" value="COMPLETED" />
            <el-option :label="$t('apiTesting.scheduledTask.status.failed')" value="FAILED" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button @click="resetFilters">{{ $t('apiTesting.common.reset') }}</el-button>
          <el-button type="primary" @click="loadTasks">{{ $t('apiTesting.common.search') }}</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 任务列表 -->
    <div class="task-list">
      <el-table :data="tasks" v-loading="loading">
        <el-table-column prop="name" :label="$t('apiTesting.scheduledTask.taskName')" min-width="200" />
        <el-table-column prop="task_type" :label="$t('apiTesting.scheduledTask.taskType')" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.task_type === 'TEST_SUITE' ? 'success' : 'primary'">
              {{ scope.row.task_type === 'TEST_SUITE' ? $t('apiTesting.scheduledTask.taskTypes.testSuiteShort') : $t('apiTesting.scheduledTask.taskTypes.apiRequestShort') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="trigger_type" :label="$t('apiTesting.scheduledTask.triggerType')" width="120">
          <template #default="scope">
            <el-tag>
              {{ getTriggerTypeText(scope.row.trigger_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" :label="$t('apiTesting.common.status')" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'ACTIVE' ? 'success' : scope.row.status === 'PAUSED' ? 'warning' : 'info'">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="notification_type_display" :label="$t('apiTesting.scheduledTask.notificationType')" width="120">
          <template #default="scope">
            <el-tag
              :type="getNotificationTypeTag(scope.row.notification_type_display)"
              size="small"
            >
              {{ scope.row.notification_type_display || '-' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="next_run_time" :label="$t('apiTesting.scheduledTask.nextRunTime')" width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.next_run_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="last_run_time" :label="$t('apiTesting.scheduledTask.lastRunTime')" width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.last_run_time) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('apiTesting.common.operation')" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="runTaskNow(scope.row)" :loading="scope.row.running">
              {{ $t('apiTesting.scheduledTask.runNow') }}
            </el-button>
            <el-dropdown @command="(command) => handleTaskAction(command, scope.row)">
              <el-button size="small">
                {{ $t('apiTesting.common.more') }}<el-icon><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="edit">{{ $t('apiTesting.common.edit') }}</el-dropdown-item>
                  <el-dropdown-item command="pause" v-if="scope.row.status === 'ACTIVE'">{{ $t('apiTesting.scheduledTask.pause') }}</el-dropdown-item>
                  <el-dropdown-item command="activate" v-if="scope.row.status === 'PAUSED'">{{ $t('apiTesting.scheduledTask.activate') }}</el-dropdown-item>
                  <el-dropdown-item command="logs">{{ $t('apiTesting.scheduledTask.executionLogs') }}</el-dropdown-item>
                  <el-dropdown-item command="delete" divided>{{ $t('apiTesting.common.delete') }}</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="pagination.current"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadTasks"
        @current-change="loadTasks"
      />
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingTask ? $t('apiTesting.scheduledTask.editTask') : $t('apiTesting.scheduledTask.createTask')"
      width="800px"
      @close="resetTaskForm"
    >
      <el-form :model="taskForm" label-width="120px">
        <el-form-item :label="$t('apiTesting.scheduledTask.taskName')" required>
          <el-input v-model="taskForm.name" :placeholder="$t('apiTesting.scheduledTask.inputTaskName')" />
        </el-form-item>

        <el-form-item :label="$t('apiTesting.scheduledTask.taskDescription')">
          <el-input v-model="taskForm.description" type="textarea" :placeholder="$t('apiTesting.scheduledTask.inputTaskDesc')" />
        </el-form-item>

        <el-form-item :label="$t('apiTesting.scheduledTask.taskType')" required>
          <el-radio-group v-model="taskForm.task_type">
            <el-radio label="TEST_SUITE">{{ $t('apiTesting.scheduledTask.taskTypes.testSuite') }}</el-radio>
            <el-radio label="API_REQUEST">{{ $t('apiTesting.scheduledTask.taskTypes.apiRequest') }}</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item :label="$t('apiTesting.scheduledTask.triggerType')" required>
          <el-radio-group v-model="taskForm.trigger_type">
            <el-radio label="CRON">{{ $t('apiTesting.scheduledTask.triggerTypes.cron') }}</el-radio>
            <el-radio label="INTERVAL">{{ $t('apiTesting.scheduledTask.triggerTypes.interval') }}</el-radio>
            <el-radio label="ONCE">{{ $t('apiTesting.scheduledTask.triggerTypes.once') }}</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 根据触发器类型显示不同配置 -->
        <el-form-item v-if="taskForm.trigger_type === 'CRON'" :label="$t('apiTesting.scheduledTask.cronExpression')" required>
          <el-input v-model="taskForm.cron_expression" placeholder="0 0 * * *" />
          <div class="cron-help">
            <el-tooltip
              raw-content
              placement="top"
            >
              <template #content>
                <div style="line-height: 1.6; text-align: left;">
                  <div>{{ $t('apiTesting.scheduledTask.cronHelp.format') }}</div>
                  <div>• {{ $t('apiTesting.scheduledTask.cronHelp.minute') }}</div>
                  <div>• {{ $t('apiTesting.scheduledTask.cronHelp.hour') }}</div>
                  <div>• {{ $t('apiTesting.scheduledTask.cronHelp.day') }}</div>
                  <div>• {{ $t('apiTesting.scheduledTask.cronHelp.month') }}</div>
                  <div>• {{ $t('apiTesting.scheduledTask.cronHelp.week') }}</div>
                  <div style="margin-top: 8px;">{{ $t('apiTesting.scheduledTask.cronHelp.examples') }}</div>
                  <div>• {{ $t('apiTesting.scheduledTask.cronHelp.daily') }}</div>
                  <div>• {{ $t('apiTesting.scheduledTask.cronHelp.hourly') }}</div>
                  <div>• {{ $t('apiTesting.scheduledTask.cronHelp.weekly') }}</div>
                  <div>• {{ $t('apiTesting.scheduledTask.cronHelp.monthly') }}</div>
                </div>
              </template>
              <span style="cursor: pointer; color: #409EFF;">{{ $t('apiTesting.scheduledTask.cronHelpLink') }}</span>
            </el-tooltip>
          </div>
        </el-form-item>

        <el-form-item v-if="taskForm.trigger_type === 'INTERVAL'" :label="$t('apiTesting.scheduledTask.intervalTime')" required>
          <el-input-number v-model="taskForm.interval_seconds" :min="60" :step="60" />
          <span class="unit">{{ $t('apiTesting.scheduledTask.seconds') }}</span>
        </el-form-item>

        <el-form-item v-if="taskForm.trigger_type === 'ONCE'" :label="$t('apiTesting.scheduledTask.executeTime')" required>
          <el-date-picker
            v-model="taskForm.execute_at"
            type="datetime"
            :placeholder="$t('apiTesting.scheduledTask.selectExecuteTime')"
          />
        </el-form-item>

        <!-- 根据任务类型显示不同配置 -->
        <el-form-item v-if="taskForm.task_type === 'TEST_SUITE'" :label="$t('apiTesting.automation.testSuite')" required>
          <el-select v-model="taskForm.test_suite" :placeholder="$t('apiTesting.scheduledTask.selectTestSuite')">
            <el-option
              v-for="suite in testSuites"
              :key="suite.id"
              :label="suite.name"
              :value="suite.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item v-if="taskForm.task_type === 'API_REQUEST'" :label="$t('apiTesting.scheduledTask.apiRequest')" required>
          <el-select v-model="taskForm.api_request" :placeholder="$t('apiTesting.scheduledTask.selectApiRequest')">
            <el-option
              v-for="request in apiRequests"
              :key="request.id"
              :label="request.name"
              :value="request.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('apiTesting.scheduledTask.executeEnvironment')">
          <el-select v-model="taskForm.environment" :placeholder="$t('apiTesting.scheduledTask.selectEnvironment')">
            <el-option
              v-for="env in environments"
              :key="env.id"
              :label="env.name"
              :value="env.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('apiTesting.scheduledTask.notificationSettings')">
          <el-checkbox v-model="taskForm.notify_on_success">{{ $t('apiTesting.scheduledTask.notifyOnSuccess') }}</el-checkbox>
          <el-checkbox v-model="taskForm.notify_on_failure">{{ $t('apiTesting.scheduledTask.notifyOnFailure') }}</el-checkbox>
        </el-form-item>

        <el-form-item v-if="taskForm.notify_on_success || taskForm.notify_on_failure" :label="$t('apiTesting.scheduledTask.notificationType')">
          <el-select v-model="taskForm.notification_type" :placeholder="$t('apiTesting.scheduledTask.selectNotificationType')">
            <el-option :label="$t('apiTesting.notification.types.email')" value="email" />
            <el-option :label="$t('apiTesting.notification.types.webhook')" value="webhook" />
            <el-option :label="$t('apiTesting.notification.types.both')" value="both" />
          </el-select>
        </el-form-item>

        <el-form-item v-if="(taskForm.notify_on_success || taskForm.notify_on_failure) && taskForm.notification_type !== 'webhook'" :label="$t('apiTesting.scheduledTask.notifyEmails')">
          <el-select
            v-model="taskForm.notify_emails"
            multiple
            filterable
            :placeholder="$t('apiTesting.scheduledTask.selectNotifyEmails')"
          >
            <el-option
              v-for="user in users"
              :key="user.id"
              :label="user.display_name"
              :value="user.email"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">{{ $t('apiTesting.common.cancel') }}</el-button>
        <el-button type="primary" @click="submitTaskForm" :loading="submitting">
          {{ editingTask ? $t('apiTesting.common.update') : $t('apiTesting.common.create') }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 执行日志对话框 -->
    <el-dialog v-model="showLogsDialog" :title="$t('apiTesting.scheduledTask.executionLogs')" width="1000px">
      <el-table :data="executionLogs" v-loading="logsLoading">
        <el-table-column prop="start_time" :label="$t('apiTesting.scheduledTask.startTime')" width="180">
          <template #default="scope">
            <div class="time-cell">{{ formatDateTime(scope.row.start_time) }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="end_time" :label="$t('apiTesting.scheduledTask.endTime')" width="180">
          <template #default="scope">
            <div class="time-cell">{{ formatDateTime(scope.row.end_time) }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="status" :label="$t('apiTesting.common.status')" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'COMPLETED' ? 'success' : 'danger'">
              {{ scope.row.status === 'COMPLETED' ? $t('apiTesting.common.success') : $t('apiTesting.common.failed') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="error_message" :label="$t('apiTesting.scheduledTask.errorMessage')" width="300" show-overflow-tooltip />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { Plus, ArrowDown } from '@element-plus/icons-vue'
import api from '@/utils/api'
import {
  getScheduledTasks,
  createScheduledTask,
  updateScheduledTask,
  deleteScheduledTask,
  runScheduledTask,
  getExecutionLogs,
  getTestSuites,
  getApiRequests,
  getEnvironments,
  getUsers
} from '@/api/api-testing.js'

const { t } = useI18n()

// 获取状态文本
const getStatusText = (status) => {
  const statusKey = {
    'ACTIVE': 'active',
    'PAUSED': 'paused',
    'COMPLETED': 'completed',
    'FAILED': 'failed'
  }[status]
  return statusKey ? t(`apiTesting.scheduledTask.status.${statusKey}`) : status
}

// 获取触发器类型文本
const getTriggerTypeText = (type) => {
  const typeKey = {
    'CRON': 'cron',
    'INTERVAL': 'interval',
    'ONCE': 'once'
  }[type]
  return typeKey ? t(`apiTesting.scheduledTask.triggerTypes.${typeKey}`) : type
}

// 数据状态
const tasks = ref([])
const executionLogs = ref([])
const testSuites = ref([])
const apiRequests = ref([])
const environments = ref([])
const users = ref([]) // 添加用户列表
const loading = ref(false)
const logsLoading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
const showLogsDialog = ref(false)
const editingTask = ref(null)

// 筛选条件
const filters = reactive({
  task_type: '',
  trigger_type: '',
  status: ''
})

// 分页配置
const pagination = reactive({
  current: 1,
  size: 10,
  total: 0
})

// 表单数据
const taskForm = reactive({
  name: '',
  description: '',
  task_type: 'TEST_SUITE',
  trigger_type: 'CRON',
  cron_expression: '0 0 * * *',
  interval_seconds: 3600,
  execute_at: '',
  test_suite: '',
  api_request: '',
  environment: '',
  notify_on_success: false,
  notify_on_failure: false,
  notify_emails: []
})

// 生命周期
onMounted(() => {
  loadTasks()
  loadTestSuites()
  loadApiRequests()
  loadEnvironments()
  loadUsers() // 加载用户列表
})

// 加载任务列表
const loadTasks = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.size,
      ...filters
    }
    const response = await getScheduledTasks(params)
    tasks.value = response.data.results
    pagination.total = response.data.count
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.loadTasksFailed'))
  } finally {
    loading.value = false
  }
}

// 加载测试套件
const loadTestSuites = async () => {
  try {
    const response = await getTestSuites()
    testSuites.value = response.data.results
  } catch (error) {
    console.error('加载测试套件失败:', error)
  }
}

// 加载API请求
const loadApiRequests = async () => {
  try {
    const response = await getApiRequests()
    apiRequests.value = response.data.results
  } catch (error) {
    console.error('加载API请求失败:', error)
  }
}

// 加载环境
const loadEnvironments = async () => {
  try {
    const response = await getEnvironments()
    environments.value = response.data.results
  } catch (error) {
    console.error('加载环境失败:', error)
  }
}

// 加载用户列表
const loadUsers = async () => {
  try {
    const response = await getUsers()
    // 处理分页数据结构
    const usersData = response.data.results || response.data
    users.value = usersData.map(user => ({
      ...user,
      display_name: user.first_name ? `${user.first_name}（${user.email}）` : `${user.username}（${user.email}）`
    }))
  } catch (error) {
    console.error('加载用户列表失败:', error)
  }
}

// 新建按钮点击
const handleCreateClick = () => {
  console.log('新建按钮点击')
  editingTask.value = null
  resetTaskForm()
  showCreateDialog.value = true
}

// 重置表单
const resetTaskForm = () => {
  Object.assign(taskForm, {
    name: '',
    description: '',
    task_type: 'TEST_SUITE',
    trigger_type: 'CRON',
    cron_expression: '0 0 * * *',
    interval_seconds: 3600,
    execute_at: '',
    test_suite: '',
    api_request: '',
    environment: '',
    notify_on_success: false,
    notify_on_failure: false,
    notification_type: 'email',
    notify_emails: []
  })
}

// 重置筛选
const resetFilters = () => {
  Object.assign(filters, {
    task_type: '',
    trigger_type: '',
    status: ''
  })
  loadTasks()
}

// 提交任务表单
const submitTaskForm = async () => {
  submitting.value = true
  try {
    // 准备提交数据，确保格式正确
    const submitData = {
      name: taskForm.name,
      description: taskForm.description,
      task_type: taskForm.task_type,
      trigger_type: taskForm.trigger_type,
      notify_on_success: taskForm.notify_on_success,
      notify_on_failure: taskForm.notify_on_failure,
      notification_type_input: taskForm.notification_type,
      notify_emails: taskForm.notify_emails,
      environment: taskForm.environment
    }

    // 根据触发器类型添加对应字段
    if (taskForm.trigger_type === 'CRON') {
      submitData.cron_expression = taskForm.cron_expression
    } else if (taskForm.trigger_type === 'INTERVAL') {
      submitData.interval_seconds = taskForm.interval_seconds
    } else if (taskForm.trigger_type === 'ONCE') {
      submitData.execute_at = taskForm.execute_at
    }

    // 根据任务类型添加对应字段
    if (taskForm.task_type === 'TEST_SUITE') {
      submitData.test_suite = taskForm.test_suite
    } else if (taskForm.task_type === 'API_REQUEST') {
      submitData.api_request = taskForm.api_request
    }

    if (editingTask.value) {
      await updateScheduledTask(editingTask.value.id, submitData)
      ElMessage.success(t('apiTesting.messages.success.taskUpdated'))
    } else {
      await createScheduledTask(submitData)
      ElMessage.success(t('apiTesting.messages.success.taskCreated'))
    }
    showCreateDialog.value = false
    loadTasks()
  } catch (error) {
    console.error('Task operation failed:', error)
    ElMessage.error(error.response?.data?.error ||
                   error.response?.data?.detail ||
                   (editingTask.value ? t('apiTesting.messages.error.updateTaskFailed') : t('apiTesting.messages.error.createTaskFailed')))
  } finally {
    submitting.value = false
  }
}

// 立即执行任务
const runTaskNow = async (task) => {
  try {
    task.running = true
    await runScheduledTask(task.id)
    ElMessage.success(t('apiTesting.messages.success.taskStarted'))
    // 等待一段时间后刷新任务状态
    setTimeout(() => {
      loadTasks()
    }, 2000)
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.executeTaskFailed'))
  } finally {
    task.running = false
  }
}

// 格式化日期时间
const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).replace(/\//g, '-')
}

// 获取通知类型标签样式
const getNotificationTypeTag = (typeDisplay) => {
  const typeMap = {
    '邮箱通知': '',
    'Webhook机器人': 'primary',
    '两种都发送': 'warning'
  }
  return typeMap[typeDisplay] || 'info'
}

// 查看执行日志
const viewTaskLogs = async (task) => {
  logsLoading.value = true
  try {
    const response = await getExecutionLogs(task.id)
    executionLogs.value = response.data.results || response.data
    showLogsDialog.value = true
  } catch (error) {
    console.error('Load execution logs failed:', error)
    ElMessage.error(t('apiTesting.messages.error.loadLogsFailed'))
  } finally {
    logsLoading.value = false
  }
}

// 处理任务操作
const handleTaskAction = (command, task) => {
  switch (command) {
    case 'pause':
      pauseTask(task)
      break
    case 'activate':
      activateTask(task)
      break
    case 'edit':
      editTask(task)
      break
    case 'logs':
      viewTaskLogs(task)
      break
    case 'delete':
      deleteTask(task)
      break
  }
}

// 编辑任务
const editTask = (task) => {
  editingTask.value = task
  Object.assign(taskForm, {
    name: task.name,
    description: task.description,
    task_type: task.task_type,
    trigger_type: task.trigger_type,
    cron_expression: task.cron_expression,
    interval_seconds: task.interval_seconds,
    execute_at: task.execute_at,
    test_suite: task.test_suite || null,
    api_request: task.api_request || null,
    environment: task.environment || null,
    notify_on_success: task.notify_on_success,
    notify_on_failure: task.notify_on_failure,
    notification_type: task.notification_type || 'email',
    notify_emails: task.notify_emails || []
  })
  console.log('编辑任务数据回显:', {
    test_suite: task.test_suite,
    environment: task.environment,
    taskForm_test_suite: taskForm.test_suite,
    taskForm_environment: taskForm.environment
  })
  showCreateDialog.value = true
}

// 暂停任务
const pauseTask = async (task) => {
  try {
    await api.post(`/api-testing/scheduled-tasks/${task.id}/pause/`)
    ElMessage.success(t('apiTesting.messages.success.taskPaused'))
    loadTasks()
  } catch (error) {
    console.error('Pause task failed:', error)
    ElMessage.error(t('apiTesting.messages.error.pauseTaskFailed'))
  }
}

// 激活任务
const activateTask = async (task) => {
  try {
    await api.post(`/api-testing/scheduled-tasks/${task.id}/activate/`)
    ElMessage.success(t('apiTesting.messages.success.taskActivated'))
    loadTasks()
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.activateTaskFailed'))
  }
}

// 删除任务
const deleteTask = async (task) => {
  try {
    await ElMessageBox.confirm(
      t('apiTesting.scheduledTask.confirmDeleteTask'),
      t('apiTesting.common.tip'),
      {
        confirmButtonText: t('apiTesting.common.confirm'),
        cancelButtonText: t('apiTesting.common.cancel'),
        type: 'warning'
      }
    )
    await deleteScheduledTask(task.id)
    ElMessage.success(t('apiTesting.messages.success.taskDeleted'))
    loadTasks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('apiTesting.messages.error.deleteTaskFailed'))
    }
  }
}
</script>

<style scoped>
.scheduled-tasks {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: px;
}

.filters {
  margin-bottom: 20px;
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
}

.task-list {
  flex: 1;
  overflow: hidden;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.cron-help {
  margin-top: 8px;
  font-size: 12px;
}

.unit {
  margin-left: 8px;
  color: #606266;
}
</style>