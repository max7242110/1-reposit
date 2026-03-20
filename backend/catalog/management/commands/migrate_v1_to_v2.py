"""Migrate data from v1 (ratings app) to v2 (brands/methodology/catalog/scoring)."""

from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction

from brands.models import Brand
from catalog.models import ACModel, EquipmentType, ModelRawValue, ModelRegion
from methodology.models import Criterion, MethodologyVersion
from ratings.models import AirConditioner, ParameterValue

V1_TO_V2_CRITERIA = {
    "Шум мин.": ("noise_min", "numeric", "min_median_max", "дБ(А)"),
    "Вибрация": ("vibration", "numeric", "min_median_max", "мм"),
    "Мин. напряжение": ("min_voltage", "lab", "custom_scale", "В"),
    "S меди внутр. блок": ("copper_area_inner", "numeric", "min_median_max", ""),
    "S меди наруж. блок": ("copper_area_outer", "numeric", "min_median_max", ""),
    "Наличие ЭРВ": ("erv", "binary", "binary", ""),
    "Подсветка пульта": ("remote_backlight", "binary", "binary", ""),
    "Тип (инвертор/он-офф)": ("inverter_type", "categorical", "universal_scale", ""),
    "Наличие WiFi": ("wifi", "categorical", "custom_scale", ""),
    "Регулировка оборотов наруж. бл.": ("fan_speed_control", "binary", "binary", ""),
    "Кол-во скоростей внутр. бл.": ("fan_speeds_indoor", "categorical", "custom_scale", ""),
    "Макс. длина фреонопровода": ("max_pipe_length", "numeric", "min_median_max", "м"),
}


class Command(BaseCommand):
    help = "Перенос данных из v1 (ratings) в v2 (brands/methodology/catalog/scoring)"

    def handle(self, *args: Any, **options: Any) -> None:
        old_acs = AirConditioner.objects.prefetch_related("parameters").all()
        if not old_acs.exists():
            self.stdout.write(self.style.WARNING("Нет данных в v1 для миграции"))
            return

        with transaction.atomic():
            methodology = self._create_methodology()
            criteria_map = self._create_criteria(methodology)
            eq_type = EquipmentType.objects.get_or_create(name="Настенная сплит-система")[0]

            migrated = 0
            for ac in old_acs:
                brand, _ = Brand.objects.get_or_create(name=ac.brand)
                ac_model = ACModel.objects.create(
                    brand=brand,
                    inner_unit=ac.model_name,
                    equipment_type=eq_type,
                    publish_status=ACModel.PublishStatus.PUBLISHED,
                    total_index=ac.total_score,
                    youtube_url=ac.youtube_url,
                    rutube_url=ac.rutube_url,
                    vk_url=ac.vk_url,
                )
                ModelRegion.objects.create(
                    model=ac_model, region_code=ModelRegion.RegionCode.RU,
                )

                for pv in ac.parameters.all():
                    criterion = criteria_map.get(pv.parameter_name)
                    if not criterion:
                        continue
                    numeric = None
                    try:
                        numeric = float(pv.raw_value)
                    except (ValueError, TypeError):
                        pass
                    ModelRawValue.objects.create(
                        model=ac_model,
                        criterion=criterion,
                        raw_value=pv.raw_value,
                        numeric_value=numeric,
                        source="Импорт v1 (xlsx)",
                    )
                migrated += 1

        self.stdout.write(self.style.SUCCESS(f"Мигрировано {migrated} моделей из v1 в v2"))

    def _create_methodology(self) -> MethodologyVersion:
        mv, _ = MethodologyVersion.objects.get_or_create(
            version="1.0",
            defaults={"name": "Август-климат v1.0", "is_active": True},
        )
        return mv

    def _create_criteria(self, methodology: MethodologyVersion) -> dict[str, Criterion]:
        criteria_map: dict[str, Criterion] = {}
        for idx, (v1_name, (code, vtype, stype, unit)) in enumerate(V1_TO_V2_CRITERIA.items()):
            criterion, _ = Criterion.objects.get_or_create(
                methodology=methodology, code=code,
                defaults={
                    "name_ru": v1_name,
                    "unit": unit,
                    "value_type": vtype,
                    "scoring_type": stype,
                    "weight": round(100 / len(V1_TO_V2_CRITERIA), 2),
                    "display_order": idx + 1,
                    "is_active": True,
                },
            )
            criteria_map[v1_name] = criterion
        return criteria_map
