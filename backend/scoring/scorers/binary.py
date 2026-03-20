"""Binary scorer: yes -> 100, no -> 0."""

from __future__ import annotations

from typing import Any

from methodology.models import Criterion

from .base import BaseScorer, ScoreResult

TRUTHY = {"да", "yes", "есть", "1", "true", "+"}


class BinaryScorer(BaseScorer):
    def calculate(self, criterion: Criterion, raw_value: Any, **context: Any) -> ScoreResult:
        val = str(raw_value).strip().lower()
        score = 100.0 if val in TRUTHY else 0.0
        return ScoreResult(normalized_score=score)
