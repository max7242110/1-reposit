from __future__ import annotations

from django.contrib import admin, messages
from django.db.models import Count, Q, QuerySet, Sum

from .models import Criterion, MethodologyVersion


class CriterionInline(admin.TabularInline):
    model = Criterion
    fk_name = "methodology"
    extra = 0
    fields = (
        "code", "name_ru", "value_type", "scoring_type", "weight",
        "is_lab", "region_scope", "is_public", "is_active", "display_order",
    )
    ordering = ("display_order",)


@admin.register(MethodologyVersion)
class MethodologyVersionAdmin(admin.ModelAdmin):
    change_form_template = "admin/methodology/methodologyversion/change_form.html"
    list_display = (
        "name",
        "version",
        "is_active",
        "criteria_count",
        "weight_sum",
        "needs_recalculation",
        "created_at",
    )
    list_filter = ("is_active", "needs_recalculation")
    search_fields = ("name", "version")
    inlines = [CriterionInline]
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request) -> QuerySet:
        return super().get_queryset(request).annotate(
            _criteria_count=Count("criteria", filter=Q(criteria__is_active=True)),
            _weight_sum=Sum("criteria__weight"),
        )

    @admin.display(description="Критериев")
    def criteria_count(self, obj) -> int:
        return getattr(obj, "_criteria_count", 0)

    @admin.display(description="Σ весов, %")
    def weight_sum(self, obj) -> str:
        total = getattr(obj, "_weight_sum", None)
        if total is None:
            return "0.00%"
        return f"{float(total):.2f}%"

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}
        total = 0.0
        if object_id:
            obj = self.get_object(request, object_id)
            if obj is not None:
                agg = obj.criteria.aggregate(s=Sum("weight"))
                total = float(agg["s"] or 0)
        extra_context["criteria_weight_total_initial"] = round(total, 2)
        return super().changeform_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.needs_recalculation:
            messages.warning(
                request,
                "Внимание: методика изменена, требуется пересчёт рейтинга! "
                "Перейдите в раздел «Расчёты» для запуска.",
            )

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            instance.save()
        formset.save_m2m()


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
