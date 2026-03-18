from django.contrib import admin

from .models import AirConditioner, ParameterValue


class ParameterValueInline(admin.TabularInline):
    model = ParameterValue
    extra = 0


@admin.register(AirConditioner)
class AirConditionerAdmin(admin.ModelAdmin):
    list_display = ("rank", "brand", "model_name", "total_score")
    list_display_links = ("brand",)
    ordering = ("-total_score",)
    inlines = [ParameterValueInline]


@admin.register(ParameterValue)
class ParameterValueAdmin(admin.ModelAdmin):
    list_display = ("air_conditioner", "parameter_name", "raw_value", "score")
    list_filter = ("parameter_name",)
