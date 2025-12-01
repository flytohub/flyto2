# Windows Setup Guide

Complete guide for setting up Flyto2 with Level 4 monitoring on Windows.

## Prerequisites

### Required Software

1. **Python 3.8+**
   ```powershell
   # Check Python version
   python --version
   # Should show Python 3.8 or higher
   ```
   Download from: https://www.python.org/downloads/

2. **Git**
   ```powershell
   # Check Git installation
   git --version
   ```
   Download from: https://git-scm.com/download/win

3. **GitHub CLI (gh)**
   ```powershell
   # Check gh installation
   gh --version
   ```
   Download from: https://cli.github.com/

4. **Task Scheduler** (built-in to Windows)
   - Used for running scheduled workflows

## Installation Steps

### Step 1: Clone Repository

```powershell
# Clone to your preferred location
cd C:\Projects
git clone <your-repo-url> flyto2
cd flyto2
```

### Step 2: Setup Python Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create `.env` file in project root:

```powershell
# Create .env file
New-Item -Path .env -ItemType File

# Edit with notepad
notepad .env
```

Add the following to `.env`:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# OpenAI API (if using AI modules)
OPENAI_API_KEY=your_openai_key_here

# GitHub (for auto-merge PR workflow)
GITHUB_TOKEN=your_github_token_here
```

**Get Telegram Bot Token:**
1. Talk to @BotFather on Telegram
2. Create new bot: `/newbot`
3. Copy the token
4. Get your chat ID: Talk to @userinfobot

**Get GitHub Token:**
```powershell
gh auth login
gh auth token
```

### Step 4: Test Installation

```powershell
# Test basic workflow execution
python -m src.cli.main workflows/_test/test_string_split.yaml

# Should see test execution output
```

## Running Workflows Manually

### Run Quality Tests

```powershell
# Test all modules (takes ~5 minutes)
.\scripts\run_quality_tests.sh

# On Windows, if bash not available, use Git Bash or:
bash scripts/run_quality_tests.sh

# Or run directly with Python
python -c "import subprocess; subprocess.run(['bash', 'scripts/run_quality_tests.sh'])"
```

### Run Regression Monitoring (Manual)

```powershell
# Activate virtual environment first
.\venv\Scripts\Activate.ps1

# Run regression monitoring
python -m src.cli.main workflows/meta/monitor_regressions.yaml

# Will check all modules and send Telegram report
```

### Test Auto-Merge PR (Manual)

```powershell
# Make sure you have a PR ready
# Then run:
python -m src.cli.main workflows/meta/auto_merge_pr.yaml --params module_id=string.split pr_number=123
```

## Scheduling Workflows on Windows

### Option 1: Task Scheduler (Recommended)

Create scheduled tasks for daily monitoring.

#### Create Daily Regression Monitoring Task

1. **Create PowerShell Script**

Create `scripts/run_monitor_regressions.ps1`:

```powershell
# run_monitor_regressions.ps1
Set-Location "C:\Projects\flyto2"
.\venv\Scripts\Activate.ps1
python -m src.cli.main workflows/meta/monitor_regressions.yaml
```

2. **Create Scheduled Task**

Open PowerShell as Administrator:

```powershell
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
  -Argument "-ExecutionPolicy Bypass -File C:\Projects\flyto2\scripts\run_monitor_regressions.ps1"

$trigger = New-ScheduledTaskTrigger -Daily -At 9am

$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -RunLevel Highest

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "Flyto2-MonitorRegressions" `
  -Action $action `
  -Trigger $trigger `
  -Principal $principal `
  -Settings $settings `
  -Description "Daily regression monitoring for Flyto2 modules"
```

3. **Verify Task**

```powershell
# List scheduled tasks
Get-ScheduledTask -TaskName "Flyto2-*"

# Run task manually to test
Start-ScheduledTask -TaskName "Flyto2-MonitorRegressions"
```

### Option 2: Windows Service (Advanced)

For production environments, consider using NSSM (Non-Sucking Service Manager):

```powershell
# Download NSSM from https://nssm.cc/download

# Install service
nssm install Flyto2Monitor "C:\Projects\flyto2\venv\Scripts\python.exe" `
  "-m src.cli.main workflows/meta/monitor_regressions.yaml"

# Set working directory
nssm set Flyto2Monitor AppDirectory "C:\Projects\flyto2"

# Start service
nssm start Flyto2Monitor
```

## File Paths on Windows

Important notes about path handling:

### In YAML workflows:

```yaml
# Use forward slashes (will work on Windows)
file_path: "metrics/module_quality.json"

# Or use backslashes with escaping
file_path: "metrics\\module_quality.json"
```

### In Python scripts:

```python
# Use Path from pathlib (recommended)
from pathlib import Path
metrics_file = Path("metrics/module_quality.json")

# Works on both Windows and Unix
```

### In Bash scripts:

```bash
# If using Git Bash on Windows, use Unix-style paths
RESULTS_FILE="metrics/test_results.txt"
```

## Troubleshooting

### Issue: PowerShell Execution Policy

**Error:**
```
cannot be loaded because running scripts is disabled on this system
```

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Python not found

**Error:**
```
'python' is not recognized as an internal or external command
```

**Solution:**
```powershell
# Add Python to PATH, or use full path
C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe
```

### Issue: Git Bash required for shell scripts

**Solution:**
Install Git for Windows (includes Git Bash), or convert scripts to PowerShell.

### Issue: Telegram notifications not working

**Check:**
1. `.env` file exists in project root
2. `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set
3. Bot has permission to send messages to you

```powershell
# Test environment variables
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('TELEGRAM_BOT_TOKEN'))"
```

### Issue: Module imports failing

**Solution:**
```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

## Maintenance

### Update Metrics After Tests

```powershell
# After running quality tests
python scripts/update_metrics.py metrics/test_results_YYYYMMDD_HHMMSS.txt
```

### View Deployment History

```powershell
python scripts/deployment_manager.py info string.split
```

### Manual Rollback (if needed)

```powershell
python scripts/deployment_manager.py rollback string.split "Manual rollback due to issue" 0.95
```

## Production Recommendations

1. **Use Windows Task Scheduler** for daily monitoring
2. **Set up logging** to track workflow executions
3. **Monitor disk space** for test results and snapshots
4. **Regular backups** of `metrics/` directory
5. **Keep virtual environment updated**

```powershell
# Regular maintenance schedule
pip install --upgrade pip
pip install -r requirements.txt --upgrade
```

## Directory Structure on Windows

```
C:\Projects\flyto2\
├── .env                          # Environment variables
├── .git\                         # Git repository
├── venv\                         # Virtual environment
├── src\                          # Source code
├── workflows\                    # Workflow definitions
│   ├── _test\                   # Test workflows
│   └── meta\                    # Meta workflows
├── metrics\                      # Quality metrics
│   ├── module_quality.json      # Current quality data
│   ├── module_deployment_history.json
│   ├── snapshots\               # Module snapshots
│   └── test_results_*.txt       # Test results
├── scripts\                      # Automation scripts
│   ├── run_quality_tests.sh     # Bash script
│   ├── run_monitor_regressions.ps1  # PowerShell script
│   ├── deployment_manager.py
│   └── update_metrics.py
└── logs\                         # Execution logs (create this)
```

## Next Steps

1. ✅ Complete installation and test basic workflows
2. ✅ Set up Telegram bot and verify notifications
3. ✅ Run manual regression monitoring to verify it works
4. ✅ Create scheduled task for daily monitoring
5. ⏳ Monitor for 1-2 weeks to build confidence
6. ⏳ Test manual auto-merge PR workflow
7. ⏳ Gradually enable more automation as confidence grows

## Getting Help

- Check logs in Windows Event Viewer for scheduled task issues
- Review Telegram messages for workflow execution status
- Check `metrics/test_results_*.txt` for detailed test output
- Use GitHub Issues for bug reports and feature requests
