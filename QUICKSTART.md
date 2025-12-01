# 🚀 Quick Start Guide

Welcome to Flyto2! Choose your setup path below.

---

## Quick Links

- **For Contributors** → [Developer Setup](#developer-setup-for-contributors)
- **For Windows Users (Bot)** → [Windows Bot Setup](#windows-bot-setup-one-click)
- **For Windows Users (Monitoring)** → [Windows Monitoring Setup](#windows-monitoring-setup)

---

## Developer Setup (For Contributors)

Get started contributing to Flyto2 in **5 minutes**.

### Prerequisites

- Python 3.8+ installed
- Git installed
- Basic Python knowledge
- (Optional) Playwright for browser automation

### 1. Clone & Setup (2 minutes)

```bash
# Clone the repository
git clone https://github.com/flytohub/flyto2.git
cd flyto2

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development

# Install Playwright browsers (optional, for browser modules)
playwright install chromium
```

### 2. Run Your First Workflow (1 minute)

```bash
# Run a simple example workflow
python -m src.cli.main workflows/api_pipeline.yaml
```

You should see output showing the workflow executing successfully! ✅

### 3. Explore the Codebase (2 minutes)

**Project Structure:**

```
flyto2/
├── src/
│   └── core/
│       ├── engine/          # Workflow execution engine
│       ├── modules/         # All 56 modules
│       │   ├── atomic/      # Core modules (no dependencies)
│       │   └── third_party/ # External integrations
│       └── browser/         # Playwright browser driver
│
├── workflows/               # Example YAML workflows
├── tests/                   # Unit tests
├── docs/                    # Documentation
└── i18n/                    # Translations (en, zh, ja)
```

**Key Files:**
- **Module Registry**: `src/core/modules/registry.py`
- **Module Base Class**: `src/core/modules/base.py`
- **Workflow Engine**: `src/core/engine/workflow_engine.py`
- **Module Specification**: `docs/MODULE_SPECIFICATION.md`

### 4. Development Best Practices

**Before Submitting a PR:**

```bash
# 1. Validate modules
python scripts/validate_all_modules.py

# 2. Run linter
python scripts/lint_modules.py --strict

# 3. Run tests
python -m pytest tests/ -v

# 4. Check Phase 2 compliance
python -m pytest tests/test_phase2_features.py -v
```

**Getting Help:**
- 📖 **Documentation**: Check `docs/` folder
- 💬 **Discussions**: [GitHub Discussions](https://github.com/flytohub/flyto2/discussions)
- 🐛 **Issues**: [Report bugs](https://github.com/flytohub/flyto2/issues)
- 📝 **Contributing Guide**: See `CONTRIBUTING.md`

---

## Windows Bot Setup (One-Click)

Super easy Telegram bot launcher for Windows users.

### Method 1: Double-Click (Easiest!)

1. **Double-click this file:**
   ```
   START_BOT.bat
   ```

2. **Follow on-screen prompts:**
   - If no Ollama → asks if you want to install
   - If no .env → interactive setup:
     - Telegram Bot Token (from @BotFather)
     - Your User ID (from @userinfobot)
     - OpenAI Key (optional, press Enter to skip)

3. **Done! Bot auto-starts**

### Method 2: PowerShell (Advanced)

```powershell
.\scripts\start_bot_windows.ps1
```

### First Time? You'll Need These

**1. Telegram Bot Token:**
1. Open Telegram
2. Search `@BotFather`
3. Send `/newbot`
4. Follow instructions to create bot
5. Copy token (e.g., `7995397831:AAEVEF...`)

**2. Your Telegram User ID:**
1. Search `@userinfobot`
2. Send `/start`
3. Copy your ID (e.g., `123456789`)

**3. OpenAI Key (Optional):**
- If you want `/gpt` command: https://platform.openai.com/api-keys
- Don't want to pay? Press Enter to skip and use free Ollama only!

### What Happens After Launch?

**Auto-completed tasks:**
```
✓ Check Python
✓ Check/start Ollama
✓ Download llama3.2 model (if needed)
✓ Install Python packages
✓ Start Bot
```

**Cost:**
- **Ollama only** (no OpenAI key): NT$0/month 🎉
- **Hybrid mode** (with OpenAI key): ~NT$30-90/month
- **vs. Full OpenAI**: NT$2,430/month (save 96%!)

**Start chatting:**
```
You: /start

Bot: 🤖 Flyto2 AI Assistant V2
     Ultra-Low-Cost Three-Tier Strategy

     Commands:
     • Just chat - I'll use Ollama
     • /gpt <q> - Force OpenAI ($)
     • /status - Quality status
     • /stats - Usage statistics
```

**Next time:** Just double-click `START_BOT.bat` - all settings saved in `.env`!

---

## Windows Monitoring Setup

Fast setup guide for running Flyto2 Level 4 monitoring on Windows.

### Prerequisites Check

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

### Setup Steps

```powershell
# 1. Clone repository
cd C:\Projects
git clone <your-repo-url> flyto2
cd flyto2

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# If execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 3. Install dependencies
pip install -r requirements.txt
```

### Configure Environment

```powershell
# Create .env file
@"
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
OPENAI_API_KEY=your_openai_key
GITHUB_TOKEN=your_github_token
"@ | Out-File -FilePath .env -Encoding UTF8
```

**Get GitHub token:**
```powershell
gh auth login
gh auth token
```

### Test & Run

```powershell
# Test a simple workflow
python -m src.cli.main workflows/_test/test_string_split.yaml

# Run manual monitoring test
python -m src.cli.main workflows/meta/monitor_regressions.yaml

# Schedule daily monitoring (Run as Administrator)
.\scripts\setup_windows_tasks.ps1
```

**Done!** System will:
- ✅ Monitor 21 modules every day at 9 AM
- ✅ Send Telegram reports if regressions detected
- ✅ Track quality metrics in `metrics/module_quality.json`

---

## Common Commands Reference

```bash
# Development
python -m src.cli.main <workflow.yaml>      # Run workflow
python scripts/validate_all_modules.py      # Validate modules
python scripts/lint_modules.py --strict     # Lint modules
python -m pytest tests/ -v                  # Run all tests

# Git
git checkout -b feature/your-feature        # New branch
git add .                                   # Stage changes
git commit -m "message"                     # Commit
git push origin feature/your-feature        # Push
```

---

## Need More Help?

### Documentation
- **Bot Architecture**: `docs/TELEGRAM_BOT_ARCHITECTURE.md`
- **Bot Setup**: `docs/TELEGRAM_BOT_SETUP.md`
- **Windows Setup**: `docs/WINDOWS_SETUP.md`
- **Module Writing**: `docs/WRITING_MODULES.md`
- **CLI Guide**: `docs/CLI.md`

### Community
- 📖 **Full docs**: `docs/README.md`
- 💬 **Discussions**: [GitHub Discussions](https://github.com/flytohub/flyto2/discussions)
- 🐛 **Report issues**: [GitHub Issues](https://github.com/flytohub/flyto2/issues)

---

**Ready to contribute?** Pick a task from [Good First Issues](https://github.com/flytohub/flyto2/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) and get started! 🚀
