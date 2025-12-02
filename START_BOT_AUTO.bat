@echo off
chcp 65001 >nul
REM Flyto2 Autonomous Self-Evolving AI
REM Starts automatically and never stops learning!

echo.
echo ╔════════════════════════════════════════╗
echo ║   Flyto2 AUTONOMOUS Evolution Mode     ║
echo ║     Self-Learning AI - Always On       ║
echo ╚════════════════════════════════════════╝
echo.
echo This mode will:
echo   • Auto-train on websites every hour
echo   • Auto-evolve and improve modules
echo   • Auto-aggregate knowledge to vector DB
echo   • Never stop learning (until you stop it)
echo.
echo Press Ctrl+C to stop autonomous mode
echo.
pause

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies if needed
pip install -q -r requirements.txt

REM Start autonomous bot
echo.
echo 🤖 Starting Autonomous AI...
echo.
python scripts/autonomous_bot.py

pause
