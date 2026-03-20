from __future__ import annotations

import pytest

from methodology.models import Criterion, MethodologyVersion
from scoring.scorers.binary import BinaryScorer
from scoring.scorers.brand_age import BrandAgeScorer
from scoring.scorers.categorical import CategoricalScorer
from scoring.scorers.custom_scale import CustomScaleScorer
from scoring.scorers.fallback import FallbackScorer
from scoring.scorers.formula import FormulaScorer
from scoring.scorers.lab import LabScorer
from scoring.scorers.numeric import NumericScorer


@pytest.fixture
def methodology(db):
    return MethodologyVersion.objects.create(version="test", name="Test", is_active=True)


def _make_criterion(methodology, code="test", **kwargs):
    defaults = {
        "name_ru": "Test",
        "value_type": "numeric",
        "scoring_type": "min_median_max",
        "weight": 10,
        "display_order": 1,
        "is_active": True,
    }
    defaults.update(kwargs)
    return Criterion.objects.create(methodology=methodology, code=code, **defaults)


# ── NumericScorer (normal) ────────────────────────────────────────────

@pytest.mark.django_db
class TestNumericScorer:
    def test_at_min(self, methodology):
        c = _make_criterion(methodology, min_value=0, max_value=100, median_value=50)
        assert NumericScorer().calculate(c, "0").normalized_score == 0

    def test_at_max(self, methodology):
        c = _make_criterion(methodology, min_value=0, max_value=100, median_value=50)
        r = NumericScorer().calculate(c, "100")
        assert r.normalized_score == 100
        assert r.above_reference is False

    def test_above_max(self, methodology):
        c = _make_criterion(methodology, min_value=0, max_value=100, median_value=50)
        r = NumericScorer().calculate(c, "120")
        assert r.normalized_score == 100
        assert r.above_reference is True

    def test_at_median(self, methodology):
        c = _make_criterion(methodology, min_value=0, max_value=100, median_value=50)
        r = NumericScorer().calculate(c, "50")
        assert r.normalized_score == 50.0

    def test_between_min_and_median(self, methodology):
        c = _make_criterion(methodology, min_value=0, max_value=100, median_value=50)
        r = NumericScorer().calculate(c, "25")
        assert r.normalized_score == 25.0

    def test_invalid_value(self, methodology):
        c = _make_criterion(methodology, min_value=0, max_value=100)
        assert NumericScorer().calculate(c, "abc").normalized_score == 0

    def test_no_median(self, methodology):
        c = _make_criterion(methodology, min_value=0, max_value=100, median_value=None)
        r = NumericScorer().calculate(c, "50")
        assert r.normalized_score == 50.0


# ── NumericScorer (inverted) ──────────────────────────────────────────

@pytest.mark.django_db
class TestNumericScorerInverted:
    def test_at_min_best(self, methodology):
        c = _make_criterion(methodology, min_value=28, max_value=46, median_value=33,
                            is_inverted=True)
        r = NumericScorer().calculate(c, "28")
        assert r.normalized_score == 100

    def test_at_max_worst(self, methodology):
        c = _make_criterion(methodology, min_value=28, max_value=46, median_value=33,
                            is_inverted=True)
        assert NumericScorer().calculate(c, "46").normalized_score == 0

    def test_at_median(self, methodology):
        c = _make_criterion(methodology, min_value=28, max_value=46, median_value=33,
                            is_inverted=True)
        assert NumericScorer().calculate(c, "33").normalized_score == 50.0

    def test_better_than_median(self, methodology):
        c = _make_criterion(methodology, min_value=28, max_value=46, median_value=33,
                            is_inverted=True)
        r = NumericScorer().calculate(c, "30")
        assert r.normalized_score == pytest.approx(80.0, abs=0.1)

    def test_worse_than_median(self, methodology):
        c = _make_criterion(methodology, min_value=28, max_value=46, median_value=33,
                            is_inverted=True)
        r = NumericScorer().calculate(c, "40")
        assert r.normalized_score == pytest.approx(23.08, abs=0.1)

    def test_below_min_capped_100(self, methodology):
        c = _make_criterion(methodology, min_value=28, max_value=46, median_value=33,
                            is_inverted=True)
        r = NumericScorer().calculate(c, "20")
        assert r.normalized_score == 100
        assert r.above_reference is True


# ── NumericScorer (capacity-dependent median) ─────────────────────────

@pytest.mark.django_db
class TestNumericScorerCapacityMedian:
    def test_picks_closest_capacity(self, methodology):
        c = _make_criterion(
            methodology, min_value=0.1, max_value=0.5, median_value=0.21,
            median_by_capacity={"2.0": 0.18, "2.5": 0.21, "3.5": 0.30},
        )
        r = NumericScorer().calculate(c, "0.21", nominal_capacity=3.5)
        assert r.normalized_score == pytest.approx(27.5, abs=0.1)

    def test_uses_exact_capacity(self, methodology):
        c = _make_criterion(
            methodology, min_value=0.1, max_value=0.5, median_value=0.21,
            median_by_capacity={"2.0": 0.18, "2.5": 0.21, "3.5": 0.30},
        )
        r = NumericScorer().calculate(c, "0.21", nominal_capacity=2.5)
        assert r.normalized_score == 50.0

    def test_falls_back_to_scalar_without_capacity(self, methodology):
        c = _make_criterion(
            methodology, min_value=0.1, max_value=0.5, median_value=0.21,
            median_by_capacity={"2.0": 0.18, "2.5": 0.21, "3.5": 0.30},
        )
        r = NumericScorer().calculate(c, "0.21")
        assert r.normalized_score == 50.0


# ── BinaryScorer ──────────────────────────────────────────────────────

@pytest.mark.django_db
class TestBinaryScorer:
    @pytest.mark.parametrize("val", ["да", "yes", "есть", "1", "true", "+"])
    def test_truthy(self, methodology, val):
        c = _make_criterion(methodology, value_type="binary", scoring_type="binary")
        assert BinaryScorer().calculate(c, val).normalized_score == 100

    @pytest.mark.parametrize("val", ["нет", "no", "0", ""])
    def test_falsy(self, methodology, val):
        c = _make_criterion(methodology, value_type="binary", scoring_type="binary")
        assert BinaryScorer().calculate(c, val).normalized_score == 0


# ── CategoricalScorer ─────────────────────────────────────────────────

@pytest.mark.django_db
class TestCategoricalScorer:
    def test_keyword_match(self, methodology):
        c = _make_criterion(methodology, value_type="categorical", scoring_type="universal_scale")
        assert CategoricalScorer().calculate(c, "нет").normalized_score == 0
        assert CategoricalScorer().calculate(c, "есть").normalized_score == 70

    def test_custom_scale_override(self, methodology):
        c = _make_criterion(
            methodology, value_type="categorical", scoring_type="universal_scale",
            custom_scale_json={"инвертор": 100, "он-офф": 30},
        )
        assert CategoricalScorer().calculate(c, "инвертор").normalized_score == 100


# ── CustomScaleScorer ─────────────────────────────────────────────────

@pytest.mark.django_db
class TestCustomScaleScorer:
    def test_dict_scale(self, methodology):
        c = _make_criterion(
            methodology, scoring_type="custom_scale",
            custom_scale_json={"100В": 100, "150В": 70, "230В": 0},
        )
        assert CustomScaleScorer().calculate(c, "100В").normalized_score == 100
        assert CustomScaleScorer().calculate(c, "230В").normalized_score == 0

    def test_interval_scale(self, methodology):
        c = _make_criterion(
            methodology, scoring_type="custom_scale",
            custom_scale_json=[
                {"from": 0, "to": 80, "score": 15},
                {"from": 80, "to": 95, "score": 70},
                {"from": 95, "to": 999, "score": 100},
            ],
        )
        assert CustomScaleScorer().calculate(c, "50").normalized_score == 15
        assert CustomScaleScorer().calculate(c, "90").normalized_score == 70

    def test_no_scale(self, methodology):
        c = _make_criterion(methodology, scoring_type="custom_scale", custom_scale_json=None)
        assert CustomScaleScorer().calculate(c, "anything").normalized_score == 0


# ── FormulaScorer ─────────────────────────────────────────────────────

@pytest.mark.django_db
class TestFormulaScorer:
    def test_with_intervals(self, methodology):
        c = _make_criterion(
            methodology, scoring_type="formula",
            formula_json=[
                {"from": 0, "to": 50, "score": 0},
                {"from": 50, "to": 100, "score": 100},
            ],
        )
        assert FormulaScorer().calculate(c, "25").normalized_score == 0
        assert FormulaScorer().calculate(c, "75").normalized_score == 100

    def test_no_formula_json(self, methodology):
        c = _make_criterion(methodology, scoring_type="formula", formula_json=None)
        assert FormulaScorer().calculate(c, "50").normalized_score == 0


# ── LabScorer ─────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestLabScorer:
    def test_not_measured(self, methodology):
        c = _make_criterion(methodology, is_lab=True)
        assert LabScorer().calculate(c, "50", lab_status="not_measured").normalized_score == 0

    def test_measured_numeric(self, methodology):
        c = _make_criterion(methodology, is_lab=True, min_value=0, max_value=100)
        r = LabScorer().calculate(c, "50", lab_status="measured")
        assert r.normalized_score == 50.0


# ── FallbackScorer (compressor power) ─────────────────────────────────

@pytest.mark.django_db
class TestFallbackScorer:
    def test_with_value_and_capacity(self, methodology):
        c = _make_criterion(
            methodology, scoring_type="formula", value_type="fallback",
            formula_json=[
                {"from": 0, "to": 80, "score": 15},
                {"from": 80, "to": 90, "score": 50},
                {"from": 90, "to": 95, "score": 70},
                {"from": 95, "to": 100, "score": 90},
                {"from": 100, "to": 999, "score": 100},
            ],
        )
        # compressor 2500W vs 2.5 kW model → ratio = 2500/2500*100 = 100%
        r = FallbackScorer().calculate(c, "2500", nominal_capacity=2.5)
        assert r.normalized_score == 100

    def test_underpowered_compressor(self, methodology):
        c = _make_criterion(
            methodology, scoring_type="formula", value_type="fallback",
            formula_json=[
                {"from": 0, "to": 80, "score": 15},
                {"from": 80, "to": 90, "score": 50},
                {"from": 90, "to": 95, "score": 70},
                {"from": 95, "to": 100, "score": 90},
                {"from": 100, "to": 999, "score": 100},
            ],
        )
        # compressor 2000W vs 2.5 kW → ratio = 80%
        r = FallbackScorer().calculate(c, "2000", nominal_capacity=2.5)
        assert r.normalized_score == 50

    def test_without_value_japanese(self, methodology):
        c = _make_criterion(methodology, scoring_type="formula", value_type="fallback")
        r = FallbackScorer().calculate(c, "", fallback_score=90)
        assert r.normalized_score == 90

    def test_without_value_chinese(self, methodology):
        c = _make_criterion(methodology, scoring_type="formula", value_type="fallback")
        r = FallbackScorer().calculate(c, "", fallback_score=50)
        assert r.normalized_score == 50

    def test_without_value_no_fallback(self, methodology):
        c = _make_criterion(methodology, scoring_type="formula", value_type="fallback")
        r = FallbackScorer().calculate(c, "")
        assert r.normalized_score == 50


# ── BrandAgeScorer ────────────────────────────────────────────────────

@pytest.mark.django_db
class TestBrandAgeScorer:
    def test_oldest_brand(self, methodology):
        c = _make_criterion(
            methodology, code="age", value_type="brand_age",
            min_value=1995, max_value=2026, median_value=2010,
        )
        r = BrandAgeScorer().calculate(c, "", sales_start_year_ru=1995)
        assert r.normalized_score == 100

    def test_brand_new(self, methodology):
        c = _make_criterion(
            methodology, code="age", value_type="brand_age",
            min_value=1995, max_value=2026, median_value=2010,
        )
        r = BrandAgeScorer().calculate(c, "", sales_start_year_ru=2026)
        assert r.normalized_score == 0

    def test_median_year(self, methodology):
        c = _make_criterion(
            methodology, code="age", value_type="brand_age",
            min_value=1995, max_value=2026, median_value=2010,
        )
        r = BrandAgeScorer().calculate(c, "", sales_start_year_ru=2010)
        assert r.normalized_score == 50.0

    def test_older_than_median(self, methodology):
        c = _make_criterion(
            methodology, code="age", value_type="brand_age",
            min_value=1995, max_value=2026, median_value=2010,
        )
        r = BrandAgeScorer().calculate(c, "", sales_start_year_ru=2000)
        assert r.normalized_score == pytest.approx(83.33, abs=0.1)

    def test_no_start_year(self, methodology):
        c = _make_criterion(
            methodology, code="age", value_type="brand_age",
            min_value=1995, max_value=2026,
        )
        r = BrandAgeScorer().calculate(c, "")
        assert r.normalized_score == 0
