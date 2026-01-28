from django.contrib import admin
from .models import (
    ApiProject, ApiCollection, ApiRequest, Environment, RequestHistory,
    TestSuite, TestExecution, ScheduledTask, TaskExecutionLog, AIServiceConfig
)


@admin.register(ApiProject)
class ApiProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'project_type', 'status', 'owner', 'start_date', 'end_date', 'created_at']
    list_filter = ['project_type', 'status', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['members']


@admin.register(ApiCollection)
class ApiCollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'parent', 'order', 'created_at']
    list_filter = ['project', 'created_at']
    search_fields = ['name', 'description']


@admin.register(ApiRequest)
class ApiRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'method', 'request_type', 'collection', 'created_by', 'created_at']
    list_filter = ['method', 'request_type', 'created_at']
    search_fields = ['name', 'url']


@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'scope', 'project', 'is_active', 'created_by', 'created_at']
    list_filter = ['scope', 'is_active', 'created_at']
    search_fields = ['name']


@admin.register(RequestHistory)
class RequestHistoryAdmin(admin.ModelAdmin):
    list_display = ['request', 'status_code', 'response_time', 'executed_by', 'executed_at']
    list_filter = ['status_code', 'executed_at']
    search_fields = ['request__name']


@admin.register(TestSuite)
class TestSuiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'environment', 'created_by', 'created_at']
    list_filter = ['project', 'created_at']
    search_fields = ['name', 'description']


@admin.register(TestExecution)
class TestExecutionAdmin(admin.ModelAdmin):
    list_display = ['test_suite', 'status', 'total_requests', 'passed_requests', 'failed_requests', 'executed_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['test_suite__name']


@admin.register(ScheduledTask)
class ScheduledTaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'task_type', 'trigger_type', 'status', 'total_runs', 'successful_runs', 'failed_runs', 'created_by', 'created_at']
    list_filter = ['task_type', 'trigger_type', 'status', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['last_run_time', 'next_run_time', 'total_runs', 'successful_runs', 'failed_runs', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        """根据用户权限过滤任务"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)


@admin.register(TaskExecutionLog)
class TaskExecutionLogAdmin(admin.ModelAdmin):
    list_display = ['task', 'status', 'start_time', 'end_time', 'duration', 'executed_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['task__name']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        """根据用户权限过滤日志"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(task__created_by=request.user)


@admin.register(AIServiceConfig)
class AIServiceConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'service_type', 'role', 'model_name', 'is_active', 'created_by', 'created_at']
    list_filter = ['service_type', 'role', 'is_active', 'created_at']
    search_fields = ['name', 'model_name']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        """根据用户权限过滤配置"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)
