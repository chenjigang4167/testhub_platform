<template>
  <div class="notification-configs-container">
    <!-- 页面说明 -->
    <div class="page-header">
      <h1 class="page-title">
        <el-icon class="title-icon">
          <Setting/>
        </el-icon>
        {{ $t('uiAutomation.notification.configs.pageTitle') }}
      </h1>
      <p class="page-description">
        {{ $t('uiAutomation.notification.configs.pageDesc') }}
      </p>
    </div>

    <!-- Tab切换 -->
    <div class="content-wrapper">
      <el-tabs v-model="activeTab" class="notification-tabs">

        <!-- 飞书机器人Tab -->
        <el-tab-pane :label="$t('uiAutomation.notification.configs.feishuBot')" name="feishu">
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
                    <el-form-item :label="$t('uiAutomation.notification.configs.botName')">
                      <el-input
                          v-model="webhookBots.feishu.name"
                          :placeholder="$t('uiAutomation.notification.configs.feishuBotNamePlaceholder')"
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item :label="$t('uiAutomation.notification.configs.enable')">
                      <el-switch v-model="webhookBots.feishu.enabled"/>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item :label="$t('uiAutomation.notification.configs.webhookUrl')">
                      <el-input
                          v-model="webhookBots.feishu.webhook_url"
                          :placeholder="$t('uiAutomation.notification.configs.webhookPlaceholder')"
                      />
                      <div class="form-item-hint">
                        {{ $t('uiAutomation.notification.configs.feishuUrlHint') }}
                      </div>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item :label="$t('uiAutomation.notification.configs.businessType')">
                      <el-checkbox v-model="webhookBots.feishu.enable_ui_automation">{{ $t('uiAutomation.notification.configs.uiAutomationTest') }}</el-checkbox>
                      <el-checkbox v-model="webhookBots.feishu.enable_api_testing">{{ $t('uiAutomation.notification.configs.apiTest') }}</el-checkbox>
                    </el-form-item>
                  </el-col>
                </el-row>

                <div class="form-actions">
                  <el-button type="primary" @click="saveWebhookBot('feishu')">
                    {{ $t('uiAutomation.notification.configs.saveFeishuConfig') }}
                  </el-button>
                </div>
              </el-form>
            </div>
          </div>
        </el-tab-pane>

        <!-- 企业微信机器人Tab -->
        <el-tab-pane :label="$t('uiAutomation.notification.configs.wechatBot')" name="wechat">
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
                    <el-form-item :label="$t('uiAutomation.notification.configs.botName')">
                      <el-input
                          v-model="webhookBots.wechat.name"
                          :placeholder="$t('uiAutomation.notification.configs.wechatBotNamePlaceholder')"
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item :label="$t('uiAutomation.notification.configs.enable')">
                      <el-switch v-model="webhookBots.wechat.enabled"/>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item :label="$t('uiAutomation.notification.configs.webhookUrl')">
                      <el-input
                          v-model="webhookBots.wechat.webhook_url"
                          :placeholder="$t('uiAutomation.notification.configs.webhookPlaceholder')"
                      />
                      <div class="form-item-hint">
                        {{ $t('uiAutomation.notification.configs.wechatUrlHint') }}
                      </div>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item :label="$t('uiAutomation.notification.configs.businessType')">
                      <el-checkbox v-model="webhookBots.wechat.enable_ui_automation">{{ $t('uiAutomation.notification.configs.uiAutomationTest') }}</el-checkbox>
                      <el-checkbox v-model="webhookBots.wechat.enable_api_testing">{{ $t('uiAutomation.notification.configs.apiTest') }}</el-checkbox>
                    </el-form-item>
                  </el-col>
                </el-row>

                <div class="form-actions">
                  <el-button type="primary" @click="saveWebhookBot('wechat')">
                    {{ $t('uiAutomation.notification.configs.saveWechatConfig') }}
                  </el-button>
                </div>
              </el-form>
            </div>
          </div>
        </el-tab-pane>

        <!-- 钉钉机器人Tab -->
        <el-tab-pane :label="$t('uiAutomation.notification.configs.dingtalkBot')" name="dingtalk">
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
                    <el-form-item :label="$t('uiAutomation.notification.configs.botName')">
                      <el-input
                          v-model="webhookBots.dingtalk.name"
                          :placeholder="$t('uiAutomation.notification.configs.dingtalkBotNamePlaceholder')"
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item :label="$t('uiAutomation.notification.configs.enable')">
                      <el-switch v-model="webhookBots.dingtalk.enabled"/>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item :label="$t('uiAutomation.notification.configs.webhookUrl')">
                      <el-input
                          v-model="webhookBots.dingtalk.webhook_url"
                          :placeholder="$t('uiAutomation.notification.configs.webhookPlaceholder')"
                      />
                      <div class="form-item-hint">
                        {{ $t('uiAutomation.notification.configs.dingtalkUrlHint') }}
                      </div>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item :label="$t('uiAutomation.notification.configs.signatureSecret')">
                      <el-input
                          v-model="webhookBots.dingtalk.secret"
                          :placeholder="$t('uiAutomation.notification.configs.signatureSecretPlaceholder')"
                          type="password"
                          show-password
                      />
                      <div class="form-item-hint">
                        {{ $t('uiAutomation.notification.configs.signatureSecretHint') }}
                      </div>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item :label="$t('uiAutomation.notification.configs.businessType')">
                      <el-checkbox v-model="webhookBots.dingtalk.enable_ui_automation">{{ $t('uiAutomation.notification.configs.uiAutomationTest') }}</el-checkbox>
                      <el-checkbox v-model="webhookBots.dingtalk.enable_api_testing">{{ $t('uiAutomation.notification.configs.apiTest') }}</el-checkbox>
                    </el-form-item>
                  </el-col>
                </el-row>

                <div class="form-actions">
                  <el-button type="primary" @click="saveWebhookBot('dingtalk')">
                    {{ $t('uiAutomation.notification.configs.saveDingtalkConfig') }}
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
import {ElMessage} from 'element-plus'
import {
  getUnifiedNotificationConfigs,
  createUnifiedNotificationConfig,
  updateUnifiedNotificationConfig
} from '@/api/core.js'
import { useI18n } from 'vue-i18n'

export default {
  name: 'NotificationConfigs',
  components: {
    Setting
  },
  setup() {
    const { t } = useI18n()

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

    // 获取config_type映射
    const getConfigType = (botType) => {
      const configTypeMap = {
        'feishu': 'webhook_feishu',
        'wechat': 'webhook_wechat',
        'dingtalk': 'webhook_dingtalk'
      }
      return configTypeMap[botType]
    }

    // 获取机器人显示名称
    const getBotDisplayName = (botType) => {
      const displayNameMap = {
        'feishu': t('uiAutomation.notification.configs.platforms.feishu'),
        'wechat': t('uiAutomation.notification.configs.platforms.wechatWork'),
        'dingtalk': t('uiAutomation.notification.configs.platforms.dingtalk')
      }
      return displayNameMap[botType] || botType
    }

    // 保存Webhook机器人配置
    const saveWebhookBot = async (botType) => {
      const formRef = botType === 'feishu' ? feishuFormRef.value :
          botType === 'wechat' ? wechatFormRef.value :
              dingtalkFormRef.value

      if (!formRef) return

      try {
        const configType = getConfigType(botType)
        const botDisplayName = getBotDisplayName(botType)

        // 检查是否已存在对应类型的机器人配置
        let webhookConfigId = null
        try {
          const response = await getUnifiedNotificationConfigs({ config_type: configType })
          if (response.data.results && response.data.results.length > 0) {
            webhookConfigId = response.data.results[0].id
          }
        } catch (error) {
          console.log(t('uiAutomation.notification.configs.messages.noExistingConfig'))
        }

        const botConfig = webhookBots[botType]
        let requestData

        if (webhookConfigId) {
          // 更新现有配置 - 需要先获取现有配置，然后更新webhook_bots
          const configResponse = await getUnifiedNotificationConfigs({ config_type: configType })
          const existingConfig = configResponse.data.results[0]

          // 合并现有的webhook_bots和其他字段
          const updatedWebhookBots = existingConfig.webhook_bots || {}
          const botData = {
            name: botConfig.name || `${botType}机器人`,
            webhook_url: botConfig.webhook_url,
            enabled: botConfig.enabled,
            enable_ui_automation: botConfig.enable_ui_automation,
            enable_api_testing: botConfig.enable_api_testing
          }

          // 钉钉机器人需要额外保存secret字段
          if (botType === 'dingtalk' && botConfig.secret) {
            botData.secret = botConfig.secret
          }

          updatedWebhookBots[botType] = botData

          requestData = {
            name: existingConfig.name || `${botDisplayName}${t('uiAutomation.notification.configs.title')}`,
            config_type: configType,
            webhook_bots: updatedWebhookBots,
            is_active: true
          }

          // 更新现有配置
          await updateUnifiedNotificationConfig(webhookConfigId, requestData)
          const successMsgKey = botType === 'feishu' ? 'feishuUpdateSuccess' :
              botType === 'wechat' ? 'wechatUpdateSuccess' : 'dingtalkUpdateSuccess'
          ElMessage.success(t(`uiAutomation.notification.configs.messages.${successMsgKey}`))
        } else {
          // 创建新配置
          const botData = {
            name: botConfig.name || `${botType}机器人`,
            webhook_url: botConfig.webhook_url,
            enabled: botConfig.enabled,
            enable_ui_automation: botConfig.enable_ui_automation,
            enable_api_testing: botConfig.enable_api_testing
          }

          // 钉钉机器人需要额外保存secret字段
          if (botType === 'dingtalk' && botConfig.secret) {
            botData.secret = botConfig.secret
          }

          requestData = {
            name: `${botDisplayName}${t('uiAutomation.notification.configs.title')}`,
            config_type: configType,
            webhook_bots: {
              [botType]: botData
            },
            is_active: true
          }

          await createUnifiedNotificationConfig(requestData)
          const successMsgKey = botType === 'feishu' ? 'feishuCreateSuccess' :
              botType === 'wechat' ? 'wechatCreateSuccess' : 'dingtalkCreateSuccess'
          ElMessage.success(t(`uiAutomation.notification.configs.messages.${successMsgKey}`))
        }

        // 重新加载数据以确保状态同步
        fetchWebhookConfig(botType)
      } catch (error) {
        console.error('保存Webhook机器人配置失败:', error)
        const failedMsgKey = botType === 'feishu' ? 'feishuSaveFailed' :
            botType === 'wechat' ? 'wechatSaveFailed' : 'dingtalkSaveFailed'
        ElMessage.error(t(`uiAutomation.notification.configs.messages.${failedMsgKey}`) + ': ' + (error.response?.data?.detail || error.message))
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
            // 钉钉机器人需要额外读取secret字段
            if (botType === 'dingtalk' && bot.secret) {
              webhookBots[botType].secret = bot.secret
            }
          }
        }
      } catch (error) {
        console.error(t('uiAutomation.notification.configs.messages.getConfigFailed'), error)
      }
    }

    // 获取所有Webhook机器人配置
    const fetchAllWebhookConfigs = async () => {
      try {
        // 遍历所有机器人类型，分别获取配置
        for (const botType of Object.keys(webhookBots)) {
          await fetchWebhookConfig(botType)
        }
      } catch (error) {
        console.error(t('uiAutomation.notification.configs.messages.getAllConfigFailed'), error)
      }
    }

    // 组件挂载时获取数据
    onMounted(async () => {
      try {
        console.log('NotificationConfigs 组件开始初始化')
        await fetchAllWebhookConfigs()
        console.log('NotificationConfigs 组件初始化完成')
      } catch (error) {
        console.error('NotificationConfigs 组件初始化失败:', error)
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
