# Деплой

## Переменные окружения (production)

### Бэкенд

| Переменная               | Описание                          | Пример                    |
|--------------------------|-----------------------------------|---------------------------|
| `DJANGO_SECRET_KEY`      | Секретный ключ Django             | Сгенерировать!            |
| `DJANGO_DEBUG`           | Режим отладки                     | `False`                   |
| `DJANGO_ALLOWED_HOSTS`   | Разрешённые хосты                 | `api.example.com`         |
| `POSTGRES_DB`            | Имя базы данных                   | `ac_rating`               |
| `POSTGRES_USER`          | Пользователь PostgreSQL           | `ac_user`                 |
| `POSTGRES_PASSWORD`      | Пароль PostgreSQL                 | `...`                     |
| `POSTGRES_HOST`          | Хост PostgreSQL                   | `localhost`               |
| `POSTGRES_PORT`          | Порт PostgreSQL                   | `5432`                    |
| `CORS_ALLOWED_ORIGINS`   | Разрешённые CORS origins          | `https://example.com`     |

### Фронтенд

| Переменная            | Описание          | Пример                              |
|-----------------------|-------------------|--------------------------------------|
| `NEXT_PUBLIC_API_URL` | URL бэкенд API    | `https://api.example.com/api`       |

## Запуск бэкенда (Gunicorn)

```bash
cd backend
source venv/bin/activate
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

## Сборка и запуск фронтенда

```bash
cd frontend
npm run build
npm start
```

## Nginx (пример конфигурации)

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Чеклист деплоя

- [ ] Установить `DJANGO_SECRET_KEY` (уникальный, случайный)
- [ ] Установить `DJANGO_DEBUG=False`
- [ ] Настроить `DJANGO_ALLOWED_HOSTS`
- [ ] Настроить `CORS_ALLOWED_ORIGINS`
- [ ] Создать базу данных PostgreSQL
- [ ] Выполнить миграции: `python manage.py migrate`
- [ ] Импортировать данные: `python manage.py import_xlsx`
- [ ] Собрать статику: `python manage.py collectstatic`
- [ ] Собрать фронтенд: `npm run build`
- [ ] Настроить HTTPS (Let's Encrypt / Cloudflare)
