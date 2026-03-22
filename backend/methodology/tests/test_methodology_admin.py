from __future__ import annotations

import pytest
from django.urls import reverse

from methodology.models import Criterion, MethodologyVersion


@pytest.mark.django_db
def test_methodology_version_change_page_renders(client, admin_user):
    mv = MethodologyVersion.objects.create(version="adm_test", name="Admin test", is_active=False)
    Criterion.objects.create(
        methodology=mv,
        code="c1",
        name_ru="К1",
        value_type="binary",
        scoring_type="binary",
        weight=10.5,
        display_order=1,
    )
    client.force_login(admin_user)
    url = reverse("admin:methodology_methodologyversion_change", args=[mv.pk])
    response = client.get(url)
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "criteria-weight-total" in content
    assert "criterion_set-group" in content
    assert "criteria-weight-banner" in content
    assert ("10.50%" in content or "10,50%" in content or "10.5" in content)


@pytest.mark.django_db
def test_methodology_version_change_missing_pk_redirects(client, admin_user):
    client.force_login(admin_user)
    url = reverse("admin:methodology_methodologyversion_change", args=[99999])
    response = client.get(url)
    # Django admin отдаёт редирект на индекс, если объекта нет
    assert response.status_code in (302, 404)
    if response.status_code == 302:
        assert "/admin/" in (response.get("Location") or "")
