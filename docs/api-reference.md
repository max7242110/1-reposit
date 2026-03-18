# API Reference

Базовый URL: `http://localhost:8000/api`

## Список кондиционеров

```
GET /api/conditioners/
```

Возвращает список всех кондиционеров, отсортированных по убыванию итогового балла.

### Ответ (200 OK)

```json
[
  {
    "id": 1,
    "rank": 8,
    "brand": "Фунай ONSEN",
    "model_name": "RAC-I-ON30HP.D01/S / RAC-I-ON30HP.D01/U",
    "total_score": 297.6
  },
  {
    "id": 2,
    "rank": 2,
    "brand": "LG Deluxe Pro",
    "model_name": "LG H12S1D.NS1R / H12S1D.U12R",
    "total_score": 242.3
  }
]
```

### Поля

| Поле         | Тип    | Описание                      |
|--------------|--------|-------------------------------|
| id           | int    | Уникальный идентификатор       |
| rank         | int    | Позиция в исходной таблице     |
| brand        | string | Бренд / название               |
| model_name   | string | Модель                         |
| total_score  | float  | Итоговый суммарный балл        |

---

## Детали кондиционера

```
GET /api/conditioners/{id}/
```

Возвращает полную информацию о кондиционере, включая параметры и видеоссылки.

### Параметры пути

| Параметр | Тип | Описание            |
|----------|-----|---------------------|
| id       | int | ID кондиционера     |

### Ответ (200 OK)

```json
{
  "id": 1,
  "rank": 8,
  "brand": "Фунай ONSEN",
  "model_name": "RAC-I-ON30HP.D01/S / RAC-I-ON30HP.D01/U",
  "youtube_url": "https://youtu.be/...",
  "rutube_url": "https://rutube.ru/video/...",
  "vk_url": "https://vk.com/video-...",
  "total_score": 297.6,
  "parameters": [
    {
      "id": 1,
      "parameter_name": "Шум мин.",
      "raw_value": "32",
      "unit": "дБ(А)",
      "score": 36.0
    }
  ]
}
```

### Ответ (404 Not Found)

```json
{
  "detail": "No AirConditioner matches the given query."
}
```

---

## CORS

Разрешённые origins настраиваются через переменную окружения `CORS_ALLOWED_ORIGINS` (по умолчанию: `http://localhost:3000`).
