@echo off
chcp 65001 >nul
REM Flyto2 Autonomous Self-Evolving AI - Interactive Setup

REM Change to script directory
cd /d "%~dp0"

echo.
echo ========================================
echo    Flyto2 Autonomous Evolution AI
echo    Interactive Setup ^& Launcher
echo ========================================
echo.

REM ========================================
REM Step 1: Check .env configuration
REM ========================================
if not exist .env (
    echo [1/4] Configuration Check
    echo.
    echo WARNING: .env file not found!
    echo.
    echo Required configuration:
    echo   - Telegram Bot Token
    echo   - Telegram User ID
    echo   - OpenAI API Key ^(optional^)
    echo.
    set /p create_env="Create .env file now? (Y/N): "
    if /i "%create_env%"=="Y" (
        echo.
        echo Copying .env.example to .env...
        copy .env.example .env >nul
        echo.
        echo SUCCESS: .env file created!
        echo.
        echo IMPORTANT: Edit .env file and fill in your tokens
        echo Then run START_BOT.bat again
        echo.
        pause
        exit /b
    ) else (
        echo.
        echo ERROR: Cannot start without .env file
        echo Please see SETUP.md for configuration guide
        echo.
        pause
        exit /b
    )
) else (
    echo [1/4] Configuration Check - OK
    echo.
)

REM ========================================
REM Step 2: Virtual environment
REM ========================================
echo [2/4] Virtual Environment Setup
echo.
if exist venv\Scripts\activate.bat (
    echo Virtual environment found - activating...
    call venv\Scripts\activate.bat
) else (
    set /p create_venv="Create Python virtual environment? (Y/N): "
    if /i "%create_venv%"=="Y" (
        echo.
        echo Creating virtual environment...
        python -m venv venv
        call venv\Scripts\activate.bat
        echo Virtual environment created successfully!
    ) else (
        echo Skipping virtual environment
    )
)
echo.

REM ========================================
REM Step 3: Dependencies
REM ========================================
echo [3/4] Dependencies Installation
echo.
set /p install_deps="Install/update dependencies? (Y/N): "
if /i "%install_deps%"=="Y" (
    echo.
    echo Installing dependencies...
    pip install -q -r requirements.txt
    echo Dependencies installed successfully!
) else (
    echo Skipping dependencies installation
)
echo.

REM ========================================
REM Step 4: Select mode
REM ========================================
echo [4/4] Mode Selection
echo.
echo Select startup mode:
echo.
echo [1] Full Auto Mode - Training every hour
echo     - Web crawler practice
echo     - Auto-evolution cycles
echo     - Vector DB updates
echo     - Telegram notifications
echo.
echo [2] Telegram Chat Bot Only
echo     - Conversation features ^(Ollama + OpenAI^)
echo     - Language selection
echo     - Vector DB management
echo     - Manual evolution triggers
echo.
echo [3] Interactive Evolution Mode
echo     - Manual step control
echo     - Real-time review
echo.
echo [0] Cancel
echo.
set /p mode="Enter option (0-3): "

if "%mode%"=="1" (
    echo.
    echo ========================================
    echo   Starting Full Auto Mode
    echo   - Auto-training every hour
    echo   - Auto-evolution and learning
    echo   - Telegram notifications
    echo ========================================
    echo.
    set /p confirm="Start now? (Y/N): "
    if /i "%confirm%"=="Y" (
        echo.
        echo Starting... Press Ctrl+C to stop
        echo.
        python scripts\autonomous_bot.py
    ) else (
        echo Cancelled
    )
) else if "%mode%"=="2" (
    echo.
    echo ========================================
    echo   Starting Telegram Chat Bot
    echo   - Conversation features
    echo   - Use /start to see all commands
    echo ========================================
    echo.
    set /p confirm="Start now? (Y/N): "
    if /i "%confirm%"=="Y" (
        echo.
        echo Starting... Press Ctrl+C to stop
        echo.
        python scripts\telegram_bot_v2.py
    ) else (
        echo Cancelled
    )
) else if "%mode%"=="3" (
    echo.
    echo ========================================
    echo   Starting Interactive Evolution Mode
    echo   - Manual step control
    echo   - Real-time review
    echo ========================================
    echo.
    set /p confirm="Start now? (Y/N): "
    if /i "%confirm%"=="Y" (
        echo.
        echo Starting... Press Ctrl+C to stop
        echo.
        python scripts\interactive_evolution_bot.py
    ) else (
        echo Cancelled
    )
) else if "%mode%"=="0" (
    echo.
    echo Startup cancelled
) else (
    echo.
    echo Invalid option!
)

echo.
pause
