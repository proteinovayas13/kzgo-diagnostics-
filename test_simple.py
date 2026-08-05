# test_simple.py - Исправленная версия
import sys
import os
from datetime import datetime
import json
import asyncio

# Функция для сериализации datetime
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

print("🚀 Запуск теста KZGO Diagnostics...")

# Проверяем импорты
try:
    print("✅ Проверка импортов...")
    from src.models.equipment import TelemetryData, Severity
    print("✅ models.equipment")
    
    from src.agents.ingestion_agent import IngestionAgent
    print("✅ agents.ingestion_agent")
    
    from src.agents.anomaly_detection_agent import AnomalyDetectionAgent
    print("✅ agents.anomaly_detection_agent")
    
    from src.agents.diagnosis_agent import DiagnosisAgent
    print("✅ agents.diagnosis_agent")
    
    from src.orchestrator import DiagnosticOrchestrator
    print("✅ orchestrator")
    
except Exception as e:
    print(f"❌ Ошибка импорта: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Конфигурация
config = {
    'INFLUXDB_URL': 'http://localhost:8086',
    'INFLUXDB_ORG': 'my-org',
    'INFLUXDB_BUCKET': 'kzgo_telemetry',
    'INFLUXDB_TOKEN': 'my-super-secret-token',
    'OPENAI_API_KEY': '',
    'VIBRATION_WARNING': 3.0,
    'VIBRATION_CRITICAL': 6.0,
    'TEMP_WARNING': 80.0,
    'TEMP_CRITICAL': 90.0,
    'PRESSURE_WARNING': 8.0,
    'PRESSURE_CRITICAL': 6.0
}

# Создаем оркестратор
print("\n📦 Создание оркестратора...")
orchestrator = DiagnosticOrchestrator(config)

# Тестовые данные с аномалией
test_data = {
    "equipment_id": "ЭКГ-8И_№27",
    "timestamp": datetime.now().isoformat() + "Z",
    "sensors": {
        "vibration_x": 5.2,  # Аномалия!
        "vibration_y": 4.8,
        "temperature": 82.5,  # Аномалия!
        "current": 156.3,
        "pressure": 12.8,
        "rpm": 1485
    }
}

print("\n🔍 Тестовая телеметрия:")
print(json.dumps(test_data, indent=2, ensure_ascii=False))

# Запуск обработки
print("\n⚙️ Обработка данных...")
result = asyncio.run(orchestrator.process_telemetry(test_data))

print("\n📊 РЕЗУЛЬТАТ ДИАГНОСТИКИ:")

# Используем кастомный сериализатор
try:
    print(json.dumps(result, indent=2, ensure_ascii=False, default=json_serial))
except Exception as e:
    print(f"Ошибка сериализации: {e}")
    print("Результат (упрощенный):")
    print(f"Equipment: {result.get('equipment_id')}")
    print(f"Has anomalies: {result.get('has_anomalies')}")
    print(f"Severity: {result.get('severity')}")
    print(f"Recommendation: {result.get('recommendation')}")

if result.get('has_anomalies'):
    print("⚠️ ОБНАРУЖЕНЫ АНОМАЛИИ!")
    print(f"Серьезность: {result.get('severity')}")
    print(f"Рекомендация: {result.get('recommendation')}")
    if result.get('anomalies'):
        print("\nСписок аномалий:")
        for anomaly in result.get('anomalies', []):
            print(f"- {anomaly.get('parameter')}: {anomaly.get('value')} ({anomaly.get('severity')})")
else:
    print("✅ Аномалий не обнаружено")

if result.get('error'):
    print(f"\n⚠️Ошибка: {result.get('error')}")
