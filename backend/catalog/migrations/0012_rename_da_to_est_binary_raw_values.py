"""Переименовать raw_value «Да/да» → «Есть/есть» для бинарных критериев.

После смены UI-лейблов (datalist: "да"/"нет" → "есть"/"нет") приводим
уже сохранённые значения в ModelRawValue к новому формату, чтобы
пользователь не видел в админке старое «Да» вперемешку с новым «Есть».
"""

from __future__ import annotations

from django.db import migrations


def rename_da_to_est(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    ModelRawValue = apps.get_model("catalog", "ModelRawValue")

    binary_codes = list(
        Criterion.objects.filter(value_type="binary").values_list("id", flat=True)
    )
    if not binary_codes:
        return

    qs = ModelRawValue.objects.filter(criterion_id__in=binary_codes)
    # Точный case-sensitive маппинг: сохраняем регистр (капс → капс).
    qs.filter(raw_value="Да").update(raw_value="Есть")
    qs.filter(raw_value="да").update(raw_value="есть")
    qs.filter(raw_value="ДА").update(raw_value="ЕСТЬ")


def rename_est_to_da(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    ModelRawValue = apps.get_model("catalog", "ModelRawValue")

    binary_codes = list(
        Criterion.objects.filter(value_type="binary").values_list("id", flat=True)
    )
    if not binary_codes:
        return

    qs = ModelRawValue.objects.filter(criterion_id__in=binary_codes)
    qs.filter(raw_value="Есть").update(raw_value="Да")
    qs.filter(raw_value="есть").update(raw_value="да")
    qs.filter(raw_value="ЕСТЬ").update(raw_value="ДА")


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0011_cleanup_criterion_standalone"),
        ("methodology", "0028_populate_criterion_descriptions"),
    ]

    operations = [
        migrations.RunPython(rename_da_to_est, rename_est_to_da),
    ]
