"""Restrict ir_sensor criterion to three categorical values."""

from django.db import migrations

IR_SENSOR_SCALE = {
    "нет": 0,
    "есть для энергосбережения": 50,
    "есть для управления потоком": 100,
}


def forwards(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    Criterion.objects.filter(code="ir_sensor").update(
        custom_scale_json=IR_SENSOR_SCALE,
    )


def backwards(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    Criterion.objects.filter(code="ir_sensor").update(
        custom_scale_json={
            "управление потоком": 100,
            "поток воздуха": 100,
            "полный": 100,
            "энергосбережение": 50,
            "только энергосбережение": 50,
            "нет": 0,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("methodology", "0010_alice_control_three_values"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
