@echo off
REM Setup Windows Scheduled Tasks for Flyto2 V4

cd /d "%~dp0\.."

echo ========================================
echo Setup Flyto2 Scheduled Tasks
echo ========================================
echo.

REM Get Python path
for /f "delims=" %%i in ('where python') do set PYTHON_PATH=%%i
echo Python: %PYTHON_PATH%
echo Project: %CD%
echo.

REM Task 1: Hourly Debug Analysis
echo Creating Task: Hourly Debug Analysis...
schtasks /create /tn "Flyto2_Debug_Analysis" /tr "\"%PYTHON_PATH%\" \"%CD%\scripts\run_scheduled_tasks.py\" --task debug" /sc hourly /ru "%USERNAME%" /f
if %errorlevel% equ 0 (
    echo   [OK] Debug Analysis task created
) else (
    echo   [FAIL] Failed to create debug task
)
echo.

REM Task 2: Daily Catalog Update
echo Creating Task: Daily Catalog Update...
schtasks /create /tn "Flyto2_Catalog_Update" /tr "\"%PYTHON_PATH%\" \"%CD%\scripts\run_scheduled_tasks.py\" --task catalog" /sc daily /st 00:00 /ru "%USERNAME%" /f
if %errorlevel% equ 0 (
    echo   [OK] Catalog Update task created
) else (
    echo   [FAIL] Failed to create catalog task
)
echo.

REM Task 3: Every 6 hours - Check Evolution Tickets
echo Creating Task: Evolution Tickets Check...
schtasks /create /tn "Flyto2_Evolution_Check" /tr "\"%PYTHON_PATH%\" \"%CD%\scripts\run_scheduled_tasks.py\" --task tickets" /sc hourly /mo 6 /ru "%USERNAME%" /f
if %errorlevel% equ 0 (
    echo   [OK] Evolution Check task created
) else (
    echo   [FAIL] Failed to create evolution task
)
echo.

echo ========================================
echo Scheduled Tasks Created
echo ========================================
echo.
echo View tasks with: schtasks /query /tn "Flyto2_*"
echo Delete task: schtasks /delete /tn "Flyto2_Debug_Analysis"
echo.

pause
