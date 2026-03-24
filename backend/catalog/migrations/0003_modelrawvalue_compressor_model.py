from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_convert_compressor_power_values_to_kw"),
    ]

    operations = [
        migrations.AddField(
            model_name="modelrawvalue",
            name="compressor_model",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Используется для критерия «Мощность компрессора».",
                max_length=255,
                verbose_name="Модель компрессора",
            ),
        ),
    ]
