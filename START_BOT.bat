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
        echo Enter your OpenAI API Key:
        set /p openai_key="OPENAI_API_KEY=sk-"

        REM Add key to .env file
        echo OPENAI_API_KEY=sk-%openai_key%>> .env

        echo.
        echo ✓ API Key saved to .env
        echo Using three-tier strategy ^(Ollama -^> Human -^> OpenAI^)
        echo.
    ) else (
        echo.
        echo Running with Ollama only ^(free^)
        echo.
    )
)

REM ========================================
REM V4 Feature Check
REM ========================================
findstr /C:"QDRANT_URL=" .env >nul 2>&1
if %errorlevel% equ 0 (
    echo V4 Features: ENABLED
    echo - Evolution Pipeline
    echo - Knowledge Base
    echo - Auto-Debug
) else (
    echo V4 Features: Basic Mode
)
echo.

REM ========================================
REM Start Interactive Evolution Bot
REM ========================================
echo ========================================
echo Starting Flyto2 V4 Interactive Bot
echo - Evolution: /evolve /debug
echo - Modules: /modules
echo - Memory: /memory_search
echo - Practice: /practice
echo - Competition: /competition
echo ========================================
echo.
echo Press Ctrl+C to stop
echo.

python scripts\interactive_evolution_bot.py

pause
