"""Restructure BrandOriginClass from per-brand to lookup table.

Before: BrandOriginClass has OneToOne(Brand), sales_start_year_ru
After:  BrandOriginClass is a lookup (origin_type unique, no brand FK)
        Brand has FK to BrandOriginClass + sales_start_year_ru
"""

import django.db.models.deletion
from django.db import migrations, models


def migrate_forward(apps, schema_editor):
    """Transfer data from old structure to new."""
    Brand = apps.get_model("brands", "Brand")
    BrandOriginClass = apps.get_model("brands", "BrandOriginClass")

    lookup = {}
    for old_oc in BrandOriginClass.objects.all():
        if old_oc.origin_type not in lookup:
            lookup[old_oc.origin_type] = {
                "fallback_score": old_oc.fallback_score,
                "pk": old_oc.pk,
            }

        brand = Brand.objects.filter(pk=old_oc.brand_id).first()
        if brand:
            brand.sales_start_year_ru = old_oc.sales_start_year_ru
            brand.new_origin_class_id = old_oc.pk
            brand.save(update_fields=["sales_start_year_ru", "new_origin_class_id"])

    seen_types = set()
    for old_oc in BrandOriginClass.objects.all().order_by("pk"):
        if old_oc.origin_type in seen_types:
            brands_pointing = Brand.objects.filter(new_origin_class_id=old_oc.pk)
            canonical_pk = lookup[old_oc.origin_type]["pk"]
            brands_pointing.update(new_origin_class_id=canonical_pk)
            old_oc.delete()
        else:
            seen_types.add(old_oc.origin_type)


def migrate_backward(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("brands", "0002_brandoriginclass_sales_start_year_ru"),
    ]

    operations = [
        # 1. Add new fields on Brand (nullable for now)
        migrations.AddField(
            model_name="brand",
            name="sales_start_year_ru",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True,
                verbose_name="Год начала продаж в РФ",
                help_text="Например: 2015",
            ),
        ),
        migrations.AddField(
            model_name="brand",
            name="new_origin_class",
            field=models.ForeignKey(
                to="brands.BrandOriginClass",
                on_delete=django.db.models.deletion.SET_NULL,
                null=True, blank=True,
                related_name="brands_new",
                verbose_name="Тип происхождения",
            ),
        ),

        # 2. Data migration: copy data from old structure to new
        migrations.RunPython(migrate_forward, migrate_backward),

        # 3. Remove old brand FK from BrandOriginClass
        migrations.RemoveField(
            model_name="brandoriginclass",
            name="brand",
        ),

        # 4. Remove old sales_start_year_ru from BrandOriginClass
        migrations.RemoveField(
            model_name="brandoriginclass",
            name="sales_start_year_ru",
        ),

        # 5. Make origin_type unique on BrandOriginClass
        migrations.AlterField(
            model_name="brandoriginclass",
            name="origin_type",
            field=models.CharField(
                choices=[
                    ("japanese", "Японский"),
                    ("chinese_oem", "Китайский / OEM"),
                    ("european", "Европейский"),
                    ("other", "Другой"),
                ],
                max_length=30, unique=True,
                verbose_name="Тип происхождения",
            ),
        ),

        # 6. Rename new_origin_class → origin_class on Brand
        migrations.RenameField(
            model_name="brand",
            old_name="new_origin_class",
            new_name="origin_class",
        ),

        # 7. Update Meta on BrandOriginClass
        migrations.AlterModelOptions(
            name="brandoriginclass",
            options={
                "verbose_name": "Тип происхождения бренда",
                "verbose_name_plural": "Типы происхождения брендов",
            },
        ),
    ]
