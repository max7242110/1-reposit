from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from core.models import TimestampMixin


class MethodologyVersion(TimestampMixin):
    version = models.CharField(max_length=30, unique=True, verbose_name="Версия")
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(blank=True, default="", verbose_name="Описание")
    is_active = models.BooleanField(
        default=False, verbose_name="Активна",
        help_text="Только одна методика может быть активной",
    )
    needs_recalculation = models.BooleanField(
        default=False, verbose_name="Требуется пересчёт",
        help_text="Устанавливается при изменении весов или формул",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Версия методики"
        verbose_name_plural = "Версии методики"

    def __str__(self) -> str:
        active = " [АКТИВНА]" if self.is_active else ""
        return f"{self.name} (v{self.version}){active}"

    def save(self, *args, **kwargs):
        if self.is_active:
            MethodologyVersion.objects.filter(is_active=True).exclude(pk=self.pk).update(
                is_active=False
            )
        super().save(*args, **kwargs)


class CriterionGroup(TimestampMixin):
    """Deprecated: kept for migration compatibility only."""
    methodology = models.ForeignKey(
        MethodologyVersion, on_delete=models.CASCADE, related_name="groups",
        verbose_name="Методика",
    )
    name_ru = models.CharField(max_length=255, verbose_name="Название (RU)")
    name_en = models.CharField(max_length=255, blank=True, default="", verbose_name="Название (EN)")
    name_de = models.CharField(max_length=255, blank=True, default="", verbose_name="Название (DE)")
    name_pt = models.CharField(max_length=255, blank=True, default="", verbose_name="Название (PT)")
    display_order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")

    class Meta:
        ordering = ["display_order"]
        verbose_name = "Группа критериев"
        verbose_name_plural = "Группы критериев"

    def __str__(self) -> str:
        return self.name_ru


class Criterion(TimestampMixin):
    class ValueType(models.TextChoices):
        NUMERIC = "numeric", "Числовой"
        BINARY = "binary", "Бинарный (да/нет)"
        CATEGORICAL = "categorical", "Категориальный"
        CUSTOM_SCALE = "custom_scale", "Индивидуальная шкала"
        FORMULA = "formula", "Формульная логика"
        LAB = "lab", "Лабораторный"
        FALLBACK = "fallback", "С fallback-логикой"
        BRAND_AGE = "brand_age", "Возраст бренда в РФ"

    class ScoringType(models.TextChoices):
        MIN_MEDIAN_MAX = "min_median_max", "Min / Median / Max"
        BINARY = "binary", "Бинарный (0 или 100)"
        UNIVERSAL_SCALE = "universal_scale", "Универсальная шкала (100/70/50/30/0)"
        CUSTOM_SCALE = "custom_scale", "Индивидуальная шкала (JSON)"
        FORMULA = "formula", "Формула (JSON)"
        INTERVAL = "interval", "Интервальная шкала"

    class RegionScope(models.TextChoices):
        GLOBAL = "global", "Глобальный"
        RU = "ru", "Только Россия"
        EU = "eu", "Только Европа"

    methodology = models.ForeignKey(
        MethodologyVersion, on_delete=models.CASCADE, related_name="criteria",
        verbose_name="Методика",
    )
    group = models.ForeignKey(
        CriterionGroup, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="criteria", verbose_name="Группа (устар.)",
    )
    code = models.CharField(
        max_length=50, verbose_name="Код",
        help_text="Уникальный код параметра в рамках методики, напр. noise_min",
    )

    name_ru = models.CharField(max_length=255, verbose_name="Название (RU)")
    name_en = models.CharField(max_length=255, blank=True, default="", verbose_name="Название (EN)")
    name_de = models.CharField(max_length=255, blank=True, default="", verbose_name="Название (DE)")
    name_pt = models.CharField(max_length=255, blank=True, default="", verbose_name="Название (PT)")

    description_ru = models.TextField(blank=True, default="", verbose_name="Описание (RU)")
    description_en = models.TextField(blank=True, default="", verbose_name="Описание (EN)")
    description_de = models.TextField(blank=True, default="", verbose_name="Описание (DE)")
    description_pt = models.TextField(blank=True, default="", verbose_name="Описание (PT)")

    unit = models.CharField(max_length=50, blank=True, default="", verbose_name="Ед. измерения")

    value_type = models.CharField(
        max_length=30, choices=ValueType.choices, verbose_name="Тип значения",
    )
    scoring_type = models.CharField(
        max_length=30, choices=ScoringType.choices, verbose_name="Тип скоринга",
    )

    weight = models.FloatField(
        default=0, verbose_name="Вес (%)",
        help_text="Вес параметра в процентах. Сумма весов всех параметров = 100%",
    )

    min_value = models.FloatField(null=True, blank=True, verbose_name="Min")
    median_value = models.FloatField(null=True, blank=True, verbose_name="Медиана")
    max_value = models.FloatField(null=True, blank=True, verbose_name="Max")

    is_inverted = models.BooleanField(
        default=False, verbose_name="Инвертированная шкала",
        help_text="Если включено: min = хорошо (100), max = плохо (0). Для шума, вибрации и т.п.",
    )
    median_by_capacity = models.JSONField(
        null=True, blank=True, verbose_name="Медианы по мощности (JSON)",
        help_text='Формат: {"2.0": 0.18, "2.5": 0.21, "3.5": 0.30}. '
                  'Ключ — номинальная мощность кВт, значение — медиана.',
    )

    custom_scale_json = models.JSONField(
        null=True, blank=True, verbose_name="Индивидуальная шкала (JSON)",
        help_text='Формат: {"значение": балл, ...} или [{"from": x, "to": y, "score": z}, ...]',
    )
    formula_json = models.JSONField(
        null=True, blank=True, verbose_name="Формула (JSON)",
        help_text="Описание формулы расчёта для формульных параметров",
    )

    is_lab = models.BooleanField(default=False, verbose_name="Лабораторный параметр")
    is_required_lab = models.BooleanField(default=False, verbose_name="Обязателен для LAB режима")
    is_required_checklist = models.BooleanField(default=False, verbose_name="Обязателен для CHECKLIST")
    is_required_catalog = models.BooleanField(default=False, verbose_name="Обязателен для CATALOG")

    use_in_lab = models.BooleanField(default=True, verbose_name="Используется в LAB")
    use_in_checklist = models.BooleanField(default=True, verbose_name="Используется в CHECKLIST")
    use_in_catalog = models.BooleanField(default=True, verbose_name="Используется в CATALOG")

    region_scope = models.CharField(
        max_length=10, choices=RegionScope.choices, default=RegionScope.GLOBAL,
        verbose_name="Регион",
    )
    note = models.TextField(blank=True, default="", verbose_name="Примечание")
    show_note_on_site = models.BooleanField(default=False, verbose_name="Отображать на сайте")
    is_public = models.BooleanField(default=True, verbose_name="Публичный")
    display_order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        ordering = ["display_order"]
        verbose_name = "Параметр"
        verbose_name_plural = "Параметры"
        constraints = [
            models.UniqueConstraint(
                fields=["methodology", "code"],
                name="unique_criterion_code_per_methodology",
            ),
            models.CheckConstraint(
                condition=models.Q(weight__gte=0),
                name="criterion_weight_non_negative",
            ),
        ]

    def clean(self):
        super().clean()
        if self.weight < 0:
            raise ValidationError({"weight": "Вес не может быть отрицательным."})
        if self.min_value is not None and self.max_value is not None:
            if self.min_value > self.max_value:
                raise ValidationError({"min_value": "min_value не может быть больше max_value."})
        if self.median_value is not None:
            if self.min_value is not None and self.median_value < self.min_value:
                raise ValidationError({"median_value": "median_value не может быть меньше min_value."})
            if self.max_value is not None and self.median_value > self.max_value:
                raise ValidationError({"median_value": "median_value не может быть больше max_value."})

    def __str__(self) -> str:
        return f"{self.name_ru} ({self.weight}%)"
