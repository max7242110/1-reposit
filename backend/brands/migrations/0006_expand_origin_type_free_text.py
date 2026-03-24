from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("brands", "0005_seed_origin_types"),
    ]

    operations = [
        migrations.AlterField(
            model_name="brandoriginclass",
            name="origin_type",
            field=models.CharField(max_length=255, unique=True, verbose_name="Тип происхождения"),
        ),
    ]
