# Flyto2 Telegram Bot with Vector Database Memory
# PowerShell deployment script for Windows

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Flyto2 AI Agent Bot with Long-Term Memory" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "[1/4] Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.10+" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check dependencies
Write-Host "[2/4] Checking dependencies..." -ForegroundColor Yellow
$packages = @("python-telegram-bot", "qdrant-client", "sentence-transformers")
foreach ($package in $packages) {
    pip show $package | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  Installing $package..." -ForegroundColor Yellow
        pip install $package --quiet
    }
}
Write-Host "✓ All dependencies installed" -ForegroundColor Green

# Check environment
Write-Host "[3/4] Checking environment..." -ForegroundColor Yellow
if (-not (Test-Path .env)) {
    Write-Host "✗ .env file not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please create .env file with:" -ForegroundColor Yellow
    Write-Host "TELEGRAM_BOT_TOKEN=your_bot_token"
    Write-Host "TELEGRAM_ALLOWED_USERS=your_telegram_user_id"
    Write-Host "OLLAMA_URL=http://localhost:11434"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ Environment configured" -ForegroundColor Green

# Start Qdrant (if not running)
Write-Host "[4/4] Starting services..." -ForegroundColor Yellow
try {
    $qdrantRunning = Get-Process -Name qdrant -ErrorAction SilentlyContinue
    if (-not $qdrantRunning) {
        Write-Host "  Starting Qdrant vector database..." -ForegroundColor Yellow
        Start-Process -FilePath "qdrant" -WindowStyle Hidden -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
    Write-Host "✓ Qdrant running" -ForegroundColor Green
} catch {
    Write-Host "⚠ Qdrant not found (will use file storage)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Bot Features:" -ForegroundColor White
Write-Host "• Three-Tier AI: Ollama → Human → OpenAI" -ForegroundColor Gray
Write-Host "• Vector Database Long-Term Memory 🧠" -ForegroundColor Gray
Write-Host "• Auto Quality Filtering" -ForegroundColor Gray
Write-Host "• Auto-Sync System" -ForegroundColor Gray
Write-Host ""
Write-Host "Commands:" -ForegroundColor White
Write-Host "• /memory search <query> - Search knowledge" -ForegroundColor Gray
Write-Host "• /memory stats - Statistics" -ForegroundColor Gray
Write-Host "• /memory recent - Recent entries" -ForegroundColor Gray
Write-Host "• /stats - Usage stats" -ForegroundColor Gray
Write-Host "• /status - Quality status" -ForegroundColor Gray
Write-Host ""
Write-Host "Cost: ~NT`$30-60/month" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting bot... Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start bot
python scripts/telegram_bot_v2.py

Read-Host "`nBot stopped. Press Enter to exit"
