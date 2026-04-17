# Рейтинг кондиционеров «Август-климат»

Независимый рейтинг бытовых кондиционеров (сплит-систем) на основе реальных лабораторных измерений: уровень шума, вибрация наружного блока, качество комплектующих, площадь теплообменников и функциональность.

## Стек

| Слой | Технологии |
|------|-----------|
| Backend | Django 5.1, Django REST Framework, PostgreSQL |
| Frontend | Next.js 16 (App Router, SSR/ISR), TypeScript, Tailwind CSS 4 |
| Деплой | Gunicorn + Nginx (backend), Node.js (frontend) |

## Быстрый старт

### Требования

- Python 3.11+
- Node.js 20+
- PostgreSQL 16+

### 1. Клонировать и настроить переменные окружения

```bash
git clone <repo-url> && cd ac-rating
cp backend/.env.example backend/.env     # отредактировать под свою БД
cp frontend/.env.example frontend/.env.local
```

### 2. Backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver  # http://localhost:8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev  # http://localhost:3000
```

### Docker (альтернативный способ)

```bash
docker compose up --build  # backend :8000, frontend :3000, postgres :5432
```

## Структура проекта

```
backend/
  config/          — Django settings (base / development / production)
  core/            — TimestampMixin, аудит, роли
  brands/          — Справочник брендов
  methodology/     — Критерии оценки, методики, веса
  catalog/         — Модели кондиционеров (ACModel), сырые значения, импорт
  scoring/         — Скоринг-движок, плагинные scorers
  reviews/         — Отзывы пользователей
  submissions/     — Заявки на добавление в рейтинг
  ratings/         — Legacy v1 (сохранён для миграции данных)

frontend/
  src/app/         — Next.js App Router (страницы)
  src/components/  — UI-компоненты (RatingTableV2, SubmitForm и др.)
  src/lib/         — API-клиент, типы, утилиты

docs/              — Документация (архитектура, API, деплой, тесты)
```

## API

Два поколения эндпоинтов работают параллельно:

| Версия | Базовый URL | Описание |
|--------|------------|----------|
| v1 | `/api/conditioners/`, `/api/v1/` | Legacy — приложение `ratings` |
| v2 | `/api/v2/` | Основной — приложение `catalog` |

Фронтенд использует v2. Подробности в [docs/api-reference.md](docs/api-reference.md).

## Ключевой data flow

1. Excel / форма заявки → `ModelRawValue` (одна строка на модель + критерий)
2. Scoring engine читает сырые значения + веса методики → вычисляет интегральный индекс
3. DRF-сериализаторы отдают данные → Next.js рендерит SSR/ISR

## Управление данными

Django Admin — основной интерфейс для работы с данными:
- Модели кондиционеров, их параметры и фотографии
- Методики оценки с критериями и весами
- Заявки от пользователей (премодерация → конвертация в ACModel)
- Справочник брендов

## Команды

```bash
# Backend (из backend/)
python manage.py runserver              # Dev-сервер
python manage.py import_v2 file.xlsx    # Импорт данных из Excel
python manage.py test                   # Тесты
pytest --cov=scoring --cov-report=html  # Тесты с покрытием

# Frontend (из frontend/)
npm run dev          # Dev-сервер
npm run build        # Продакшн-сборка
npm run lint         # ESLint
npm test             # Jest
```

## Документация

- [Архитектура](docs/architecture.md)
- [Модель данных](docs/data-model.md)
- [API-справочник](docs/api-reference.md)
- [Локальная разработка](docs/development.md)
- [Деплой](docs/deployment.md)
- [Тестирование](docs/testing.md)

## Лицензия

Проприетарный код. Все права защищены.
