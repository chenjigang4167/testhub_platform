<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">{{ isEdit ? '编辑评审' : '创建评审' }}</h1>
      <div>
        <el-button @click="$router.back()">返回</el-button>
        <el-button type="primary" @click="saveReview" :loading="saving">保存</el-button>
      </div>
    </div>

    <div class="form-container">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="评审标题" prop="title">
              <el-input v-model="form.title" placeholder="请输入评审标题" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="关联项目" prop="projects">
              <el-select 
                v-model="form.projects" 
                multiple 
                placeholder="请选择项目" 
                @change="onProjectChange"
              >
                <el-option
                  v-for="project in projects"
                  :key="project.id"
                  :label="project.name"
                  :value="project.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="form.priority" placeholder="请选择优先级">
                <el-option label="低" value="low" />
                <el-option label="中" value="medium" />
                <el-option label="高" value="high" />
                <el-option label="紧急" value="urgent" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="截止日期">
              <el-date-picker
                v-model="form.deadline"
                type="datetime"
                placeholder="请选择截止日期"
                format="YYYY-MM-DD HH:mm"
                value-format="YYYY-MM-DD HH:mm:ss"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="评审描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入评审描述"
          />
        </el-form-item>

        <el-form-item label="选择用例" prop="testcases">
          <div class="testcase-selector">
            <div class="search-bar">
              <el-input
                v-model="testcaseSearch"
                placeholder="搜索用例"
                @input="searchTestcases"
                clearable
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
              <el-button type="primary" @click="showTestcaseSelector">选择用例</el-button>
            </div>
            
            <div class="selected-testcases">
              <el-tag
                v-for="testcase in selectedTestcases"
                :key="testcase.id"
                closable
                @close="removeTestcase(testcase.id)"
                class="testcase-tag"
              >
                {{ testcase.title }}
              </el-tag>
              <div v-if="selectedTestcases.length === 0" class="empty-tip">
                请选择要评审的测试用例
              </div>
            </div>
          </div>
        </el-form-item>

        <el-form-item label="评审人员" prop="reviewers">
          <el-select
            v-model="form.reviewers"
            multiple
            placeholder="请选择评审人员"
            @change="onReviewersChange"
          >
            <el-option
              v-for="user in projectUsers"
              :key="user.id"
              :label="user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="评审模板">
          <el-select v-model="form.template" placeholder="可选择评审模板" @change="applyTemplate">
            <el-option
              v-for="template in templates"
              :key="template.id"
              :label="template.name"
              :value="template.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
    </div>

    <!-- 用例选择对话框 -->
    <el-dialog v-model="testcaseSelectorVisible" title="选择测试用例" width="800px">
      <div class="testcase-selector-content">
        <el-input
          v-model="testcaseSearchInDialog"
          placeholder="搜索用例"
          @input="searchTestcasesInDialog"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-table
          :data="filteredTestcases"
          @selection-change="handleTestcaseSelection"
          max-height="400"
          class="testcase-table"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="title" label="用例标题" min-width="200" show-overflow-tooltip />
          <el-table-column prop="test_type" label="测试类型" width="120" />
          <el-table-column prop="priority" label="优先级" width="100">
            <template #default="{ row }">
              <el-tag :class="`priority-tag ${row.priority}`">{{ getPriorityText(row.priority) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="author.username" label="作者" width="120" />
        </el-table>
      </div>
      <template #footer>
        <el-button @click="testcaseSelectorVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmTestcaseSelection">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import api from '@/utils/api'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)

const formRef = ref()
const saving = ref(false)
const testcaseSelectorVisible = ref(false)
const testcaseSearch = ref('')
const testcaseSearchInDialog = ref('')

const projects = ref([])
const projectUsers = ref([])
const templates = ref([])
const testcases = ref([])
const selectedTestcases = ref([])
const tempSelectedTestcases = ref([])

const form = reactive({
  title: '',
  description: '',
  projects: [],
  priority: 'medium',
  deadline: '',
  testcases: [],
  reviewers: [],
  template: ''
})

const rules = {
  title: [{ required: true, message: '请输入评审标题', trigger: 'blur' }],
  projects: [{ required: true, message: '请选择项目', trigger: 'change' }],
  testcases: [{ required: true, message: '请选择要评审的用例', trigger: 'change' }],
  reviewers: [{ required: true, message: '请选择评审人员', trigger: 'change' }]
}

const filteredTestcases = computed(() => {
  if (!testcaseSearchInDialog.value) return testcases.value
  return testcases.value.filter(tc => 
    tc.title.toLowerCase().includes(testcaseSearchInDialog.value.toLowerCase())
  )
})

const fetchProjects = async () => {
  try {
    const response = await api.get('/projects/')
    projects.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error('获取项目列表失败')
  }
}

const fetchProjectUsers = async () => {
  try {
    const response = await api.get('/auth/users/')
    projectUsers.value = response.data.results || response.data || []
    console.log('All users:', projectUsers.value) // 调试用
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败')
    projectUsers.value = []
  }
}

const fetchTestcases = async (projectIds) => {
  try {
    // 如果没有选择项目，清空用例列表
    if (!projectIds || projectIds.length === 0) {
      testcases.value = []
      return
    }
    
    // 获取所有选中项目的用例
    const promises = projectIds.map(projectId => 
      api.get('/testcases/', { params: { project: projectId } })
    )
    
    const responses = await Promise.all(promises)
    const allTestcases = []
    
    responses.forEach(response => {
      const cases = response.data.results || response.data || []
      allTestcases.push(...cases)
    })
    
    // 去重（基于用例ID）
    const uniqueTestcases = allTestcases.filter((testcase, index, self) => 
      index === self.findIndex(t => t.id === testcase.id)
    )
    
    testcases.value = uniqueTestcases
  } catch (error) {
    console.error('获取用例列表失败:', error)
  }
}

const fetchTemplates = async (projectIds) => {
  try {
    // 如果没有选择项目，清空模板列表
    if (!projectIds || projectIds.length === 0) {
      templates.value = []
      return
    }
    
    // 获取所有选中项目的模板
    const promises = projectIds.map(projectId => 
      api.get('/reviews/review-templates/', { params: { project: projectId } })
    )
    
    const responses = await Promise.all(promises)
    const allTemplates = []
    
    responses.forEach(response => {
      const temps = response.data.results || response.data || []
      allTemplates.push(...temps)
    })
    
    // 去重（基于模板ID）
    const uniqueTemplates = allTemplates.filter((template, index, self) => 
      index === self.findIndex(t => t.id === template.id)
    )
    
    templates.value = uniqueTemplates
  } catch (error) {
    console.error('获取模板列表失败:', error)
  }
}

const onProjectChange = (projectIds) => {
  if (projectIds && projectIds.length > 0) {
    fetchTestcases(projectIds)
    fetchTemplates(projectIds)
  } else {
    // 如果没有选择项目，清空相关数据
    testcases.value = []
    templates.value = []
  }
  
  // 清空相关选择
  form.reviewers = []
  form.testcases = []
  selectedTestcases.value = []
}

const showTestcaseSelector = () => {
  if (!form.projects || form.projects.length === 0) {
    ElMessage.warning('请先选择项目')
    return
  }
  testcaseSelectorVisible.value = true
}

const handleTestcaseSelection = (selection) => {
  tempSelectedTestcases.value = selection
}

const confirmTestcaseSelection = () => {
  selectedTestcases.value = [...tempSelectedTestcases.value]
  form.testcases = selectedTestcases.value.map(tc => tc.id)
  testcaseSelectorVisible.value = false
}

const removeTestcase = (id) => {
  selectedTestcases.value = selectedTestcases.value.filter(tc => tc.id !== id)
  form.testcases = selectedTestcases.value.map(tc => tc.id)
}

const onReviewersChange = () => {
  // 可以在这里添加评审人员变更的逻辑
}

const applyTemplate = async (templateId) => {
  if (!templateId) return
  
  try {
    const template = templates.value.find(t => t.id === templateId)
    if (template) {
      // 应用模板的默认评审人员
      form.reviewers = template.default_reviewers.map(u => u.id)
    }
  } catch (error) {
    console.error('应用模板失败:', error)
  }
}

const saveReview = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    saving.value = true
    
    const data = {
      ...form,
      testcases: form.testcases,
      reviewers: form.reviewers,
      // 确保包含 template 字段
      template: form.template || null
    }
    
    if (isEdit.value) {
      await api.put(`/reviews/reviews/${route.params.id}/`, data)
      ElMessage.success('评审更新成功')
    } else {
      await api.post('/reviews/reviews/', data)
      ElMessage.success('评审创建成功')
    }
    
    router.push('/ai-generation/reviews')
    
  } catch (error) {
    if (error.response?.data) {
      const errors = Object.values(error.response.data).flat()
      ElMessage.error(errors[0] || '保存失败')
    } else {
      ElMessage.error('保存失败')
    }
  } finally {
    saving.value = false
  }
}

const getPriorityText = (priority) => {
  const textMap = {
    low: '低',
    medium: '中',
    high: '高',
    critical: '紧急'
  }
  return textMap[priority] || priority
}

const findMatchingTemplate = (review, templateList) => {
  if (!templateList || templateList.length === 0) return null
  
  // 获取评审的项目ID列表和评审人ID列表
  const reviewProjectIds = review.projects.map(p => p.id).sort()
  const reviewReviewerIds = review.assignments.map(a => a.reviewer.id).sort()
  
  let bestMatch = null
  let bestScore = 0
  
  for (const template of templateList) {
    let score = 0
    
    // 检查项目匹配度
    const templateProjectIds = (template.project || []).map(p => p.id).sort()
    const projectIntersection = reviewProjectIds.filter(id => templateProjectIds.includes(id))
    if (projectIntersection.length > 0) {
      score += projectIntersection.length * 2 // 项目匹配权重更高
    }
    
    // 检查默认评审人匹配度
    const templateReviewerIds = (template.default_reviewers || []).map(r => r.id).sort()
    const reviewerIntersection = reviewReviewerIds.filter(id => templateReviewerIds.includes(id))
    if (reviewerIntersection.length > 0) {
      score += reviewerIntersection.length // 评审人匹配
    }
    
    // 如果有更高的匹配分数，更新最佳匹配
    if (score > bestScore) {
      bestScore = score
      bestMatch = template
    }
  }
  
  // 只有当匹配分数大于0时才返回匹配的模板
  return bestScore > 0 ? bestMatch : null
}

const fetchReviewData = async (reviewId) => {
  try {
    const response = await api.get(`/reviews/reviews/${reviewId}/`)
    const review = response.data
    
    // 填充表单数据
    form.title = review.title
    form.description = review.description
    form.projects = review.projects.map(p => p.id)
    form.priority = review.priority
    form.deadline = review.deadline
    form.reviewers = review.assignments.map(a => a.reviewer.id)
    
    // 处理测试用例
    selectedTestcases.value = review.testcases
    form.testcases = review.testcases.map(tc => tc.id)
    
    // 加载项目相关数据
    if (form.projects.length > 0) {
      await fetchTestcases(form.projects)
      await fetchTemplates(form.projects)
      
      // 在模板加载完成后，尝试找到匹配的模板
      const matchingTemplate = findMatchingTemplate(review, templates.value)
      if (matchingTemplate) {
        form.template = matchingTemplate.id
      }
    }
    
  } catch (error) {
    console.error('获取评审数据失败:', error)
    ElMessage.error('获取评审数据失败')
    router.push('/ai-generation/reviews')
  }
}

onMounted(() => {
  fetchProjects()
  fetchProjectUsers() // 页面加载时就获取所有用户
  
  if (isEdit.value) {
    // 如果是编辑模式，加载现有数据
    fetchReviewData(route.params.id)
  }
})
</script>

<style lang="scss" scoped>
.testcase-selector {
  .search-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
  }
  
  .selected-testcases {
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    min-height: 80px;
    padding: 8px;
    
    .testcase-tag {
      margin: 4px;
    }
    
    .empty-tip {
      color: #909399;
      text-align: center;
      padding: 24px;
    }
  }
}

.testcase-selector-content {
  .el-input {
    margin-bottom: 16px;
  }
}

.priority-tag {
  &.low { color: #67c23a; }
  &.medium { color: #e6a23c; }
  &.high { color: #f56c6c; }
  &.critical { color: #f56c6c; font-weight: bold; }
}
</style>