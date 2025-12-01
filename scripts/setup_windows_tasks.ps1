# setup_windows_tasks.ps1
# Setup Windows Task Scheduler tasks for Flyto2 monitoring
# Run this script as Administrator

param(
    [string]$ProjectPath = "C:\Projects\flyto2",
    [string]$MonitorTime = "09:00"  # 9 AM
)

Write-Host "Setting up Windows Scheduled Tasks for Flyto2" -ForegroundColor Cyan
Write-Host "Project Path: $ProjectPath" -ForegroundColor Yellow
Write-Host ""

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Verify project path exists
if (-not (Test-Path $ProjectPath)) {
    Write-Host "ERROR: Project path not found: $ProjectPath" -ForegroundColor Red
    exit 1
}

# Verify scripts exist
$monitorScript = Join-Path $ProjectPath "scripts\run_monitor_regressions.ps1"
if (-not (Test-Path $monitorScript)) {
    Write-Host "ERROR: Monitor script not found: $monitorScript" -ForegroundColor Red
    exit 1
}

Write-Host "Creating Task: Flyto2-MonitorRegressions" -ForegroundColor Green

# Create action
$action = New-ScheduledTaskAction `
    -Execute "PowerShell.exe" `
    -Argument "-ExecutionPolicy Bypass -NoProfile -File `"$monitorScript`" -ProjectPath `"$ProjectPath`""

# Create trigger (daily at specified time)
$trigger = New-ScheduledTaskTrigger -Daily -At $MonitorTime

# Create principal (run as current user)
$principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERNAME" `
    -RunLevel Highest `
    -LogonType Interactive

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

# Remove existing task if it exists
$existingTask = Get-ScheduledTask -TaskName "Flyto2-MonitorRegressions" -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Removing existing task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName "Flyto2-MonitorRegressions" -Confirm:$false
}

# Register new task
Register-ScheduledTask `
    -TaskName "Flyto2-MonitorRegressions" `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Settings $settings `
    -Description "Daily regression monitoring for Flyto2 modules. Runs at $MonitorTime daily and sends Telegram reports."

Write-Host ""
Write-Host "Task created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Task Details:" -ForegroundColor Cyan
Write-Host "  Name: Flyto2-MonitorRegressions" -ForegroundColor White
Write-Host "  Schedule: Daily at $MonitorTime" -ForegroundColor White
Write-Host "  Script: $monitorScript" -ForegroundColor White
Write-Host ""

# Test the task
Write-Host "Would you like to test the task now? (Y/N)" -ForegroundColor Yellow
$response = Read-Host

if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host ""
    Write-Host "Running task manually..." -ForegroundColor Green
    Start-ScheduledTask -TaskName "Flyto2-MonitorRegressions"

    Write-Host ""
    Write-Host "Task started. Check Task Scheduler for status." -ForegroundColor Green
    Write-Host "You should receive a Telegram notification when complete." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To manage tasks:" -ForegroundColor Cyan
Write-Host "  View all tasks:  Get-ScheduledTask -TaskName 'Flyto2-*'" -ForegroundColor White
Write-Host "  Run manually:    Start-ScheduledTask -TaskName 'Flyto2-MonitorRegressions'" -ForegroundColor White
Write-Host "  Disable task:    Disable-ScheduledTask -TaskName 'Flyto2-MonitorRegressions'" -ForegroundColor White
Write-Host "  Remove task:     Unregister-ScheduledTask -TaskName 'Flyto2-MonitorRegressions'" -ForegroundColor White
Write-Host ""
