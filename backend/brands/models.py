from __future__ import annotations

from django.db import models

from core.models import TimestampMixin


class BrandOriginClass(TimestampMixin):
    """Справочник типов происхождения бренда для fallback-логики."""

    origin_type = models.CharField(
        max_length=255, unique=True,
        verbose_name="Тип происхождения",
    )
    fallback_score = models.FloatField(
        default=50, verbose_name="Fallback-балл",
        help_text="Балл по умолчанию для мощности компрессора при отсутствии данных",
    )

    class Meta:
        verbose_name = "Тип происхождения бренда"
        verbose_name_plural = "Типы происхождения брендов"

    def __str__(self) -> str:
        return f"{self.origin_type} ({self.fallback_score})"


class Brand(TimestampMixin):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название")
    logo = models.ImageField(upload_to="brands/", blank=True, default="", verbose_name="Логотип")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    origin_class = models.ForeignKey(
        BrandOriginClass, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="brands", verbose_name="Тип происхождения",
    )
    sales_start_year_ru = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Год начала продаж в РФ",
        help_text="Например: 2015",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"

    def __str__(self) -> str:
        return self.name
