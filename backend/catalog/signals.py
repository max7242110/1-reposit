"""Сигналы каталога: пересчёт индекса при изменении бренда."""

from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from brands.models import Brand

# Поля бренда, влияющие на расчёт индекса моделей
_BRAND_FIELDS_RECALC = frozenset({"sales_start_year_ru", "origin_class_id"})


@receiver(post_save, sender=Brand)
def on_brand_saved(sender, instance: Brand, created, update_fields, **kwargs):
    from catalog.models import ACModel
    from catalog.sync_brand_age import sync_brand_age_for_brand
    from scoring.engine import update_model_total_index

    if not created:
        if update_fields is not None:
            if not (_BRAND_FIELDS_RECALC & set(update_fields)):
                return

    if created or update_fields is None or "sales_start_year_ru" in (update_fields or []):
        sync_brand_age_for_brand(instance)

    for m in ACModel.objects.filter(brand=instance).select_related(
        "brand", "brand__origin_class",
    ):
        update_model_total_index(m)
