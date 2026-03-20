from __future__ import annotations

from rest_framework import serializers

from brands.models import Brand
from core.i18n import get_localized_field
from methodology.models import Criterion, MethodologyVersion
from scoring.models import CalculationResult

from .models import ACModel, ModelRawValue, ModelRegion


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name"]
        read_only_fields = fields


class RegionSerializer(serializers.ModelSerializer):
    region_display = serializers.CharField(source="get_region_code_display", read_only=True)

    class Meta:
        model = ModelRegion
        fields = ["region_code", "region_display"]
        read_only_fields = fields


class ParameterScoreSerializer(serializers.ModelSerializer):
    criterion_code = serializers.CharField(source="criterion.code", read_only=True)
    criterion_name = serializers.CharField(source="criterion.name_ru", read_only=True)
    unit = serializers.CharField(source="criterion.unit", read_only=True)

    class Meta:
        model = CalculationResult
        fields = [
            "criterion_code", "criterion_name", "unit",
            "raw_value", "normalized_score", "weighted_score", "above_reference",
        ]
        read_only_fields = fields


class RawValueSerializer(serializers.ModelSerializer):
    criterion_code = serializers.CharField(source="criterion.code", read_only=True)
    criterion_name = serializers.CharField(source="criterion.name_ru", read_only=True)
    verification_display = serializers.CharField(source="get_verification_status_display", read_only=True)

    class Meta:
        model = ModelRawValue
        fields = [
            "criterion_code", "criterion_name",
            "raw_value", "numeric_value",
            "source", "source_url",
            "verification_status", "verification_display",
        ]
        read_only_fields = fields


class ACModelListSerializer(serializers.ModelSerializer):
    brand = serializers.CharField(source="brand.name", read_only=True)
    region_availability = RegionSerializer(source="regions", many=True, read_only=True)

    class Meta:
        model = ACModel
        fields = [
            "id", "brand", "inner_unit", "series",
            "nominal_capacity", "total_index",
            "publish_status", "region_availability",
        ]
        read_only_fields = fields


class ACModelDetailSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    region_availability = RegionSerializer(source="regions", many=True, read_only=True)
    parameter_scores = serializers.SerializerMethodField()
    raw_values = RawValueSerializer(many=True, read_only=True)
    methodology_version = serializers.SerializerMethodField()

    class Meta:
        model = ACModel
        fields = [
            "id", "brand", "series", "inner_unit", "outer_unit",
            "nominal_capacity", "total_index",
            "publish_status", "region_availability",
            "youtube_url", "rutube_url", "vk_url",
            "parameter_scores", "raw_values",
            "methodology_version",
        ]
        read_only_fields = fields

    def _get_latest_run_id(self, obj: ACModel) -> int | None:
        results = list(obj.calculation_results.all())
        if not results:
            return None
        return max(results, key=lambda r: r.run_id).run_id

    def get_parameter_scores(self, obj: ACModel) -> list[dict]:
        run_id = self._get_latest_run_id(obj)
        if run_id is None:
            return []
        results = [
            r for r in obj.calculation_results.all() if r.run_id == run_id
        ]
        results.sort(key=lambda r: r.criterion.display_order)
        return ParameterScoreSerializer(results, many=True).data

    def get_methodology_version(self, obj: ACModel) -> str | None:
        run_id = self._get_latest_run_id(obj)
        if run_id is None:
            return None
        for r in obj.calculation_results.all():
            if r.run_id == run_id:
                return r.run.methodology.version
        return None


class CriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Criterion
        fields = [
            "code", "name_ru", "name_en", "description_ru",
            "unit", "value_type", "scoring_type", "weight",
            "min_value", "median_value", "max_value",
            "is_lab", "region_scope", "is_public",
            "display_order",
        ]
        read_only_fields = fields


class MethodologySerializer(serializers.ModelSerializer):
    criteria = CriterionSerializer(many=True, read_only=True)

    class Meta:
        model = MethodologyVersion
        fields = ["version", "name", "description", "is_active", "criteria"]
        read_only_fields = fields
