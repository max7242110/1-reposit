from __future__ import annotations

from django.contrib import admin, messages

from ..models import Criterion


@admin.register(Criterion)
class CriterionAdmin(admin.ModelAdmin):
    list_display = (
        "code", "name_ru", "methodology", "value_type", "scoring_type", "weight",
        "is_inverted", "is_lab", "region_scope", "is_active",
    )
    list_filter = ("methodology", "value_type", "scoring_type", "is_lab", "region_scope", "is_active")
    search_fields = ("code", "name_ru", "name_en")
    list_select_related = ("methodology",)
    list_per_page = 50
    ordering = ("display_order",)
    fieldsets = (
        ("Основное", {
            "fields": ("methodology", "code", "name_ru", "name_en", "name_de", "name_pt", "unit"),
        }),
        ("Описание", {
            "classes": ("collapse",),
            "fields": ("description_ru", "description_en", "description_de", "description_pt"),
        }),
        ("Скоринг", {
            "fields": (
                "value_type", "scoring_type", "weight",
                "min_value", "median_value", "max_value",
                "is_inverted", "median_by_capacity",
                "custom_scale_json", "formula_json",
            ),
        }),
        ("Режимы и обязательность", {
            "fields": (
                "is_lab", "is_required_lab", "is_required_checklist", "is_required_catalog",
                "use_in_lab", "use_in_checklist", "use_in_catalog",
            ),
        }),
        ("Отображение", {
            "fields": ("region_scope", "is_public", "display_order", "is_active"),
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        methodology = obj.methodology
        if not methodology.needs_recalculation:
            methodology.needs_recalculation = True
            methodology.save(update_fields=["needs_recalculation", "updated_at"])
            messages.info(request, "Методика отмечена для пересчёта.")
