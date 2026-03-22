# Локальная разработка

## Требования

- Python 3.11+
- Node.js 20+
- PostgreSQL 16+

## 1. Клонирование

```bash
git clone git@github.com:max7242110/1-reposit.git
cd 1-reposit
```

## 2. Бэкенд (Django)

```bash
cd backend

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# Установка зависимостей
pip install -r requirements.txt

# Настройка БД
createdb ac_rating  # или через psql: CREATE DATABASE ac_rating;

# Запуск PostgreSQL (Homebrew). Если `brew` в `~/homebrew`:
export PATH="$HOME/homebrew/bin:$PATH"
brew services start postgresql@16

# Чтобы Django использовал PostgreSQL, не задавайте `DJANGO_USE_SQLITE`
# (в `config/settings/development.py` SQLite включается только при DJANGO_USE_SQLITE=1).

# Переменные окружения (опционально)
export POSTGRES_DB=ac_rating
export POSTGRES_USER=$USER
export POSTGRES_PASSWORD=
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432

# Миграции
python manage.py migrate

# Импорт данных из xlsx
python manage.py import_xlsx

# Запуск сервера разработки
python manage.py runserver
```

Бэкенд будет доступен на `http://localhost:8000`.

### Приложение `catalog` (рефакторинг структуры)

- **`catalog/admin/`** — пакет админки: `ac_model_admin`, `equipment_admin`, `forms`, `inlines`, `datalist`, `constants`
- **`catalog/services/`** — логика без HTTP (например `ensure_all_criteria_rows` для строк критериев)
- **`catalog/signals.py`** — пересчёт итогового индекса моделей при изменении полей бренда

## 3. Фронтенд (Next.js)

```bash
cd frontend

# Установка зависимостей
npm install

# Переменные окружения
echo 'NEXT_PUBLIC_API_URL=http://localhost:8000/api' > .env.local

# Запуск сервера разработки
npm run dev
```

Фронтенд будет доступен на `http://localhost:3000`.

## 4. Проверка работы

1. Откройте `http://localhost:8000/api/conditioners/` — должен вернуться JSON со списком кондиционеров
2. Откройте `http://localhost:3000` — должна отображаться таблица рейтинга
3. Кликните на любую строку — откроется детальная страница с параметрами и видео

## Полезные команды

```bash
# Django admin (создать суперпользователя)
python manage.py createsuperuser
# Каталог моделей и критерии: http://localhost:8000/admin/catalog/
# Раздел /admin/ratings/ (v1) в админке отключён; API /api/v1/ при необходимости сохраняется

# Тесты бэкенда
cd backend && source venv/bin/activate
pytest --cov=ratings

# Тесты фронтенда
cd frontend
npm test
npm run test:coverage
```
