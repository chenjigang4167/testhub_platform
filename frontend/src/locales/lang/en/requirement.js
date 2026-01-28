export default {
  requirementAnalysis: {
    // Page
    title: 'AI Test Case Generation',
    subtitle: 'AI will generate high-quality test cases based on requirement descriptions or documents',

    // Output Mode
    outputModeTitle: '📤 Output Mode Settings',
    outputModeDesc: 'Select the output method for test case generation (applies to both manual input and document upload)',
    realtimeStream: '⚡ Real-time Stream',
    realtimeStreamDesc: 'Display character by character, smooth experience, suitable for large requirement documents',
    completeOutput: '📄 Complete Output',
    completeOutputDesc: 'Display all at once after completion, suitable for simple requirements',

    // Manual Input
    manualInputTitle: '✍️ Manual Input',
    requirementTitle: 'Requirement Title',
    requirementDescription: 'Requirement Description',
    relatedProject: 'Related Project (Optional)',
    associatedProject: 'Related Project (Optional)',
    titlePlaceholder: 'Enter requirement title, e.g.: User Login Feature',
    descriptionPlaceholder: 'Describe your requirement in detail, including features, scenarios, business flows, etc.',
    selectProject: 'Select Project',
    charCount: '{count}/2000',
    generating: '🔄 Generating...',
    generateBtn: '🚀 Generate Test Cases',
    generateButton: '🚀 Generate Test Cases',

    // Document Upload
    uploadTitle: '📄 Upload Document',
    dragDropText: 'Drag file here or click to select',
    supportedFormats: 'Supports PDF, Word, TXT, Markdown formats',
    selectFileBtn: 'Select File',
    selectFile: 'Select File',
    removeFile: '❌',
    documentTitle: 'Document Title',
    documentTitlePlaceholder: 'Enter document title',
    documentPlaceholder: 'Enter document title',
    documentContent: 'Document Content',
    fileSize: 'File Size',

    // Generation Options
    generationOptions: '⚙️ Generation Options',
    testCaseCount: 'Expected Number of Test Cases',
    detailLevel: 'Detail Level',
    detailSimple: 'Simple',
    detailNormal: 'Normal',
    detailDetailed: 'Detailed',
    includeEdgeCases: 'Include Edge Cases',
    includeNegativeCases: 'Include Negative Cases',
    submitGeneration: 'Submit Generation Task',

    // Divider
    dividerOr: 'or',

    // Messages
    titleRequired: 'Please enter requirement title',
    descriptionRequired: 'Please enter requirement description',
    descriptionTooShort: 'Description must be at least 10 characters',
    fileRequired: 'Please select a file',
    generateSuccess: 'Generation task submitted!',
    generateFailed: 'Generation failed',
    uploadSuccess: 'File uploaded successfully',
    uploadFailed: 'File upload failed',
    fillRequiredInfo: 'Please fill in required information',
    selectFileAndTitle: 'Please select a file and enter document title',
    invalidFileFormat: 'Unsupported file format',
    invalidFileFormatDetail: 'Please select a PDF, Word, TXT, or Markdown file',
    extractingContent: 'Extracting document content...',
    extractionFailed: 'Failed to extract document content',
    documentProcessingFailed: 'Document processing failed',
    loadProjectsFailed: 'Failed to load project list',

    // Progress
    analyzingRequirement: '📖 Analyzing requirement...',
    generatingTestCases: '✍️ Writing test cases...',
    reviewingTestCases: '🔍 Reviewing test cases...',
    generationComplete: '✅ Generation Complete!',
    generationFailed: '❌ Generation Failed',
    creatingTask: 'Creating generation task...',
    taskCreated: 'Task created, starting generation...',
    preparing: 'Preparing...',

    // Generation Status
    aiGeneratingTitle: '🤖 AI is Generating Test Cases',
    taskId: 'Task ID',
    currentStatus: 'Current Status',
    taskStatus: 'Task Status',
    progress: 'Progress',
    stepAnalysis: 'Requirement Analysis',
    stepWriting: 'Writing Cases',
    stepReview: 'Case Review',
    stepComplete: 'Complete',
    cancelGeneration: 'Cancel Generation',
    generationCancelled: 'Generation cancelled',
    statusGenerating: 'Writing test cases...',
    statusReviewing: 'Reviewing test cases...',
    statusRevising: 'Generating final test cases...',
    statusCompleted: 'Generation complete!',
    statusFailed: 'Generation failed',
    generateCompleteSuccess: 'Test case generation complete!',
    checkProgressFailed: 'Failed to check progress',
    createTaskFailed: 'Failed to create task',
    unknownError: 'Unknown error',
    tokenRefreshFailed: 'Token refresh failed, please login again',
    streamConnectionInterrupted: 'Stream connection interrupted, switching to polling mode',
    fetchResultFailed: 'Failed to fetch result',

    // Stream Display
    realtimeGeneratedContent: '✍️ Real-time Generated Content',
    aiReviewComments: '📝 AI Review Comments',
    finalVersionTestCases: '✅ Final Test Cases',
    characters: '{count} characters',

    // Results
    viewResultsBtn: 'View Results',
    generateAgainBtn: 'Generate Again',
    backBtn: 'Back',
    newGeneration: 'New Generation Task',
    summaryTaskId: 'Task ID: {taskId}',
    summaryGenerationTime: 'Generation Time: {time}',
    aiGeneratedTestCases: 'AI Generated Test Cases',
    aiReviewFeedback: 'AI Review Feedback',
    finalTestCases: 'Final Test Cases',
    downloadExcel: 'Download Excel',
    saveToRecords: 'Save to Records',

    // Excel Export
    testCaseSheetName: 'Test Cases',
    excelFileName: 'AI_Generated_TestCases_{taskId}_{date}.xlsx',
    downloadSuccess: 'Download successful',
    downloadFailed: 'Download failed',
    testCaseContent: 'Test Case Content',
    excelTestCaseNumber: 'Case No.',
    excelTestScenario: 'Test Scenario',
    excelPrecondition: 'Precondition',
    excelTestSteps: 'Test Steps',
    excelExpectedResult: 'Expected Result',
    excelPriority: 'Priority',

    // Save
    saveSuccess: 'Successfully saved {count} test cases',
    saveFailed: 'Save failed',
    alreadySaved: 'Test cases already saved',

    // Status
    pending: 'Pending',
    processing: 'Processing',
    completed: 'Completed',
    failed: 'Failed'
  },
  generatedTestCases: {
    // Page
    title: 'AI Generated Test Cases',

    // Filters
    statusFilter: 'Status Filter:',
    allStatus: 'All Status',
    pending: 'Analyzing',
    generating: 'Writing',
    reviewing: 'Reviewing',
    completed: 'Completed',
    failed: 'Failed',

    // Status Display
    statusPending: 'Analyzing',
    statusGenerating: 'Writing',
    statusReviewing: 'Reviewing',
    statusCompleted: 'Completed',
    statusFailed: 'Failed',
    statusDraft: 'Draft',
    statusActive: 'Active',

    // Actions
    batchDelete: '🗑️ Batch Delete({count})',
    deleting: '🗑️ Deleting...',
    refresh: '🔄 Refresh',
    loading: '🔄 Loading...',

    // Stats
    totalTasks: 'Total',
    completedTasks: 'Completed',
    runningTasks: 'Running',
    failedTasks: 'Failed',
    completedCount: 'Completed',
    runningCount: 'Running',
    failedCount: 'Failed',

    // Table Headers
    serialNumber: 'No.',
    taskId: 'Task ID',
    relatedRequirement: 'Requirement',
    requirement: 'Requirement',
    status: 'Status',
    caseCount: 'Cases',
    generatedTime: 'Time',
    generationTime: 'Time',
    actions: 'Actions',

    // Actions
    viewDetail: 'View',
    adoptAll: 'Adopt All',
    exportExcel: 'Export',
    delete: 'Delete',
    batchAdopt: 'Batch Adopt',
    batchDiscard: 'Batch Discard',

    // Empty State
    noTasks: 'No Tasks',
    noTasksHint: 'No AI generation tasks yet. Go to',
    noTasksLink: 'AI Generation',
    noTasksHint2: 'page to create one!',
    emptyHint: 'No AI generation tasks yet. Go to',
    aiGeneration: 'AI Generation',
    createTask: 'page to create one!',

    // Loading
    loadingTasks: '🔄 Loading task list...',
    generatingWait: 'Task is generating, please wait...',

    // Pagination
    pageSize: 'Page Size:',
    pageSizeUnit: '{size} items',
    previousPage: 'Previous',
    nextPage: 'Next',
    jumpTo: 'Jump to:',
    pageNumber: 'Page',
    jump: 'Go',
    paginationInfo: 'Showing {start}-{end} of {total}',

    // Detail Modal
    caseNumber: 'Case No.',
    priority: 'Priority',
    preconditions: 'Preconditions',
    testSteps: 'Test Steps',
    expectedResult: 'Expected Result',
    reviewComments: 'Review Comments',
    generatedAI: 'Generated By',
    reviewedAI: 'Reviewed By',

    // Adopt Modal
    adoptModalTitle: 'Adopt Test Case',
    caseTitle: 'Case Title',
    caseTitlePlaceholder: 'Enter case title',
    caseDescription: 'Case Description',
    caseDescriptionPlaceholder: 'Enter case description',
    belongsToProject: 'Project',
    selectProject: 'Select Project',
    relatedVersion: 'Version',
    selectVersion: 'Select Version',
    baseline: '(Baseline)',
    showingProjectVersions: 'Showing versions for {project}',
    showingAllVersions: 'Showing all versions',
    priorityLow: 'Low',
    priorityMedium: 'Medium',
    priorityHigh: 'High',
    priorityCritical: 'Critical',
    testType: 'Test Type',
    testTypeFunctional: 'Functional',
    testTypeIntegration: 'Integration',
    testTypeAPI: 'API',
    testTypeUI: 'UI',
    testTypePerformance: 'Performance',
    testTypeSecurity: 'Security',
    preconditionsPlaceholder: 'Enter preconditions',
    operationSteps: 'Steps',
    operationStepsPlaceholder: 'Enter operation steps',
    expectedResultPlaceholder: 'Enter expected result',
    adopting: 'Adopting...',
    confirmAdopt: 'Confirm Adopt',
    cancel: 'Cancel',

    // Messages
    deleteConfirm: 'Are you sure to delete this task?',
    batchDeleteConfirm: 'Are you sure to delete {count} selected tasks? This cannot be undone.',
    deleteSuccess: 'Successfully deleted {success} tasks, {failed} failed',
    deleteFailed: 'Delete failed',
    batchDeleteSuccess: 'Successfully deleted {count} tasks',
    batchDeleteFailed: 'Batch delete failed',
    adoptAllSuccess: 'All cases adopted successfully',
    adoptAllFailed: 'Adopt failed',
    exportSuccess: 'Export successful',
    exportFailed: 'Export failed',
    loadFailed: 'Failed to load task list',
    loadTasksFailed: 'Failed to load task list',
    loadStatsFailed: 'Failed to load statistics',
    selectTasksFirst: 'Please select tasks to delete first',
    unknownError: 'Unknown error',

    // Adopt/Discard
    adoptConfirm: 'Are you sure to adopt all cases for task "{title}"?',
    adoptSuccess: 'Adopted successfully',
    adoptFailed: 'Adopt failed',
    discardConfirm: 'Are you sure to discard all cases for task "{title}"?',
    discardSuccess: 'Discarded successfully',
    discardFailed: 'Discard failed',
    fetchProjectsFailed: 'Failed to fetch projects',
    fetchVersionsFailed: 'Failed to fetch versions',
    fetchProjectVersionsFailed: 'Failed to fetch project versions',
    selectProjectRequired: 'Please select a project',
    selectVersionRequired: 'Please select a version',
    enterCaseTitle: 'Please enter case title',
    enterExpectedResult: 'Please enter expected result',
    updateStatusFailed: 'Failed to update status',
    adoptModalSuccess: 'Case adopted successfully!',
    adoptCaseFailed: 'Failed to adopt case',
    adoptCaseFailedRetry: 'Failed to adopt case, please retry',
    discardCaseConfirm: 'Are you sure to discard case "{title}"?',
    caseDiscarded: 'Case discarded',
    discardCaseFailed: 'Failed to discard case',
    discardCaseFailedRetry: 'Failed to discard case, please retry',

    // Selection
    selectAll: 'Select All',
    selectedCount: '{count} selected'
  },
  promptConfig: {
    // Page
    title: '📝 Prompt Configuration',
    subtitle: 'Configure AI prompts for test case writing and review',

    // Section
    configListTitle: 'Prompt Configuration List',
    loadDefaults: '📂 Load Defaults',
    addConfig: '➕ Add Config',

    // Config Card
    enabled: 'Enabled',
    disabled: 'Disabled',
    preview: '👁️ Preview',
    edit: '✏️ Edit',
    delete: '🗑️ Delete',

    // Config Details
    contentPreview: 'Content Preview:',
    createdAt: 'Created:',
    updatedAt: 'Updated:',
    creator: 'Creator:',
    createdBy: 'Creator:',
    unknown: 'Unknown',

    // Modal
    addTitle: 'Add Prompt Configuration',
    editTitle: 'Edit Prompt Configuration',
    editConfig: 'Edit Prompt Configuration',
    configName: 'Config Name',
    configNamePlaceholder: 'e.g.: Test Case Writing Prompt v1.0',
    required: '*',
    promptType: 'Prompt Type',
    testCaseWriter: 'Test Case Writer',
    testCaseReviewer: 'Test Case Reviewer',
    selectType: 'Select Type',
    selectPromptType: 'Select Prompt Type',
    writerPrompt: 'Test Case Writer Prompt',
    reviewerPrompt: 'Test Case Reviewer Prompt',
    isActive: 'Enable',
    promptContent: 'Prompt Content',
    contentPlaceholder: 'Enter prompt content, supports variables...',
    contentHint: 'Tip: Use variables like {requirement} {project}',
    charCount: 'Characters: {count}',
    saveBtn: '💾 Save',
    saveConfig: '💾 Save Config',
    cancel: 'Cancel',
    cancelBtn: 'Cancel',
    saving: '💾 Saving...',
    enableConfig: 'Enable this config',
    enableHint: 'When enabled, other configs of the same type will be disabled',

    // Writing Tips
    writingTipsTitle: 'Prompt Writing Tips:',
    tip1: 'Use {requirement} for requirement content',
    tip2: 'Use {project} for project information',
    tip3: 'Clearly describe AI role and task',
    tip4: 'Specify output format and structure',

    // Preview Modal
    previewTitle: 'Preview Prompt - {name}',
    type: 'Type:',
    status: 'Status:',
    closeBtn: 'Close',

    // Default Prompts Modal
    defaultPromptsPreview: 'Default Prompts Preview',
    writerTab: 'Test Case Writer',
    reviewerTab: 'Test Case Reviewer',
    noContent: 'No content',
    loading: 'Loading...',
    confirmLoad: 'Confirm Load',
    defaultWriterName: 'Default Test Case Writer Prompt',
    defaultReviewerName: 'Default Test Case Reviewer Prompt',
    defaultsLoadSuccess: 'Default prompts loaded successfully',

    // Empty State
    noConfigs: 'No Configurations',
    noConfigsHint: 'Add prompt configurations to customize AI behavior and output format',
    emptyHint: 'Add prompt configurations to customize AI behavior and output format',
    addFirstConfig: '➕ Add First Config',
    loadDefaultsFirst: '📂 Load Defaults',

    // Messages
    nameRequired: 'Please enter config name',
    typeRequired: 'Please select prompt type',
    contentRequired: 'Please enter prompt content',
    saveSuccess: 'Saved successfully',
    saveFailed: 'Save failed',
    addSuccess: 'Configuration added successfully',
    updateSuccess: 'Configuration updated successfully',
    saveConfigFailed: 'Failed to save configuration',
    deleteConfirm: 'Are you sure to delete this configuration?',
    deleteSuccess: 'Deleted successfully',
    deleteFailed: 'Delete failed',
    deleteConfigFailed: 'Failed to delete configuration',
    loadDefaultsSuccess: 'Default prompts loaded successfully',
    loadDefaultsFailed: 'Failed to load default prompts',
    loadConfigsFailed: 'Failed to load configurations',
    loadFailed: 'Load failed',
    pleaseLogin: 'Please login first'
  },
  generationConfig: {
    // Page
    title: '⚙️ Generation Behavior Config',
    subtitle: 'Configure default behavior and automation flow for test case generation',
    description: 'Configure default behavior and automation flow for test case generation',

    // Config List
    configList: 'Configuration List',
    addConfig: '➕ Add Config',
    addFirstConfig: '➕ Add First Config',
    emptyTitle: 'No Generation Config',
    emptyDescription: 'Please add generation behavior config to control default behavior of test case generation',

    // Config Card
    enabled: '✅ Enabled',
    disabled: '❌ Disabled',
    streamMode: '⚡ Stream Output',
    completeMode: '📄 Complete Output',
    enable: '✅ Enable',
    edit: '✏️ Edit',
    delete: '🗑️ Delete',

    // Sections
    outputMode: '📤 Output Mode',
    automationProcess: '🤖 Automation Process',
    timeoutSettings: '⏱️ Timeout Settings',

    // Fields
    defaultMode: 'Default Mode:',
    aiReview: 'AI Review & Improve:',
    reviewTimeout: 'Review & Improve Timeout:',
    seconds: 'seconds',
    createdAt: 'Created At:',
    updatedAt: 'Updated At:',

    // Form
    editTitle: 'Edit',
    addTitle: 'Add',
    formTitle: 'Generation Behavior Config',
    basicInfo: '📋 Basic Information',
    configName: 'Config Name',
    configNamePlaceholder: 'e.g.: Default Generation Config',
    defaultConfigName: 'Default Generation Config',
    enableThisConfig: 'Enable this config',
    enableHint: 'Note: Only one config can be enabled. Enabling this will automatically disable other configs',

    // Output Mode
    outputModeSettings: '📤 Output Mode Settings',
    defaultOutputMode: 'Default Output Mode',
    realtimeStream: '⚡ Real-time Stream',
    completeOutput: '📄 Complete Output',
    outputModeHint: 'Real-time Stream: Display character by character; Complete Output: Display all at once after completion',

    // Automation
    automationSettings: '🤖 Automation Process Config',
    enableAutoReview: 'Enable AI Review & Improve',
    autoReviewHint: 'Automatically perform AI review after generation and improve test cases based on review feedback',

    // Timeout
    timeoutSettingsLabel: '⏱️ Timeout Settings',
    reviewTimeoutLabel: 'Review & Improve Timeout (seconds)',
    timeoutHint: 'Total timeout for AI review and improvement (Recommended: 120s for small docs, 600-1800s for large docs, up to 3600s for very large docs)',

    // Buttons
    cancel: 'Cancel',
    saving: '🔄 Saving...',
    saveConfig: '💾 Save Config',

    // Messages
    loadFailed: 'Failed to load configurations',
    pleaseLogin: 'Please login first',
    saveSuccess: 'Configuration added successfully',
    updateSuccess: 'Configuration updated successfully',
    saveFailed: 'Failed to save',
    enableSuccess: 'Configuration enabled',
    enableFailed: 'Failed to enable',
    deleteSuccess: 'Configuration deleted successfully',
    deleteFailed: 'Failed to delete',
    deleteConfirm: 'Are you sure to delete this configuration?'
  },

  // Task Detail Page
  taskDetail: {
    // Page Header
    title: 'Task Detail',
    taskId: 'Task ID',
    exportBtn: '💾 Export Excel',
    exporting: '💾 Exporting...',

    // Requirement Collapse Card
    requirementTitle: '📋 Requirement Description',
    requirementHint: '(Click to expand for full content)',
    copyRequirement: 'Copy Requirement',

    // Status
    statusPending: 'Analyzing Requirement',
    statusGenerating: 'Writing Test Cases',
    statusReviewing: 'Reviewing Test Cases',
    statusCompleted: 'Completed',
    statusFailed: 'Failed',

    // Batch Operations
    selectAll: 'Select All',
    selectedCount: '{count} test cases selected',
    batchAdopt: '✅ Batch Adopt ({count})',
    batchDiscard: '❌ Batch Discard ({count})',

    // Table Headers
    tableSelect: 'Select',
    tableCaseId: 'Test Case ID',
    tableScenario: 'Test Scenario',
    tablePrecondition: 'Precondition',
    tableSteps: 'Test Steps',
    tableExpected: 'Expected Result',
    tablePriority: 'Priority',
    tableActions: 'Actions',

    // Table Action Buttons
    viewDetail: '📖 View Detail',
    adopt: '✅ Adopt',
    discard: '❌ Discard',

    // Empty State
    emptyTitle: 'No Test Case Data',
    emptyHint: 'No test cases generated yet or all cases have been cleared',

    // Pagination
    paginationInfo: 'Showing {start}-{end} of {total} total',
    pageSizeLabel: 'Items per page:',
    pageSizeOption: '{size} items',
    previousPage: 'Previous',
    nextPage: 'Next',
    currentPageInfo: 'Page {current} of {total}',

    // Modal
    modalEditTitle: 'Edit Test Case',
    modalViewTitle: 'Test Case Detail',
    labelCaseId: 'Case ID:',
    labelScenario: 'Test Scenario:',
    labelPrecondition: 'Precondition:',
    labelSteps: 'Test Steps:',
    labelExpected: 'Expected Result:',
    labelPriority: 'Priority:',
    labelNone: 'None',
    btnEdit: '✏️ Edit',
    btnClose: 'Close',
    btnSave: '💾 Save',
    btnSaveing: '💾 Saving...',
    btnCancel: 'Cancel',

    // Placeholders
    placeholderScenario: 'Enter test scenario',
    placeholderPrecondition: 'Enter precondition',
    placeholderSteps: 'Enter test steps',
    placeholderExpected: 'Enter expected result',
    placeholderPriority: 'Select priority',

    // Messages
    loading: '🔄 Loading task details...',
    taskNotExist: 'Task does not exist or has been deleted',
    backToList: 'Back to Task List',
    copySuccess: 'Requirement description copied to clipboard',
    copyFailed: 'Copy failed, please copy manually',
    loadFailed: 'Failed to load task details',
    pleaseSelectFirst: 'Please select test cases to {action} first',
    confirmAdopt: 'Are you sure to adopt {count} selected test cases?',
    confirmDiscard: 'Are you sure to discard {count} selected test cases? This cannot be undone.',
    confirmAdoptTitle: 'Confirm Adopt',
    confirmDiscardTitle: 'Confirm Discard',
    confirmAdoptSingle: 'Are you sure to adopt test case "{scenario}"?',
    confirmDiscardSingle: 'Are you sure to discard test case "{scenario}"? This cannot be undone.',
    adoptSuccess: 'Successfully adopted {count} test cases!',
    discardSuccess: 'Successfully discarded {count} test cases',
    allDiscardedSuccess: 'All test cases discarded, task deleted',
    caseDiscardedSuccess: 'Test case discarded',
    batchAdoptFailed: 'Batch adopt failed',
    batchDiscardFailed: 'Batch discard failed',
    adoptFailed: 'Failed to adopt test case',
    discardFailed: 'Failed to discard test case',
    enterScenario: 'Please enter test scenario',
    updateSuccess: 'Test case updated successfully',
    updateFailed: 'Update failed',
    noCasesToExport: 'No test cases to export',
    exportSuccess: 'Test cases exported successfully',
    exportFailed: 'Excel export failed',

    // Confirm Buttons
    btnConfirm: 'Confirm',
    btnCancelOperation: 'Cancel',

    // Excel Export
    excelSheetName: 'Test Cases',
    excelFileName: 'TestCases_{taskId}_{date}.xlsx'
  },

  // Configuration Guide Modal
  configGuide: {
    title: 'Get Started with AI Test Case Generation',
    subtitle: 'Please complete the following configurations before use:',
    // Configuration Groups
    modelConfig: 'Model Configuration',
    promptConfig: 'Prompt Configuration',
    generationConfig: 'Generation Behavior Configuration',
    // Configuration Item Labels
    caseWriter: 'Case Writer',
    caseReviewer: 'Case Reviewer',
    generationSettings: 'Generation Settings',
    // Status Text
    unconfigured: 'Not Configured',
    disabled: 'Disabled',
    // Buttons
    goToConfig: 'Configure Now',
    configureLater: 'Configure Later'
  }
}
