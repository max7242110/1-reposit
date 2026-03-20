"""Rebalance heating_capability scores per product spec (-15=25, …, -7 и выше=0)."""

from django.db import migrations

HEATING_SCALE = {
    "-30": 100,
    "-25": 75,
    "-20": 50,
    "-15": 25,
    "-7 и выше": 0,
}


def forwards(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    Criterion.objects.filter(code="heating_capability").update(
        custom_scale_json=HEATING_SCALE,
    )


def backwards(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    Criterion.objects.filter(code="heating_capability").update(
        custom_scale_json={
            "-30": 100,
            "-25": 75,
            "-20": 50,
            "-15": 0,
            "-7 и выше": 0,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("methodology", "0014_heating_capability_add_minus7"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
