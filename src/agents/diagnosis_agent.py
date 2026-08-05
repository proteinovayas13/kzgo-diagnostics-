import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np
from ..models.equipment import Severity

logger = logging.getLogger(__name__)

class DiagnosisAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Упрощенная диагностика без LLM
        self.use_llm = False
        try:
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(
                temperature=0.2,
                model="gpt-4",
                api_key=config.get('OPENAI_API_KEY')
            )
            self.use_llm = True
        except Exception as e:
            logger.warning(f"LLM not available: {e}. Using rule-based diagnosis.")
            self.llm = None
        
        # Маппинг симптомов на диагнозы (русские тексты)
        self.diagnosis_patterns = {
            'vibration_x': {
                'high': 'Износ подшипника',
                'critical': 'Разрушение подшипника'
            },
            'vibration_y': {
                'high': 'Дисбаланс ротора',
                'critical': 'Критический дисбаланс'
            },
            'temperature': {
                'high': 'Проблемы с охлаждением',
                'critical': 'Перегрев редуктора'
            },
            'current': {
                'high': 'Повышенная нагрузка на двигатель',
                'low': 'Обрыв фазы или неисправность реле'
            },
            'pressure': {
                'low': 'Утечка в гидросистеме',
                'high': 'Засорение фильтра'
            }
        }
    
    def get_diagnosis(self, equipment_id: str, anomalies: List[Dict]) -> Dict:
        """Получение диагноза на основе аномалий"""
        if not anomalies:
            return {
                "root_cause": "Аномалий не обнаружено",
                "severity": Severity.INFO,
                "recommended_action": "Продолжить мониторинг",
                "estimated_time_to_failure": "Не определено",
                "confidence": 1.0
            }
        
        # Определяем серьезность
        critical_anomalies = [a for a in anomalies if a.get('severity') == 'critical']
        warning_anomalies = [a for a in anomalies if a.get('severity') == 'warning']
        
        if critical_anomalies:
            severity = Severity.CRITICAL
            confidence = 0.85
            time_to_failure = "24-48 часов"
        elif warning_anomalies:
            severity = Severity.WARNING
            confidence = 0.70
            time_to_failure = "72-120 часов"
        else:
            severity = Severity.INFO
            confidence = 0.60
            time_to_failure = "Не определено"
        
        # Определяем причины
        causes = []
        for anomaly in anomalies:
            param = anomaly.get('parameter')
            severity_level = anomaly.get('severity')
            
            if param in self.diagnosis_patterns:
                if severity_level == 'critical' and 'critical' in self.diagnosis_patterns[param]:
                    causes.append(self.diagnosis_patterns[param]['critical'])
                elif 'high' in self.diagnosis_patterns[param]:
                    causes.append(self.diagnosis_patterns[param]['high'])
        
        root_cause = ", ".join(causes) if causes else "Неизвестная причина"
        
        # Рекомендации (русские тексты)
        if severity == Severity.CRITICAL:
            recommendation = "НЕМЕДЛЕННАЯ ОСТАНОВКА оборудования! Вызвать ремонтную бригаду. Провести полную диагностику."
        elif severity == Severity.WARNING:
            recommendation = "Запланировать внеплановый осмотр. Проверить параметры работы. Подготовить запасные части."
        else:
            recommendation = "Продолжить мониторинг. Включить оборудование в план ТО."
        
        return {
            "root_cause": root_cause,
            "severity": severity,
            "recommended_action": recommendation,
            "estimated_time_to_failure": time_to_failure,
            "confidence": confidence,
            "references": ["База знаний КЗГО - автоматическая диагностика"]
        }
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Основной метод обработки"""
        equipment_id = state.get('equipment_id')
        anomalies = state.get('anomalies', [])
        
        if not anomalies:
            state['diagnosis'] = None
            state['recommendation'] = "Аномалий не обнаружено"
            state['severity'] = Severity.INFO
            state['confidence'] = 1.0
            return state
        
        # Проведение диагностики
        diagnosis = self.get_diagnosis(equipment_id, anomalies)
        
        if diagnosis:
            state['diagnosis'] = diagnosis
            state['recommendation'] = diagnosis.get('recommended_action', 'Рекомендация отсутствует')
            state['severity'] = diagnosis.get('severity', Severity.INFO)
            state['confidence'] = diagnosis.get('confidence', 0.5)
        
        return state
