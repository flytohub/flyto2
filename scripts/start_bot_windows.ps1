param(
    [string]$ProjectPath = (Split-Path $PSScriptRoot -Parent)
)

Write-Host "Starting Flyto2 Telegram Bot..."
Write-Host ""

Set-Location $ProjectPath

# ----- Step 1: Check Python -----
Write-Host "Checking Python..."
try {
    $pythonVersion = python --version
    Write-Host "Python OK: $pythonVersion"
} catch {
    Write-Host "Python not found. Install Python 3.8+ first."
    exit 1
}

# ----- Step 2: Check Ollama -----
Write-Host "Checking Ollama..."
$ollamaInstalled = $true
try {
    $ov = ollama --version
    Write-Host "Ollama OK"
} catch {
    Write-Host "Ollama not found. Continuing without local AI."
    $ollamaInstalled = $false
}

# ----- Step 3: Load .env -----
$envFile = Join-Path $ProjectPath ".env"
if (Test-Path $envFile) {
    Write-Host ".env found. Loading..."

    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $key   = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
} else {
    Write-Host ".env not found. Creating..."

    $botToken = Read-Host "Enter TELEGRAM_BOT_TOKEN"
    $chatId   = Read-Host "Enter TELEGRAM_CHAT_ID"

    @"
TELEGRAM_BOT_TOKEN=$botToken
TELEGRAM_CHAT_ID=$chatId
OLLAMA_URL=http://localhost:11434
"@ | Out-File -FilePath $envFile -Encoding utf8
}

# ----- Step 4: Virtual Environment -----
$venvPath = Join-Path $ProjectPath "venv"
$activate = Join-Path $venvPath "Scripts\Activate.ps1"

if (-not (Test-Path $venvPath)) {
    Write-Host "Creating Python venv..."
    python -m venv venv
}

Write-Host "Activating venv..."
& $activate

Write-Host "Installing dependencies..."
pip install python-telegram-bot requests openai -q

# ----- Step 5: Ask which bot version to run -----
Write-Host ""
Write-Host "Select bot version:"
Write-Host "1 = telegram_bot_v2.py (recommended)"
Write-Host "2 = telegram_bot.py (classic)"
$choice = Read-Host "Enter 1 or 2"

if ($choice -eq "2") {
    $botScript = "telegram_bot.py"
} else {
    $botScript = "telegram_bot_v2.py"
}

Write-Host ""
Write-Host "Starting $botScript ..."
python (Join-Path $ProjectPath "scripts\$botScript")

Write-Host "Bot stopped."
Read-Host "Press Enter to exit."
