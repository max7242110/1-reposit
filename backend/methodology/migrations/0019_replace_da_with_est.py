"""Замена значения 'Да' на 'Есть' в 6 критериях (custom_scale_json + ModelRawValue)."""

from django.db import migrations

CRITERIA_NAMES = [
    "Наличие ЭРВ",
    "Регулировка оборотов вентилятора наруж. блока",
    "Наличие подсветки экрана пульта",
    "Держатель пульта ДУ",
    "Функция дежурного обогрева +8С",
    "Ароматизатор воздуха",
]


def replace_da_with_est(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    ModelRawValue = apps.get_model("catalog", "ModelRawValue")

    for criterion in Criterion.objects.filter(name_ru__in=CRITERIA_NAMES):
        # Обновить custom_scale_json: "Да" → "Есть"
        if criterion.custom_scale_json and isinstance(criterion.custom_scale_json, dict):
            if "Да" in criterion.custom_scale_json:
                scale = dict(criterion.custom_scale_json)
                scale["Есть"] = scale.pop("Да")
                criterion.custom_scale_json = scale
                criterion.save(update_fields=["custom_scale_json"])

        # Обновить raw_value в ModelRawValue
        ModelRawValue.objects.filter(
            criterion=criterion, raw_value="Да"
        ).update(raw_value="Есть")


def reverse_replace(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    ModelRawValue = apps.get_model("catalog", "ModelRawValue")

    for criterion in Criterion.objects.filter(name_ru__in=CRITERIA_NAMES):
        if criterion.custom_scale_json and isinstance(criterion.custom_scale_json, dict):
            if "Есть" in criterion.custom_scale_json:
                scale = dict(criterion.custom_scale_json)
                scale["Да"] = scale.pop("Есть")
                criterion.custom_scale_json = scale
                criterion.save(update_fields=["custom_scale_json"])

        ModelRawValue.objects.filter(
            criterion=criterion, raw_value="Есть"
        ).update(raw_value="Да")


class Migration(migrations.Migration):
    dependencies = [
        ("methodology", "0018_set_compressor_power_unit_watts"),
        ("catalog", "0005_acmodel_cons_text_acmodel_price_acmodel_pros_text_and_more"),
    ]

    operations = [
        migrations.RunPython(replace_da_with_est, reverse_replace),
    ]
