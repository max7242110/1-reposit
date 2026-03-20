"""Restrict fan_speeds_indoor to discrete values 0–10 and 100 (custom scale)."""

from django.db import migrations

FAN_SPEEDS_SCALE = {
    "0": 0,
    "1": 0,
    "2": 12.5,
    "3": 25,
    "4": 37.5,
    "5": 50,
    "6": 52.63,
    "7": 55.26,
    "8": 57.89,
    "9": 60.53,
    "10": 63.16,
    "100": 100,
}


def forwards(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    Criterion.objects.filter(code="fan_speeds_indoor").update(
        value_type="categorical",
        scoring_type="custom_scale",
        min_value=None,
        median_value=None,
        max_value=None,
        median_by_capacity=None,
        custom_scale_json=FAN_SPEEDS_SCALE,
    )


def backwards(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    Criterion.objects.filter(code="fan_speeds_indoor").update(
        value_type="numeric",
        scoring_type="min_median_max",
        min_value=1,
        median_value=5,
        max_value=100,
        median_by_capacity=None,
        custom_scale_json=None,
    )


class Migration(migrations.Migration):

    dependencies = [
        ("methodology", "0005_populate_criteria_v3"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
