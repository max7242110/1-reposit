from __future__ import annotations

from django.db import models


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        abstract = True


class Page(TimestampMixin):
    """Простая текстовая страница, редактируемая через админку."""

    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL-slug")
    title_ru = models.CharField(max_length=255, verbose_name="Заголовок")
    content_ru = models.TextField(verbose_name="Контент (HTML)", help_text="Поддерживает HTML-разметку")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Страница"
        verbose_name_plural = "Страницы"

    def __str__(self) -> str:
        return self.title_ru
