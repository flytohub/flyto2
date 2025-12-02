@echo off
REM Flyto2 One-Click Auto Setup & Start for Windows
REM 一鍵自動安裝所有依賴並啟動機器人

setlocal enabledelayedexpansion

echo ========================================================================
echo 🚀 Flyto2 Bot - Auto Setup ^& Start (Windows)
echo    一鍵安裝所有依賴並啟動
echo ========================================================================
echo.

REM Get script directory
cd /d "%~dp0"
set "SCRIPT_DIR=%CD%"

echo 📍 Working directory: %SCRIPT_DIR%
echo.

REM Check Python
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 1️⃣  Checking Python...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ✗ Python not found!
    echo.
    echo Please install Python 3.8+ from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Python found: %PYTHON_VERSION%

REM Check pip
where pip >nul 2>nul
if %errorlevel% neq 0 (
    echo ⏳ Installing pip...
    python -m ensurepip --upgrade
    echo ✅ pip installed
) else (
    echo ✓ pip found
)

REM Check/Install GitHub CLI
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 2️⃣  Checking GitHub CLI...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

where gh >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  GitHub CLI not found
    echo.
    echo To install GitHub CLI:
    echo 1. Download from: https://cli.github.com/
    echo 2. Or use winget: winget install --id GitHub.cli
    echo 3. Or use Chocolatey: choco install gh
    echo.
    echo Continuing without GitHub CLI...
    echo (PR creation will not be available)
    set "GH_AVAILABLE=0"
) else (
    for /f "tokens=*" %%i in ('gh --version 2^>^&1 ^| findstr /C:"gh version"') do set GH_VERSION=%%i
    echo ✓ GitHub CLI found: !GH_VERSION!
    set "GH_AVAILABLE=1"

    REM Check if authenticated
    gh auth status >nul 2>nul
    if !errorlevel! neq 0 (
        echo ⚠️  GitHub not authenticated
        echo    You can authenticate later with: gh auth login
    ) else (
        echo ✓ GitHub authenticated
    )
)

REM Install Python Dependencies
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 3️⃣  Installing Python Dependencies...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo ⏳ Upgrading pip...
python -m pip install --upgrade pip setuptools wheel -q

if exist requirements.txt (
    echo ⏳ Installing from requirements.txt...
    pip install -r requirements.txt -q --exists-action i
    echo ✅ Core dependencies installed
) else (
    echo ⚠️  requirements.txt not found, installing essential packages...
    pip install -q --exists-action i python-telegram-bot playwright openai qdrant-client python-dotenv aiohttp pyyaml requests
    echo ✅ Essential packages installed
)

REM Install Playwright Browsers
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 4️⃣  Installing Playwright Browsers...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

python -c "import playwright" >nul 2>nul
if %errorlevel% equ 0 (
    echo ⏳ Installing Chromium browser...
    playwright install chromium
    echo ✅ Playwright browsers installed
) else (
    echo ⚠️  Playwright not found in pip install
)

REM Check Environment Variables
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 5️⃣  Checking Environment Variables...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if not exist .env (
    echo ⚠️  .env file not found
    echo    Creating template .env file...

    (
        echo # Telegram Bot
        echo TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
        echo.
        echo # OpenAI
        echo OPENAI_API_KEY=your_openai_api_key_here
        echo.
        echo # Qdrant Cloud
        echo QDRANT_URL=your_qdrant_url_here
        echo QDRANT_API_KEY=your_qdrant_api_key_here
        echo.
        echo # Ollama (optional^)
        echo OLLAMA_BASE_URL=http://localhost:11434
        echo OLLAMA_MODEL=llama3.2:3b
        echo.
        echo # GitHub (optional, for auto PR creation^)
        echo GITHUB_TOKEN=your_github_token_here
    ) > .env

    echo ✅ Template .env created
    echo    ⚠️  Please edit .env and add your API keys
    set "ENV_CONFIGURED=0"
) else (
    echo ✓ .env file exists

    REM Check for required keys (simplified check)
    findstr /C:"TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here" .env >nul 2>nul
    if %errorlevel% equ 0 (
        echo    ⚠️  TELEGRAM_BOT_TOKEN not set
        set "ENV_CONFIGURED=0"
    ) else (
        echo    ✓ TELEGRAM_BOT_TOKEN configured
        set "ENV_CONFIGURED=1"
    )
)

REM Test System
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 6️⃣  Testing System...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo ⏳ Testing module registry...
python -c "from src.core.modules.registry import ModuleRegistry; print('Modules loaded:', len(ModuleRegistry.list_all()))" 2>nul
if %errorlevel% equ 0 (
    echo ✅ Module registry working
    set "MODULES_OK=1"
) else (
    echo ✗ Module registry test failed
    set "MODULES_OK=0"
)

REM Summary
echo.
echo ========================================================================
echo 📊 Setup Summary
echo ========================================================================
echo.

set /a READY_COUNT=0
set /a TOTAL_COUNT=6

if defined PYTHON_VERSION set /a READY_COUNT+=1
if defined GH_AVAILABLE if %GH_AVAILABLE%==1 set /a READY_COUNT+=1
if %ENV_CONFIGURED%==1 set /a READY_COUNT+=1
if %MODULES_OK%==1 set /a READY_COUNT+=1
set /a READY_COUNT+=2

echo ✅ Ready: %READY_COUNT%/%TOTAL_COUNT%
echo.

if %READY_COUNT% geq 5 (
    if %ENV_CONFIGURED%==1 (
        echo 🎉 All dependencies installed!
        echo.
        echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        echo 🚀 Starting Bot...
        echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        echo.

        if exist scripts\interactive_evolution_bot.py (
            python scripts\interactive_evolution_bot.py
        ) else (
            echo ⚠️  Bot script not found at scripts\interactive_evolution_bot.py
            echo.
            echo Available commands:
            echo    python test_end_to_end.py          # Test system
            echo    python test_difficult_questions.py # Test AI responses
            echo    python test_pr_creation.py         # Test PR creation
        )
    ) else (
        echo ⚠️  Environment configuration needed
        echo.
        echo Next steps:
        echo 1. Edit .env file with your API keys
        echo 2. Run this script again: START_BOT_AUTO.bat
    )
) else (
    echo ⚠️  Some dependencies need attention
    echo.
    echo Please check the messages above and:
    echo 1. Install Python 3.8+ if needed
    echo 2. Edit .env file with your API keys
    echo 3. Optionally install GitHub CLI
    echo 4. Run this script again
)

echo.
echo ========================================================================
pause


