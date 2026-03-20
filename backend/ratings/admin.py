from __future__ import annotations

from django.contrib import admin

from .models import AirConditioner, ParameterValue


class ParameterValueInline(admin.TabularInline):
    model = ParameterValue
    extra = 0
    readonly_fields = ("parameter_name", "raw_value", "unit", "score")


@admin.register(AirConditioner)
class AirConditionerAdmin(admin.ModelAdmin):
    list_display = ("rank", "brand", "model_name", "total_score")
    list_display_links = ("brand",)
    search_fields = ("brand", "model_name")
    list_filter = ("total_score",)
    list_per_page = 30
    ordering = ("-total_score",)
    inlines = [ParameterValueInline]


@admin.register(ParameterValue)
class ParameterValueAdmin(admin.ModelAdmin):
    list_display = ("air_conditioner", "parameter_name", "raw_value", "score")
    list_filter = ("parameter_name",)
    list_select_related = ("air_conditioner",)
    search_fields = ("air_conditioner__brand", "air_conditioner__model_name")
    list_per_page = 50
