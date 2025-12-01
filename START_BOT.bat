@echo off
chcp 65001 >nul
REM Flyto2 Interactive Evolution System
REM Autonomous AI Agent + Telegram Bot

echo.
echo ╔════════════════════════════════════════╗
echo ║      Flyto2 Interactive Evolution       ║
echo ║         Autonomous AI System            ║
echo ╚════════════════════════════════════════╝
echo.

REM Check if PowerShell is available
where powershell >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] PowerShell not found.
    pause
    exit /b 1
)

REM Start the interactive evolution launcher
echo Launching Interactive Evolution System...
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\start_interactive_evolution.ps1"

pause
