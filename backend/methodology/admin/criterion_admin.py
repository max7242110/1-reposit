from __future__ import annotations

from django.contrib import admin, messages

from ..models import Criterion, MethodologyVersion


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
        "is_inverted", "is_lab", "show_note_on_site", "region_scope", "is_active",
    )
    list_filter = (MethodologyMultiFilter, "value_type", "scoring_type", "is_lab", "region_scope", "is_active")
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
                "note", "show_note_on_site",
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
