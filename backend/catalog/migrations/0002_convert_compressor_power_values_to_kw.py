from django.db import migrations


def convert_to_kw(apps, schema_editor):
    ModelRawValue = apps.get_model("catalog", "ModelRawValue")
    qs = ModelRawValue.objects.filter(criterion__code="compressor_power")
    for rv in qs.iterator():
        raw = (rv.raw_value or "").strip().replace(",", ".")
        if not raw:
            continue
        try:
            value = float(raw)
        except (ValueError, TypeError):
            continue
        if value > 100:
            kw = round(value / 1000.0, 3)
            rv.raw_value = f"{kw:g}"
            rv.numeric_value = kw
            rv.save(update_fields=["raw_value", "numeric_value", "updated_at"])


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0001_initial"),
        ("methodology", "0017_set_compressor_power_unit_kw"),
    ]

    operations = [
        migrations.RunPython(convert_to_kw, migrations.RunPython.noop),
    ]
