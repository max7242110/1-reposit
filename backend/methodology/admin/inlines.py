from __future__ import annotations

from django.contrib import admin

from ..models import Criterion
from ..services import template_criteria_inline_initial


class CriterionInline(admin.TabularInline):
    model = Criterion
    fk_name = "methodology"
    extra = 0
    fields = (
        "code", "name_ru", "value_type", "scoring_type", "weight",
        "note", "show_note_on_site", "is_lab", "region_scope", "is_public", "is_active", "display_order",
    )
    ordering = ("display_order",)

    def get_extra(self, request, obj=None, **kwargs):
        if getattr(obj, "pk", None):
            return 0
        return len(template_criteria_inline_initial())

    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super().get_formset(request, obj, **kwargs)
        if getattr(obj, "pk", None):
            return FormSet
        rows = template_criteria_inline_initial()
        if not rows:
            return FormSet

        rows_closure = rows

        class PrefilledCriterionFormSet(FormSet):
            def __init__(self, *args, **inner_kw):
                super().__init__(*args, **inner_kw)
                if self.instance.pk is None and not self.is_bound:
                    for i, row in enumerate(rows_closure):
                        if i < len(self.forms):
                            for key, val in row.items():
                                if key in self.forms[i].fields:
                                    self.forms[i].initial[key] = val

        return PrefilledCriterionFormSet
