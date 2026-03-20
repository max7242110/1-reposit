"""One-off / bulk sync: fill brand_age raw_value from Brand.sales_start_year_ru."""

from django.core.management.base import BaseCommand

from catalog.models import ACModel
from catalog.sync_brand_age import sync_brand_age_for_model


class Command(BaseCommand):
    help = (
        "Проставить значения критерия «возраст бренда» из справочника брендов "
        "(поле «Год начала продаж в РФ») для всех моделей каталога."
    )

    def handle(self, *args, **options):
        qs = ACModel.objects.select_related("brand").order_by("pk")
        total = 0
        for ac in qs.iterator(chunk_size=200):
            sync_brand_age_for_model(ac)
            total += 1
        self.stdout.write(self.style.SUCCESS(f"Обработано моделей: {total}"))
