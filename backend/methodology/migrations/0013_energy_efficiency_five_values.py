"""Restrict energy_efficiency to five label values (Cyrillic A scale)."""

from django.db import migrations

ENERGY_EFFICIENCY_SCALE = {
    "Ниже А": 0,
    "А": 25,
    "А+": 50,
    "А++": 75,
    "А+++": 100,
}


def forwards(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    Criterion.objects.filter(code="energy_efficiency").update(
        custom_scale_json=ENERGY_EFFICIENCY_SCALE,
    )


def backwards(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    Criterion.objects.filter(code="energy_efficiency").update(
        custom_scale_json={
            "А+++": 100,
            "A+++": 100,
            "А++": 75,
            "A++": 75,
            "А+": 50,
            "A+": 50,
            "А": 25,
            "A": 25,
            "ниже А": 0,
            "B": 0,
            "C": 0,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("methodology", "0012_uv_lamp_three_values"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
