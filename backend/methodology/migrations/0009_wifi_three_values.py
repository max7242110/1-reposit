"""Restrict wifi criterion to three categorical values."""

from django.db import migrations

WIFI_SCALE = {
    "нет": 0,
    "опционально": 50,
    "есть в базе": 100,
}


def forwards(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    Criterion.objects.filter(code="wifi").update(
        custom_scale_json=WIFI_SCALE,
    )


def backwards(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    Criterion.objects.filter(code="wifi").update(
        custom_scale_json={
            "базовая комплектация": 100,
            "есть": 100,
            "да": 100,
            "опционально": 50,
            "опция": 50,
            "нет": 0,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("methodology", "0008_fresh_air_three_values"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
