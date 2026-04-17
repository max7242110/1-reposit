# Frontend — Рейтинг кондиционеров

Next.js 16 приложение (App Router) с серверным рендерингом и ISR-кэшированием.

## Стек

- **Next.js 16** — App Router, SSR/ISR
- **React 19** — UI
- **TypeScript** — строгий режим
- **Tailwind CSS 4** — стилизация

## Запуск

```bash
cp .env.example .env.local   # настроить API URL
npm install
npm run dev                  # http://localhost:3000
```

## Переменные окружения

| Переменная | Описание | По умолчанию |
|-----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | URL бэкенда | `http://localhost:8000/api` |
| `NEXT_PUBLIC_SITE_URL` | URL сайта (для canonical, OG) | `http://localhost:3000` |

## Структура

```
src/
  app/              — Страницы (App Router)
    page.tsx        — Главная (рейтинг с табами и фильтрами)
    [slug]/         — Карточка модели
    quiet/          — Рейтинг тихих кондиционеров (SEO)
    price/[slug]/   — Рейтинг по ценовым сегментам (SEO)
    submit/         — Форма заявки
    methodology/    — Страница методики
    archive/        — Архивные модели
  components/       — UI-компоненты
  lib/
    api.ts          — API-клиент (v1 + v2)
    types.ts        — TypeScript-типы
    year.ts         — Утилита для текущего года рейтинга
```

## Команды

```bash
npm run dev          # Dev-сервер с HMR
npm run build        # Продакшн-сборка
npm start            # Запуск продакшн-сборки
npm run lint         # ESLint
npm test             # Jest-тесты
npm run test:coverage # Тесты с покрытием
```

## ISR-кэширование

Страницы используют `revalidate` для ISR:
- Главная, quiet, price — `86400` (24 часа)
- Submit, methodology — `60` (1 минута, CMS-контент)
- Карточка модели — `86400`
