from __future__ import annotations

from typing import Any

from django.db import transaction
from django.db.models import Max

from .models import Criterion, MethodologyVersion

_SKIP_CRITERION_FIELDS = frozenset({"id", "methodology", "group", "created_at", "updated_at"})

# Поля инлайна MethodologyVersionAdmin / CriterionInline (остальное копируется при сохранении).
CRITERION_INLINE_FORM_FIELDS = frozenset({
    "code",
    "name_ru",
    "value_type",
    "scoring_type",
    "weight",
    "is_lab",
    "region_scope",
    "is_public",
    "is_active",
    "display_order",
})


def backfill_criterion_extras_from_methodology(
    criterion: Criterion,
    template_methodology_pk: int | None,
) -> None:
    """
    Подставляет поля, которых нет в инлайне, по критерию с тем же code
    в указанной версии методики (до сохранения новой версии это была активная).
    """
    if template_methodology_pk is None:
        return
    tpl_mv = MethodologyVersion.objects.filter(pk=template_methodology_pk).first()
    if tpl_mv is None:
        return
    try:
        tpl = tpl_mv.criteria.get(code=criterion.code)
    except Criterion.DoesNotExist:
        return
    skip = _SKIP_CRITERION_FIELDS | CRITERION_INLINE_FORM_FIELDS
    for f in Criterion._meta.local_fields:
        if f.name in skip:
            continue
        setattr(criterion, f.name, getattr(tpl, f.name))
    criterion.save()


def template_criteria_inline_initial() -> list[dict[str, Any]]:
    """
    Данные для предзаполнения инлайна критериев при создании новой версии методики:
    копия строк активной методики (как в каталоге критериев для неё), вес = 0.
    """
    active = MethodologyVersion.objects.filter(is_active=True).first()
    if active is None:
        return []
    rows: list[dict[str, Any]] = []
    for c in active.criteria.order_by("display_order", "pk"):
        rows.append(
            {
                "code": c.code,
                "name_ru": c.name_ru,
                "value_type": c.value_type,
                "scoring_type": c.scoring_type,
                "weight": 0.0,
                "is_lab": c.is_lab,
                "region_scope": c.region_scope,
                "is_public": c.is_public,
                "is_active": c.is_active,
                "display_order": c.display_order,
            }
        )
    return rows


def _criterion_clone_kwargs(criterion: Criterion) -> dict:
    kwargs: dict = {}
    for f in Criterion._meta.local_fields:
        if f.name in _SKIP_CRITERION_FIELDS:
            continue
        kwargs[f.name] = getattr(criterion, f.name)
    return kwargs


def _append_criteria_from_methodology(
    target: MethodologyVersion,
    template: MethodologyVersion,
    *,
    codes_present: set[str],
    weight_override: float | None = None,
) -> None:
    """Добавляет к target критерии из template, чьих кодов нет в codes_present."""
    extra = template.criteria.order_by("display_order", "pk").exclude(code__in=codes_present)
    if not extra:
        return
    max_order = target.criteria.aggregate(m=Max("display_order"))["m"] or 0
    next_order = max_order + 1
    for c in extra:
        kwargs = _criterion_clone_kwargs(c)
        if weight_override is not None:
            kwargs["weight"] = weight_override
        kwargs["display_order"] = next_order
        next_order += 1
        Criterion.objects.create(methodology=target, group=None, **kwargs)
        codes_present.add(c.code)


def duplicate_methodology_version(
    source: MethodologyVersion,
    *,
    version: str,
    name: str,
    description: str | None = None,
) -> MethodologyVersion:
    """
    Создаёт новую MethodologyVersion с копией критериев исходной версии.

    Дополнительно подтягивает критерии из активной методики, которых не было
    у исходной (типичный случай: новые параметры завели в админке критериев
    у активной методики, а дублируют старую версию). Такие строки добавляются
    с весом 0 и порядком в конце списка.
    """
    if MethodologyVersion.objects.filter(version=version).exists():
        raise ValueError(f"Версия «{version}» уже существует.")
    desc = source.description if description is None else description
    with transaction.atomic():
        new_mv = MethodologyVersion.objects.create(
            version=version,
            name=name,
            description=desc,
            is_active=False,
            needs_recalculation=source.needs_recalculation,
        )
        codes_in_new: set[str] = set()
        for c in source.criteria.all().order_by("display_order", "pk"):
            kwargs = _criterion_clone_kwargs(c)
            Criterion.objects.create(methodology=new_mv, group=None, **kwargs)
            codes_in_new.add(c.code)

        active = MethodologyVersion.objects.filter(is_active=True).first()
        if active is not None:
            _append_criteria_from_methodology(
                new_mv,
                active,
                codes_present=codes_in_new,
                weight_override=0.0,
            )
    return new_mv
