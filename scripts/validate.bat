@echo off
REM Workflow Validation Helper Script for Windows
REM Simple wrapper around validate_workflow.yaml meta-workflow

setlocal enabledelayedexpansion

REM Check if no arguments
if "%~1"=="" (
    echo Error: No workflow path provided
    echo.
    call :show_help
    exit /b 2
)

REM Check for help flag
if "%~1"=="--help" (
    call :show_help
    exit /b 0
)
if "%~1"=="-h" (
    call :show_help
    exit /b 0
)

REM Get workflow path
set WORKFLOW_PATH=%~1
shift

REM Check if file exists
if not exist "%WORKFLOW_PATH%" (
    echo Error: Workflow file not found: %WORKFLOW_PATH%
    exit /b 2
)

REM Parse options
set STRICT=false
:parse_options
if "%~1"=="" goto run_validation
if "%~1"=="--strict" (
    set STRICT=true
    shift
    goto parse_options
)
echo Warning: Unknown option: %~1
shift
goto parse_options

:run_validation
REM Print header
echo Validating workflow: %WORKFLOW_PATH%
echo.

REM Run validation
python -m src.cli.main workflows/meta/validate_workflow.yaml --param target="%WORKFLOW_PATH%" --param strict="%STRICT%"

REM Check exit code
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [32m✓ Validation passed[0m
    exit /b 0
) else (
    echo.
    echo [31m✗ Validation failed[0m
    exit /b 1
)

:show_help
echo Flyto2 Workflow Validation Tool
echo.
echo Usage:
echo   validate.bat ^<workflow_path^> [options]
echo.
echo Options:
echo   --strict          Enable strict validation mode
echo   --help           Show this help message
echo.
echo Examples:
echo   validate.bat workflows\google_search.yaml
echo   validate.bat workflows\_generated\new_workflow.yaml --strict
echo.
echo Description:
echo   This script validates Flyto2 workflow YAML files by running the
echo   validate_workflow.yaml meta-workflow.
echo.
echo Exit Codes:
echo   0 - Validation passed
echo   1 - Validation failed
echo   2 - Invalid usage
exit /b 0
