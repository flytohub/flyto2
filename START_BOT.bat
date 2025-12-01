@echo off
REM Flyto2 Telegram Bot - One-Click Launcher
REM Double-click this file to start the bot

echo.
echo ╔════════════════════════════════════════╗
echo ║  Flyto2 Telegram Bot Launcher          ║
echo ╚════════════════════════════════════════╝
echo.

REM Check if PowerShell is available
where powershell >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PowerShell not found
    echo Please run: scripts\start_bot_windows.ps1 manually
    pause
    exit /b 1
)

REM Run the PowerShell launcher
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\start_bot_windows.ps1"

pause
