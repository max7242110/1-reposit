"""Restrict alice_control criterion to three categorical values."""

from django.db import migrations

ALICE_CONTROL_SCALE = {
    "нет": 0,
    "есть через сторонние сервисы": 50,
    "есть в базе": 100,
}


def forwards(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    Criterion.objects.filter(code="alice_control").update(
        custom_scale_json=ALICE_CONTROL_SCALE,
    )


def backwards(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    Criterion.objects.filter(code="alice_control").update(
        custom_scale_json={
            "базовая": 100,
            "есть": 100,
            "да": 100,
            "сторонние сервисы": 50,
            "через сторонние": 50,
            "нет": 0,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("methodology", "0009_wifi_three_values"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
