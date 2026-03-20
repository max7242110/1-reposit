"""Data migration: populate 33 criteria per Methodology 3.0 spec.

Deletes existing criteria for the active methodology, then creates all 33
from the canonical definition.  Weights sum to exactly 100%.
"""

from django.db import migrations

CRITERIA = [
    # (display_order, code, name_ru, value_type, scoring_type, weight,
    #  min_value, median_value, max_value, unit,
    #  is_inverted, median_by_capacity, custom_scale_json, formula_json)
    (1, "heat_exchanger_inner", "Площадь труб теплообменника внутр. блока",
     "numeric", "min_median_max", 6.0,
     0.1, 0.21, 0.5, "кв.м",
     False, {"2.0": 0.18, "2.5": 0.21, "3.5": 0.30}, None, None),

    (2, "heat_exchanger_outer", "Площадь труб теплообменника наруж. блока",
     "numeric", "min_median_max", 6.0,
     0.15, 0.31, 1.2, "кв.м",
     False, {"2.0": 0.26, "2.5": 0.31, "3.5": 0.37}, None, None),

    (3, "compressor_power", "Мощность компрессора",
     "fallback", "formula", 10.0,
     None, None, None, "Вт",
     False, None, None,
     [{"from": 0, "to": 80, "score": 15},
      {"from": 80, "to": 90, "score": 50},
      {"from": 90, "to": 95, "score": 70},
      {"from": 95, "to": 100, "score": 90},
      {"from": 100, "to": 999, "score": 100}]),

    (4, "erv", "Наличие ЭРВ",
     "binary", "binary", 4.0,
     None, None, None, "",
     False, None, None, None),

    (5, "fan_speed_outdoor", "Регулировка оборотов вентилятора наруж. блока",
     "binary", "binary", 4.0,
     None, None, None, "",
     False, None, None, None),

    (6, "drain_pan_heater", "Наличие обогрева поддона",
     "categorical", "custom_scale", 4.0,
     None, None, None, "",
     False, None,
     {"металлический тэн": 100, "тэн": 100, "термокабель": 50, "нет": 0}, None),

    (7, "noise", "Замер уровня шума",
     "numeric", "min_median_max", 6.0,
     28, 33, 46, "дБ(А)",
     True, None, None, None),

    (8, "min_voltage", "Мин. напряжение",
     "categorical", "custom_scale", 3.0,
     None, None, None, "В",
     False, None,
     {"100": 100, "100В": 100, "150": 50, "150В": 50, "230": 0, "230В": 0}, None),

    (9, "vibration", "Вибрация наружного блока",
     "numeric", "min_median_max", 5.0,
     0.05, 0.2, 0.6, "мм",
     True, None, None, None),

    (10, "ionizer_type", "Тип ионизатора",
     "categorical", "custom_scale", 2.0,
     None, None, None, "",
     False, None,
     {"технологичный": 100, "отдельный прибор": 100, "щётка": 50, "обычная щётка": 50, "нет": 0}, None),

    # Criterion 11 (UV lamp type) removed — duplicate of criterion 27

    (12, "fine_filters", "Тип фильтров тонкой очистки",
     "categorical", "custom_scale", 1.0,
     None, None, None, "",
     False, None,
     {"два фильтра": 100, "два": 100, "2": 100, "один фильтр": 50, "один": 50, "1": 50, "нет": 0, "0": 0}, None),

    (13, "remote_backlight", "Наличие подсветки экрана пульта",
     "binary", "binary", 1.0,
     None, None, None, "",
     False, None, None, None),

    (14, "fan_speeds_indoor", "Количество скоростей вентилятора внутр. блока",
     "numeric", "min_median_max", 2.0,
     1, 5, 100, "шт.",
     False, None, None, None),

    (15, "russian_remote", "Русифицированный пульт ДУ",
     "categorical", "custom_scale", 1.0,
     None, None, None, "",
     False, None,
     {"корпус и экран": 100, "полная": 100, "только корпус": 50, "корпус": 50, "нет": 0}, None),

    (16, "remote_holder", "Держатель пульта ДУ",
     "binary", "binary", 1.0,
     None, None, None, "",
     False, None, None, None),

    (17, "mounting_kit", "Монтажный комплект (медные трубы) в комплекте",
     "binary", "binary", 1.0,
     None, None, None, "",
     False, None, None, None),

    (18, "inverter", "Инверторный компрессор",
     "binary", "binary", 4.0,
     None, None, None, "",
     False, None, None, None),

    (19, "fresh_air", "Приток свежего воздуха",
     "categorical", "custom_scale", 3.0,
     None, None, None, "",
     False, None,
     {"с подогревом": 100, "приток с подогревом": 100, "без подогрева": 50, "приток без подогрева": 50, "нет": 0}, None),

    (20, "heating_capability", "Работа на обогрев",
     "categorical", "custom_scale", 5.0,
     None, None, None, "°C",
     False, None,
     {"-30": 100, "-25": 75, "-20": 50, "-15": 0}, None),

    (21, "max_pipe_length", "Максимальная длина фреонопровода",
     "numeric", "min_median_max", 3.0,
     5, 15, 40, "м",
     False, None, None, None),

    (22, "max_height_diff", "Максимальный перепад высот",
     "numeric", "min_median_max", 3.0,
     3, 5, 15, "м",
     False, None, None, None),

    (23, "wifi", "Наличие WiFi",
     "categorical", "custom_scale", 2.0,
     None, None, None, "",
     False, None,
     {"базовая комплектация": 100, "есть": 100, "да": 100, "опционально": 50, "опция": 50, "нет": 0}, None),

    (24, "alice_control", "Управление через Алису",
     "categorical", "custom_scale", 2.0,
     None, None, None, "",
     False, None,
     {"базовая": 100, "есть": 100, "да": 100, "сторонние сервисы": 50, "через сторонние": 50, "нет": 0}, None),

    (25, "louver_control", "Управление жалюзи в стороны с пульта",
     "binary", "binary", 1.0,
     None, None, None, "",
     False, None, None, None),

    (26, "ir_sensor", "Наличие ИК датчика присутствия человека",
     "categorical", "custom_scale", 2.0,
     None, None, None, "",
     False, None,
     {"управление потоком": 100, "поток воздуха": 100, "полный": 100, "энергосбережение": 50, "только энергосбережение": 50, "нет": 0}, None),

    (27, "uv_lamp", "Наличие УФ-лампы",
     "categorical", "custom_scale", 2.0,
     None, None, None, "",
     False, None,
     {"крупная лампа": 100, "крупная": 100, "светодиоды": 50, "мелкие светодиоды": 50, "нет": 0}, None),

    (28, "self_clean_freezing", "Наличие самоочистки замораживанием",
     "binary", "binary", 1.0,
     None, None, None, "",
     False, None, None, None),

    (29, "temp_sterilization", "Наличие функции температурной стерилизации",
     "binary", "binary", 1.0,
     None, None, None, "",
     False, None, None, None),

    (30, "brand_age_ru", "Возраст бренда на рынке РФ",
     "brand_age", "min_median_max", 3.0,
     1995, 2010, 2026, "год",
     False, None, None, None),

    (31, "energy_efficiency", "Энергоэффективность",
     "categorical", "custom_scale", 5.0,
     None, None, None, "",
     False, None,
     {"А+++": 100, "A+++": 100, "А++": 75, "A++": 75, "А+": 50, "A+": 50, "А": 25, "A": 25, "ниже А": 0, "B": 0, "C": 0}, None),

    (32, "standby_heating", "Функция дежурного обогрева +8 °C",
     "binary", "binary", 1.0,
     None, None, None, "",
     False, None, None, None),

    (33, "warranty", "Гарантия",
     "numeric", "min_median_max", 4.0,
     1, 3, 7, "лет",
     False, None, None, None),

    (34, "air_freshener", "Ароматизатор воздуха",
     "binary", "binary", 1.0,
     None, None, None, "",
     False, None, None, None),
]


def populate_criteria(apps, schema_editor):
    MethodologyVersion = apps.get_model("methodology", "MethodologyVersion")
    Criterion = apps.get_model("methodology", "Criterion")

    methodology = MethodologyVersion.objects.filter(is_active=True).first()
    if methodology is None:
        methodology = MethodologyVersion.objects.first()
    if methodology is None:
        methodology = MethodologyVersion.objects.create(
            version="3.0",
            name="Август-климат 3.0",
            is_active=True,
        )

    Criterion.objects.filter(methodology=methodology).delete()

    for row in CRITERIA:
        (display_order, code, name_ru, value_type, scoring_type, weight,
         min_value, median_value, max_value, unit,
         is_inverted, median_by_capacity, custom_scale_json, formula_json) = row

        Criterion.objects.create(
            methodology=methodology,
            display_order=display_order,
            code=code,
            name_ru=name_ru,
            value_type=value_type,
            scoring_type=scoring_type,
            weight=weight,
            min_value=min_value,
            median_value=median_value,
            max_value=max_value,
            unit=unit,
            is_inverted=is_inverted,
            median_by_capacity=median_by_capacity,
            custom_scale_json=custom_scale_json,
            formula_json=formula_json,
            is_active=True,
            is_public=True,
            region_scope="global",
        )


def reverse_populate(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("methodology", "0004_add_brand_age_value_type"),
    ]

    operations = [
        migrations.RunPython(populate_criteria, reverse_populate),
    ]
