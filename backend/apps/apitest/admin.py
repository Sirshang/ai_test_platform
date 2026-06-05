from django.contrib import admin

from apps.apitest.models import ApiEnvironment, ApiTestCase


@admin.register(ApiEnvironment)
class ApiEnvironmentAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "base_url", "created_at")
    list_filter = ("project",)
    search_fields = ("name", "base_url")


@admin.register(ApiTestCase)
class ApiTestCaseAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "method", "path", "status", "last_run_status")
    list_filter = ("project", "status", "method")
    search_fields = ("title", "path", "description")
