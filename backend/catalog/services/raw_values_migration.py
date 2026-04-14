"""Перенос ModelRawValue между версиями методики.

После рефакторинга Criterion стал standalone — raw values привязаны к параметру,
а не к методике. Миграция значений между методиками больше не требуется,
т.к. все методики ссылаются на одни и те же Criterion записи.
"""

from __future__ import annotations


def migrate_model_raw_values_between_methodologies(
    source_methodology_id: int | None,
    target_methodology_id: int,
) -> int:
    """No-op: raw values now reference standalone Criterion, shared across methodologies."""
    return 0
