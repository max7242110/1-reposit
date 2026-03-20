"""Админка типов оборудования."""

from django.contrib import admin

from catalog.models import EquipmentType


@admin.register(EquipmentType)
class EquipmentTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
