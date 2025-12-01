# run_monitor_regressions.ps1
# PowerShell script to run regression monitoring on Windows
# Can be used with Windows Task Scheduler

param(
    [string]$ProjectPath = "C:\Projects\flyto2"
)

# Set working directory
Set-Location $ProjectPath

# Activate virtual environment
& "$ProjectPath\venv\Scripts\Activate.ps1"

# Run regression monitoring
Write-Host "Starting regression monitoring..." -ForegroundColor Green
python -m src.cli.main workflows/meta/monitor_regressions.yaml

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host "Regression monitoring completed successfully" -ForegroundColor Green
} else {
    Write-Host "Regression monitoring failed with exit code $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}
