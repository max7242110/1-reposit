from django.contrib import admin

from .audit import AuditLog
from .models import Page


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("changed_at", "action", "entity_type", "entity_id", "field_name", "changed_by")
    list_filter = ("action", "entity_type", "changed_by")
    search_fields = ("entity_type", "field_name", "old_value", "new_value", "comment")
    date_hierarchy = "changed_at"
    readonly_fields = (
        "entity_type", "entity_id", "action", "field_name",
        "old_value", "new_value", "changed_by", "changed_at", "comment",
    )
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "slug", "is_active", "updated_at")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("title_ru",)}
    search_fields = ("title_ru", "slug")
