from __future__ import annotations

import pytest

from brands.models import Brand, BrandOriginClass
from catalog.models import ACModel, EquipmentType, ModelRawValue
from methodology.models import Criterion, MethodologyVersion
from catalog.sync_brand_age import sync_brand_age_for_model
from scoring.engine import recalculate_all, update_model_total_index, validate_weights
from scoring.models import CalculationResult, CalculationRun


@pytest.fixture
def methodology(db):
    return MethodologyVersion.objects.create(version="test", name="Test", is_active=True)


@pytest.fixture
def brand(db):
    return Brand.objects.create(name="TestBrand")


@pytest.fixture
def eq_type(db):
    return EquipmentType.objects.create(name="Сплит")


@pytest.fixture
def ac_model(brand, eq_type):
    return ACModel.objects.create(
        brand=brand, inner_unit="Model-X", equipment_type=eq_type,
        nominal_capacity=2.5,
    )


@pytest.mark.django_db
class TestWeightValidation:
    def test_valid_weights(self, methodology):
        Criterion.objects.create(
            methodology=methodology, code="a", name_ru="A",
            value_type="binary", scoring_type="binary", weight=60, display_order=1,
        )
        Criterion.objects.create(
            methodology=methodology, code="b", name_ru="B",
            value_type="binary", scoring_type="binary", weight=40, display_order=2,
        )
        validate_weights(methodology)


@pytest.mark.django_db
class TestRecalculateAll:
    def test_basic_calculation(self, methodology, ac_model):
        c1 = Criterion.objects.create(
            methodology=methodology, code="noise", name_ru="Шум",
            value_type="numeric", scoring_type="min_median_max",
            weight=50, min_value=20, median_value=30, max_value=40,
            display_order=1,
        )
        c2 = Criterion.objects.create(
            methodology=methodology, code="erv", name_ru="ЭРВ",
            value_type="binary", scoring_type="binary",
            weight=50, display_order=2,
        )
        ModelRawValue.objects.create(model=ac_model, criterion=c1, raw_value="30")
        ModelRawValue.objects.create(model=ac_model, criterion=c2, raw_value="да")

        run = recalculate_all()
        ac_model.refresh_from_db()

        assert run.status == CalculationRun.Status.COMPLETED
        assert run.models_processed == 1
        assert CalculationResult.objects.filter(run=run).count() == 2

        noise_result = CalculationResult.objects.get(run=run, criterion=c1)
        assert noise_result.normalized_score == 50.0
        assert noise_result.weighted_score == pytest.approx(25.0, abs=0.01)

        erv_result = CalculationResult.objects.get(run=run, criterion=c2)
        assert erv_result.normalized_score == 100.0

        assert ac_model.total_index == pytest.approx(75.0, abs=0.01)

    def test_no_active_methodology(self, db):
        MethodologyVersion.objects.filter(is_active=True).update(is_active=False)
        with pytest.raises(ValueError, match="активной методики"):
            recalculate_all()

    def test_selected_models(self, methodology, ac_model, brand, eq_type):
        c = Criterion.objects.create(
            methodology=methodology, code="x", name_ru="X",
            value_type="binary", scoring_type="binary",
            weight=100, display_order=1,
        )
        other = ACModel.objects.create(brand=brand, inner_unit="Other", equipment_type=eq_type)
        ModelRawValue.objects.create(model=ac_model, criterion=c, raw_value="да")

        run = recalculate_all(model_ids=[ac_model.pk])
        assert run.models_processed == 1

    def test_inverted_noise(self, methodology, ac_model):
        c = Criterion.objects.create(
            methodology=methodology, code="noise_inv", name_ru="Шум (инв.)",
            value_type="numeric", scoring_type="min_median_max",
            weight=100, min_value=28, median_value=33, max_value=46,
            is_inverted=True, display_order=1,
        )
        ModelRawValue.objects.create(model=ac_model, criterion=c, raw_value="30")

        run = recalculate_all()
        result = CalculationResult.objects.get(run=run, criterion=c)
        assert result.normalized_score == pytest.approx(80.0, abs=0.1)

    def test_capacity_dependent_median(self, methodology, ac_model):
        c = Criterion.objects.create(
            methodology=methodology, code="hx_inner", name_ru="Теплообменник",
            value_type="numeric", scoring_type="min_median_max",
            weight=100, min_value=0.1, max_value=0.5, median_value=0.21,
            median_by_capacity={"2.0": 0.18, "2.5": 0.21, "3.5": 0.30},
            display_order=1,
        )
        ModelRawValue.objects.create(model=ac_model, criterion=c, raw_value="0.21")

        run = recalculate_all()
        result = CalculationResult.objects.get(run=run, criterion=c)
        assert result.normalized_score == 50.0

    def test_fallback_compressor_with_origin(self, methodology, eq_type):
        origin, _ = BrandOriginClass.objects.get_or_create(
            origin_type="japanese", defaults={"fallback_score": 90},
        )
        jp_brand = Brand.objects.create(name="JapanBrand", origin_class=origin)
        model = ACModel.objects.create(
            brand=jp_brand, inner_unit="JP-Model", equipment_type=eq_type,
            nominal_capacity=2.5,
        )
        c = Criterion.objects.create(
            methodology=methodology, code="comp", name_ru="Компрессор",
            value_type="fallback", scoring_type="formula",
            weight=100, display_order=1,
            formula_json=[
                {"from": 0, "to": 80, "score": 15},
                {"from": 80, "to": 90, "score": 50},
                {"from": 90, "to": 95, "score": 70},
                {"from": 95, "to": 100, "score": 90},
                {"from": 100, "to": 999, "score": 100},
            ],
        )
        run = recalculate_all()
        result = CalculationResult.objects.get(run=run, criterion=c, model=model)
        assert result.normalized_score == 90

    def test_brand_age_scorer_in_engine(self, methodology, eq_type):
        origin, _ = BrandOriginClass.objects.get_or_create(
            origin_type="japanese", defaults={"fallback_score": 90},
        )
        jp_brand = Brand.objects.create(
            name="OldBrand", origin_class=origin, sales_start_year_ru=2000,
        )
        model = ACModel.objects.create(
            brand=jp_brand, inner_unit="JP-Age", equipment_type=eq_type,
        )
        c = Criterion.objects.create(
            methodology=methodology, code="brand_age", name_ru="Возраст",
            value_type="brand_age", scoring_type="min_median_max",
            weight=100, min_value=1995, max_value=2026, median_value=2010,
            display_order=1,
        )
        run = recalculate_all()
        result = CalculationResult.objects.get(run=run, criterion=c, model=model)
        assert result.normalized_score == pytest.approx(83.33, abs=0.1)

    def test_sync_brand_age_for_model_updates_raw_value(self, methodology, eq_type):
        origin, _ = BrandOriginClass.objects.get_or_create(
            origin_type="japanese", defaults={"fallback_score": 90},
        )
        brand = Brand.objects.create(
            name="SyncBrandAge", origin_class=origin, sales_start_year_ru=2012,
        )
        model = ACModel.objects.create(
            brand=brand, inner_unit="Sync-X", equipment_type=eq_type,
        )
        c = Criterion.objects.create(
            methodology=methodology, code="brand_age_ru", name_ru="Возраст",
            value_type="brand_age", scoring_type="min_median_max",
            weight=100, min_value=1995, max_value=2026, median_value=2010,
            display_order=1,
        )
        rv = ModelRawValue.objects.create(
            model=model, criterion=c, raw_value="should_be_replaced",
        )
        sync_brand_age_for_model(model)
        rv.refresh_from_db()
        assert rv.raw_value == "2012"

        brand.sales_start_year_ru = 2000
        brand.save()
        rv.refresh_from_db()
        assert rv.raw_value == "2000"


@pytest.mark.django_db
def test_update_model_total_index_without_calculation_run(methodology, ac_model):
    c1 = Criterion.objects.create(
        methodology=methodology, code="noise", name_ru="Шум",
        value_type="numeric", scoring_type="min_median_max",
        weight=50, min_value=20, median_value=30, max_value=40,
        display_order=1,
    )
    c2 = Criterion.objects.create(
        methodology=methodology, code="erv", name_ru="ЭРВ",
        value_type="binary", scoring_type="binary",
        weight=50, display_order=2,
    )
    ModelRawValue.objects.create(model=ac_model, criterion=c1, raw_value="30")
    ModelRawValue.objects.create(model=ac_model, criterion=c2, raw_value="да")

    runs_before = CalculationRun.objects.count()
    assert update_model_total_index(ac_model) is True
    ac_model.refresh_from_db()
    assert ac_model.total_index == pytest.approx(75.0, abs=0.02)
    assert CalculationRun.objects.count() == runs_before
