"""Shared constants for parameter definitions used in import and tests."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ParameterDef:
    value_col: str
    score_col: str
    name: str
    unit: str


PARAMETER_DEFS: tuple[ParameterDef, ...] = (
    ParameterDef("G", "H", "Шум мин.", "дБ(А)"),
    ParameterDef("I", "J", "Вибрация", "мм"),
    ParameterDef("K", "L", "Мин. напряжение", "В"),
    ParameterDef("M", "N", "S меди внутр. блок", ""),
    ParameterDef("O", "P", "S меди наруж. блок", ""),
    ParameterDef("Q", "R", "Наличие ЭРВ", ""),
    ParameterDef("S", "T", "Подсветка пульта", ""),
    ParameterDef("U", "V", "Тип (инвертор/он-офф)", ""),
    ParameterDef("W", "X", "Наличие WiFi", ""),
    ParameterDef("Y", "Z", "Регулировка оборотов наруж. бл.", ""),
    ParameterDef("AA", "AB", "Кол-во скоростей внутр. бл.", ""),
    ParameterDef("AC", "AD", "Макс. длина фреонопровода", "м"),
)

PARAMETER_NAMES: tuple[str, ...] = tuple(p.name for p in PARAMETER_DEFS)
