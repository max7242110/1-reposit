from __future__ import annotations

import math

from django.db import models

from brands.models import Brand
from catalog.models import ACModel
from core.models import TimestampMixin


class ACSubmission(TimestampMixin):
    class Status(models.TextChoices):
        PENDING = "pending", "На рассмотрении"
        APPROVED = "approved", "Одобрена"
        REJECTED = "rejected", "Отклонена"

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING,
        db_index=True, verbose_name="Статус",
    )

    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="submissions", verbose_name="Бренд",
    )
    custom_brand_name = models.CharField(
        max_length=255, blank=True, default="",
        verbose_name="Бренд (если нет в списке)",
    )
    series = models.CharField(
        max_length=255, blank=True, default="", verbose_name="Серия",
    )
    inner_unit = models.CharField(max_length=255, verbose_name="Модель внутреннего блока")
    outer_unit = models.CharField(max_length=255, verbose_name="Модель наружного блока")
    compressor_model = models.CharField(max_length=255, verbose_name="Модель компрессора")
    nominal_capacity_watt = models.PositiveIntegerField(
        verbose_name="Номинальная холодопроизводительность (Вт)",
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Цена (руб.)",
    )

    drain_pan_heater = models.CharField(
        max_length=50, verbose_name="Обогрев поддона",
    )
    erv = models.BooleanField(verbose_name="Наличие ЭРВ")
    fan_speed_outdoor = models.BooleanField(
        verbose_name="Регулировка оборотов вент. наруж. блока",
    )
    remote_backlight = models.BooleanField(verbose_name="Подсветка экрана пульта")

    fan_speeds_indoor = models.PositiveSmallIntegerField(
        verbose_name="Кол-во скоростей вент. внутр. блока",
    )
    fine_filters = models.PositiveSmallIntegerField(
        verbose_name="Кол-во фильтров тонкой очистки",
    )
    ionizer_type = models.CharField(
        max_length=100, verbose_name="Тип ионизатора",
    )
    russian_remote = models.CharField(
        max_length=100, verbose_name="Русифицированный пульт ДУ",
    )
    uv_lamp = models.CharField(max_length=100, verbose_name="УФ-лампа")

    inner_he_length_mm = models.FloatField(
        verbose_name="Длина теплообменника внутр. блока (мм)",
    )
    inner_he_tube_count = models.PositiveIntegerField(
        verbose_name="Кол-во трубок теплообменника внутр. блока",
    )
    inner_he_tube_diameter_mm = models.FloatField(
        verbose_name="Диаметр трубок теплообменника внутр. блока (мм)",
    )
    inner_he_surface_area = models.FloatField(
        editable=False, default=0,
        verbose_name="Площадь труб теплообменника внутр. блока (м²)",
    )

    outer_he_length_mm = models.FloatField(
        verbose_name="Длина теплообменника наруж. блока (мм)",
    )
    outer_he_tube_count = models.PositiveIntegerField(
        verbose_name="Кол-во трубок теплообменника наруж. блока",
    )
    outer_he_tube_diameter_mm = models.FloatField(
        verbose_name="Диаметр трубок теплообменника наруж. блока (мм)",
    )
    outer_he_thickness_mm = models.FloatField(
        verbose_name="Толщина теплообменника наруж. блока (мм)",
    )
    outer_he_surface_area = models.FloatField(
        editable=False, default=0,
        verbose_name="Площадь труб теплообменника наруж. блока (м²)",
    )

    video_url = models.URLField(
        max_length=512, blank=True, default="",
        verbose_name="Ссылка на видео измерений",
    )
    buy_url = models.URLField(
        max_length=512, blank=True, default="",
        verbose_name="Где купить (ссылка)",
    )
    supplier_url = models.URLField(
        max_length=512, blank=True, default="",
        verbose_name="Сайт поставщика",
    )

    submitter_email = models.EmailField(verbose_name="E-mail отправителя")
    consent = models.BooleanField(
        default=False,
        verbose_name="Согласие на обработку персональных данных",
    )

    ip_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name="IP-адрес",
    )
    admin_notes = models.TextField(
        blank=True, default="", verbose_name="Заметки администратора",
    )
    converted_model = models.ForeignKey(
        ACModel, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="source_submission", verbose_name="Созданная модель",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Заявка на добавление кондиционера"
        verbose_name_plural = "Заявки на добавление кондиционеров"

    def _compute_surface_areas(self) -> None:
        self.inner_he_surface_area = round(
            math.pi
            * self.inner_he_tube_diameter_mm
            * self.inner_he_length_mm
            * self.inner_he_tube_count
            / 1_000_000,
            4,
        )
        self.outer_he_surface_area = round(
            math.pi
            * self.outer_he_tube_diameter_mm
            * self.outer_he_length_mm
            * self.outer_he_tube_count
            / 1_000_000,
            4,
        )

    def save(self, *args, **kwargs):
        self._compute_surface_areas()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        brand = self.brand.name if self.brand else self.custom_brand_name
        return f"{brand} {self.inner_unit} ({self.get_status_display()})"


class SubmissionPhoto(TimestampMixin):
    submission = models.ForeignKey(
        ACSubmission, on_delete=models.CASCADE, related_name="photos",
        verbose_name="Заявка",
    )
    image = models.ImageField(upload_to="submissions/", verbose_name="Фото")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Фото заявки"
        verbose_name_plural = "Фото заявок"

    def __str__(self) -> str:
        return f"Фото #{self.order} к заявке {self.submission_id}"
