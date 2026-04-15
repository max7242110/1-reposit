# Спецправило для параметра «Замер уровня шума»

## Контекст

На фронтенде есть таб «Самые тихие кондиционеры», который сортирует модели по `noise_score`. Сейчас этот балл берётся из кэша скоров, который строится только из активных (`is_active=True`) `MethodologyCriterion` активной методики. Если в активной методике у параметра `noise` снят чек-бокс «Активен» (или его вообще нет) — `noise_score` и `has_noise_measurement` становятся None/False, и таб «Самые тихие» оказывается пустым.

Максим решил: параметр `noise` — особый. Если в активной методике у него снят `is_active` — он НЕ участвует в расчёте общего индекса (это уже работает из коробки), но **всё равно** должен считаться для таба «Самые тихие». Если `MethodologyCriterion` с кодом `noise` в активной методике вообще отсутствует — показывать админу предупреждение.

Правило касается только кода `noise` — хардкод в коде приемлем.

## Решение

**Суть:** в serializer context дополнительно класть `noise_mc` — найденный в активной методике `MethodologyCriterion` для `noise`, **игнорируя `is_active`**. Serializer-методы `get_noise_score` и `get_has_noise_measurement` используют этот объект отдельно от основного `criteria` списка.

### 1. Backend — `catalog/views/ac_models.py`

В `ACModelListView.get_serializer_context()` добавить отдельный поиск `noise_mc` без фильтра `is_active`:

```python
ctx["noise_mc"] = (
    MethodologyCriterion.objects
    .filter(methodology=active, criterion__code="noise")
    .select_related("criterion")
    .first()
) if active else None
```

Основной `criteria` список (с фильтром `is_active=True`) остаётся как есть — шум автоматически исключается из общего индекса, когда чек-бокс снят.

### 2. Backend — `catalog/serializers.py`

Переписать `get_noise_score` и `get_has_noise_measurement`, чтобы они не зависели от `_scores_cache`, а считали через `noise_mc` из контекста:

```python
def _get_noise_score(self, obj: ACModel) -> float | None:
    if hasattr(obj, "_noise_score_cache"):
        return obj._noise_score_cache

    noise_mc = self.context.get("noise_mc")
    score = None
    if noise_mc:
        rv = next(
            (r for r in obj.raw_values.all()
             if r.criterion_id == noise_mc.criterion_id),
            None,
        )
        raw = rv.raw_value if rv else ""
        scorer = _get_scorer(noise_mc)
        if scorer:
            model_ctx = _build_model_context(obj)
            if rv:
                model_ctx["lab_status"] = rv.lab_status
            result = scorer.calculate(noise_mc, raw, **model_ctx)
            score = round(result.normalized_score, 2)
    obj._noise_score_cache = score
    return score

def get_noise_score(self, obj: ACModel) -> float | None:
    return self._get_noise_score(obj)

def get_has_noise_measurement(self, obj: ACModel) -> bool:
    score = self._get_noise_score(obj)
    return score is not None and score > 0
```

`get_scores` (словарь всех скоров для общего индекса) по-прежнему использует `_get_scores_cache` и **не** включает `noise`, если он снят с `is_active`. То есть в детальной карточке и в расчёте индекса шум отсутствует — это ожидаемо.

### 3. Backend — предупреждение админу

В `methodology/admin/methodology_version.py` для `MethodologyVersionAdmin.changelist_view` (и `change_view`) — показать `messages.warning`, если у активной методики нет `MethodologyCriterion` с `criterion__code="noise"` (ни активного, ни неактивного):

```python
def _check_noise_presence(self, request):
    active = MethodologyVersion.objects.filter(is_active=True).first()
    if not active:
        return
    has_noise = MethodologyCriterion.objects.filter(
        methodology=active, criterion__code="noise",
    ).exists()
    if not has_noise:
        messages.warning(
            request,
            "В активной методике отсутствует параметр «Замер уровня шума» (code=noise). "
            "Таб «Самые тихие кондиционеры» на фронтенде будет пустым. "
            "Добавьте параметр в активную методику (можно со снятым чек-боксом «Активен»).",
        )

def changelist_view(self, request, extra_context=None):
    self._check_noise_presence(request)
    return super().changelist_view(request, extra_context)
```

Если `is_active=False` — предупреждение НЕ показываем, потому что это штатный режим по новому правилу (параметр в методике есть, просто не учитывается в индексе).

## Ключевые файлы

| Файл | Изменение |
|------|-----------|
| `backend/catalog/views/ac_models.py` | + `noise_mc` в `get_serializer_context` |
| `backend/catalog/serializers.py` | `get_noise_score`/`get_has_noise_measurement` считают через `noise_mc` отдельным путём |
| `backend/methodology/admin/methodology_version.py` | `messages.warning`, если в активной методике нет noise |

Frontend — **не трогаем**. `RatingPageContent.tsx` уже фильтрует по `has_noise_measurement` — всё заработает автоматически.

## Проверка

1. `python3 -m py_compile` для изменённых файлов
2. `python manage.py check`
3. `pytest` — старые тесты не должны упасть
4. Ручная проверка:
   - В активной методике у `noise` стоит `is_active=True` → таб «По индексу» включает шум, таб «Самые тихие» работает
   - Снять `is_active` у noise → таб «По индексу» шум НЕ учитывает, но таб «Самые тихие» всё ещё работает
   - Удалить `MethodologyCriterion` noise полностью → при заходе в админку методики показывается warning
5. `curl http://localhost:8000/api/v2/models/` — в ответе `noise_score` и `has_noise_measurement=true` для моделей с замером, независимо от `is_active` у noise в методике

---

План составлен, Максим. Перечитай его и убедись, что он идеален. Если хочешь что-то изменить — скажи, поправлю. Не приступаю к коду, пока не одобришь.
