from __future__ import annotations

from django.contrib import admin, messages
from django.db.models import Count, Q, QuerySet, Sum

from .models import Criterion, MethodologyVersion

MAX_TOTAL_WEIGHT = 100.0


def _cap_criterion_weight(criterion: Criterion, request) -> None:
    """Ensure total methodology weight does not exceed 100%.

    Calculates the sum of weights of all *other* active criteria in the same
    methodology.  If adding this criterion's weight would push the total above
    100%, the weight is automatically reduced (down to 0%) and an error message
    is shown.
    """
    others_sum = (
        Criterion.objects.filter(
            methodology=criterion.methodology,
            is_active=True,
        )
        .exclude(pk=criterion.pk)
        .aggregate(s=Sum("weight"))["s"]
    ) or 0.0

    available = max(0.0, MAX_TOTAL_WEIGHT - others_sum)

    if criterion.weight > available:
        original = criterion.weight
        criterion.weight = round(available, 2)
        criterion.save(update_fields=["weight"])
        messages.error(
            request,
            f"Сумма весов не может превышать {MAX_TOTAL_WEIGHT:.0f}%! "
            f"Вес критерия «{criterion.code}» автоматически уменьшен "
            f"с {original:.2f}% до {criterion.weight:.2f}% "
            f"(доступно: {available:.2f}%, занято другими: {others_sum:.2f}%).",
        )


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
    list_display = ("name", "version", "is_active", "criteria_count", "weight_sum", "needs_recalculation", "created_at")
    list_filter = ("is_active", "needs_recalculation")
    search_fields = ("name", "version")
    inlines = [CriterionInline]
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request) -> QuerySet:
        return super().get_queryset(request).annotate(
            _criteria_count=Count("criteria", filter=Q(criteria__is_active=True)),
            _weight_sum=Sum("criteria__weight", filter=Q(criteria__is_active=True)),
        )

    @admin.display(description="Критериев")
    def criteria_count(self, obj) -> int:
        return getattr(obj, "_criteria_count", 0)

    @admin.display(description="Сумма весов")
    def weight_sum(self, obj) -> str:
        total = getattr(obj, "_weight_sum", None) or 0
        return f"{total:.1f}%"

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

        methodology = form.instance
        total = (
            Criterion.objects.filter(methodology=methodology, is_active=True)
            .aggregate(s=Sum("weight"))["s"]
        ) or 0.0

        if total > MAX_TOTAL_WEIGHT:
            over = total - MAX_TOTAL_WEIGHT
            criteria = list(
                Criterion.objects.filter(methodology=methodology, is_active=True)
                .order_by("-display_order")
            )
            remaining_over = over
            for c in criteria:
                if remaining_over <= 0:
                    break
                reduction = min(c.weight, remaining_over)
                c.weight = round(c.weight - reduction, 2)
                c.save(update_fields=["weight"])
                remaining_over = round(remaining_over - reduction, 2)

            messages.error(
                request,
                f"Сумма весов превысила {MAX_TOTAL_WEIGHT:.0f}% на {over:.2f}%! "
                f"Веса последних критериев автоматически уменьшены.",
            )


@admin.register(Criterion)
class CriterionAdmin(admin.ModelAdmin):
    list_display = (
        "code", "name_ru", "methodology", "value_type", "scoring_type",
        "weight", "is_inverted", "is_lab", "region_scope", "is_active",
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
        _cap_criterion_weight(obj, request)
        methodology = obj.methodology
        if not methodology.needs_recalculation:
            methodology.needs_recalculation = True
            methodology.save(update_fields=["needs_recalculation", "updated_at"])
            messages.info(request, "Методика отмечена для пересчёта.")
