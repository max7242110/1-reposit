"""Перенос ModelRawValue между версиями методики по коду критерия."""

from __future__ import annotations

from collections.abc import Iterable

from catalog.models import ModelRawValue
from methodology.models import MethodologyVersion


def _build_code_to_criterion_id(methodology_id: int) -> dict[str, int]:
    return {
        code: pk
        for code, pk in MethodologyVersion.objects.get(pk=methodology_id).criteria.values_list("code", "pk")
    }


def migrate_model_raw_values_between_methodologies(
    source_methodology_id: int | None,
    target_methodology_id: int,
) -> int:
    """
    Копирует ModelRawValue по совпадающему criterion.code из source в target.

    Правила:
    - если source не задан или совпадает с target -> ничего не делаем;
    - копируются только пары критериев с одинаковым code;
    - существующие строки target (model + criterion) НЕ перезаписываются.
    """
    if not source_methodology_id or source_methodology_id == target_methodology_id:
        return 0

    source_by_code = _build_code_to_criterion_id(source_methodology_id)
    target_by_code = _build_code_to_criterion_id(target_methodology_id)
    common_codes = source_by_code.keys() & target_by_code.keys()
    if not common_codes:
        return 0

    source_to_target: dict[int, int] = {
        source_by_code[code]: target_by_code[code]
        for code in common_codes
    }
    target_criterion_ids = set(source_to_target.values())

    existing_pairs = set(
        ModelRawValue.objects.filter(criterion_id__in=target_criterion_ids).values_list(
            "model_id", "criterion_id",
        )
    )

    source_rows: Iterable[ModelRawValue] = ModelRawValue.objects.filter(
        criterion_id__in=source_to_target.keys(),
    ).iterator()

    to_create: list[ModelRawValue] = []
    for rv in source_rows:
        target_criterion_id = source_to_target.get(rv.criterion_id)
        if target_criterion_id is None:
            continue
        pair = (rv.model_id, target_criterion_id)
        if pair in existing_pairs:
            continue
        existing_pairs.add(pair)
        to_create.append(
            ModelRawValue(
                model_id=rv.model_id,
                criterion_id=target_criterion_id,
                raw_value=rv.raw_value,
                numeric_value=rv.numeric_value,
                source=rv.source,
                source_url=rv.source_url,
                comment=rv.comment,
                verification_status=rv.verification_status,
                lab_status=rv.lab_status,
                entered_by_id=rv.entered_by_id,
                approved_by_id=rv.approved_by_id,
            )
        )

    if not to_create:
        return 0
    ModelRawValue.objects.bulk_create(to_create)
    return len(to_create)

