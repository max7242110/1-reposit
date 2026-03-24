from __future__ import annotations

from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, QuerySet, Sum
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _

from catalog.services import migrate_model_raw_values_between_methodologies
from .inlines import CriterionInline
from ..forms import DuplicateMethodologyVersionForm
from ..models import Criterion, MethodologyVersion
from ..services import (
    backfill_criterion_extras_from_methodology,
    duplicate_methodology_version,
)
from scoring.engine import refresh_all_ac_model_total_indices


@admin.register(MethodologyVersion)
class MethodologyVersionAdmin(admin.ModelAdmin):
    change_form_template = "admin/methodology/methodologyversion/change_form.html"
    duplicate_form_template = "admin/methodology/methodologyversion/duplicate_form.html"
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

    def get_urls(self):
        info = self.opts.app_label, self.opts.model_name
        return [
            path(
                "<path:object_id>/duplicate/",
                self.admin_site.admin_view(self.duplicate_view),
                name="%s_%s_duplicate" % info,
            ),
        ] + super().get_urls()

    def duplicate_view(self, request, object_id):
        source = self.get_object(request, object_id)
        if source is None:
            raise Http404
        if not self.has_change_permission(request, source):
            raise PermissionDenied
        opts = self.model._meta
        if request.method == "POST":
            form = DuplicateMethodologyVersionForm(request.POST)
            if form.is_valid():
                try:
                    new_mv = duplicate_methodology_version(
                        source,
                        version=form.cleaned_data["version"],
                        name=form.cleaned_data["name"],
                        description=(form.cleaned_data["description"] or "").strip() or None,
                    )
                except ValueError as e:
                    form.add_error("version", str(e))
                else:
                    messages.success(request, _("Создана копия методики."))
                    return HttpResponseRedirect(
                        reverse(
                            f"admin:{opts.app_label}_{opts.model_name}_change",
                            args=[new_mv.pk],
                        )
                    )
        else:
            form = DuplicateMethodologyVersionForm(
                initial={
                    "version": f"{source.version}-copy",
                    "name": f"Копия: {source.name}",
                    "description": source.description,
                },
            )
        context = {
            **self.admin_site.each_context(request),
            "opts": opts,
            "form": form,
            "source": source,
            "title": _("Дублирование методики"),
        }
        return TemplateResponse(request, self.duplicate_form_template, context)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}
        total = 0.0
        if object_id:
            obj = self.get_object(request, object_id)
            if obj is not None:
                agg = obj.criteria.aggregate(s=Sum("weight"))
                total = float(agg["s"] or 0)
                if self.has_change_permission(request, obj):
                    meta = self.model._meta
                    extra_context["duplicate_url"] = reverse(
                        f"admin:{meta.app_label}_{meta.model_name}_duplicate",
                        args=[object_id],
                    )
        extra_context["criteria_weight_total_initial"] = round(total, 2)
        return super().changeform_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        previous_active = MethodologyVersion.objects.filter(is_active=True).exclude(pk=obj.pk).first()
        request._previous_active_methodology_pk = previous_active.pk if previous_active is not None else None
        if not change:
            active_before = MethodologyVersion.objects.filter(is_active=True).first()
            request._methodology_backfill_template_pk = (
                active_before.pk if active_before is not None else None
            )
        super().save_model(request, obj, form, change)
        if obj.needs_recalculation and not obj.is_active:
            messages.warning(
                request,
                "Внимание: методика изменена, требуется пересчёт рейтинга! "
                "Перейдите в раздел «Расчёты» для запуска.",
            )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if form.instance.pk and form.instance.is_active:
            moved = migrate_model_raw_values_between_methodologies(
                source_methodology_id=getattr(request, "_previous_active_methodology_pk", None),
                target_methodology_id=form.instance.pk,
            )
            if moved:
                messages.info(
                    request,
                    _("Скопированы значения критериев в новую методику: %(n)s.") % {"n": moved},
                )
            n = refresh_all_ac_model_total_indices()
            if n:
                messages.success(
                    request,
                    _("Итоговый индекс в каталоге обновлён для %(n)s моделей.") % {"n": n},
                )

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            instance.save()
        formset.save_m2m()
        if (
            not change
            and formset.model is Criterion
            and form.instance.pk
        ):
            tpl_pk = getattr(request, "_methodology_backfill_template_pk", None)
            for c in form.instance.criteria.all():
                backfill_criterion_extras_from_methodology(c, tpl_pk)
