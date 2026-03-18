import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestConditionerListAPI:
    def test_list_returns_200(self, api_client, sample_ac):
        url = reverse("ratings:list")
        response = api_client.get(url)
        assert response.status_code == 200

    def test_list_returns_all(self, api_client, sample_ac, second_ac):
        url = reverse("ratings:list")
        response = api_client.get(url)
        assert len(response.data) == 2

    def test_list_ordered_by_score_desc(self, api_client, sample_ac, second_ac):
        url = reverse("ratings:list")
        response = api_client.get(url)
        scores = [item["total_score"] for item in response.data]
        assert scores == sorted(scores, reverse=True)

    def test_list_fields(self, api_client, sample_ac):
        url = reverse("ratings:list")
        response = api_client.get(url)
        item = response.data[0]
        assert "id" in item
        assert "rank" in item
        assert "brand" in item
        assert "model_name" in item
        assert "total_score" in item
        assert "parameters" not in item

    def test_empty_list(self, api_client, db):
        url = reverse("ratings:list")
        response = api_client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 0


@pytest.mark.django_db
class TestConditionerDetailAPI:
    def test_detail_returns_200(self, api_client, sample_ac_with_params):
        url = reverse("ratings:detail", args=[sample_ac_with_params.pk])
        response = api_client.get(url)
        assert response.status_code == 200

    def test_detail_includes_parameters(self, api_client, sample_ac_with_params):
        url = reverse("ratings:detail", args=[sample_ac_with_params.pk])
        response = api_client.get(url)
        assert "parameters" in response.data
        assert len(response.data["parameters"]) == 12

    def test_detail_parameter_fields(self, api_client, sample_ac_with_params):
        url = reverse("ratings:detail", args=[sample_ac_with_params.pk])
        response = api_client.get(url)
        param = response.data["parameters"][0]
        assert "id" in param
        assert "parameter_name" in param
        assert "raw_value" in param
        assert "unit" in param
        assert "score" in param

    def test_detail_includes_video_urls(self, api_client, sample_ac_with_params):
        url = reverse("ratings:detail", args=[sample_ac_with_params.pk])
        response = api_client.get(url)
        assert "youtube_url" in response.data
        assert "rutube_url" in response.data
        assert "vk_url" in response.data

    def test_detail_404(self, api_client, db):
        url = reverse("ratings:detail", args=[99999])
        response = api_client.get(url)
        assert response.status_code == 404
