from django.db import migrations


def convert_to_watts(apps, schema_editor):
    ACModel = apps.get_model("catalog", "ACModel")
    ModelRawValue = apps.get_model("catalog", "ModelRawValue")

    for ac in ACModel.objects.exclude(nominal_capacity__isnull=True).iterator():
        cap = float(ac.nominal_capacity)
        if 0 < cap < 100:
            ac.nominal_capacity = round(cap * 1000.0, 3)
            ac.save(update_fields=["nominal_capacity", "updated_at"])

    qs = ModelRawValue.objects.filter(criterion__code="compressor_power")
    for rv in qs.iterator():
        raw = (rv.raw_value or "").strip().replace(",", ".")
        if not raw:
            continue
        try:
            value = float(raw)
        except (ValueError, TypeError):
            continue
        if 0 < value < 100:
            watts = round(value * 1000.0, 3)
            rv.raw_value = f"{watts:g}"
            rv.numeric_value = watts
            rv.save(update_fields=["raw_value", "numeric_value", "updated_at"])


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_modelrawvalue_compressor_model"),
        ("methodology", "0018_set_compressor_power_unit_watts"),
    ]

    operations = [
        migrations.RunPython(convert_to_watts, migrations.RunPython.noop),
    ]
