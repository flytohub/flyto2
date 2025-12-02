@echo off
REM ============================================================================
REM Flyto2 Bot - 全功能啟動器 / All-in-One Launcher
REM ============================================================================
REM 功能:
REM   - 自動安裝依賴 (Auto-install dependencies)
REM   - 環境檢查 (Environment checks)
REM   - 診斷模式 (Diagnostic mode)
REM   - 快速啟動模式 (Quick start mode)
REM
REM 使用方法:
REM   START_BOT.bat            - 完整檢查並啟動 (Full check and start)
REM   START_BOT.bat /quick     - 快速啟動 (Quick start, skip checks)
REM   START_BOT.bat /diagnose  - 診斷模式 (Diagnostic mode)
REM ============================================================================

setlocal enabledelayedexpansion

REM Get script directory
cd /d "%~dp0"
set "SCRIPT_DIR=%CD%"

REM Check for command line arguments
set "MODE=full"
if /i "%~1"=="/quick" set "MODE=quick"
if /i "%~1"=="/diagnose" set "MODE=diagnose"
if /i "%~1"=="-quick" set "MODE=quick"
if /i "%~1"=="-diagnose" set "MODE=diagnose"
if /i "%~1"=="/q" set "MODE=quick"
if /i "%~1"=="-q" set "MODE=quick"
if /i "%~1"=="/d" set "MODE=diagnose"
if /i "%~1"=="-d" set "MODE=diagnose"

REM ============================================================================
REM QUICK START MODE - Skip all checks, direct launch
REM ============================================================================
if "%MODE%"=="quick" (
    echo ========================================================================
    echo 🚀 Flyto2 Bot - Quick Start
    echo ========================================================================
    echo.

    REM Check Python
    python --version >nul 2>nul
    if %errorlevel% neq 0 (
        echo ✗ Python not found!
        echo   Please install Python 3.8+ and add to PATH
        pause
        exit /b 1
    )

    REM Check .env
    if not exist .env (
        echo ✗ .env file not found!
        echo.
        echo Please create .env file:
        echo   1. Copy .env.example to .env
        echo   2. Edit .env and add your Telegram bot token
        echo.
        pause
        exit /b 1
    )

    REM Start bot directly
    echo ✓ Starting bot...
    echo.
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo Press Ctrl+C to stop the bot
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo.

    set TOKENIZERS_PARALLELISM=false
    python scripts\interactive_evolution_bot.py

    echo.
    echo Bot stopped.
    pause
    exit /b 0
)

REM ============================================================================
REM DIAGNOSTIC MODE - Detailed system check
REM ============================================================================
if "%MODE%"=="diagnose" (
    echo ========================================================================
    echo 🔍 Flyto2 Configuration Diagnostics
    echo ========================================================================
    echo.

    REM Check if .env exists
    echo [1/7] Checking .env file...
    if exist .env (
        echo ✓ .env file exists
        echo.
        echo Content of .env:
        echo ────────────────────────────────────
        type .env
        echo ────────────────────────────────────
    ) else (
        echo ✗ .env file NOT found!
        echo   Please copy .env.example to .env
        goto :diagnose_end
    )

    echo.
    echo [2/7] Checking TELEGRAM_BOT_TOKEN...
    findstr /B "TELEGRAM_BOT_TOKEN=" .env >nul 2>nul
    if %errorlevel% equ 0 (
        for /f "tokens=2 delims==" %%a in ('findstr /B "TELEGRAM_BOT_TOKEN=" .env') do (
            set "TOKEN=%%a"
            if "!TOKEN:~0,3!"=="799" (
                echo ✓ TELEGRAM_BOT_TOKEN found: !TOKEN:~0,10!...
            ) else (
                echo ✓ TELEGRAM_BOT_TOKEN found
            )
        )
    ) else (
        echo ✗ TELEGRAM_BOT_TOKEN not found in .env
    )

    echo.
    echo [3/7] Checking for placeholder values...
    findstr /C:"your_telegram_bot_token_here" .env >nul 2>nul
    if %errorlevel% equ 0 (
        echo ⚠️  Found placeholder value - needs to be replaced
    ) else (
        findstr /C:"your_" .env >nul 2>nul
        if %errorlevel% equ 0 (
            echo ⚠️  Found placeholder values (your_*)
        ) else (
            echo ✓ No placeholders found - tokens appear to be set
        )
    )

    echo.
    echo [4/7] Checking Python...
    python --version 2>nul
    if %errorlevel% equ 0 (
        for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo ✓ Python installed: %%i
    ) else (
        echo ✗ Python is NOT installed
        echo   Download from: https://www.python.org/downloads/
    )

    echo.
    echo [5/7] Checking Python packages...
    python -c "import telegram; print('✓ python-telegram-bot:', telegram.__version__)" 2>nul
    if %errorlevel% neq 0 echo ✗ python-telegram-bot not installed

    python -c "import playwright; print('✓ playwright installed')" 2>nul
    if %errorlevel% neq 0 echo ✗ playwright not installed

    echo.
    echo [6/7] Checking Ollama...
    curl -s http://localhost:11434/api/tags >nul 2>nul
    if %errorlevel% equ 0 (
        echo ✓ Ollama is running on http://localhost:11434
    ) else (
        echo ✗ Ollama is NOT running
        echo   Please start Ollama:
        echo     - Windows: Open Ollama app
        echo     - Command: ollama serve
    )

    echo.
    echo [7/7] Testing bot script import...
    python -c "import sys; sys.path.insert(0, '.'); from scripts.interactive_evolution_bot import *" 2>test_error.txt
    if %errorlevel% equ 0 (
        echo ✓ Bot script can be imported successfully
        del test_error.txt 2>nul
    ) else (
        echo ✗ Bot script import failed
        echo.
        echo Error details:
        echo ────────────────────────────────────
        type test_error.txt 2>nul
        echo ────────────────────────────────────
        del test_error.txt 2>nul
    )

    echo.
    echo ========================================================================
    echo 🎯 Diagnosis Complete
    echo ========================================================================
    echo.
    echo If you see ✗ errors above, please fix them before starting the bot.
    echo.
    echo Commands:
    echo   START_BOT.bat          - Full setup and start
    echo   START_BOT.bat /quick   - Quick start (skip checks)
    echo.

    :diagnose_end
    pause
    exit /b 0
)

REM ============================================================================
REM FULL SETUP MODE - Auto-install all dependencies and start
REM ============================================================================
echo ========================================================================
echo 🚀 Flyto2 Bot - Auto Setup ^& Start
echo    一鍵安裝所有依賴並啟動
echo ========================================================================
echo.
echo 📍 Working directory: %SCRIPT_DIR%
echo.
echo 💡 TIP: Use "START_BOT.bat /quick" to skip checks next time
echo 💡 TIP: Use "START_BOT.bat /diagnose" for detailed diagnostics
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
echo 2️⃣  Checking GitHub CLI (Optional)...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

where gh >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  GitHub CLI not found (optional)
    echo    Bot will work without it, but PR creation won't be available
    echo.
    echo    To install GitHub CLI:
    echo      winget install --id GitHub.cli
    echo.
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

    if exist .env.example (
        echo.
        echo 💡 Found .env.example - copying to .env...
        copy .env.example .env >nul
        echo ✅ Created .env from .env.example
        echo    Please verify the configuration is correct
        set "ENV_CONFIGURED=1"
    ) else (
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
    )
) else (
    echo ✓ .env file exists

    REM Check for required keys (simplified check)
    findstr /B "TELEGRAM_BOT_TOKEN=" .env >nul 2>nul
    if errorlevel 1 (
        echo    ⚠️  TELEGRAM_BOT_TOKEN not found
        set "ENV_CONFIGURED=0"
    ) else (
        REM Check if it's a placeholder
        findstr /C:"TELEGRAM_BOT_TOKEN=your_" .env >nul 2>nul
        if errorlevel 1 (
            echo    ✓ TELEGRAM_BOT_TOKEN configured
            set "ENV_CONFIGURED=1"
        ) else (
            echo    ⚠️  TELEGRAM_BOT_TOKEN is placeholder
            set "ENV_CONFIGURED=0"
        )
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
        echo 🎉 All dependencies installed and configured!
        echo.
        echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        echo 🚀 Starting Bot...
        echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        echo.
        echo Press Ctrl+C to stop the bot
        echo.

        set TOKENIZERS_PARALLELISM=false

        if exist scripts\interactive_evolution_bot.py (
            python scripts\interactive_evolution_bot.py
        ) else (
            echo ⚠️  Bot script not found at scripts\interactive_evolution_bot.py
            echo.
            echo Available test commands:
            echo    python test_end_to_end.py          # Test system
            echo    python test_difficult_questions.py # Test AI responses
            echo    python test_pr_creation.py         # Test PR creation
        )

        echo.
        echo Bot stopped.
    ) else (
        echo ⚠️  Environment configuration needed
        echo.
        echo The .env file was created, but needs configuration:
        echo.
        echo Next steps:
        echo   1. Edit .env file with your Telegram bot token
        echo   2. Get token from: https://t.me/BotFather
        echo   3. Run this script again: START_BOT.bat
        echo.
        echo Or run diagnostics: START_BOT.bat /diagnose
    )
) else (
    echo ⚠️  Some dependencies need attention
    echo.
    echo Please check the messages above and:
    echo   1. Install Python 3.8+ if needed
    echo   2. Configure .env file with your API keys
    echo   3. Optionally install GitHub CLI
    echo   4. Run this script again
    echo.
    echo For detailed diagnostics, run: START_BOT.bat /diagnose
)

echo.
echo ========================================================================
pause
