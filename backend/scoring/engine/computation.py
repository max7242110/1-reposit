"""Расчёт индекса без записи в БД (кроме вызывающего кода)."""

from __future__ import annotations

import logging
from typing import Any

from catalog.models import ACModel, ModelRawValue
from methodology.models import Criterion, MethodologyVersion
from scoring.scorers import SCORER_MAP
from scoring.scorers.base import BaseScorer, ScoreResult
from scoring.scorers.brand_age import BrandAgeScorer
from scoring.scorers.fallback import FallbackScorer
from scoring.scorers.lab import LabScorer

logger = logging.getLogger(__name__)


def validate_weights(methodology: MethodologyVersion) -> None:
    """Раньше проверяла сумму весов = 100%; ограничение снято — оставлена для совместимости вызовов."""
    return None


def _get_scorer(criterion: Criterion) -> BaseScorer | None:
    if criterion.value_type == Criterion.ValueType.BRAND_AGE:
        return BrandAgeScorer()
    if criterion.value_type == Criterion.ValueType.FALLBACK:
        return FallbackScorer()
    if criterion.value_type == Criterion.ValueType.LAB:
        return LabScorer()

    scorer_class = SCORER_MAP.get(criterion.scoring_type)
    if scorer_class:
        return scorer_class()

    logger.warning(
        "No scorer for criterion %s (type=%s, scoring=%s)",
        criterion.code, criterion.value_type, criterion.scoring_type,
    )
    return None


def _build_model_context(ac_model: ACModel) -> dict[str, Any]:
    ctx: dict[str, Any] = {}

    if ac_model.nominal_capacity:
        ctx["nominal_capacity"] = ac_model.nominal_capacity

    brand = ac_model.brand
    if brand.origin_class_id:
        ctx["fallback_score"] = brand.origin_class.fallback_score
    if brand.sales_start_year_ru:
        ctx["sales_start_year_ru"] = brand.sales_start_year_ru

    return ctx


def max_possible_total_index(methodology: MethodologyVersion | None) -> float:
    """
    Верхняя граница итогового индекса: сумма весов активных критериев,
    по которым есть скорер (при normalized_score = 100 для каждого).
    """
    if methodology is None:
        return 100.0
    criteria = Criterion.objects.filter(
        methodology=methodology, is_active=True,
    ).order_by("display_order", "code")
    total = 0.0
    for criterion in criteria:
        if _get_scorer(criterion):
            total += float(criterion.weight)
    return round(total, 2)


def compute_scores_for_model(
    ac_model: ACModel,
    methodology: MethodologyVersion,
) -> tuple[float, list[dict[str, Any]]]:
    """
    Считает итоговый индекс и разбивку по критериям.
    Без записи в БД. Пустой raw_value — как у соответствующих скореров (часто 0).
    """
    criteria = Criterion.objects.filter(
        methodology=methodology, is_active=True,
    ).order_by("display_order", "code")

    raw_values = {
        rv.criterion_id: rv
        for rv in ModelRawValue.objects.filter(
            model=ac_model, criterion__isnull=False,
        ).select_related("criterion")
    }

    model_ctx = _build_model_context(ac_model)

    total_index = 0.0
    rows: list[dict[str, Any]] = []

    for criterion in criteria:
        rv = raw_values.get(criterion.pk)
        raw = rv.raw_value if rv else ""

        scorer = _get_scorer(criterion)
        if not scorer:
            continue

        context: dict[str, Any] = {**model_ctx}
        if rv:
            context["lab_status"] = rv.lab_status

        result: ScoreResult = scorer.calculate(criterion, raw, **context)

        weighted = round(criterion.weight * result.normalized_score / 100, 4)
        total_index += weighted

        rows.append({
            "criterion": criterion,
            "raw_value": str(raw),
            "compressor_model": rv.compressor_model if rv else "",
            "normalized_score": round(result.normalized_score, 2),
            "weighted_score": round(weighted, 4),
            "above_reference": result.above_reference,
        })

    return round(total_index, 2), rows
