from django.contrib import admin

from apps.tasks.models import Category, Task, TaskShare


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "created_at"]
    list_filter = ["owner"]
    search_fields = ["name", "owner__email"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "owner", "category", "priority", "is_completed", "due_date", "created_at"]
    list_filter = ["is_completed", "priority", "category"]
    search_fields = ["title", "description", "owner__email"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(TaskShare)
class TaskShareAdmin(admin.ModelAdmin):
    list_display = ["task", "shared_with", "created_at"]
    search_fields = ["task__title", "shared_with__email"]
    readonly_fields = ["id", "created_at"]
