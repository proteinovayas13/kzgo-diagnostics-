from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from enum import Enum

class EquipmentType(str, Enum):
    EKG = "ЭКГ"
    SBSh = "СБШ"
    DRILL = "Дробилка"
    MILL = "Мельница"

class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class TelemetryData(BaseModel):
    equipment_id: str
    timestamp: datetime
    vibration_x: Optional[float] = None
    vibration_y: Optional[float] = None
    temperature: Optional[float] = None
    current: Optional[float] = None
    pressure: Optional[float] = None
    rpm: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "equipment_id": "ЭКГ-8И_№27",
                "timestamp": "2026-08-03T14:23:45Z",
                "vibration_x": 2.4,
                "vibration_y": 3.1,
                "temperature": 78.5,
                "current": 145.2,
                "pressure": 12.8
            }
        }

class Anomaly(BaseModel):
    equipment_id: str
    timestamp: datetime
    parameter: str
    value: float
    threshold: float
    severity: Severity
    method: str
    description: str

class Diagnosis(BaseModel):
    equipment_id: str
    timestamp: datetime
    root_cause: str
    confidence: float = Field(ge=0, le=1)
    severity: Severity
    estimated_time_to_failure: Optional[str] = None
    recommended_action: str
    references: List[str] = []
    anomalies: List[Anomaly] = []

class Equipment(BaseModel):
    id: str
    name: str
    type: EquipmentType
    model: str
    serial_number: str
    installation_date: datetime
    last_maintenance: Optional[datetime] = None
    location: str
    status: str
    threshold_config: Dict[str, float]
