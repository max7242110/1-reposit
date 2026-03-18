import pytest

from ratings.serializers import (
    AirConditionerDetailSerializer,
    AirConditionerListSerializer,
    ParameterValueSerializer,
)
from ratings.models import ParameterValue


@pytest.mark.django_db
class TestParameterValueSerializer:
    def test_fields(self, sample_ac):
        pv = ParameterValue.objects.create(
            air_conditioner=sample_ac,
            parameter_name="Шум мин.",
            raw_value="32",
            unit="дБ(А)",
            score=36.0,
        )
        data = ParameterValueSerializer(pv).data
        assert data["parameter_name"] == "Шум мин."
        assert data["raw_value"] == "32"
        assert data["unit"] == "дБ(А)"
        assert data["score"] == 36.0
        assert "id" in data


@pytest.mark.django_db
class TestAirConditionerListSerializer:
    def test_fields(self, sample_ac):
        data = AirConditionerListSerializer(sample_ac).data
        assert data["brand"] == "TestBrand"
        assert data["model_name"] == "TestModel-X100"
        assert data["total_score"] == 200.5
        assert "parameters" not in data

    def test_no_video_urls_in_list(self, sample_ac):
        data = AirConditionerListSerializer(sample_ac).data
        assert "youtube_url" not in data


@pytest.mark.django_db
class TestAirConditionerDetailSerializer:
    def test_includes_parameters(self, sample_ac_with_params):
        data = AirConditionerDetailSerializer(sample_ac_with_params).data
        assert "parameters" in data
        assert len(data["parameters"]) == 12

    def test_includes_video_urls(self, sample_ac):
        data = AirConditionerDetailSerializer(sample_ac).data
        assert data["youtube_url"] == "https://youtu.be/test123"
        assert data["rutube_url"] == "https://rutube.ru/video/test123/"

    def test_all_fields_present(self, sample_ac_with_params):
        data = AirConditionerDetailSerializer(sample_ac_with_params).data
        expected = {
            "id", "rank", "brand", "model_name",
            "youtube_url", "rutube_url", "vk_url",
            "total_score", "parameters",
        }
        assert set(data.keys()) == expected
