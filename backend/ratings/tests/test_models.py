from __future__ import annotations

import pytest
from django.db import IntegrityError

from ratings.constants import PARAMETER_DEFS
from ratings.models import AirConditioner, ParameterValue


@pytest.mark.django_db
class TestAirConditionerModel:
    def test_create(self, sample_ac: AirConditioner) -> None:
        assert sample_ac.pk is not None
        assert sample_ac.brand == "TestBrand"
        assert sample_ac.model_name == "TestModel-X100"
        assert sample_ac.total_score == 200.5

    def test_str(self, sample_ac: AirConditioner) -> None:
        assert str(sample_ac) == "TestBrand TestModel-X100"

    def test_ordering(self, sample_ac: AirConditioner, second_ac: AirConditioner) -> None:
        qs = AirConditioner.objects.all()
        assert qs[0].total_score >= qs[1].total_score

    def test_default_urls_are_empty(self, db: None) -> None:
        ac = AirConditioner.objects.create(
            rank=99, brand="X", model_name="Y", total_score=10
        )
        assert ac.youtube_url == ""
        assert ac.rutube_url == ""
        assert ac.vk_url == ""


@pytest.mark.django_db
class TestParameterValueModel:
    def test_create(self, sample_ac: AirConditioner) -> None:
        pv = ParameterValue.objects.create(
            air_conditioner=sample_ac,
            parameter_name="Шум мин.",
            raw_value="32",
            unit="дБ(А)",
            score=36.0,
        )
        assert pv.pk is not None
        assert pv.score == 36.0

    def test_str(self, sample_ac: AirConditioner) -> None:
        pv = ParameterValue.objects.create(
            air_conditioner=sample_ac,
            parameter_name="Вибрация",
            raw_value="0.07",
            unit="мм",
            score=4.3,
        )
        assert "Вибрация" in str(pv)
        assert "4.3" in str(pv)

    def test_str_empty_raw_value(self, sample_ac: AirConditioner) -> None:
        pv = ParameterValue.objects.create(
            air_conditioner=sample_ac,
            parameter_name="Тест",
            raw_value="",
            score=0,
        )
        assert "Тест" in str(pv)

    def test_unique_constraint(self, sample_ac: AirConditioner) -> None:
        ParameterValue.objects.create(
            air_conditioner=sample_ac,
            parameter_name="Шум мин.",
            raw_value="32",
            score=36.0,
        )
        with pytest.raises(IntegrityError):
            ParameterValue.objects.create(
                air_conditioner=sample_ac,
                parameter_name="Шум мин.",
                raw_value="30",
                score=40.0,
            )

    def test_cascade_delete(self, sample_ac_with_params: AirConditioner) -> None:
        ac_id = sample_ac_with_params.pk
        param_count = len(PARAMETER_DEFS)
        assert ParameterValue.objects.filter(air_conditioner_id=ac_id).count() == param_count
        sample_ac_with_params.delete()
        assert ParameterValue.objects.filter(air_conditioner_id=ac_id).count() == 0

    def test_related_name(self, sample_ac_with_params: AirConditioner) -> None:
        params = sample_ac_with_params.parameters.all()
        assert params.count() == len(PARAMETER_DEFS)
