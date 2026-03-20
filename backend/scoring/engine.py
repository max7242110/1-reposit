"""Core scoring engine: Index = Sum(Weight_i * Score_i) / 100 (TZ section 6)."""

from __future__ import annotations

import logging
from typing import Any

from django.db import transaction
from django.utils import timezone

from catalog.models import ACModel, ModelRawValue
from methodology.models import Criterion, MethodologyVersion
from scoring.models import CalculationResult, CalculationRun
from scoring.scorers import SCORER_MAP
from scoring.scorers.base import BaseScorer, ScoreResult
from scoring.scorers.brand_age import BrandAgeScorer
from scoring.scorers.fallback import FallbackScorer
from scoring.scorers.lab import LabScorer

logger = logging.getLogger(__name__)


class WeightValidationError(Exception):
    pass


def validate_weights(methodology: MethodologyVersion) -> None:
    """Validate that sum of weights = 100% (TZ section 6.1)."""
    criteria = Criterion.objects.filter(
        methodology=methodology, is_active=True,
    )
    total = sum(c.weight for c in criteria)
    if abs(total - 100.0) > 0.01:
        raise WeightValidationError(
            f"Сумма весов = {total:.2f}%, должна быть 100%. "
            f"Разница: {total - 100:.2f}%"
        )


def _get_scorer(criterion: Criterion) -> BaseScorer | None:
    """Get the appropriate scorer based on criterion config."""
    if criterion.value_type == Criterion.ValueType.BRAND_AGE:
        return BrandAgeScorer()
    if criterion.value_type == Criterion.ValueType.FALLBACK:
        return FallbackScorer()
    if criterion.value_type == Criterion.ValueType.LAB or criterion.is_lab:
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
    """Build context dict with model-level data for scorers."""
    ctx: dict[str, Any] = {}

    if ac_model.nominal_capacity:
        ctx["nominal_capacity"] = ac_model.nominal_capacity

    brand = ac_model.brand
    if brand.origin_class_id:
        ctx["fallback_score"] = brand.origin_class.fallback_score
    if brand.sales_start_year_ru:
        ctx["sales_start_year_ru"] = brand.sales_start_year_ru

    return ctx


def calculate_model(
    ac_model: ACModel,
    methodology: MethodologyVersion,
    run: CalculationRun,
) -> float:
    """Calculate index for a single model. Returns total_index."""
    criteria = Criterion.objects.filter(
        methodology=methodology, is_active=True,
    )

    raw_values = {
        rv.criterion_id: rv
        for rv in ModelRawValue.objects.filter(model=ac_model).select_related("criterion")
    }

    model_ctx = _build_model_context(ac_model)

    total_index = 0.0
    results: list[CalculationResult] = []

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

        results.append(CalculationResult(
            run=run,
            model=ac_model,
            criterion=criterion,
            raw_value=str(raw),
            normalized_score=round(result.normalized_score, 2),
            weighted_score=round(weighted, 4),
            above_reference=result.above_reference,
        ))

    CalculationResult.objects.bulk_create(results)
    total_index = round(total_index, 2)

    ac_model.total_index = total_index
    ac_model.save(update_fields=["total_index", "updated_at"])

    return total_index


def recalculate_all(
    methodology: MethodologyVersion | None = None,
    user=None,
    model_ids: list[int] | None = None,
) -> CalculationRun:
    """Recalculate index for all (or selected) models."""
    if methodology is None:
        methodology = MethodologyVersion.objects.filter(is_active=True).first()
        if not methodology:
            raise ValueError("Нет активной методики")

    validate_weights(methodology)

    run = CalculationRun.objects.create(
        methodology=methodology,
        triggered_by=user,
        status=CalculationRun.Status.RUNNING,
    )

    try:
        with transaction.atomic():
            qs = ACModel.objects.select_related("brand", "brand__origin_class")
            if model_ids:
                qs = qs.filter(pk__in=model_ids)

            CalculationResult.objects.filter(run=run).delete()

            count = 0
            for ac_model in qs:
                calculate_model(ac_model, methodology, run)
                count += 1

            run.status = CalculationRun.Status.COMPLETED
            run.finished_at = timezone.now()
            run.models_processed = count
            run.save()

            methodology.needs_recalculation = False
            methodology.save(update_fields=["needs_recalculation", "updated_at"])

    except Exception:
        logger.exception("Recalculation failed for run #%s", run.pk)
        run.status = CalculationRun.Status.FAILED
        run.error_message = str(run.pk)
        run.finished_at = timezone.now()
        run.save()
        raise

    return run
