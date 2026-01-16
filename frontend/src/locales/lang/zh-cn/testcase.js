export default {
  testcase: {
    // Page titles
    title: '测试用例',
    detail: '用例详情',
    edit: '编辑测试用例',
    create: '创建测试用例',

    // Actions
    newCase: '新建用例',
    batchDelete: '批量删除',
    exportExcel: '导出Excel',
    saveChanges: '保存修改',
    createCase: '创建用例',

    // Field labels
    caseTitle: '用例标题',
    caseDescription: '用例描述',
    project: '归属项目',
    relatedProject: '关联项目',
    relatedVersions: '关联版本',
    priority: '优先级',
    status: '状态',
    testType: '测试类型',
    preconditions: '前置条件',
    steps: '操作步骤',
    expectedResult: '预期结果',
    author: '作者',
    createdAt: '创建时间',
    serialNumber: '序号',

    // Priority
    low: '低',
    medium: '中',
    high: '高',
    critical: '紧急',

    // Status
    draft: '草稿',
    active: '激活',
    deprecated: '废弃',

    // Test types
    functional: '功能测试',
    integration: '集成测试',
    api: 'API测试',
    ui: 'UI测试',
    performance: '性能测试',
    security: '安全测试',

    // Placeholders
    searchPlaceholder: '搜索用例标题',
    caseTitlePlaceholder: '请输入测试用例标题',
    caseDescriptionPlaceholder: '请输入用例描述',
    selectProject: '请选择项目',
    selectPriority: '请选择优先级',
    selectTestType: '请选择测试类型',
    selectStatus: '请选择状态',
    selectVersions: '请选择版本（可多选）',
    preconditionsPlaceholder: '请输入前置条件',
    stepsPlaceholder: '请输入详细的操作步骤，如：\n1. 打开登录页面\n2. 输入用户名和密码\n3. 点击登录按钮\n4. 验证登录结果',
    expectedResultPlaceholder: '请输入整体预期结果',
    priorityFilter: '优先级筛选',
    statusFilter: '状态筛选',

    // Messages
    fetchListFailed: '获取测试用例列表失败',
    fetchDetailFailed: '获取用例详情失败',
    deleteConfirm: '确定要删除这个测试用例吗？',
    deleteSuccess: '测试用例删除成功',
    deleteFailed: '测试用例删除失败',
    selectFirst: '请先选择要删除的测试用例',
    batchDeleteConfirm: '确定要删除选中的 {count} 个测试用例吗？此操作不可恢复。',
    batchDeleteSuccess: '成功删除 {successCount} 个测试用例',
    batchDeletePartialSuccess: '成功删除 {successCount} 个测试用例，{failCount} 个失败',
    batchDeleteFailed: '删除失败',
    batchDeleteError: '批量删除失败',
    noDataToExport: '没有测试用例数据可导出',
    exportSuccess: '测试用例导出成功',
    exportFailed: '导出测试用例失败',
    createSuccess: '测试用例创建成功',
    createFailed: '测试用例创建失败',
    updateSuccess: '测试用例修改成功',
    updateFailed: '测试用例修改失败',
    fetchProjectsFailed: '获取项目列表失败',
    fetchVersionsFailed: '获取项目版本失败',

    // Other
    noVersion: '未关联版本',
    noProject: '未关联项目',
    noDescription: '暂无描述',
    none: '无',
    baseline: '基线',

    // Validation
    titleRequired: '请输入用例标题',
    titleLength: '标题长度在 5 到 500 个字符',
    expectedResultRequired: '请输入预期结果',
    stepsMaxLength: '操作步骤不能超过1000个字符',

    // Excel export
    excelNumber: '测试用例编号',
    excelTitle: '用例标题',
    excelProject: '关联项目',
    excelVersions: '关联版本',
    excelPreconditions: '前置条件',
    excelSteps: '操作步骤',
    excelExpectedResult: '预期结果',
    excelPriority: '优先级',
    excelStatus: '状态',
    excelTestType: '测试类型',
    excelAuthor: '作者',
    excelCreatedAt: '创建时间',
    excelSheetName: '测试用例',
    excelFileName: '测试用例_{date}.xlsx'
  },
  testSuite: {
    title: '测试套件',
    newSuite: '新建套件',
    inDevelopment: '测试套件功能开发中...'
  }
}
