# 🚀 Quick Start - One-Click Setup

**最快速的啟動方式 - 一鍵安裝所有依賴**

---

## 📦 What Gets Installed Automatically

The auto setup script will install:

✅ **Python Dependencies**
- python-telegram-bot
- playwright (browser automation)
- openai (AI capabilities)
- qdrant-client (vector database)
- All other required packages

✅ **Playwright Browsers**
- Chromium (for web automation)

✅ **GitHub CLI** (for PR creation)
- macOS: via Homebrew
- Windows: Instructions provided
- Linux: via package manager

✅ **Environment Configuration**
- Creates `.env` template if not exists
- Validates all required API keys

---

## 🖥️ Platform-Specific Instructions

### macOS / Linux

**One Command:**
```bash
./START_BOT_AUTO.sh
```

**First Time:**
1. The script will check and install everything
2. Edit `.env` with your API keys (see below)
3. Run `./START_BOT_AUTO.sh` again
4. Bot starts automatically! 🎉

### Windows

**One Command:**
```cmd
START_BOT_AUTO.bat
```

**First Time:**
1. Double-click `START_BOT_AUTO.bat`
2. It will check and install everything
3. Edit `.env` with your API keys (see below)
4. Run `START_BOT_AUTO.bat` again
5. Bot starts automatically! 🎉

---

## 🔑 Required API Keys

Edit `.env` file with these values:

```env
# 1. Telegram Bot Token (Required)
# Get from: https://t.me/BotFather
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# 2. OpenAI API Key (Required for embeddings & AI)
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 3. Qdrant Cloud (Required for knowledge base)
# Get from: https://cloud.qdrant.io/
QDRANT_URL=https://xxxxx.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 4. GitHub Token (Optional, for PR creation)
# Get from: https://github.com/settings/tokens
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 5. Ollama (Optional, for local LLM)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
```

---

## 📋 What Happens on First Run

```
1️⃣  Checking Python...           ✓ Python 3.10.6
2️⃣  Checking Homebrew...         ✓ Found
3️⃣  Checking GitHub CLI...       ⏳ Installing...
4️⃣  Installing Dependencies...   ⏳ pip install...
5️⃣  Installing Browsers...       ⏳ playwright install...
6️⃣  Checking Environment...      ⚠️  Edit .env
7️⃣  Testing System...            ✓ 120 modules loaded

📊 Setup Summary
✅ Ready: 6/7

⚠️  Environment configuration needed

Next steps:
1. Edit .env file with your API keys
2. Run this script again
```

---

## ✅ After Setup Completes

```
🎉 All dependencies installed!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 Starting Bot...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 Flyto2 Evolution Bot
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Bot is running... Press Ctrl+C to stop

Commands available:
  /start     - Start the bot
  /help      - Show help message
  /test      - Run test workflow
  /debug     - Show debug info
  /evolve    - Trigger evolution
  /modules   - List atomic modules
```

Bot is now running and ready to use! 🚀

---

## 🎯 What the Bot Can Do

### ✅ Fully Working Now:
1. **Execute Workflows** - Run any YAML workflow
2. **120+ Atomic Modules** - Browser, API, Data, File, etc.
3. **Knowledge Base** - Query English documentation
4. **Generate Code** - Create new modules automatically
5. **Create PRs** - Submit to GitHub for review

### 💬 Example Commands:

**Via Telegram:**
```
User: 幫我爬蟲 google.com
Bot: ✅ [Executes workflow, returns results]

User: 幫我加一個壓縮圖片的模組
Bot: ✅ [Generates code, creates PR]

User: 檢查 example.com 是否有廣告
Bot: ✅ [Runs browser workflow, returns answer]
```

**Via CLI:**
```bash
# Execute workflow
python3 -m src.cli.main workflows/my_workflow.yaml

# Test system
python3 test_end_to_end.py

# Test AI responses
python3 test_difficult_questions.py

# Test PR creation
python3 test_pr_creation.py
```

---

## 🐛 Troubleshooting

### Script Won't Run

**macOS/Linux:**
```bash
chmod +x START_BOT_AUTO.sh
./START_BOT_AUTO.sh
```

**Windows:**
- Right-click → "Run as Administrator"
- Or open CMD as admin: `START_BOT_AUTO.bat`

### Python Not Found

**Install Python 3.8+:**
- macOS: `brew install python3`
- Windows: https://www.python.org/downloads/
- Linux: `sudo apt install python3`

### GitHub CLI Not Installing

**Manual Install:**

**macOS:**
```bash
brew install gh
gh auth login
```

**Windows:**
```cmd
winget install --id GitHub.cli
```

Or download from: https://cli.github.com/

**Linux:**
```bash
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

### Playwright Browsers Won't Install

**Manual Install:**
```bash
playwright install chromium
```

---

## 📚 Additional Resources

- **Full Test Results**: `TEST_RESULTS_SUMMARY.md`
- **Implementation Guide**: `ENGLISH_KNOWLEDGE_BASE.md`
- **Architecture**: `IMPLEMENTATION_GUIDE_V4.md`

---

## 🎉 Success Checklist

- [x] Script runs without errors
- [x] All dependencies installed
- [x] `.env` configured with API keys
- [x] GitHub CLI authenticated (optional)
- [x] Bot starts successfully
- [x] Can execute workflows
- [x] Knowledge base accessible

**Ready to evolve!** 🧬

---

## 💡 Pro Tips

1. **Keep API keys secure** - Never commit `.env` to git
2. **Test first** - Run `test_end_to_end.py` to verify everything works
3. **GitHub auth** - Run `gh auth login` to enable PR creation
4. **Monitor logs** - Check console output for errors
5. **Regular updates** - Pull latest changes from git

---

**Last Updated**: 2025-12-02
**Version**: V4.0
**Status**: ✅ Production Ready
