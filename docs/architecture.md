# Архитектура приложения

## Обзор

Приложение «Рейтинг кондиционеров» состоит из двух частей, связанных через REST API:

- **Бэкенд** — Django + Django REST Framework, PostgreSQL
- **Фронтенд** — Next.js (App Router) с серверным рендерингом (SSR) для SEO

```
┌──────────────┐     HTTP/JSON     ┌──────────────┐
│              │  ◄──────────────► │              │
│   Next.js    │   /api/...        │   Django     │
│   (SSR)      │                   │   (DRF)      │
│   Port 3000  │                   │   Port 8000  │
└──────────────┘                   └──────┬───────┘
                                          │
                                   ┌──────▼───────┐
                                   │  PostgreSQL   │
                                   │  Port 5432    │
                                   └──────────────┘
```

## Выбор технологий

| Компонент    | Технология         | Обоснование                                         |
|--------------|--------------------|-----------------------------------------------------|
| Бэкенд       | Django 5.1 + DRF   | Зрелый фреймворк, ORM, admin, миграции              |
| Фронтенд     | Next.js 16 (App Router) | SSR/SSG для SEO, React Server Components        |
| CSS          | Tailwind CSS 4     | Утилитарный подход, быстрая стилизация               |
| БД           | PostgreSQL 16      | Надёжность, полнотекстовый поиск, JSON-поддержка     |
| API          | REST (JSON)        | Простота, совместимость, стандартность                |

## Потоки данных

1. **Импорт данных**: xlsx-файл → management-команда `import_xlsx` → PostgreSQL
2. **Отображение рейтинга**: Next.js SSR → fetch `/api/conditioners/` → Django DRF → PostgreSQL
3. **Детальная страница**: Next.js SSR → fetch `/api/conditioners/{id}/` → Django DRF → PostgreSQL

## Структура проекта

```
backend/          Django-проект
  config/         Настройки (settings, urls, wsgi)
  ratings/        Приложение рейтинга (models, views, serializers, urls)
    management/   Команды управления (import_xlsx)
    tests/        Тесты бэкенда

frontend/         Next.js-проект
  src/app/        Страницы (App Router)
  src/components/ React-компоненты
  src/lib/        Типы и API-утилиты

docs/             Документация разработчика
```
