@echo off
chcp 65001 >nul
REM Flyto2 Autonomous Self-Evolving AI - Auto Setup

REM Change to script directory
cd /d "%~dp0"

echo.
echo ========================================
echo    Flyto2 Autonomous Evolution AI
echo ========================================
echo.

REM ========================================
REM Step 1: Check .env configuration
REM ========================================
if not exist .env (
    echo Creating .env configuration file...
    copy .env.example .env >nul
    echo.
    echo IMPORTANT: Please edit .env file and fill in:
    echo   - TELEGRAM_BOT_TOKEN
    echo   - TELEGRAM_ALLOWED_USERS
    echo.
    echo Then run START_BOT.bat again
    echo.
    pause
    exit /b
)

REM ========================================
REM Step 2: Virtual environment (auto)
REM ========================================
if not exist venv\Scripts\activate.bat (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat

REM ========================================
REM Step 3: Dependencies (auto)
REM ========================================
echo Installing dependencies...
pip install -q -r requirements.txt
echo.

REM ========================================
REM Step 4: OpenAI Check
REM ========================================
findstr /C:"OPENAI_API_KEY=sk-" .env >nul 2>&1
if %errorlevel% equ 0 (
    echo OpenAI API Key detected - using three-tier strategy
    echo ^(Ollama -^> Human -^> OpenAI^)
    echo.
) else (
    echo.
    echo OpenAI API Key not found in .env
    echo.
    set /p enable_openai="Enable OpenAI? (Y/N): "
    if /i "%enable_openai%"=="Y" (
        echo.
        echo Please add your OpenAI API key to .env file:
        echo   OPENAI_API_KEY=sk-your-key-here
        echo.
        echo Then run START_BOT.bat again
        echo.
        pause
        exit /b
    ) else (
        echo.
        echo Running with Ollama only ^(free^)
        echo.
    )
)

REM ========================================
REM Start Unified Bot
REM ========================================
echo ========================================
echo Starting Unified Bot
echo - Chat features: /start /lang /gpt /memory
echo - Auto-training in background
echo - All features in one bot
echo ========================================
echo.
echo Press Ctrl+C to stop
echo.

python scripts\unified_bot.py

pause
