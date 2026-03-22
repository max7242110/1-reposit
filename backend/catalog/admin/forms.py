"""Формы и formset для админки каталога."""

from __future__ import annotations

from django import forms
from django.forms import BaseInlineFormSet
from django.urls import reverse
from django.utils.safestring import mark_safe

from methodology.models import Criterion

from catalog.models import ACModel

from .datalist import DatalistTextInput, build_hint, build_options, format_number


class RawValueFormSet(BaseInlineFormSet):
    """Настройка виджета raw_value по типу критерия."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        criterion_ids = {
            f.instance.criterion_id
            for f in self.forms
            if f.instance and f.instance.criterion_id
        }
        criteria_cache: dict[int, Criterion] = {}
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

            if criterion.value_type == Criterion.ValueType.BRAND_AGE:
                brand = inst.model.brand
                year = brand.sales_start_year_ru
                form.initial["raw_value"] = str(year) if year is not None else ""
                form.fields["raw_value"].widget.attrs["readonly"] = "readonly"
                form.fields["raw_value"].widget.attrs["style"] = (
                    "width:180px;background:#f4f4f4;cursor:not-allowed;"
                )
                url = reverse("admin:brands_brand_change", args=[brand.pk])
                form.fields["raw_value"].help_text = mark_safe(
                    "Автоматически из поля «Год начала продаж в РФ» в "
                    f'<a href="{url}" target="_blank" rel="noopener">справочнике брендов</a>.'
                )
                continue

            options = build_options(criterion)
            hint = build_hint(criterion)

            if options:
                form.fields["raw_value"].widget = DatalistTextInput(
                    datalist_options=options,
                )
            if hint:
                form.fields["raw_value"].help_text = hint


_CAPACITY_OPTIONS = [format_number(round(2.0 + i * 0.05, 2)) for i in range(41)]


class ACModelForm(forms.ModelForm):
    class Meta:
        model = ACModel
        fields = "__all__"
        widgets = {
            "nominal_capacity": DatalistTextInput(
                datalist_options=_CAPACITY_OPTIONS,
                attrs={"style": "width:200px;"},
            ),
        }
