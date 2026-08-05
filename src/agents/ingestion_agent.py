import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from ..models.equipment import TelemetryData

logger = logging.getLogger(__name__)

class IngestionAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Пробуем подключиться к InfluxDB, но не падаем если нет
        self.influx_client = None
        self.write_api = None
        try:
            from influxdb_client import InfluxDBClient
            from influxdb_client.client.write_api import SYNCHRONOUS
            
            self.influx_client = InfluxDBClient(
                url=config.get('INFLUXDB_URL'),
                token=config.get('INFLUXDB_TOKEN'),
                org=config.get('INFLUXDB_ORG')
            )
            self.write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)
            logger.info("Подключение к InfluxDB установлено")
        except Exception as e:
            logger.warning(f"InfluxDB недоступен: {e}. Данные не будут сохранены.")
        
    def validate_data(self, raw_data: Dict[str, Any]) -> Optional[TelemetryData]:
        try:
            required_fields = ['equipment_id', 'timestamp']
            for field in required_fields:
                if field not in raw_data:
                    logger.error(f"Отсутствует обязательное поле: {field}")
                    return None
            
            sensors = raw_data.get('sensors', {})
            if 'temperature' in sensors:
                temp = sensors['temperature']
                if not (20 <= temp <= 120):
                    logger.warning(f"Подозрительная температура: {temp}°C")
                    
            telemetry = TelemetryData(
                equipment_id=raw_data['equipment_id'],
                timestamp=datetime.fromisoformat(raw_data['timestamp'].replace('Z', '+00:00')),
                vibration_x=sensors.get('vibration_x'),
                vibration_y=sensors.get('vibration_y'),
                temperature=sensors.get('temperature'),
                current=sensors.get('current'),
                pressure=sensors.get('pressure'),
                rpm=sensors.get('rpm')
            )
            
            return telemetry
            
        except Exception as e:
            logger.error(f"Ошибка валидации: {e}")
            return None
    
    def store_influxdb(self, telemetry: TelemetryData):
        """Сохранение данных в InfluxDB (если доступен)"""
        if not self.write_api:
            logger.debug("InfluxDB недоступен, пропускаем сохранение")
            return
            
        try:
            point = {
                "measurement": "telemetry",
                "tags": {
                    "equipment_id": telemetry.equipment_id
                },
                "fields": {
                    "vibration_x": telemetry.vibration_x,
                    "vibration_y": telemetry.vibration_y,
                    "temperature": telemetry.temperature,
                    "current": telemetry.current,
                    "pressure": telemetry.pressure,
                    "rpm": telemetry.rpm
                },
                "time": telemetry.timestamp
            }
            
            self.write_api.write(
                bucket=self.config.get('INFLUXDB_BUCKET'),
                record=point
            )
            logger.info(f"Сохранены данные для {telemetry.equipment_id}")
        except Exception as e:
            logger.error(f"Ошибка сохранения в InfluxDB: {e}")
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        raw_data = state.get('raw_data', {})
        
        telemetry = self.validate_data(raw_data)
        if not telemetry:
            state['error'] = 'Ошибка валидации данных'
            return state
        
        self.store_influxdb(telemetry)
        
        state['validated_data'] = telemetry.dict()
        state['equipment_id'] = telemetry.equipment_id
        
        return state
    
    def __del__(self):
        if hasattr(self, 'influx_client') and self.influx_client:
            try:
                self.influx_client.close()
            except:
                pass
