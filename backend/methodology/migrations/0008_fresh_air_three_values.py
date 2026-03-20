"""Restrict fresh_air to three categorical values per methodology spec."""

from django.db import migrations

FRESH_AIR_SCALE = {
    "нет": 0,
    "приток без подогрева": 50,
    "приток с подогревом": 100,
}


def forwards(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    Criterion.objects.filter(code="fresh_air").update(
        custom_scale_json=FRESH_AIR_SCALE,
    )


def backwards(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    Criterion.objects.filter(code="fresh_air").update(
        custom_scale_json={
            "с подогревом": 100,
            "приток с подогревом": 100,
            "без подогрева": 50,
            "приток без подогрева": 50,
            "нет": 0,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("methodology", "0007_russian_remote_three_values"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
