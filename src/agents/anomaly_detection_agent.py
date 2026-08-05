import numpy as np
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
import logging

from ..models.equipment import Anomaly, Severity

logger = logging.getLogger(__name__)

class AnomalyDetectionAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Пороговые значения из конфига
        self.thresholds = {
            'vibration_x': {
                'warning': float(config.get('VIBRATION_WARNING', 3.0)),
                'critical': float(config.get('VIBRATION_CRITICAL', 6.0))
            },
            'vibration_y': {
                'warning': float(config.get('VIBRATION_WARNING', 3.0)),
                'critical': float(config.get('VIBRATION_CRITICAL', 6.0))
            },
            'temperature': {
                'warning': float(config.get('TEMP_WARNING', 80.0)),
                'critical': float(config.get('TEMP_CRITICAL', 90.0))
            },
            'current': {
                'warning': 160.0,
                'critical': 180.0
            },
            'pressure': {
                'warning': float(config.get('PRESSURE_WARNING', 8.0)),
                'critical': float(config.get('PRESSURE_CRITICAL', 6.0))
            }
        }
    
    def threshold_check(self, value: float, parameter: str) -> Tuple[bool, Severity, str]:
        """Проверка статических порогов"""
        if parameter not in self.thresholds:
            return False, Severity.INFO, "Порог не определен"
        
        thresholds = self.thresholds[parameter]
        
        if value >= thresholds.get('critical', float('inf')):
            return True, Severity.CRITICAL, f"Критическое превышение порога: {value} (порог: {thresholds['critical']})"
        elif value >= thresholds.get('warning', float('inf')):
            return True, Severity.WARNING, f"Превышение порога предупреждения: {value} (порог: {thresholds['warning']})"
        
        return False, Severity.INFO, "В пределах нормы"
    
    def detect_anomalies(self, telemetry: Dict[str, Any]) -> List[Anomaly]:
        """Обнаружение аномалий во всех параметрах"""
        anomalies = []
        equipment_id = telemetry['equipment_id']
        timestamp = telemetry['timestamp']
        
        # Параметры для проверки
        parameters = ['vibration_x', 'vibration_y', 'temperature', 'current', 'pressure']
        
        for param in parameters:
            if param not in telemetry or telemetry[param] is None:
                continue
                
            value = telemetry[param]
            
            # Проверка статических порогов
            is_anomaly, severity, description = self.threshold_check(value, param)
            
            if is_anomaly:
                threshold = self.thresholds[param]['critical'] if severity == Severity.CRITICAL else self.thresholds[param]['warning']
                anomalies.append(Anomaly(
                    equipment_id=equipment_id,
                    timestamp=timestamp,
                    parameter=param,
                    value=value,
                    threshold=threshold,
                    severity=severity,
                    method='threshold',
                    description=description
                ))
        
        return anomalies
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Основной метод обработки"""
        telemetry = state.get('validated_data', {})
        
        if not telemetry:
            state['error'] = 'Нет данных для анализа'
            return state
        
        # Обнаружение аномалий
        anomalies = self.detect_anomalies(telemetry)
        
        # Сохранение результатов
        state['anomalies'] = [a.dict() for a in anomalies]
        state['has_anomalies'] = len(anomalies) > 0
        
        logger.info(f"Обнаружено {len(anomalies)} аномалий для {telemetry['equipment_id']}")
        
        return state
