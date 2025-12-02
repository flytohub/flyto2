@echo off
chcp 65001 >nul
REM Flyto2 Autonomous Self-Evolving AI

echo.
echo ╔════════════════════════════════════════╗
echo ║   Flyto2 Autonomous Evolution AI       ║
echo ║     Self-Learning - Always Active      ║
echo ╚════════════════════════════════════════╝
echo.

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
)

REM Install/update dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

echo.
echo ╔════════════════════════════════════════╗
echo ║  AI will auto-start training now!      ║
echo ║  • Crawls websites every hour          ║
echo ║  • Auto-evolves modules                ║
echo ║  • Updates knowledge base              ║
echo ║  • Reports to Telegram                 ║
echo ╚════════════════════════════════════════╝
echo.
echo Press Ctrl+C to stop
echo.

REM Start autonomous bot
python scripts\autonomous_bot.py

pause
