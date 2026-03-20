"""Sync ModelRawValue for brand_age criteria from Brand.sales_start_year_ru."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import QuerySet

from catalog.models import ACModel, ModelRawValue
from methodology.models import Criterion, MethodologyVersion

if TYPE_CHECKING:
    from brands.models import Brand


def active_brand_age_criteria() -> QuerySet[Criterion]:
    methodology = MethodologyVersion.objects.filter(is_active=True).first()
    if methodology is None:
        return Criterion.objects.none()
    return Criterion.objects.filter(
        methodology=methodology,
        is_active=True,
        value_type=Criterion.ValueType.BRAND_AGE,
    )


def _year_raw_value(brand: "Brand") -> str:
    y = brand.sales_start_year_ru
    return str(y) if y is not None else ""


def sync_brand_age_for_model(ac_model: ACModel) -> int:
    """
    Set raw_value for all brand_age criteria on this model from the linked Brand.
    Returns number of ModelRawValue rows updated or created.
    """
    criteria = active_brand_age_criteria()
    if not criteria.exists():
        return 0

    val = _year_raw_value(ac_model.brand)
    n = 0
    for crit in criteria:
        updated = ModelRawValue.objects.filter(
            model=ac_model, criterion=crit,
        ).update(raw_value=val)
        if updated:
            n += updated
        else:
            ModelRawValue.objects.create(
                model=ac_model, criterion=crit, raw_value=val,
            )
            n += 1
    return n


def sync_brand_age_for_brand(brand: "Brand") -> int:
    """
    Update raw_value for all models of this brand (active methodology, brand_age criteria).
    Returns number of rows updated.
    """
    criteria = active_brand_age_criteria()
    if not criteria.exists():
        return 0

    val = _year_raw_value(brand)
    return ModelRawValue.objects.filter(
        model__brand=brand, criterion__in=criteria,
    ).update(raw_value=val)


def flag_active_methodology_recalc() -> None:
    MethodologyVersion.objects.filter(is_active=True).update(needs_recalculation=True)
