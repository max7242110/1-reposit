from django.db import migrations


def set_unit_kw(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    Criterion.objects.filter(code="compressor_power").update(unit="кВт")


class Migration(migrations.Migration):

    dependencies = [
        ("methodology", "0016_criterion_note_and_site_flag"),
    ]

    operations = [
        migrations.RunPython(set_unit_kw, migrations.RunPython.noop),
    ]
