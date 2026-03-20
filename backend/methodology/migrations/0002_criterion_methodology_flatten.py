"""Add Criterion.methodology FK, populate from group, make group nullable, update constraint."""

from django.db import migrations, models
import django.db.models.deletion


def populate_methodology(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    for c in Criterion.objects.select_related("group").all():
        if c.group_id and not c.methodology_id:
            c.methodology_id = c.group.methodology_id
            c.save(update_fields=["methodology_id"])


class Migration(migrations.Migration):
    dependencies = [
        ("methodology", "0001_initial"),
    ]

    operations = [
        # 1. Add methodology FK as nullable
        migrations.AddField(
            model_name="criterion",
            name="methodology",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="criteria",
                to="methodology.methodologyversion",
                verbose_name="Методика",
            ),
        ),
        # 2. Populate methodology from group.methodology
        migrations.RunPython(populate_methodology, migrations.RunPython.noop),
        # 3. Make methodology non-nullable
        migrations.AlterField(
            model_name="criterion",
            name="methodology",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="criteria",
                to="methodology.methodologyversion",
                verbose_name="Методика",
            ),
        ),
        # 4. Make group nullable
        migrations.AlterField(
            model_name="criterion",
            name="group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="criteria",
                to="methodology.criteriongroup",
                verbose_name="Группа (устар.)",
            ),
        ),
        # 5. Remove old constraint
        migrations.RemoveConstraint(
            model_name="criterion",
            name="unique_criterion_code_per_group",
        ),
        # 6. Add new constraint
        migrations.AddConstraint(
            model_name="criterion",
            constraint=models.UniqueConstraint(
                fields=["methodology", "code"],
                name="unique_criterion_code_per_methodology",
            ),
        ),
    ]
