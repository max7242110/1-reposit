"""Seed the three origin types: Japanese, Chinese factory, Chinese OEM.

Remaps existing brands that pointed to old types (european, other) and
removes unused entries.
"""

from django.db import migrations

ORIGIN_TYPES = [
    ("japanese", 90),
    ("chinese_factory", 70),
    ("chinese_oem", 50),
]


def seed(apps, schema_editor):
    BrandOriginClass = apps.get_model("brands", "BrandOriginClass")
    Brand = apps.get_model("brands", "Brand")

    BrandOriginClass.objects.filter(origin_type__in=["european", "other"]).delete()

    for origin_type, fallback_score in ORIGIN_TYPES:
        BrandOriginClass.objects.update_or_create(
            origin_type=origin_type,
            defaults={"fallback_score": fallback_score},
        )


def reverse_seed(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("brands", "0004_update_origin_types"),
    ]

    operations = [
        migrations.RunPython(seed, reverse_seed),
    ]
