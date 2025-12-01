# =========================================
#   Flyto2 Telegram Bot Launcher (Fixed)
#   Two-phase Boot: Safe, Non-Blocking UX
# =========================================

param()

Write-Host "======================================"
Write-Host "      Flyto2 Telegram Bot Launcher     "
Write-Host "======================================"
Write-Host ""

# Detect project root
$ProjectPath = Split-Path $PSScriptRoot -Parent
Set-Location $ProjectPath


# ======================================
# Step 1: Ensure .env exists
# ======================================
$envFile = Join-Path $ProjectPath ".env"
$needConfig = $false

if (-not (Test-Path $envFile)) {
    Write-Host "[!] .env not found." -ForegroundColor Yellow
    Write-Host "    We'll create it now." -ForegroundColor Yellow
    $needConfig = $true
}
else {
    Write-Host "[✓] Found .env" -ForegroundColor Green
}

if ($needConfig) {
    Write-Host ""
    Write-Host "----------------------------------------"
    Write-Host " STEP 1 — Basic Setup Required"
    Write-Host "----------------------------------------"
    Write-Host ""

    # 1. Ask Bot Token
    $botToken = Read-Host "Enter TELEGRAM_BOT_TOKEN (from BotFather)"

    # 2. Ask Chat ID
    Write-Host ""
    Write-Host "You need your Telegram Chat ID."
    Write-Host "Open Telegram and send /start to: @userinfobot"
    Write-Host "It will give you something like: 123456789"
    Write-Host ""

    $chatId = Read-Host "Enter TELEGRAM_CHAT_ID"

    # Save config
    @"
# Telegram
TELEGRAM_BOT_TOKEN=$botToken
TELEGRAM_CHAT_ID=$chatId
TELEGRAM_ALLOWED_USERS=$chatId

# Local LLM
OLLAMA_URL=http://localhost:11434

# OpenAI (optional)
OPENAI_API_KEY=
"@ | Out-File -Encoding UTF8 -FilePath $envFile

    Write-Host "[✓] .env created!" -ForegroundColor Green
}

# ======================================
# Step 2: Load .env (silent)
# ======================================
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}


# ======================================
# Step 3: Ensure Python & venv
# ======================================
try {
    $pythonVersion = python --version
    Write-Host "[✓] Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[X] Python missing — install Python 3.8+ first" -ForegroundColor Red
    exit 1
}

$venvPath = Join-Path $ProjectPath "venv"
$activate = Join-Path $venvPath "Scripts\Activate.ps1"

if (-not (Test-Path $venvPath)) {
    Write-Host "Creating Python venv..."
    python -m venv venv
}

Write-Host "Activating venv..."
& $activate

Write-Host "Installing required packages..."
pip install python-telegram-bot requests openai -q


# ======================================
# Step 4: Launch Bot
# ======================================
Write-Host ""
Write-Host "----------------------------------------"
Write-Host " STEP 4 — Launch Bot"
Write-Host "----------------------------------------"
Write-Host ""

$botScript = "telegram_bot_v2.py"  # always use V2

Write-Host "[✓] Starting bot..."
python (Join-Path $ProjectPath "scripts\$botScript")

Write-Host ""
Write-Host "Bot stopped."
Read-Host "Press Enter to exit."
