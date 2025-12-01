# Quick Start - Windows

Fast setup guide for running Flyto2 Level 4 monitoring on Windows.

## 5-Minute Setup

### 1. Install Prerequisites

```powershell
# Check if installed
python --version  # Need 3.8+
git --version
gh --version

# If missing, download:
# Python: https://www.python.org/downloads/
# Git: https://git-scm.com/download/win
# GitHub CLI: https://cli.github.com/
```

### 2. Clone and Setup

```powershell
# Clone repository
cd C:\Projects
git clone <your-repo-url> flyto2
cd flyto2

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# If execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```powershell
# Create .env file
@"
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
OPENAI_API_KEY=your_openai_key
GITHUB_TOKEN=your_github_token
"@ | Out-File -FilePath .env -Encoding UTF8
```

**Get Telegram credentials:**
1. Talk to @BotFather on Telegram → `/newbot`
2. Talk to @userinfobot → get your chat ID

**Get GitHub token:**
```powershell
gh auth login
gh auth token
```

### 4. Test It Works

```powershell
# Test a simple workflow
python -m src.cli.main workflows/_test/test_string_split.yaml

# Should see: "Workflow completed successfully"
```

### 5. Run Daily Monitoring

```powershell
# Manual test first
python -m src.cli.main workflows/meta/monitor_regressions.yaml

# Check Telegram - you should get a report!
```

### 6. Schedule Daily Monitoring

```powershell
# Run as Administrator
.\scripts\setup_windows_tasks.ps1

# This creates a daily 9 AM task
# You'll be asked if you want to test it now - say Y
```

## Done!

Your system will now:
- ✅ Monitor 21 modules every day at 9 AM
- ✅ Send Telegram reports if regressions detected
- ✅ Track quality metrics in `metrics/module_quality.json`

## What's Next?

### Week 1-2: Monitor Daily Reports

Just let it run and check Telegram每天早上 9:00.

Reports look like:
```
✅ Regression Monitoring Report

Status: ALL HEALTHY
Time: 2025-12-01 09:00 UTC

Summary:
• Total modules checked: 21
• Regressions: 0 🚨
• Warnings: 0 ⚠️
• Healthy: 21 ✅
```

### Week 3+: Test Manual Auto-Merge

When you have a PR ready:

```powershell
# Make sure PR is ready and mergeable
python -m src.cli.main workflows/meta/auto_merge_pr.yaml `
  --params module_id=string.split pr_number=123
```

Only works for: `string.*`, `array.*`, `data.json.*`, `math.*`, `object.*`

## Common Commands

```powershell
# Activate environment
.\venv\Scripts\Activate.ps1

# Run regression monitoring manually
python -m src.cli.main workflows/meta/monitor_regressions.yaml

# Run quality tests for all modules
bash scripts/run_quality_tests.sh  # Need Git Bash

# Update metrics after tests
python scripts/update_metrics.py metrics/test_results_*.txt

# View module deployment info
python scripts/deployment_manager.py info string.split

# Check scheduled tasks
Get-ScheduledTask -TaskName "Flyto2-*"

# Run task manually
Start-ScheduledTask -TaskName "Flyto2-MonitorRegressions"
```

## Troubleshooting

**Virtual environment not activating?**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Python not found?**
```powershell
# Use full path
C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe -m venv venv
```

**No Telegram notifications?**
- Check `.env` file exists
- Check bot token and chat ID are correct
- Make sure you started a conversation with your bot

**Scheduled task not running?**
- Open Task Scheduler (search in Start menu)
- Find "Flyto2-MonitorRegressions"
- Check "Last Run Result" - should be 0x0 (success)
- Check "History" tab for details

## File Locations

```
C:\Projects\flyto2\
├── .env                    # Your secrets (don't commit!)
├── venv\                   # Virtual environment
├── metrics\
│   ├── module_quality.json           # Current quality
│   ├── module_deployment_history.json
│   └── test_results_*.txt            # Test outputs
├── workflows\
│   ├── _test\              # Test workflows
│   └── meta\
│       ├── monitor_regressions.yaml  # Daily monitoring
│       └── auto_merge_pr.yaml        # Manual auto-merge
└── scripts\
    ├── run_monitor_regressions.ps1   # PowerShell runner
    └── setup_windows_tasks.ps1       # Task setup
```

## Need More Help?

- 📖 Full guide: `docs/WINDOWS_SETUP.md`
- 🏗️ Architecture: `docs/LEVEL_4_ARCHITECTURE.md`
- ❓ Issues: GitHub Issues

---

**Remember:** Start slow, build confidence, then gradually enable automation! 🚀
