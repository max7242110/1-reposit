"""Админка моделей кондиционеров."""

from __future__ import annotations

from django.contrib import admin, messages
from django.http import HttpRequest

from methodology.models import MethodologyVersion
from scoring.engine import update_model_total_index

from catalog.models import ACModel, ModelRawValue
from catalog.services import ensure_all_criteria_rows
from catalog.sync_brand_age import sync_brand_age_for_model

from .forms import ACModelForm
from .inlines import ModelRawValueInline, ModelRegionInline


@admin.register(ACModel)
class ACModelAdmin(admin.ModelAdmin):
    form = ACModelForm
    list_display = (
        "brand",
        "inner_unit",
        "series",
        "nominal_capacity",
        "total_index",
        "publish_status",
    )
    list_filter = ("publish_status", "brand", "equipment_type")
    list_select_related = ("brand", "equipment_type")
    search_fields = ("inner_unit", "outer_unit", "brand__name", "series")
    list_per_page = 30
    ordering = ("-total_index",)
    inlines = [ModelRegionInline, ModelRawValueInline]
    readonly_fields = ("total_index", "created_at", "updated_at")
    actions = ["recalculate_selected"]

    fieldsets = (
        (
            "Основное",
            {
                "fields": (
                    "brand",
                    "series",
                    "inner_unit",
                    "outer_unit",
                    "nominal_capacity",
                    "equipment_type",
                ),
            },
        ),
        ("Публикация", {"fields": ("publish_status", "total_index")}),
        (
            "Видео",
            {"classes": ("collapse",), "fields": ("youtube_url", "rutube_url", "vk_url")},
        ),
        (
            "Даты",
            {"classes": ("collapse",), "fields": ("created_at", "updated_at")},
        ),
    )

    def change_view(self, request: HttpRequest, object_id, form_url="", extra_context=None):
        ac_model = self.get_object(request, object_id)
        if ac_model:
            ensure_all_criteria_rows(ac_model)
            sync_brand_age_for_model(ac_model)
        return super().change_view(request, object_id, form_url, extra_context)

    @admin.action(description="Пересчитать индекс для выбранных моделей")
    def recalculate_selected(self, request, queryset):
        methodology = MethodologyVersion.objects.filter(is_active=True).first()
        if methodology is None:
            messages.error(request, "Нет активной методики.")
            return
        n = 0
        for obj in queryset.select_related("brand", "brand__origin_class"):
            if update_model_total_index(obj):
                n += 1
        messages.success(request, f"Индекс пересчитан для моделей: {n}.")

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            if isinstance(obj, ModelRawValue) and not obj.entered_by_id:
                obj.entered_by = request.user
            obj.save()
        for obj in formset.deleted_objects:
            obj.delete()
        formset.save_m2m()

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        instance = form.instance
        sync_brand_age_for_model(instance)
        update_model_total_index(instance)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            ensure_all_criteria_rows(obj)
        sync_brand_age_for_model(obj)
