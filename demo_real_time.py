# demo_real_time.py - Демонстрация работы с реальными данными
import asyncio
import json
from datetime import datetime
from src.sensor_emulator import SensorEmulator, TelemetryStream

async def demo():
    """Демонстрация работы эмулятора"""
    print("\n" + "="*60)
    print("🔧 ДЕМОНСТРАЦИЯ РАБОТЫ ЭМУЛЯТОРА ДАТЧИКОВ")
    print("="*60)
    
    # Создаем поток
    stream = TelemetryStream()
    
    # Добавляем оборудование
    equipment = ["ЭКГ-8И_№27", "ЭКГ-8И_№28", "СБШ-250_№15"]
    for eq in equipment:
        stream.add_equipment(eq)
        print(f"✅ Добавлено: {eq}")
    
    print("\n📊 Демонстрация режимов работы:")
    print("-"*40)
    
    # Демонстрация разных режимов
    modes = [
        ("normal", "🟢 Нормальный режим"),
        ("warning", "🟡 Режим с предупреждениями"),
        ("critical", "🔴 Критический режим"),
        ("degrading", "📉 Постепенная деградация")
    ]
    
    for mode, description in modes:
        print(f"\n{description}")
        print("-"*40)
        
        # Устанавливаем режим
        for eq in equipment:
            stream.set_mode(eq, mode)
        
        # Отправляем 3 пакета данных
        for i in range(3):
            for eq in equipment:
                await stream.send_telemetry(eq)
            await asyncio.sleep(1)
            
        print("✅ Отправлено 3 пакета данных")
    
    print("\n" + "="*60)
    print("📊 Демонстрация завершена")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(demo())
