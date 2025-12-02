@echo off
REM Flyto2 Bot - Ultra Simple Launcher
REM Just works, no fancy checks

echo ========================================
echo Flyto2 Bot Launcher
echo ========================================
echo.

cd /d "%~dp0"

REM Quick Python check
python --version >nul 2>nul
if errorlevel 1 goto :no_python

REM Quick .env check
if not exist .env goto :no_env

REM Start bot
echo Starting bot...
echo Press Ctrl+C to stop
echo.

set TOKENIZERS_PARALLELISM=false
python scripts\interactive_evolution_bot.py

echo.
echo Bot stopped.
pause
exit /b 0

:no_python
echo ERROR: Python not installed
echo Please install from: https://www.python.org/downloads/
pause
exit /b 1

:no_env
echo ERROR: .env file not found
echo.
if exist .env.example (
    echo Creating .env from .env.example...
    copy .env.example .env
    echo Done! Now starting bot...
    echo.
    set TOKENIZERS_PARALLELISM=false
    python scripts\interactive_evolution_bot.py
    echo.
    echo Bot stopped.
    pause
    exit /b 0
)
echo Please create .env file with your Telegram token
pause
exit /b 1
