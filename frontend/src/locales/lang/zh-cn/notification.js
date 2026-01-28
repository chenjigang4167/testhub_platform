export default {
  // 页面标题
  configs: {
    title: '通知配置',
    description: '配置飞书、企微、钉钉Webhook机器人地址'
  },

  // 机器人类型
  botTypes: {
    feishu: '飞书机器人',
    wechat: '企微机器人',
    dingtalk: '钉钉机器人'
  },

  // 表单标签
  form: {
    botName: '机器人名称',
    enabled: '启用',
    webhookUrl: 'Webhook URL',
    businessType: '业务类型',
    signatureKey: '签名密钥',
    uiAutomation: 'UI自动化测试',
    apiTesting: '接口测试'
  },

  // 占位符
  placeholders: {
    feishuBotName: '请输入飞书机器人名称',
    feishuWebhook: '请输入飞书机器人Webhook URL',
    wechatBotName: '请输入企业微信机器人名称',
    wechatWebhook: '请输入企业微信机器人Webhook URL',
    dingtalkBotName: '请输入钉钉机器人名称',
    dingtalkWebhook: '请输入钉钉机器人Webhook URL',
    dingtalkSecret: '请输入钉钉机器人签名密钥（可选）'
  },

  // 提示信息
  hints: {
    feishuWebhook: '飞书机器人Webhook URL格式：https://open.feishu.cn/open-apis/bot/v2/hook/...',
    wechatWebhook: '企业微信机器人Webhook URL格式：https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=...',
    dingtalkWebhook: '钉钉机器人Webhook URL格式：https://oapi.dingtalk.com/robot/send?access_token=...',
    dingtalkSecret: '钉钉机器人的签名密钥，用于安全验证。如果机器人开启了"加签"安全设置，请填写此字段。'
  },

  // 按钮文本
  buttons: {
    saveFeishu: '保存飞书机器人配置',
    saveWechat: '保存企微机器人配置',
    saveDingtalk: '保存钉钉机器人配置'
  },

  // 消息
  messages: {
    saveSuccess: '{type}机器人配置{action}成功',
    saveFailed: '{type}机器人配置保存失败',
    fetchFailed: '获取Webhook机器人配置失败',
    fetchAllFailed: '获取所有Webhook机器人配置失败',
    notFoundCreating: '未找到现有Webhook配置，将创建新配置',
    created: '创建',
    updated: '更新'
  },

  // 日志页面
  logs: {
    // 搜索
    searchTaskName: '搜索任务名称',
    rangeSeparator: '至',
    startDate: '开始日期',
    endDate: '结束日期',
    notificationStatus: '通知状态',
    search: '搜索',
    reset: '重置',

    // 状态选项
    statusOptions: {
      all: '全部状态',
      success: '成功',
      failed: '失败',
      retrying: '重试中'
    },

    // 表格列
    columns: {
      taskName: '任务名称',
      taskType: '任务类型',
      notificationType: '通知类型',
      notificationTarget: '通知对象',
      notificationTime: '通知时间',
      status: '状态',
      operation: '操作'
    },

    // 加载提示
    loading: '加载中...',

    // 操作
    viewDetail: '查看详情',

    // 详情弹窗
    detailDialog: {
      title: '通知详情',
      taskName: '任务名称',
      taskType: '任务类型',
      notificationType: '通知类型',
      status: '状态',
      notificationTime: '通知时间',
      sentTime: '发送时间',
      notificationTarget: '通知对象',
      notificationContent: '通知内容',
      errorMessage: '错误信息',
      close: '关闭'
    },

    // 消息
    messages: {
      fetchFailed: '获取通知日志失败',
      fetchDetailFailed: '获取通知详情失败'
    }
  }
}
