from django.contrib import admin
from .models import RequirementDocument, RequirementAnalysis, BusinessRequirement, GeneratedTestCase, AnalysisTask


@admin.register(RequirementDocument)
class RequirementDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'document_type', 'status', 'uploaded_by', 'created_at']
    list_filter = ['document_type', 'status', 'created_at']
    search_fields = ['title', 'uploaded_by__username']
    readonly_fields = ['file_size', 'extracted_text', 'created_at', 'updated_at']


@admin.register(RequirementAnalysis)
class RequirementAnalysisAdmin(admin.ModelAdmin):
    list_display = ['document', 'requirements_count', 'analysis_time', 'created_at']
    list_filter = ['created_at']
    search_fields = ['document__title']
    readonly_fields = ['analysis_time', 'created_at', 'updated_at']


@admin.register(BusinessRequirement)
class BusinessRequirementAdmin(admin.ModelAdmin):
    list_display = ['requirement_id', 'requirement_name', 'requirement_type', 'requirement_level', 'module']
    list_filter = ['requirement_type', 'requirement_level', 'module', 'created_at']
    search_fields = ['requirement_id', 'requirement_name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(GeneratedTestCase)
class GeneratedTestCaseAdmin(admin.ModelAdmin):
    list_display = ['case_id', 'title', 'priority', 'status', 'generated_by_ai', 'reviewed_by_ai']
    list_filter = ['priority', 'status', 'generated_by_ai', 'reviewed_by_ai', 'created_at']
    search_fields = ['case_id', 'title', 'requirement__requirement_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AnalysisTask)
class AnalysisTaskAdmin(admin.ModelAdmin):
    list_display = ['task_id', 'task_type', 'status', 'progress', 'created_at']
    list_filter = ['task_type', 'status', 'created_at']
    search_fields = ['task_id', 'document__title']
    readonly_fields = ['task_id', 'started_at', 'completed_at', 'created_at']