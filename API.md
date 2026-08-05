Полная спецификация всех эндпоинтов REST API для предиктивной диагностики горного оборудования.

**Базовый URL:** `http://localhost:8000`  
**Версия API:** `v2.0.0`  
**Формат данных:** `JSON`  
**Кодировка:** `UTF-8`

## 📋 Содержание

- [Общие эндпоинты](#-общие-эндпоинты)
  - [GET / — Корневой эндпоинт](#get---корневой-эндпоинт)
  - [GET /health — Проверка здоровья](#get-health--проверка-здоровья)
- [Диагностика](#-диагностика)
  - [POST /diagnostics/single — Одиночная диагностика](#post-diagnosticssingle--одиночная-диагностика)
  - [POST /diagnostics/batch — Пакетная диагностика](#post-diagnosticsbatch--пакетная-диагностика)
- [Оборудование](#-оборудование)
  - [GET /equipment/list — Список оборудования](#get-equipmentlist--список-оборудования)
  - [GET /equipment/{equipment_id}/history — История оборудования](#get-equipmentequipment_idhistory--история-оборудования)
- [Веб-интерфейс](#-веб-интерфейс)
  - [GET /web — Веб-интерфейс](#get-web--веб-интерфейс)
  - [GET /static/ — Статические файлы](#get-static--статические-файлы)
- [Документация](#-документация)
  - [GET /docs — Swagger UI](#get-docs--swagger-ui)
  - [GET /redoc — ReDoc](#get-redoc--redoc)
- [Коды ошибок](#-коды-ошибок)
- [Примеры использования](#-примеры-использования)
- [Лимиты и политики](#-лимиты-и-политики)


## 🌐 Общие эндпоинты

### GET / — Корневой эндпоинт

Возвращает информацию о сервисе, версию и доступные эндпоинты.

**Запрос:**
```bash
curl http://localhost:8000/

Ответ:

json
{
  "message": "KZGO Diagnostics API",
  "status": "running",
  "version": "1.0.0",
  "endpoints": {
    "docs": "/docs",
    "health": "/health",
    "diagnostics": "/diagnostics/single",
    "batch": "/diagnostics/batch",
    "web_interface": "/static/index.html"
  }
}
Коды ответа:

200 — успешно

GET /health — Проверка здоровья
Проверяет состояние сервиса и всех зависимостей (InfluxDB, OpenAI API).

Запрос:
```bash
curl http://localhost:8000/health

Ответ:

json
{
  "status": "healthy",
  "timestamp": "2026-08-05T10:00:00Z",
  "config": {
    "influxdb": "http://localhost:8086",
    "openai": "configured"
  }
}
Поля ответа:

Поле	Тип	Описание
status	string	healthy — сервис работает, degraded — частичная недоступность, unhealthy — критическая ошибка
timestamp	string	Время проверки в ISO 8601
config.influxdb	string	URL InfluxDB или not configured
config.openai	string	configured или not configured
Коды ответа:

200 — сервис здоров

503 — одна или несколько зависимостей недоступны

🔬 Диагностика
POST /diagnostics/single — Одиночная диагностика
Выполняет полную диагностику по одной точке телеметрии.

Запрос:

```bash
curl -X POST http://localhost:8000/diagnostics/single \
  -H "Content-Type: application/json" \
  -d '{
    "equipment_id": "ЭКГ-8И_№27",
    "timestamp": "2026-08-05T10:00:00Z",
    "vibration_x": 5.2,
    "vibration_y": 4.8,
    "temperature": 82.5,
    "current": 156.3,
    "pressure": 12.8,
    "rpm": 1485
  }'

Параметры запроса (JSON):

Поле	Тип	Обязательное	Описание
equipment_id	string	✅	ID оборудования (например, ЭКГ-8И_№27)
timestamp	string	✅	Время замера в ISO 8601 (с Z или +00:00)
vibration_x	float	❌	Вибрация по оси X (мм/с)
vibration_y	float	❌	Вибрация по оси Y (мм/с)
temperature	float	❌	Температура (°C)
current	float	❌	Ток двигателя (А)
pressure	float	❌	Давление в гидросистеме (МПа)
rpm	float	❌	Частота вращения (об/мин)
Ответ:

json
{
  "success": true,
  "data": {
    "equipment_id": "ЭКГ-8И_№27",
    "has_anomalies": true,
    "anomalies": [
      {
        "parameter": "vibration_x",
        "value": 5.2,
        "threshold": 3.0,
        "severity": "warning",
        "method": "threshold",
        "description": "Превышение порога предупреждения: 5.2 (порог: 3.0)"
      },
      {
        "parameter": "temperature",
        "value": 82.5,
        "threshold": 80.0,
        "severity": "warning",
        "method": "threshold",
        "description": "Превышение порога предупреждения: 82.5 (порог: 80.0)"
      }
    ],
    "diagnosis": {
      "root_cause": "Износ подшипника, Проблемы с охлаждением",
      "severity": "warning",
      "recommended_action": "Запланировать внеплановый осмотр. Проверить параметры работы. Подготовить запасные части.",
      "estimated_time_to_failure": "72-120 часов",
      "confidence": 0.70,
      "references": ["База знаний КЗГО - автоматическая диагностика"]
    },
    "recommendation": "Запланировать внеплановый осмотр. Проверить параметры работы. Подготовить запасные части.",
    "severity": "warning",
    "confidence": 0.70,
    "error": null
  },
  "timestamp": "2026-08-05T10:00:01Z"
}
Поля ответа:

Поле	Тип	Описание
success	boolean	true — диагностика выполнена успешно
data.equipment_id	string	ID оборудования
data.has_anomalies	boolean	Есть ли аномалии
data.anomalies	array	Список обнаруженных аномалий
data.diagnosis	object	Диагноз (если есть аномалии)
data.recommendation	string	Рекомендация для оператора
data.severity	string	Серьёзность (info, warning, critical)
data.confidence	float	Уверенность в диагнозе (0.0–1.0)
data.error	string	Ошибка (если есть)
Структура аномалии:

json
{
  "parameter": "vibration_x",
  "value": 5.2,
  "threshold": 3.0,
  "severity": "warning",
  "method": "threshold",
  "description": "Превышение порога предупреждения: 5.2 (порог: 3.0)"
}
Структура диагноза:

json
{
  "root_cause": "Износ подшипника",
  "severity": "warning",
  "recommended_action": "Запланировать внеплановый осмотр",
  "estimated_time_to_failure": "72-120 часов",
  "confidence": 0.70,
  "references": ["База знаний КЗГО - автоматическая диагностика"]
}
Коды ответа:

200 — диагностика выполнена

400 — невалидные данные (проверьте формат timestamp или типы полей)

500 — внутренняя ошибка сервера

POST /diagnostics/batch — Пакетная диагностика
Выполняет диагностику для нескольких точек телеметрии одновременно.

Запрос:

```bash
curl -X POST http://localhost:8000/diagnostics/batch \
  -H "Content-Type: application/json" \
  -d '{
    "telemetry_list": [
      {
        "equipment_id": "ЭКГ-8И_№27",
        "timestamp": "2026-08-05T10:00:00Z",
        "vibration_x": 5.2,
        "temperature": 82.5
      },
      {
        "equipment_id": "СБШ-250_№15",
        "timestamp": "2026-08-05T10:05:00Z",
        "vibration_y": 7.2,
        "pressure": 5.5
      }
    ]
  }'

Параметры запроса (JSON):

Поле	Тип	Обязательное	Описание
telemetry_list	array	✅	Массив объектов телеметрии (до 100 записей)
Каждый объект в telemetry_list имеет ту же структуру, что и в /diagnostics/single.

Ответ:

json
{
  "success": true,
  "processed": 2,
  "errors": 0,
  "data": [
    {
      "index": 0,
      "equipment_id": "ЭКГ-8И_№27",
      "result": {
        "has_anomalies": true,
        "anomalies": [...],
        "diagnosis": {...},
        "recommendation": "Запланировать внеплановый осмотр",
        "severity": "warning",
        "confidence": 0.70
      }
    },
    {
      "index": 1,
      "equipment_id": "СБШ-250_№15",
      "result": {
        "has_anomalies": true,
        "anomalies": [...],
        "diagnosis": {...},
        "recommendation": "НЕМЕДЛЕННАЯ ОСТАНОВКА оборудования!",
        "severity": "critical",
        "confidence": 0.85
      }
    }
  ],
  "error_details": null,
  "timestamp": "2026-08-05T10:00:02Z"
}
Поля ответа:

Поле	Тип	Описание
success	boolean	true — все запросы обработаны без ошибок
processed	integer	Количество успешно обработанных записей
errors	integer	Количество записей с ошибками
data	array	Массив результатов для каждой записи
error_details	array	Детали ошибок (если есть)
Коды ответа:

200 — все записи обработаны

400 — невалидный формат запроса

500 — внутренняя ошибка

🏗️ Оборудование
GET /equipment/list — Список оборудования
Возвращает список всех единиц оборудования в системе.

Запрос:

```bash
curl http://localhost:8000/equipment/list

Ответ:

json
{
  "equipment": [
    {
      "id": "ЭКГ-8И_№27",
      "type": "ЭКГ",
      "model": "8И",
      "status": "active"
    },
    {
      "id": "ЭКГ-8И_№28",
      "type": "ЭКГ",
      "model": "8И",
      "status": "active"
    },
    {
      "id": "СБШ-250_№15",
      "type": "СБШ",
      "model": "250",
      "status": "maintenance"
    },
    {
      "id": "СБШ-250_№16",
      "type": "СБШ",
      "model": "250",
      "status": "active"
    }
  ]
}
Поля ответа:

Поле	Тип	Описание
equipment	array	Массив объектов оборудования
equipment[].id	string	ID оборудования
equipment[].type	string	Тип оборудования (ЭКГ, СБШ, Дробилка, Мельница)
equipment[].model	string	Модель оборудования
equipment[].status	string	Статус (active, maintenance, offline)
Коды ответа:

200 — список получен

GET /equipment/{equipment_id}/history — История оборудования
Возвращает исторические данные телеметрии для конкретного оборудования.

Запрос:

```bash
curl "http://localhost:8000/equipment/ЭКГ-8И_№27/history?hours=24"

Параметры:

Параметр	Тип	Обязательное	Описание
equipment_id	string	✅	ID оборудования (в пути)
hours	integer	❌	Количество часов истории (по умолчанию 24, максимум 168)
Ответ:

json
{
  "equipment_id": "ЭКГ-8И_№27",
  "hours": 24,
  "message": "History endpoint - requires InfluxDB connection",
  "data": [
    {
      "timestamp": "2026-08-04T10:00:00Z",
      "vibration_x": 2.4,
      "vibration_y": 3.1,
      "temperature": 75.5,
      "current": 145.2,
      "pressure": 12.8,
      "rpm": 1470,
      "has_anomaly": false
    },
    {
      "timestamp": "2026-08-04T10:05:00Z",
      "vibration_x": 2.6,
      "vibration_y": 3.0,
      "temperature": 76.0,
      "current": 146.1,
      "pressure": 12.7,
      "rpm": 1472,
      "has_anomaly": false
    }
  ]
}
Поля ответа:

Поле	Тип	Описание
equipment_id	string	ID оборудования
hours	integer	Запрошенный период в часах
message	string	Информационное сообщение
data	array	Массив точек телеметрии
Коды ответа:

200 — данные получены

404 — оборудование не найдено

503 — InfluxDB недоступен

🖥️ Веб-интерфейс
GET /web — Веб-интерфейс
Возвращает HTML-страницу веб-интерфейса для ручной диагностики.

Запрос:

```bash
curl http://localhost:8000/web

Ответ: HTML-страница с формой ввода телеметрии.

Примечание: Для использования откройте в браузере: http://localhost:8000/web

GET /static/ — Статические файлы
Доступ к статическим файлам (CSS, JS, HTML).

Запрос:

```bash
curl http://localhost:8000/static/index.html


Примечание: Все статические файлы находятся в папке src/api/static/.

📖 Документация
GET /docs — Swagger UI
Интерактивная документация API в формате Swagger UI.

Запрос:

```bash
curl http://localhost:8000/docs

Примечание: Откройте в браузере для использования.

GET /redoc — ReDoc
Альтернативная документация API в формате ReDoc.

Запрос:

```bash
curl http://localhost:8000/redoc

Примечание: Откройте в браузере для использования.

⚠️ Коды ошибок
Код	Название	Описание	Решение
400	Bad Request	Невалидные данные запроса	Проверьте формат timestamp (ISO 8601) и типы полей
404	Not Found	Оборудование не найдено	Проверьте equipment_id
500	Internal Server Error	Внутренняя ошибка сервера	Проверьте логи сервера (logs/)
503	Service Unavailable	Зависимость недоступна	Проверьте InfluxDB или OpenAI API
Пример ответа с ошибкой:

json
{
  "detail": "Ошибка валидации данных: поле 'timestamp' должно быть в формате ISO 8601"
}
📚 Примеры использования (curl)
1. Проверка здоровья сервиса
bash
curl http://localhost:8000/health
2. Одиночная диагностика (норма)
```bash
curl -X POST http://localhost:8000/diagnostics/single \
  -H "Content-Type: application/json" \
  -d '{
    "equipment_id": "ЭКГ-8И_№27",
    "timestamp": "2026-08-05T10:00:00Z",
    "vibration_x": 2.4,
    "temperature": 75.5,
    "pressure": 12.5
  }'
3. Одиночная диагностика (критическая)
```bash
curl -X POST http://localhost:8000/diagnostics/single \
  -H "Content-Type: application/json" \
  -d '{
    "equipment_id": "ЭКГ-8И_№27",
    "timestamp": "2026-08-05T10:00:00Z",
    "vibration_x": 7.5,
    "temperature": 92.5,
    "pressure": 5.5
  }'

4. Пакетная диагностика
bash
curl -X POST http://localhost:8000/diagnostics/batch \
  -H "Content-Type: application/json" \
  -d '{
    "telemetry_list": [
      {
        "equipment_id": "ЭКГ-8И_№27",
        "timestamp": "2026-08-05T10:00:00Z",
        "vibration_x": 5.2
      },
      {
        "equipment_id": "СБШ-250_№15",
        "timestamp": "2026-08-05T10:05:00Z",
        "temperature": 91.0
      }
    ]
  }'
5. История оборудования
bash
curl "http://localhost:8000/equipment/ЭКГ-8И_№27/history?hours=48"
6. Список оборудования
```bash
curl http://localhost:8000/equipment/list

7. Веб-интерфейс
Откройте в браузере: http://localhost:8000/web

⚡ Лимиты и политики
Лимит	Значение
Максимальный размер telemetry_list	100 записей
Максимальный период истории	168 часов (7 дней)
Таймаут запроса	30 секунд
Поддерживаемые форматы timestamp	ISO 8601 (2026-08-05T10:00:00Z)


💡 Вопросы и идеи: GitHub Discussions

📧 Почта: urevna111@mail.ru

API — это не просто интерфейс. Это язык, на котором система говорит с теми, кто её контролирует.


Дополнительно: если хотите, чтобы API.md открывался в веб-интерфейсе
Добавьте в src/api/server.py:

python
from fastapi.responses import HTMLResponse
import markdown

@app.get("/docs/api", response_class=HTMLResponse)
async def api_docs():
    with open("API.md", "r", encoding="utf-8") as f:
        md_content = f.read()
    html_content = markdown.markdown(md_content)
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>KZGO Diagnostics — API Reference</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; line-height: 1.8; }}
            h1, h2, h3 {{ color: #2c3e50; }}
            code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 4px; }}
            pre {{ background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 8px; overflow-x: auto; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
