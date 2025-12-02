@echo off
REM Flyto2 Telegram Bot with Vector Database Memory
REM One-click deployment for Windows

echo ============================================
echo Flyto2 AI Agent Bot with Long-Term Memory
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.10+
    pause
    exit /b 1
)

echo [1/4] Checking dependencies...
pip show python-telegram-bot >nul 2>&1
if errorlevel 1 (
    echo Installing Telegram Bot dependencies...
    pip install python-telegram-bot python-dotenv requests openai
)

pip show qdrant-client >nul 2>&1
if errorlevel 1 (
    echo Installing Vector Database dependencies...
    pip install qdrant-client sentence-transformers
)

echo [2/4] Checking environment variables...
if not exist .env (
    echo ERROR: .env file not found!
    echo.
    echo Please create .env file with:
    echo TELEGRAM_BOT_TOKEN=your_bot_token
    echo TELEGRAM_ALLOWED_USERS=your_telegram_user_id
    echo OLLAMA_URL=http://localhost:11434
    echo.
    pause
    exit /b 1
)

echo [3/4] Starting Qdrant vector database...
start /B "" qdrant 2>nul
timeout /t 2 /nobreak >nul

echo [4/4] Starting Telegram Bot...
echo.
echo Bot Features:
echo - Three-Tier AI: Ollama -^> Human -^> OpenAI
echo - Vector Database Long-Term Memory
echo - Auto Quality Filtering
echo - Commands: /memory, /stats, /status
echo.
echo Cost: ~NT$30-60/month
echo.
echo Press Ctrl+C to stop
echo ============================================
echo.

python scripts/telegram_bot_v2.py

pause
