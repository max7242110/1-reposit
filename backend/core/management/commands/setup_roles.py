"""Create Django groups with permissions for each role (TZ section 24)."""

from __future__ import annotations

from typing import Any

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from core.roles import ROLES


class Command(BaseCommand):
    help = "Создать роли (группы) и назначить права"

    def handle(self, *args: Any, **options: Any) -> None:
        for role_key, role_def in ROLES.items():
            group, created = Group.objects.get_or_create(name=role_def["name"])
            perms = []
            for perm_codename in role_def["permissions"]:
                app_label, codename = perm_codename.split(".")
                try:
                    perm = Permission.objects.get(
                        content_type__app_label=app_label, codename=codename,
                    )
                    perms.append(perm)
                except Permission.DoesNotExist:
                    self.stderr.write(f"  Permission not found: {perm_codename}")
            group.permissions.set(perms)
            status = "создана" if created else "обновлена"
            self.stdout.write(f"  Роль «{role_def['name']}» {status}: {len(perms)} прав")

        self.stdout.write(self.style.SUCCESS(f"Готово: настроено {len(ROLES)} ролей"))
