from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand

from scoring.engine import recalculate_all


class Command(BaseCommand):
    help = "Пересчитать индекс для всех моделей по активной методике"

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--model-ids", nargs="+", type=int,
            help="ID конкретных моделей для пересчёта",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        model_ids = options.get("model_ids")
        self.stdout.write("Запуск пересчёта...")

        run = recalculate_all(model_ids=model_ids)

        self.stdout.write(self.style.SUCCESS(
            f"Расчёт #{run.pk} завершён: "
            f"{run.models_processed} моделей, статус: {run.get_status_display()}"
        ))
