# План: загрузка фотографий для моделей кондиционеров без фото

## Context

В БД `catalog_acmodel` — 26 моделей, у 24 нет ни одной `ACModelPhoto`. Нужно найти в интернете фото (внутренний блок, наружный блок, пульт — до 3 шт на модель) и загрузить только те, в которых есть уверенность, что это именно та модель (виден артикул на странице-источнике).

Поле `photo_type` в `ACModelPhoto` отсутствует — тип фото кодируется через `order` (1=внутр, 2=наруж, 3=пульт) и дублируется человекочитаемо в `alt`.

Фронтенд `PhotoGallery` на `frontend/src/app/[slug]/page.tsx:144` уже готов рендерить массив `photos` по порядку — никаких правок фронта не нужно.

## Принципы

- **Точность > покрытие**: нет артикула на странице-источнике → не грузим. Лучше 0 фото, чем чужая модель.
- **Частичные наборы OK**: нашлось 2 из 3 — грузим 2, пропуск в `order` допустим.
- **Идемпотентность**: повторный запуск не плодит дубли.

## Workflow (в две фазы)

### Фаза A — Research (делаю я в чате, не скриптом)

Для каждой из 24 моделей (список — см. ниже) запускаю research-сабагента с промптом вида:

> Найди официальные/магазинные страницы, где явно виден артикул `<inner_unit>` / `<outer_unit>` бренда `<brand>`. Для каждой страницы, где артикул подтверждён, верни URL-ы прямых картинок (`<img src>`):
> 1. Внутренний блок
> 2. Наружный блок
> 3. Пульт ДУ
> Верни JSON: `{"slug": "...", "indoor": {"url": "...", "source": "..."} | null, "outdoor": {...} | null, "remote": {...} | null, "notes": "..."}`. Если артикул нигде не подтверждён — все поля null.

Результаты агрегирую в `tmp/photos_manifest.json`.

**Бренды, для которых ожидаю реальные источники**: LG, Midea, Haier, Mitsubishi Heavy, MDV, Royal Clima, AUX, FUNAI, Rovex, Energolux, Kalashnikov, Hyundai, Ballu, Electrolux, Samsung.

**Подозрительные** (бренд/артикул выглядит тестовым — вероятно будет null): `THAICON-SENSAIR-TL-RWS25-FR`, `FeRRUM-Titan_inv_-IFIS09VR`, `AQUA-Towada`. Честно пропущу, если не подтвердится.

### Фаза B — Загрузка скриптом

Создаю `tmp/fetch_photos.py` (разовый, как просил Максим). Скрипт:

1. Запускается из `backend/` через `./venv/bin/python ../tmp/fetch_photos.py`
2. `django.setup()` с `DJANGO_SETTINGS_MODULE=config.settings.development`
3. Читает `tmp/photos_manifest.json`
4. По каждой записи:
   - `ACModel.objects.get(slug=entry["slug"])`
   - Если у модели уже есть `photos.exists()` — пропуск (лог `SKIP already has photos`)
   - Для каждого из `indoor/outdoor/remote`:
     - `requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})`
     - Проверка `Content-Type` начинается на `image/`, размер > 5 КБ
     - `ACModelPhoto.objects.create(model=m, order=<1|2|3>, alt="Внутренний блок"|"Наружный блок"|"Пульт ДУ")` и `photo.image.save(f"{slug}-{order}.jpg", ContentFile(resp.content))`
   - Ошибки ловятся per-photo → лог и продолжаем
5. Финальная сводка: `X моделей обработано, Y фото загружено, Z пропущено, N ошибок`

## Файлы

**Новые:**
- `tmp/photos_manifest.json` — результат research-фазы (ручной/агентный сбор)
- `tmp/fetch_photos.py` — скрипт загрузки

**Чтение:**
- `backend/catalog/models.py:211` — `ACModelPhoto` (структура)
- `backend/catalog/serializers.py:81` — как сериализуется (подтверждает что `alt`/`order` достаточно)
- `backend/config/settings/base.py:89` — `MEDIA_ROOT = BASE_DIR/media`

**НЕ меняем**: ни модели, ни миграции, ни admin, ни фронт.

## Переиспользуем

- `ImageField.save(name, ContentFile)` — стандартный Django, файл ляжет в `backend/media/ac_photos/`
- `request.build_absolute_uri(obj.image.url)` в `ACModelPhotoSerializer.get_image_url` — уже отдаёт абсолютный URL фронту
- `PhotoGallery` (frontend) — рендерит по `order` без доработок

## Список 24 моделей (slug → бренд/артикул)

Полный список доступен через `ACModel.objects.filter(photos__isnull=True)`; в research-фазе итерирую по нему программно.

## Verification

1. `./venv/bin/python ../tmp/fetch_photos.py` — скрипт отрабатывает без крэша, выводит сводку
2. `./venv/bin/python manage.py shell -c "from catalog.models import ACModelPhoto; print(ACModelPhoto.objects.count())"` — число выросло
3. `ls backend/media/ac_photos/` — файлы на месте
4. `curl -s http://localhost:8000/api/v2/models/by-slug/<slug>/ | python3 -m json.tool | grep -A3 photos` — в ответе появился массив `photos` с `image_url`
5. Открыть `http://localhost:3000/<slug>` для 2-3 моделей — галерея отображает фото в правильном порядке (внутр→наруж→пульт), lightbox работает
6. Идемпотентность: повторный запуск скрипта → `SKIP already has photos` для всех обработанных

## Риски и как митигирую

- **Антибот/403 на прямой `requests.get`**: если источник блокирует — в manifest пишу `null` для этого фото (не загружаю битое)
- **Сомнительный бренд (THAICON/FeRRUM/AQUA)**: если research не подтверждает артикул — пропускаю модель целиком
- **iCloud-путь с пробелами**: команды запускаю с правильным кавычением; венв-python через абсолютный путь
- **Объём**: 24 модели × 3 типа = до 72 поисков. Research-фазу выполняю батчами по ~5 моделей, чтобы не упереться в лимиты; между батчами показываю Максиму промежуточный manifest для одобрения, прежде чем грузить

## Что НЕ делаю (подтверждение scope)

- Не добавляю поле `photo_type` в модель (Максим выбрал `order`-конвенцию)
- Не правлю admin/inlines
- Не трогаю модели с уже существующими фото
- Не публикую автоматически — модели уже в своих текущих статусах, статус не меняю
