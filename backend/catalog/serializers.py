from __future__ import annotations

from rest_framework import serializers

from brands.models import Brand
from core.i18n import DEFAULT_LANGUAGE, get_localized_field
from methodology.models import Criterion, MethodologyVersion
from scoring.engine import compute_scores_for_model, max_possible_total_index
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
    index_max = serializers.SerializerMethodField()

    class Meta:
        model = ACModel
        fields = [
            "id", "brand", "inner_unit", "series",
            "nominal_capacity", "total_index", "index_max",
            "publish_status", "region_availability",
        ]
        read_only_fields = fields

    def get_index_max(self, _obj: ACModel) -> float:
        return float(self.context.get("index_max", 100.0))


class ACModelDetailSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    region_availability = RegionSerializer(source="regions", many=True, read_only=True)
    parameter_scores = serializers.SerializerMethodField()
    raw_values = RawValueSerializer(many=True, read_only=True)
    methodology_version = serializers.SerializerMethodField()
    index_max = serializers.SerializerMethodField()

    class Meta:
        model = ACModel
        fields = [
            "id", "brand", "series", "inner_unit", "outer_unit",
            "nominal_capacity", "total_index", "index_max",
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

    def _get_methodology_for_detail(self, obj: ACModel) -> MethodologyVersion | None:
        run_id = self._get_latest_run_id(obj)
        if run_id is not None:
            for r in obj.calculation_results.all():
                if r.run_id == run_id:
                    return r.run.methodology
        return MethodologyVersion.objects.filter(is_active=True).first()

    def get_parameter_scores(self, obj: ACModel) -> list[dict]:
        methodology = self._get_methodology_for_detail(obj)
        if methodology is None:
            return []
        _total, rows = compute_scores_for_model(obj, methodology)
        lang = self.context.get("lang") or DEFAULT_LANGUAGE
        rows.sort(key=lambda r: (r["criterion"].display_order, r["criterion"].code))
        return [
            {
                "criterion_code": r["criterion"].code,
                "criterion_name": get_localized_field(r["criterion"], "name", lang),
                "criterion_note": r["criterion"].note if r["criterion"].show_note_on_site else "",
                "compressor_model": (r.get("compressor_model") or "").strip(),
                "unit": r["criterion"].unit or "",
                "raw_value": r["raw_value"],
                "normalized_score": r["normalized_score"],
                "weighted_score": r["weighted_score"],
                "above_reference": r["above_reference"],
            }
            for r in rows
        ]

    def get_methodology_version(self, obj: ACModel) -> str | None:
        methodology = self._get_methodology_for_detail(obj)
        return methodology.version if methodology else None

    def get_index_max(self, obj: ACModel) -> float:
        return float(max_possible_total_index(self._get_methodology_for_detail(obj)))


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
