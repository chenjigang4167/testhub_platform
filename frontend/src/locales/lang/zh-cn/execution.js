export default {
  // Page titles
  title: '执行记录',
  testPlan: '测试计划',
  planDetail: '计划详情',
  executionHistory: '执行历史记录',
  inDevelopment: '执行记录功能开发中...',

  // Actions
  newPlan: '新建测试计划',
  batchDelete: '批量删除',
  viewExecution: '查看执行',
  createPlan: '创建',
  updatePlan: '保存',
  closePlan: '关闭',
  activatePlan: '激活',
  viewHistory: '历史',

  // Table columns
  serialNumber: '序号',
  planName: '计划名称',
  project: '项目',
  projects: '项目',
  version: '版本',
  creator: '创建者',
  status: '状态',
  createdAt: '创建时间',
  actions: '操作',
  testCase: '测试用例',
  executionStatus: '执行状态',
  comments: '备注',
  executedBy: '执行者',
  executedAt: '执行时间',

  // Status
  active: '激活',
  closed: '已关闭',
  untested: '未测试',
  passed: '通过',
  failed: '失败',
  blocked: '阻塞',
  retest: '重测',
  completed: '已完成',
  notStarted: '未开始',
  inProgress: '进行中',

  // Statistics
  total: '总计',
  progressRate: '进度',

  // Dialog titles
  createPlanDialog: '新建测试计划',
  editPlanDialog: '编辑测试计划',

  // Form labels
  planDescription: '计划描述',
  relatedProjects: '关联项目',
  relatedVersion: '关联版本',
  testCases: '测试用例',
  assignees: '指派给',
  planStatus: '状态',
  activeText: '激活',
  inactiveText: '已关闭',

  // Placeholders
  planNamePlaceholder: '请输入计划名称',
  planDescriptionPlaceholder: '请输入计划描述',
  selectProjects: '请选择项目',
  selectVersion: '请选择版本',
  selectTestcases: '请选择用例',
  selectTestcasesDisabled: '请先选择项目',
  loadingTestcases: '加载中...',
  selectAssignees: '请选择执行人员',
  commentsPlaceholder: '请输入备注',

  // Filters
  selectProject: '选择项目',
  selectStatus: '选择状态',
  filterActive: '激活',
  filterClosed: '已关闭',

  // Messages
  fetchListFailed: '获取测试计划失败',
  fetchDetailFailed: '获取测试计划详情失败',
  fetchBasicDataFailed: '获取基础数据失败',
  fetchTestcasesFailed: '获取测试用例失败',
  fetchHistoryFailed: '获取历史记录失败',
  createSuccess: '测试计划创建成功',
  createFailed: '创建测试计划失败',
  updateSuccess: '测试计划更新成功',
  updateFailed: '更新测试计划失败',
  statusUpdateSuccess: '状态更新成功',
  statusUpdateFailed: '状态更新失败',
  detailsUpdateSuccess: '详细信息更新成功',
  detailsUpdateFailed: '详细信息更新失败',
  selectFirst: '请先选择要删除的测试计划',
  selectCasesFirst: '请先选择要删除的用例',
  selectProjectFirst: '请先选择项目',
  batchDeleteConfirm: '确定要删除选中的 {count} 个测试计划吗？此操作不可恢复。',
  batchDeleteCasesConfirm: '确定要删除选中的 {count} 个用例吗？此操作不可恢复。',
  batchDeleteSuccess: '成功删除 {successCount} 个测试计划',
  batchDeleteCasesSuccess: '成功删除 {successCount} 个用例',
  batchDeletePartialSuccess: '成功删除 {successCount} 个测试计划，{failCount} 个失败',
  batchDeleteCasesPartialSuccess: '成功删除 {successCount} 个用例，{failCount} 个失败',
  batchDeleteFailed: '删除失败',
  toggleStatusConfirm: '确定要{action}这个测试计划吗？',
  toggleStatusSuccess: '{action}成功',
  toggleStatusFailed: '操作失败',

  // Other
  noProject: '未关联项目',
  noData: '-',

  // Validation
  planNameRequired: '请输入计划名称',
  projectsRequired: '请选择项目',
  testcasesRequired: '请选择至少一个测试用例',
  selectProjectBeforeTestcases: '请先选择项目'
}
