export default {
  requirementAnalysis: {
    // Page
    title: '智能测试用例生成',
    subtitle: '基于需求描述或文档，AI将直接为您生成高质量的测试用例',

    // Output Mode
    outputModeTitle: '📤 输出模式设置',
    outputModeDesc: '选择测试用例生成的输出方式（适用于手动输入和文档上传两种方式）',
    realtimeStream: '⚡ 实时流式输出',
    realtimeStreamDesc: '内容逐字显示，体验流畅，适合大需求文档',
    completeOutput: '📄 完整输出',
    completeOutputDesc: '完成后一次性展示，适合简单需求',

    // Manual Input
    manualInputTitle: '✍️ 手动输入需求描述',
    requirementTitle: '需求标题',
    requirementDescription: '需求描述',
    relatedProject: '关联项目（可选）',
    titlePlaceholder: '请输入需求标题，如：用户登录功能需求',
    descriptionPlaceholder: '请详细描述您的需求，包括功能描述、使用场景、业务流程等',
    selectProject: '请选择项目',
    charCount: '{count}/2000',
    generating: '🔄 生成中...',
    generateBtn: '🚀 生成测试用例',

    // Document Upload
    uploadTitle: '📄 上传需求文档',
    dragDropText: '拖拽文件到此处或点击选择文件',
    supportedFormats: '支持 PDF、Word、TXT、Markdown 格式',
    selectFileBtn: '选择文件',
    selectFile: '选择文件',
    removeFile: '❌',
    documentTitle: '文档标题',
    documentTitlePlaceholder: '请输入文档标题',
    documentPlaceholder: '请输入文档标题',
    documentContent: '文档内容',
    fileSize: '文件大小',

    // Generation Options
    generationOptions: '⚙️ 生成选项',
    testCaseCount: '期望生成测试用例数量',
    detailLevel: '详细程度',
    detailSimple: '简要',
    detailNormal: '正常',
    detailDetailed: '详细',
    includeEdgeCases: '包含边界场景',
    includeNegativeCases: '包含异常场景',
    submitGeneration: '提交生成任务',

    // Divider
    dividerOr: '或',

    // Messages
    titleRequired: '请输入需求标题',
    descriptionRequired: '请输入需求描述',
    descriptionTooShort: '需求描述至少需要10个字符',
    fileRequired: '请选择文件',
    generateSuccess: '生成任务已提交！',
    generateFailed: '生成失败',
    uploadSuccess: '文件上传成功',
    uploadFailed: '文件上传失败',
    fillRequiredInfo: '请填写必填信息',
    selectFileAndTitle: '请选择文件并填写文档标题',
    invalidFileFormat: '不支持的文件格式',
    invalidFileFormatDetail: '请选择 PDF、Word、TXT 或 Markdown 格式的文件',
    extractingContent: '正在提取文档内容...',
    extractionFailed: '文档内容提取失败',
    documentProcessingFailed: '文档处理失败',
    loadProjectsFailed: '加载项目列表失败',

    // Progress
    analyzingRequirement: '📖 分析需求文档中...',
    generatingTestCases: '✍️ 编写测试用例中...',
    reviewingTestCases: '🔍 评审测试用例中...',
    generationComplete: '✅ 生成完成！',
    generationFailed: '❌ 生成失败',
    creatingTask: '正在创建生成任务...',
    taskCreated: '任务创建成功，开始生成...',
    preparing: '准备中...',

    // Generation Status
    aiGeneratingTitle: '🤖 AI正在生成测试用例',
    taskId: '任务ID',
    currentStatus: '当前状态',
    taskStatus: '任务状态',
    progress: '进度',
    stepAnalysis: '需求分析',
    stepWriting: '用例编写',
    stepReview: '用例评审',
    stepComplete: '生成完成',
    cancelGeneration: '取消生成',
    generationCancelled: '生成已取消',
    statusGenerating: '正在编写测试用例...',
    statusReviewing: '正在评审测试用例...',
    statusRevising: '正在生成最终版用例...',
    statusCompleted: '生成完成！',
    statusFailed: '生成失败',
    generateCompleteSuccess: '测试用例生成完成！',
    checkProgressFailed: '检查进度失败',
    createTaskFailed: '创建任务失败',
    unknownError: '未知错误',
    tokenRefreshFailed: 'Token刷新失败，请重新登录',
    streamConnectionInterrupted: '流式连接中断，切换到轮询模式',
    fetchResultFailed: '获取结果失败',

    // Stream Display
    realtimeGeneratedContent: '✍️ 实时生成内容',
    aiReviewComments: '📝 AI评审意见',
    finalVersionTestCases: '✅ 最终版测试用例',
    characters: '{count} 字符',

    // Results
    viewResultsBtn: '查看生成结果',
    generateAgainBtn: '重新生成',
    backBtn: '返回',
    newGeneration: '新建生成任务',
    summaryTaskId: '任务ID: {taskId}',
    summaryGenerationTime: '生成时间: {time}',
    aiGeneratedTestCases: 'AI生成的测试用例',
    aiReviewFeedback: 'AI评审反馈',
    finalTestCases: '最终测试用例',
    downloadExcel: '下载Excel',
    saveToRecords: '保存到记录',

    // Excel Export
    testCaseSheetName: '测试用例',
    excelFileName: 'AI生成测试用例_{taskId}_{date}.xlsx',
    downloadSuccess: '下载成功',
    downloadFailed: '下载失败',
    testCaseContent: '测试用例内容',
    excelTestCaseNumber: '用例编号',
    excelTestScenario: '测试场景',
    excelPrecondition: '前置条件',
    excelTestSteps: '测试步骤',
    excelExpectedResult: '预期结果',
    excelPriority: '优先级',

    // Save
    saveSuccess: '成功保存 {count} 条测试用例',
    saveFailed: '保存失败',
    alreadySaved: '测试用例已保存过',

    // Status
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  },
  generatedTestCases: {
    // Page
    title: 'AI生成用例记录',

    // Filters
    statusFilter: '状态筛选:',
    allStatus: '全部状态',
    pending: '需求分析中',
    generating: '用例编写中',
    reviewing: '用例评审中',
    completed: '已完成',
    failed: '失败',

    // Status Display
    statusPending: '需求分析中',
    statusGenerating: '用例编写中',
    statusReviewing: '用例评审中',
    statusCompleted: '已完成',
    statusFailed: '失败',
    statusDraft: '草稿',
    statusActive: '激活',

    // Actions
    batchDelete: '🗑️ 批量删除({count})',
    deleting: '🗑️ 删除中...',
    refresh: '🔄 刷新',
    loading: '🔄 加载中...',

    // Stats
    totalTasks: '任务总数',
    completedTasks: '已完成',
    runningTasks: '进行中',
    failedTasks: '失败',
    completedCount: '已完成',
    runningCount: '进行中',
    failedCount: '失败',

    // Table Headers
    serialNumber: '序号',
    taskId: '任务ID',
    relatedRequirement: '关联需求',
    requirement: '关联需求',
    status: '状态',
    caseCount: '用例条数',
    generatedTime: '生成时间',
    generationTime: '生成时间',
    actions: '操作',

    // Actions
    viewDetail: '查看详情',
    adoptAll: '全部采纳',
    exportExcel: '导出Excel',
    delete: '删除',
    batchAdopt: '批量采纳',
    batchDiscard: '批量弃用',

    // Empty State
    noTasks: '暂无生成任务',
    noTasksHint: '还没有AI生成用例任务，去',
    noTasksLink: 'AI用例生成',
    noTasksHint2: '页面创建一个任务吧！',
    emptyHint: '还没有AI生成用例任务，去',
    aiGeneration: 'AI用例生成',
    createTask: '页面创建一个任务吧！',

    // Loading
    loadingTasks: '🔄 正在加载任务列表...',
    generatingWait: '任务正在生成中，请稍候...',

    // Pagination
    pageSize: '每页显示:',
    pageSizeUnit: '{size} 条',
    previousPage: '上一页',
    nextPage: '下一页',
    jumpTo: '跳转到:',
    pageNumber: '页码',
    jump: '跳转',
    paginationInfo: '显示 {start}-{end} 条，共 {total} 条',

    // Detail Modal
    caseNumber: '用例编号',
    priority: '优先级',
    preconditions: '前置条件',
    testSteps: '测试步骤',
    expectedResult: '预期结果',
    reviewComments: '评审意见',
    generatedAI: '生成模型',
    reviewedAI: '评审模型',

    // Adopt Modal
    adoptModalTitle: '采纳测试用例',
    caseTitle: '用例标题',
    caseTitlePlaceholder: '请输入用例标题',
    caseDescription: '用例描述',
    caseDescriptionPlaceholder: '请输入用例描述',
    belongsToProject: '所属项目',
    selectProject: '请选择项目',
    relatedVersion: '关联版本',
    selectVersion: '请选择版本',
    baseline: '(基线)',
    showingProjectVersions: '显示 {project} 项目的版本',
    showingAllVersions: '显示所有版本',
    priorityLow: '低',
    priorityMedium: '中',
    priorityHigh: '高',
    priorityCritical: '紧急',
    testType: '测试类型',
    testTypeFunctional: '功能测试',
    testTypeIntegration: '集成测试',
    testTypeAPI: 'API测试',
    testTypeUI: 'UI测试',
    testTypePerformance: '性能测试',
    testTypeSecurity: '安全测试',
    preconditionsPlaceholder: '请输入前置条件',
    operationSteps: '操作步骤',
    operationStepsPlaceholder: '请输入操作步骤',
    expectedResultPlaceholder: '请输入预期结果',
    adopting: '采纳中...',
    confirmAdopt: '确认采纳',
    cancel: '取消',

    // Messages
    deleteConfirm: '确定要删除这个任务吗？',
    batchDeleteConfirm: '确定要删除选中的 {count} 个任务吗？此操作不可恢复。',
    deleteSuccess: '成功删除 {success} 个任务，失败 {failed} 个',
    deleteFailed: '删除失败',
    batchDeleteSuccess: '成功删除 {count} 个任务',
    batchDeleteFailed: '批量删除失败',
    adoptAllSuccess: '全部采纳成功',
    adoptAllFailed: '采纳失败',
    exportSuccess: '导出成功',
    exportFailed: '导出失败',
    loadFailed: '加载任务列表失败',
    loadTasksFailed: '加载任务列表失败',
    loadStatsFailed: '加载统计信息失败',
    selectTasksFirst: '请先选择要删除的任务',
    unknownError: '未知错误',

    // Adopt/Discard
    adoptConfirm: '确定要全部采纳任务 "{title}" 的所有用例吗？',
    adoptSuccess: '采纳成功',
    adoptFailed: '采纳失败',
    discardConfirm: '确定要弃用任务 "{title}" 的所有用例吗？',
    discardSuccess: '弃用成功',
    discardFailed: '弃用失败',
    fetchProjectsFailed: '获取项目列表失败',
    fetchVersionsFailed: '获取版本列表失败',
    fetchProjectVersionsFailed: '获取项目版本失败',
    selectProjectRequired: '请选择所属项目',
    selectVersionRequired: '请选择关联版本',
    enterCaseTitle: '请输入用例标题',
    enterExpectedResult: '请输入预期结果',
    updateStatusFailed: '更新状态失败',
    adoptModalSuccess: '用例采纳成功！',
    adoptCaseFailed: '采纳用例失败',
    adoptCaseFailedRetry: '采纳用例失败，请重试',
    discardCaseConfirm: '确定要弃用用例 "{title}" 吗？',
    caseDiscarded: '用例已弃用',
    discardCaseFailed: '弃用用例失败',
    discardCaseFailedRetry: '弃用用例失败，请重试',

    // Selection
    selectAll: '全选',
    selectedCount: '已选择 {count} 项'
  },
  promptConfig: {
    // Page
    title: '📝 提示词配置',
    subtitle: '配置用于测试用例编写和评审的AI提示词',

    // Section
    configListTitle: '提示词配置列表',
    loadDefaults: '📂 加载默认提示词',
    addConfig: '➕ 添加配置',

    // Config Card
    enabled: '启用',
    disabled: '禁用',
    preview: '👁️ 预览',
    edit: '✏️ 编辑',
    delete: '🗑️ 删除',

    // Config Details
    contentPreview: '提示词内容预览:',
    createdAt: '创建时间:',
    updatedAt: '更新时间:',
    creator: '创建者:',
    createdBy: '创建者:',
    unknown: '未知',

    // Modal
    addTitle: '添加提示词配置',
    editTitle: '编辑提示词配置',
    editConfig: '编辑提示词配置',
    configName: '配置名称',
    configNamePlaceholder: '例如：测试用例编写提示词 v1.0',
    required: '*',
    promptType: '提示词类型',
    testCaseWriter: '测试用例编写',
    testCaseReviewer: '测试用例评审',
    selectType: '请选择类型',
    selectPromptType: '请选择提示词类型',
    writerPrompt: '测试用例编写提示词',
    reviewerPrompt: '测试用例评审提示词',
    isActive: '是否启用',
    promptContent: '提示词内容',
    contentPlaceholder: '请输入提示词内容，支持使用变量占位符...',
    contentHint: '提示：可使用 {requirement} {project} 等变量',
    charCount: '字符数: {count}',
    saveBtn: '💾 保存',
    saveConfig: '💾 保存配置',
    cancel: '取消',
    cancelBtn: '取消',
    saving: '💾 保存中...',
    enableConfig: '启用此配置',
    enableHint: '启用后，相同类型的其他配置将被禁用',

    // Writing Tips
    writingTipsTitle: '提示词编写建议:',
    tip1: '使用 {requirement} 表示需求内容',
    tip2: '使用 {project} 表示项目信息',
    tip3: '清晰描述AI的角色和任务',
    tip4: '指定输出格式和结构',

    // Preview Modal
    previewTitle: '预览提示词 - {name}',
    type: '类型:',
    status: '状态:',
    closeBtn: '关闭',

    // Default Prompts Modal
    defaultPromptsPreview: '默认提示词预览',
    writerTab: '测试用例编写',
    reviewerTab: '测试用例评审',
    noContent: '暂无内容',
    loading: '加载中...',
    confirmLoad: '确认加载',
    defaultWriterName: '默认测试用例编写提示词',
    defaultReviewerName: '默认测试用例评审提示词',
    defaultsLoadSuccess: '默认提示词加载成功',

    // Empty State
    noConfigs: '暂无提示词配置',
    noConfigsHint: '请添加提示词配置以自定义AI的行为和输出格式',
    emptyHint: '请添加提示词配置以自定义AI的行为和输出格式',
    addFirstConfig: '➕ 添加第一个配置',
    loadDefaultsFirst: '📂 加载默认提示词',

    // Messages
    nameRequired: '请输入配置名称',
    typeRequired: '请选择提示词类型',
    contentRequired: '请输入提示词内容',
    saveSuccess: '保存成功',
    saveFailed: '保存失败',
    addSuccess: '配置添加成功',
    updateSuccess: '配置更新成功',
    saveConfigFailed: '保存配置失败',
    deleteConfirm: '确定要删除这个配置吗？',
    deleteSuccess: '删除成功',
    deleteFailed: '删除失败',
    deleteConfigFailed: '删除配置失败',
    loadDefaultsSuccess: '默认提示词加载成功',
    loadDefaultsFailed: '加载默认提示词失败',
    loadConfigsFailed: '加载配置失败',
    loadFailed: '加载失败',
    pleaseLogin: '请先登录'
  },
  generationConfig: {
    // Page
    title: '⚙️ 生成行为配置',
    subtitle: '配置测试用例生成的默认行为和自动化流程',
    description: '配置测试用例生成的默认行为和自动化流程',

    // Config List
    configList: '配置列表',
    addConfig: '➕ 添加配置',
    addFirstConfig: '➕ 添加第一个配置',
    emptyTitle: '暂无生成配置',
    emptyDescription: '请添加生成行为配置以控制测试用例生成的默认行为',

    // Config Card
    enabled: '✅ 启用中',
    disabled: '❌ 未启用',
    streamMode: '⚡ 流式输出',
    completeMode: '📄 完整输出',
    enable: '✅ 启用',
    edit: '✏️ 编辑',
    delete: '🗑️ 删除',

    // Sections
    outputMode: '📤 输出模式',
    automationProcess: '🤖 自动化流程',
    timeoutSettings: '⏱️ 超时设置',

    // Fields
    defaultMode: '默认模式:',
    aiReview: 'AI评审和改进:',
    reviewTimeout: '评审和改进超时:',
    seconds: '秒',
    createdAt: '创建时间:',
    updatedAt: '更新时间:',

    // Form
    editTitle: '编辑',
    addTitle: '添加',
    formTitle: '生成行为配置',
    basicInfo: '📋 基本信息',
    configName: '配置名称',
    configNamePlaceholder: '例如：默认生成配置',
    defaultConfigName: '默认生成配置',
    enableThisConfig: '启用此配置',
    enableHint: '注意：只能有一个启用的配置，启用此配置将自动禁用其他配置',

    // Output Mode
    outputModeSettings: '📤 输出模式设置',
    defaultOutputMode: '默认输出模式',
    realtimeStream: '⚡ 实时流式输出',
    completeOutput: '📄 完整输出',
    outputModeHint: '实时流式输出：内容逐字显示，体验流畅；完整输出：完成后一次性展示',

    // Automation
    automationSettings: '🤖 自动化流程配置',
    enableAutoReview: '启用AI评审和改进',
    autoReviewHint: '生成完成后自动进行AI评审，并根据评审意见改进测试用例',

    // Timeout
    timeoutSettingsLabel: '⏱️ 超时设置',
    reviewTimeoutLabel: '评审和改进超时时间（秒）',
    timeoutHint: 'AI评审和改进的总超时时间（建议：小文档120秒，大文档600-1800秒，超大文档可设置到3600秒）',

    // Buttons
    cancel: '取消',
    saving: '🔄 保存中...',
    saveConfig: '💾 保存配置',

    // Messages
    loadFailed: '加载配置失败',
    pleaseLogin: '请先登录',
    saveSuccess: '配置添加成功',
    updateSuccess: '配置更新成功',
    saveFailed: '保存失败',
    enableSuccess: '配置已启用',
    enableFailed: '启用失败',
    deleteSuccess: '配置删除成功',
    deleteFailed: '删除失败',
    deleteConfirm: '确定要删除此配置吗？'
  },

  // 任务详情页面
  taskDetail: {
    // 页面头部
    title: '任务详情',
    taskId: '任务ID',
    exportBtn: '💾 导出Excel',
    exporting: '💾 导出中...',

    // 需求描述折叠卡片
    requirementTitle: '📋 需求描述',
    requirementHint: '（点击展开查看完整内容）',
    copyRequirement: '复制需求描述',

    // 状态
    statusPending: '需求分析中',
    statusGenerating: '用例编写中',
    statusReviewing: '用例评审中',
    statusCompleted: '已完成',
    statusFailed: '失败',

    // 批量操作
    selectAll: '全选',
    selectedCount: '已选择 {count} 条用例',
    batchAdopt: '✅ 一键采纳 ({count})',
    batchDiscard: '❌ 一键弃用 ({count})',

    // 表格头部
    tableSelect: '选择',
    tableCaseId: '测试用例编号',
    tableScenario: '测试场景',
    tablePrecondition: '前置条件',
    tableSteps: '操作步骤',
    tableExpected: '预期结果',
    tablePriority: '优先级',
    tableActions: '操作',

    // 表格操作按钮
    viewDetail: '📖 查看详情',
    adopt: '✅ 采纳',
    discard: '❌ 弃用',

    // 空状态
    emptyTitle: '暂无测试用例数据',
    emptyHint: '该任务还没有生成测试用例或用例已被清空',

    // 分页
    paginationInfo: '显示 {start}-{end} 条，共 {total} 条',
    pageSizeLabel: '每页显示：',
    pageSizeOption: '{size} 条',
    previousPage: '上一页',
    nextPage: '下一页',
    currentPageInfo: '第 {current} 页，共 {total} 页',

    // 弹窗
    modalEditTitle: '编辑测试用例',
    modalViewTitle: '测试用例详情',
    labelCaseId: '用例编号:',
    labelScenario: '测试场景:',
    labelPrecondition: '前置条件:',
    labelSteps: '操作步骤:',
    labelExpected: '预期结果:',
    labelPriority: '优先级:',
    labelNone: '无',
    btnEdit: '✏️ 编辑',
    btnClose: '关闭',
    btnSave: '💾 保存',
    btnSaveing: '💾 保存中...',
    btnCancel: '取消',

    // 占位符
    placeholderScenario: '请输入测试场景',
    placeholderPrecondition: '请输入前置条件',
    placeholderSteps: '请输入操作步骤',
    placeholderExpected: '请输入预期结果',
    placeholderPriority: '请选择优先级',

    // 消息提示
    loading: '🔄 正在加载任务详情...',
    taskNotExist: '任务不存在或已被删除',
    backToList: '返回任务列表',
    copySuccess: '需求描述已复制到剪贴板',
    copyFailed: '复制失败，请手动复制',
    loadFailed: '加载任务详情失败',
    pleaseSelectFirst: '请先选择要{action}的测试用例',
    confirmAdopt: '确定要采纳选中的 {count} 条测试用例吗？',
    confirmDiscard: '确定要弃用选中的 {count} 条测试用例吗？此操作不可恢复。',
    confirmAdoptTitle: '确认采纳',
    confirmDiscardTitle: '确认弃用',
    confirmAdoptSingle: '确定要采纳测试用例"{scenario}"吗？',
    confirmDiscardSingle: '确定要弃用测试用例"{scenario}"吗？此操作不可恢复。',
    adoptSuccess: '成功采纳 {count} 条测试用例！',
    discardSuccess: '成功弃用 {count} 条测试用例',
    allDiscardedSuccess: '所有测试用例已弃用，任务已删除',
    caseDiscardedSuccess: '测试用例已弃用',
    batchAdoptFailed: '批量采纳失败',
    batchDiscardFailed: '批量弃用失败',
    adoptFailed: '采纳用例失败',
    discardFailed: '弃用用例失败',
    enterScenario: '请输入测试场景',
    updateSuccess: '测试用例更新成功',
    updateFailed: '更新失败',
    noCasesToExport: '没有测试用例可以导出',
    exportSuccess: '测试用例导出成功',
    exportFailed: '导出Excel失败',

    // 确认按钮
    btnConfirm: '确定',
    btnCancelOperation: '取消',

    // Excel 导出
    excelSheetName: '测试用例',
    excelFileName: '测试用例_{taskId}_{date}.xlsx'
  },

  // 配置引导弹框
  configGuide: {
    title: '开始使用AI用例生成功能',
    subtitle: '在使用前，请先完成以下配置：',
    // 配置分组
    modelConfig: '模型配置',
    promptConfig: '提示词配置',
    generationConfig: '生成行为配置',
    // 配置项标签
    caseWriter: '用例编写',
    caseReviewer: '用例评审',
    generationSettings: '生成配置',
    // 状态文本
    unconfigured: '未配置',
    disabled: '已禁用',
    // 按钮
    goToConfig: '去配置',
    configureLater: '稍后配置'
  }
}
