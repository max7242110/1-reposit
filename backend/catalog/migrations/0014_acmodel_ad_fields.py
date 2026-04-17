from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0013_acmodelphoto_alt"),
    ]

    operations = [
        migrations.AddField(
            model_name="acmodel",
            name="is_ad",
            field=models.BooleanField(default=False, verbose_name="Рекламная модель"),
        ),
        migrations.AddField(
            model_name="acmodel",
            name="ad_position",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="Номер позиции в списке (1 = первая). Пусто = не рекламная.",
                null=True,
                verbose_name="Позиция в рейтинге",
            ),
        ),
    ]
