# Flyto2 Telegram Bot - Windows Auto Setup Script
# Includes automatic Ollama installation and configuration

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Flyto2 Telegram Bot - Windows Auto Setup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if command exists
function Test-Command {
    param($Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Function to check if Ollama is running
function Test-OllamaRunning {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -UseBasicParsing
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

# 1. Check Python
Write-Host "[1/7] Checking Python..." -ForegroundColor Yellow
if (Test-Command python) {
    $pythonVersion = python --version
    Write-Host "  ✓ $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  ✗ Python not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.10+ from:" -ForegroundColor Red
    Write-Host "  https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# 2. Check/Install Ollama
Write-Host ""
Write-Host "[2/7] Checking Ollama..." -ForegroundColor Yellow

if (Test-Command ollama) {
    Write-Host "  ✓ Ollama is installed" -ForegroundColor Green

    # Check if Ollama is running
    if (Test-OllamaRunning) {
        Write-Host "  ✓ Ollama service is running" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Ollama is not running, starting..." -ForegroundColor Yellow
        Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
        Start-Sleep -Seconds 3

        if (Test-OllamaRunning) {
            Write-Host "  ✓ Ollama started successfully" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ Could not start Ollama automatically" -ForegroundColor Yellow
            Write-Host "  Please start Ollama manually before running the bot" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  ✗ Ollama not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Do you want to download and install Ollama now?" -ForegroundColor Yellow
    $install = Read-Host "  (Y/N)"

    if ($install -eq "Y" -or $install -eq "y") {
        Write-Host ""
        Write-Host "  → Downloading Ollama installer..." -ForegroundColor Cyan

        $installerUrl = "https://ollama.com/download/OllamaSetup.exe"
        $installerPath = "$env:TEMP\OllamaSetup.exe"

        try {
            Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath
            Write-Host "  ✓ Downloaded to $installerPath" -ForegroundColor Green

            Write-Host ""
            Write-Host "  → Running installer..." -ForegroundColor Cyan
            Start-Process -FilePath $installerPath -Wait

            Write-Host "  ✓ Ollama installed!" -ForegroundColor Green
            Write-Host ""
            Write-Host "  Please restart this script after installation completes." -ForegroundColor Yellow
            Read-Host "Press Enter to exit"
            exit 0
        } catch {
            Write-Host "  ✗ Failed to download Ollama" -ForegroundColor Red
            Write-Host "  Please download manually from: https://ollama.com/download" -ForegroundColor Yellow
            Read-Host "Press Enter to exit"
            exit 1
        }
    } else {
        Write-Host ""
        Write-Host "  Ollama is required for AI code generation." -ForegroundColor Yellow
        Write-Host "  Download from: https://ollama.com/download" -ForegroundColor Cyan
        Write-Host ""
        $continue = Read-Host "  Continue without Ollama? (Y/N)"
        if ($continue -ne "Y" -and $continue -ne "y") {
            exit 0
        }
    }
}

# 3. Check/Pull Ollama Model
Write-Host ""
Write-Host "[3/7] Checking Ollama model (llama3.2)..." -ForegroundColor Yellow

if (Test-Command ollama) {
    try {
        $models = ollama list 2>&1 | Out-String

        if ($models -match "llama3.2") {
            Write-Host "  ✓ llama3.2 model is available" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ llama3.2 model not found" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "Do you want to download llama3.2 model now? (~2GB)" -ForegroundColor Yellow
            $download = Read-Host "  (Y/N)"

            if ($download -eq "Y" -or $download -eq "y") {
                Write-Host ""
                Write-Host "  → Downloading llama3.2 model..." -ForegroundColor Cyan
                Write-Host "  This may take a few minutes..." -ForegroundColor Yellow

                ollama pull llama3.2

                Write-Host "  ✓ Model downloaded!" -ForegroundColor Green
            }
        }
    } catch {
        Write-Host "  ⚠ Could not check Ollama models" -ForegroundColor Yellow
    }
}

# 4. Check .env file
Write-Host ""
Write-Host "[4/7] Checking configuration..." -ForegroundColor Yellow

$envPath = ".env"
$envExamplePath = ".env.example"

if (Test-Path $envPath) {
    Write-Host "  ✓ .env file exists" -ForegroundColor Green

    # Check for required keys
    $envContent = Get-Content $envPath -Raw

    $requiredKeys = @(
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_ALLOWED_USERS"
    )

    $missingKeys = @()
    foreach ($key in $requiredKeys) {
        if ($envContent -notmatch "$key=\S+") {
            $missingKeys += $key
        }
    }

    if ($missingKeys.Count -gt 0) {
        Write-Host "  ⚠ Missing or empty configuration:" -ForegroundColor Yellow
        foreach ($key in $missingKeys) {
            Write-Host "    - $key" -ForegroundColor Yellow
        }
        Write-Host ""
        Write-Host "  Please update .env file with your values" -ForegroundColor Yellow

        $edit = Read-Host "  Open .env file for editing? (Y/N)"
        if ($edit -eq "Y" -or $edit -eq "y") {
            notepad.exe $envPath
        }
    } else {
        Write-Host "  ✓ All required keys configured" -ForegroundColor Green
    }
} else {
    Write-Host "  ✗ .env file not found" -ForegroundColor Red

    if (Test-Path $envExamplePath) {
        Write-Host ""
        Write-Host "  Creating .env from .env.example..." -ForegroundColor Cyan
        Copy-Item $envExamplePath $envPath
        Write-Host "  ✓ .env created" -ForegroundColor Green
        Write-Host ""
        Write-Host "  Please update .env with your configuration:" -ForegroundColor Yellow
        Write-Host "    - TELEGRAM_BOT_TOKEN (from @BotFather)" -ForegroundColor Yellow
        Write-Host "    - TELEGRAM_ALLOWED_USERS (your Telegram user ID)" -ForegroundColor Yellow
        Write-Host "    - SERPAPI_KEY (optional, for search features)" -ForegroundColor Yellow
        Write-Host ""

        $edit = Read-Host "  Open .env file for editing now? (Y/N)"
        if ($edit -eq "Y" -or $edit -eq "y") {
            notepad.exe $envPath
            Write-Host ""
            Read-Host "  Press Enter after saving the file"
        }
    } else {
        Write-Host "  Please create .env file with required configuration" -ForegroundColor Red
        exit 1
    }
}

# 5. Install Python dependencies
Write-Host ""
Write-Host "[5/7] Checking Python dependencies..." -ForegroundColor Yellow

if (Test-Path "requirements.txt") {
    Write-Host "  → Installing dependencies from requirements.txt..." -ForegroundColor Cyan
    python -m pip install --upgrade pip -q
    python -m pip install -r requirements.txt -q
    Write-Host "  ✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ⚠ requirements.txt not found" -ForegroundColor Yellow
}

# 6. Check Playwright browsers
Write-Host ""
Write-Host "[6/7] Checking Playwright browsers..." -ForegroundColor Yellow

try {
    $playwrightCheck = python -c "from playwright.sync_api import sync_playwright; print('ok')" 2>&1
    if ($playwrightCheck -match "ok") {
        Write-Host "  ✓ Playwright is installed" -ForegroundColor Green

        Write-Host "  → Installing Chromium browser..." -ForegroundColor Cyan
        python -m playwright install chromium --with-deps 2>&1 | Out-Null
        Write-Host "  ✓ Chromium installed" -ForegroundColor Green
    }
} catch {
    Write-Host "  ⚠ Playwright not available" -ForegroundColor Yellow
}

# 7. Start the bot
Write-Host ""
Write-Host "[7/7] Starting Telegram Bot..." -ForegroundColor Yellow
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Bot is starting..." -ForegroundColor Green
Write-Host "  Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variable for tokenizers
$env:TOKENIZERS_PARALLELISM = "false"

# Start the bot
python scripts/interactive_evolution_bot.py

# If we get here, the bot has stopped
Write-Host ""
Write-Host "Bot stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
