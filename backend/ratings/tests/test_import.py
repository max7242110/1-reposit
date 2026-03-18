import tempfile
from pathlib import Path

import openpyxl
import pytest
from django.core.management import call_command

from ratings.models import AirConditioner, ParameterValue


def _create_test_xlsx(path: Path, rows: list[list]) -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    headers = [
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
    ws.append(headers)
    for row in rows:
        ws.append(row)
    wb.save(str(path))


def _make_row(rank, brand, model, total, noise_val=32, noise_score=36):
    return [
        rank, brand, model,
        "https://youtu.be/abc", "https://rutube.ru/v/abc", "https://vk.com/v",
        noise_val, noise_score,
        0.07, 4.3,
        100, 5,
        0.26, 26,
        0.28, 28,
        "нет", 0,
        "есть", 10,
        "инвертор", 30,
        "Опция", 5,
        "Есть", 10,
        5, 1,
        20, None,
        total,
    ]


@pytest.mark.django_db
class TestImportXlsx:
    def test_basic_import(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = Path(f.name)
        _create_test_xlsx(path, [
            _make_row(1, "BrandA", "Model-A1", 155.3),
            _make_row(2, "BrandB", "Model-B2", 242.3),
        ])
        call_command("import_xlsx", str(path))
        assert AirConditioner.objects.count() == 2
        assert ParameterValue.objects.count() == 24
        path.unlink()

    def test_skips_empty_rows(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = Path(f.name)
        _create_test_xlsx(path, [
            _make_row(1, "BrandA", "Model-A1", 155.3),
            [None] * 31,
        ])
        call_command("import_xlsx", str(path))
        assert AirConditioner.objects.count() == 1
        path.unlink()

    def test_skips_zero_score(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = Path(f.name)
        _create_test_xlsx(path, [
            _make_row(1, "BrandA", "Model-A1", 0),
        ])
        call_command("import_xlsx", str(path))
        assert AirConditioner.objects.count() == 0
        path.unlink()

    def test_idempotent_import(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = Path(f.name)
        _create_test_xlsx(path, [
            _make_row(1, "BrandA", "Model-A1", 155.3),
        ])
        call_command("import_xlsx", str(path))
        call_command("import_xlsx", str(path))
        assert AirConditioner.objects.count() == 1
        path.unlink()

    def test_parameter_values_correct(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = Path(f.name)
        _create_test_xlsx(path, [
            _make_row(1, "BrandA", "Model-A1", 155.3, noise_val=30, noise_score=40),
        ])
        call_command("import_xlsx", str(path))
        ac = AirConditioner.objects.first()
        noise_param = ac.parameters.get(parameter_name="Шум мин.")
        assert noise_param.raw_value == "30"
        assert noise_param.score == 40.0
        path.unlink()

    def test_file_not_found(self):
        with pytest.raises(Exception, match="не найден"):
            call_command("import_xlsx", "/nonexistent/file.xlsx")
