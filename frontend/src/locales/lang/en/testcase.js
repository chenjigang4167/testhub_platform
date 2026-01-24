export default {
  testcase: {
    // Page titles
    title: 'Test Cases',
    detail: 'Test Case Details',
    edit: 'Edit Test Case',
    create: 'Create Test Case',

    // Actions
    newCase: 'New Case',
    batchDelete: 'Batch Delete',
    exportExcel: 'Export Excel',
    saveChanges: 'Save Changes',
    createCase: 'Create Case',

    // Field labels
    caseTitle: 'Case Title',
    caseDescription: 'Case Description',
    project: 'Project',
    relatedProject: 'Related Project',
    relatedVersions: 'Related Versions',
    priority: 'Priority',
    status: 'Status',
    testType: 'Test Type',
    preconditions: 'Preconditions',
    steps: 'Steps',
    expectedResult: 'Expected Result',
    author: 'Author',
    createdAt: 'Created At',
    serialNumber: 'No.',

    // Priority
    low: 'Low',
    medium: 'Medium',
    high: 'High',
    critical: 'Critical',

    // Status
    draft: 'Draft',
    active: 'Active',
    deprecated: 'Deprecated',

    // Test types
    functional: 'Functional Testing',
    integration: 'Integration Testing',
    api: 'API Testing',
    ui: 'UI Testing',
    performance: 'Performance Testing',
    security: 'Security Testing',

    // Placeholders
    searchPlaceholder: 'Search case title',
    caseTitlePlaceholder: 'Enter test case title',
    caseDescriptionPlaceholder: 'Enter case description',
    selectProject: 'Select project',
    selectPriority: 'Select priority',
    selectTestType: 'Select test type',
    selectStatus: 'Select status',
    selectVersions: 'Select versions (multiple)',
    preconditionsPlaceholder: 'Enter preconditions',
    stepsPlaceholder: 'Enter detailed steps, e.g.:\n1. Open login page\n2. Enter username and password\n3. Click login button\n4. Verify login result',
    expectedResultPlaceholder: 'Enter overall expected result',
    priorityFilter: 'Priority Filter',
    statusFilter: 'Status Filter',

    // Messages
    fetchListFailed: 'Failed to fetch test case list',
    fetchDetailFailed: 'Failed to fetch test case details',
    deleteConfirm: 'Are you sure to delete this test case?',
    deleteSuccess: 'Test case deleted successfully',
    deleteFailed: 'Failed to delete test case',
    selectFirst: 'Please select test cases to delete first',
    batchDeleteConfirm: 'Are you sure to delete selected {count} test cases? This action cannot be undone.',
    batchDeleteSuccess: 'Successfully deleted {successCount} test cases',
    batchDeletePartialSuccess: 'Successfully deleted {successCount} test cases, {failCount} failed',
    batchDeleteFailed: 'Delete failed',
    batchDeleteError: 'Batch delete failed',
    noDataToExport: 'No test case data to export',
    exportSuccess: 'Test cases exported successfully',
    exportFailed: 'Failed to export test cases',
    createSuccess: 'Test case created successfully',
    createFailed: 'Failed to create test case',
    updateSuccess: 'Test case updated successfully',
    updateFailed: 'Failed to update test case',
    fetchProjectsFailed: 'Failed to fetch project list',
    fetchVersionsFailed: 'Failed to fetch project versions',

    // Other
    noVersion: 'No version',
    noProject: 'No project',
    noDescription: 'No description',
    none: 'None',
    baseline: 'Baseline',

    // Validation
    titleRequired: 'Please enter case title',
    titleLength: 'Title length must be between 5 and 500 characters',
    expectedResultRequired: 'Please enter expected result',
    stepsMaxLength: 'Steps cannot exceed 1000 characters',

    // Excel export
    excelNumber: 'Test Case ID',
    excelTitle: 'Case Title',
    excelProject: 'Related Project',
    excelVersions: 'Related Versions',
    excelPreconditions: 'Preconditions',
    excelSteps: 'Steps',
    excelExpectedResult: 'Expected Result',
    excelPriority: 'Priority',
    excelStatus: 'Status',
    excelTestType: 'Test Type',
    excelAuthor: 'Author',
    excelCreatedAt: 'Created At',
    excelSheetName: 'Test Cases',
    excelFileName: 'TestCases_{date}.xlsx'
  },
  testSuite: {
    title: 'Test Suites',
    newSuite: 'New Suite',
    inDevelopment: 'Test suite feature is under development...'
  }
}
