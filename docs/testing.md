# Тестирование

## Бэкенд

Тесты расположены в `backend/ratings/tests/`.

### Запуск тестов

```bash
cd backend
source venv/bin/activate
pytest
```

### С отчётом покрытия

```bash
pytest --cov=ratings --cov-report=term-missing
```

### HTML-отчёт покрытия

```bash
pytest --cov=ratings --cov-report=html
open htmlcov/index.html
```

### Структура тестов

| Файл                   | Что тестирует                                          |
|------------------------|--------------------------------------------------------|
| `test_models.py`       | Создание, валидация, связи моделей, каскадное удаление |
| `test_api.py`          | HTTP-ответы, коды статусов, структура JSON             |
| `test_serializers.py`  | Корректность полей сериализаторов                      |
| `test_import.py`       | Импорт из xlsx, пустые строки, идемпотентность         |

### Фикстуры (conftest.py)

- `sample_ac` — кондиционер с базовыми полями
- `sample_ac_with_params` — кондиционер со всеми 12 параметрами
- `second_ac` — второй кондиционер для тестов сортировки

---

## Фронтенд

Тесты расположены в `frontend/src/__tests__/`.

### Запуск тестов

```bash
cd frontend
npm test
```

### С отчётом покрытия

```bash
npm run test:coverage
```

### Структура тестов

| Файл                      | Что тестирует                                    |
|---------------------------|--------------------------------------------------|
| `RatingTable.test.tsx`    | Рендеринг таблицы, ссылки, позиции, пустое состояние |
| `ParameterBar.test.tsx`   | Отображение параметра, progress bar, единицы     |
| `VideoLinks.test.tsx`     | Видеоссылки, iframe embed, пустое состояние      |

### Используемые библиотеки

- **Jest** — тест-раннер
- **React Testing Library** — тестирование React-компонентов
