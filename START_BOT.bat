@echo off
chcp 65001 >nul
REM Flyto2 Interactive Evolution System
REM 自主進化 AI Agent + Telegram Bot

echo.
echo ╔════════════════════════════════════════╗
echo ║  Flyto2 互動式自主進化系統              ║
echo ║  Interactive Evolution System          ║
echo ╚════════════════════════════════════════╝
echo.

REM Check if PowerShell is available
where powershell >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [錯誤] PowerShell 未找到
    pause
    exit /b 1
)

REM Run the interactive evolution launcher
echo 啟動互動式進化系統...
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\start_interactive_evolution.ps1"

pause
