from __future__ import annotations

from django.db import models


class AirConditioner(models.Model):
    rank = models.PositiveIntegerField(verbose_name="Позиция в рейтинге")
    brand = models.CharField(max_length=255, verbose_name="Бренд / Название")
    model_name = models.CharField(max_length=512, verbose_name="Модель")
    youtube_url = models.URLField(max_length=512, blank=True, default="")
    rutube_url = models.URLField(max_length=512, blank=True, default="")
    vk_url = models.URLField(max_length=512, blank=True, default="")
    total_score = models.FloatField(default=0, db_index=True, verbose_name="Итоговый балл")

    class Meta:
        ordering = ["-total_score"]
        verbose_name = "Кондиционер"
        verbose_name_plural = "Кондиционеры"

    def __str__(self) -> str:
        return f"{self.brand} {self.model_name}"


class ParameterValue(models.Model):
    air_conditioner = models.ForeignKey(
        AirConditioner,
        on_delete=models.CASCADE,
        related_name="parameters",
    )
    parameter_name = models.CharField(
        max_length=255, db_index=True, verbose_name="Параметр"
    )
    raw_value = models.CharField(max_length=255, verbose_name="Значение")
    unit = models.CharField(max_length=50, blank=True, default="", verbose_name="Ед. измерения")
    score = models.FloatField(default=0, verbose_name="Баллы (индекс)")

    class Meta:
        ordering = ["id"]
        verbose_name = "Значение параметра"
        verbose_name_plural = "Значения параметров"
        constraints = [
            models.UniqueConstraint(
                fields=["air_conditioner", "parameter_name"],
                name="unique_ac_parameter",
            )
        ]

    def __str__(self) -> str:
        return f"{self.parameter_name}: {self.raw_value} ({self.score} б.)"
