<template>
  <div class="notification-management">
    <!-- 顶部标题 -->
    <div class="header">
      <h3>{{ $t('apiTesting.notification.title') }}</h3>
    </div>

    <!-- Tab页 -->
    <el-tabs v-model="activeTab" class="notification-tabs">
      <!-- 通知列表Tab -->
      <el-tab-pane :label="$t('apiTesting.notification.notificationList')" name="list">
        <div class="tab-content">
          <!-- 筛选条件 -->
          <div class="filters">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-input
                  v-model="filters.task_name"
                  :placeholder="$t('apiTesting.notification.searchTaskName')"
                  clearable
                />
              </el-col>
              <el-col :span="6">
                <el-date-picker
                  v-model="filters.date_range"
                  type="daterange"
                  :range-separator="$t('apiTesting.notification.to')"
                  :start-placeholder="$t('apiTesting.notification.startDate')"
                  :end-placeholder="$t('apiTesting.notification.endDate')"
                  value-format="YYYY-MM-DD"
                />
              </el-col>
              <el-col :span="6">
                <el-button type="primary" @click="loadNotifications">
                  <el-icon><Search /></el-icon>
                  {{ $t('apiTesting.common.search') }}
                </el-button>
                <el-button @click="resetFilters">
                  <el-icon><Refresh /></el-icon>
                  {{ $t('apiTesting.common.reset') }}
                </el-button>
              </el-col>
            </el-row>
          </div>

          <!-- 通知列表 -->
          <el-table
            :data="notifications"
            v-loading="loading"
            style="width: 100%"
          >
            <el-table-column prop="task_name" :label="$t('apiTesting.notification.taskName')" min-width="120" />
            <el-table-column prop="notify_time" :label="$t('apiTesting.notification.notifyTime')" min-width="140">
              <template #default="{ row }">
                {{ formatDateTime(row.notify_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="recipients" :label="$t('apiTesting.notification.recipients')" min-width="120">
              <template #default="{ row }">
                <span v-if="row.notify_type === 'EMAIL'">
                  {{ row.recipients.join(', ') }}
                </span>
                <span v-else-if="row.notify_type === 'WEBHOOK'">
                  {{ $t('apiTesting.notification.webhookBot') }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="status" :label="$t('apiTesting.common.status')" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'SUCCESS' ? 'success' : 'danger'">
                  {{ row.status === 'SUCCESS' ? $t('apiTesting.common.success') : $t('apiTesting.common.failed') }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="$t('apiTesting.common.operation')" width="100">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  size="small"
                  @click="showNotificationDetail(row)"
                >
                  {{ $t('apiTesting.notification.viewDetail') }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 分页 -->
          <div class="pagination">
            <el-pagination
              v-model:current-page="pagination.current"
              v-model:page-size="pagination.size"
              :total="pagination.total"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="loadNotifications"
              @current-change="loadNotifications"
            />
          </div>
        </div>
      </el-tab-pane>

      <!-- 通知配置Tab -->
      <el-tab-pane :label="$t('apiTesting.notification.notificationConfig')" name="config">
        <div class="tab-content">
          <!-- 邮箱配置 -->
          <div class="config-section">
            <h4>{{ $t('apiTesting.notification.emailConfig') }}</h4>
            <el-card>
              <div class="config-form">
                <el-form :model="emailConfig" label-width="120px">
                  <el-form-item :label="$t('apiTesting.notification.senderEmail')" required>
                    <el-input
                      v-model="emailConfig.sender_email"
                      :placeholder="$t('apiTesting.notification.inputSenderEmail')"
                    />
                  </el-form-item>
                  <el-form-item :label="$t('apiTesting.notification.smtpServer')" required>
                    <el-input
                      v-model="emailConfig.smtp_host"
                      :placeholder="$t('apiTesting.notification.smtpServerPlaceholder')"
                    />
                  </el-form-item>
                  <el-form-item :label="$t('apiTesting.notification.smtpPort')" required>
                    <el-input-number
                      v-model="emailConfig.smtp_port"
                      :min="1"
                      :max="65535"
                    />
                  </el-form-item>
                  <el-form-item :label="$t('apiTesting.notification.authCode')" required>
                    <el-input
                      v-model="emailConfig.smtp_password"
                      type="password"
                      :placeholder="$t('apiTesting.notification.inputAuthCode')"
                    />
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="saveEmailConfig">
                      {{ $t('apiTesting.notification.saveConfig') }}
                    </el-button>
                    <el-button @click="testEmailConfig">
                      {{ $t('apiTesting.notification.testConnection') }}
                    </el-button>
                  </el-form-item>
                </el-form>
              </div>
            </el-card>
          </div>

          <!-- 收件人管理 -->
          <div class="config-section">
            <h4>{{ $t('apiTesting.notification.recipientManagement') }}</h4>
            <el-card>
              <div class="recipient-header">
                <el-button type="primary" @click="showAddRecipientDialog">
                  <el-icon><Plus /></el-icon>
                  {{ $t('apiTesting.notification.addRecipient') }}
                </el-button>
              </div>
              <el-table :data="recipients" style="width: 100%">
                <el-table-column prop="name" :label="$t('apiTesting.notification.recipientName')" width="120" />
                <el-table-column prop="email" :label="$t('apiTesting.notification.emailAddress')" min-width="200" />
                <el-table-column :label="$t('apiTesting.common.operation')" width="120">
                  <template #default="{ row }">
                    <el-button
                      type="danger"
                      size="small"
                      @click="deleteRecipient(row)"
                    >
                      {{ $t('apiTesting.common.delete') }}
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </div>

          <!-- Webhook配置 -->
          <div class="config-section">
            <h4>{{ $t('apiTesting.notification.webhookConfig') }}</h4>
            <el-card>
              <div class="webhook-header">
                <el-button type="primary" @click="showAddWebhookDialog">
                  <el-icon><Plus /></el-icon>
                  {{ $t('apiTesting.notification.addWebhook') }}
                </el-button>
              </div>
              <el-table :data="webhooks" style="width: 100%">
                <el-table-column prop="name" :label="$t('apiTesting.common.name')" width="120" />
                <el-table-column prop="platform" :label="$t('apiTesting.notification.platform')" width="100">
                  <template #default="{ row }">
                    <el-tag :type="getPlatformTagType(row.platform)">
                      {{ getPlatformName(row.platform) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="webhook_url" :label="$t('apiTesting.notification.webhookAddress')" min-width="200" />
                <el-table-column prop="enabled" :label="$t('apiTesting.common.status')" width="80">
                  <template #default="{ row }">
                    <el-switch
                      v-model="row.enabled"
                      @change="toggleWebhookStatus(row)"
                    />
                  </template>
                </el-table-column>
                <el-table-column :label="$t('apiTesting.common.operation')" width="120">
                  <template #default="{ row }">
                    <el-button
                      type="danger"
                      size="small"
                      @click="deleteWebhook(row)"
                    >
                      {{ $t('apiTesting.common.delete') }}
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 通知详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="$t('apiTesting.notification.notificationDetail')"
      width="600px"
    >
      <div v-if="currentNotification" class="notification-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item :label="$t('apiTesting.notification.taskName')">
            {{ currentNotification.task_name }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('apiTesting.notification.notifyTime')">
            {{ formatDateTime(currentNotification.notify_time) }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('apiTesting.notification.notificationType')">
            {{ currentNotification.notify_type === 'EMAIL' ? $t('apiTesting.notification.emailNotification') : $t('apiTesting.notification.webhookNotification') }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('apiTesting.notification.recipients')">
            <span v-if="currentNotification.notify_type === 'EMAIL'">
              {{ currentNotification.recipients.join(', ') }}
            </span>
            <span v-else>
              {{ $t('apiTesting.notification.webhookBot') }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('apiTesting.common.status')">
            <el-tag :type="currentNotification.status === 'SUCCESS' ? 'success' : 'danger'">
              {{ currentNotification.status === 'SUCCESS' ? $t('apiTesting.common.success') : $t('apiTesting.common.failed') }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('apiTesting.notification.content')">
            <pre class="content-pre">{{ currentNotification.content }}</pre>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('apiTesting.scheduledTask.errorMessage')" v-if="currentNotification.error_message">
            {{ currentNotification.error_message }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- 新增收件人对话框 -->
    <el-dialog
      v-model="showRecipientDialog"
      :title="$t('apiTesting.notification.addRecipient')"
      width="400px"
    >
      <el-form :model="newRecipient" label-width="80px">
        <el-form-item :label="$t('apiTesting.notification.recipientName')" required>
          <el-input v-model="newRecipient.name" :placeholder="$t('apiTesting.notification.inputName')" />
        </el-form-item>
        <el-form-item :label="$t('apiTesting.notification.emailAddress')" required>
          <el-input v-model="newRecipient.email" :placeholder="$t('apiTesting.notification.inputEmail')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRecipientDialog = false">{{ $t('apiTesting.common.cancel') }}</el-button>
        <el-button type="primary" @click="addRecipient">{{ $t('apiTesting.common.confirm') }}</el-button>
      </template>
    </el-dialog>

    <!-- 新增Webhook对话框 -->
    <el-dialog
      v-model="showWebhookDialog"
      :title="$t('apiTesting.notification.addWebhook')"
      width="500px"
    >
      <el-form :model="newWebhook" label-width="100px">
        <el-form-item :label="$t('apiTesting.common.name')" required>
          <el-input v-model="newWebhook.name" :placeholder="$t('apiTesting.notification.inputWebhookName')" />
        </el-form-item>
        <el-form-item :label="$t('apiTesting.notification.platform')" required>
          <el-select v-model="newWebhook.platform" :placeholder="$t('apiTesting.notification.selectPlatform')">
            <el-option :label="$t('apiTesting.notification.platforms.feishu')" value="FEISHU" />
            <el-option :label="$t('apiTesting.notification.platforms.wechatWork')" value="WECHAT_WORK" />
            <el-option :label="$t('apiTesting.notification.platforms.dingtalk')" value="DINGTALK" />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('apiTesting.notification.webhookAddress')" required>
          <el-input
            v-model="newWebhook.webhook_url"
            :placeholder="$t('apiTesting.notification.inputWebhookAddress')"
            type="textarea"
            :rows="2"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showWebhookDialog = false">{{ $t('apiTesting.common.cancel') }}</el-button>
        <el-button type="primary" @click="addWebhook">{{ $t('apiTesting.common.confirm') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'

const { t } = useI18n()
const activeTab = ref('list')
const loading = ref(false)
const showDetailDialog = ref(false)
const showRecipientDialog = ref(false)
const showWebhookDialog = ref(false)

// 筛选条件
const filters = reactive({
  task_name: '',
  date_range: []
})

// 分页配置
const pagination = reactive({
  current: 1,
  size: 10,
  total: 0
})

// 通知列表数据
const notifications = ref([])
const currentNotification = ref(null)

// 邮箱配置
const emailConfig = reactive({
  sender_email: '',
  smtp_host: '',
  smtp_port: 465,
  smtp_password: ''
})

// 收件人列表
const recipients = ref([])
const newRecipient = reactive({
  name: '',
  email: ''
})

// Webhook列表
const webhooks = ref([])
const newWebhook = reactive({
  name: '',
  platform: '',
  webhook_url: ''
})

// 加载通知列表
const loadNotifications = async () => {
  loading.value = true
  try {
    // 模拟数据
    notifications.value = [
      {
        id: 1,
        task_name: '每日API测试',
        notify_time: new Date().toISOString(),
        notify_type: 'EMAIL',
        recipients: ['user1@example.com', 'user2@example.com'],
        status: 'SUCCESS',
        content: '测试任务执行完成，共执行10个接口，成功8个，失败2个',
        error_message: ''
      },
      {
        id: 2,
        task_name: '每周数据同步',
        notify_time: new Date(Date.now() - 86400000).toISOString(),
        notify_type: 'WEBHOOK',
        recipients: [],
        status: 'FAILED',
        content: '数据同步任务执行失败',
        error_message: '网络连接超时'
      }
    ]
    pagination.total = 2
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.loadNotifications'))
  } finally {
    loading.value = false
  }
}

// 重置筛选条件
const resetFilters = () => {
  filters.task_name = ''
  filters.date_range = []
  loadNotifications()
}

// 显示通知详情
const showNotificationDetail = (notification) => {
  currentNotification.value = notification
  showDetailDialog.value = true
}

// 格式化日期时间
const formatDateTime = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 保存邮箱配置
const saveEmailConfig = async () => {
  try {
    ElMessage.success(t('apiTesting.messages.success.emailConfigSaved'))
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.emailConfigFailed'))
  }
}

// 测试邮箱配置
const testEmailConfig = async () => {
  try {
    ElMessage.success(t('apiTesting.messages.success.emailTestSuccess'))
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.emailTestFailed'))
  }
}

// 显示新增收件人对话框
const showAddRecipientDialog = () => {
  newRecipient.name = ''
  newRecipient.email = ''
  showRecipientDialog.value = true
}

// 添加收件人
const addRecipient = async () => {
  if (!newRecipient.name || !newRecipient.email) {
    ElMessage.warning(t('apiTesting.notification.fillCompleteInfo'))
    return
  }

  recipients.value.push({ ...newRecipient })
  showRecipientDialog.value = false
  ElMessage.success(t('apiTesting.messages.success.recipientAdded'))
}

// 删除收件人
const deleteRecipient = async (recipient) => {
  try {
    await ElMessageBox.confirm(
      t('apiTesting.notification.confirmDeleteRecipient'),
      t('apiTesting.common.tip'),
      {
        confirmButtonText: t('apiTesting.common.confirm'),
        cancelButtonText: t('apiTesting.common.cancel'),
        type: 'warning'
      }
    )

    const index = recipients.value.findIndex(r => r.email === recipient.email)
    if (index !== -1) {
      recipients.value.splice(index, 1)
      ElMessage.success(t('apiTesting.messages.success.recipientDeleted'))
    }
  } catch (error) {
    // 用户取消删除
  }
}

// 显示新增Webhook对话框
const showAddWebhookDialog = () => {
  newWebhook.name = ''
  newWebhook.platform = ''
  newWebhook.webhook_url = ''
  showWebhookDialog.value = true
}

// 添加Webhook
const addWebhook = async () => {
  if (!newWebhook.name || !newWebhook.platform || !newWebhook.webhook_url) {
    ElMessage.warning(t('apiTesting.notification.fillCompleteInfo'))
    return
  }

  webhooks.value.push({
    ...newWebhook,
    enabled: true
  })
  showWebhookDialog.value = false
  ElMessage.success(t('apiTesting.messages.success.webhookAdded'))
}

// 删除Webhook
const deleteWebhook = async (webhook) => {
  try {
    await ElMessageBox.confirm(
      t('apiTesting.notification.confirmDeleteWebhook'),
      t('apiTesting.common.tip'),
      {
        confirmButtonText: t('apiTesting.common.confirm'),
        cancelButtonText: t('apiTesting.common.cancel'),
        type: 'warning'
      }
    )

    const index = webhooks.value.findIndex(w => w.webhook_url === webhook.webhook_url)
    if (index !== -1) {
      webhooks.value.splice(index, 1)
      ElMessage.success(t('apiTesting.messages.success.webhookDeleted'))
    }
  } catch (error) {
    // 用户取消删除
  }
}

// 切换Webhook状态
const toggleWebhookStatus = async (webhook) => {
  try {
    ElMessage.success(webhook.enabled ? t('apiTesting.notification.webhookEnabled') : t('apiTesting.notification.webhookDisabled'))
  } catch (error) {
    webhook.enabled = !webhook.enabled
    ElMessage.error(t('apiTesting.messages.error.operationFailed'))
  }
}

// 获取平台名称
const getPlatformName = (platform) => {
  const platformKey = {
    FEISHU: 'feishu',
    WECHAT_WORK: 'wechatWork',
    DINGTALK: 'dingtalk'
  }[platform]
  return platformKey ? t(`apiTesting.notification.platforms.${platformKey}`) : platform
}

// 获取平台标签类型
const getPlatformTagType = (platform) => {
  const typeMap = {
    FEISHU: 'success',
    WECHAT_WORK: 'primary',
    DINGTALK: 'warning'
  }
  return typeMap[platform] || 'info'
}

// 初始化加载数据
onMounted(() => {
  loadNotifications()
  
  // 加载模拟数据
  recipients.value = [
    { name: '张三', email: 'zhangsan@example.com' },
    { name: '李四', email: 'lisi@example.com' }
  ]
  
  webhooks.value = [
    {
      name: '飞书通知',
      platform: 'FEISHU',
      webhook_url: 'https://open.feishu.cn/open-apis/bot/v2/hook/xxx',
      enabled: true
    },
    {
      name: '企业微信通知',
      platform: 'WECHAT_WORK',
      webhook_url: 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx',
      enabled: true
    }
  ]
})
</script>

<style scoped>
.notification-management {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100%;
}

.header {
  margin-bottom: 20px;
}

.header h3 {
  margin: 0;
  color: #303133;
}

.notification-tabs {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.tab-content {
  padding: 20px;
}

.filters {
  margin-bottom: 20px;
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.config-section {
  margin-bottom: 24px;
}

.config-section h4 {
  margin: 0 0 16px 0;
  color: #303133;
  font-weight: 600;
}

.recipient-header,
.webhook-header {
  margin-bottom: 16px;
}

.notification-detail .content-pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  line-height: 1.5;
}
</style>