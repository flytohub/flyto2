@echo off
REM Flyto2 One-Click Auto Setup & Start (Windows)
REM 一鍵自動安裝所有依賴並啟動機器人

setlocal enabledelayedexpansion

echo ========================================================================
echo.
echo    Flyto2 Bot - Auto Setup ^& Start (Windows)
echo    一鍵安裝所有依賴並啟動
echo.
echo ========================================================================
echo.

cd /d "%~dp0"

echo Working directory: %CD%
echo.

REM ========================================================================
REM 1. Check Python
REM ========================================================================
echo ========================================================================
echo 1. Checking Python...
echo ========================================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python not found
    echo.
    echo Please install Python 3.8+ from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python found: %PYTHON_VERSION%
echo.

REM ========================================================================
REM 2. Check/Install Scoop (Windows Package Manager)
REM ========================================================================
echo ========================================================================
echo 2. Checking Scoop...
echo ========================================================================
echo.

where scoop >nul 2>&1
if errorlevel 1 (
    echo [!] Scoop not found, installing...
    echo.
    powershell -Command "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"
    powershell -Command "irm get.scoop.sh | iex"
    echo [OK] Scoop installed
) else (
    echo [OK] Scoop found
)
echo.

REM ========================================================================
REM 3. Check/Install GitHub CLI
REM ========================================================================
echo ========================================================================
echo 3. Checking GitHub CLI...
echo ========================================================================
echo.

where gh >nul 2>&1
if errorlevel 1 (
    echo [!] Installing GitHub CLI...
    echo.
    scoop install gh
    if errorlevel 1 (
        echo [!] Scoop install failed, trying winget...
        winget install --id GitHub.cli -e
    )
    echo [OK] GitHub CLI installed
) else (
    for /f "tokens=3" %%i in ('gh --version 2^>^&1 ^| findstr "gh version"') do set GH_VERSION=%%i
    echo [OK] GitHub CLI found: !GH_VERSION!
)

REM Check authentication
gh auth status >nul 2>&1
if errorlevel 1 (
    echo [!] GitHub not authenticated
    echo    You can authenticate with: gh auth login
) else (
    echo [OK] GitHub authenticated
)
echo.

REM ========================================================================
REM 4. Install Python Dependencies
REM ========================================================================
echo ========================================================================
echo 4. Installing Python Dependencies...
echo ========================================================================
echo.

echo [!] Upgrading pip...
python -m pip install --upgrade pip setuptools wheel --quiet
echo [OK] pip upgraded
echo.

if exist requirements.txt (
    echo [!] Installing core dependencies...
    pip install -r requirements.txt --quiet --exists-action i
    echo [OK] Core dependencies installed
) else (
    echo [!] requirements.txt not found, installing essential packages...
    pip install --quiet --exists-action i python-telegram-bot playwright openai qdrant-client python-dotenv aiohttp pyyaml requests
    echo [OK] Essential packages installed
)
echo.

REM ========================================================================
REM 5. Install Playwright Browsers
REM ========================================================================
echo ========================================================================
echo 5. Installing Playwright Browsers...
echo ========================================================================
echo.

python -c "import playwright" >nul 2>&1
if not errorlevel 1 (
    echo [!] Installing Chromium browser...
    playwright install chromium
    echo [OK] Playwright browsers installed
) else (
    echo [!] Playwright not found in pip install
)
echo.

REM ========================================================================
REM 6. Check Environment Variables
REM ========================================================================
echo ========================================================================
echo 6. Checking Environment Variables...
echo ========================================================================
echo.

if not exist .env (
    echo [!] .env file not found
    echo    Creating template .env file...
    echo.

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
        echo # Ollama ^(optional^)
        echo OLLAMA_BASE_URL=http://localhost:11434
        echo OLLAMA_MODEL=llama3.2:3b
        echo.
        echo # GitHub ^(optional, for auto PR creation^)
        echo GITHUB_TOKEN=your_github_token_here
    ) > .env

    echo [OK] Template .env created
    echo [!] Please edit .env and add your API keys
) else (
    echo [OK] .env file exists

    REM Check for required keys
    findstr /C:"TELEGRAM_BOT_TOKEN=" .env | findstr /V /C:"your_telegram_bot_token_here" >nul
    if errorlevel 1 (
        echo    [!] TELEGRAM_BOT_TOKEN not set
    ) else (
        echo    [OK] TELEGRAM_BOT_TOKEN configured
    )

    findstr /C:"OPENAI_API_KEY=" .env | findstr /V /C:"your_openai_api_key_here" >nul
    if errorlevel 1 (
        echo    [!] OPENAI_API_KEY not set
    ) else (
        echo    [OK] OPENAI_API_KEY configured
    )

    findstr /C:"QDRANT_URL=" .env | findstr /V /C:"your_qdrant_url_here" >nul
    if errorlevel 1 (
        echo    [!] QDRANT credentials not set
    ) else (
        echo    [OK] QDRANT credentials configured
    )
)
echo.

REM ========================================================================
REM 7. Test System
REM ========================================================================
echo ========================================================================
echo 7. Testing System...
echo ========================================================================
echo.

echo [!] Testing module registry...
python -c "from src.core.modules.registry import ModuleRegistry; print(f'Modules loaded: {len(ModuleRegistry.list_all())}')" >nul 2>&1
if errorlevel 1 (
    echo [X] Module registry test failed
) else (
    echo [OK] Module registry working
)
echo.

REM ========================================================================
REM 8. Summary
REM ========================================================================
echo ========================================================================
echo.
echo    Setup Summary
echo.
echo ========================================================================
echo.

set /a READY_COUNT=0
set /a TOTAL_COUNT=7

python --version >nul 2>&1
if not errorlevel 1 set /a READY_COUNT+=1

where scoop >nul 2>&1
if not errorlevel 1 set /a READY_COUNT+=1

where gh >nul 2>&1
if not errorlevel 1 set /a READY_COUNT+=1

python -m pip --version >nul 2>&1
if not errorlevel 1 set /a READY_COUNT+=1

python -c "import playwright" >nul 2>&1
if not errorlevel 1 set /a READY_COUNT+=1

if exist .env set /a READY_COUNT+=1

python -c "from src.core.modules.registry import ModuleRegistry" >nul 2>&1
if not errorlevel 1 set /a READY_COUNT+=1

echo [OK] Ready: %READY_COUNT%/%TOTAL_COUNT%
echo.

if %READY_COUNT% EQU %TOTAL_COUNT% (
    echo [OK] All dependencies installed!
    echo.
    echo ========================================================================
    echo.
    echo    Starting Bot...
    echo.
    echo ========================================================================
    echo.

    if exist scripts\interactive_evolution_bot.py (
        set TOKENIZERS_PARALLELISM=false
        python scripts\interactive_evolution_bot.py
    ) else (
        echo [!] Bot script not found at scripts\interactive_evolution_bot.py
        echo.
        echo    Available commands:
        echo    - python test_end_to_end.py          # Test system
        echo    - python test_difficult_questions.py # Test AI responses
        echo    - python test_pr_creation.py         # Test PR creation
    )
) else (
    echo [!] Some dependencies need attention
    echo.
    echo Next steps:
    echo 1. Edit .env file with your API keys
    echo 2. If needed: gh auth login
    echo 3. Run this script again: START_BOT_AUTO.bat
)

echo.
echo ========================================================================
echo.

pause
