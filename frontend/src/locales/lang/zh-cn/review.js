export default {
  reviewList: {
    title: '用例评审',
    createReview: '创建评审',
    project: '项目',
    selectProject: '请选择项目',
    status: '评审状态',
    selectStatus: '请选择状态',
    reviewer: '评审人',
    selectReviewer: '请选择评审人',
    search: '搜索',
    reset: '重置',

    // Table columns
    reviewTitle: '评审标题',
    reviewProject: '项目',
    reviewStatus: '评审状态',
    priority: '优先级',
    creator: '创建人',
    testcaseCount: '用例数量',
    progress: '评审进度',
    deadline: '截止时间',
    createdAt: '创建时间',
    actions: '操作',

    // Status
    statusPending: '待评审',
    statusInProgress: '评审中',
    statusApproved: '已通过',
    statusRejected: '未通过',
    statusCancelled: '已取消',

    // Priority
    priorityLow: '低',
    priorityMedium: '中',
    priorityHigh: '高',
    priorityCritical: '紧急',

    // Actions
    detail: '详情',
    review: '评审',
    edit: '编辑',
    delete: '删除',

    // Review dialog
    submitReview: '提交评审',
    reviewResult: '评审结果',
    approved: '通过',
    rejected: '未通过',
    reviewComment: '评审意见',
    reviewCommentPlaceholder: '请输入评审意见',
    submit: '提交',
    cancel: '取消',

    // Messages
    deleteConfirm: '确定要删除这条评审吗？',
    deleteSuccess: '删除成功',
    deleteFailed: '删除失败',
    submitSuccess: '提交成功',
    submitFailed: '提交失败',
    fetchListFailed: '获取评审列表失败',
    fetchProjectsFailed: '获取项目列表失败',
    fetchReviewersFailed: '获取评审人列表失败',

    // Empty state
    noData: '暂无数据',
    noDeadline: '无截止时间'
  },
  reviewTemplate: {
    title: '评审模板',
    createTemplate: '创建模板',
    useTemplate: '使用',
    edit: '编辑',
    delete: '删除',

    // Filter
    project: '项目',
    selectProject: '请选择项目',

    // Card labels
    projectLabel: '项目:',
    creatorLabel: '创建人:',
    createdAtLabel: '创建时间:',
    descriptionLabel: '描述',
    checklistTitle: '检查清单:',
    reviewersTitle: '默认评审人:',

    // Empty states
    noDescription: '暂无描述',
    noChecklist: '暂无检查清单',
    noReviewers: '未设置默认评审人',
    noData: '暂无评审模板',
    moreItems: '还有 {count} 项...',

    // Dialog
    createTitle: '创建模板',
    editTitle: '编辑模板',
    templateName: '模板名称',
    templateNamePlaceholder: '请输入模板名称',
    associatedProject: '关联项目',
    templateDescription: '模板描述',
    templateDescriptionPlaceholder: '请输入模板描述',
    checklist: '检查清单',
    checklistItemPlaceholder: '请输入检查项',
    addChecklistItem: '添加检查项',
    defaultReviewers: '默认评审人',
    selectDefaultReviewers: '请选择默认评审人',
    save: '保存',
    cancel: '取消',

    // Validation
    nameRequired: '请输入模板名称',
    projectRequired: '请选择项目',

    // Messages
    deleteConfirm: '确定要删除这个模板吗？',
    deleteSuccess: '删除成功',
    deleteFailed: '删除失败',
    createSuccess: '模板创建成功',
    createFailed: '模板创建失败',
    updateSuccess: '模板更新成功',
    updateFailed: '模板更新失败',
    fetchListFailed: '获取模板列表失败',
    fetchProjectsFailed: '获取项目列表失败',
    fetchUsersFailed: '获取用户列表失败'
  }
}
