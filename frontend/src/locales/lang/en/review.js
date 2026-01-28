export default {
  reviewList: {
    title: 'Test Case Review',
    createReview: 'Create Review',
    project: 'Project',
    selectProject: 'Select Project',
    status: 'Review Status',
    selectStatus: 'Select Status',
    reviewer: 'Reviewer',
    selectReviewer: 'Select Reviewer',
    search: 'Search',
    reset: 'Reset',

    // Table columns
    reviewTitle: 'Review Title',
    reviewProject: 'Project',
    reviewStatus: 'Review Status',
    priority: 'Priority',
    creator: 'Creator',
    testcaseCount: 'Test Cases',
    progress: 'Review Progress',
    deadline: 'Deadline',
    createdAt: 'Created At',
    actions: 'Actions',

    // Status
    statusPending: 'Pending',
    statusInProgress: 'In Progress',
    statusApproved: 'Approved',
    statusRejected: 'Rejected',
    statusCancelled: 'Cancelled',

    // Priority
    priorityLow: 'Low',
    priorityMedium: 'Medium',
    priorityHigh: 'High',
    priorityCritical: 'Critical',

    // Actions
    detail: 'Detail',
    review: 'Review',
    edit: 'Edit',
    delete: 'Delete',

    // Review dialog
    submitReview: 'Submit Review',
    reviewResult: 'Review Result',
    approved: 'Approved',
    rejected: 'Rejected',
    reviewComment: 'Review Comment',
    reviewCommentPlaceholder: 'Enter review comment',
    submit: 'Submit',
    cancel: 'Cancel',

    // Messages
    deleteConfirm: 'Are you sure to delete this review?',
    deleteSuccess: 'Deleted successfully',
    deleteFailed: 'Failed to delete',
    submitSuccess: 'Submitted successfully',
    submitFailed: 'Failed to submit',
    fetchListFailed: 'Failed to fetch review list',
    fetchProjectsFailed: 'Failed to fetch projects',
    fetchReviewersFailed: 'Failed to fetch reviewers',

    // Empty state
    noData: 'No data',
    noDeadline: 'No deadline'
  },

  // Review Detail Page
  reviewDetail: {
    title: 'Review Detail',
    back: 'Back',
    edit: 'Edit',
    submitReview: 'Submit Review',

    // Basic Info Card
    basicInfo: 'Basic Information',
    reviewTitle: 'Review Title',
    associatedProject: 'Associated Project',
    notSet: 'Not Set',
    creator: 'Creator',
    useTemplate: 'Template',
    noTemplate: 'No Template',
    reviewStatus: 'Review Status',
    priority: 'Priority',
    deadline: 'Deadline',
    none: 'None',
    createdAt: 'Created At',
    reviewDescription: 'Review Description',

    // Progress Card
    reviewProgress: 'Review Progress',
    reviewers: 'Reviewers',
    completed: 'Completed',
    pendingReview: 'Pending',

    // Reviewers Card
    reviewersCard: 'Reviewers',
    reviewer: 'Reviewer',
    reviewerStatus: 'Review Status',
    reviewerComment: 'Review Comment',
    checklist: 'Checklist',
    notFilled: 'Not Filled',
    assignedAt: 'Assigned At',
    reviewedAt: 'Reviewed At',
    pendingReviewTime: 'Pending',

    // Assignment Status
    assignmentPending: 'Pending',
    assignmentApproved: 'Approved',
    assignmentRejected: 'Rejected',
    assignmentAbstained: 'Abstained',

    // Testcases Card
    reviewTestcases: 'Review Test Cases',
    testcaseTitle: 'Test Case Title',
    testType: 'Test Type',
    author: 'Author',
    view: 'View',
    comment: 'Comment',

    // Test Types
    testTypeFunctional: 'Functional Test',
    testTypeIntegration: 'Integration Test',
    testTypeApi: 'API Test',
    testTypeUi: 'UI Test',
    testTypePerformance: 'Performance Test',
    testTypeSecurity: 'Security Test',

    // Comments Card
    reviewComments: 'Review Comments',
    addComment: 'Add Comment',
    relatedTestcase: 'Related Test Case',
    noComments: 'No review comments',

    // Comment Types
    commentTypeGeneral: 'General Comment',
    commentTypeTestcase: 'Test Case Comment',
    commentTypeStep: 'Step Comment',

    // Submit Review Dialog
    submitReviewDialog: 'Submit Review',
    reviewResult: 'Review Result',
    approved: 'Approved',
    rejected: 'Rejected',
    abstained: 'Abstained',
    checklistTitle: 'Checklist',
    allPass: 'All Pass',
    allFail: 'All Fail',
    reviewCommentLabel: 'Review Comment',
    reviewCommentPlaceholder: 'Enter review comment',
    cancel: 'Cancel',
    submit: 'Submit',

    // Add Comment Dialog
    addCommentDialog: 'Add Review Comment',
    commentType: 'Comment Type',
    generalComment: 'General Comment',
    testcaseComment: 'Test Case Comment',
    relatedTestcaseLabel: 'Related Test Case',
    selectTestcase: 'Select test case',
    commentContent: 'Comment Content',
    commentContentPlaceholder: 'Enter comment content',

    // Checklist Stats
    checklistPass: 'Pass',
    checklistFail: 'Fail',
    checklistTotal: 'Total',

    // Messages
    fetchDetailFailed: 'Failed to fetch review detail',
    submitSuccess: 'Review submitted successfully',
    submitFailed: 'Failed to submit review',
    addCommentSuccess: 'Comment added successfully',
    addCommentFailed: 'Failed to add comment',
    commentRequired: 'Please enter comment content'
  },

  // Review Form Page
  reviewForm: {
    createTitle: 'Create Review',
    editTitle: 'Edit Review',
    back: 'Back',
    save: 'Save',

    // Form Fields
    reviewTitle: 'Review Title',
    reviewTitlePlaceholder: 'Enter review title',
    associatedProject: 'Associated Project',
    selectProject: 'Select project',
    priority: 'Priority',
    selectPriority: 'Select priority',
    priorityLow: 'Low',
    priorityMedium: 'Medium',
    priorityHigh: 'High',
    priorityUrgent: 'Urgent',
    deadline: 'Deadline',
    deadlinePlaceholder: 'Select deadline',
    description: 'Review Description',
    descriptionPlaceholder: 'Enter review description',

    // Testcase Selection
    selectTestcases: 'Select Test Cases',
    searchTestcases: 'Search test cases',
    selectTestcasesBtn: 'Select Test Cases',
    emptyTestcasesTip: 'Please select test cases for review',

    // Reviewers
    reviewers: 'Reviewers',
    selectReviewers: 'Select reviewers',

    // Template
    reviewTemplate: 'Review Template',
    selectTemplate: 'Select review template (optional)',

    // Testcase Selector Dialog
    testcaseSelectorTitle: 'Select Test Cases',
    testcaseTitle: 'Test Case Title',
    testType: 'Test Type',
    author: 'Author',
    confirm: 'Confirm',
    cancel: 'Cancel',

    // Validation
    titleRequired: 'Please enter review title',
    projectRequired: 'Please select project',
    testcasesRequired: 'Please select test cases for review',
    reviewersRequired: 'Please select reviewers',
    selectProjectFirst: 'Please select a project first',

    // Messages
    createSuccess: 'Review created successfully',
    updateSuccess: 'Review updated successfully',
    saveFailed: 'Failed to save',
    fetchProjectsFailed: 'Failed to fetch projects',
    fetchUsersFailed: 'Failed to fetch users',
    fetchTestcasesFailed: 'Failed to fetch test cases',
    fetchTemplatesFailed: 'Failed to fetch templates',
    fetchReviewFailed: 'Failed to fetch review data'
  },
  reviewTemplate: {
    title: 'Review Templates',
    createTemplate: 'Create Template',
    useTemplate: 'Use',
    edit: 'Edit',
    delete: 'Delete',

    // Filter
    project: 'Project',
    selectProject: 'Select Project',

    // Card labels
    projectLabel: 'Project:',
    creatorLabel: 'Creator:',
    createdAtLabel: 'Created At:',
    descriptionLabel: 'Description',
    checklistTitle: 'Checklist:',
    reviewersTitle: 'Default Reviewers:',

    // Empty states
    noDescription: 'No description',
    noChecklist: 'No checklist',
    noReviewers: 'No default reviewers',
    noData: 'No review templates',
    moreItems: '{count} more items...',

    // Dialog
    createTitle: 'Create Template',
    editTitle: 'Edit Template',
    templateName: 'Template Name',
    templateNamePlaceholder: 'Enter template name',
    associatedProject: 'Associated Project',
    templateDescription: 'Template Description',
    templateDescriptionPlaceholder: 'Enter template description',
    checklist: 'Checklist',
    checklistItemPlaceholder: 'Enter checklist item',
    addChecklistItem: 'Add Checklist Item',
    defaultReviewers: 'Default Reviewers',
    selectDefaultReviewers: 'Select default reviewers',
    save: 'Save',
    cancel: 'Cancel',

    // Validation
    nameRequired: 'Please enter template name',
    projectRequired: 'Please select project',

    // Messages
    deleteConfirm: 'Are you sure to delete this template?',
    deleteSuccess: 'Deleted successfully',
    deleteFailed: 'Failed to delete',
    createSuccess: 'Template created successfully',
    createFailed: 'Failed to create template',
    updateSuccess: 'Template updated successfully',
    updateFailed: 'Failed to update template',
    fetchListFailed: 'Failed to fetch template list',
    fetchProjectsFailed: 'Failed to fetch projects',
    fetchUsersFailed: 'Failed to fetch users'
  }
}
