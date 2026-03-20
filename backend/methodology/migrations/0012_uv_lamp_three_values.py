"""Restrict uv_lamp criterion to three categorical values."""

from django.db import migrations

UV_LAMP_SCALE = {
    "нет": 0,
    "мелкие светодиоды": 50,
    "крупная лампа": 100,
}


def forwards(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    Criterion.objects.filter(code="uv_lamp").update(
        custom_scale_json=UV_LAMP_SCALE,
    )


def backwards(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    Criterion.objects.filter(code="uv_lamp").update(
        custom_scale_json={
            "крупная лампа": 100,
            "крупная": 100,
            "светодиоды": 50,
            "мелкие светодиоды": 50,
            "нет": 0,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("methodology", "0011_ir_sensor_three_values"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
