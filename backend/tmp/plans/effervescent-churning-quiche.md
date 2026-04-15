# План: Аудит + исправление критических проблем

## Контекст

Проведён глубокий аудит бэкенда и фронтенда. Проект работает, но есть реальные проблемы, которые стоит исправить до дальнейших доработок. Ниже — только то, что стоит чинить, сгруппировано по приоритету.

---

## Фаза 1: CRITICAL — исправить сейчас

### 1.1 Division by zero в NumericScorer
**Файл:** `backend/scoring/scorers/numeric.py:60-68`
**Проблема:** Если `median == min` или `median == max`, деление на ноль.
**Фикс:** Добавить guard: если `md == mn` или `md == mx`, считать без медианы (линейная шкала).

### 1.2 N+1 запросы в детальном сериализаторе
**Файл:** `backend/catalog/serializers.py:193-204`
**Проблема:** `_get_latest_run_id()` вызывает `calculation_results.all()` дважды.
**Фикс:** Кэшировать результат или использовать `.order_by('-run_id').first()`.

### 1.3 Миграция raw_values без транзакции
**Файл:** `backend/catalog/services/raw_values_migration.py`
**Проблема:** `bulk_create` без `transaction.atomic()` — при сбое частичные данные.
**Фикс:** Обернуть функцию в `@transaction.atomic()`.

### 1.4 JSON.parse без защиты в api.ts
**Файл:** `frontend/src/lib/api.ts:48`
**Проблема:** `res.json()` может упасть если тело не валидный JSON (502 с HTML).
**Фикс:** Обернуть `res.json()` в try-catch, бросать `ApiError`.

---

## Фаза 2: WARNING — исправить в этом спринте

### 2.1 Добавить db_index на часто фильтруемые поля
**Файл:** `backend/catalog/models.py` — `verification_status`, `lab_status`
**Фикс:** Миграция с `db_index=True`.

### 2.2 Alt-текст для логотипов брендов
**Файл:** `frontend/src/components/RatingTableV2.tsx:85`
**Фикс:** `alt=""` → `alt={m.brand}`.

### 2.3 Удалить мёртвый код v1
**Файлы:**
- `frontend/src/components/RatingTable.tsx` — не импортируется нигде
- `frontend/src/lib/api.ts:82-89` — `getConditioners()`, `getConditioner()`
- `frontend/src/lib/types.ts:123-145` — v1 типы
- `frontend/src/app/conditioner/` — v1 route (если не нужен)
**Фикс:** Удалить неиспользуемый код.

### 2.4 Scorer edge cases — тесты
**Файл:** `backend/scoring/tests/test_scorers.py`
**Добавить тесты:**
- NumericScorer: median == min, median == max
- CustomScaleScorer: значение вне всех интервалов
- FallbackScorer: brand без origin_class
- BrandAgeScorer: NULL sales_start_year_ru

---

## Фаза 3: Тесты для непокрытых путей

### 3.1 Тесты v2 API (catalog app) — ОТСУТСТВУЮТ ПОЛНОСТЬЮ
**Создать:** `backend/catalog/tests/test_api.py`
- GET /v2/models/ — фильтрация по brand, capacity, price, region
- GET /v2/models/{id}/ — детальный ответ
- GET /v2/models/by-slug/{slug}/ — поиск по slug
- GET /v2/models/archive/ — архивные модели
- GET /v2/methodology/ — методология

### 3.2 Тесты raw_values_migration
**Создать:** `backend/catalog/tests/test_raw_values_migration.py`
- Миграция между методиками с совпадающими кодами
- Пропуск критериев без совпадения
- Не перезаписывать существующие значения

### 3.3 Фронтенд — тесты критических компонентов
- `CustomRatingPanel` — toggle чекбоксов, кнопка "Включить все"
- `RatingPageContent` — переключение табов, custom index
- `PhotoGallery` — lightbox, keyboard navigation

---

## Файлы для изменений

### Бэкенд:
- `scoring/scorers/numeric.py` — guard div/0
- `catalog/serializers.py` — fix N+1
- `catalog/services/raw_values_migration.py` — transaction.atomic
- `catalog/models.py` — db_index миграция
- `scoring/tests/test_scorers.py` — edge case тесты
- `catalog/tests/test_api.py` — НОВЫЙ
- `catalog/tests/test_raw_values_migration.py` — НОВЫЙ

### Фронтенд:
- `src/lib/api.ts` — json parse guard
- `src/components/RatingTableV2.tsx` — alt text
- Удаление: `src/components/RatingTable.tsx`, v1 types/api/routes

---

## Проверка

- `./venv/bin/python -m pytest` — все тесты проходят
- `npx tsc --noEmit` — без ошибок
- `npx jest` — все тесты проходят
- Django system check — без новых warnings
- Ручная проверка: главная, страница модели, архив
