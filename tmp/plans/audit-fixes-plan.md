# План: Исправление проблем аудита математического аппарата Scoring Engine

## Контекст

Проведён аудит scoring engine рейтинга кондиционеров. Найдены проблемы от критических до низких. Все проблемы описаны в `Разовые задачи доработки/АУДИТ-МАТЕМАТИКИ.md`. Issue #1 (нормализация весов) — отложена на следующий раз.

## Решения, согласованные с пользователем

| # | Проблема | Решение |
|---|----------|---------|
| ~~1~~ | ~~Веса не нормализуются~~ | **ОТЛОЖЕНО** |
| 2 | Несогласованность интервалов | Единая конвенция `[from, to)` |
| 3 | kW/W эвристика | Убрать, требовать ватты |
| 4-5 | is_inverted игнорируется | Binary: добавить поддержку. Categorical/CustomScale/Formula: блокировать в админке. BrandAge: by design, задокументировать |
| 6 | Нет валидации min≤median≤max | Добавить в модель |
| 7 | Нет валидации weight≥0 | Добавить в модель + DB constraint |
| 10 | BrandAge жёстко инвертирован | By design, задокументировать |
| 14 | Fan speed gap | Оставить как есть |
| 17-21 | Float, тесты, мёртвый код, concurrent | Чинить всё |

---

## Фаза 1: КРИТИЧЕСКАЯ — Единая конвенция интервалов (Issue #2)

**Файл:** `backend/scoring/scorers/custom_scale.py`

- Строка ~51: заменить `if low <= value <= high:` на `if low <= value < high:`
- Убедиться что последний интервал в шкалах покрывает верхнюю границу (может понадобиться `to: inf` или `to: 999999`)

**Тесты:** добавить тест на граничное значение (value == to → попадает в следующий интервал)

---

## Фаза 2: СЕРЬЁЗНЫЕ — Целостность данных и корректность scorers

### 2A. Убрать kW/W эвристику (Issue #3)

**Файл:** `backend/scoring/scorers/fallback.py`

- Удалить строки 60-66 (обе проверки `if 0 < value < 100: value *= 1000`)
- Обновить docstring модуля (строки 1-13) — убрать упоминание обратной совместимости с kW
- Добавить защиту от `nominal_w == 0` после `float()` (Issue #9 заодно)

**Файл:** `backend/scoring/scorers/numeric.py`

- В `_resolve_median()` строки 18-19: убрать `if cap_for_map > 100: cap_for_map /= 1000`. Median keys должны быть в тех же единицах что nominal_capacity. **Внимание:** нужна data-миграция если в БД ключи в кВт

### 2B. Поддержка is_inverted (Issues #4-5)

**Файл:** `backend/scoring/scorers/binary.py`

- Добавить проверку `criterion.is_inverted`:
  ```python
  is_true = val in TRUTHY
  if criterion.is_inverted:
      score = 0.0 if is_true else 100.0
  else:
      score = 100.0 if is_true else 0.0
  ```

**Файл:** `backend/methodology/admin/criterion_admin.py`

- Добавить валидацию: если `is_inverted=True` и `scoring_type` в `(custom_scale, universal_scale, formula, interval)` — `ValidationError("Для этого типа скоринга инверсия задаётся в самой шкале")`

**Файл:** `backend/scoring/scorers/brand_age.py`

- Добавить docstring: "Инверсия by design: меньший год (старше бренд) = выше балл. is_inverted не используется, т.к. направление шкалы зашито в логику доменной области."

### 2C. Валидация на уровне модели (Issues #6, #7)

**Файл:** `backend/methodology/models.py`

- Добавить `clean()` в `Criterion`:
  - `weight >= 0` — иначе `ValidationError`
  - Если заданы `min_value`, `median_value`, `max_value` — проверить `min <= median <= max`
- Добавить DB constraint: `CheckConstraint(check=Q(weight__gte=0), name="criterion_weight_non_negative")`

**Миграция:** `python3 manage.py makemigrations methodology` — перед этим убедиться что в БД нет невалидных данных

---

## Фаза 3: СРЕДНИЕ — Детерминизм, ошибки, производительность

### 3A. Детерминизм _resolve_median (Issue #8)

**Файл:** `backend/scoring/scorers/numeric.py`

- В `_resolve_median()` строки 22-29: при `dist == best_dist` выбирать ключ с меньшим числовым значением:
  ```python
  if dist < best_dist or (dist == best_dist and float(key) < float(best_key)):
  ```

### 3B. Деление на ноль nominal_capacity (Issue #9)

**Файл:** `backend/scoring/scorers/fallback.py`

- После `nominal_w = float(nominal_capacity)` добавить: `if nominal_w == 0: return ScoreResult(normalized_score=0)`

### 3C. Документация BrandAgeScorer (Issue #10)

**Файл:** `backend/scoring/scorers/brand_age.py` — уже описано в 2B

### 3D. Мёртвый код и error_message в batch.py (Issues #11, #12)

**Файл:** `backend/scoring/engine/batch.py`

- Строка 42: удалить `CalculationResult.objects.filter(run=run).delete()` — run только что создан, результатов у него нет
- Строка 57: `except Exception:` → `except Exception as e:`
- Строка 60: `run.error_message = str(run.pk)` → `run.error_message = str(e)`

### 3E. N+1 запросы при массовом пересчёте (Issue #13)

**Файл:** `backend/scoring/engine/persistence.py`

- В `refresh_all_ac_model_total_indices()`: строка 48 вызывает `update_model_total_index(ac)` который делает повторный SELECT (строка 24 `ACModel.objects.get(pk=ac_model.pk)`). Для каждой модели N запросов к Criterion и ModelRawValue.
- Решение: передавать уже загруженный объект в `compute_scores_for_model()` вместо повторной загрузки. Убрать `fresh = ACModel.objects.get(pk=ac_model.pk)` из `update_model_total_index()`, использовать переданный `ac_model` напрямую (он уже загружен с `select_related`)

### 3F. CategoricalScorer — неявный fallback (Issue #15)

**Файл:** `backend/scoring/scorers/categorical.py`

- Строки 26-29: после перебора `custom_scale_json`, если значение не найдено — вернуть `ScoreResult(normalized_score=0)`, а **не** проваливаться в `QUALITY_KEYWORDS`:
  ```python
  if criterion.custom_scale_json and isinstance(criterion.custom_scale_json, dict):
      for key, score in criterion.custom_scale_json.items():
          if val == str(key).strip().lower():
              return ScoreResult(normalized_score=float(score)).clamp()
      return ScoreResult(normalized_score=0)  # ← ДОБАВИТЬ
  ```

### 3G. LabScorer — whitelist вместо blacklist (Issue #16)

**Файл:** `backend/scoring/scorers/lab.py`

- Строка 23: заменить `if lab_status in ("not_measured", "pending", "not_in_mode"):` на `if lab_status != "measured":`

---

## Фаза 4: НИЗКИЕ — Точность, тесты, concurrent safety

### 4A. Float-точность (Issue #17)

- Существующее округление `round(..., 4)` / `round(..., 2)` достаточно для рейтинга
- Добавить `round()` в scorers где промежуточные вычисления могут накапливать ошибку (numeric.py пилообразная формула)

### 4B. Edge-case тесты (Issue #18)

Добавить тесты:
- Граничные значения на интервалах `[from, to)` для CustomScaleScorer и FormulaScorer
- `custom_scale_json = {}` (пустой dict)
- `median_by_capacity` с нечисловыми ключами
- BinaryScorer с `is_inverted=True`
- ~~Нормализация при сумме весов != 100~~ (отложено вместе с Issue #1)
- `nominal_capacity = 0` в FallbackScorer
- min > max в NumericScorer

### 4C. Мёртвый код (Issue #19)

- `validate_weights()` — оставить как есть (будет реализована при работе над Issue #1)

### 4D. Concurrent safety (Issue #20)

**Файл:** `backend/scoring/engine/batch.py`

- В начале `recalculate_all()` проверить наличие `CalculationRun` со статусом `RUNNING`:
  ```python
  if CalculationRun.objects.filter(status=CalculationRun.Status.RUNNING).exists():
      raise ValueError("Расчёт уже выполняется")
  ```
- Рассмотреть `select_for_update()` на ACModel в транзакции

---

## Фаза 5: ЗАМЕЧАНИЯ — Соответствие ТЗ

### 5A. Шкала обогрева (Issue #22)

- Проверить criterion `heating` — его `custom_scale_json` или `formula_json` должны соответствовать ТЗ:
  - Обогрев при -30°C и выше → 100
  - Обогрев при -25°C → 75
  - Обогрев при -20°C → 50
  - Обогрев при -15°C → 0
- При расхождении — data-миграция для исправления JSON

### 5B. help_text о весах (Issue #23)

- Отложено вместе с Issue #1 (нормализация весов)

---

## Миграции

1. **Фаза 2C:** `CheckConstraint` на `weight >= 0` — новая миграция
2. **Фаза 2A:** Возможна data-миграция для `median_by_capacity` если ключи в кВт → перевести в Вт
3. **Фаза 5A:** Возможна data-миграция для шкалы обогрева

---

## Верификация

### После каждой фазы:
```bash
cd backend && source venv/bin/activate
pytest scoring/tests/ methodology/tests/ -v
python3 -m py_compile scoring/engine/computation.py
python3 -m py_compile scoring/scorers/fallback.py
# ... все изменённые файлы
```

### Финальная проверка:
1. Запустить `recalculate_all()` — сравнить total_index до и после
2. Ранжирование моделей должно сохраниться
3. Админка: попробовать сохранить `is_inverted=True` на custom_scale → ожидаем ошибку
4. Запустить субагент `reviewer` для независимой проверки

### Критические файлы:
- `backend/scoring/engine/computation.py`
- `backend/scoring/engine/batch.py`
- `backend/scoring/engine/persistence.py`
- `backend/scoring/scorers/fallback.py`
- `backend/scoring/scorers/custom_scale.py`
- `backend/scoring/scorers/binary.py`
- `backend/scoring/scorers/categorical.py`
- `backend/scoring/scorers/lab.py`
- `backend/scoring/scorers/brand_age.py`
- `backend/scoring/scorers/numeric.py`
- `backend/methodology/models.py`
- `backend/methodology/admin/criterion_admin.py`
- `backend/scoring/tests/test_scorers.py`
- `backend/scoring/tests/test_engine.py`
