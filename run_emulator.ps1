# run_emulator.ps1 - Запуск эмулятора датчиков
Write-Host "🚀 KZGO Эмулятор датчиков" -ForegroundColor Green
Write-Host "="*60 -ForegroundColor Green

# Проверяем что сервер запущен
Write-Host "`n🔍 Проверка API сервера..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    Write-Host "✅ API сервер работает" -ForegroundColor Green
} catch {
    Write-Host "❌ API сервер не отвечает!" -ForegroundColor Red
    Write-Host "Запустите сначала: python -m src.api.server" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n📦 Запуск эмулятора..." -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Gray
Write-Host "Доступные команды:" -ForegroundColor Yellow
Write-Host "normal- Нормальный режим работы" -ForegroundColor Gray
Write-Host "warning- Режим с предупреждениями" -ForegroundColor Gray
Write-Host "critical- Критический режим" -ForegroundColor Gray
Write-Host "degrading- Постепенная деградация" -ForegroundColor Gray
Write-Host "start- Запуск потока данных" -ForegroundColor Gray
Write-Host "stop- Остановка потока" -ForegroundColor Gray
Write-Host "status- Статус оборудования" -ForegroundColor Gray
Write-Host "exit- Выход" -ForegroundColor Gray
Write-Host "="*60 -ForegroundColor Gray

# Запуск эмулятора
python -m src.sensor_emulator
