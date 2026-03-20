from __future__ import annotations

from django.contrib import admin

from .models import Brand, BrandOriginClass


@admin.register(BrandOriginClass)
class BrandOriginClassAdmin(admin.ModelAdmin):
    list_display = ("origin_type", "fallback_score")
    list_editable = ("fallback_score",)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "origin_class", "sales_start_year_ru", "is_active", "created_at")
    list_filter = ("is_active", "origin_class")
    search_fields = ("name",)
    list_per_page = 30
    list_select_related = ("origin_class",)
