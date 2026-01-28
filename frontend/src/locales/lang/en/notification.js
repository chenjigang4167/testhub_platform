export default {
  // Page title
  configs: {
    title: 'Notification Configuration',
    description: 'Configure Feishu, WeCom, DingTalk Webhook bot addresses'
  },

  // Bot types
  botTypes: {
    feishu: 'Feishu Bot',
    wechat: 'WeCom Bot',
    dingtalk: 'DingTalk Bot'
  },

  // Form labels
  form: {
    botName: 'Bot Name',
    enabled: 'Enabled',
    webhookUrl: 'Webhook URL',
    businessType: 'Business Type',
    signatureKey: 'Signature Key',
    uiAutomation: 'UI Automation Testing',
    apiTesting: 'API Testing'
  },

  // Placeholders
  placeholders: {
    feishuBotName: 'Enter Feishu bot name',
    feishuWebhook: 'Enter Feishu bot Webhook URL',
    wechatBotName: 'Enter WeCom bot name',
    wechatWebhook: 'Enter WeCom bot Webhook URL',
    dingtalkBotName: 'Enter DingTalk bot name',
    dingtalkWebhook: 'Enter DingTalk bot Webhook URL',
    dingtalkSecret: 'Enter DingTalk bot signature key (optional)'
  },

  // Hints
  hints: {
    feishuWebhook: 'Feishu bot Webhook URL format: https://open.feishu.cn/open-apis/bot/v2/hook/...',
    wechatWebhook: 'WeCom bot Webhook URL format: https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=...',
    dingtalkWebhook: 'DingTalk bot Webhook URL format: https://oapi.dingtalk.com/robot/send?access_token=...',
    dingtalkSecret: 'DingTalk bot signature key for security verification. Fill in this field if the bot has enabled "Sign" security settings.'
  },

  // Button text
  buttons: {
    saveFeishu: 'Save Feishu Bot Configuration',
    saveWechat: 'Save WeCom Bot Configuration',
    saveDingtalk: 'Save DingTalk Bot Configuration'
  },

  // Messages
  messages: {
    saveSuccess: '{type} bot configuration {action} successfully',
    saveFailed: '{type} bot configuration save failed',
    fetchFailed: 'Failed to fetch Webhook bot configuration',
    fetchAllFailed: 'Failed to fetch all Webhook bot configurations',
    notFoundCreating: 'No existing Webhook configuration found, creating new configuration',
    created: 'created',
    updated: 'updated'
  },

  // Logs page
  logs: {
    // Search
    searchTaskName: 'Search task name',
    rangeSeparator: 'to',
    startDate: 'Start date',
    endDate: 'End date',
    notificationStatus: 'Notification status',
    search: 'Search',
    reset: 'Reset',

    // Status options
    statusOptions: {
      all: 'All Status',
      success: 'Success',
      failed: 'Failed',
      retrying: 'Retrying'
    },

    // Table columns
    columns: {
      taskName: 'Task Name',
      taskType: 'Task Type',
      notificationType: 'Notification Type',
      notificationTarget: 'Notification Target',
      notificationTime: 'Notification Time',
      status: 'Status',
      operation: 'Operation'
    },

    // Loading text
    loading: 'Loading...',

    // Actions
    viewDetail: 'View Detail',

    // Detail dialog
    detailDialog: {
      title: 'Notification Detail',
      taskName: 'Task Name',
      taskType: 'Task Type',
      notificationType: 'Notification Type',
      status: 'Status',
      notificationTime: 'Notification Time',
      sentTime: 'Sent Time',
      notificationTarget: 'Notification Target',
      notificationContent: 'Notification Content',
      errorMessage: 'Error Message',
      close: 'Close'
    },

    // Messages
    messages: {
      fetchFailed: 'Failed to fetch notification logs',
      fetchDetailFailed: 'Failed to fetch notification detail'
    }
  }
}
