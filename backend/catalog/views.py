from __future__ import annotations

import csv
import io
import logging

from django.http import HttpResponse
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from core.i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES
from methodology.models import MethodologyVersion

from .models import ACModel
from .serializers import ACModelDetailSerializer, ACModelListSerializer, MethodologySerializer

logger = logging.getLogger(__name__)


class LangMixin:
    """Add lang to serializer context from query params."""

    def get_serializer_context(self) -> dict:
        ctx = super().get_serializer_context()  # type: ignore[misc]
        lang = self.request.query_params.get("lang", DEFAULT_LANGUAGE)  # type: ignore[attr-defined]
        ctx["lang"] = lang if lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
        return ctx


def _parse_float_param(value: str | None, name: str) -> float | None:
    if not value:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        raise ValidationError({name: f"Неверное числовое значение: {value}"})


class ACModelListView(LangMixin, generics.ListAPIView):
    serializer_class = ACModelListSerializer

    def get_queryset(self):
        qs = ACModel.objects.select_related("brand").prefetch_related("regions").filter(
            publish_status=ACModel.PublishStatus.PUBLISHED,
        ).order_by("-total_index")

        brand = self.request.query_params.get("brand")
        if brand:
            qs = qs.filter(brand__name__icontains=brand)

        region = self.request.query_params.get("region")
        if region:
            qs = qs.filter(regions__region_code=region)

        capacity_min = _parse_float_param(
            self.request.query_params.get("capacity_min"), "capacity_min",
        )
        capacity_max = _parse_float_param(
            self.request.query_params.get("capacity_max"), "capacity_max",
        )
        if capacity_min is not None:
            qs = qs.filter(nominal_capacity__gte=capacity_min)
        if capacity_max is not None:
            qs = qs.filter(nominal_capacity__lte=capacity_max)

        return qs


class ACModelDetailView(LangMixin, generics.RetrieveAPIView):
    serializer_class = ACModelDetailSerializer

    def get_queryset(self):
        return ACModel.objects.select_related("brand").prefetch_related(
            "regions",
            "raw_values__criterion",
            "calculation_results__run__methodology",
            "calculation_results__criterion",
        )


class MethodologyView(LangMixin, generics.RetrieveAPIView):
    serializer_class = MethodologySerializer

    def get_object(self):
        obj = MethodologyVersion.objects.prefetch_related(
            "criteria",
        ).filter(is_active=True).first()
        if obj is None:
            raise NotFound("Активная методика не найдена")
        return obj


class ExportCSVView(generics.GenericAPIView):
    def get(self, request: Request, *args, **kwargs) -> HttpResponse:
        models = ACModel.objects.select_related("brand").filter(
            publish_status=ACModel.PublishStatus.PUBLISHED,
        ).order_by("-total_index")

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["brand", "model", "nominal_capacity", "total_index", "publish_status"])
        for m in models:
            writer.writerow([m.brand.name, m.inner_unit, m.nominal_capacity, m.total_index, m.publish_status])

        response = HttpResponse(output.getvalue(), content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="rating_export.csv"'
        return response
