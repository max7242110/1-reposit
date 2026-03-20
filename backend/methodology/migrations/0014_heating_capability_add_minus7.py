"""Add heating_capability option «-7 и выше» (0 pts, mild-climate tier)."""

from django.db import migrations

HEATING_SCALE = {
    "-30": 100,
    "-25": 75,
    "-20": 50,
    "-15": 0,
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
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("methodology", "0013_energy_efficiency_five_values"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
