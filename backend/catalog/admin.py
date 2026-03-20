from __future__ import annotations

import logging
from django import forms
from django.contrib import admin, messages
from django.forms import BaseInlineFormSet
from django.http import HttpRequest
from django.utils.safestring import mark_safe

from methodology.models import Criterion, MethodologyVersion
from scoring.engine import WeightValidationError, recalculate_all

from .models import ACModel, EquipmentType, ModelRawValue, ModelRegion

logger = logging.getLogger(__name__)

MAX_DATALIST_OPTIONS = 120


# ── Helpers ───────────────────────────────────────────────────────────

def _ensure_all_criteria(ac_model: ACModel) -> int:
    """Create empty ModelRawValue for every active criterion not yet present."""
    methodology = MethodologyVersion.objects.filter(is_active=True).first()
    if not methodology:
        return 0

    existing_ids = set(
        ModelRawValue.objects.filter(model=ac_model)
        .values_list("criterion_id", flat=True)
    )
    missing = Criterion.objects.filter(
        methodology=methodology, is_active=True,
    ).exclude(pk__in=existing_ids)

    to_create = [
        ModelRawValue(model=ac_model, criterion=c)
        for c in missing
    ]
    if to_create:
        ModelRawValue.objects.bulk_create(to_create)
    return len(to_create)


def _numeric_step(mn: float, mx: float) -> float:
    """Pick a sensible step so we get ~20-80 options."""
    rng = mx - mn
    if rng < 1:
        return 0.01
    if rng < 5:
        return 0.05
    if rng < 50:
        return 0.5
    return 1.0


def _format_number(val: float) -> str:
    """Format a number without trailing zeros, but keep one decimal."""
    if val == int(val):
        return str(int(val))
    txt = f"{val:.4f}".rstrip("0").rstrip(".")
    return txt


def _build_options(criterion: Criterion) -> list[str]:
    """Build datalist options for any criterion type."""
    if criterion.value_type == Criterion.ValueType.BINARY:
        return ["да", "нет"]

    if criterion.value_type == Criterion.ValueType.BRAND_AGE:
        return [str(y) for y in range(1995, 2027)]

    if criterion.value_type == Criterion.ValueType.FALLBACK:
        return [str(v) for v in range(500, 5100, 100)]

    scale = criterion.custom_scale_json
    if isinstance(scale, dict) and scale:
        seen: set[str] = set()
        opts: list[str] = []
        for key in scale:
            label = str(key).strip()
            if label.lower() not in seen:
                seen.add(label.lower())
                opts.append(label)
        return opts

    mn = criterion.min_value
    mx = criterion.max_value
    if mn is not None and mx is not None and mx > mn:
        step = _numeric_step(mn, mx)
        count = int((mx - mn) / step) + 1
        if count > MAX_DATALIST_OPTIONS:
            step = (mx - mn) / MAX_DATALIST_OPTIONS
        opts = []
        val = mn
        while val <= mx + step * 0.01:
            opts.append(_format_number(round(val, 4)))
            val += step
            if len(opts) > MAX_DATALIST_OPTIONS:
                break
        return opts

    return []


def _build_hint(criterion: Criterion) -> str:
    """Build help_text hint for the field."""
    parts: list[str] = []

    if criterion.unit:
        parts.append(criterion.unit)

    if criterion.min_value is not None and criterion.max_value is not None:
        inv = " ↓инв." if criterion.is_inverted else ""
        parts.append(f"{criterion.min_value}–{criterion.max_value}{inv}")

    if criterion.median_value is not None:
        parts.append(f"мед. {criterion.median_value}")

    if criterion.value_type == Criterion.ValueType.BRAND_AGE:
        parts.append("авто по году бренда")

    if criterion.value_type == Criterion.ValueType.FALLBACK:
        parts.append("Вт компрессора, fallback по бренду")

    return " | ".join(parts)


# ── Datalist widget ───────────────────────────────────────────────────

class DatalistTextInput(forms.TextInput):
    """<input> + <datalist> combo: dropdown suggestions + free text."""

    def __init__(self, datalist_options: list[str], attrs=None):
        self.datalist_options = datalist_options
        super().__init__(attrs=attrs)

    def render(self, name, value, attrs=None, renderer=None):
        dl_id = f"dl_{name}"
        attrs = attrs or {}
        attrs["list"] = dl_id
        attrs.setdefault("style", "width:180px;")

        input_html = super().render(name, value, attrs, renderer)

        options_html = "".join(
            f'<option value="{opt}">' for opt in self.datalist_options
        )
        datalist_html = f'<datalist id="{dl_id}">{options_html}</datalist>'

        return mark_safe(input_html + datalist_html)


# ── Custom formset ────────────────────────────────────────────────────

class RawValueFormSet(BaseInlineFormSet):
    """Customize raw_value widget per-row based on criterion type."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        criteria_cache: dict[int, Criterion] = {}
        criterion_ids = {
            f.instance.criterion_id
            for f in self.forms
            if f.instance and f.instance.criterion_id
        }
        if criterion_ids:
            criteria_cache = {
                c.pk: c
                for c in Criterion.objects.filter(pk__in=criterion_ids)
            }

        for form in self.forms:
            inst = form.instance
            if not inst or not inst.criterion_id:
                continue

            criterion = criteria_cache.get(inst.criterion_id)
            if not criterion:
                continue

            options = _build_options(criterion)
            hint = _build_hint(criterion)

            if options:
                form.fields["raw_value"].widget = DatalistTextInput(
                    datalist_options=options,
                )
            if hint:
                form.fields["raw_value"].help_text = hint


# ── Inlines ───────────────────────────────────────────────────────────

class ModelRegionInline(admin.TabularInline):
    model = ModelRegion
    extra = 0


class ModelRawValueInline(admin.TabularInline):
    model = ModelRawValue
    formset = RawValueFormSet
    extra = 0
    fields = ("criterion", "raw_value", "verification_status", "source")
    readonly_fields = ("criterion",)
    ordering = ("criterion__display_order",)
    can_delete = False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("criterion")

    def has_add_permission(self, request, obj=None):
        return False


# ── Main admin ────────────────────────────────────────────────────────

@admin.register(ACModel)
class ACModelAdmin(admin.ModelAdmin):
    list_display = (
        "brand", "inner_unit", "series", "nominal_capacity",
        "total_index", "publish_status",
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
        ("Основное", {
            "fields": (
                "brand", "series", "inner_unit", "outer_unit",
                "nominal_capacity", "equipment_type",
            ),
        }),
        ("Публикация", {
            "fields": ("publish_status", "total_index"),
        }),
        ("Видео", {
            "classes": ("collapse",),
            "fields": ("youtube_url", "rutube_url", "vk_url"),
        }),
        ("Даты", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at"),
        }),
    )

    def change_view(self, request: HttpRequest, object_id, form_url="", extra_context=None):
        ac_model = self.get_object(request, object_id)
        if ac_model:
            _ensure_all_criteria(ac_model)
        return super().change_view(request, object_id, form_url, extra_context)

    @admin.action(description="Пересчитать индекс для выбранных моделей")
    def recalculate_selected(self, request, queryset):
        ids = list(queryset.values_list("pk", flat=True))
        try:
            run = recalculate_all(model_ids=ids, user=request.user)
            messages.success(
                request,
                f"Расчёт #{run.pk} завершён: {run.models_processed} моделей пересчитано.",
            )
        except WeightValidationError as e:
            messages.error(request, f"Ошибка валидации весов: {e}")
        except ValueError as e:
            messages.error(request, f"Ошибка пересчёта: {e}")

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            if isinstance(obj, ModelRawValue) and not obj.entered_by_id:
                obj.entered_by = request.user
            obj.save()
        for obj in formset.deleted_objects:
            obj.delete()
        formset.save_m2m()

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            _ensure_all_criteria(obj)


@admin.register(EquipmentType)
class EquipmentTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
