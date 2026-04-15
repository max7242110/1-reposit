# Задачи доработки от 14 апреля

## Контекст

Три задачи для развития проекта рейтинга кондиционеров:
1. **Фото критерия** — добавить возможность загружать фото для каждого параметра из админки
2. **Страница «Методика рейтинга»** — подробная страница для пользователя: как считается рейтинг, описание каждого критерия с весом, типом оценки, min/max/median и фото
3. **Страница «Добавить в рейтинг»** — редактируемая из админки страница с инструкцией и ссылкой на Google-форму

**Зависимости**: Задача 1 → блокирует Задачу 2 (фото отображается на странице методики). Задача 3 — независима.

---

## Задача 1: Фото критерия

### Backend

**1.1 Модель** — `backend/methodology/models.py`
Добавить `ImageField` в `Criterion` (после `description_pt`, ~строка 102):
```python
photo = models.ImageField(upload_to="criteria/", blank=True, default="", verbose_name="Фото")
```
Паттерн: аналогично `Brand.logo = ImageField(upload_to="brands/")`.

**1.2 Миграция** — `makemigrations methodology` → `0027_criterion_photo.py`

**1.3 Админка** — `backend/methodology/admin/criterion_admin.py`
Добавить `"photo"` в fieldset «Основное» после `"unit"`.

**1.4 Сериализатор** — `backend/catalog/serializers.py`
В `MethodologyCriterionSerializer` добавить `photo_url = SerializerMethodField()`:
```python
def get_photo_url(self, obj):
    photo = obj.criterion.photo
    if not photo:
        return ""
    request = self.context.get("request")
    return request.build_absolute_uri(photo.url) if request else photo.url
```
Добавить `"photo_url"` в `fields`.

### Frontend

**1.5 Тип** — `frontend/src/lib/types.ts`
В `CriterionInfo` добавить `photo_url: string`.

---

## Задача 2: Страница «Методика рейтинга»

### Backend

**2.1 Описания критериев** — data migration `backend/methodology/migrations/0028_populate_criterion_descriptions.py`

Заполнить `description_ru` для всех 34 критериев (сейчас все пустые). Каждое описание 2-4 предложения: что измеряет, почему важно для пользователя, принцип оценки. Обновлять только пустые (`description_ru=""`), чтобы не затирать правки из админки.

34 кода: `air_freshener, alice_control, brand_age_ru, compressor_power, drain_pan_heater, energy_efficiency, erv, fan_speed_outdoor, fan_speeds_indoor, fine_filters, fresh_air, heat_exchanger_inner, heat_exchanger_outer, heating_capability, inverter, ionizer_type, ir_sensor, louver_control, max_height_diff, max_pipe_length, min_voltage, noise, remote_backlight, remote_holder, russian_remote, self_clean_freezing, standby_heating, temp_sterilization, tolschina_heat_outdoor, tolschina-NB, uv_lamp, vibration, warranty, wifi`

### Frontend

**2.2 Страница** — создать `frontend/src/app/methodology/page.tsx`
- Server component (async), `getMethodology()` fetch
- `BackLink` → `/`
- `<h1>` «Методика рейтинга «Август-климат»»
- Шапка: `methodology.description` (из поля «Описание» активной методики)
- Сводка: кол-во критериев, сумма весов
- Карточки критериев (отсортированы по `display_order`):
  - Фото слева (если `photo_url`), `<img loading="lazy">`
  - Название `<h3>`, бейдж веса (напр. «8%»)
  - `description_ru` — текст описания
  - Тип оценки (человеко-понятная метка), min/median/max, ед. измерения

**2.3 Словарь меток типа скоринга** (внутри страницы или в `utils.ts`):
```typescript
const SCORING_LABELS: Record<string, string> = {
  min_median_max: "Линейная шкала (min → медиана → max)",
  binary: "Да / Нет",
  universal_scale: "Универсальная шкала",
  custom_scale: "Индивидуальная шкала",
  formula: "Расчёт по формуле",
  interval: "Интервальная шкала",
};
```

**2.4 Ссылка в footer** — `frontend/src/app/layout.tsx`
```tsx
<Link href="/methodology">Методика рейтинга</Link>
```

---

## Задача 3: Страница «Добавить в рейтинг»

### Backend

**3.1 Модель Page** — `backend/core/models.py`
```python
class Page(TimestampMixin):
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL-slug")
    title_ru = models.CharField(max_length=255, verbose_name="Заголовок")
    content_ru = models.TextField(verbose_name="Контент (HTML)")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
```
Минимальная модель — одна страница = одна запись. HTML-контент редактируется через админку.

**3.2 Миграция** — `makemigrations core` (первая миграция для core)

**3.3 Админка** — `backend/core/admin.py`
Дополнить `PageAdmin`: list_display, prepopulated_fields slug, search_fields.

**3.4 API** — новые файлы:
- `backend/core/serializers.py` — `PageSerializer(slug, title_ru, content_ru)`
- `backend/core/views.py` — `PageDetailView(RetrieveAPIView, lookup_field="slug")`
- `backend/core/urls.py` — `path("pages/<slug:slug>/", ...)`
- `backend/config/urls.py` — `path("api/v2/", include("core.urls"))`

**3.5 Начальный контент** — data migration
Создать страницу `slug="submit"` с title и HTML-контентом (инструкция + placeholder-ссылка на Google-форму).

### Frontend

**3.6 API-клиент** — `frontend/src/lib/api.ts`
```typescript
export interface PageContent { slug: string; title_ru: string; content_ru: string; }
export async function getPage(slug: string): Promise<PageContent> { ... }
```

**3.7 Страница** — создать `frontend/src/app/submit/page.tsx`
- Server component, `getPage("submit")`
- `BackLink` → `/`, `<h1>` из `page.title_ru`
- `dangerouslySetInnerHTML` из `page.content_ru` (доверенный контент)
- Tailwind `prose dark:prose-invert` для стилизации HTML

**3.8 @tailwindcss/typography** — НЕ установлен, нужно:
- `npm install @tailwindcss/typography`
- В `globals.css`: `@plugin "@tailwindcss/typography"` (Tailwind CSS 4)

**3.9 Ссылки**
- Footer (`layout.tsx`): `<Link href="/submit">Добавить в рейтинг</Link>`
- Главная (`RatingPageContent.tsx`): заметная CTA-кнопка/ссылка

---

## Порядок реализации

```
Фаза 1: Задача 1 (фото критерия)
  1.1 модель → 1.2 миграция → 1.3 админка → 1.4 сериализатор → 1.5 тип

Фаза 2 (параллельно):
  Задача 2: 2.1 описания → 2.2 страница → 2.3 метки → 2.4 footer
  Задача 3: 3.1 модель → 3.2 миграция → 3.3 админка → 3.4 API → 3.5 контент
           → 3.6 клиент → 3.7 страница → 3.8 typography → 3.9 ссылки
```

---

## Проверка

1. **Фото**: загрузить фото через `/admin/methodology/criterion/`, `curl /api/v2/methodology/` содержит `photo_url`
2. **Методика**: `localhost:3000/methodology/` — шапка, карточки с описаниями и фото, ссылка в footer
3. **Добавить**: создать/отредактировать через `/admin/core/page/`, `localhost:3000/submit/` — HTML рендерится
4. `py_compile` всех .py, `pytest`, `manage.py check`
5. Фронтенд: `npm run dev` — обе страницы рендерятся, ссылки в footer и на главной работают

---

## Ключевые файлы

| Файл | Изменения |
|------|-----------|
| `backend/methodology/models.py` | ImageField photo |
| `backend/methodology/admin/criterion_admin.py` | photo в fieldset |
| `backend/catalog/serializers.py` | photo_url в MethodologyCriterionSerializer |
| `backend/core/models.py` | Новая модель Page |
| `backend/core/admin.py` | PageAdmin |
| `backend/core/serializers.py` | **Новый**: PageSerializer |
| `backend/core/views.py` | **Новый**: PageDetailView |
| `backend/core/urls.py` | **Новый**: URL pages |
| `backend/config/urls.py` | include core.urls |
| `frontend/src/lib/types.ts` | photo_url, PageContent |
| `frontend/src/lib/api.ts` | getPage() |
| `frontend/src/app/methodology/page.tsx` | **Новый** |
| `frontend/src/app/submit/page.tsx` | **Новый** |
| `frontend/src/app/layout.tsx` | Ссылки в footer |
| `frontend/src/components/RatingPageContent.tsx` | CTA-ссылка |
