# Неактивные параметры на странице модели + спецоформление noise

## Контекст

На странице модели (`/{slug}`) список параметров формируется из `parameter_scores`, которые backend считает через `compute_scores_for_model`. Функция фильтрует `is_active=True`, поэтому если у критерия в активной методике снят чек-бокс «Активен», критерий **не появляется** в карточке модели вообще — даже если у модели есть замеренное значение.

По новому правилу:

1. **noise — особый**. Если у модели есть замер, его карточка должна быть **первой** в списке параметров и визуально выделена синей рамкой. Если у noise в методике снят `is_active` — «Вклад в индекс: 0.00», но карточка всё равно первой. Если замера нет — карточки нет.
2. **Остальные неактивные параметры.** Если у модели есть `raw_value` — показывать карточку с «Вклад в индекс: 0.00», место в списке определяется значением `weighted_score` (а т.к. он 0 — естественно уходят в конец).
3. **Сортировка** всего списка: noise всегда первый (если есть), далее по `weighted_score DESC` (чем больше вклад — тем выше).

Фронт-эндпоинт `ACModelListView` с `noise_mc` и таб «Самые тихие» — **не трогаем** (уже работает).

## Решение

### 1. Backend — `backend/catalog/serializers.py`

Переписать `ACModelDetailSerializer.get_parameter_scores` (строки 229–250):

- Активные критерии берём через существующий `compute_scores_for_model` (он и так фильтрует `is_active=True`) — **движок не трогаем**, сохраняем корректный расчёт `total_index`.
- Неактивные критерии подтягиваем отдельным запросом:
  ```python
  inactive_mcs = (
      methodology.methodology_criteria
      .filter(is_active=False)
      .select_related("criterion")
  )
  ```
- Для каждого неактивного: берём `ModelRawValue` модели. Если `raw_value` пустой — пропускаем. Иначе вычисляем `normalized_score` через `_get_scorer(mc).calculate(mc, raw, **model_ctx)`; `weighted_score = 0.0`.
- В возвращаемый dict каждого элемента добавляем поле `"is_active": bool` (для дебага/фронта; фронт само по себе оно может и не использовать, но поле полезное).
- Серверную сортировку `display_order` можно оставить — фронт всё равно пересортирует.
- Переиспользуем уже импортированные `_build_model_context`, `_get_scorer` из `scoring.engine.computation`.

Псевдокод добавляемого блока:
```python
_total, rows = compute_scores_for_model(obj, methodology)
for r in rows:
    r["is_active"] = True

# добор неактивных с непустым raw_value
raw_map = {rv.criterion_id: rv for rv in obj.raw_values.all() if rv.criterion_id}
model_ctx = _build_model_context(obj)
for mc in methodology.methodology_criteria.filter(is_active=False).select_related("criterion"):
    rv = raw_map.get(mc.criterion_id)
    if not rv or not (rv.raw_value or "").strip():
        continue
    scorer = _get_scorer(mc)
    if not scorer:
        continue
    ctx = {**model_ctx, "lab_status": rv.lab_status}
    result = scorer.calculate(mc, rv.raw_value, **ctx)
    rows.append({
        "criterion": mc,
        "raw_value": str(rv.raw_value),
        "compressor_model": rv.compressor_model or "",
        "normalized_score": round(result.normalized_score, 2),
        "weighted_score": 0.0,
        "above_reference": result.above_reference,
        "is_active": False,
    })
```
В финальном словаре на отдачу — добавить `"is_active": r["is_active"]`.

### 2. Frontend — `frontend/src/lib/types.ts`

Добавить в интерфейс `ParameterScore` поле:
```typescript
is_active: boolean;
```

### 3. Frontend — `frontend/src/app/[slug]/page.tsx` (строки 50–52)

Изменить сортировку:
```typescript
const sortedScores = [...model.parameter_scores].sort((a, b) => {
  if (a.criterion_code === "noise") return -1;
  if (b.criterion_code === "noise") return 1;
  return b.weighted_score - a.weighted_score
      || b.normalized_score - a.normalized_score;
});
```
Noise всегда первый, далее по `weighted_score DESC`, тай-брейкер — `normalized_score DESC`.

### 4. Frontend — `frontend/src/components/IndexCriterionCard.tsx`

Добавить условное выделение рамкой, если `criterion.criterion_code === "noise"`:
- root-элементу добавить класс `border-2 border-blue-400 dark:border-blue-500 rounded-lg p-3` (минимальная правка; если сейчас у карточки уже есть `rounded`/`p-*` — переиспользовать без дублирования).
- `weighted_score` уже приходит `0` для неактивных — отдельной логики для надписи «Вклад в индекс: 0.00» не нужно, существующая разметка отрендерит `weighted_score.toFixed(2)`.

## Ключевые файлы

| Файл | Изменение |
|------|-----------|
| `backend/catalog/serializers.py` (`ACModelDetailSerializer.get_parameter_scores`) | Добавить строки для неактивных критериев с непустым `raw_value`, поле `is_active` в каждом элементе |
| `frontend/src/lib/types.ts` (`ParameterScore`) | `is_active: boolean` |
| `frontend/src/app/[slug]/page.tsx` | Новая сортировка: noise → weighted_score DESC |
| `frontend/src/components/IndexCriterionCard.tsx` | Синяя рамка, если `criterion_code === "noise"` |

## Что НЕ трогаем

- `backend/scoring/engine/computation.py::compute_scores_for_model` — движок расчёта индекса остаётся как есть, `is_active=True` фильтр сохраняется → `total_index` считается корректно.
- `ACModelListView` / `ACModelListSerializer` / `noise_mc` / таб «Самые тихие» — уже работают.
- `MethodologySerializer.get_criteria` — публичная методика по-прежнему отдаёт только активные критерии.
- Предупреждение админу о пропаже noise в активной методике — уже реализовано.

## Проверка

1. `python3 -m py_compile backend/catalog/serializers.py`
2. `cd backend && source venv/bin/activate && python manage.py check`
3. `cd backend && pytest` — старые тесты не должны упасть.
4. Ручная проверка на `http://localhost:3000/MDV-NOVA_3-in-1-MDSAH-09HRFN8-MDOAH-09HFN8`:
   - Кейс A: noise активен, замер есть → карточка noise **первой**, с рамкой, вклад рассчитан и >0.
   - Кейс B: у noise снят `is_active`, замер есть → карточка noise **первой**, с рамкой, «Вклад в индекс: 0.00».
   - Кейс C: у noise нет замера → карточки noise **нет**; остальные по `weighted_score DESC`.
   - Кейс D: взять любой другой критерий (например `energy_a`), снять `is_active` в методике, у модели есть значение → карточка этого критерия есть в списке, «Вклад в индекс: 0.00», в самом низу списка (ибо 0).
   - Кейс E: неактивный критерий, у модели нет значения → карточки нет.
5. `curl http://localhost:8000/api/v2/models/<slug>/` — в `parameter_scores` присутствуют неактивные с `is_active: false`, `weighted_score: 0.0`.

---

План составлен, Максим. Перечитай и убедись, что всё сходится. Если что-то подправить — скажи, поправлю. Не приступаю к коду, пока не одобришь.
