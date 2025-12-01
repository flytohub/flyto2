# =========================================
#   Flyto2 Interactive Evolution System
#   Level 4 Self-Evolving AI Agent
# =========================================

param(
    [string]$ProjectPath = $null
)

Write-Host "=========================================="
Write-Host "  Flyto2 Interactive Evolution System     "
Write-Host "   Level 4 Self-Evolving AI Agent         "
Write-Host "=========================================="
Write-Host ""

# Detect project root
if (-not $ProjectPath) {
    $ProjectPath = Split-Path $PSScriptRoot -Parent
}
Set-Location $ProjectPath

Write-Host "[*] Project Path: $ProjectPath" -ForegroundColor Cyan
Write-Host ""

# ======================================
# Step 1: Check Prerequisites
# ======================================
Write-Host "=========================================="
Write-Host "  Step 1: Checking Prerequisites"
Write-Host "=========================================="
Write-Host ""

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[✓] Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[✗] Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check Ollama
$ollamaRunning = $false
try {
    $ollamaCheck = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
    Write-Host "[✓] Ollama is running" -ForegroundColor Green
    $ollamaRunning = $true
} catch {
    Write-Host "[!] Ollama not running" -ForegroundColor Yellow

    # Check if Ollama is installed
    $ollamaInstalled = Get-Command ollama -ErrorAction SilentlyContinue

    if (-not $ollamaInstalled) {
        Write-Host ""
        Write-Host "=========================================="
        Write-Host "  Ollama Not Installed"
        Write-Host "=========================================="
        Write-Host ""
        Write-Host "Ollama provides FREE local AI (no API costs)." -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Options:" -ForegroundColor Yellow
        Write-Host "  [1] Auto-install Ollama (Recommended)" -ForegroundColor White
        Write-Host "  [2] I'll install manually later" -ForegroundColor White
        Write-Host "  [3] Skip Ollama, use OpenAI only (need API key)" -ForegroundColor White
        Write-Host ""

        $choice = Read-Host "Choose option [1/2/3]"

        if ($choice -eq "1") {
            Write-Host ""
            Write-Host "[*] Downloading Ollama installer..." -ForegroundColor Cyan

            $installerPath = "$env:TEMP\OllamaSetup.exe"
            $downloadUrl = "https://ollama.com/download/OllamaSetup.exe"

            try {
                Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing
                Write-Host "[✓] Downloaded" -ForegroundColor Green

                Write-Host "[*] Installing Ollama..." -ForegroundColor Cyan
                Write-Host "    (Installation window will appear)" -ForegroundColor Gray

                Start-Process -FilePath $installerPath -Wait

                Write-Host "[✓] Ollama installed!" -ForegroundColor Green
                Write-Host ""
                Write-Host "[*] Starting Ollama service..." -ForegroundColor Cyan

                # Wait for Ollama to start
                Start-Sleep -Seconds 5

                # Download model
                Write-Host "[*] Downloading AI model (llama3.2)..." -ForegroundColor Cyan
                Write-Host "    This may take 5-10 minutes..." -ForegroundColor Gray

                $process = Start-Process -FilePath "ollama" -ArgumentList "pull llama3.2" -NoNewWindow -PassThru -Wait

                if ($process.ExitCode -eq 0) {
                    Write-Host "[✓] Model downloaded!" -ForegroundColor Green
                    $ollamaRunning = $true
                } else {
                    Write-Host "[!] Model download may have issues, but continuing..." -ForegroundColor Yellow
                }

            } catch {
                Write-Host "[✗] Auto-install failed: $($_.Exception.Message)" -ForegroundColor Red
                Write-Host ""
                Write-Host "Please install manually:" -ForegroundColor Yellow
                Write-Host "  1. Visit: https://ollama.com/download" -ForegroundColor White
                Write-Host "  2. Download and install" -ForegroundColor White
                Write-Host "  3. Run: ollama pull llama3.2" -ForegroundColor White
                Write-Host "  4. Run this script again" -ForegroundColor White
                exit 1
            }

        } elseif ($choice -eq "2") {
            Write-Host ""
            Write-Host "Please install Ollama manually:" -ForegroundColor Yellow
            Write-Host "  1. Visit: https://ollama.com/download" -ForegroundColor White
            Write-Host "  2. Download and install" -ForegroundColor White
            Write-Host "  3. Run: ollama pull llama3.2" -ForegroundColor White
            Write-Host "  4. Run this script again" -ForegroundColor White
            exit 1

        } elseif ($choice -eq "3") {
            Write-Host ""
            Write-Host "[!] Skipping Ollama - will use OpenAI only" -ForegroundColor Yellow
            Write-Host "    (You'll need to provide OpenAI API key)" -ForegroundColor Gray
            $ollamaRunning = $false
        }

    } else {
        # Ollama installed but not running
        Write-Host ""
        Write-Host "[*] Ollama is installed but not running" -ForegroundColor Cyan
        Write-Host "[*] Starting Ollama..." -ForegroundColor Cyan

        try {
            # Try to start Ollama service
            Start-Process -FilePath "ollama" -ArgumentList "serve" -NoNewWindow
            Start-Sleep -Seconds 5

            # Check if running now
            try {
                $ollamaCheck = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
                Write-Host "[✓] Ollama started successfully!" -ForegroundColor Green
                $ollamaRunning = $true
            } catch {
                Write-Host "[!] Ollama may not have started properly" -ForegroundColor Yellow
            }

        } catch {
            Write-Host "[!] Could not auto-start Ollama" -ForegroundColor Yellow
            Write-Host "    Please run: ollama serve" -ForegroundColor Gray
        }
    }
}

# ======================================
# Step 2: Environment Setup
# ======================================
Write-Host ""
Write-Host "=========================================="
Write-Host "  Step 2: Environment Setup"
Write-Host "=========================================="
Write-Host ""

$envFile = Join-Path $ProjectPath ".env"
$needConfig = $false

if (-not (Test-Path $envFile)) {
    Write-Host "[!] .env file not found" -ForegroundColor Yellow
    $needConfig = $true
} else {
    Write-Host "[✓] .env file exists" -ForegroundColor Green

    # Load and check required vars
    $envContent = Get-Content $envFile -Raw
    if ($envContent -notmatch "TELEGRAM_BOT_TOKEN") {
        Write-Host "[!] TELEGRAM_BOT_TOKEN missing" -ForegroundColor Yellow
        $needConfig = $true
    }
}

if ($needConfig) {
    Write-Host ""
    Write-Host "----------------------------------------"
    Write-Host " Configuration Required"
    Write-Host "----------------------------------------"
    Write-Host ""

    # Get Telegram Bot Token
    Write-Host "To create a Telegram bot:" -ForegroundColor Cyan
    Write-Host "  1. Open Telegram and message @BotFather" -ForegroundColor White
    Write-Host "  2. Send: /newbot" -ForegroundColor White
    Write-Host "  3. Follow instructions to get your token" -ForegroundColor White
    Write-Host ""
    $botToken = Read-Host "Enter TELEGRAM_BOT_TOKEN"

    # Get Chat ID
    Write-Host ""
    Write-Host "To find your Chat ID:" -ForegroundColor Cyan
    Write-Host "  1. Open Telegram and message @userinfobot" -ForegroundColor White
    Write-Host "  2. It will show your Chat ID (numbers only)" -ForegroundColor White
    Write-Host ""
    $chatId = Read-Host "Enter TELEGRAM_CHAT_ID"

    # Ask about OpenAI
    Write-Host ""
    if (-not $ollamaRunning) {
        Write-Host "OpenAI API Key (REQUIRED - Ollama not available):" -ForegroundColor Yellow
        Write-Host "  - Will be used as primary AI" -ForegroundColor White
        Write-Host "  - Get key from: https://platform.openai.com/api-keys" -ForegroundColor White
        Write-Host "  - Expected cost: ~$2-5/month for moderate use" -ForegroundColor White
        Write-Host ""
        $openaiKey = Read-Host "Enter OPENAI_API_KEY (required)"

        if ([string]::IsNullOrWhiteSpace($openaiKey)) {
            Write-Host ""
            Write-Host "[✗] OpenAI key required when Ollama not available" -ForegroundColor Red
            Write-Host "    Please install Ollama OR provide OpenAI key" -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host "OpenAI API Key (OPTIONAL):" -ForegroundColor Cyan
        Write-Host "  - Used ONLY when Ollama uncertain AND you approve" -ForegroundColor White
        Write-Host "  - Expected cost: ~$1-3/month (rarely needed)" -ForegroundColor White
        Write-Host "  - Get key from: https://platform.openai.com/api-keys" -ForegroundColor White
        Write-Host "  - Press Enter to skip (you can add it later)" -ForegroundColor White
        Write-Host ""
        $openaiKey = Read-Host "Enter OPENAI_API_KEY (or press Enter to skip)"
    }

    # Create .env file
    $envContent = @"
# Telegram Configuration
TELEGRAM_BOT_TOKEN=$botToken
TELEGRAM_CHAT_ID=$chatId
TELEGRAM_ALLOWED_USERS=$chatId

# Local AI (Ollama)
OLLAMA_URL=http://localhost:11434

# OpenAI (Optional - only used when escalated)
OPENAI_API_KEY=$openaiKey

# Safety Configuration
# Change these to control AI behavior
AI_AUTOMATION_ENABLED=true
AUTO_MERGE_ENABLED=true
AUTO_ROLLBACK_ENABLED=true
DRY_RUN_MODE=false
"@

    $envContent | Out-File -Encoding UTF8 -FilePath $envFile
    Write-Host ""
    Write-Host "[✓] .env file created!" -ForegroundColor Green
}

# Load environment variables
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}

# ======================================
# Step 3: Python Environment
# ======================================
Write-Host ""
Write-Host "=========================================="
Write-Host "  Step 3: Python Environment"
Write-Host "=========================================="
Write-Host ""

$venvPath = Join-Path $ProjectPath "venv"
$activate = Join-Path $venvPath "Scripts\Activate.ps1"

if (-not (Test-Path $venvPath)) {
    Write-Host "[*] Creating Python virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[✗] Failed to create venv" -ForegroundColor Red
        exit 1
    }
}

Write-Host "[*] Activating virtual environment..." -ForegroundColor Cyan
& $activate

Write-Host "[*] Installing/updating required packages..." -ForegroundColor Cyan
pip install -q --upgrade python-telegram-bot requests pyyaml python-dotenv

if (Test-Path (Join-Path $ProjectPath "requirements.txt")) {
    pip install -q -r requirements.txt
}

# ======================================
# Step 4: Safety Check
# ======================================
Write-Host ""
Write-Host "=========================================="
Write-Host "  Step 4: Safety Configuration Check"
Write-Host "=========================================="
Write-Host ""

if (Test-Path "config/safety.yaml") {
    Write-Host "[✓] Safety configuration exists" -ForegroundColor Green

    # Check safety status
    $safetyStatus = python scripts/safety_manager.py status | ConvertFrom-Json

    Write-Host ""
    Write-Host "Current Safety Settings:" -ForegroundColor Cyan
    Write-Host "  Automation Enabled: $($safetyStatus.automation_enabled)" -ForegroundColor White
    Write-Host "  Auto-merge Enabled: $($safetyStatus.auto_merge_enabled)" -ForegroundColor White
    Write-Host "  Auto-rollback Enabled: $($safetyStatus.auto_rollback_enabled)" -ForegroundColor White
    Write-Host "  Dry-run Mode: $($safetyStatus.dry_run_enabled)" -ForegroundColor White
    Write-Host ""

    if ($safetyStatus.dry_run_enabled) {
        Write-Host "[!] DRY-RUN MODE is enabled" -ForegroundColor Yellow
        Write-Host "    AI will propose changes but NOT auto-merge them" -ForegroundColor Yellow
        Write-Host ""
    }
} else {
    Write-Host "[!] Safety configuration not found (using defaults)" -ForegroundColor Yellow
}

# ======================================
# Step 5: Launch Options
# ======================================
Write-Host ""
Write-Host "=========================================="
Write-Host "  Step 5: Launch Mode"
Write-Host "=========================================="
Write-Host ""

Write-Host "Choose launch mode:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  [1] Interactive Mode (Recommended first time)" -ForegroundColor White
Write-Host "      - Auto-tests in background (hourly)" -ForegroundColor Gray
Write-Host "      - Chat with AI via Telegram" -ForegroundColor Gray
Write-Host "      - AI auto-analyzes and proposes fixes" -ForegroundColor Gray
Write-Host "      - Requires your approval to merge (safe)" -ForegroundColor Gray
Write-Host ""
Write-Host "  [2] Autonomous Mode (Fully automated, advanced)" -ForegroundColor White
Write-Host "      - Auto-tests in background (hourly)" -ForegroundColor Gray
Write-Host "      - AI auto-improves modules" -ForegroundColor Gray
Write-Host "      - Auto-merges if pass 98% gate" -ForegroundColor Gray
Write-Host "      - Only notifies results (after merge)" -ForegroundColor Gray
Write-Host ""
Write-Host "  [3] One-time Test Run (Test once and exit)" -ForegroundColor White
Write-Host "      - Run quality tests once" -ForegroundColor Gray
Write-Host "      - Get AI analysis report" -ForegroundColor Gray
Write-Host "      - Exit after completion" -ForegroundColor Gray
Write-Host ""

$mode = Read-Host "Select mode [1/2/3]"

Write-Host ""
Write-Host "=========================================="
Write-Host "  Starting System..."
Write-Host "=========================================="
Write-Host ""

if ($mode -eq "1") {
    Write-Host "[✓] Launching Interactive Evolution Bot..." -ForegroundColor Green
    Write-Host ""
    Write-Host "Open Telegram and send /start to your bot" -ForegroundColor Cyan
    Write-Host "Bot will respond with available commands" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
    Write-Host ""

    python scripts/interactive_evolution_bot.py

} elseif ($mode -eq "2") {
    Write-Host "[!] Autonomous Mode" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "AI will:" -ForegroundColor Cyan
    Write-Host "  • Run quality tests every hour" -ForegroundColor White
    Write-Host "  • Auto-propose improvements" -ForegroundColor White
    Write-Host "  • Auto-merge if pass rate > 98%" -ForegroundColor White
    Write-Host "  • Send Telegram notifications" -ForegroundColor White
    Write-Host ""

    if ($safetyStatus.dry_run_enabled) {
        Write-Host "[✓] DRY-RUN is enabled (safe for testing)" -ForegroundColor Green
    } else {
        Write-Host "[!] DRY-RUN is DISABLED - AI will auto-merge changes!" -ForegroundColor Yellow
        Write-Host ""
        $confirm = Read-Host "Are you sure? [y/N]"
        if ($confirm -ne 'y' -and $confirm -ne 'Y') {
            Write-Host "Cancelled" -ForegroundColor Yellow
            exit 0
        }
    }

    Write-Host ""
    Write-Host "[✓] Starting autonomous agent..." -ForegroundColor Green
    Write-Host ""

    python -m src.cli.main workflows/meta/continuous_improvement_agent.yaml --param max_improvements=5

} elseif ($mode -eq "3") {
    Write-Host "[✓] Running one-time quality test..." -ForegroundColor Green
    Write-Host ""

    python scripts/validate_all_modules.py

    Write-Host ""
    Write-Host "Test complete!" -ForegroundColor Green
    Write-Host ""
    Read-Host "Press Enter to exit"

} else {
    Write-Host "[✗] Invalid mode selected" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "System stopped." -ForegroundColor Cyan
Read-Host "Press Enter to exit"
