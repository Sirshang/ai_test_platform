from django.contrib import admin

from apps.projects.models import Project, ProjectMember


class ProjectMemberInline(admin.TabularInline):
    model = ProjectMember
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at", "updated_at")
    search_fields = ("name", "description")
    inlines = [ProjectMemberInline]


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ("project", "user", "created_at")
    list_filter = ("project",)
