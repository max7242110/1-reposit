from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from ratings.models import AirConditioner


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.mark.django_db
class TestConditionerListAPI:
    def test_list_returns_200(self, api_client: APIClient, sample_ac: AirConditioner) -> None:
        response = api_client.get(reverse("ratings:list"))
        assert response.status_code == 200

    def test_list_returns_all(
        self, api_client: APIClient, sample_ac: AirConditioner, second_ac: AirConditioner
    ) -> None:
        response = api_client.get(reverse("ratings:list"))
        assert len(response.data) == 2

    def test_list_ordered_by_score_desc(
        self, api_client: APIClient, sample_ac: AirConditioner, second_ac: AirConditioner
    ) -> None:
        response = api_client.get(reverse("ratings:list"))
        scores = [item["total_score"] for item in response.data]
        assert scores == sorted(scores, reverse=True)

    def test_list_fields(self, api_client: APIClient, sample_ac: AirConditioner) -> None:
        response = api_client.get(reverse("ratings:list"))
        item = response.data[0]
        expected_keys = {"id", "rank", "brand", "model_name", "total_score"}
        assert set(item.keys()) == expected_keys

    def test_empty_list(self, api_client: APIClient, db: None) -> None:
        response = api_client.get(reverse("ratings:list"))
        assert response.status_code == 200
        assert len(response.data) == 0

    def test_v1_endpoint_works(self, api_client: APIClient, sample_ac: AirConditioner) -> None:
        response = api_client.get("/api/v1/conditioners/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestConditionerDetailAPI:
    def test_detail_returns_200(
        self, api_client: APIClient, sample_ac_with_params: AirConditioner
    ) -> None:
        url = reverse("ratings:detail", args=[sample_ac_with_params.pk])
        response = api_client.get(url)
        assert response.status_code == 200

    def test_detail_includes_parameters(
        self, api_client: APIClient, sample_ac_with_params: AirConditioner
    ) -> None:
        url = reverse("ratings:detail", args=[sample_ac_with_params.pk])
        response = api_client.get(url)
        assert "parameters" in response.data
        assert len(response.data["parameters"]) == 12

    def test_detail_parameter_fields(
        self, api_client: APIClient, sample_ac_with_params: AirConditioner
    ) -> None:
        url = reverse("ratings:detail", args=[sample_ac_with_params.pk])
        response = api_client.get(url)
        param = response.data["parameters"][0]
        expected_keys = {"id", "parameter_name", "raw_value", "unit", "score"}
        assert set(param.keys()) == expected_keys

    def test_detail_includes_video_urls(
        self, api_client: APIClient, sample_ac_with_params: AirConditioner
    ) -> None:
        url = reverse("ratings:detail", args=[sample_ac_with_params.pk])
        response = api_client.get(url)
        assert "youtube_url" in response.data
        assert "rutube_url" in response.data
        assert "vk_url" in response.data

    def test_detail_404(self, api_client: APIClient, db: None) -> None:
        url = reverse("ratings:detail", args=[99999])
        response = api_client.get(url)
        assert response.status_code == 404

    def test_detail_all_fields(
        self, api_client: APIClient, sample_ac_with_params: AirConditioner
    ) -> None:
        url = reverse("ratings:detail", args=[sample_ac_with_params.pk])
        response = api_client.get(url)
        expected_keys = {
            "id", "rank", "brand", "model_name",
            "youtube_url", "rutube_url", "vk_url",
            "total_score", "parameters",
        }
        assert set(response.data.keys()) == expected_keys
