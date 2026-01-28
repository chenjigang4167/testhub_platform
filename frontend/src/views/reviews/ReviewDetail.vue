<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">{{ $t('reviewDetail.title') }}</h1>
      <div>
        <el-button @click="$router.back()">{{ $t('reviewDetail.back') }}</el-button>
        <el-button v-if="canEdit" type="warning" @click="editReview">{{ $t('reviewDetail.edit') }}</el-button>
        <el-button v-if="canReview" type="success" @click="showReviewDialog">{{ $t('reviewDetail.submitReview') }}</el-button>
      </div>
    </div>

    <div v-if="review" class="content-container">
      <!-- 评审基本信息 -->
      <el-card class="info-card">
        <template #header>
          <span class="card-header">{{ $t('reviewDetail.basicInfo') }}</span>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="$t('reviewDetail.reviewTitle')" :span="2">{{ review.title }}</el-descriptions-item>
          <el-descriptions-item :label="$t('reviewDetail.associatedProject')">
            {{ Array.isArray(review.projects)
                ? review.projects.map(p => p.name).join(', ')
                : (review.projects?.name || $t('reviewDetail.notSet')) }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('reviewDetail.creator')">{{ review.creator?.username }}</el-descriptions-item>
          <el-descriptions-item :label="$t('reviewDetail.useTemplate')">
            {{ review.template?.name || $t('reviewDetail.noTemplate') }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('reviewDetail.reviewStatus')">
            <el-tag :type="getStatusType(review.status)">{{ getStatusText(review.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('reviewDetail.priority')">
            <el-tag :class="`priority-tag ${review.priority}`">{{ getPriorityText(review.priority) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('reviewDetail.deadline')">{{ review.deadline ? formatDate(review.deadline) : $t('reviewDetail.none') }}</el-descriptions-item>
          <el-descriptions-item :label="$t('reviewDetail.createdAt')">{{ formatDate(review.created_at) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('reviewDetail.reviewDescription')" :span="2">{{ review.description || $t('reviewDetail.none') }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 评审进度 -->
      <el-card class="progress-card">
        <template #header>
          <span class="card-header">{{ $t('reviewDetail.reviewProgress') }}</span>
        </template>
        <div class="progress-content">
          <div class="progress-stats">
            <div class="stat-item">
              <div class="stat-number">{{ review.assignments?.length || 0 }}</div>
              <div class="stat-label">{{ $t('reviewDetail.reviewers') }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ completedReviews }}</div>
              <div class="stat-label">{{ $t('reviewDetail.completed') }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ pendingReviews }}</div>
              <div class="stat-label">{{ $t('reviewDetail.pendingReview') }}</div>
            </div>
          </div>
          <el-progress
            :percentage="reviewProgress"
            :color="progressColor"
            :stroke-width="8"
            class="main-progress"
          />
        </div>
      </el-card>

      <!-- 评审人员状态 -->
      <el-card class="reviewers-card">
        <template #header>
          <span class="card-header">{{ $t('reviewDetail.reviewersCard') }}</span>
        </template>
        <el-table :data="review.assignments" stripe>
          <el-table-column prop="reviewer.username" :label="$t('reviewDetail.reviewer')" width="150" />
          <el-table-column :label="$t('reviewDetail.reviewerStatus')" width="120">
            <template #default="{ row }">
              <el-tag :type="getAssignmentStatusType(row.status)">
                {{ getAssignmentStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="comment" :label="$t('reviewDetail.reviewerComment')" min-width="200" show-overflow-tooltip />
          <el-table-column v-if="review.template?.checklist?.length" :label="$t('reviewDetail.checklist')" width="150">
            <template #default="{ row }">
              <div v-if="row.checklist_results && Object.keys(row.checklist_results).length > 0" class="checklist-summary">
                <el-tooltip effect="dark" placement="top">
                  <template #content>
                    <div class="checklist-tooltip">
                      <div v-for="(item, index) in review.template.checklist" :key="index" class="checklist-item">
                        <el-icon v-if="row.checklist_results[index] === true" class="pass-icon"><Check /></el-icon>
                        <el-icon v-else-if="row.checklist_results[index] === false" class="fail-icon"><Close /></el-icon>
                        <el-icon v-else class="pending-icon"><QuestionFilled /></el-icon>
                        <span>{{ item }}</span>
                      </div>
                    </div>
                  </template>
                  <span class="checklist-stats">
                    {{ getChecklistStats(row.checklist_results, review.template.checklist) }}
                  </span>
                </el-tooltip>
              </div>
              <span v-else class="no-checklist">{{ $t('reviewDetail.notFilled') }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="assigned_at" :label="$t('reviewDetail.assignedAt')" width="160">
            <template #default="{ row }">
              {{ formatDate(row.assigned_at) }}
            </template>
          </el-table-column>
          <el-table-column prop="reviewed_at" :label="$t('reviewDetail.reviewedAt')" width="160">
            <template #default="{ row }">
              {{ row.reviewed_at ? formatDate(row.reviewed_at) : $t('reviewDetail.pendingReviewTime') }}
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 评审用例 -->
      <el-card class="testcases-card">
        <template #header>
          <span class="card-header">{{ $t('reviewDetail.reviewTestcases') }} ({{ review.testcases?.length || 0 }})</span>
        </template>
        <el-table :data="review.testcases" stripe>
          <el-table-column prop="title" :label="$t('reviewDetail.testcaseTitle')" min-width="200" show-overflow-tooltip />
          <el-table-column :label="$t('reviewDetail.testType')" width="120">
            <template #default="{ row }">
              {{ getTypeText(row.test_type) }}
            </template>
          </el-table-column>
          <el-table-column :label="$t('reviewDetail.priority')" width="100">
            <template #default="{ row }">
              <el-tag :class="`priority-tag ${row.priority}`">{{ getPriorityText(row.priority) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="author.username" :label="$t('reviewDetail.author')" width="120" />
          <el-table-column :label="$t('reviewList.actions')" width="120">
            <template #default="{ row }">
              <el-button link type="primary" @click="viewTestcase(row.id)">{{ $t('reviewDetail.view') }}</el-button>
              <el-button link type="success" @click="addComment(row)">{{ $t('reviewDetail.comment') }}</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 评审意见 -->
      <el-card class="comments-card">
        <template #header>
          <div class="card-header-with-action">
            <span class="card-header">{{ $t('reviewDetail.reviewComments') }}</span>
            <el-button type="primary" size="small" @click="showAddCommentDialog">{{ $t('reviewDetail.addComment') }}</el-button>
          </div>
        </template>
        <div class="comments-list">
          <div
            v-for="comment in review.comments"
            :key="comment.id"
            class="comment-item"
          >
            <div class="comment-header">
              <div class="comment-author">
                <el-avatar :size="32" :src="comment.author.avatar" />
                <span class="author-name">{{ comment.author.username }}</span>
                <el-tag size="small" :type="getCommentTypeColor(comment.comment_type)">
                  {{ getCommentTypeText(comment.comment_type) }}
                </el-tag>
              </div>
              <div class="comment-time">{{ formatDate(comment.created_at) }}</div>
            </div>
            <div class="comment-content">{{ comment.content }}</div>
            <div v-if="comment.testcase" class="comment-testcase">
              {{ $t('reviewDetail.relatedTestcase') }}: {{ comment.testcase.title }}
            </div>
          </div>
          <div v-if="!review.comments?.length" class="empty-comments">
            {{ $t('reviewDetail.noComments') }}
          </div>
        </div>
      </el-card>
    </div>

    <!-- 提交评审对话框 -->
    <el-dialog v-model="reviewDialogVisible" :title="$t('reviewDetail.submitReviewDialog')" :close-on-click-modal="false" :close-on-press-escape="false" :modal="true" :destroy-on-close="false" width="800px">
      <el-form :model="reviewForm" label-width="100px">
        <el-form-item :label="$t('reviewDetail.reviewResult')" required>
          <el-radio-group v-model="reviewForm.status">
            <el-radio-button label="approved">{{ $t('reviewDetail.approved') }}</el-radio-button>
            <el-radio-button label="rejected">{{ $t('reviewDetail.rejected') }}</el-radio-button>
            <el-radio-button label="abstained">{{ $t('reviewDetail.abstained') }}</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <!-- 模板检查清单 -->
        <el-form-item v-if="review?.template?.checklist?.length" :label="$t('reviewDetail.checklist')" class="checklist-form-item">
          <div class="checklist-container">
            <div class="checklist-header">
              <span class="checklist-title">{{ review.template.name }} - {{ $t('reviewDetail.checklistTitle') }}</span>
              <div class="checklist-actions">
                <el-button size="small" @click="checkAll(true)">{{ $t('reviewDetail.allPass') }}</el-button>
                <el-button size="small" @click="checkAll(false)">{{ $t('reviewDetail.allFail') }}</el-button>
              </div>
            </div>
            <div class="checklist-items">
              <div
                v-for="(item, index) in review.template.checklist"
                :key="index"
                class="checklist-item"
              >
                <div class="item-content">
                  <span class="item-text">{{ item }}</span>
                </div>
                <div class="item-controls">
                  <el-radio-group v-model="reviewForm.checklist_results[index]">
                    <el-radio-button :label="true">{{ $t('reviewDetail.approved') }}</el-radio-button>
                    <el-radio-button :label="false">{{ $t('reviewDetail.rejected') }}</el-radio-button>
                  </el-radio-group>
                </div>
              </div>
            </div>
          </div>
        </el-form-item>

        <el-form-item :label="$t('reviewDetail.reviewCommentLabel')">
          <el-input
            v-model="reviewForm.comment"
            type="textarea"
            :rows="4"
            :placeholder="$t('reviewDetail.reviewCommentPlaceholder')"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewDialogVisible = false">{{ $t('reviewDetail.cancel') }}</el-button>
        <el-button type="primary" @click="submitReview">{{ $t('reviewDetail.submit') }}</el-button>
      </template>
    </el-dialog>

    <!-- 添加意见对话框 -->
    <el-dialog v-model="commentDialogVisible" :title="$t('reviewDetail.addCommentDialog')" :close-on-click-modal="false" width="600px">
      <el-form :model="commentForm" label-width="100px">
        <el-form-item :label="$t('reviewDetail.commentType')" required>
          <el-radio-group v-model="commentForm.comment_type">
            <el-radio-button label="general">{{ $t('reviewDetail.generalComment') }}</el-radio-button>
            <el-radio-button label="testcase">{{ $t('reviewDetail.testcaseComment') }}</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="commentForm.comment_type === 'testcase'" :label="$t('reviewDetail.relatedTestcaseLabel')">
          <el-select v-model="commentForm.testcase" :placeholder="$t('reviewDetail.selectTestcase')">
            <el-option
              v-for="testcase in review.testcases"
              :key="testcase.id"
              :label="testcase.title"
              :value="testcase.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('reviewDetail.commentContent')" required>
          <el-input
            v-model="commentForm.content"
            type="textarea"
            :rows="4"
            :placeholder="$t('reviewDetail.commentContentPlaceholder')"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="commentDialogVisible = false">{{ $t('reviewDetail.cancel') }}</el-button>
        <el-button type="primary" @click="addCommentSubmit">{{ $t('reviewDetail.submit') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Check, Close, QuestionFilled } from '@element-plus/icons-vue'
import api from '@/utils/api'
import dayjs from 'dayjs'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const { t } = useI18n()

const review = ref(null)
const reviewDialogVisible = ref(false)
const commentDialogVisible = ref(false)

const reviewForm = reactive({
  status: 'approved',
  comment: '',
  checklist_results: {}
})

const commentForm = reactive({
  comment_type: 'general',
  testcase: '',
  content: ''
})

const completedReviews = computed(() => {
  return review.value?.assignments?.filter(a => a.status !== 'pending').length || 0
})

const pendingReviews = computed(() => {
  return review.value?.assignments?.filter(a => a.status === 'pending').length || 0
})

const reviewProgress = computed(() => {
  const total = review.value?.assignments?.length || 0
  if (total === 0) return 0
  return Math.round((completedReviews.value / total) * 100)
})

const progressColor = computed(() => {
  const progress = reviewProgress.value
  if (progress === 100) return '#67c23a'
  if (progress >= 50) return '#e6a23c'
  return '#f56c6c'
})

const canEdit = computed(() => {
  return review.value?.creator?.id === userStore.user?.id &&
         ['pending', 'in_progress'].includes(review.value?.status)
})

const canReview = computed(() => {
  return review.value?.assignments?.some(a =>
    a.reviewer.id === userStore.user?.id && a.status === 'pending'
  )
})

const fetchReview = async () => {
  try {
    const response = await api.get(`/reviews/reviews/${route.params.id}/`)
    review.value = response.data
  } catch (error) {
    ElMessage.error(t('reviewDetail.fetchDetailFailed'))
    router.push('/ai-generation/reviews')
  }
}

const editReview = () => {
  router.push(`/ai-generation/reviews/${route.params.id}/edit`)
}

const showReviewDialog = () => {
  reviewForm.status = 'approved'
  reviewForm.comment = ''
  reviewForm.checklist_results = {}

  // 如果有模板检查清单，初始化检查清单结果
  if (review.value?.template?.checklist?.length) {
    review.value.template.checklist.forEach((item, index) => {
      reviewForm.checklist_results[index] = null
    })
  }

  reviewDialogVisible.value = true
}

const submitReview = async () => {
  try {
    await api.post(`/reviews/reviews/${route.params.id}/submit_review/`, reviewForm)
    ElMessage.success(t('reviewDetail.submitSuccess'))
    reviewDialogVisible.value = false
    fetchReview()
  } catch (error) {
    ElMessage.error(t('reviewDetail.submitFailed'))
  }
}

const showAddCommentDialog = () => {
  commentForm.comment_type = 'general'
  commentForm.testcase = ''
  commentForm.content = ''
  commentDialogVisible.value = true
}

const addComment = (testcase) => {
  commentForm.comment_type = 'testcase'
  commentForm.testcase = testcase.id
  commentForm.content = ''
  commentDialogVisible.value = true
}

const addCommentSubmit = async () => {
  if (!commentForm.content) {
    ElMessage.warning(t('reviewDetail.commentRequired'))
    return
  }

  try {
    const data = {
      review: review.value.id,
      comment_type: commentForm.comment_type,
      content: commentForm.content
    }

    if (commentForm.comment_type === 'testcase' && commentForm.testcase) {
      data.testcase = commentForm.testcase
    }

    await api.post('/reviews/review-comments/', data)
    ElMessage.success(t('reviewDetail.addCommentSuccess'))
    commentDialogVisible.value = false
    fetchReview()
  } catch (error) {
    console.error('Add comment failed:', error)
    ElMessage.error(t('reviewDetail.addCommentFailed'))
  }
}

const viewTestcase = (id) => {
  router.push(`/ai-generation/testcases/${id}`)
}

const getStatusType = (status) => {
  const typeMap = {
    pending: 'warning',
    in_progress: 'primary',
    approved: 'success',
    rejected: 'danger',
    cancelled: 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    pending: t('reviewDetail.assignmentPending'),
    in_progress: t('reviewList.statusInProgress'),
    approved: t('reviewDetail.assignmentApproved'),
    rejected: t('reviewDetail.assignmentRejected'),
    cancelled: t('reviewList.statusCancelled')
  }
  return textMap[status] || status
}

const getAssignmentStatusType = (status) => {
  const typeMap = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    abstained: 'info'
  }
  return typeMap[status] || 'info'
}

const getAssignmentStatusText = (status) => {
  const textMap = {
    pending: t('reviewDetail.assignmentPending'),
    approved: t('reviewDetail.assignmentApproved'),
    rejected: t('reviewDetail.assignmentRejected'),
    abstained: t('reviewDetail.assignmentAbstained')
  }
  return textMap[status] || status
}

const getPriorityText = (priority) => {
  const textMap = {
    low: t('reviewList.priorityLow'),
    medium: t('reviewList.priorityMedium'),
    high: t('reviewList.priorityHigh'),
    critical: t('reviewList.priorityCritical'),
    urgent: t('reviewList.priorityCritical')
  }
  return textMap[priority] || priority
}

const getTypeText = (type) => {
  const textMap = {
    functional: t('reviewDetail.testTypeFunctional'),
    integration: t('reviewDetail.testTypeIntegration'),
    api: t('reviewDetail.testTypeApi'),
    ui: t('reviewDetail.testTypeUi'),
    performance: t('reviewDetail.testTypePerformance'),
    security: t('reviewDetail.testTypeSecurity')
  }
  return textMap[type] || '-'
}

const getCommentTypeColor = (type) => {
  const colorMap = {
    general: 'primary',
    testcase: 'success',
    step: 'warning'
  }
  return colorMap[type] || 'info'
}

const getCommentTypeText = (type) => {
  const textMap = {
    general: t('reviewDetail.commentTypeGeneral'),
    testcase: t('reviewDetail.commentTypeTestcase'),
    step: t('reviewDetail.commentTypeStep')
  }
  return textMap[type] || '-'
}

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm')
}

// 检查清单相关方法
const checkAll = (value) => {
  if (review.value?.template?.checklist?.length) {
    review.value.template.checklist.forEach((item, index) => {
      reviewForm.checklist_results[index] = value
    })
  }
}

const getChecklistStats = (checklistResults, checklist) => {
  if (!checklistResults || !checklist) return '0/0'

  const total = checklist.length
  const passed = Object.values(checklistResults).filter(result => result === true).length
  const failed = Object.values(checklistResults).filter(result => result === false).length

  return `${t('reviewDetail.checklistPass')}: ${passed}, ${t('reviewDetail.checklistFail')}: ${failed}, ${t('reviewDetail.checklistTotal')}: ${total}`
}

onMounted(() => {
  fetchReview()
})
</script>

<style lang="scss" scoped>
.content-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-header {
  font-weight: 600;
  font-size: 16px;
}

.card-header-with-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-content {
  .progress-stats {
    display: flex;
    justify-content: space-around;
    margin-bottom: 20px;

    .stat-item {
      text-align: center;

      .stat-number {
        font-size: 28px;
        font-weight: bold;
        color: #409eff;
        margin-bottom: 4px;
      }

      .stat-label {
        color: #909399;
        font-size: 14px;
      }
    }
  }

  .main-progress {
    margin-top: 10px;
  }
}

.comments-list {
  .comment-item {
    border-bottom: 1px solid #f0f0f0;
    padding: 16px 0;

    &:last-child {
      border-bottom: none;
    }

    .comment-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;

      .comment-author {
        display: flex;
        align-items: center;
        gap: 8px;

        .author-name {
          font-weight: 500;
        }
      }

      .comment-time {
        color: #909399;
        font-size: 12px;
      }
    }

    .comment-content {
      margin-bottom: 8px;
      line-height: 1.6;
    }

    .comment-testcase {
      color: #409eff;
      font-size: 12px;
    }
  }

  .empty-comments {
    text-align: center;
    color: #909399;
    padding: 40px;
  }
}

.priority-tag {
  &.low { color: #67c23a; }
  &.medium { color: #e6a23c; }
  &.high { color: #f56c6c; }
  &.critical { color: #f56c6c; font-weight: bold; }
  &.urgent { color: #f56c6c; font-weight: bold; }
}

// 检查清单样式
.checklist-summary {
  .checklist-stats {
    font-size: 12px;
    color: #606266;
    cursor: pointer;
  }
}

.no-checklist {
  color: #909399;
  font-size: 12px;
}

.checklist-tooltip {
  .checklist-item {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;

    .pass-icon {
      color: #67c23a;
    }

    .fail-icon {
      color: #f56c6c;
    }

    .pending-icon {
      color: #909399;
    }
  }
}

// 提交评审对话框中的检查清单样式
.checklist-form-item {
  .checklist-container {
    border: 1px solid #dcdfe6;
    border-radius: 4px;

    .checklist-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 16px;
      background-color: #f5f7fa;
      border-bottom: 1px solid #dcdfe6;

      .checklist-title {
        font-weight: 500;
        color: #303133;
      }

      .checklist-actions {
        display: flex;
        gap: 8px;
      }
    }

    .checklist-items {
      padding: 16px;

      .checklist-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #f0f0f0;

        &:last-child {
          border-bottom: none;
        }

        .item-content {
          flex: 1;

          .item-text {
            color: #303133;
            line-height: 1.6;
          }
        }

        .item-controls {
          margin-left: 16px;
        }
      }
    }
  }
}
</style>
