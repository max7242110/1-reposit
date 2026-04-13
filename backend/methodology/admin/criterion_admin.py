from __future__ import annotations

from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db.models import Sum

from ..models import Criterion, MethodologyVersion

INVERSION_BLOCKED_SCORING_TYPES = {
    "custom_scale", "universal_scale", "formula", "interval",
}

INVERSION_BLOCKED_VALUE_TYPES = {
    "brand_age", "fallback",
}


class MethodologyMultiFilter(admin.SimpleListFilter):
    title = "Методики"
    parameter_name = "methodology__id__in"
    template = "admin/methodology/filters/methodology_multiselect_filter.html"

    def lookups(self, request, model_admin):
        qs = MethodologyVersion.objects.order_by("-created_at").only("id", "name", "version")
        return [(str(m.pk), f"{m.name} (v{m.version})") for m in qs]

    def _selected_ids(self) -> set[str]:
        raw = self.value() or ""
        return {x.strip() for x in raw.split(",") if x.strip()}

    def queryset(self, request, queryset):
        selected = self._selected_ids()
        if not selected:
            return queryset
        valid_int_ids = [int(x) for x in selected if x.isdigit()]
        if not valid_int_ids:
            return queryset.none()
        return queryset.filter(methodology_id__in=valid_int_ids)

    def choices(self, changelist):
        selected = self._selected_ids()
        for lookup, title in self.lookup_choices:
            lookup_s = str(lookup)
            yield {
                "lookup": lookup_s,
                "title": title,
                "selected": lookup_s in selected,
            }


@admin.register(Criterion)
class CriterionAdmin(admin.ModelAdmin):
    list_display = (
        "code", "name_ru", "methodology", "value_type", "scoring_type", "weight",
        "is_inverted", "region_scope", "is_active",
    )
    list_filter = (MethodologyMultiFilter, "value_type", "scoring_type", "region_scope", "is_active")
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
            "fields": (
                "description_ru", "description_en", "description_de", "description_pt",
                "note",
            ),
        }),
        ("Скоринг", {
            "fields": (
                "value_type", "scoring_type", "weight",
                "min_value", "median_value", "max_value",
                "is_inverted", "median_by_capacity",
                "custom_scale_json", "formula_json",
            ),
        }),
        ("Отображение", {
            "fields": ("region_scope", "is_public", "display_order", "is_active"),
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.is_inverted and (obj.scoring_type in INVERSION_BLOCKED_SCORING_TYPES or obj.value_type in INVERSION_BLOCKED_VALUE_TYPES):
            raise ValidationError(
                f"Флаг is_inverted нельзя использовать с типом скоринга «{obj.scoring_type}». "
                "Для этого типа направление шкалы задаётся в самих данных (custom_scale_json / formula_json)."
            )
        super().save_model(request, obj, form, change)
        methodology = obj.methodology
        if not methodology.needs_recalculation:
            methodology.needs_recalculation = True
            methodology.save(update_fields=["needs_recalculation", "updated_at"])
            messages.info(request, "Методика отмечена для пересчёта.")
        total = (
            Criterion.objects.filter(methodology=methodology, is_active=True)
            .aggregate(s=Sum("weight"))["s"]
            or 0
        )
        if abs(total - 100) > 0.01:
            self.message_user(
                request,
                f"⚠️ Сумма весов активных параметров = {total:.2f}%. Должно быть ровно 100%.",
                level=messages.WARNING,
            )
