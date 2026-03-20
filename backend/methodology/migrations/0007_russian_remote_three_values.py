"""Restrict russian_remote to three categorical values per methodology spec."""

from django.db import migrations

RUSSIAN_REMOTE_SCALE = {
    "нет": 0,
    "только корпус": 50,
    "корпус и экран": 100,
}


def forwards(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    Criterion.objects.filter(code="russian_remote").update(
        custom_scale_json=RUSSIAN_REMOTE_SCALE,
    )


def backwards(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    Criterion.objects.filter(code="russian_remote").update(
        custom_scale_json={
            "корпус и экран": 100,
            "полная": 100,
            "только корпус": 50,
            "корпус": 50,
            "нет": 0,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("methodology", "0006_fan_speeds_indoor_discrete_scale"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
