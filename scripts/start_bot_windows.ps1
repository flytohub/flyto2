# start_bot_windows.ps1
# One-click startup for Flyto2 Telegram Bot on Windows
# Handles Ollama startup + interactive configuration + bot launch

param(
    [string]$ProjectPath = $PSScriptRoot | Split-Path -Parent
)

# Colors
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Cyan = "Cyan"

Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Flyto2 Telegram Bot Launcher (V2)    ║" -ForegroundColor Cyan
Write-Host "║  Ultra-Low-Cost Human-Guided Strategy  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Set working directory
Set-Location $ProjectPath
Write-Host "Working directory: $ProjectPath" -ForegroundColor Yellow
Write-Host ""

# ==================================
# Step 1: Check Prerequisites
# ==================================
Write-Host "Step 1: Checking prerequisites..." -ForegroundColor Cyan

# Check Python
Write-Host "  Checking Python..." -NoNewline
try {
    $pythonVersion = python --version 2>&1
    Write-Host " ✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host " ✗ Not found" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Ollama
Write-Host "  Checking Ollama..." -NoNewline
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host " ✓ Installed" -ForegroundColor Green
} catch {
    Write-Host " ✗ Not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Ollama is not installed. Would you like to:" -ForegroundColor Yellow
    Write-Host "  1. Install now (opens browser)"
    Write-Host "  2. Continue without Ollama (will use OpenAI only)"
    Write-Host "  3. Exit"
    $choice = Read-Host "Enter choice (1-3)"

    if ($choice -eq "1") {
        Start-Process "https://ollama.com/download"
        Write-Host "Please install Ollama and run this script again." -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 0
    } elseif ($choice -eq "2") {
        Write-Host "Continuing without Ollama..." -ForegroundColor Yellow
        $skipOllama = $true
    } else {
        exit 0
    }
}

Write-Host ""

# ==================================
# Step 2: Configure Environment Variables
# ==================================
Write-Host "Step 2: Configuring environment..." -ForegroundColor Cyan
Write-Host ""

$envFile = Join-Path $ProjectPath ".env"
$envExists = Test-Path $envFile

if ($envExists) {
    Write-Host ".env file found!" -ForegroundColor Green

    # Load existing .env
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }

    Write-Host ""
    Write-Host "Current configuration:" -ForegroundColor Yellow

    $botToken = [Environment]::GetEnvironmentVariable("TELEGRAM_BOT_TOKEN")
    $allowedUsers = [Environment]::GetEnvironmentVariable("TELEGRAM_ALLOWED_USERS")
    $openaiKey = [Environment]::GetEnvironmentVariable("OPENAI_API_KEY")

    Write-Host "  Bot Token: " -NoNewline
    if ($botToken) {
        Write-Host "****$(($botToken).Substring($botToken.Length - 10))" -ForegroundColor Green
    } else {
        Write-Host "Not set" -ForegroundColor Red
    }

    Write-Host "  Allowed Users: " -NoNewline
    if ($allowedUsers) {
        Write-Host "$allowedUsers" -ForegroundColor Green
    } else {
        Write-Host "Not set" -ForegroundColor Red
    }

    Write-Host "  OpenAI Key: " -NoNewline
    if ($openaiKey) {
        Write-Host "****$(($openaiKey).Substring($openaiKey.Length - 10))" -ForegroundColor Green
    } else {
        Write-Host "Not set (optional)" -ForegroundColor Yellow
    }

    Write-Host ""
    $reconfigure = Read-Host "Reconfigure? (y/n)"

    if ($reconfigure -ne "y") {
        $needsConfig = $false
    } else {
        $needsConfig = $true
    }
} else {
    Write-Host ".env file not found. Let's create it!" -ForegroundColor Yellow
    $needsConfig = $true
}

if ($needsConfig) {
    Write-Host ""
    Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  Interactive Configuration" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""

    # Telegram Bot Token
    Write-Host "1. TELEGRAM BOT TOKEN" -ForegroundColor Yellow
    Write-Host "   Get from: @BotFather on Telegram" -ForegroundColor Gray
    Write-Host "   Command: /newbot" -ForegroundColor Gray
    Write-Host ""
    $botToken = Read-Host "   Enter Bot Token"

    # Telegram User ID
    Write-Host ""
    Write-Host "2. YOUR TELEGRAM USER ID" -ForegroundColor Yellow
    Write-Host "   Get from: @userinfobot on Telegram" -ForegroundColor Gray
    Write-Host "   Command: /start" -ForegroundColor Gray
    Write-Host ""
    $userId = Read-Host "   Enter Your User ID"

    # OpenAI API Key (optional)
    Write-Host ""
    Write-Host "3. OPENAI API KEY (Optional)" -ForegroundColor Yellow
    Write-Host "   For /gpt commands (costs money)" -ForegroundColor Gray
    Write-Host "   Get from: https://platform.openai.com/api-keys" -ForegroundColor Gray
    Write-Host "   Leave empty to skip" -ForegroundColor Gray
    Write-Host ""
    $openaiKey = Read-Host "   Enter OpenAI Key (or press Enter to skip)"

    # Create .env file
    $envContent = @"
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=$botToken
TELEGRAM_CHAT_ID=$userId
TELEGRAM_ALLOWED_USERS=$userId

# Ollama (Local LLM)
OLLAMA_URL=http://localhost:11434

# OpenAI (Optional - for /gpt commands)
OPENAI_API_KEY=$openaiKey

# GitHub (Optional)
GITHUB_TOKEN=
"@

    $envContent | Out-File -FilePath $envFile -Encoding UTF8

    Write-Host ""
    Write-Host "✓ Configuration saved to .env" -ForegroundColor Green

    # Load into current process
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

Write-Host ""

# ==================================
# Step 3: Start Ollama
# ==================================
if (-not $skipOllama) {
    Write-Host "Step 3: Starting Ollama..." -ForegroundColor Cyan

    # Check if Ollama is already running
    Write-Host "  Checking if Ollama is running..." -NoNewline
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434" -TimeoutSec 2 -ErrorAction SilentlyContinue
        Write-Host " ✓ Already running" -ForegroundColor Green
    } catch {
        Write-Host " ✗ Not running" -ForegroundColor Yellow
        Write-Host "  Starting Ollama server..." -NoNewline

        # Start Ollama in background
        Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden

        # Wait for Ollama to start
        $maxWait = 30
        $waited = 0
        $started = $false

        while ($waited -lt $maxWait) {
            Start-Sleep -Seconds 1
            $waited++

            try {
                $response = Invoke-WebRequest -Uri "http://localhost:11434" -TimeoutSec 2 -ErrorAction SilentlyContinue
                $started = $true
                break
            } catch {
                # Still waiting
            }
        }

        if ($started) {
            Write-Host " ✓ Started" -ForegroundColor Green
        } else {
            Write-Host " ✗ Failed to start" -ForegroundColor Red
            Write-Host "  Please start Ollama manually: ollama serve" -ForegroundColor Yellow
        }
    }

    # Check if model is installed
    Write-Host "  Checking llama3.2 model..." -NoNewline
    $models = ollama list 2>&1 | Out-String

    if ($models -match "llama3.2") {
        Write-Host " ✓ Installed" -ForegroundColor Green
    } else {
        Write-Host " ✗ Not installed" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  Would you like to download llama3.2? (Recommended, ~2GB)" -ForegroundColor Yellow
        $download = Read-Host "  Download now? (y/n)"

        if ($download -eq "y") {
            Write-Host "  Downloading llama3.2 (this may take a few minutes)..." -ForegroundColor Cyan
            ollama pull llama3.2
            Write-Host "  ✓ Model downloaded" -ForegroundColor Green
        }
    }

    Write-Host ""
}

# ==================================
# Step 4: Install Python Dependencies
# ==================================
Write-Host "Step 4: Checking Python dependencies..." -ForegroundColor Cyan

$venvPath = Join-Path $ProjectPath "venv"
$venvActivate = Join-Path $venvPath "Scripts\Activate.ps1"

if (-not (Test-Path $venvPath)) {
    Write-Host "  Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "  Activating virtual environment..." -ForegroundColor Yellow
& $venvActivate

Write-Host "  Installing dependencies..." -ForegroundColor Yellow
pip install -q python-telegram-bot requests openai

Write-Host "  ✓ Dependencies ready" -ForegroundColor Green
Write-Host ""

# ==================================
# Step 5: Launch Bot
# ==================================
Write-Host "Step 5: Launching bot..." -ForegroundColor Cyan
Write-Host ""
Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║         Bot Starting...                ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

# Choose which bot version to run
Write-Host "Which bot version to run?" -ForegroundColor Yellow
Write-Host "  1. V2 (Ultra-Low-Cost with Human Guidance) - Recommended"
Write-Host "  2. V1 (Original Hybrid Auto-Fallback)"
Write-Host ""
$botChoice = Read-Host "Enter choice (1 or 2, default: 1)"

if ($botChoice -eq "2") {
    $botScript = "telegram_bot.py"
} else {
    $botScript = "telegram_bot_v2.py"
}

Write-Host ""
Write-Host "Starting $botScript..." -ForegroundColor Green
Write-Host ""
Write-Host "Bot will run in this window. Press Ctrl+C to stop." -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Run the bot
python (Join-Path $ProjectPath "scripts\$botScript")

# If bot stops, show message
Write-Host ""
Write-Host "Bot stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
