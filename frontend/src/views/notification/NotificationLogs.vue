<template>
  <div class="notification-logs-container">
    <!-- 页面操作栏 -->
    <div class="page-actions">
      <el-row :gutter="20" class="filter-row">
        <el-col :span="6">
          <el-input
              v-model="searchForm.taskName"
              placeholder="搜索任务名称"
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
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              @change="handleSearch"
          />
        </el-col>
        <el-col :span="6">
          <el-select
              v-model="searchForm.status"
              placeholder="通知状态"
              clearable
              @change="handleSearch"
          >
            <el-option label="全部状态" value=""/>
            <el-option label="成功" value="SUCCESS"/>
            <el-option label="失败" value="FAILED"/>
            <el-option label="重试中" value="RETRYING"/>
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="handleSearch">
            <el-icon>
              <Search/>
            </el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            重置
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 通知列表 -->
    <div class="logs-table-container">
      <el-table
          :data="logsData"
          v-loading="loading"
          element-loading-text="加载中..."
          stripe
          style="width: 100%"
          @sort-change="handleSortChange"
      >
        <el-table-column
            prop="task_name"
            label="任务名称"
            min-width="150"
            sortable="custom"
        />
        <el-table-column
            prop="task_type_display"
            label="任务类型"
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
            label="通知类型"
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
            label="通知对象"
            min-width="150"
        >
          <template #default="{ row }">
            <span>{{ row.notification_target_display || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column
            prop="created_at"
            label="通知时间"
            min-width="180"
            sortable="custom"
        >
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column
            prop="status_display"
            label="状态"
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
            label="操作"
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
              查看详情
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
        title="通知详情"
        width="600px"
        :before-close="handleDetailDialogClose"
    >
      <el-form
          v-if="selectedLog"
          label-position="top"
          class="notification-detail-form"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="任务名称">
              <span>{{ selectedLog.task_name }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="任务类型">
              <span>{{ selectedLog.task_type_display }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="通知类型">
              <el-tag :type="getNotificationTypeTagType(selectedLog.notification_type_display)">
                {{ selectedLog.notification_type_display }}
              </el-tag>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-tag :type="getStatusTagType(selectedLog.status_display)">
                {{ selectedLog.status_display }}
              </el-tag>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="通知时间">
              <span>{{ formatDate(selectedLog.created_at) }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="发送时间">
              <span>{{ selectedLog.sent_at ? formatDate(selectedLog.sent_at) : '-' }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="24" v-if="selectedLog.notification_target_display && selectedLog.notification_target_display.length > 0">
            <el-form-item label="通知对象">
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
            <el-form-item label="通知内容">
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
            <el-form-item label="错误信息">
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
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import {Search} from '@element-plus/icons-vue'
import {ref, reactive, onMounted, computed} from 'vue'
import {ElMessage} from 'element-plus'
import axios from 'axios'

export default {
  name: 'NotificationLogs',
  components: {
    Search
  },
  setup() {
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
        console.error('获取通知日志失败:', error)
        ElMessage.error('获取通知日志失败')
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
        console.error('获取通知详情失败:', error)
        ElMessage.error('获取通知详情失败')
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
      return date.toLocaleString('zh-CN')
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

      // 如果是字符串，直接返回
      if (typeof recipients === 'string') {
        return recipients.length > 20 ? recipients.substring(0, 20) + '...' : recipients
      }

      // 如果是数组，按原逻辑处理
      if (Array.isArray(recipients)) {
        if (recipients.length === 0) return '-'
        if (recipients.length === 1) return recipients[0]
        return `${recipients[0]} 等${recipients.length}人`
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
        // 尝试解析JSON格式的通知内容(Webhook)
        const jsonContent = JSON.parse(content)
        const result = []

        // 提取内容文本
        let contentText = ''

        // 处理企业微信格式
        if (jsonContent.msgtype === 'markdown' && jsonContent.markdown) {
          // 优先使用text字段(钉钉格式)
          if (jsonContent.markdown.text) {
            contentText = jsonContent.markdown.text
          } else if (jsonContent.markdown.content) {
            contentText = jsonContent.markdown.content
          }
        }
        // 处理飞书格式
        else if (jsonContent.msg_type === 'interactive' && jsonContent.card) {
          if (jsonContent.card.elements && jsonContent.card.elements[0] && jsonContent.card.elements[0].text) {
            contentText = jsonContent.card.elements[0].text.content
          }
        }

        if (contentText) {
          // 解析文本内容,提取关键信息
          const lines = contentText.split('\n').filter(line => line.trim())

          lines.forEach(line => {
            // 跳过标题行(包含**的行)和空行
            if (line.includes('**') || line.trim() === '') {
              return
            }

            // 解析键值对
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
        // JSON解析失败,尝试作为纯文本解析(邮件通知)
        console.log('尝试解析为纯文本格式')
      }

      // 解析纯文本格式的邮件内容
      try {
        const result = []
        const lines = content.split('\n').filter(line => line.trim())

        lines.forEach(line => {
          // 跳过空行
          if (!line.trim()) {
            return
          }

          // 解析键值对 (格式: "标签: 值")
          const colonIndex = line.indexOf(':')
          if (colonIndex > 0) {
            const label = line.substring(0, colonIndex).trim()
            const value = line.substring(colonIndex + 1).trim()

            // 过滤掉包含详细测试结果的行(通常会是大字典或JSON字符串)
            // 跳过包含'results'关键字的超长值
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
        // 如果所有解析都失败,返回null以显示原始内容
        console.error('解析通知内容失败:', e)
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