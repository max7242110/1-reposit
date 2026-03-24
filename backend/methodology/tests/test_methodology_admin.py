from __future__ import annotations

import re

import pytest
from django.urls import reverse

from brands.models import Brand
from catalog.models import ACModel, ModelRawValue
from catalog.services import migrate_model_raw_values_between_methodologies
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


@pytest.mark.django_db
def test_methodology_version_change_page_has_duplicate_link(client, admin_user):
    mv = MethodologyVersion.objects.create(version="dup_src", name="Source", is_active=False)
    client.force_login(admin_user)
    url = reverse("admin:methodology_methodologyversion_change", args=[mv.pk])
    response = client.get(url)
    assert response.status_code == 200
    dup_url = reverse("admin:methodology_methodologyversion_duplicate", args=[mv.pk])
    assert dup_url in response.content.decode("utf-8")


@pytest.mark.django_db
def test_methodology_version_duplicate_creates_copy(client, admin_user):
    mv = MethodologyVersion.objects.create(
        version="orig_v",
        name="Original",
        description="Desc",
        is_active=True,
        needs_recalculation=True,
    )
    Criterion.objects.create(
        methodology=mv,
        code="c_dup",
        name_ru="Критерий",
        value_type="binary",
        scoring_type="binary",
        weight=5.0,
        display_order=1,
    )
    client.force_login(admin_user)
    dup_url = reverse("admin:methodology_methodologyversion_duplicate", args=[mv.pk])
    assert client.get(dup_url).status_code == 200
    response = client.post(
        dup_url,
        {
            "version": "new_v_unique",
            "name": "Cloned name",
            "description": "",
        },
    )
    assert response.status_code == 302
    clone = MethodologyVersion.objects.get(version="new_v_unique")
    assert clone.pk != mv.pk
    assert clone.name == "Cloned name"
    assert clone.description == "Desc"
    assert clone.is_active is False
    assert clone.needs_recalculation is True
    assert clone.criteria.count() == 1
    c = clone.criteria.get()
    assert c.code == "c_dup"
    assert c.weight == 5.0
    assert c.group_id is None


@pytest.mark.django_db
def test_duplicate_adds_active_criteria_missing_on_source_with_zero_weight(client, admin_user):
    active = MethodologyVersion.objects.create(version="act_v", name="Active", is_active=True)
    old = MethodologyVersion.objects.create(version="old_v", name="Old", is_active=False)
    Criterion.objects.create(
        methodology=active,
        code="on_both",
        name_ru="Оба",
        value_type="binary",
        scoring_type="binary",
        weight=10.0,
        display_order=1,
    )
    Criterion.objects.create(
        methodology=old,
        code="on_both",
        name_ru="Оба (старая редакция)",
        value_type="binary",
        scoring_type="binary",
        weight=3.0,
        display_order=1,
    )
    Criterion.objects.create(
        methodology=active,
        code="only_active",
        name_ru="Только в активной",
        value_type="binary",
        scoring_type="binary",
        weight=7.0,
        display_order=2,
    )
    Criterion.objects.create(
        methodology=old,
        code="only_old",
        name_ru="Только в старой",
        value_type="binary",
        scoring_type="binary",
        weight=4.0,
        display_order=2,
    )
    client.force_login(admin_user)
    dup_url = reverse("admin:methodology_methodologyversion_duplicate", args=[old.pk])
    response = client.post(
        dup_url,
        {"version": "merged_v", "name": "Merged", "description": ""},
    )
    assert response.status_code == 302
    clone = MethodologyVersion.objects.get(version="merged_v")
    by_code = {c.code: c for c in clone.criteria.all()}
    assert set(by_code) == {"on_both", "only_old", "only_active"}
    assert by_code["on_both"].weight == 3.0
    assert by_code["only_old"].weight == 4.0
    assert by_code["only_active"].weight == 0.0
    assert by_code["only_active"].name_ru == "Только в активной"


@pytest.mark.django_db
def test_methodology_add_prefills_criteria_from_active_with_zero_weight(client, admin_user):
    active = MethodologyVersion.objects.create(version="act_prefill", name="Active", is_active=True)
    Criterion.objects.create(
        methodology=active,
        code="pre_code",
        name_ru="Из активной методики",
        value_type="binary",
        scoring_type="binary",
        weight=11.25,
        display_order=3,
    )
    client.force_login(admin_user)
    url = reverse("admin:methodology_methodologyversion_add")
    response = client.get(url)
    assert response.status_code == 200
    html = response.content.decode("utf-8")
    assert "pre_code" in html
    assert "Из активной методики" in html
    # префикс инлайна — related_name FK: criteria (не criterion_set)
    assert 'name="criteria-0-weight"' in html
    assert re.search(
        r'name="criteria-0-weight"[\s\S]{0,800}?value="0(?:\.0)?"',
        html,
    ), "ожидался вес 0 в первой строке инлайна"


@pytest.mark.django_db
def test_criterion_admin_multiselect_methodology_filter(client, admin_user):
    m1 = MethodologyVersion.objects.create(version="f1", name="M1", is_active=False)
    m2 = MethodologyVersion.objects.create(version="f2", name="M2", is_active=True)
    m3 = MethodologyVersion.objects.create(version="f3", name="M3", is_active=False)
    Criterion.objects.create(
        methodology=m1, code="m1_only", name_ru="M1", value_type="binary", scoring_type="binary", weight=1.0
    )
    Criterion.objects.create(
        methodology=m2, code="m2_only", name_ru="M2", value_type="binary", scoring_type="binary", weight=1.0
    )
    Criterion.objects.create(
        methodology=m3, code="m3_only", name_ru="M3", value_type="binary", scoring_type="binary", weight=1.0
    )
    client.force_login(admin_user)
    url = reverse("admin:methodology_criterion_changelist")
    response = client.get(url, {"methodology__id__in": f"{m1.pk},{m2.pk}"})
    assert response.status_code == 200
    html = response.content.decode("utf-8")
    assert "m1_only" in html
    assert "m2_only" in html
    assert "m3_only" not in html


@pytest.mark.django_db
def test_migrate_model_raw_values_between_methodologies_by_code():
    source = MethodologyVersion.objects.create(version="m_src", name="Source", is_active=True)
    target = MethodologyVersion.objects.create(version="m_tgt", name="Target", is_active=False)
    c_src_common = Criterion.objects.create(
        methodology=source, code="common", name_ru="Common", value_type="binary", scoring_type="binary", weight=5.0
    )
    Criterion.objects.create(
        methodology=source, code="source_only", name_ru="SrcOnly", value_type="binary", scoring_type="binary", weight=1.0
    )
    c_tgt_common = Criterion.objects.create(
        methodology=target, code="common", name_ru="Common tgt", value_type="binary", scoring_type="binary", weight=3.0
    )
    Criterion.objects.create(
        methodology=target, code="target_only", name_ru="TgtOnly", value_type="binary", scoring_type="binary", weight=1.0
    )
    brand = Brand.objects.create(name="B1")
    model = ACModel.objects.create(brand=brand, inner_unit="X")
    ModelRawValue.objects.create(
        model=model,
        criterion=c_src_common,
        raw_value="да",
        source="catalog",
        comment="copied",
        lab_status=ModelRawValue.LabStatus.MEASURED,
    )

    moved = migrate_model_raw_values_between_methodologies(source.pk, target.pk)
    assert moved == 1
    rv_new = ModelRawValue.objects.get(model=model, criterion=c_tgt_common)
    assert rv_new.raw_value == "да"
    assert rv_new.source == "catalog"
    assert rv_new.comment == "copied"
    assert rv_new.lab_status == ModelRawValue.LabStatus.MEASURED


@pytest.mark.django_db
def test_activate_methodology_migrates_raw_values_by_code(client, admin_user):
    src = MethodologyVersion.objects.create(version="act_src", name="Active source", is_active=True)
    tgt = MethodologyVersion.objects.create(version="act_tgt", name="Target", is_active=False)
    c_src = Criterion.objects.create(
        methodology=src,
        code="noise",
        name_ru="Шум",
        value_type="binary",
        scoring_type="binary",
        weight=5.0,
        display_order=1,
    )
    c_tgt = Criterion.objects.create(
        methodology=tgt,
        code="noise",
        name_ru="Шум (новая)",
        value_type="binary",
        scoring_type="binary",
        weight=4.0,
        display_order=1,
    )
    brand = Brand.objects.create(name="Brand M")
    model = ACModel.objects.create(brand=brand, inner_unit="M-1")
    ModelRawValue.objects.create(model=model, criterion=c_src, raw_value="да")

    client.force_login(admin_user)
    url = reverse("admin:methodology_methodologyversion_change", args=[tgt.pk])
    response = client.post(
        url,
        {
            "version": tgt.version,
            "name": tgt.name,
            "description": tgt.description,
            "is_active": "on",
            "needs_recalculation": "on" if tgt.needs_recalculation else "",
            "criteria-TOTAL_FORMS": "1",
            "criteria-INITIAL_FORMS": "1",
            "criteria-MIN_NUM_FORMS": "0",
            "criteria-MAX_NUM_FORMS": "1000",
            "criteria-0-id": str(c_tgt.pk),
            "criteria-0-code": c_tgt.code,
            "criteria-0-name_ru": c_tgt.name_ru,
            "criteria-0-value_type": c_tgt.value_type,
            "criteria-0-scoring_type": c_tgt.scoring_type,
            "criteria-0-weight": str(c_tgt.weight),
            "criteria-0-is_lab": "on" if c_tgt.is_lab else "",
            "criteria-0-region_scope": c_tgt.region_scope,
            "criteria-0-is_public": "on" if c_tgt.is_public else "",
            "criteria-0-is_active": "on" if c_tgt.is_active else "",
            "criteria-0-display_order": str(c_tgt.display_order),
        },
        follow=True,
    )
    assert response.status_code == 200
    assert MethodologyVersion.objects.get(pk=tgt.pk).is_active is True
    copied = ModelRawValue.objects.filter(model=model, criterion=c_tgt).first()
    assert copied is not None
    assert copied.raw_value == "да"
