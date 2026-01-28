<template>
  <div class="scheduled-tasks">
    <div class="header">
      <h3>{{ $t('uiAutomation.scheduledTask.title') }}</h3>
      <el-button type="primary" @click="handleCreateClick">
        <el-icon><Plus /></el-icon>
        {{ $t('uiAutomation.scheduledTask.newTask') }}
      </el-button>
    </div>

    <!-- 筛选条件 -->
    <div class="filters">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-select v-model="filters.task_type" :placeholder="$t('uiAutomation.scheduledTask.taskType')" clearable>
            <el-option :label="$t('uiAutomation.scheduledTask.taskTypes.testSuite')" value="TEST_SUITE" />
            <el-option :label="$t('uiAutomation.scheduledTask.taskTypes.testCase')" value="TEST_CASE" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="filters.trigger_type" :placeholder="$t('uiAutomation.scheduledTask.triggerType')" clearable>
            <el-option :label="$t('uiAutomation.scheduledTask.triggerTypes.cron')" value="CRON" />
            <el-option :label="$t('uiAutomation.scheduledTask.triggerTypes.interval')" value="INTERVAL" />
            <el-option :label="$t('uiAutomation.scheduledTask.triggerTypes.once')" value="ONCE" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="filters.status" :placeholder="$t('uiAutomation.scheduledTask.status')" clearable>
            <el-option :label="$t('uiAutomation.scheduledTask.statusTypes.active')" value="ACTIVE" />
            <el-option :label="$t('uiAutomation.scheduledTask.statusTypes.paused')" value="PAUSED" />
            <el-option :label="$t('uiAutomation.scheduledTask.statusTypes.completed')" value="COMPLETED" />
            <el-option :label="$t('uiAutomation.scheduledTask.statusTypes.failed')" value="FAILED" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button @click="resetFilters">{{ $t('uiAutomation.common.reset') }}</el-button>
          <el-button type="primary" @click="loadTasks">{{ $t('uiAutomation.common.search') }}</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 任务列表 -->
    <div class="task-list">
      <el-table :data="tasks" v-loading="loading">
        <el-table-column prop="name" :label="$t('uiAutomation.scheduledTask.taskName')" min-width="200" />
        <el-table-column prop="task_type" :label="$t('uiAutomation.scheduledTask.taskType')" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.task_type === 'TEST_SUITE' ? 'success' : 'primary'">
              {{ scope.row.task_type === 'TEST_SUITE' ? $t('uiAutomation.scheduledTask.taskTypes.testSuiteShort') : $t('uiAutomation.scheduledTask.taskTypes.testCaseShort') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="notification_type_display" :label="$t('uiAutomation.scheduledTask.notificationType')" width="130">
          <template #default="scope">
            <el-tag v-if="scope.row.notification_type_display && scope.row.notification_type_display !== '-'"
                    :type="getNotificationTypeTagType(scope.row.notification_type_display)"
                    size="small">
              {{ getNotificationTypeText(scope.row.notification_type) }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="trigger_type" :label="$t('uiAutomation.scheduledTask.triggerType')" width="120">
          <template #default="scope">
            <el-tag>
              {{ getTriggerTypeText(scope.row.trigger_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" :label="$t('uiAutomation.scheduledTask.status')" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'ACTIVE' ? 'success' : scope.row.status === 'PAUSED' ? 'warning' : 'info'">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="engine" :label="$t('uiAutomation.scheduledTask.executionEngine')" width="120">
          <template #default="scope">
            <el-tag size="small" type="info">
              {{ scope.row.engine === 'playwright' ? 'Playwright' : 'Selenium' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="browser" :label="$t('uiAutomation.scheduledTask.browser')" width="100">
          <template #default="scope">
            {{ scope.row.browser || 'chrome' }}
          </template>
        </el-table-column>
        <el-table-column prop="next_run_time" :label="$t('uiAutomation.scheduledTask.nextRunTime')" width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.next_run_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="last_run_time" :label="$t('uiAutomation.scheduledTask.lastRunTime')" width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.last_run_time) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('uiAutomation.common.operation')" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="runTaskNow(scope.row)" :loading="scope.row.running">
              {{ $t('uiAutomation.scheduledTask.runNow') }}
            </el-button>
            <el-dropdown @command="(command) => handleTaskAction(command, scope.row)">
              <el-button size="small">
                {{ $t('uiAutomation.scheduledTask.more') }}<el-icon><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="edit">{{ $t('uiAutomation.scheduledTask.actions.edit') }}</el-dropdown-item>
                  <el-dropdown-item command="pause" v-if="scope.row.status === 'ACTIVE'">{{ $t('uiAutomation.scheduledTask.actions.pause') }}</el-dropdown-item>
                  <el-dropdown-item command="resume" v-if="scope.row.status === 'PAUSED'">{{ $t('uiAutomation.scheduledTask.actions.resume') }}</el-dropdown-item>
                  <el-dropdown-item command="delete" divided>{{ $t('uiAutomation.scheduledTask.actions.delete') }}</el-dropdown-item>
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
      :title="editingTask ? $t('uiAutomation.scheduledTask.editTask') : $t('uiAutomation.scheduledTask.createTask')"
      width="800px"
      @close="resetTaskForm"
    >
      <el-form :model="taskForm" label-width="120px">
        <el-form-item :label="$t('uiAutomation.scheduledTask.taskName')" required>
          <el-input v-model="taskForm.name" :placeholder="$t('uiAutomation.scheduledTask.taskNamePlaceholder')" />
        </el-form-item>

        <el-form-item :label="$t('uiAutomation.scheduledTask.taskDesc')">
          <el-input v-model="taskForm.description" type="textarea" :placeholder="$t('uiAutomation.scheduledTask.taskDescPlaceholder')" />
        </el-form-item>

        <el-form-item :label="$t('uiAutomation.scheduledTask.relatedProject')" required>
          <el-select v-model="taskForm.project" :placeholder="$t('uiAutomation.scheduledTask.selectProject')" @change="onProjectChange">
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('uiAutomation.scheduledTask.taskType')" required>
          <el-radio-group v-model="taskForm.task_type" @change="onTaskTypeChange">
            <el-radio value="TEST_SUITE">{{ $t('uiAutomation.scheduledTask.taskTypes.testSuite') }}</el-radio>
            <el-radio value="TEST_CASE">{{ $t('uiAutomation.scheduledTask.taskTypes.testCase') }}</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 根据任务类型显示不同配置 - 移到任务类型下面 -->
        <el-form-item v-if="taskForm.task_type === 'TEST_SUITE'" :label="$t('uiAutomation.scheduledTask.testSuite')" required>
          <el-select v-model="taskForm.test_suite" :placeholder="$t('uiAutomation.scheduledTask.selectSuite')">
            <el-option
              v-for="suite in testSuites"
              :key="suite.id"
              :label="suite.name"
              :value="suite.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item v-if="taskForm.task_type === 'TEST_CASE'" :label="$t('uiAutomation.scheduledTask.testCase')" required>
          <el-select
            v-model="taskForm.test_cases"
            multiple
            filterable
            :placeholder="$t('uiAutomation.scheduledTask.selectTestCase')"
          >
            <el-option
              v-for="testCase in testCases"
              :key="testCase.id"
              :label="testCase.name"
              :value="testCase.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('uiAutomation.scheduledTask.triggerType')" required>
          <el-radio-group v-model="taskForm.trigger_type">
            <el-radio value="CRON">{{ $t('uiAutomation.scheduledTask.triggerTypes.cron') }}</el-radio>
            <el-radio value="INTERVAL">{{ $t('uiAutomation.scheduledTask.triggerTypes.interval') }}</el-radio>
            <el-radio value="ONCE">{{ $t('uiAutomation.scheduledTask.triggerTypes.once') }}</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 根据触发器类型显示不同配置 -->
        <el-form-item v-if="taskForm.trigger_type === 'CRON'" :label="$t('uiAutomation.scheduledTask.cronExpression')" required>
          <el-input v-model="taskForm.cron_expression" :placeholder="$t('uiAutomation.scheduledTask.cronPlaceholder')" />
          <div class="cron-help">
            <el-tooltip raw-content placement="top">
              <template #content>
                <div style="line-height: 1.6; text-align: left;">
                  <div>{{ $t('uiAutomation.scheduledTask.cronHelp.format') }}</div>
                  <div>{{ $t('uiAutomation.scheduledTask.cronHelp.minute') }}</div>
                  <div>{{ $t('uiAutomation.scheduledTask.cronHelp.hour') }}</div>
                  <div>{{ $t('uiAutomation.scheduledTask.cronHelp.day') }}</div>
                  <div>{{ $t('uiAutomation.scheduledTask.cronHelp.month') }}</div>
                  <div>{{ $t('uiAutomation.scheduledTask.cronHelp.week') }}</div>
                  <div style="margin-top: 8px;">{{ $t('uiAutomation.scheduledTask.cronHelp.examples') }}</div>
                  <div>{{ $t('uiAutomation.scheduledTask.cronHelp.everyDay') }}</div>
                  <div>{{ $t('uiAutomation.scheduledTask.cronHelp.everyHour') }}</div>
                  <div>{{ $t('uiAutomation.scheduledTask.cronHelp.everyMonday') }}</div>
                  <div>{{ $t('uiAutomation.scheduledTask.cronHelp.everyMonth') }}</div>
                </div>
              </template>
              <span style="cursor: pointer; color: #409EFF;">{{ $t('uiAutomation.scheduledTask.cronHelpLink') }}</span>
            </el-tooltip>
          </div>
        </el-form-item>

        <el-form-item v-if="taskForm.trigger_type === 'INTERVAL'" :label="$t('uiAutomation.scheduledTask.intervalTime')" required>
          <el-input-number v-model="taskForm.interval_seconds" :min="60" :step="60" />
          <span class="unit">{{ $t('uiAutomation.scheduledTask.intervalUnit') }}</span>
        </el-form-item>

        <el-form-item v-if="taskForm.trigger_type === 'ONCE'" :label="$t('uiAutomation.scheduledTask.executeTime')" required>
          <el-date-picker
            v-model="taskForm.execute_at"
            type="datetime"
            :placeholder="$t('uiAutomation.scheduledTask.selectExecuteTime')"
          />
        </el-form-item>

        <el-form-item :label="$t('uiAutomation.scheduledTask.executionEngine')" required>
          <el-radio-group v-model="taskForm.engine">
            <el-radio value="playwright">Playwright</el-radio>
            <el-radio value="selenium">Selenium</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item :label="$t('uiAutomation.scheduledTask.browserType')" required>
          <el-select v-model="taskForm.browser" :placeholder="$t('uiAutomation.scheduledTask.selectBrowser')">
            <el-option label="Chrome" value="chrome" />
            <el-option label="Firefox" value="firefox" />
            <el-option label="Edge" value="edge" />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('uiAutomation.scheduledTask.runMode')">
          <el-checkbox v-model="taskForm.headless">{{ $t('uiAutomation.scheduledTask.headlessMode') }}</el-checkbox>
        </el-form-item>

        <el-form-item :label="$t('uiAutomation.scheduledTask.notificationSettings')">
          <el-checkbox v-model="taskForm.notify_on_success">{{ $t('uiAutomation.scheduledTask.notifyOnSuccess') }}</el-checkbox>
          <el-checkbox v-model="taskForm.notify_on_failure">{{ $t('uiAutomation.scheduledTask.notifyOnFailure') }}</el-checkbox>
        </el-form-item>

        <el-form-item v-if="taskForm.notify_on_success || taskForm.notify_on_failure" :label="$t('uiAutomation.scheduledTask.notificationType')">
          <el-select v-model="taskForm.notification_type" :placeholder="$t('uiAutomation.scheduledTask.selectNotificationType')">
            <el-option :label="$t('uiAutomation.scheduledTask.notificationTypes.email')" value="email" />
            <el-option :label="$t('uiAutomation.scheduledTask.notificationTypes.webhook')" value="webhook" />
            <el-option :label="$t('uiAutomation.scheduledTask.notificationTypes.both')" value="both" />
          </el-select>
        </el-form-item>

        <el-form-item v-if="(taskForm.notify_on_success || taskForm.notify_on_failure) && (taskForm.notification_type === 'email' || taskForm.notification_type === 'both')" :label="$t('uiAutomation.scheduledTask.notifyEmails')">
          <el-select
            v-model="taskForm.notify_emails"
            multiple
            filterable
            :placeholder="$t('uiAutomation.scheduledTask.selectNotifyEmails')"
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
        <el-button @click="showCreateDialog = false">{{ $t('uiAutomation.common.cancel') }}</el-button>
        <el-button type="primary" @click="submitTaskForm" :loading="submitting">
          {{ editingTask ? $t('uiAutomation.messages.success.update') : $t('uiAutomation.messages.success.create') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, ArrowDown } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import {
  getScheduledTasks,
  createScheduledTask,
  updateScheduledTask,
  deleteScheduledTask,
  runScheduledTask,
  pauseScheduledTask,
  resumeScheduledTask,
  getUiProjects,
  getTestSuites,
  getTestCases,
  getUiUsers
} from '@/api/ui_automation.js'

const { t, locale } = useI18n()

// 数据状态
const tasks = ref([])
const projects = ref([])
const testSuites = ref([])
const testCases = ref([])
const users = ref([])
const loading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
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
  project: '',
  task_type: 'TEST_SUITE',
  trigger_type: 'CRON',
  cron_expression: '0 0 * * *',
  interval_seconds: 3600,
  execute_at: '',
  test_suite: '',
  test_cases: [],
  engine: 'playwright',
  browser: 'chrome',
  headless: false,
  notify_on_success: false,
  notify_on_failure: false,
  notification_type: '',
  notify_emails: []
})

// 获取触发器类型文本
const getTriggerTypeText = (type) => {
  const typeMap = {
    'CRON': t('uiAutomation.scheduledTask.triggerTypes.cronShort'),
    'INTERVAL': t('uiAutomation.scheduledTask.triggerTypes.intervalShort'),
    'ONCE': t('uiAutomation.scheduledTask.triggerTypes.onceShort')
  }
  return typeMap[type] || type
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    'ACTIVE': t('uiAutomation.scheduledTask.statusTypes.active'),
    'PAUSED': t('uiAutomation.scheduledTask.statusTypes.paused'),
    'COMPLETED': t('uiAutomation.scheduledTask.statusTypes.completedShort'),
    'FAILED': t('uiAutomation.scheduledTask.statusTypes.failed')
  }
  return statusMap[status] || status
}

// 获取通知类型文本
const getNotificationTypeText = (type) => {
  const typeMap = {
    'email': t('uiAutomation.scheduledTask.notificationTypes.email'),
    'webhook': t('uiAutomation.scheduledTask.notificationTypes.webhook'),
    'both': t('uiAutomation.scheduledTask.notificationTypes.both')
  }
  return typeMap[type] || type
}

// 生命周期
onMounted(() => {
  loadTasks()
  loadProjects()
  loadUsers()
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
    ElMessage.error(t('uiAutomation.scheduledTask.messages.loadFailed'))
  } finally {
    loading.value = false
  }
}

// 加载项目列表
const loadProjects = async () => {
  try {
    const response = await getUiProjects()
    projects.value = response.data.results
  } catch (error) {
    console.error('Load projects failed:', error)
  }
}

// 加载用户列表
const loadUsers = async () => {
  try {
    const response = await getUiUsers()
    // 处理分页数据结构
    const usersData = response.data.results || response.data
    users.value = usersData.map(user => ({
      ...user,
      display_name: user.first_name ? `${user.first_name}（${user.email}）` : `${user.username}（${user.email}）`
    }))
  } catch (error) {
    console.error('Load users failed:', error)
  }
}

// 项目变化时加载对应的套件和用例
const onProjectChange = async (projectId) => {
  if (!projectId) return

  try {
    // 加载测试套件
    const suitesResponse = await getTestSuites({ project: projectId })
    testSuites.value = suitesResponse.data.results

    // 加载测试用例
    const casesResponse = await getTestCases({ project: projectId })
    testCases.value = casesResponse.data.results
  } catch (error) {
    console.error('Load project data failed:', error)
  }
}

// 任务类型变化
const onTaskTypeChange = () => {
  taskForm.test_suite = ''
  taskForm.test_cases = []
}

// 新建按钮点击
const handleCreateClick = () => {
  editingTask.value = null
  resetTaskForm()
  showCreateDialog.value = true
}

// 重置表单
const resetTaskForm = () => {
  Object.assign(taskForm, {
    name: '',
    description: '',
    project: '',
    task_type: 'TEST_SUITE',
    trigger_type: 'CRON',
    cron_expression: '0 0 * * *',
    interval_seconds: 3600,
    execute_at: '',
    test_suite: '',
    test_cases: [],
    engine: 'playwright',
    browser: 'chrome',
    headless: false,
    notify_on_success: false,
    notify_on_failure: false,
    notification_type: '',
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
    const submitData = {
      name: taskForm.name,
      description: taskForm.description,
      project: taskForm.project,
      task_type: taskForm.task_type,
      trigger_type: taskForm.trigger_type,
      engine: taskForm.engine,
      browser: taskForm.browser,
      headless: taskForm.headless,
      notify_on_success: taskForm.notify_on_success,
      notify_on_failure: taskForm.notify_on_failure
    }

    // 添加通知相关字段
    if (taskForm.notify_on_success || taskForm.notify_on_failure) {
      if (taskForm.notification_type) {
        submitData.notification_type = taskForm.notification_type
      }
      if (taskForm.notify_emails && taskForm.notify_emails.length > 0) {
        submitData.notify_emails = taskForm.notify_emails
      }
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
    } else if (taskForm.task_type === 'TEST_CASE') {
      submitData.test_cases = taskForm.test_cases
    }

    if (editingTask.value) {
      await updateScheduledTask(editingTask.value.id, submitData)
      ElMessage.success(t('uiAutomation.scheduledTask.messages.updateSuccess'))
    } else {
      await createScheduledTask(submitData)
      ElMessage.success(t('uiAutomation.scheduledTask.messages.createSuccess'))
    }
    showCreateDialog.value = false
    loadTasks()
  } catch (error) {
    console.error('Task operation failed:', error)
    ElMessage.error(error.response?.data?.error ||
                   error.response?.data?.detail ||
                   (editingTask.value ? t('uiAutomation.scheduledTask.messages.updateFailed') : t('uiAutomation.scheduledTask.messages.createFailed')))
  } finally {
    submitting.value = false
  }
}

// 立即执行任务
const runTaskNow = async (task) => {
  try {
    task.running = true
    await runScheduledTask(task.id)
    ElMessage.success(t('uiAutomation.scheduledTask.messages.runSuccess'))
    setTimeout(() => {
      loadTasks()
    }, 2000)
  } catch (error) {
    ElMessage.error(t('uiAutomation.scheduledTask.messages.runFailed'))
  } finally {
    task.running = false
  }
}

// 格式化日期时间
const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  const localeStr = locale.value === 'en' ? 'en-US' : 'zh-CN'
  return date.toLocaleString(localeStr, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).replace(/\//g, '-')
}

// 获取通知类型标签类型
const getNotificationTypeTagType = (typeDisplay) => {
  const typeMap = {
    '邮箱通知': '',
    'Email Notification': '',
    'Webhook机器人': 'primary',
    'Webhook Robot': 'primary',
    '两者都发送': 'warning',
    'Both': 'warning'
  }
  return typeMap[typeDisplay] || 'info'
}

// 处理任务操作
const handleTaskAction = (command, task) => {
  switch (command) {
    case 'pause':
      pauseTask(task)
      break
    case 'resume':
      resumeTask(task)
      break
    case 'edit':
      editTask(task)
      break
    case 'delete':
      deleteTask(task)
      break
  }
}

// 编辑任务
const editTask = async (task) => {
  editingTask.value = task
  Object.assign(taskForm, {
    name: task.name,
    description: task.description,
    project: task.project,
    task_type: task.task_type,
    trigger_type: task.trigger_type,
    cron_expression: task.cron_expression,
    interval_seconds: task.interval_seconds,
    execute_at: task.execute_at,
    test_suite: task.test_suite || '',
    test_cases: task.test_cases || [],
    engine: task.engine || 'playwright',
    browser: task.browser || 'chrome',
    headless: task.headless || false,
    notify_on_success: task.notify_on_success || false,
    notify_on_failure: task.notify_on_failure || false,
    notification_type: task.notification_type || '',
    notify_emails: task.notify_emails || []
  })

  // 加载项目相关数据
  if (task.project) {
    await onProjectChange(task.project)
  }

  showCreateDialog.value = true
}

// 暂停任务
const pauseTask = async (task) => {
  try {
    await pauseScheduledTask(task.id)
    ElMessage.success(t('uiAutomation.scheduledTask.messages.pauseSuccess'))
    loadTasks()
  } catch (error) {
    console.error('Pause task failed:', error)
    ElMessage.error(t('uiAutomation.scheduledTask.messages.pauseFailed'))
  }
}

// 恢复任务
const resumeTask = async (task) => {
  try {
    await resumeScheduledTask(task.id)
    ElMessage.success(t('uiAutomation.scheduledTask.messages.resumeSuccess'))
    loadTasks()
  } catch (error) {
    ElMessage.error(t('uiAutomation.scheduledTask.messages.resumeFailed'))
  }
}

// 删除任务
const deleteTask = async (task) => {
  try {
    await ElMessageBox.confirm(t('uiAutomation.scheduledTask.messages.deleteConfirm'), t('uiAutomation.scheduledTask.messages.deleteConfirmTitle'), {
      confirmButtonText: t('uiAutomation.common.confirm'),
      cancelButtonText: t('uiAutomation.common.cancel'),
      type: 'warning'
    })
    await deleteScheduledTask(task.id)
    ElMessage.success(t('uiAutomation.scheduledTask.messages.deleteSuccess'))
    loadTasks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('uiAutomation.scheduledTask.messages.deleteFailed'))
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
  margin-bottom: 20px;
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
