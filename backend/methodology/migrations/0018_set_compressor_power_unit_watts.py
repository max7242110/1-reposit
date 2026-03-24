from django.db import migrations


def set_unit_watts(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    Criterion.objects.filter(code="compressor_power").update(unit="Вт")


class Migration(migrations.Migration):

    dependencies = [
        ("methodology", "0017_set_compressor_power_unit_kw"),
    ]

    operations = [
        migrations.RunPython(set_unit_watts, migrations.RunPython.noop),
    ]
