# test_api.py - Тестирование API
import requests
import json
from datetime import datetime, timedelta

# URL API
BASE_URL = "http://localhost:8000"

def test_health():
    """Тест проверки здоровья"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    return response.status_code == 200
def test_diagnosis():
    """Тест диагностики"""
    # Данные с аномалией
    data = {
        "equipment_id": "ЭКГ-8И_№27",
        "timestamp": datetime.now().isoformat() + "Z",
        "vibration_x": 5.2,
        "vibration_y": 4.8,
        "temperature": 82.5,
        "current": 156.3,
        "pressure": 12.8,
        "rpm": 1485
    }
    
    response = requests.post(f"{BASE_URL}/diagnostics/single", json=data)
    print(f"Diagnosis test: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return response.status_code == 200

def test_batch():
    """Тест пакетной обработки"""
    telemetry_list = []
    
    for i in range(10):
        data = {
            "equipment_id": f"ЭКГ-8И_№{27 + i}",
            "timestamp": (datetime.now() - timedelta(minutes=i*5)).isoformat() + "Z",
            "vibration_x": 2.0 + i * 0.3,
            "vibration_y": 2.5 + i * 0.2,
            "temperature": 70.0 + i * 1.0,
            "current": 145.0 + i * 0.5,
            "pressure": 12.0 - i * 0.1
        }
        telemetry_list.append(data)
    
    response = requests.post(f"{BASE_URL}/diagnostics/batch", json={"telemetry_list": telemetry_list})
    print(f"Batch test: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return response.status_code == 200

if __name__ == "__main__":
    print("🚀 Testing KZGO Diagnostics API...")
    print("=" * 50)
    
    if test_health():
        print("✅ Health check passed")
    else:
        print("❌ Health check failed")
    
    if test_diagnosis():
        print("✅ Single diagnosis test passed")
    else:
        print("❌ Single diagnosis test failed")
    
    if test_batch():
        print("✅ Batch diagnosis test passed")
    else:
        print("❌ Batch diagnosis test failed")
    
    print("=" * 50)
    print("📊 Test complete!")
