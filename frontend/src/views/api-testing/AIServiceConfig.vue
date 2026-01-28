<template>
  <div class="ai-service-config">
    <div class="page-header">
      <h2>{{ $t('apiTesting.aiServiceConfig.title') }}</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        {{ $t('apiTesting.aiServiceConfig.addConfig') }}
      </el-button>
    </div>

    <div class="config-list">
      <el-table :data="configs" v-loading="loading" stripe>
        <el-table-column prop="name" :label="$t('apiTesting.aiServiceConfig.configName')" width="200" />
        <el-table-column prop="service_type_display" :label="$t('apiTesting.aiServiceConfig.serviceType')" width="120" />
        <el-table-column prop="role_display" :label="$t('apiTesting.aiServiceConfig.roleType')" width="150" />
        <el-table-column prop="model_name" :label="$t('apiTesting.aiServiceConfig.modelName')" width="200" />
        <el-table-column :label="$t('apiTesting.aiServiceConfig.status')" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? $t('apiTesting.aiServiceConfig.enabled') : $t('apiTesting.aiServiceConfig.disabled') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_by_name" :label="$t('apiTesting.aiServiceConfig.creator')" width="120" />
        <el-table-column prop="created_at" :label="$t('apiTesting.aiServiceConfig.createdAt')" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('apiTesting.aiServiceConfig.operation')" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="testConnection(row)" :loading="testing[row.id]">
              {{ $t('apiTesting.aiServiceConfig.testConnection') }}
            </el-button>
            <el-button size="small" @click="editConfig(row)">{{ $t('apiTesting.aiServiceConfig.edit') }}</el-button>
            <el-button size="small" type="danger" @click="deleteConfig(row.id)">{{ $t('apiTesting.aiServiceConfig.delete') }}</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog
      v-model="showCreateDialog"
      :title="editingConfig ? $t('apiTesting.aiServiceConfig.editConfig') : $t('apiTesting.aiServiceConfig.addConfig')"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-form-item :label="$t('apiTesting.aiServiceConfig.configName')" prop="name">
          <el-input v-model="form.name" :placeholder="$t('apiTesting.aiServiceConfig.inputConfigName')" />
        </el-form-item>
        <el-form-item :label="$t('apiTesting.aiServiceConfig.serviceType')" prop="service_type">
          <el-select v-model="form.service_type" :placeholder="$t('apiTesting.aiServiceConfig.selectServiceType')" style="width: 100%">
            <el-option :label="$t('apiTesting.aiServiceConfig.serviceTypes.openai')" value="openai" />
            <el-option :label="$t('apiTesting.aiServiceConfig.serviceTypes.azure')" value="azure" />
            <el-option :label="$t('apiTesting.aiServiceConfig.serviceTypes.anthropic')" value="anthropic" />
            <el-option :label="$t('apiTesting.aiServiceConfig.serviceTypes.deepseek')" value="deepseek" />
            <el-option :label="$t('apiTesting.aiServiceConfig.serviceTypes.qwen')" value="qwen" />
            <el-option :label="$t('apiTesting.aiServiceConfig.serviceTypes.siliconflow')" value="siliconflow" />
            <el-option :label="$t('apiTesting.aiServiceConfig.serviceTypes.other')" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('apiTesting.aiServiceConfig.roleType')" prop="role">
          <el-select v-model="form.role" :placeholder="$t('apiTesting.aiServiceConfig.selectRoleType')" style="width: 100%">
            <el-option :label="$t('apiTesting.aiServiceConfig.roleTypes.docExtractor')" value="doc_extractor" />
            <el-option :label="$t('apiTesting.aiServiceConfig.roleTypes.naming')" value="naming" />
            <el-option :label="$t('apiTesting.aiServiceConfig.roleTypes.mockData')" value="mock_data" />
            <el-option :label="$t('apiTesting.aiServiceConfig.roleTypes.description')" value="description" />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('apiTesting.aiServiceConfig.apiKey')" prop="api_key">
          <el-input v-model="form.api_key" type="password" :placeholder="$t('apiTesting.aiServiceConfig.inputApiKey')" show-password />
        </el-form-item>
        <el-form-item :label="$t('apiTesting.aiServiceConfig.apiBaseUrl')" prop="base_url">
          <el-input v-model="form.base_url" :placeholder="$t('apiTesting.aiServiceConfig.inputApiBaseUrl')" />
        </el-form-item>
        <el-form-item :label="$t('apiTesting.aiServiceConfig.modelName')" prop="model_name">
          <el-input v-model="form.model_name" :placeholder="$t('apiTesting.aiServiceConfig.inputModelName')" />
        </el-form-item>
        <el-form-item :label="$t('apiTesting.aiServiceConfig.maxTokens')" prop="max_tokens">
          <el-input-number v-model="form.max_tokens" :min="100" :max="32000" :step="100" />
        </el-form-item>
        <el-form-item :label="$t('apiTesting.aiServiceConfig.temperature')" prop="temperature">
          <el-slider v-model="form.temperature" :min="0" :max="2" :step="0.1" show-input />
        </el-form-item>
        <el-form-item :label="$t('apiTesting.aiServiceConfig.isActive')" prop="is_active">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">{{ $t('apiTesting.aiServiceConfig.cancel') }}</el-button>
        <el-button type="primary" @click="saveConfig" :loading="saving">{{ $t('apiTesting.aiServiceConfig.save') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { Plus } from '@element-plus/icons-vue'
import api from '@/utils/api'

const { t } = useI18n()
const loading = ref(false)
const configs = ref([])
const showCreateDialog = ref(false)
const editingConfig = ref(null)
const saving = ref(false)
const testing = ref({})
const formRef = ref(null)

const form = reactive({
  name: '',
  service_type: '',
  role: '',
  api_key: '',
  base_url: '',
  model_name: '',
  max_tokens: 4096,
  temperature: 0.7,
  is_active: true
})

const rules = computed(() => ({
  name: [{ required: true, message: t('apiTesting.aiServiceConfig.validation.configNameRequired'), trigger: 'blur' }],
  service_type: [{ required: true, message: t('apiTesting.aiServiceConfig.validation.serviceTypeRequired'), trigger: 'change' }],
  role: [{ required: true, message: t('apiTesting.aiServiceConfig.validation.roleTypeRequired'), trigger: 'change' }],
  api_key: [{ required: true, message: t('apiTesting.aiServiceConfig.validation.apiKeyRequired'), trigger: 'blur' }],
  base_url: [{ required: true, message: t('apiTesting.aiServiceConfig.validation.apiBaseUrlRequired'), trigger: 'blur' }],
  model_name: [{ required: true, message: t('apiTesting.aiServiceConfig.validation.modelNameRequired'), trigger: 'blur' }]
}))

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const loadConfigs = async () => {
  loading.value = true
  try {
    const res = await api.get('/api-testing/ai-service-configs/')
    configs.value = res.data.results || res.data
  } catch (error) {
    ElMessage.error(t('apiTesting.aiServiceConfig.messages.loadFailed'))
  } finally {
    loading.value = false
  }
}

const editConfig = (config) => {
  editingConfig.value = config
  Object.assign(form, {
    name: config.name,
    service_type: config.service_type,
    role: config.role,
    api_key: config.api_key,
    base_url: config.base_url,
    model_name: config.model_name,
    max_tokens: config.max_tokens,
    temperature: config.temperature,
    is_active: config.is_active
  })
  showCreateDialog.value = true
}

const saveConfig = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
  } catch (error) {
    return
  }

  saving.value = true
  try {
    if (editingConfig.value) {
      await api.put(`/api-testing/ai-service-configs/${editingConfig.value.id}/`, form)
      ElMessage.success(t('apiTesting.aiServiceConfig.messages.updateSuccess'))
    } else {
      await api.post('/api-testing/ai-service-configs/', form)
      ElMessage.success(t('apiTesting.aiServiceConfig.messages.createSuccess'))
    }
    showCreateDialog.value = false
    resetForm()
    await loadConfigs()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || t('apiTesting.aiServiceConfig.messages.saveFailed'))
  } finally {
    saving.value = false
  }
}

const deleteConfig = async (id) => {
  try {
    await ElMessageBox.confirm(t('apiTesting.aiServiceConfig.messages.confirmDelete'), t('apiTesting.common.tip'), {
      type: 'warning'
    })
    await api.delete(`/api-testing/ai-service-configs/${id}/`)
    ElMessage.success(t('apiTesting.aiServiceConfig.messages.deleteSuccess'))
    await loadConfigs()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('apiTesting.aiServiceConfig.messages.deleteFailed'))
    }
  }
}

const testConnection = async (config) => {
  testing.value[config.id] = true
  try {
    await api.post('/api-testing/ai-service-configs/test_connection/', {
      config_id: config.id
    })
    ElMessage.success(t('apiTesting.aiServiceConfig.messages.testSuccess'))
  } catch (error) {
    ElMessage.error(error.response?.data?.error || t('apiTesting.aiServiceConfig.messages.testFailed'))
  } finally {
    testing.value[config.id] = false
  }
}

const resetForm = () => {
  editingConfig.value = null
  Object.assign(form, {
    name: '',
    service_type: '',
    role: '',
    api_key: '',
    base_url: '',
    model_name: '',
    max_tokens: 4096,
    temperature: 0.7,
    is_active: true
  })
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

onMounted(() => {
  loadConfigs()
})
</script>

<style scoped>
.ai-service-config {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
}

.config-list {
  flex: 1;
  overflow: auto;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table .cell) {
  padding: 8px 0;
}
</style>
