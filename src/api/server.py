from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import logging
from datetime import datetime
import os
from dotenv import load_dotenv
import json
import os.path

# Загрузка переменных окружения
load_dotenv()

from ..orchestrator import DiagnosticOrchestrator
from ..models.equipment import TelemetryData, Severity

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

# Инициализация приложения
app = FastAPI(
    title="KZGO Diagnostics API",
    description="API для предиктивной диагностики горного оборудования ООО КЗГО",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаем папку для статических файлов если её нет
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Конфигурация из переменных окружения
config = {
    'INFLUXDB_URL': os.getenv('INFLUXDB_URL', 'http://localhost:8086'),
    'INFLUXDB_ORG': os.getenv('INFLUXDB_ORG', 'my-org'),
    'INFLUXDB_BUCKET': os.getenv('INFLUXDB_BUCKET', 'kzgo_telemetry'),
    'INFLUXDB_TOKEN': os.getenv('INFLUXDB_TOKEN', 'my-super-secret-token'),
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
    'VIBRATION_WARNING': float(os.getenv('VIBRATION_WARNING', 3.0)),
    'VIBRATION_CRITICAL': float(os.getenv('VIBRATION_CRITICAL', 6.0)),
    'TEMP_WARNING': float(os.getenv('TEMP_WARNING', 80.0)),
    'TEMP_CRITICAL': float(os.getenv('TEMP_CRITICAL', 90.0)),
    'PRESSURE_WARNING': float(os.getenv('PRESSURE_WARNING', 8.0)),
    'PRESSURE_CRITICAL': float(os.getenv('PRESSURE_CRITICAL', 6.0))
}

# Создание оркестратора
orchestrator = DiagnosticOrchestrator(config)

# Модели запросов
class TelemetryRequest(BaseModel):
    equipment_id: str
    timestamp: str
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
                "vibration_x": 5.2,
                "vibration_y": 4.8,
                "temperature": 82.5,
                "current": 156.3,
                "pressure": 12.8,
                "rpm": 1485
            }
        }

class BatchTelemetryRequest(BaseModel):
    telemetry_list: List[TelemetryRequest]

# Эндпоинты
@app.get("/")
async def root():
    return {
        "message": "KZGO Diagnostics API",
        "status": "running",
        "version": "2.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "diagnostics": "/diagnostics/single",
            "batch": "/diagnostics/batch",
            "web_interface": "/static/index.html"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "influxdb": config['INFLUXDB_URL'],
            "openai": "configured" if config['OPENAI_API_KEY'] else "not configured"
        }
    }

def datetime_to_str(obj):
    """Преобразование datetime в строку для JSON"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

@app.post("/diagnostics/single")
async def diagnose_single(request: TelemetryRequest):
    """Диагностика по одной точке телеметрии"""
    try:
        # Преобразование в нужный формат
        raw_data = {
            "equipment_id": request.equipment_id,
            "timestamp": request.timestamp,
            "sensors": {
                "vibration_x": request.vibration_x,
                "vibration_y": request.vibration_y,
                "temperature": request.temperature,
                "current": request.current,
                "pressure": request.pressure,
                "rpm": request.rpm
            }
        }
        
        logger.info(f"Processing telemetry for {request.equipment_id}")
        
        # Обработка
        result = await orchestrator.process_telemetry(raw_data)
        
        # Преобразуем datetime в строки для JSON
        response_data = {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
        return JSONResponse(
            content=json.loads(json.dumps(response_data, default=datetime_to_str)),
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        
    except Exception as e:
        logger.error(f"Diagnostics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/diagnostics/batch")
async def diagnose_batch(request: BatchTelemetryRequest):
    """Диагностика по нескольким точкам телеметрии"""
    results = []
    errors = []
    
    for i, telemetry in enumerate(request.telemetry_list):
        try:
            raw_data = {
                "equipment_id": telemetry.equipment_id,
                "timestamp": telemetry.timestamp,
                "sensors": {
                    "vibration_x": telemetry.vibration_x,
                    "vibration_y": telemetry.vibration_y,
                    "temperature": telemetry.temperature,
                    "current": telemetry.current,
                    "pressure": telemetry.pressure,
                    "rpm": telemetry.rpm
                }
            }
            
            result = await orchestrator.process_telemetry(raw_data)
            results.append({
                "index": i,
                "equipment_id": telemetry.equipment_id,
                "result": result
            })
            
        except Exception as e:
            errors.append({
                "index": i,
                "equipment_id": telemetry.equipment_id,
                "error": str(e)
            })
    
    response_data = {
        "success": len(errors) == 0,
        "processed": len(results),
        "errors": len(errors),
        "data": results,
        "error_details": errors if errors else None,
        "timestamp": datetime.now().isoformat()
    }
    
    return JSONResponse(
        content=json.loads(json.dumps(response_data, default=datetime_to_str)),
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

@app.get("/equipment/{equipment_id}/history")
async def get_equipment_history(equipment_id: str, hours: int = 24):
    """Получение исторических данных по оборудованию"""
    return {
        "equipment_id": equipment_id,
        "hours": hours,
        "message": "History endpoint - requires InfluxDB connection",
        "data": []
    }

@app.get("/equipment/list")
async def get_equipment_list():
    """Список оборудования"""
    return {
        "equipment": [
            {"id": "ЭКГ-8И_№27", "type": "ЭКГ", "model": "8И", "status": "active"},
            {"id": "ЭКГ-8И_№28", "type": "ЭКГ", "model": "8И", "status": "active"},
            {"id": "СБШ-250_№15", "type": "СБШ", "model": "250", "status": "maintenance"},
            {"id": "СБШ-250_№16", "type": "СБШ", "model": "250", "status": "active"}
        ]
    }

# Эндпоинт для веб-интерфейса
@app.get("/web")
async def web_interface():
    """Перенаправление на веб-интерфейс"""
    return FileResponse(os.path.join(static_dir, "index.html"))

if __name__ == "__main__":
    uvicorn.run(
        "src.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
