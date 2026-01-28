<template>
  <div class="notification-configs-container">
    <!-- 页面说明 -->
    <div class="page-header">
      <h1 class="page-title">
        <el-icon class="title-icon">
          <Setting/>
        </el-icon>
        {{ $t('notification.configs.title') }}
      </h1>
      <p class="page-description">
        {{ $t('notification.configs.description') }}
      </p>
    </div>

    <!-- Tab切换 -->
    <div class="content-wrapper">
      <el-tabs v-model="activeTab" class="notification-tabs">


        <!-- 飞书机器人Tab -->
        <el-tab-pane :label="$t('notification.botTypes.feishu')" name="feishu">
          <div class="tab-content">
            <div class="config-section">
              <el-form
                  ref="feishuFormRef"
                  :model="webhookBots.feishu"
                  label-position="top"
                  class="config-form"
              >
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item :label="$t('notification.form.botName')">
                      <el-input
                          v-model="webhookBots.feishu.name"
                          :placeholder="$t('notification.placeholders.feishuBotName')"
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item :label="$t('notification.form.enabled')">
                      <el-switch v-model="webhookBots.feishu.enabled"/>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item :label="$t('notification.form.webhookUrl')">
                      <el-input
                          v-model="webhookBots.feishu.webhook_url"
                          :placeholder="$t('notification.placeholders.feishuWebhook')"
                      />
                      <div class="form-item-hint">
                        {{ $t('notification.hints.feishuWebhook') }}
                      </div>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item :label="$t('notification.form.businessType')">
                      <el-checkbox v-model="webhookBots.feishu.enable_ui_automation">{{ $t('notification.form.uiAutomation') }}</el-checkbox>
                      <el-checkbox v-model="webhookBots.feishu.enable_api_testing">{{ $t('notification.form.apiTesting') }}</el-checkbox>
                    </el-form-item>
                  </el-col>
                </el-row>

                <div class="form-actions">
                  <el-button type="primary" @click="saveWebhookBot('feishu')">
                    {{ $t('notification.buttons.saveFeishu') }}
                  </el-button>
                </div>
              </el-form>
            </div>
          </div>
        </el-tab-pane>

        <!-- 企业微信机器人Tab -->
        <el-tab-pane :label="$t('notification.botTypes.wechat')" name="wechat">
          <div class="tab-content">
            <div class="config-section">
              <el-form
                  ref="wechatFormRef"
                  :model="webhookBots.wechat"
                  label-position="top"
                  class="config-form"
              >
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item :label="$t('notification.form.botName')">
                      <el-input
                          v-model="webhookBots.wechat.name"
                          :placeholder="$t('notification.placeholders.wechatBotName')"
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item :label="$t('notification.form.enabled')">
                      <el-switch v-model="webhookBots.wechat.enabled"/>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item :label="$t('notification.form.webhookUrl')">
                      <el-input
                          v-model="webhookBots.wechat.webhook_url"
                          :placeholder="$t('notification.placeholders.wechatWebhook')"
                      />
                      <div class="form-item-hint">
                        {{ $t('notification.hints.wechatWebhook') }}
                      </div>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item :label="$t('notification.form.businessType')">
                      <el-checkbox v-model="webhookBots.wechat.enable_ui_automation">{{ $t('notification.form.uiAutomation') }}</el-checkbox>
                      <el-checkbox v-model="webhookBots.wechat.enable_api_testing">{{ $t('notification.form.apiTesting') }}</el-checkbox>
                    </el-form-item>
                  </el-col>
                </el-row>

                <div class="form-actions">
                  <el-button type="primary" @click="saveWebhookBot('wechat')">
                    {{ $t('notification.buttons.saveWechat') }}
                  </el-button>
                </div>
              </el-form>
            </div>
          </div>
        </el-tab-pane>

        <!-- 钉钉机器人Tab -->
        <el-tab-pane :label="$t('notification.botTypes.dingtalk')" name="dingtalk">
          <div class="tab-content">
            <div class="config-section">
              <el-form
                  ref="dingtalkFormRef"
                  :model="webhookBots.dingtalk"
                  label-position="top"
                  class="config-form"
              >
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item :label="$t('notification.form.botName')">
                      <el-input
                          v-model="webhookBots.dingtalk.name"
                          :placeholder="$t('notification.placeholders.dingtalkBotName')"
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item :label="$t('notification.form.enabled')">
                      <el-switch v-model="webhookBots.dingtalk.enabled"/>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item :label="$t('notification.form.webhookUrl')">
                      <el-input
                          v-model="webhookBots.dingtalk.webhook_url"
                          :placeholder="$t('notification.placeholders.dingtalkWebhook')"
                      />
                      <div class="form-item-hint">
                        {{ $t('notification.hints.dingtalkWebhook') }}
                      </div>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item :label="$t('notification.form.signatureKey')">
                      <el-input
                          v-model="webhookBots.dingtalk.secret"
                          :placeholder="$t('notification.placeholders.dingtalkSecret')"
                          type="password"
                          show-password
                      />
                      <div class="form-item-hint">
                        {{ $t('notification.hints.dingtalkSecret') }}
                      </div>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item :label="$t('notification.form.businessType')">
                      <el-checkbox v-model="webhookBots.dingtalk.enable_ui_automation">{{ $t('notification.form.uiAutomation') }}</el-checkbox>
                      <el-checkbox v-model="webhookBots.dingtalk.enable_api_testing">{{ $t('notification.form.apiTesting') }}</el-checkbox>
                    </el-form-item>
                  </el-col>
                </el-row>

                <div class="form-actions">
                  <el-button type="primary" @click="saveWebhookBot('dingtalk')">
                    {{ $t('notification.buttons.saveDingtalk') }}
                  </el-button>
                </div>
              </el-form>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script>
import {Setting} from '@element-plus/icons-vue'
import {ref, reactive, onMounted} from 'vue'
import {useI18n} from 'vue-i18n'
import {ElMessage} from 'element-plus'
import {
  getUnifiedNotificationConfigs,
  createUnifiedNotificationConfig,
  updateUnifiedNotificationConfig
} from '@/api/core.js'

export default {
  name: 'NotificationConfigs',
  components: {
    Setting
  },
  setup() {
    const {t} = useI18n()

    // 数据状态
    const feishuFormRef = ref(null)
    const wechatFormRef = ref(null)
    const dingtalkFormRef = ref(null)
    const activeTab = ref('feishu')


    // Webhook机器人配置
    const webhookBots = reactive({
      feishu: {
        name: '',
        webhook_url: '',
        enabled: true,
        enable_ui_automation: true,
        enable_api_testing: true
      },
      wechat: {
        name: '',
        webhook_url: '',
        enabled: true,
        enable_ui_automation: true,
        enable_api_testing: true
      },
      dingtalk: {
        name: '',
        webhook_url: '',
        secret: '',
        enabled: true,
        enable_ui_automation: true,
        enable_api_testing: true
      }
    })

    // 获取机器人类型显示名称
    const getBotTypeName = (botType) => {
      const typeMap = {
        'feishu': t('notification.botTypes.feishu'),
        'wechat': t('notification.botTypes.wechat'),
        'dingtalk': t('notification.botTypes.dingtalk')
      }
      return typeMap[botType] || botType
    }

    // 获取config_type映射
    const getConfigType = (botType) => {
      const configTypeMap = {
        'feishu': 'webhook_feishu',
        'wechat': 'webhook_wechat',
        'dingtalk': 'webhook_dingtalk'
      }
      return configTypeMap[botType]
    }

    // 保存Webhook机器人配置
    const saveWebhookBot = async (botType) => {
      const formRef = botType === 'feishu' ? feishuFormRef.value :
          botType === 'wechat' ? wechatFormRef.value :
              dingtalkFormRef.value

      if (!formRef) return

      // 验证表单
      await new Promise((resolve) => {
        formRef.validate((valid) => {
          resolve(valid)
        })
      })

      try {
        const configType = getConfigType(botType)
        const botTypeName = getBotTypeName(botType)

        // 检查是否已存在对应类型的机器人配置
        let webhookConfigId = null
        try {
          const response = await getUnifiedNotificationConfigs({ config_type: configType })
          if (response.data.results && response.data.results.length > 0) {
            webhookConfigId = response.data.results[0].id
          }
        } catch (error) {
          console.log(t('notification.messages.notFoundCreating'))
        }

        const botConfig = webhookBots[botType]
        let requestData

        if (webhookConfigId) {
          // 更新现有配置
          const configResponse = await getUnifiedNotificationConfigs({ config_type: configType })
          const existingConfig = configResponse.data.results[0]

          const updatedWebhookBots = existingConfig.webhook_bots || {}
          const botData = {
            name: botConfig.name || `${botType} bot`,
            webhook_url: botConfig.webhook_url,
            enabled: botConfig.enabled,
            enable_ui_automation: botConfig.enable_ui_automation,
            enable_api_testing: botConfig.enable_api_testing
          }

          if (botType === 'dingtalk' && botConfig.secret) {
            botData.secret = botConfig.secret
          }

          updatedWebhookBots[botType] = botData

          requestData = {
            name: existingConfig.name || `${botTypeName} Configuration`,
            config_type: configType,
            webhook_bots: updatedWebhookBots,
            is_active: true
          }

          await updateUnifiedNotificationConfig(webhookConfigId, requestData)
          ElMessage.success(t('notification.messages.saveSuccess', { type: botTypeName, action: t('notification.messages.updated') }))
        } else {
          // 创建新配置
          const botData = {
            name: botConfig.name || `${botType} bot`,
            webhook_url: botConfig.webhook_url,
            enabled: botConfig.enabled,
            enable_ui_automation: botConfig.enable_ui_automation,
            enable_api_testing: botConfig.enable_api_testing
          }

          if (botType === 'dingtalk' && botConfig.secret) {
            botData.secret = botConfig.secret
          }

          requestData = {
            name: `${botTypeName} Configuration`,
            config_type: configType,
            webhook_bots: {
              [botType]: botData
            },
            is_active: true
          }

          await createUnifiedNotificationConfig(requestData)
          ElMessage.success(t('notification.messages.saveSuccess', { type: botTypeName, action: t('notification.messages.created') }))
        }

        // 重新加载数据以确保状态同步
        fetchWebhookConfig(botType)
      } catch (error) {
        console.error('Save Webhook bot configuration failed:', error)
        const botTypeName = getBotTypeName(botType)
        ElMessage.error(t('notification.messages.saveFailed', { type: botTypeName }) + ': ' + (error.response?.data?.detail || error.message))
      }
    }

    // 获取Webhook机器人配置
    const fetchWebhookConfig = async (botType) => {
      try {
        const configType = getConfigType(botType)
        const response = await getUnifiedNotificationConfigs({ config_type: configType })
        if (response.data.results && response.data.results.length > 0) {
          const config = response.data.results[0]
          if (config.webhook_bots && config.webhook_bots[botType]) {
            const bot = config.webhook_bots[botType]
            webhookBots[botType].name = bot.name || ''
            webhookBots[botType].webhook_url = bot.webhook_url || ''
            webhookBots[botType].enabled = bot.enabled !== false
            webhookBots[botType].enable_ui_automation = bot.enable_ui_automation !== false
            webhookBots[botType].enable_api_testing = bot.enable_api_testing !== false
            if (botType === 'dingtalk' && bot.secret) {
              webhookBots[botType].secret = bot.secret
            }
          }
        }
      } catch (error) {
        console.error('Fetch Webhook bot configuration failed:', error)
      }
    }

    // 获取所有Webhook机器人配置
    const fetchAllWebhookConfigs = async () => {
      try {
        for (const botType of Object.keys(webhookBots)) {
          await fetchWebhookConfig(botType)
        }
      } catch (error) {
        console.error('Fetch all Webhook bot configurations failed:', error)
      }
    }

    // 组件挂载时获取数据
    onMounted(async () => {
      try {
        console.log('NotificationConfigs component initializing')
        await fetchAllWebhookConfigs()
        console.log('NotificationConfigs component initialized')
      } catch (error) {
        console.error('NotificationConfigs component initialization failed:', error)
      }
    })

    return {
      feishuFormRef,
      wechatFormRef,
      dingtalkFormRef,
      activeTab,
      webhookBots,
      saveWebhookBot,
      fetchWebhookConfig,
      fetchAllWebhookConfigs
    }
  }
}
</script>

<style scoped>
.notification-configs-container {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 32px 24px;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
}

.title-icon {
  margin-right: 12px;
  font-size: 24px;
}

.page-description {
  font-size: 16px;
  opacity: 0.9;
  margin: 0;
}

.content-wrapper {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.notification-tabs :deep(.el-tabs__nav-wrap) {
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.notification-tabs :deep(.el-tabs__nav-scroll) {
  padding: 0;
}

.notification-tabs :deep(.el-tabs__nav) {
  display: flex;
  background: #f8f9fa;
}

.notification-tabs :deep(.el-tabs__item) {
  padding: 16px 32px;
  font-size: 15px;
  font-weight: 500;
  color: #6c757d;
  border: none;
  position: relative;
}

.notification-tabs :deep(.el-tabs__item:hover) {
  color: #667eea;
  background: rgba(102, 126, 234, 0.08);
}

.notification-tabs :deep(.el-tabs__item.is-active) {
  color: #667eea;
  background: white;
  border-bottom: 2px solid #667eea;
}

.notification-tabs :deep(.el-tabs__active-bar) {
  background-color: #667eea;
  height: 2px;
}

.notification-tabs :deep(.el-tabs__content) {
  padding: 0;
}

.tab-content {
  min-height: 600px;
  padding: 24px;
}

.config-section {
  padding: 20px 0;
}

.config-section h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}


.section-title h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}


.form-item-hint {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.form-actions {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
  text-align: right;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .notification-configs-container {
    padding: 16px;
  }

  .page-header {
    padding: 24px 16px;
  }

  .page-title {
    font-size: 24px;
  }

  .notification-tabs :deep(.el-tabs__item) {
    padding: 12px 20px;
    font-size: 14px;
  }

  .tab-content {
    padding: 16px;
  }
}
</style>
