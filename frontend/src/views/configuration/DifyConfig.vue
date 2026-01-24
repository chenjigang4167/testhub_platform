<template>
  <div class="dify-config-container">
    <div class="page-header">
      <h1>{{ $t('configuration.dify.title') }}</h1>
      <p>{{ $t('configuration.dify.description') }}</p>
    </div>

    <div class="config-content">
      <el-card class="config-card">
        <template #header>
          <div class="card-header">
            <span>{{ $t('configuration.dify.apiConfig') }}</span>
            <el-tag v-if="currentConfig" type="success">{{ $t('configuration.common.configured') }}</el-tag>
            <el-tag v-else type="info">{{ $t('configuration.common.notConfigured') }}</el-tag>
          </div>
        </template>

        <el-form :model="form" :rules="rules" ref="configForm" label-width="120px">
          <el-form-item :label="$t('configuration.dify.apiUrl')" prop="api_url">
            <el-input
              v-model="form.api_url"
              :placeholder="$t('configuration.dify.apiUrlPlaceholder')"
              clearable
            >
              <template #prepend>
                <el-icon><Link /></el-icon>
              </template>
            </el-input>
            <div class="form-tip">{{ $t('configuration.dify.apiUrlTip') }}</div>
          </el-form-item>

          <el-form-item :label="$t('configuration.dify.apiKey')" prop="api_key">
            <el-input
              v-model="form.api_key"
              type="password"
              :placeholder="currentConfig ? $t('configuration.dify.apiKeyPlaceholderEdit') : $t('configuration.dify.apiKeyPlaceholder')"
              show-password
              clearable
            >
              <template #prepend>
                <el-icon><Key /></el-icon>
              </template>
            </el-input>
            <div class="form-tip">{{ $t('configuration.dify.apiKeyTip') }}</div>
          </el-form-item>

          <el-form-item :label="$t('configuration.dify.enableStatus')" prop="is_active">
            <el-switch v-model="form.is_active" />
            <span class="switch-label">{{ form.is_active ? $t('configuration.common.enabled') : $t('configuration.common.disabled') }}</span>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="testConnection" :loading="testing">
              <el-icon><Connection /></el-icon>
              {{ $t('configuration.dify.testConnection') }}
            </el-button>
            <el-button type="success" @click="saveConfig" :loading="saving">
              <el-icon><Check /></el-icon>
              {{ $t('configuration.common.save') }}
            </el-button>
            <el-button @click="resetForm">
              <el-icon><RefreshLeft /></el-icon>
              {{ $t('configuration.common.reset') }}
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="info-card" v-if="currentConfig">
        <template #header>
          <span>{{ $t('configuration.dify.currentConfig') }}</span>
        </template>
        <el-descriptions :column="1" border>
          <el-descriptions-item :label="$t('configuration.dify.apiUrl')">
            {{ currentConfig.api_url }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('configuration.dify.apiKey')">
            {{ currentConfig.api_key_masked || '****' }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('configuration.common.status')">
            <el-tag :type="currentConfig.is_active ? 'success' : 'info'">
              {{ currentConfig.is_active ? $t('configuration.common.enabled') : $t('configuration.common.disabled') }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('configuration.common.createdAt')">
            {{ formatDate(currentConfig.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('configuration.common.updatedAt')">
            {{ formatDate(currentConfig.updated_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Link, Key, Connection, Check, RefreshLeft } from '@element-plus/icons-vue'
import api from '@/utils/api'

const { t, locale } = useI18n()

const configForm = ref(null)
const currentConfig = ref(null)
const testing = ref(false)
const saving = ref(false)

const form = ref({
  api_url: '',
  api_key: '',
  is_active: true
})

const rules = computed(() => ({
  api_url: [
    { required: true, message: t('configuration.dify.validation.apiUrlRequired'), trigger: 'blur' },
    { type: 'url', message: t('configuration.dify.validation.apiUrlInvalid'), trigger: 'blur' }
  ],
  api_key: [
    { min: 8, message: t('configuration.dify.validation.apiKeyMinLength'), trigger: 'blur' }
  ]
}))

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString(locale.value === 'zh-cn' ? 'zh-CN' : 'en-US')
}

const loadConfig = async () => {
  try {
    const response = await api.get('/assistant/config/dify/')
    currentConfig.value = response.data
    form.value = {
      api_url: response.data.api_url,
      api_key: '', // Don't populate API key for security
      is_active: response.data.is_active
    }
  } catch (error) {
    if (error.response?.status !== 404) {
      console.error(t('configuration.dify.messages.loadFailed'), error)
    }
  }
}

const testConnection = async () => {
  if (!configForm.value) return

  await configForm.value.validate(async (valid) => {
    if (!valid) return

    testing.value = true
    try {
      const response = await api.post('/assistant/config/dify/test_connection/', {
        api_url: form.value.api_url,
        api_key: form.value.api_key
      })

      if (response.data.success) {
        ElMessage.success(t('configuration.dify.messages.testSuccess'))
      } else {
        ElMessage.error(response.data.error || t('configuration.dify.messages.testFailed'))
      }
    } catch (error) {
      console.error(t('configuration.dify.messages.testFailed'), error)
      ElMessage.error(error.response?.data?.error || t('configuration.dify.messages.testFailed'))
    } finally {
      testing.value = false
    }
  })
}

const saveConfig = async () => {
  if (!configForm.value) return

  await configForm.value.validate(async (valid) => {
    if (!valid) return

    saving.value = true
    try {
      // Prepare data to save
      const dataToSave = {
        api_url: form.value.api_url,
        is_active: form.value.is_active
      }

      // Only send API Key if user entered a new one
      if (form.value.api_key && form.value.api_key.trim()) {
        dataToSave.api_key = form.value.api_key
      }

      if (currentConfig.value) {
        // Update existing config
        await api.patch(`/assistant/config/dify/${currentConfig.value.id}/`, dataToSave)
        ElMessage.success(t('configuration.dify.messages.updateSuccess'))
      } else {
        // Create new config - API key is required
        if (!form.value.api_key || !form.value.api_key.trim()) {
          ElMessage.error(t('configuration.dify.messages.apiKeyRequired'))
          saving.value = false
          return
        }
        await api.post('/assistant/config/dify/', dataToSave)
        ElMessage.success(t('configuration.dify.messages.saveSuccess'))
      }

      // Clear API Key input for security
      form.value.api_key = ''
      await loadConfig()
    } catch (error) {
      console.error(t('configuration.dify.messages.saveFailed'), error)
      ElMessage.error(error.response?.data?.error || t('configuration.dify.messages.saveFailed'))
    } finally {
      saving.value = false
    }
  })
}

const resetForm = () => {
  if (configForm.value) {
    configForm.value.resetFields()
  }
  if (currentConfig.value) {
    form.value = {
      api_url: currentConfig.value.api_url,
      api_key: '',
      is_active: currentConfig.value.is_active
    }
  }
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped lang="scss">
.dify-config-container {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;

  h1 {
    font-size: 2rem;
    color: #2c3e50;
    margin-bottom: 10px;
  }

  p {
    color: #666;
    font-size: 1rem;
  }
}

.config-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.config-card, .info-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.switch-label {
  margin-left: 10px;
  color: #606266;
}

.el-form-item {
  margin-bottom: 24px;
}
</style>
