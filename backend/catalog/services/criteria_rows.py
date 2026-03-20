"""Создание строк ModelRawValue под все активные критерии методики."""

from __future__ import annotations

from methodology.models import Criterion, MethodologyVersion

from catalog.models import ACModel, ModelRawValue


def ensure_all_criteria_rows(ac_model: ACModel) -> int:
    """Создать пустые ModelRawValue для каждого активного критерия, если строки ещё нет."""
    methodology = MethodologyVersion.objects.filter(is_active=True).first()
    if not methodology:
        return 0

    existing_ids = set(
        ModelRawValue.objects.filter(model=ac_model).values_list(
            "criterion_id", flat=True,
        )
    )
    missing = Criterion.objects.filter(
        methodology=methodology, is_active=True,
    ).exclude(pk__in=existing_ids)

    to_create = [ModelRawValue(model=ac_model, criterion=c) for c in missing]
    if to_create:
        ModelRawValue.objects.bulk_create(to_create)
    return len(to_create)
