from __future__ import annotations

from rest_framework import serializers

from brands.models import Brand
from core.i18n import DEFAULT_LANGUAGE, get_localized_field
from methodology.models import Criterion, MethodologyVersion
from scoring.engine import compute_scores_for_model, max_possible_total_index
from scoring.engine.computation import _build_model_context, _get_scorer
from scoring.models import CalculationResult

from .models import ACModel, ACModelPhoto, ACModelSupplier, ModelRawValue, ModelRegion


class BrandSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ["id", "name", "logo"]
        read_only_fields = ["id", "name"]

    def get_logo(self, obj: Brand) -> str:
        if not obj.logo:
            return ""
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.logo.url)
        return obj.logo.url


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
    criterion_code = serializers.SerializerMethodField()
    criterion_name = serializers.SerializerMethodField()
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

    def get_criterion_code(self, obj: ModelRawValue) -> str:
        if obj.criterion:
            return obj.criterion.code
        return obj.criterion_code

    def get_criterion_name(self, obj: ModelRawValue) -> str:
        if obj.criterion:
            return obj.criterion.name_ru
        return obj.criterion_code


class ACModelPhotoSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ACModelPhoto
        fields = ["id", "image_url", "order"]
        read_only_fields = fields

    def get_image_url(self, obj: ACModelPhoto) -> str:
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        if obj.image:
            return obj.image.url
        return ""


class ACModelSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = ACModelSupplier
        fields = ["id", "name", "url", "order"]
        read_only_fields = fields


class ACModelListSerializer(serializers.ModelSerializer):
    brand = serializers.CharField(source="brand.name", read_only=True)
    brand_logo = serializers.SerializerMethodField()
    region_availability = RegionSerializer(source="regions", many=True, read_only=True)
    index_max = serializers.SerializerMethodField()
    noise_score = serializers.SerializerMethodField()
    has_noise_measurement = serializers.SerializerMethodField()
    scores = serializers.SerializerMethodField()

    class Meta:
        model = ACModel
        fields = [
            "id", "slug", "brand", "brand_logo", "inner_unit", "series",
            "nominal_capacity", "total_index", "index_max",
            "publish_status", "region_availability",
            "price", "noise_score", "has_noise_measurement", "scores",
        ]
        read_only_fields = fields

    def get_brand_logo(self, obj: ACModel) -> str:
        if not obj.brand.logo:
            return ""
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.brand.logo.url)
        return obj.brand.logo.url

    def get_index_max(self, _obj: ACModel) -> float:
        return float(self.context.get("index_max", 100.0))

    def _get_scores_cache(self, obj: ACModel) -> dict:
        if not hasattr(obj, "_scores_cache"):
            criteria = self.context.get("criteria", [])
            if not criteria:
                obj._scores_cache = {}
                return obj._scores_cache

            raw_values_map = {rv.criterion_id: rv for rv in obj.raw_values.all() if rv.criterion_id}
            model_ctx = _build_model_context(obj)
            scores = {}
            for criterion in criteria:
                rv = raw_values_map.get(criterion.pk)
                raw = rv.raw_value if rv else ""
                scorer = _get_scorer(criterion)
                if scorer:
                    ctx = {**model_ctx}
                    if rv:
                        ctx["lab_status"] = rv.lab_status
                    result = scorer.calculate(criterion, raw, **ctx)
                    scores[criterion.code] = round(result.normalized_score, 2)
            obj._scores_cache = scores
        return obj._scores_cache

    def get_scores(self, obj: ACModel) -> dict:
        return self._get_scores_cache(obj)

    def get_noise_score(self, obj: ACModel) -> float | None:
        return self._get_scores_cache(obj).get("noise")

    def get_has_noise_measurement(self, obj: ACModel) -> bool:
        score = self._get_scores_cache(obj).get("noise")
        return score is not None and score > 0


class ACModelDetailSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    region_availability = RegionSerializer(source="regions", many=True, read_only=True)
    parameter_scores = serializers.SerializerMethodField()
    raw_values = RawValueSerializer(many=True, read_only=True)
    methodology_version = serializers.SerializerMethodField()
    index_max = serializers.SerializerMethodField()
    photos = ACModelPhotoSerializer(many=True, read_only=True)
    suppliers = ACModelSupplierSerializer(many=True, read_only=True)

    class Meta:
        model = ACModel
        fields = [
            "id", "slug", "brand", "series", "inner_unit", "outer_unit",
            "nominal_capacity", "total_index", "index_max",
            "publish_status", "region_availability",
            "price", "pros_text", "cons_text",
            "youtube_url", "rutube_url", "vk_url",
            "photos", "suppliers",
            "parameter_scores", "raw_values",
            "methodology_version",
        ]
        read_only_fields = fields

    def _get_methodology_for_detail(self, obj: ACModel) -> MethodologyVersion | None:
        results = list(obj.calculation_results.all())
        if results:
            latest = max(results, key=lambda r: r.run_id)
            return latest.run.methodology
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
                "criterion_note": r["criterion"].note or "",
                "criterion_description": get_localized_field(r["criterion"], "description", lang) or "",
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
            "region_scope", "is_public",
            "display_order",
        ]
        read_only_fields = fields


class MethodologySerializer(serializers.ModelSerializer):
    criteria = CriterionSerializer(many=True, read_only=True)

    class Meta:
        model = MethodologyVersion
        fields = [
            "version", "name", "description", "is_active",
            "tab_description_index", "tab_description_quiet", "tab_description_custom",
            "criteria",
        ]
        read_only_fields = fields
