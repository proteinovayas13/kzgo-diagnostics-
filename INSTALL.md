# KZGO Diagnostics — Полная установка

> **Оборудование помнит. Инженеры принимают решения.**

Добро пожаловать в KZGO Diagnostics — систему предиктивной диагностики горного оборудования.  
Этот документ содержит всё, что нужно для запуска системы: от локальной разработки до продакшен-развертывания.

---

## 📋 Содержание

- [Требования](#-требования)
- [Быстрая установка (для тестирования)](#-быстрая-установка-для-тестирования)
- [Установка с Docker](#-установка-с-docker)
- [Настройка переменных окружения](#-настройка-переменных-окружения)
- [Запуск и проверка](#-запуск-и-проверка)
- [Установка на сервер (продакшен)](#-установка-на-сервер-продакшен)
- [Настройка InfluxDB](#-настройка-influxdb)
- [Интеграция с OpenAI](#-интеграция-с-openai)
- [Сброс и перезапуск](#-сброс-и-перезапуск)
- [Порты и доступы](#-порты-и-доступы)
- [Устранение неполадок](#-устранение-неполадок)
- [Поддержка](#-поддержка)

---

## ⚙️ Требования

| Компонент | Версия | Примечание |
|-----------|--------|------------|
| Python | 3.10+ | Обязательно |
| InfluxDB | 2.x | Опционально (рекомендуется) |
| Docker | 20.10+ | Для контейнерной установки |
| OpenAI API Key | — | Для LLM-диагностики (опционально) |
| Операционная система | Linux / macOS / Windows (WSL2) | |

---

## 🚀 Быстрая установка (для тестирования)

Этот вариант подойдёт для локального тестирования или демонстрации.

### Шаг 1. Клонирование репозитория

```bash
git clone https://github.com/your-org/KZGO-Diagnostics.git
cd KZGO-Diagnostics
Шаг 2. Настройка окружения
bash
cp .env.example .env
Откройте .env в любом редакторе и заполните минимальные параметры:

ini
# Обязательные
VIBRATION_WARNING=3.0
VIBRATION_CRITICAL=6.0
TEMP_WARNING=80.0
TEMP_CRITICAL=90.0
PRESSURE_WARNING=8.0
PRESSURE_CRITICAL=6.0

# Опциональные (для InfluxDB и OpenAI)
INFLUXDB_URL=http://localhost:8086
INFLUXDB_ORG=my-org
INFLUXDB_BUCKET=kzgo_telemetry
INFLUXDB_TOKEN=your-token
OPENAI_API_KEY=sk-...
Шаг 3. Установка зависимостей
bash
pip install -r requirements.txt
Если файл requirements.txt отсутствует, установите вручную:

bash
pip install fastapi uvicorn pydantic python-dotenv langgraph influxdb-client langchain-openai aiohttp markdown
Шаг 4. Запуск сервера
bash
python -m src.api.server
Ожидаемый вывод:

text
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
Шаг 5. Проверка
Откройте в браузере:

Веб-интерфейс: http://localhost:8000/web

Документация API: http://localhost:8000/docs

Health check: http://localhost:8000/health

Если всё работает — вы готовы к диагностике!

🐳 Установка с Docker
Рекомендуемый способ для продакшена и изолированного окружения.

Шаг 1. Сборка образа
bash
docker build -t kzgo-diagnostics:latest .
Шаг 2. Запуск контейнера
bash
docker run -d \
  --name kzgo-diagnostics \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  kzgo-diagnostics:latest
Шаг 3. Проверка работы контейнера
bash
docker logs -f kzgo-diagnostics
Шаг 4. Остановка и удаление
bash
docker stop kzgo-diagnostics
docker rm kzgo-diagnostics
🔧 Настройка переменных окружения
Все параметры системы настраиваются через файл .env.

Обязательные параметры (пороговые значения)
Переменная	Описание	Пример
VIBRATION_WARNING	Порог предупреждения по вибрации (мм/с)	3.0
VIBRATION_CRITICAL	Критический порог по вибрации (мм/с)	6.0
TEMP_WARNING	Порог предупреждения по температуре (°C)	80.0
TEMP_CRITICAL	Критический порог по температуре (°C)	90.0
PRESSURE_WARNING	Порог предупреждения по давлению (МПа)	8.0
PRESSURE_CRITICAL	Критический порог по давлению (МПа)	6.0
Опциональные параметры
Переменная	Описание	Пример
INFLUXDB_URL	Адрес InfluxDB	http://localhost:8086
INFLUXDB_ORG	Организация InfluxDB	my-org
INFLUXDB_BUCKET	Имя bucket для хранения телеметрии	kzgo_telemetry
INFLUXDB_TOKEN	Токен доступа к InfluxDB	my-super-secret-token
OPENAI_API_KEY	API-ключ OpenAI для LLM-диагностики	sk-...
✅ Запуск и проверка
Проверка здоровья сервиса
bash
curl http://localhost:8000/health
Ожидаемый ответ:

json
{
  "status": "healthy",
  "timestamp": "2026-08-05T10:00:00Z",
  "config": {
    "influxdb": "http://localhost:8086",
    "openai": "configured"
  }
}
Проверка диагностики
bash
curl -X POST http://localhost:8000/diagnostics/single \
  -H "Content-Type: application/json" \
  -d '{
    "equipment_id": "ЭКГ-8И_№27",
    "timestamp": "2026-08-05T10:00:00Z",
    "vibration_x": 5.2,
    "temperature": 82.5
  }'
Проверка веб-интерфейса
Откройте http://localhost:8000/web и введите тестовые данные или используйте пресеты:

✅ Норма — зелёный сценарий

⚠️ Предупреждение — жёлтый сценарий

🔴 Критично — красный сценарий

🏭 Установка на сервер (продакшен)
Шаг 1. Подготовка сервера
bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и pip
sudo apt install python3 python3-pip python3-venv -y

# Установка Docker (рекомендуется)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
Шаг 2. Настройка firewall
bash
# Открыть порт 8000
sudo ufw allow 8000/tcp
sudo ufw reload
Шаг 3. Клонирование и запуск
bash
git clone https://github.com/your-org/KZGO-Diagnostics.git
cd KZGO-Diagnostics
cp .env.example .env
nano .env  # заполните все параметры
python -m src.api.server
Шаг 4. Настройка systemd (для автозапуска)
Создайте файл /etc/systemd/system/kzgo-diagnostics.service:

ini
[Unit]
Description=KZGO Diagnostics Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/KZGO-Diagnostics
EnvironmentFile=/home/ubuntu/KZGO-Diagnostics/.env
ExecStart=/usr/bin/python3 -m src.api.server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
Запустите и включите автозапуск:

bash
sudo systemctl daemon-reload
sudo systemctl enable kzgo-diagnostics
sudo systemctl start kzgo-diagnostics
sudo systemctl status kzgo-diagnostics
📊 Настройка InfluxDB
Установка InfluxDB (Linux)
bash
# Добавление репозитория
curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
echo "deb https://repos.influxdata.com/ubuntu focal stable" | sudo tee /etc/apt/sources.list.d/influxdb.list

# Установка
sudo apt update
sudo apt install influxdb2 -y

# Запуск
sudo systemctl start influxdb
sudo systemctl enable influxdb
Создание bucket и токена
bash
# Через веб-интерфейс: http://localhost:8086
# Или через CLI:
influx bucket create -n kzgo_telemetry -o my-org
influx auth create -o my-org -d kzgo-token -w bucket=kzgo_telemetry
Проверка подключения
python
# Тестовый скрипт проверки InfluxDB
from influxdb_client import InfluxDBClient
client = InfluxDBClient(url="http://localhost:8086", token="your-token", org="my-org")
print(client.ping())  # Должно вернуть True
🤖 Интеграция с OpenAI
Если вы хотите использовать LLM для более точной диагностики:

Получите API-ключ на OpenAI Platform

Добавьте в .env:

text
OPENAI_API_KEY=sk-...
Перезапустите сервер

Без OpenAI система использует rule-based диагностику (встроенные правила).

🔄 Сброс и перезапуск
Перезапуск сервера
bash
# Если запущен через uvicorn
CTRL+C  # остановка
python -m src.api.server  # повторный запуск

# Если через systemd
sudo systemctl restart kzgo-diagnostics

# Если через Docker
docker restart kzgo-diagnostics
Полный сброс данных
bash
# Очистка базы InfluxDB
influx delete --bucket kzgo_telemetry --start 2020-01-01T00:00:00Z --stop 2030-01-01T00:00:00Z

# Удаление файлов конфигурации (осторожно!)
rm -rf data/
🔌 Порты и доступы
Порт	Сервис	Доступ
8000	FastAPI (основной API и веб-интерфейс)	Все пользователи
8086	InfluxDB (база данных)	Только администратор
8125	(резерв)	—
🐛 Устранение неполадок
Ошибка: "InfluxDB недоступен"
Причина: InfluxDB не запущен или неправильные настройки.

Решение:

bash
# Проверьте статус InfluxDB
sudo systemctl status influxdb

# Проверьте доступность
curl http://localhost:8086/health

# Проверьте переменные в .env
echo $INFLUXDB_URL
Ошибка: "OpenAI API key not configured"
Причина: API-ключ не указан или невалиден.

Решение:

bash
# Проверьте наличие ключа в .env
grep OPENAI_API_KEY .env

# Если ключа нет — система использует rule-based диагностику
# Это не ошибка, просто режим работы без LLM
Ошибка: "Port 8000 already in use"
Причина: Другой процесс использует порт 8000.

Решение:

bash
# Найдите процесс
sudo lsof -i :8000

# Завершите процесс (замените PID)
sudo kill -9 <PID>

# Или запустите на другом порту:
python -m src.api.server --port 8080
Ошибка: "ModuleNotFoundError"
Причина: Не установлены зависимости.

Решение:

bash
pip install -r requirements.txt
Если файла requirements.txt нет:

bash
pip install fastapi uvicorn pydantic python-dotenv langgraph influxdb-client langchain-openai aiohttp markdown
Проблемы с веб-интерфейсом
Симптом: Интерфейс не открывается или отображается некорректно.

Решение:

Проверьте, что сервер запущен

Откройте http://localhost:8000/static/index.html напрямую

Очистите кэш браузера (CTRL+F5)

Проверьте консоль браузера на ошибки (F12 → Console)

📞 Поддержка
🐞 Баг-репорты: GitHub Issues

💡 Вопросы и идеи: GitHub Discussions

📧 Почта: support@kzgo-diagnostics.com

Установка — это не просто настройка. Это начало доверия между системой и теми, кто ей управляет.

text

---

## Как сохранить и использовать

1. **Скопируйте** весь текст выше
2. **Создайте** файл `INSTALL.md` в корне вашего проекта
3. **Вставьте** скопированный текст
4. **Сохраните** файл

Теперь в вашем главном `README.md` ссылка `[INSTALL.md](INSTALL.md)` будет открывать этот файл при клике.

---

## Дополнительно: если хотите, чтобы INSTALL.md открывался в веб-интерфейсе

Добавьте в `src/api/server.py`:

```python
from fastapi.responses import HTMLResponse
import markdown

@app.get("/docs/install", response_class=HTMLResponse)
async def install_docs():
    with open("INSTALL.md", "r", encoding="utf-8") as f:
        md_content = f.read()
    html_content = markdown.markdown(md_content)
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>KZGO Diagnostics — Установка</title>
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