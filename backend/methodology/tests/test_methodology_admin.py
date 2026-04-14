from __future__ import annotations

import re

import pytest
from django.urls import reverse

from brands.models import Brand
from catalog.models import ACModel, ModelRawValue
from catalog.services import migrate_model_raw_values_between_methodologies
from methodology.models import Criterion, MethodologyCriterion, MethodologyVersion


def _make_mc(methodology, code, name_ru="Test", value_type="binary", **mc_kwargs):
    """Helper: create standalone Criterion + MethodologyCriterion."""
    mc_defaults = {"scoring_type": "binary", "weight": 1.0, "display_order": 1, "is_active": True}
    mc_defaults.update(mc_kwargs)
    criterion, _ = Criterion.objects.get_or_create(
        code=code, defaults={"name_ru": name_ru, "value_type": value_type},
    )
    return MethodologyCriterion.objects.create(
        methodology=methodology, criterion=criterion, **mc_defaults,
    )


@pytest.mark.django_db
def test_methodology_version_change_page_renders(client, admin_user):
    mv = MethodologyVersion.objects.create(version="adm_test", name="Admin test", is_active=False)
    _make_mc(mv, "c1", "К1", "binary", weight=10.5, display_order=1)
    client.force_login(admin_user)
    url = reverse("admin:methodology_methodologyversion_change", args=[mv.pk])
    response = client.get(url)
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "criteria-weight-total" in content
    assert "methodology_criteria-group" in content
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
    mc = _make_mc(mv, "c_dup", "Критерий", "binary", weight=5.0, display_order=1)
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
    # M2M через MethodologyCriterion — проверяем через through-таблицу
    clone_mcs = MethodologyCriterion.objects.filter(methodology=clone)
    assert clone_mcs.count() == 1
    clone_mc = clone_mcs.first()
    assert clone_mc.criterion.code == "c_dup"
    assert clone_mc.weight == 5.0


@pytest.mark.django_db
def test_duplicate_adds_active_criteria_missing_on_source_with_zero_weight(client, admin_user):
    active = MethodologyVersion.objects.create(version="act_v", name="Active", is_active=True)
    old = MethodologyVersion.objects.create(version="old_v", name="Old", is_active=False)

    # Общий параметр — один Criterion, два MethodologyCriterion
    shared_crit = Criterion.objects.create(code="on_both", name_ru="Оба", value_type="binary")
    MethodologyCriterion.objects.create(
        methodology=active, criterion=shared_crit,
        scoring_type="binary", weight=10.0, display_order=1,
    )
    MethodologyCriterion.objects.create(
        methodology=old, criterion=shared_crit,
        scoring_type="binary", weight=3.0, display_order=1,
    )

    # Параметр только в активной
    only_active_crit = Criterion.objects.create(
        code="only_active", name_ru="Только в активной", value_type="binary",
    )
    MethodologyCriterion.objects.create(
        methodology=active, criterion=only_active_crit,
        scoring_type="binary", weight=7.0, display_order=2,
    )

    # Параметр только в старой
    only_old_crit = Criterion.objects.create(
        code="only_old", name_ru="Только в старой", value_type="binary",
    )
    MethodologyCriterion.objects.create(
        methodology=old, criterion=only_old_crit,
        scoring_type="binary", weight=4.0, display_order=2,
    )

    client.force_login(admin_user)
    dup_url = reverse("admin:methodology_methodologyversion_duplicate", args=[old.pk])
    response = client.post(
        dup_url,
        {"version": "merged_v", "name": "Merged", "description": ""},
    )
    assert response.status_code == 302
    clone = MethodologyVersion.objects.get(version="merged_v")
    by_code = {mc.criterion.code: mc for mc in MethodologyCriterion.objects.filter(
        methodology=clone,
    ).select_related("criterion")}
    assert set(by_code) == {"on_both", "only_old", "only_active"}
    assert by_code["on_both"].weight == 3.0
    assert by_code["only_old"].weight == 4.0
    assert by_code["only_active"].weight == 0.0
    assert by_code["only_active"].criterion.name_ru == "Только в активной"


@pytest.mark.django_db
def test_methodology_add_prefills_criteria_from_active_with_zero_weight(client, admin_user):
    active = MethodologyVersion.objects.create(version="act_prefill", name="Active", is_active=True)
    crit = Criterion.objects.create(
        code="pre_code", name_ru="Из активной методики", value_type="binary",
    )
    MethodologyCriterion.objects.create(
        methodology=active, criterion=crit,
        scoring_type="binary", weight=11.25, display_order=3,
    )
    client.force_login(admin_user)
    url = reverse("admin:methodology_methodologyversion_add")
    response = client.get(url)
    assert response.status_code == 200
    html = response.content.decode("utf-8")
    assert "pre_code" in html or str(crit.pk) in html
    # Проверяем что вес 0 задан в предзаполненном инлайне
    assert 'name="methodology_criteria-0-weight"' in html
    assert re.search(
        r'name="methodology_criteria-0-weight"[\s\S]{0,800}?value="0(?:\.0)?"',
        html,
    ), "ожидался вес 0 в первой строке инлайна"


@pytest.mark.django_db
def test_criterion_admin_changelist_renders(client, admin_user):
    """Проверяем что страница списка параметров рендерится."""
    Criterion.objects.create(code="test_crit", name_ru="Тестовый", value_type="binary")
    client.force_login(admin_user)
    url = reverse("admin:methodology_criterion_changelist")
    response = client.get(url)
    assert response.status_code == 200
    html = response.content.decode("utf-8")
    assert "test_crit" in html


@pytest.mark.django_db
def test_migrate_model_raw_values_between_methodologies_is_noop():
    """After refactor, raw values reference standalone Criterion — migration is no-op."""
    moved = migrate_model_raw_values_between_methodologies(1, 2)
    assert moved == 0


@pytest.mark.django_db
def test_activate_methodology_saves(client, admin_user):
    """Проверяем что активация методики работает через admin."""
    src = MethodologyVersion.objects.create(version="act_src", name="Active source", is_active=True)
    tgt = MethodologyVersion.objects.create(version="act_tgt", name="Target", is_active=False)

    crit, _ = Criterion.objects.get_or_create(code="noise", defaults={"name_ru": "Шум", "value_type": "binary"})
    mc_src = MethodologyCriterion.objects.create(
        methodology=src, criterion=crit,
        scoring_type="binary", weight=5.0, display_order=1,
    )
    mc_tgt = MethodologyCriterion.objects.create(
        methodology=tgt, criterion=crit,
        scoring_type="binary", weight=4.0, display_order=1,
    )

    brand = Brand.objects.create(name="Brand M")
    model = ACModel.objects.create(brand=brand, inner_unit="M-1")
    # Raw value ссылается на standalone Criterion — доступна для обеих методик
    ModelRawValue.objects.create(model=model, criterion=crit, raw_value="да")

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
            "methodology_criteria-TOTAL_FORMS": "1",
            "methodology_criteria-INITIAL_FORMS": "1",
            "methodology_criteria-MIN_NUM_FORMS": "0",
            "methodology_criteria-MAX_NUM_FORMS": "1000",
            "methodology_criteria-0-id": str(mc_tgt.pk),
            "methodology_criteria-0-methodology": str(tgt.pk),
            "methodology_criteria-0-criterion": str(crit.pk),
            "methodology_criteria-0-scoring_type": mc_tgt.scoring_type,
            "methodology_criteria-0-weight": str(mc_tgt.weight),
            "methodology_criteria-0-region_scope": mc_tgt.region_scope,
            "methodology_criteria-0-is_public": "on" if mc_tgt.is_public else "",
            "methodology_criteria-0-is_active": "on" if mc_tgt.is_active else "",
            "methodology_criteria-0-display_order": str(mc_tgt.display_order),
        },
        follow=True,
    )
    assert response.status_code == 200
    assert MethodologyVersion.objects.get(pk=tgt.pk).is_active is True
    # Raw value по-прежнему привязана к standalone Criterion — доступна
    rv = ModelRawValue.objects.filter(model=model, criterion=crit).first()
    assert rv is not None
    assert rv.raw_value == "да"
