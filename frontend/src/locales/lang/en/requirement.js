export default {
  requirementAnalysis: {
    // Page
    title: 'AI Test Case Generation',
    subtitle: 'AI will generate high-quality test cases based on requirement descriptions or documents',

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
    supportedFormats: 'Supports PDF, Word, TXT formats',
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
    statusCompleted: 'Generation complete!',
    statusFailed: 'Generation failed',
    generateCompleteSuccess: 'Test case generation complete!',
    checkProgressFailed: 'Failed to check progress',
    createTaskFailed: 'Failed to create task',
    unknownError: 'Unknown error',

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
  }
}
