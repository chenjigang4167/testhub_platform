<template>
  <div class="ai-model-config">
    <div class="page-header">
      <h1>{{ $t('configuration.aiModel.title') }}</h1>
      <p>{{ $t('configuration.aiModel.description') }}</p>
    </div>

    <div class="main-content">
      <!-- 配置列表 -->
      <div class="configs-section">
        <div class="section-header">
          <h2>{{ $t('configuration.aiModel.configList') }}</h2>
          <button
            class="add-config-btn"
            @click.stop="openAddModal"
            type="button">
            {{ $t('configuration.aiModel.addConfig') }}
          </button>
        </div>

        <div class="configs-grid">
          <template v-for="config in configs" :key="config?.id || 'unknown'">
            <div v-if="config && config.id" class="config-card">
              <div class="config-header">
                <div class="config-title">
                  <h3>{{ config.name || $t('configuration.common.unnamed') }}</h3>
                  <div class="config-badges">
                    <span class="model-badge" :class="config.model_type">
                      {{ $t('configuration.aiModel.modelTypes.' + config.model_type) }}
                    </span>
                    <span class="role-badge" :class="config.role">
                      {{ $t('configuration.aiModel.roles.' + config.role) }}
                    </span>
                    <span class="status-badge" :class="{ active: config.is_active }">
                      {{ config.is_active ? $t('configuration.common.enabled') : $t('configuration.common.disabled') }}
                    </span>
                  </div>
                </div>
                <div class="config-actions">
                  <button
                    class="test-btn"
                    @click="testConnection(config)"
                    :disabled="isTestingConnection">
                    {{ $t('configuration.aiModel.testConnection') }}
                  </button>
                  <button class="edit-btn" @click="editConfig(config)">{{ $t('configuration.common.edit') }}</button>
                  <button class="delete-btn" @click="deleteConfig(config.id)">{{ $t('configuration.common.delete') }}</button>
                </div>
              </div>

              <div class="config-details">
              <div class="detail-item">
                <label>{{ $t('configuration.aiModel.baseUrl') }}:</label>
                <span>{{ config.base_url }}</span>
              </div>
              <div class="detail-item">
                <label>{{ $t('configuration.aiModel.modelName') }}:</label>
                <span>{{ config.model_name }}</span>
              </div>
              <div class="detail-item">
                <label>{{ $t('configuration.aiModel.maxTokens') }}:</label>
                <span>{{ config.max_tokens }}</span>
              </div>
              <div class="detail-item">
                <label>{{ $t('configuration.aiModel.temperature') }}:</label>
                <span>{{ config.temperature }}</span>
              </div>
              <div class="detail-item">
                <label>{{ $t('configuration.aiModel.topP') }}:</label>
                <span>{{ config.top_p }}</span>
              </div>
              <div class="detail-item">
                <label>{{ $t('configuration.common.createdAt') }}:</label>
                <span>{{ formatDateTime(config.created_at) }}</span>
              </div>
              </div>
            </div>
          </template>
        </div>

        <div v-if="configs.length === 0" class="empty-state">
          <div class="empty-icon"></div>
          <h3>{{ $t('configuration.aiModel.emptyTitle') }}</h3>
          <p>{{ $t('configuration.aiModel.emptyDescription') }}</p>
          <button
            class="add-first-config-btn"
            @click.stop="openAddModal"
            type="button">
            {{ $t('configuration.aiModel.addFirstConfig') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 添加/编辑配置弹窗 -->
    <div
      v-show="shouldShowModal"
      :class="['config-modal', { hidden: !shouldShowModal }]"
      @click="closeModals"
      @keydown.esc="closeModals">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditing ? $t('configuration.aiModel.editConfig') : $t('configuration.aiModel.addConfigTitle') }}</h3>
          <button class="close-btn" @click.stop="closeModals" type="button">x</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveConfig">
            <div class="form-group">
              <label>{{ $t('configuration.aiModel.configName') }} <span class="required">*</span></label>
              <input
                v-model="configForm.name"
                type="text"
                class="form-input"
                :placeholder="$t('configuration.aiModel.configNamePlaceholder')"
                required>
            </div>

            <div class="form-group">
              <label>{{ $t('configuration.aiModel.modelType') }} <span class="required">*</span></label>
              <select
                v-model="configForm.model_type"
                class="form-select"
                required
                @change="onModelTypeChange(configForm.model_type)">
                <option value="">{{ $t('configuration.aiModel.selectModelType') }}</option>
                <option value="deepseek">{{ $t('configuration.aiModel.modelTypes.deepseek') }}</option>
                <option value="qwen">{{ $t('configuration.aiModel.modelTypes.qwen') }}</option>
                <option value="siliconflow">{{ $t('configuration.aiModel.modelTypes.siliconflow') }}</option>
                <option value="other">{{ $t('configuration.aiModel.modelTypes.other') }}</option>
              </select>
            </div>

            <div class="form-group">
              <label>{{ $t('configuration.aiModel.role') }} <span class="required">*</span></label>
              <select
                v-model="configForm.role"
                class="form-select"
                required
                @change="console.log('Role changed to:', configForm.role)">
                <option value="">{{ $t('configuration.aiModel.selectRole') }}</option>
                <option value="writer">{{ $t('configuration.aiModel.roles.writer') }}</option>
                <option value="reviewer">{{ $t('configuration.aiModel.roles.reviewer') }}</option>
              </select>
            </div>

            <div class="form-group">
              <label>{{ $t('configuration.aiModel.apiKey') }} <span class="required">*</span></label>
              <input
                v-model="configForm.api_key"
                type="password"
                class="form-input"
                :placeholder="isEditing ? $t('configuration.aiModel.apiKeyPlaceholderEdit') : $t('configuration.aiModel.apiKeyPlaceholder')"
                :required="!isEditing">
              <small v-if="isEditing && configForm.api_key && configForm.api_key.includes('*')" class="form-hint">
                {{ $t('configuration.aiModel.apiKeyMaskHint') }}
              </small>
            </div>

            <div class="form-group">
              <label>{{ $t('configuration.aiModel.baseUrl') }} <span class="required">*</span></label>
              <input
                v-model="configForm.base_url"
                type="url"
                class="form-input"
                :placeholder="$t('configuration.aiModel.baseUrlPlaceholder')"
                required>
              <small class="form-hint">
                {{ $t('configuration.aiModel.baseUrlHint') }}
              </small>
            </div>

            <div class="form-group">
              <label>{{ $t('configuration.aiModel.modelName') }} <span class="required">*</span></label>
              <input
                v-model="configForm.model_name"
                type="text"
                class="form-input"
                :placeholder="$t('configuration.aiModel.modelNamePlaceholder')"
                required>
              <small class="form-hint">
                {{ $t('configuration.aiModel.modelNameHint') }}
              </small>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>{{ $t('configuration.aiModel.maxTokens') }}</label>
                <input
                  v-model.number="configForm.max_tokens"
                  type="number"
                  min="100"
                  max="32000"
                  class="form-input"
                  placeholder="4096">
              </div>

              <div class="form-group">
                <label>{{ $t('configuration.aiModel.temperature') }}</label>
                <input
                  v-model.number="configForm.temperature"
                  type="number"
                  min="0"
                  max="2"
                  step="0.1"
                  class="form-input"
                  placeholder="0.7">
              </div>

              <div class="form-group">
                <label>{{ $t('configuration.aiModel.topP') }}</label>
                <input
                  v-model.number="configForm.top_p"
                  type="number"
                  min="0"
                  max="1"
                  step="0.1"
                  class="form-input"
                  placeholder="0.9">
              </div>
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input
                  v-model="configForm.is_active"
                  type="checkbox">
                <span class="checkmark"></span>
                {{ $t('configuration.aiModel.enableConfig') }}
              </label>
            </div>

            <div class="modal-actions">
              <button type="button" class="cancel-btn" @click="closeModals">{{ $t('configuration.common.cancel') }}</button>
              <button
                type="submit"
                class="confirm-btn"
                :disabled="isSaving">
                <span v-if="isSaving">{{ $t('configuration.aiModel.saving') }}</span>
                <span v-else>{{ $t('configuration.aiModel.saveConfig') }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 连接测试结果弹窗 -->
    <div v-if="showTestResult" class="test-result-modal" @click="closeTestResult">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ $t('configuration.aiModel.testResult') }}</h3>
          <button class="close-btn" @click="closeTestResult">x</button>
        </div>
        <div class="modal-body">
          <div class="test-result" :class="{ success: testResult.success, error: !testResult.success }">
            <div class="result-icon">
              {{ testResult.success ? '✅' : '❌' }}
            </div>
            <div class="result-content">
              <h4>{{ testResult.success ? $t('configuration.aiModel.connectionSuccess') : $t('configuration.aiModel.connectionFailed') }}</h4>
              <p>{{ testResult.message }}</p>
              <div v-if="testResult.response" class="api-response">
                <label>{{ $t('configuration.aiModel.aiResponse') }}:</label>
                <p>{{ testResult.response }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'

export default {
  name: 'AIModelConfig',
  setup() {
    const { t } = useI18n()
    return { t }
  },
  data() {
    return {
      configs: [], // 确保初始化为空数组
      showAddModal: false,
      showEditModal: false,
      showTestResult: false,
      isEditing: false,
      isSaving: false,
      isTestingConnection: false,
      testingConfigId: null,
      editingConfigId: null,
      configForm: {
        name: '',
        model_type: '',
        role: '',
        api_key: '',
        base_url: '',
        model_name: '',
        max_tokens: 4096,
        temperature: 0.7,
        top_p: 0.9,
        is_active: true
      },
      // 模型类型与API Base URL的映射关系
      modelBaseUrlMap: {
        deepseek: 'https://api.deepseek.com',
        qwen: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
        siliconflow: 'https://api.siliconflow.cn/v1',
        other: ''
      },
      testResult: {
        success: false,
        message: '',
        response: ''
      }
    }
  },

  computed: {
    shouldShowModal() {
      const show = this.showAddModal || this.showEditModal
      console.log('Computed shouldShowModal:', show, {
        showAddModal: this.showAddModal,
        showEditModal: this.showEditModal
      })
      return show
    }
  },

  watch: {
    configForm: {
      handler(newVal, oldVal) {
        console.log('ConfigForm changed:', JSON.stringify(newVal))
      },
      deep: true
    },
    shouldShowModal(newVal, oldVal) {
      console.log('Modal visibility changed:', newVal, 'was:', oldVal)
    }
  },

  mounted() {
    console.log('AIModelConfig component mounted')
    console.log('Initial showAddModal state:', this.showAddModal)
    console.log('Initial showEditModal state:', this.showEditModal)
    console.log('Initial configForm:', JSON.stringify(this.configForm))
    
    // 确保组件初始状态正确
    this.initializeComponent()
    
    this.loadConfigs()
  },

  methods: {
    // 当模型类型改变时自动填充API Base URL
    onModelTypeChange(modelType) {
      console.log('Model type changed to:', modelType)

      // 根据选择的模型类型自动填充base_url
      if (this.modelBaseUrlMap[modelType]) {
        this.configForm.base_url = this.modelBaseUrlMap[modelType]
        console.log('Auto-filled base_url:', this.configForm.base_url)
      }

      // 根据模型类型自动填充模型名称建议
      if (modelType === 'deepseek' && !this.configForm.model_name) {
        this.configForm.model_name = 'deepseek-chat'
      } else if (modelType === 'qwen' && !this.configForm.model_name) {
        this.configForm.model_name = 'qwen-plus'
      } else if (modelType === 'siliconflow' && !this.configForm.model_name) {
        this.configForm.model_name = 'Qwen/Qwen2.5-7B-Instruct'
      }
    },

    initializeComponent() {
      // 强制重置所有状态
      this.showAddModal = false
      this.showEditModal = false
      this.showTestResult = false
      this.isEditing = false
      this.isSaving = false
      this.isTestingConnection = false
      this.testingConfigId = null
      this.editingConfigId = null
      
      console.log('Component initialized with states:', {
        showAddModal: this.showAddModal,
        showEditModal: this.showEditModal,
        isEditing: this.isEditing
      })
    },
    async loadConfigs() {
      try {
        console.log('Loading configs...')
        const response = await api.get('/requirement-analysis/ai-models/')
        console.log('API response:', response.data)
        
        // 处理分页API响应格式 {count: 1, next: null, previous: null, results: [...]}
        if (response.data && response.data.results && Array.isArray(response.data.results)) {
          this.configs = response.data.results.filter(config => config && config.id)
          console.log('Loaded configs from results:', this.configs)
        } else if (response.data && Array.isArray(response.data)) {
          // 直接数组格式的fallback
          this.configs = response.data.filter(config => config && config.id)
          console.log('Loaded configs from direct array:', this.configs)
        } else {
          console.warn('Unexpected API response format:', response.data)
          this.configs = []
        }
        
        console.log('Final configs count:', this.configs.length)
      } catch (error) {
        console.error('Failed to load configs:', error)
        this.configs = [] // 确保configs始终是数组

        if (error.response?.status === 401) {
          ElMessage.error(this.t('configuration.aiModel.messages.pleaseLogin'))
        } else {
          ElMessage.error(this.t('configuration.aiModel.messages.loadFailedDetail', { error: error.response?.data?.error || error.message }))
        }
      }
    },

    openAddModal() {
      console.log('Opening add modal - button clicked')
      try {
        this.resetForm()
        this.isEditing = false
        this.showAddModal = true
        console.log('Modal state set to true:', this.showAddModal)
        console.log('Initial form after reset:', JSON.stringify(this.configForm))
        
        // 强制Vue重新渲染
        this.$nextTick(() => {
          console.log('Modal should be visible now:', this.showAddModal)
          console.log('Form in nextTick:', JSON.stringify(this.configForm))
        })
      } catch (error) {
        console.error('Error in openAddModal:', error)
      }
    },

    resetForm() {
      // 使用Object.assign确保响应式
      Object.assign(this.configForm, {
        name: '',
        model_type: '',
        role: '',
        api_key: '',
        base_url: '',
        model_name: '',
        max_tokens: 4096,
        temperature: 0.7,
        top_p: 0.9,
        is_active: true
      })
      console.log('Form reset:', JSON.stringify(this.configForm))
    },

    editConfig(config) {
      this.isEditing = true
      this.editingConfigId = config.id
      this.configForm = {
        name: config.name,
        model_type: config.model_type,
        role: config.role,
        api_key: config.api_key_masked || '', // 显示掩码版本的API Key
        base_url: config.base_url,
        model_name: config.model_name,
        max_tokens: config.max_tokens,
        temperature: config.temperature,
        top_p: config.top_p,
        is_active: config.is_active
      }
      this.showEditModal = true
    },

    async saveConfig() {
      console.log('Saving config with data:', this.configForm)
      
      // 详细检查每个字段
      console.log('Field values:')
      console.log('- name:', this.configForm.name, 'length:', this.configForm.name?.length)
      console.log('- model_type:', this.configForm.model_type, 'length:', this.configForm.model_type?.length)
      console.log('- role:', this.configForm.role, 'length:', this.configForm.role?.length)
      console.log('- api_key:', this.configForm.api_key, 'length:', this.configForm.api_key?.length)
      console.log('- base_url:', this.configForm.base_url, 'length:', this.configForm.base_url?.length)
      console.log('- model_name:', this.configForm.model_name, 'length:', this.configForm.model_name?.length)
      
      // 验证必填字段
      const requiredFields = [
        { name: 'name', value: this.configForm.name },
        { name: 'model_type', value: this.configForm.model_type },
        { name: 'role', value: this.configForm.role },
        { name: 'api_key', value: this.configForm.api_key },
        { name: 'base_url', value: this.configForm.base_url },
        { name: 'model_name', value: this.configForm.model_name }
      ]
      
      const emptyFields = requiredFields.filter(field => !field.value || field.value.trim() === '')
      
      if (emptyFields.length > 0) {
        console.log('Empty fields:', emptyFields)
        ElMessage.error(this.t('configuration.aiModel.messages.fillRequired', { fields: emptyFields.map(f => f.name).join(', ') }))
        return
      }
      
      // 检查唯一约束冲突（仅在创建新配置且is_active为true时）
      if (!this.isEditing && this.configForm.is_active) {
        const existingConfig = this.configs.find(config => 
          config.model_type === this.configForm.model_type && 
          config.role === this.configForm.role && 
          config.is_active === true
        )
        
        if (existingConfig) {
          ElMessage.error(this.t('configuration.aiModel.messages.duplicateConfig', { name: existingConfig.name }))
          return
        }
      }
      
      this.isSaving = true
      
      try {
        if (this.isEditing) {
          // 编辑时，如果API Key是掩码格式或为空，则不更新它
          const updateData = { ...this.configForm }
          if (!updateData.api_key || updateData.api_key.includes('*')) {
            delete updateData.api_key
          }
          
          console.log('Updating with data:', updateData)
          await api.patch(`/requirement-analysis/ai-models/${this.editingConfigId}/`, updateData)
          ElMessage.success(this.t('configuration.aiModel.messages.updateSuccess'))
        } else {
          console.log('Creating with data:', this.configForm)
          await api.post('/requirement-analysis/ai-models/', this.configForm)
          ElMessage.success(this.t('configuration.aiModel.messages.saveSuccess'))
        }
        
        this.closeModals()
        
        // 等待模态框关闭后再刷新数据
        await this.$nextTick()
        await this.loadConfigs()
        
        // 强制重新渲染确保列表更新
        this.$forceUpdate()
        
        console.log('Config saved and list refreshed, total configs:', this.configs.length)
      } catch (error) {
        console.error('Failed to save config:', error)
        console.error('Error response:', error.response?.data)

        if (error.response?.data) {
          const errors = error.response.data
          let errorMessage = this.t('configuration.aiModel.messages.saveFailed') + ': '

          // 处理唯一约束错误
          if (errors.non_field_errors) {
            const uniqueConstraintError = errors.non_field_errors.find(err =>
              err.includes('唯一集合') || err.includes('unique')
            )
            if (uniqueConstraintError) {
              errorMessage = this.t('configuration.aiModel.messages.conflictError')
            } else {
              errorMessage += errors.non_field_errors.join(', ')
            }
          } else {
            // 处理字段特定错误
            Object.keys(errors).forEach(field => {
              if (Array.isArray(errors[field])) {
                errorMessage += `${field}: ${errors[field].join(', ')}; `
              } else {
                errorMessage += `${field}: ${errors[field]}; `
              }
            })
          }

          ElMessage.error(errorMessage)
        } else {
          ElMessage.error(this.t('configuration.aiModel.messages.saveFailedDetail', { error: error.message }))
        }
      } finally {
        this.isSaving = false
      }
    },

    async deleteConfig(configId) {
      try {
        await ElMessageBox.confirm(
          this.t('configuration.aiModel.messages.deleteConfirm'),
          this.t('configuration.aiModel.messages.deleteTitle'),
          {
            confirmButtonText: this.t('configuration.common.confirm'),
            cancelButtonText: this.t('configuration.common.cancel'),
            type: 'warning'
          }
        )
      } catch {
        return
      }

      try {
        await api.delete(`/requirement-analysis/ai-models/${configId}/`)
        ElMessage.success(this.t('configuration.aiModel.messages.deleteSuccess'))
        this.loadConfigs()
      } catch (error) {
        console.error('Failed to delete config:', error)
        ElMessage.error(this.t('configuration.aiModel.messages.deleteFailedDetail', { error: error.response?.data?.error || error.message }))
      }
    },

    async testConnection(config) {
      this.isTestingConnection = true
      this.testingConfigId = config.id

      try {
        const response = await api.post(`/requirement-analysis/ai-models/${config.id}/test_connection/`)
        this.testResult = response.data
        this.showTestResult = true
      } catch (error) {
        console.error('Failed to test connection:', error)
        this.testResult = {
          success: false,
          message: error.response?.data?.message || error.message,
          response: ''
        }
        this.showTestResult = true
      } finally {
        this.isTestingConnection = false
        this.testingConfigId = null
      }
    },

    closeModals() {
      console.log('Closing modals - current states:', {
        showAddModal: this.showAddModal,
        showEditModal: this.showEditModal,
        isEditing: this.isEditing
      })
      
      this.showAddModal = false
      this.showEditModal = false
      this.isEditing = false
      this.editingConfigId = null
      this.resetForm()
      
      // 强制Vue重新渲染
      this.$nextTick(() => {
        console.log('After nextTick - states:', {
          showAddModal: this.showAddModal,
          showEditModal: this.showEditModal,
          shouldShow: this.shouldShowModal
        })
        
        // 强制更新组件
        this.$forceUpdate()
      })
      
      console.log('After closing - states:', {
        showAddModal: this.showAddModal,
        showEditModal: this.showEditModal,
        isEditing: this.isEditing
      })
    },

    closeTestResult() {
      this.showTestResult = false
    },

    formatDateTime(dateString) {
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
  }
}
</script>

<style scoped>
.ai-model-config {
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
  pointer-events: auto;
  z-index: 1;
  position: relative;
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

.model-badge, .role-badge, .status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

.model-badge.deepseek {
  background: #e3f2fd;
  color: #1976d2;
}

.model-badge.qwen {
  background: #f3e5f5;
  color: #7b1fa2;
}

.model-badge.siliconflow {
  background: #e0f7fa;
  color: #006064;
}

.model-badge.other {
  background: #eceff1;
  color: #455a64;
}

.role-badge.writer {
  background: #e8f5e8;
  color: #388e3c;
}

.role-badge.reviewer {
  background: #fff3e0;
  color: #f57c00;
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
  gap: 8px;
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
  pointer-events: auto;
  z-index: 1;
  position: relative;
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 15px;
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

.cancel-btn {
  background: #95a5a6;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
}

.cancel-btn:hover {
  background: #7f8c8d;
}

.confirm-btn {
  background: #27ae60;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
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

.api-response {
  margin-top: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #3498db;
}

.api-response label {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

.api-response p {
  margin: 0;
  color: #666;
  line-height: 1.5;
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
  
  .form-row {
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