import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from typing import TypedDict

from .agents.ingestion_agent import IngestionAgent
from .agents.anomaly_detection_agent import AnomalyDetectionAgent
from .agents.diagnosis_agent import DiagnosisAgent
from .models.equipment import TelemetryData

logger = logging.getLogger(__name__)

# Определение состояния
class DiagnosticsState(TypedDict):
    raw_data: Dict[str, Any]
    validated_data: Dict[str, Any]
    equipment_id: str
    anomalies: list
    has_anomalies: bool
    diagnosis: Dict[str, Any]
    recommendation: str
    severity: str
    confidence: float
    error: str

class DiagnosticOrchestrator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Инициализация агентов
        self.ingestion_agent = IngestionAgent(config)
        self.anomaly_detection_agent = AnomalyDetectionAgent(config)
        self.diagnosis_agent = DiagnosisAgent(config)
        
        # Создание графа
        self.graph = self._build_graph()
        
    def _build_graph(self):
        """Построение графа LangGraph"""
        
        # Создание графа с состоянием
        workflow = StateGraph(DiagnosticsState)
        
        # Добавление узлов (агентов)
        workflow.add_node("ingestion", self.ingestion_agent.process)
        workflow.add_node("anomaly_detection", self.anomaly_detection_agent.process)
        workflow.add_node("diagnosis", self.diagnosis_agent.process)
        
        # Добавление ребер
        workflow.add_edge("ingestion", "anomaly_detection")
        
        # Условное ребро: если есть аномалии -> диагностика, иначе завершение
        def check_anomalies(state: DiagnosticsState) -> str:
            if state.get("has_anomalies", False):
                return "diagnosis"
            return "end"
        
        workflow.add_conditional_edges(
            "anomaly_detection",
            check_anomalies,
            {
                "diagnosis": "diagnosis",
                "end": END
            }
        )
        
        workflow.add_edge("diagnosis", END)
        
        # Установка точки входа
        workflow.set_entry_point("ingestion")
        
        return workflow.compile()
    
    async def process_telemetry(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка телеметрии"""
        try:
            # Запуск графа
            result = await self.graph.ainvoke({
                "raw_data": raw_data,
                "validated_data": {},
                "equipment_id": "",
                "anomalies": [],
                "has_anomalies": False,
                "diagnosis": {},
                "recommendation": "",
                "severity": "",
                "confidence": 0.0,
                "error": ""
            })
            
            # Формирование ответа
            response = {
                "equipment_id": result.get("equipment_id"),
                "has_anomalies": result.get("has_anomalies", False),
                "anomalies": result.get("anomalies", []),
                "diagnosis": result.get("diagnosis"),
                "recommendation": result.get("recommendation"),
                "severity": result.get("severity"),
                "confidence": result.get("confidence", 0.0),
                "error": result.get("error", None)
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Processing error: {e}")
            return {
                "error": str(e),
                "has_anomalies": False,
                "recommendation": "Ошибка обработки данных"
            }
