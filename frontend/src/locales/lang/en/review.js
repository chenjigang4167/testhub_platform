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
