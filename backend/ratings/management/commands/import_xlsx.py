from pathlib import Path

import openpyxl
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ratings.models import AirConditioner, ParameterValue

PARAMETER_COLUMNS = [
    # (value_col, score_col, name, unit)
    ("G", "H", "Шум мин.", "дБ(А)"),
    ("I", "J", "Вибрация", "мм"),
    ("K", "L", "Мин. напряжение", "В"),
    ("M", "N", "S меди внутр. блок", ""),
    ("O", "P", "S меди наруж. блок", ""),
    ("Q", "R", "Наличие ЭРВ", ""),
    ("S", "T", "Подсветка пульта", ""),
    ("U", "V", "Тип (инвертор/он-офф)", ""),
    ("W", "X", "Наличие WiFi", ""),
    ("Y", "Z", "Регулировка оборотов наруж. бл.", ""),
    ("AA", "AB", "Кол-во скоростей внутр. бл.", ""),
    ("AC", "AD", "Макс. длина фреонопровода", "м"),
]


def col_to_index(col_letter: str) -> int:
    """Convert Excel column letter(s) to 0-based index."""
    result = 0
    for ch in col_letter.upper():
        result = result * 26 + (ord(ch) - ord("A") + 1)
    return result - 1


class Command(BaseCommand):
    help = "Импорт данных кондиционеров из xlsx-файла"

    def add_arguments(self, parser):
        parser.add_argument(
            "file",
            nargs="?",
            default=None,
            help="Путь к xlsx-файлу (по умолчанию: Рейтинг 2026-1.xlsx в корне проекта)",
        )

    def handle(self, *args, **options):
        file_path = options["file"]
        if file_path is None:
            project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
            file_path = project_root / "Рейтинг 2026-1.xlsx"
        else:
            file_path = Path(file_path)

        if not file_path.exists():
            raise CommandError(f"Файл не найден: {file_path}")

        self.stdout.write(f"Загрузка из {file_path}...")

        wb = openpyxl.load_workbook(str(file_path), data_only=True)
        ws = wb.active

        imported = 0
        skipped = 0

        with transaction.atomic():
            AirConditioner.objects.all().delete()

            for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
                cells = {c.column_letter: c.value for c in row}
                multi_letter = {}
                for c in row:
                    col_idx = c.column - 1
                    if col_idx >= 26:
                        first = chr(ord("A") + col_idx // 26 - 1)
                        second = chr(ord("A") + col_idx % 26)
                        multi_letter[first + second] = c.value

                cells.update(multi_letter)

                rank = cells.get("A")
                if rank is None:
                    skipped += 1
                    continue

                brand = str(cells.get("B") or "").strip()
                model_name = str(cells.get("C") or "").strip()

                if not brand and not model_name:
                    skipped += 1
                    continue

                total_score = cells.get("AE")
                if total_score is None or total_score == 0:
                    skipped += 1
                    continue

                ac = AirConditioner.objects.create(
                    rank=int(rank),
                    brand=brand,
                    model_name=model_name,
                    youtube_url=str(cells.get("D") or "").strip(),
                    rutube_url=str(cells.get("E") or "").strip(),
                    vk_url=str(cells.get("F") or "").strip(),
                    total_score=round(float(total_score), 2),
                )

                for val_col, score_col, name, unit in PARAMETER_COLUMNS:
                    raw = cells.get(val_col)
                    score = cells.get(score_col)
                    ParameterValue.objects.create(
                        air_conditioner=ac,
                        parameter_name=name,
                        raw_value=str(raw) if raw is not None else "",
                        unit=unit,
                        score=round(float(score), 2) if score is not None else 0,
                    )

                imported += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Готово: импортировано {imported} моделей, пропущено {skipped} строк"
            )
        )
