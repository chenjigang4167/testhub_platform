<template>
  <div class="notification-logs-container">
    <!-- 页面操作栏 -->
    <div class="page-actions">
      <el-row :gutter="20" class="filter-row">
        <el-col :span="6">
          <el-input
              v-model="searchForm.taskName"
              :placeholder="$t('notification.logs.searchTaskName')"
              clearable
              @clear="handleSearch"
              @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon>
                <Search/>
              </el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="6">
          <el-date-picker
              v-model="searchForm.dateRange"
              type="daterange"
              :range-separator="$t('notification.logs.rangeSeparator')"
              :start-placeholder="$t('notification.logs.startDate')"
              :end-placeholder="$t('notification.logs.endDate')"
              value-format="YYYY-MM-DD"
              @change="handleSearch"
          />
        </el-col>
        <el-col :span="6">
          <el-select
              v-model="searchForm.status"
              :placeholder="$t('notification.logs.notificationStatus')"
              clearable
              @change="handleSearch"
          >
            <el-option :label="$t('notification.logs.statusOptions.all')" value=""/>
            <el-option :label="$t('notification.logs.statusOptions.success')" value="SUCCESS"/>
            <el-option :label="$t('notification.logs.statusOptions.failed')" value="FAILED"/>
            <el-option :label="$t('notification.logs.statusOptions.retrying')" value="RETRYING"/>
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="handleSearch">
            <el-icon>
              <Search/>
            </el-icon>
            {{ $t('notification.logs.search') }}
          </el-button>
          <el-button @click="handleReset">
            {{ $t('notification.logs.reset') }}
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 通知列表 -->
    <div class="logs-table-container">
      <el-table
          :data="logsData"
          v-loading="loading"
          :element-loading-text="$t('notification.logs.loading')"
          stripe
          style="width: 100%"
          @sort-change="handleSortChange"
      >
        <el-table-column
            prop="task_name"
            :label="$t('notification.logs.columns.taskName')"
            min-width="150"
            sortable="custom"
        />
        <el-table-column
            prop="task_type_display"
            :label="$t('notification.logs.columns.taskType')"
            min-width="100"
        >
          <template #default="{ row }">
            <el-tag
                type="info"
                size="small"
            >
              {{ row.task_type_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
            prop="notification_type_display"
            :label="$t('notification.logs.columns.notificationType')"
            min-width="120"
        >
          <template #default="{ row }">
            <el-tag
                :type="getNotificationTypeTagType(row.notification_type_display)"
                size="small"
            >
              {{ row.notification_type_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
            prop="notification_target_display"
            :label="$t('notification.logs.columns.notificationTarget')"
            min-width="150"
        >
          <template #default="{ row }">
            <span>{{ row.notification_target_display || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column
            prop="created_at"
            :label="$t('notification.logs.columns.notificationTime')"
            min-width="180"
            sortable="custom"
        >
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column
            prop="status_display"
            :label="$t('notification.logs.columns.status')"
            min-width="100"
            sortable="custom"
        >
          <template #default="{ row }">
            <el-tag
                :type="getStatusTagType(row.status_display)"
                size="small"
            >
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
            :label="$t('notification.logs.columns.operation')"
            fixed="right"
            width="120"
        >
          <template #default="{ row }">
            <el-button
                type="primary"
                link
                size="small"
                @click="viewDetail(row)"
            >
              {{ $t('notification.logs.viewDetail') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 详情弹窗 -->
    <el-dialog
        v-model="detailDialogVisible"
        :title="$t('notification.logs.detailDialog.title')"
        width="600px"
        :before-close="handleDetailDialogClose"
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        :modal="true"
        :destroy-on-close="false"
    >
      <el-form
          v-if="selectedLog"
          label-position="top"
          class="notification-detail-form"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item :label="$t('notification.logs.detailDialog.taskName')">
              <span>{{ selectedLog.task_name }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('notification.logs.detailDialog.taskType')">
              <span>{{ selectedLog.task_type_display }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('notification.logs.detailDialog.notificationType')">
              <el-tag :type="getNotificationTypeTagType(selectedLog.notification_type_display)">
                {{ selectedLog.notification_type_display }}
              </el-tag>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('notification.logs.detailDialog.status')">
              <el-tag :type="getStatusTagType(selectedLog.status_display)">
                {{ selectedLog.status_display }}
              </el-tag>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('notification.logs.detailDialog.notificationTime')">
              <span>{{ formatDate(selectedLog.created_at) }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('notification.logs.detailDialog.sentTime')">
              <span>{{ selectedLog.sent_at ? formatDate(selectedLog.sent_at) : '-' }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="24" v-if="selectedLog.notification_target_display && selectedLog.notification_target_display.length > 0">
            <el-form-item :label="$t('notification.logs.detailDialog.notificationTarget')">
              <div class="notification-targets">
                <el-tag
                    v-for="(target, index) in selectedLog.notification_target_display"
                    :key="index"
                    class="target-tag"
                    size="small"
                    :type="getTargetTagType(target.type)"
                >
                  {{ target.display }}（{{ target.name }}）
                </el-tag>
                <span v-if="!selectedLog.notification_target_display || selectedLog.notification_target_display.length === 0">-</span>
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item :label="$t('notification.logs.detailDialog.notificationContent')">
              <div class="notification-content">
                <div v-if="parsedNotificationContent" class="notification-content-parsed">
                  <div class="content-item" v-for="(item, index) in parsedNotificationContent" :key="index">
                    <span class="content-label">{{ item.label }}:</span>
                    <span class="content-value">{{ item.value }}</span>
                  </div>
                </div>
                <div v-else class="notification-content-raw">
                  <pre>{{ selectedLog.notification_content || '-' }}</pre>
                </div>
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="24" v-if="selectedLog.error_message">
            <el-form-item :label="$t('notification.logs.detailDialog.errorMessage')">
              <div class="error-message">
                <el-alert
                    :title="selectedLog.error_message"
                    type="error"
                    show-icon
                    :closable="false"
                />
              </div>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">{{ $t('notification.logs.detailDialog.close') }}</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import {Search} from '@element-plus/icons-vue'
import {ref, reactive, onMounted, computed} from 'vue'
import {useI18n} from 'vue-i18n'
import {ElMessage} from 'element-plus'
import axios from 'axios'

export default {
  name: 'NotificationLogs',
  components: {
    Search
  },
  setup() {
    const {t, locale} = useI18n()

    // 数据状态
    const loading = ref(false)
    const logsData = ref([])
    const detailDialogVisible = ref(false)
    const selectedLog = ref(null)

    // 搜索表单
    const searchForm = reactive({
      taskName: '',
      dateRange: [],
      status: ''
    })

    // 分页配置
    const pagination = reactive({
      currentPage: 1,
      pageSize: 10,
      total: 0
    })

    // 排序参数
    const sortParams = reactive({
      prop: 'created_at',
      order: 'descending'
    })

    // 获取通知日志数据
    const fetchLogsData = async () => {
      loading.value = true
      try {
        const params = {
          page: pagination.currentPage,
          page_size: pagination.pageSize,
          ordering: sortParams.order === 'ascending' ? sortParams.prop : `-${sortParams.prop}`
        }

        // 添加搜索条件
        if (searchForm.taskName) {
          params.search = searchForm.taskName
        }
        if (searchForm.dateRange && searchForm.dateRange.length === 2) {
          params.start_date = searchForm.dateRange[0]
          params.end_date = searchForm.dateRange[1]
        }
        if (searchForm.status) {
          params.status = searchForm.status
        }

        const response = await axios.get('/api/api-testing/notification-logs/', {params})
        logsData.value = response.data.results || []
        pagination.total = response.data.count || 0
      } catch (error) {
        console.error('Fetch notification logs failed:', error)
        ElMessage.error(t('notification.logs.messages.fetchFailed'))
      } finally {
        loading.value = false
      }
    }

    // 处理搜索
    const handleSearch = () => {
      pagination.currentPage = 1
      fetchLogsData()
    }

    // 重置搜索
    const handleReset = () => {
      searchForm.taskName = ''
      searchForm.dateRange = []
      searchForm.status = ''
      pagination.currentPage = 1
      fetchLogsData()
    }

    // 处理分页变化
    const handleSizeChange = (val) => {
      pagination.pageSize = val
      pagination.currentPage = 1
      fetchLogsData()
    }

    const handleCurrentChange = (val) => {
      pagination.currentPage = val
      fetchLogsData()
    }

    // 处理排序
    const handleSortChange = ({prop, order}) => {
      sortParams.prop = prop
      sortParams.order = order || 'descending'
      fetchLogsData()
    }

    // 查看详情
    const viewDetail = async (row) => {
      try {
        const response = await axios.get(`/api/api-testing/notification-logs/${row.id}/detail/`)
        selectedLog.value = response.data
        detailDialogVisible.value = true
      } catch (error) {
        console.error('Fetch notification detail failed:', error)
        ElMessage.error(t('notification.logs.messages.fetchDetailFailed'))
      }
    }

    // 关闭详情弹窗
    const handleDetailDialogClose = (done) => {
      selectedLog.value = null
      done()
    }

    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleString(locale.value === 'zh-cn' ? 'zh-CN' : 'en-US')
    }

    // 获取状态标签类型
    const getStatusTagType = (status) => {
      const typeMap = {
        '发送成功': 'success',
        'success': 'success',
        '发送失败': 'danger',
        'failed': 'danger',
        '待发送': 'info',
        'pending': 'info',
        '发送中': 'warning',
        'sending': 'warning',
        '已取消': 'info',
        'cancelled': 'info'
      }
      return typeMap[status] || 'info'
    }

    // 获取通知类型标签类型
    const getNotificationTypeTagType = (typeDisplay) => {
      const typeMap = {
        '邮箱通知': '',
        'Webhook机器人': 'primary',
        '两种都发送': 'warning'
      }
      return typeMap[typeDisplay] || 'info'
    }

    // 获取通知对象标签类型
    const getTargetTagType = (targetType) => {
      const typeMap = {
        'wechat': 'success',
        'feishu': 'primary',
        'dingtalk': 'warning',
        'email': 'info'
      }
      return typeMap[targetType] || 'info'
    }

    // 格式化收件人显示
    const formatRecipients = (recipients) => {
      if (!recipients) return '-'

      if (typeof recipients === 'string') {
        return recipients.length > 20 ? recipients.substring(0, 20) + '...' : recipients
      }

      if (Array.isArray(recipients)) {
        if (recipients.length === 0) return '-'
        if (recipients.length === 1) return recipients[0]
        return `${recipients[0]} +${recipients.length - 1}`
      }

      return '-'
    }

    // 格式化收件人信息
    const formatRecipientInfo = (recipientInfo) => {
      if (!recipientInfo) return []
      if (Array.isArray(recipientInfo)) {
        return recipientInfo.map(item =>
            item.email ? `${item.name} <${item.email}>` : item.name
        )
      }
      return [recipientInfo]
    }

    // 格式化Webhook信息
    const formatWebhookInfo = (webhookInfo) => {
      if (!webhookInfo) return []
      if (Array.isArray(webhookInfo)) {
        return webhookInfo.map(item => item.name || item.type)
      }
      return [webhookInfo.name || webhookInfo.type]
    }

    // 解析通知内容为结构化数据
    const parsedNotificationContent = computed(() => {
      if (!selectedLog.value || !selectedLog.value.notification_content) {
        return null
      }

      const content = selectedLog.value.notification_content

      try {
        const jsonContent = JSON.parse(content)
        const result = []

        let contentText = ''

        if (jsonContent.msgtype === 'markdown' && jsonContent.markdown) {
          if (jsonContent.markdown.text) {
            contentText = jsonContent.markdown.text
          } else if (jsonContent.markdown.content) {
            contentText = jsonContent.markdown.content
          }
        }
        else if (jsonContent.msg_type === 'interactive' && jsonContent.card) {
          if (jsonContent.card.elements && jsonContent.card.elements[0] && jsonContent.card.elements[0].text) {
            contentText = jsonContent.card.elements[0].text.content
          }
        }

        if (contentText) {
          const lines = contentText.split('\n').filter(line => line.trim())

          lines.forEach(line => {
            if (line.includes('**') || line.trim() === '') {
              return
            }

            const colonIndex = line.indexOf(':')
            if (colonIndex > 0) {
              const label = line.substring(0, colonIndex).trim()
              const value = line.substring(colonIndex + 1).trim()

              if (label && value) {
                result.push({
                  label: label,
                  value: value
                })
              }
            }
          })

          return result.length > 0 ? result : null
        }
      } catch (e) {
        console.log('Trying to parse as plain text format')
      }

      try {
        const result = []
        const lines = content.split('\n').filter(line => line.trim())

        lines.forEach(line => {
          if (!line.trim()) {
            return
          }

          const colonIndex = line.indexOf(':')
          if (colonIndex > 0) {
            const label = line.substring(0, colonIndex).trim()
            const value = line.substring(colonIndex + 1).trim()

            if (label && value && !value.includes("'results':") && !value.includes('"results":')) {
              result.push({
                label: label,
                value: value
              })
            }
          }
        })

        return result.length > 0 ? result : null
      } catch (e) {
        console.error('Parse notification content failed:', e)
        return null
      }
    })

    // 组件挂载时获取数据
    onMounted(() => {
      fetchLogsData()
    })

    return {
      loading,
      logsData,
      detailDialogVisible,
      selectedLog,
      searchForm,
      pagination,
      sortParams,
      parsedNotificationContent,
      handleSearch,
      handleReset,
      handleSizeChange,
      handleCurrentChange,
      handleSortChange,
      viewDetail,
      handleDetailDialogClose,
      formatDate,
      getStatusTagType,
      getNotificationTypeTagType,
      getTargetTagType,
      formatRecipients,
      formatRecipientInfo,
      formatWebhookInfo
    }
  }
}
</script>

<style scoped>
.notification-logs-container {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.page-actions {
  margin-bottom: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 6px;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logs-table-container {
  margin-top: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.notification-detail-form :deep(.el-form-item) {
  margin-bottom: 18px;
}

.notification-targets {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.target-tag {
  margin: 0;
}

.notification-content {
  width: 100%;
}

.notification-content-parsed {
  background: #ffffff;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.content-item {
  display: flex;
  align-items: flex-start;
  padding: 12px 0;
  border-bottom: 1px solid #f0f2f5;
}

.content-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.content-item:first-child {
  padding-top: 0;
}

.content-label {
  font-weight: 600;
  color: #606266;
  min-width: 100px;
  flex-shrink: 0;
  margin-right: 16px;
  font-size: 14px;
  line-height: 1.8;
}

.content-value {
  color: #303133;
  flex: 1;
  word-break: break-word;
  font-size: 14px;
  line-height: 1.8;
}

.notification-content-raw pre {
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  font-size: 13px;
  line-height: 1.6;
  color: #606266;
  max-height: 400px;
  overflow-y: auto;
}

.notification-content-raw pre::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.notification-content-raw pre::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.notification-content-raw pre::-webkit-scrollbar-thumb:hover {
  background: #a8abb2;
}

.error-message {
  margin-top: 8px;
}

.response-info pre {
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
  max-height: 150px;
  overflow-y: auto;
  font-family: monospace;
  font-size: 12px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
