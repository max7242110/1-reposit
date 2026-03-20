"""Audit log system for tracking all changes (TZ section 17)."""

from __future__ import annotations

from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = "create", "Создание"
        UPDATE = "update", "Изменение"
        DELETE = "delete", "Удаление"
        CALCULATE = "calculate", "Расчёт"

    entity_type = models.CharField(max_length=100, db_index=True, verbose_name="Тип сущности")
    entity_id = models.PositiveIntegerField(db_index=True, verbose_name="ID сущности")
    action = models.CharField(max_length=20, choices=Action.choices, verbose_name="Действие")
    field_name = models.CharField(max_length=100, blank=True, default="", verbose_name="Поле")
    old_value = models.TextField(blank=True, default="", verbose_name="Старое значение")
    new_value = models.TextField(blank=True, default="", verbose_name="Новое значение")
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Кто изменил",
    )
    changed_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Когда")
    comment = models.TextField(blank=True, default="", verbose_name="Комментарий")

    class Meta:
        ordering = ["-changed_at"]
        verbose_name = "Запись аудит-лога"
        verbose_name_plural = "Аудит-лог"
        indexes = [
            models.Index(fields=["entity_type", "entity_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.get_action_display()} {self.entity_type}#{self.entity_id} — {self.field_name}"

    @classmethod
    def log_change(
        cls,
        entity: models.Model,
        action: str,
        field_name: str = "",
        old_value: str = "",
        new_value: str = "",
        user=None,
        comment: str = "",
    ) -> "AuditLog":
        return cls.objects.create(
            entity_type=entity.__class__.__name__,
            entity_id=entity.pk,
            action=action,
            field_name=field_name,
            old_value=str(old_value),
            new_value=str(new_value),
            changed_by=user,
            comment=comment,
        )

    @classmethod
    def log_model_changes(cls, instance: models.Model, old_data: dict, user=None) -> list["AuditLog"]:
        """Compare old_data dict with current instance fields and log all changes."""
        logs = []
        for field_name, old_val in old_data.items():
            new_val = getattr(instance, field_name, None)
            if str(old_val) != str(new_val):
                logs.append(cls.log_change(
                    entity=instance,
                    action=cls.Action.UPDATE,
                    field_name=field_name,
                    old_value=old_val,
                    new_value=new_val,
                    user=user,
                ))
        return logs
