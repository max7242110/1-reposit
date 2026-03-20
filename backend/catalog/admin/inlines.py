"""Инлайны для ACModel в админке."""

from __future__ import annotations

from django.contrib import admin

from catalog.models import ModelRawValue, ModelRegion

from .forms import RawValueFormSet


class ModelRegionInline(admin.TabularInline):
    model = ModelRegion
    extra = 0


class ModelRawValueInline(admin.TabularInline):
    model = ModelRawValue
    formset = RawValueFormSet
    extra = 0
    fields = ("criterion", "raw_value", "verification_status", "source")
    readonly_fields = ("criterion",)
    ordering = ("criterion__display_order",)
    can_delete = False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("criterion", "model__brand")

    def has_add_permission(self, request, obj=None):
        return False
