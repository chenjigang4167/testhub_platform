<template>
  <div class="ai-mode-config">
    <div class="page-header">
      <h1>{{ $t('configuration.aiMode.title') }}</h1>
      <p>{{ $t('configuration.aiMode.description') }}</p>
    </div>

    <div class="main-content">
      <!-- 配置列表 -->
      <div class="configs-section">
        <div class="section-header">
          <h2>{{ $t('configuration.aiMode.configList') }}</h2>
          <button class="add-config-btn" @click="openAddModal">
            {{ $t('configuration.aiMode.addConfig') }}
          </button>
        </div>

        <div class="configs-grid">
          <div v-for="config in configs" :key="config.id" class="config-card">
            <div class="config-header">
              <div class="config-title">
                <h3>{{ config.name || $t('configuration.common.unnamed') }}</h3>
                <div class="config-badges">
                  <span class="provider-badge" :class="config.model_type">
                    {{ getProviderLabel(config.model_type) }}
                  </span>
                  <span class="model-name-badge">{{ config.model_name }}</span>
                  <span class="status-badge" :class="{ active: config.is_active }">
                    {{ config.is_active ? $t('configuration.common.enabled') : $t('configuration.common.disabled') }}
                  </span>
                </div>
              </div>
              <div class="config-actions">
                <el-switch
                  v-model="config.is_active"
                  @change="toggleActive(config)"
                  :active-text="$t('configuration.common.enabled')"
                  :inactive-text="$t('configuration.common.disabled')"
                  :loading="config.toggling"
                />
                <button class="test-btn" @click="testConnection(config)" :disabled="config.testing">
                  {{ $t('configuration.aiMode.testConnection') }}
                </button>
                <button class="edit-btn" @click="editConfig(config)">✏️</button>
                <button class="delete-btn" @click="deleteConfig(config.id)">🗑️</button>
              </div>
            </div>

            <div class="config-details">
              <div class="detail-item">
                <label>{{ $t('configuration.aiMode.baseUrl') }}:</label>
                <span>{{ config.base_url || $t('configuration.common.notSet') }}</span>
              </div>
              <div class="detail-item">
                <label>{{ $t('configuration.common.createdAt') }}:</label>
                <span>{{ formatDateTime(config.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="configs.length === 0" class="empty-state">
          <div class="empty-icon"></div>
          <h3>{{ $t('configuration.aiMode.emptyTitle') }}</h3>
          <p>{{ $t('configuration.aiMode.emptyDescription') }}</p>
          <button class="add-first-config-btn" @click="openAddModal">
            {{ $t('configuration.aiMode.addFirstConfig') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 添加/编辑配置弹窗 -->
    <div v-show="shouldShowModal" :class="['config-modal', { hidden: !shouldShowModal }]" @click="closeModals" @keydown.esc="closeModals">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditing ? $t('configuration.aiMode.editConfig') : $t('configuration.aiMode.addConfigTitle') }}</h3>
          <button class="close-btn" @click.stop="closeModals" type="button">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveConfig">
            <div class="form-group">
              <label>{{ $t('configuration.aiMode.configName') }} <span class="required">*</span></label>
              <input
                v-model="configForm.name"
                type="text"
                class="form-input"
                :placeholder="$t('configuration.aiMode.configNamePlaceholder')"
                required>
            </div>

            <div class="form-group">
              <label>{{ $t('configuration.aiMode.modelProvider') }} <span class="required">*</span></label>
              <select
                v-model="configForm.model_type"
                class="form-select"
                required
                @change="onModelTypeChange">
                <option value="">{{ $t('configuration.aiMode.selectProvider') }}</option>
                <option value="openai">{{ $t('configuration.aiMode.providers.openai') }}</option>
                <option value="azure_openai">{{ $t('configuration.aiMode.providers.azure_openai') }}</option>
                <option value="anthropic">{{ $t('configuration.aiMode.providers.anthropic') }}</option>
                <option value="google_gemini">{{ $t('configuration.aiMode.providers.google_gemini') }}</option>
                <option value="deepseek">{{ $t('configuration.aiMode.providers.deepseek') }}</option>
                <option value="siliconflow">{{ $t('configuration.aiMode.providers.siliconflow') }}</option>
                <option value="other">{{ $t('configuration.aiMode.providers.other') }}</option>
              </select>
            </div>

            <div class="form-group">
              <label>{{ $t('configuration.aiMode.modelName') }} <span class="required">*</span></label>
              <input
                v-model="configForm.model_name"
                type="text"
                class="form-input"
                :placeholder="$t('configuration.aiMode.modelNamePlaceholder')"
                required>
            </div>

            <div class="form-group">
              <label>{{ $t('configuration.aiMode.apiKey') }} <span class="required">*</span></label>
              <input
                v-model="configForm.api_key"
                type="password"
                class="form-input"
                :placeholder="isEditing ? $t('configuration.aiMode.apiKeyPlaceholderEdit') : $t('configuration.aiMode.apiKeyPlaceholder')"
                :required="!isEditing">
              <small v-if="isEditing && configForm.api_key && configForm.api_key.includes('*')" class="form-hint">
                {{ $t('configuration.aiMode.apiKeyMaskHint') }}
              </small>
            </div>

            <div class="form-group">
              <label>{{ $t('configuration.aiMode.baseUrl') }}</label>
              <input
                v-model="configForm.base_url"
                type="url"
                class="form-input"
                :placeholder="$t('configuration.aiMode.baseUrlPlaceholder')">
              <small class="form-hint">
                {{ $t('configuration.aiMode.baseUrlHint') }}
              </small>
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input v-model="configForm.is_active" type="checkbox">
                <span class="checkmark"></span>
                {{ $t('configuration.aiMode.enableConfig') }}
              </label>
              <small class="form-hint">
                {{ $t('configuration.aiMode.enableConfigHint') }}
              </small>
            </div>

            <div class="modal-actions">
              <button type="button" class="cancel-btn" @click="closeModals">{{ $t('configuration.common.cancel') }}</button>
              <button type="button" class="test-btn-form" @click="testConnectionInModal">
                <span v-if="isTestingInModal">{{ $t('configuration.aiMode.testing') }}</span>
                <span v-else>{{ $t('configuration.aiMode.testConnection') }}</span>
              </button>
              <button type="submit" class="confirm-btn" :disabled="isSaving">
                <span v-if="isSaving">{{ $t('configuration.aiMode.saving') }}</span>
                <span v-else>{{ $t('configuration.aiMode.saveConfig') }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 连接测试结果弹窗 -->
    <div v-if="showTestResult" class="test-result-modal" @keydown.esc="closeTestResult">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ $t('configuration.aiMode.testResult') }}</h3>
          <button class="close-btn" @click="closeTestResult">×</button>
        </div>
        <div class="modal-body">
          <div class="test-result" :class="{ success: testResult.success, error: !testResult.success }">
            <div class="result-icon">
              {{ testResult.success ? '' : '' }}
            </div>
            <div class="result-content">
              <h4>{{ testResult.success ? $t('configuration.aiMode.connectionSuccess') : $t('configuration.aiMode.connectionFailed') }}</h4>
              <p>{{ testResult.message }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

const { t } = useI18n()

const configs = ref([])
const showAddModal = ref(false)
const showEditModal = ref(false)
const showTestResult = ref(false)
const isEditing = ref(false)
const isSaving = ref(false)
const isTestingInModal = ref(false)
const editingConfigId = ref(null)
const testResult = ref({
  success: false,
  message: ''
})

const configForm = ref({
  name: '',
  model_type: '',
  model_name: '',
  api_key: '',
  base_url: '',
  is_active: true
})

// 模型提供商与Base URL的映射关系
const modelBaseUrlMap = {
  openai: 'https://api.openai.com/v1',
  azure_openai: '',
  anthropic: 'https://api.anthropic.com',
  google_gemini: '',
  deepseek: 'https://api.deepseek.com',
  siliconflow: 'https://api.siliconflow.cn/v1',
  other: ''
}

const shouldShowModal = computed(() => showAddModal.value || showEditModal.value)

const getProviderLabel = (modelType) => {
  const key = `configuration.aiMode.providers.${modelType}`
  const translated = t(key)
  // 如果翻译key存在则返回翻译，否则返回原值
  return translated !== key ? translated : modelType
}

const loadConfigs = async () => {
  try {
    const response = await api.get('/ui-automation/ai-models/')
    if (response.data && Array.isArray(response.data)) {
      configs.value = response.data.map(config => ({
        ...config,
        toggling: false,
        testing: false
      }))
    }
  } catch (error) {
    console.error('Load config failed:', error)
    ElMessage.error(t('configuration.aiMode.messages.loadFailed'))
  }
}

const openAddModal = () => {
  resetForm()
  isEditing.value = false
  showAddModal.value = true
}

const resetForm = () => {
  configForm.value = {
    name: '',
    model_type: '',
    model_name: '',
    api_key: '',
    base_url: '',
    is_active: true
  }
}

const editConfig = (config) => {
  isEditing.value = true
  editingConfigId.value = config.id

  // 使用后端返回的api_key_length生成掩码
  const maskLength = Math.max(config.api_key_length || 8, 8)
  const maskedKey = '*'.repeat(maskLength)

  configForm.value = {
    name: config.name,
    model_type: config.model_type,
    model_name: config.model_name,
    api_key: maskedKey, // 显示与原API Key相同长度的掩码
    base_url: config.base_url,
    is_active: config.is_active
  }
  showEditModal.value = true
}

const onModelTypeChange = () => {
  // 根据选择的提供商自动填充base_url
  if (modelBaseUrlMap[configForm.value.model_type]) {
    configForm.value.base_url = modelBaseUrlMap[configForm.value.model_type]
  }

  // 根据提供商自动填充模型名称建议
  if (configForm.value.model_type === 'openai' && !configForm.value.model_name) {
    configForm.value.model_name = 'gpt-4o'
  } else if (configForm.value.model_type === 'anthropic' && !configForm.value.model_name) {
    configForm.value.model_name = 'claude-3-5-sonnet-20241022'
  } else if (configForm.value.model_type === 'deepseek' && !configForm.value.model_name) {
    configForm.value.model_name = 'deepseek-chat'
  } else if (configForm.value.model_type === 'siliconflow' && !configForm.value.model_name) {
    configForm.value.model_name = 'Qwen/Qwen2.5-7B-Instruct'
  }
}

const saveConfig = async () => {
  const requiredFields = [
    { name: 'name', value: configForm.value.name },
    { name: 'model_type', value: configForm.value.model_type },
    { name: 'model_name', value: configForm.value.model_name },
    { name: 'api_key', value: configForm.value.api_key }
  ]

  const emptyFields = requiredFields.filter(field => !field.value || (typeof field.value === 'string' && field.value.trim() === ''))

  if (emptyFields.length > 0) {
    ElMessage.error(`${t('configuration.aiMode.messages.fillRequired')}: ${emptyFields.map(f => f.name).join(', ')}`)
    return
  }

  isSaving.value = true

  try {
    const saveData = { ...configForm.value }

    if (isEditing.value) {
      // 编辑时，如果API Key是掩码格式或为空，则不更新它
      if (!saveData.api_key || saveData.api_key.includes('*')) {
        delete saveData.api_key
      }

      const response = await api.put(`/ui-automation/ai-models/${editingConfigId.value}/`, saveData)

      // 检查是否禁用了其他配置
      if (response.data.disabled_configs && response.data.disabled_configs.length > 0) {
        ElMessage.success(
          t('configuration.aiMode.messages.configEnabled', { name: configForm.value.name, configs: response.data.disabled_configs.join(', ') })
        )
      } else {
        ElMessage.success(t('configuration.aiMode.messages.updateSuccess'))
      }
    } else {
      // 新增配置
      const response = await api.post('/ui-automation/ai-models/', saveData)

      // 检查是否禁用了其他配置
      if (response.data.disabled_configs && response.data.disabled_configs.length > 0) {
        ElMessage.success(
          t('configuration.aiMode.messages.configAdded', { name: configForm.value.name, configs: response.data.disabled_configs.join(', ') })
        )
      } else {
        ElMessage.success(t('configuration.aiMode.messages.saveSuccess'))
      }
    }

    closeModals()
    await loadConfigs()
  } catch (error) {
    console.error('Save config failed:', error)
    ElMessage.error(t('configuration.aiMode.messages.saveFailed') + ': ' + (error.response?.data?.error || error.message))
  } finally {
    isSaving.value = false
  }
}

const deleteConfig = async (configId) => {
  try {
    await ElMessageBox.confirm(
      t('configuration.aiMode.messages.deleteConfirm'),
      t('configuration.common.confirm'),
      {
        confirmButtonText: t('configuration.common.confirm'),
        cancelButtonText: t('configuration.common.cancel'),
        type: 'warning'
      }
    )
  } catch {
    return
  }

  try {
    await api.delete(`/ui-automation/ai-models/${configId}/`)
    ElMessage.success(t('configuration.aiMode.messages.deleteSuccess'))
    await loadConfigs()
  } catch (error) {
    console.error('Delete config failed:', error)
    ElMessage.error(t('configuration.aiMode.messages.deleteFailed') + ': ' + (error.response?.data?.error || error.message))
  }
}

const toggleActive = async (config) => {
  // 如果要启用配置,检查是否有其他已启用的配置
  if (config.is_active) {
    const activeConfigs = configs.value.filter(c => c.id !== config.id && c.is_active)
    if (activeConfigs.length > 0) {
      const activeConfigNames = activeConfigs.map(c => c.name).join(', ')
      try {
        await ElMessageBox.confirm(
          t('configuration.aiMode.messages.toggleConfirm', { name: config.name, configs: activeConfigNames }),
          t('configuration.common.confirm'),
          {
            confirmButtonText: t('configuration.common.confirm'),
            cancelButtonText: t('configuration.common.cancel'),
            type: 'warning'
          }
        )
      } catch {
        // 恢复开关状态
        config.is_active = false
        return
      }
    }
  }

  config.toggling = true

  try {
    await api.patch(`/ui-automation/ai-models/${config.id}/`, {
      is_active: config.is_active
    })

    ElMessage.success(t('configuration.aiMode.messages.toggleSuccess', { status: config.is_active ? t('configuration.common.enabled') : t('configuration.common.disabled') }))
    await loadConfigs()
  } catch (error) {
    console.error('Toggle status failed:', error)
    ElMessage.error(t('configuration.aiMode.messages.toggleFailed') + ': ' + (error.response?.data?.error || error.message))
    // 回滚状态
    config.is_active = !config.is_active
  } finally {
    config.toggling = false
  }
}

const testConnection = async (config) => {
  config.testing = true

  try {
    // 测试连接需要更长的超时时间（90秒），因为大模型响应较慢
    await api.post(
      `/ui-automation/ai-models/${config.id}/test_connection/`,
      {},
      { timeout: 90000 }  // 90秒超时
    )
    testResult.value = {
      success: true,
      message: t('configuration.aiMode.connectionSuccessMsg')
    }
    showTestResult.value = true
  } catch (error) {
    console.error('Test connection failed:', error)
    testResult.value = {
      success: false,
      message: error.response?.data?.error || error.message || t('configuration.aiMode.connectionFailed')
    }
    showTestResult.value = true
  } finally {
    config.testing = false
  }
}

const testConnectionInModal = async () => {
  // 验证必填字段
  if (!configForm.value.api_key) {
    ElMessage.warning(t('configuration.aiMode.messages.enterApiKey'))
    return
  }

  if (!configForm.value.model_type || !configForm.value.model_name) {
    ElMessage.warning(t('configuration.aiMode.messages.selectProviderModel'))
    return
  }

  // 编辑模式下,如果API Key是掩码(用户未修改),使用已保存配置的测试接口
  if (isEditing.value && configForm.value.api_key.includes('*')) {
    isTestingInModal.value = true
    try {
      // 测试连接需要90秒超时
      await api.post(
        `/ui-automation/ai-models/${editingConfigId.value}/test_connection/`,
        {},
        { timeout: 90000 }
      )

      testResult.value = {
        success: true,
        message: t('configuration.aiMode.connectionSuccessMsg')
      }
      showTestResult.value = true
    } catch (error) {
      console.error('Test connection failed:', error)
      testResult.value = {
        success: false,
        message: error.response?.data?.error || error.message || t('configuration.aiMode.connectionFailed')
      }
      showTestResult.value = true
    } finally {
      isTestingInModal.value = false
    }
    return
  }

  // 新增模式,或编辑模式已修改API Key
  isTestingInModal.value = true

  try {
    // 测试连接需要90秒超时
    await api.post(
      '/ui-automation/ai-models/test_connection/',
      {
        provider: configForm.value.model_type,
        model_name: configForm.value.model_name,
        api_key: configForm.value.api_key,
        base_url: configForm.value.base_url
      },
      { timeout: 90000 }
    )

    testResult.value = {
      success: true,
      message: t('configuration.aiMode.connectionSuccessMsg')
    }
    showTestResult.value = true
  } catch (error) {
    console.error('Test connection failed:', error)
    testResult.value = {
      success: false,
      message: error.response?.data?.error || error.message || t('configuration.aiMode.connectionFailed')
    }
    showTestResult.value = true
  } finally {
    isTestingInModal.value = false
  }
}

const closeModals = () => {
  showAddModal.value = false
  showEditModal.value = false
  isEditing.value = false
  editingConfigId.value = null
  resetForm()
}

const closeTestResult = () => {
  showTestResult.value = false
}

const formatDateTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const locale = t('configuration.common.locale') || 'zh-CN'
  return date.toLocaleString(locale, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadConfigs()
})
</script>

<style scoped>
.ai-mode-config {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 10px;
}

.page-header p {
  color: #666;
  font-size: 1.1rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.section-header h2 {
  color: #2c3e50;
  margin: 0;
}

.add-config-btn {
  background: #27ae60;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.3s ease;
}

.add-config-btn:hover {
  background: #219a52;
}

.configs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
  gap: 20px;
}

.config-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border: 1px solid #e1e8ed;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.config-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  gap: 15px;
}

.config-title h3 {
  color: #2c3e50;
  margin: 0 0 10px 0;
  font-size: 1.3rem;
}

.config-badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.provider-badge, .model-name-badge, .status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

.provider-badge.openai {
  background: #e3f2fd;
  color: #1976d2;
}

.provider-badge.anthropic {
  background: #fff3e0;
  color: #e65100;
}

.provider-badge.deepseek {
  background: #e3f2fd;
  color: #1976d2;
}

.provider-badge.siliconflow {
  background: #e0f7fa;
  color: #006064;
}

.provider-badge.other {
  background: #eceff1;
  color: #455a64;
}

.model-name-badge {
  background: #f3e5f5;
  color: #7b1fa2;
}

.status-badge {
  background: #ffebee;
  color: #d32f2f;
}

.status-badge.active {
  background: #e8f5e8;
  color: #388e3c;
}

.config-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.test-btn, .edit-btn, .delete-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background 0.3s ease;
}

.test-btn {
  background: #3498db;
  color: white;
}

.test-btn:hover:not(:disabled) {
  background: #2980b9;
}

.test-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.edit-btn {
  background: #f39c12;
  color: white;
}

.edit-btn:hover {
  background: #e67e22;
}

.delete-btn {
  background: #e74c3c;
  color: white;
}

.delete-btn:hover {
  background: #c0392b;
}

.config-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item label {
  font-size: 0.85rem;
  color: #666;
  font-weight: 600;
}

.detail-item span {
  color: #2c3e50;
  font-size: 0.9rem;
  word-break: break-all;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #666;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.empty-state h3 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.add-first-config-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.1rem;
  margin-top: 20px;
  transition: background 0.3s ease;
}

.add-first-config-btn:hover {
  background: #2980b9;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
}

.close-btn {
  background: none !important;
  border: none !important;
  font-size: 1.5rem !important;
  cursor: pointer !important;
  color: #666 !important;
  padding: 5px 10px !important;
  z-index: 10001 !important;
  position: relative !important;
  pointer-events: auto !important;
}

.close-btn:hover {
  color: #333 !important;
  background: #f0f0f0 !important;
  border-radius: 3px !important;
}

.modal-body {
  padding: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #2c3e50;
}

.form-input, .form-select {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-input:focus, .form-select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  user-select: none;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
}

.required {
  color: #e74c3c;
}

.form-hint {
  display: block;
  margin-top: 5px;
  color: #666;
  font-size: 0.85rem;
  font-style: italic;
}

.modal-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 30px;
}

.cancel-btn, .test-btn-form, .confirm-btn {
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
}

.cancel-btn {
  background: #95a5a6;
}

.cancel-btn:hover {
  background: #7f8c8d;
}

.test-btn-form {
  background: #3498db;
}

.test-btn-form:hover {
  background: #2980b9;
}

.confirm-btn {
  background: #27ae60;
}

.confirm-btn:hover:not(:disabled) {
  background: #219a52;
}

.confirm-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.test-result {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.result-icon {
  font-size: 3rem;
  flex-shrink: 0;
}

.result-content h4 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.test-result.success .result-content h4 {
  color: #27ae60;
}

.test-result.error .result-content h4 {
  color: #e74c3c;
}

@media (max-width: 768px) {
  .configs-grid {
    grid-template-columns: 1fr;
  }

  .config-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }

  .config-details {
    grid-template-columns: 1fr;
  }
}
</style>

<style>
/* 全局样式，不受scoped限制 */
.config-modal, .test-result-modal {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  background: rgba(0, 0, 0, 0.5) !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  z-index: 9999 !important;
  visibility: visible !important;
  opacity: 1 !important;
}

/* 隐藏状态 */
.config-modal.hidden, .test-result-modal.hidden {
  display: none !important;
  visibility: hidden !important;
  opacity: 0 !important;
}

.config-modal .modal-content, .test-result-modal .modal-content {
  background: white !important;
  border-radius: 12px !important;
  padding: 0 !important;
  max-width: 600px !important;
  width: 90% !important;
  max-height: 90vh !important;
  overflow-y: auto !important;
  position: relative !important;
  z-index: 10000 !important;
}
</style>
