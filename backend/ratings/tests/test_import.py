from __future__ import annotations

import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import openpyxl
import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from ratings.constants import PARAMETER_DEFS
from ratings.models import AirConditioner, ParameterValue

HEADERS = [
    "№", "Ролик", "Модель", "YouTube", "RuTube", "VK",
    "Шум мин.\nдБ(А)", "Баллы",
    "Вибрация\n(мм)", "Баллы",
    "Мин напряжение (В)", "Баллы",
    "S меди внутр блок", "Баллы",
    "S меди наруж блок", "Баллы",
    "Наличие ЭРВ", "Баллы",
    "Подсветка пульта", "Баллы",
    "Тип Инвертор\nили он/офф", "Баллы",
    "Наличие WiFi", "Баллы",
    "Регулировка оборотов наруж.бл.", "Баллы",
    "Кол-во скоростей внутр.бл.", "Баллы",
    "Макс. длина фреонопровода", "Баллы",
    "Итог",
]

NUM_PARAM_COLUMNS = len(PARAMETER_DEFS)


@contextmanager
def temp_xlsx(rows: list[list]) -> Generator[Path, None, None]:
    """Create a temporary xlsx and ensure cleanup."""
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        path = Path(f.name)
    try:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(HEADERS)
        for row in rows:
            ws.append(row)
        wb.save(str(path))
        wb.close()
        yield path
    finally:
        path.unlink(missing_ok=True)


def make_row(
    rank: int,
    brand: str,
    model: str,
    total: float,
    noise_val: int = 32,
    noise_score: float = 36,
) -> list:
    return [
        rank, brand, model,
        "https://youtu.be/abc", "https://rutube.ru/v/abc", "https://vk.com/v",
        noise_val, noise_score,
        0.07, 4.3, 100, 5, 0.26, 26, 0.28, 28,
        "нет", 0, "есть", 10, "инвертор", 30, "Опция", 5,
        "Есть", 10, 5, 1, 20, None,
        total,
    ]


@pytest.mark.django_db
class TestImportXlsx:
    def test_basic_import(self) -> None:
        with temp_xlsx([
            make_row(1, "BrandA", "Model-A1", 155.3),
            make_row(2, "BrandB", "Model-B2", 242.3),
        ]) as path:
            call_command("import_xlsx", str(path))
        assert AirConditioner.objects.count() == 2
        assert ParameterValue.objects.count() == 2 * NUM_PARAM_COLUMNS

    def test_skips_empty_rows(self) -> None:
        with temp_xlsx([
            make_row(1, "BrandA", "Model-A1", 155.3),
            [None] * len(HEADERS),
        ]) as path:
            call_command("import_xlsx", str(path))
        assert AirConditioner.objects.count() == 1

    def test_skips_zero_score(self) -> None:
        with temp_xlsx([make_row(1, "BrandA", "Model-A1", 0)]) as path:
            call_command("import_xlsx", str(path))
        assert AirConditioner.objects.count() == 0

    def test_idempotent_import(self) -> None:
        with temp_xlsx([make_row(1, "BrandA", "Model-A1", 155.3)]) as path:
            call_command("import_xlsx", str(path))
            call_command("import_xlsx", str(path))
        assert AirConditioner.objects.count() == 1

    def test_parameter_values_correct(self) -> None:
        with temp_xlsx([
            make_row(1, "BrandA", "Model-A1", 155.3, noise_val=30, noise_score=40),
        ]) as path:
            call_command("import_xlsx", str(path))
        ac = AirConditioner.objects.first()
        assert ac is not None
        noise_param = ac.parameters.get(parameter_name="Шум мин.")
        assert noise_param.raw_value == "30"
        assert noise_param.score == 40.0

    def test_file_not_found(self) -> None:
        with pytest.raises(CommandError, match="не найден"):
            call_command("import_xlsx", "/nonexistent/file.xlsx")

    def test_headers_only_xlsx(self) -> None:
        with temp_xlsx([]) as path:
            call_command("import_xlsx", str(path))
        assert AirConditioner.objects.count() == 0

    def test_invalid_rank_skipped(self) -> None:
        row = make_row(1, "BrandA", "Model-A1", 155.3)
        row[0] = "not-a-number"
        with temp_xlsx([row]) as path:
            call_command("import_xlsx", str(path))
        assert AirConditioner.objects.count() == 0

    def test_bulk_creates_parameters(self) -> None:
        with temp_xlsx([make_row(1, "BrandA", "Model-A1", 155.3)]) as path:
            call_command("import_xlsx", str(path))
        ac = AirConditioner.objects.first()
        assert ac is not None
        assert ac.parameters.count() == NUM_PARAM_COLUMNS
