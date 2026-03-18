# Модель данных

## ER-диаграмма

```
┌─────────────────────────┐       ┌─────────────────────────┐
│    AirConditioner       │       │    ParameterValue       │
├─────────────────────────┤       ├─────────────────────────┤
│ id          BIGINT PK   │ 1───* │ id              BIGINT PK │
│ rank        INT          │       │ air_conditioner FK       │
│ brand       VARCHAR(255) │       │ parameter_name  VARCHAR  │
│ model_name  VARCHAR(512) │       │ raw_value       VARCHAR  │
│ youtube_url VARCHAR(512) │       │ unit            VARCHAR  │
│ rutube_url  VARCHAR(512) │       │ score           FLOAT    │
│ vk_url      VARCHAR(512) │       └─────────────────────────┘
│ total_score FLOAT        │
└─────────────────────────┘
```

## Таблица `ratings_airconditioner`

| Поле         | Тип            | Описание                               |
|--------------|----------------|----------------------------------------|
| id           | BigAutoField   | Первичный ключ (автоинкремент)          |
| rank         | PositiveIntegerField | Позиция в исходной таблице        |
| brand        | CharField(255) | Бренд / название модели                |
| model_name   | CharField(512) | Точное название модели                 |
| youtube_url  | URLField(512)  | Ссылка на YouTube видеообзор           |
| rutube_url   | URLField(512)  | Ссылка на RuTube видеообзор            |
| vk_url       | URLField(512)  | Ссылка на VK видеообзор                |
| total_score  | FloatField     | Итоговый суммарный балл (сумма индексов)|

Сортировка по умолчанию: `-total_score` (убывание).

## Таблица `ratings_parametervalue`

| Поле             | Тип            | Описание                                  |
|------------------|----------------|-------------------------------------------|
| id               | BigAutoField   | Первичный ключ                             |
| air_conditioner  | ForeignKey     | Связь с AirConditioner (CASCADE)           |
| parameter_name   | CharField(255) | Название параметра                         |
| raw_value        | CharField(255) | Исходное значение из xlsx                  |
| unit             | CharField(50)  | Единица измерения (может быть пустым)      |
| score            | FloatField     | Рассчитанный индекс (баллы)               |

Ограничение: `unique_together = (air_conditioner, parameter_name)`.

## Параметры

В системе используются следующие параметры кондиционеров:

| Параметр                               | Единица  |
|----------------------------------------|----------|
| Шум мин.                              | дБ(А)    |
| Вибрация                              | мм       |
| Мин. напряжение                       | В        |
| S меди внутр. блок                    | —        |
| S меди наруж. блок                    | —        |
| Наличие ЭРВ                           | —        |
| Подсветка пульта                      | —        |
| Тип (инвертор/он-офф)                | —        |
| Наличие WiFi                          | —        |
| Регулировка оборотов наруж. бл.      | —        |
| Кол-во скоростей внутр. бл.          | —        |
| Макс. длина фреонопровода            | м        |
