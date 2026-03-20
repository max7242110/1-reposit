"""Fallback scorer using brand origin class for compressor power (TZ 3.0 criterion 3).

When raw_value is provided, it is treated as compressor refrigeration capacity (W)
and compared to the model's nominal_capacity.  The ratio (compressor / catalog * 100)
is scored via interval scale.

When raw_value is missing, a fallback coefficient is applied:
  - Japanese brands: 100 * 0.9 = 90
  - Chinese / OEM brands: 100 * 0.5 = 50
"""

from __future__ import annotations

from typing import Any

from methodology.models import Criterion

from .base import BaseScorer, ScoreResult

DEFAULT_INTERVALS: list[dict[str, float]] = [
    {"from": 0, "to": 80, "score": 15},
    {"from": 80, "to": 90, "score": 50},
    {"from": 90, "to": 95, "score": 70},
    {"from": 95, "to": 100, "score": 90},
    {"from": 100, "to": 999, "score": 100},
]


class FallbackScorer(BaseScorer):
    """Compressor power scorer with brand-origin fallback."""

    def calculate(self, criterion: Criterion, raw_value: Any, **context: Any) -> ScoreResult:
        has_value = raw_value is not None and str(raw_value).strip() != ""

        if has_value:
            return self._score_by_ratio(criterion, raw_value, **context)

        fallback_score = context.get("fallback_score")
        if fallback_score is not None:
            return ScoreResult(normalized_score=float(fallback_score)).clamp()

        return ScoreResult(normalized_score=50)

    def _score_by_ratio(
        self, criterion: Criterion, raw_value: Any, **context: Any,
    ) -> ScoreResult:
        try:
            compressor_w = float(raw_value)
        except (ValueError, TypeError):
            return ScoreResult(normalized_score=0)

        nominal_capacity = context.get("nominal_capacity")
        if not nominal_capacity:
            return ScoreResult(normalized_score=0)

        catalog_w = nominal_capacity * 1000
        ratio = compressor_w / catalog_w * 100

        intervals = (
            criterion.formula_json
            if isinstance(criterion.formula_json, list)
            else DEFAULT_INTERVALS
        )

        for interval in intervals:
            low = float(interval.get("from", 0))
            high = float(interval.get("to", float("inf")))
            if low <= ratio < high:
                return ScoreResult(normalized_score=float(interval["score"])).clamp()

        return ScoreResult(normalized_score=0)
