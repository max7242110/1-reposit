"""Удаление невалидных вариантов значений из custom_scale_json + обнуление raw_value."""

from django.db import migrations

REMOVALS = {
    "Наличие обогрева поддона": ["металлический тэн"],
    "Мин. напряжение": ["100", "150"],
    "Ионизатор": ["обычная щетка", "технологичный"],
    "Приток свежего воздуха": ["да"],
    "Работа на обогрев": ["нет", "да"],
    "Максимальная длина фреонопровода": ["-15", "-7 и выше", "-25"],
    "Энергоэффективность": ["2012", "2011", "2008"],
    "Функция дежурного обогрева +8С": ["А", "А++"],
    "Гарантия": ["Да", "Нет"],
    "Ароматизатор воздуха": ["3", "7", "5"],
}


def remove_scale_values(apps, schema_editor):
    Criterion = apps.get_model("methodology", "Criterion")
    ModelRawValue = apps.get_model("catalog", "ModelRawValue")

    for name, values_to_remove in REMOVALS.items():
        # Может быть несколько критериев с одним именем (разные версии методики)
        criteria = Criterion.objects.filter(name_ru=name)
        for criterion in criteria:
            # Удалить из custom_scale_json
            if criterion.custom_scale_json and isinstance(criterion.custom_scale_json, dict):
                scale = dict(criterion.custom_scale_json)
                changed = False
                for v in values_to_remove:
                    if v in scale:
                        del scale[v]
                        changed = True
                if changed:
                    criterion.custom_scale_json = scale
                    criterion.save(update_fields=["custom_scale_json"])

            # Обнулить raw_value у моделей с удалёнными значениями
            ModelRawValue.objects.filter(
                criterion=criterion, raw_value__in=values_to_remove
            ).update(raw_value="")


def reverse_noop(apps, schema_editor):
    # Обратная операция невозможна: удалённые значения и баллы неизвестны
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("methodology", "0019_replace_da_with_est"),
        ("catalog", "0005_acmodel_cons_text_acmodel_price_acmodel_pros_text_and_more"),
    ]

    operations = [
        migrations.RunPython(remove_scale_values, reverse_noop),
    ]
