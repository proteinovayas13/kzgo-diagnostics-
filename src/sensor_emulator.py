# src/sensor_emulator.py - Эмулятор датчиков для тестирования
import asyncio
import random
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import aiohttp
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SensorEmulator:
    """Эмулятор датчиков оборудования"""
    
    def __init__(self, equipment_id: str = "ЭКГ-8И_№27"):
        self.equipment_id = equipment_id
        self.is_running = False
        
        # Базовые параметры для нормальной работы
        self.base_params = {
            'vibration_x': 2.0,      # мм/с
            'vibration_y': 2.2,      # мм/с
            'temperature': 70.0,     # °C
            'current': 145.0,        # А
            'pressure': 12.5,        # МПа
            'rpm': 1470              # об/мин
        }
        
        # Диапазоны для случайных колебаний
        self.noise_range = {
            'vibration_x': 0.3,
            'vibration_y': 0.3,
            'temperature': 3.0,
            'current': 5.0,
            'pressure': 0.5,
            'rpm': 10
        }
        
        # Режимы работы
        self.modes = {
            'normal': self._normal_mode,
            'warning': self._warning_mode,
            'critical': self._critical_mode,
            'degrading': self._degrading_mode
        }
        self.current_mode = 'normal'
        self.degradation_step = 0
        
        # История данных для трендов
        self.history = []
        
    def _normal_mode(self, params: Dict[str, float]) -> Dict[str, float]:
        """Нормальный режим работы"""
        return {
            'vibration_x': params['vibration_x'] + random.uniform(-0.3, 0.3),
            'vibration_y': params['vibration_y'] + random.uniform(-0.3, 0.3),
            'temperature': params['temperature'] + random.uniform(-2.0, 2.0),
            'current': params['current'] + random.uniform(-3.0, 3.0),
            'pressure': params['pressure'] + random.uniform(-0.3, 0.3),
            'rpm': params['rpm'] + random.uniform(-5, 5)
        }
    
    def _warning_mode(self, params: Dict[str, float]) -> Dict[str, float]:
        """Режим с предупреждениями"""
        return {
            'vibration_x': params['vibration_x'] + 2.5 + random.uniform(-0.5, 0.5),
            'vibration_y': params['vibration_y'] + 2.0 + random.uniform(-0.5, 0.5),
            'temperature': params['temperature'] + 10.0 + random.uniform(-1.0, 1.0),
            'current': params['current'] + 12.0 + random.uniform(-2.0, 2.0),
            'pressure': params['pressure'] + random.uniform(-0.5, 0.5),
            'rpm': params['rpm'] + random.uniform(-10, 10)
        }
    
    def _critical_mode(self, params: Dict[str, float]) -> Dict[str, float]:
        """Критический режим"""
        return {
            'vibration_x': params['vibration_x'] + 4.5 + random.uniform(-0.8, 0.8),
            'vibration_y': params['vibration_y'] + 4.0 + random.uniform(-0.8, 0.8),
            'temperature': params['temperature'] + 20.0 + random.uniform(-2.0, 2.0),
            'current': params['current'] + 25.0 + random.uniform(-3.0, 3.0),
            'pressure': params['pressure'] - 5.0 + random.uniform(-0.5, 0.5),
            'rpm': params['rpm'] + random.uniform(-20, 20)
        }
    
    def _degrading_mode(self, params: Dict[str, float]) -> Dict[str, float]:
        """Режим постепенной деградации"""
        self.degradation_step += 0.01
        degradation = min(self.degradation_step * 5, 5.0)
        
        return {
            'vibration_x': params['vibration_x'] + degradation * 0.8 + random.uniform(-0.3, 0.3),
            'vibration_y': params['vibration_y'] + degradation * 0.6 + random.uniform(-0.3, 0.3),
            'temperature': params['temperature'] + degradation * 2.0 + random.uniform(-1.0, 1.0),
            'current': params['current'] + degradation * 3.0 + random.uniform(-2.0, 2.0),
            'pressure': params['pressure'] - degradation * 0.5 + random.uniform(-0.3, 0.3),
            'rpm': params['rpm'] + random.uniform(-15, 15)
        }
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """Генерация телеметрии"""
        # Генерируем данные в зависимости от режима
        data = self.modes[self.current_mode](self.base_params)
        
        # Округляем значения
        telemetry = {
            'equipment_id': self.equipment_id,
            'timestamp': datetime.now().isoformat() + 'Z',
            'sensors': {
                'vibration_x': round(data['vibration_x'], 2),
                'vibration_y': round(data['vibration_y'], 2),
                'temperature': round(data['temperature'], 1),
                'current': round(data['current'], 1),
                'pressure': round(data['pressure'], 1),
                'rpm': round(data['rpm'])
            }
        }
        
        # Сохраняем в историю
        self.history.append(telemetry)
        if len(self.history) > 1000:
            self.history.pop(0)
        
        return telemetry
    
    def set_mode(self, mode: str):
        """Установка режима работы"""
        if mode in self.modes:
            self.current_mode = mode
            if mode == 'normal':
                self.degradation_step = 0
            logger.info(f"Режим изменен на: {mode}")
        else:
            logger.error(f"Неизвестный режим: {mode}. Доступные: {list(self.modes.keys())}")
    
    def get_modes(self) -> list:
        """Получение списка доступных режимов"""
        return list(self.modes.keys())

class TelemetryStream:
    """Поток телеметрии в реальном времени"""
    
    def __init__(self, api_url: str = "http://localhost:8000/diagnostics/single"):
        self.api_url = api_url
        self.emulators = {}
        self.is_running = False
        
    def add_equipment(self, equipment_id: str):
        """Добавление оборудования в поток"""
        if equipment_id not in self.emulators:
            self.emulators[equipment_id] = SensorEmulator(equipment_id)
            logger.info(f"Добавлено оборудование: {equipment_id}")
    
    def remove_equipment(self, equipment_id: str):
        """Удаление оборудования из потока"""
        if equipment_id in self.emulators:
            del self.emulators[equipment_id]
            logger.info(f"Удалено оборудование: {equipment_id}")
    
    def set_mode(self, equipment_id: str, mode: str):
        """Установка режима для оборудования"""
        if equipment_id in self.emulators:
            self.emulators[equipment_id].set_mode(mode)
        else:
            logger.error(f"Оборудование {equipment_id} не найдено")
    
    async def send_telemetry(self, equipment_id: str):
        """Отправка телеметрии на API"""
        emulator = self.emulators.get(equipment_id)
        if not emulator:
            return
        
        telemetry = emulator.generate_telemetry()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json={
                        'equipment_id': telemetry['equipment_id'],
                        'timestamp': telemetry['timestamp'],
                        'vibration_x': telemetry['sensors']['vibration_x'],
                        'vibration_y': telemetry['sensors']['vibration_y'],
                        'temperature': telemetry['sensors']['temperature'],
                        'current': telemetry['sensors']['current'],
                        'pressure': telemetry['sensors']['pressure'],
                        'rpm': telemetry['sensors']['rpm']
                    },
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('data', {}).get('has_anomalies'):
                            logger.warning(f"⚠️ Аномалия на {equipment_id}!")
                        logger.debug(f"✅ Отправлены данные для {equipment_id}")
                    else:
                        logger.error(f"❌ Ошибка отправки: {response.status}")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения: {e}")
    
    async def run_stream(self, interval: float = 2.0):
        """Запуск потока телеметрии"""
        self.is_running = True
        logger.info(f"🚀 Запуск потока телеметрии (интервал: {interval}с)")
        
        while self.is_running:
            tasks = []
            for equipment_id in self.emulators.keys():
                tasks.append(self.send_telemetry(equipment_id))
            
            if tasks:
                await asyncio.gather(*tasks)
            
            await asyncio.sleep(interval)
    
    def stop(self):
        """Остановка потока"""
        self.is_running = False
        logger.info("⏹️ Поток остановлен")

# Команды для управления
async def interactive_control():
    """Интерактивное управление эмулятором"""
    stream = TelemetryStream()
    
    # Добавляем оборудование
    equipment_list = ["ЭКГ-8И_№27", "ЭКГ-8И_№28", "СБШ-250_№15"]
    for eq in equipment_list:
        stream.add_equipment(eq)
    
    print("\n" + "="*60)
    print("🔧 KZGO ЭМУЛЯТОР ДАТЧИКОВ")
    print("="*60)
    print("\nДоступные команды:")
    print("normal- Нормальный режим")
    print("warning- Режим с предупреждениями")
    print("critical- Критический режим")
    print("degrading- Постепенная деградация")
    print("start- Запуск потока")
    print("stop- Остановка потока")
    print("status- Статус оборудования")
    print("xit- Выход")
    print("="*60)
    
    mode_task = None
    
    while True:
        try:
            command = input("\n> ").strip().lower()
            
            if command == 'start':
                if not stream.is_running:
                    print("🚀 Запуск потока телеметрии...")
                    mode_task = asyncio.create_task(stream.run_stream(interval=2.0))
                else:
                    print("⚠️ Поток уже запущен")
            
            elif command == 'stop':
                if stream.is_running:
                    stream.stop()
                    if mode_task:
                        mode_task.cancel()
                    print("⏹️ Поток остановлен")
                else:
                    print("⚠️ Поток не запущен")
            
            elif command in ['normal', 'warning', 'critical', 'degrading']:
                for eq in equipment_list:
                    stream.set_mode(eq, command)
                print(f"✅ Режим изменен на: {command}")
            
            elif command == 'status':
                print("\n📊 Статус оборудования:")
                print("-"*40)
                for eq, emulator in stream.emulators.items():
                    mode = emulator.current_mode
                    params = emulator.base_params
                    print(f"{eq}: {mode}")
                    print(f"Вибрация: {params['vibration_x']} мм/с")
                    print(f"Температура: {params['temperature']}°C")
                    print(f"Давление: {params['pressure']} МПа")
                print("-"*40)
            
            elif command == 'exit':
                if stream.is_running:
                    stream.stop()
                    if mode_task:
                        mode_task.cancel()
                print("👋 Выход...")
                break
            
            else:
                print(f"❌ Неизвестная команда: {command}")
                print("Доступные команды: normal, warning, critical, degrading, start, stop, status, exit")
                
        except KeyboardInterrupt:
            print("\n👋 Выход...")
            if stream.is_running:
                stream.stop()
                if mode_task:
                    mode_task.cancel()
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(interactive_control())
