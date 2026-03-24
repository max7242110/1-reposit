from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("methodology", "0015_heating_capability_rebalance_scores"),
    ]

    operations = [
        migrations.AddField(
            model_name="criterion",
            name="note",
            field=models.TextField(blank=True, default="", verbose_name="Примечание"),
        ),
        migrations.AddField(
            model_name="criterion",
            name="show_note_on_site",
            field=models.BooleanField(default=False, verbose_name="Отображать на сайте"),
        ),
    ]
