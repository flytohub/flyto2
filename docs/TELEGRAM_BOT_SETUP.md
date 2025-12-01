# Telegram Bot Setup Guide

Quick setup guide for the Flyto2 AI Assistant bot.

## Prerequisites

### 1. Install Ollama (Local LLM)

**Windows:**
```powershell
# Download from https://ollama.com/download
# Or use winget
winget install Ollama.Ollama

# Start Ollama
ollama serve

# Pull a model (in another terminal)
ollama pull llama3.2
```

**Mac/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
ollama pull llama3.2
```

### 2. Install Python Dependencies

```powershell
cd C:\Projects\flyto2
.\venv\Scripts\Activate.ps1

pip install python-telegram-bot requests openai
```

### 3. Get Your Telegram User ID

1. Open Telegram
2. Search for `@userinfobot`
3. Send `/start`
4. Copy your ID (e.g., `123456789`)

## Configuration

### Update .env File

```env
# Telegram Bot (you already have this)
TELEGRAM_BOT_TOKEN=7995397831:AAEVEF1TMAqrgvkWWgGzWGhHarKiTBEMg-Y
TELEGRAM_CHAT_ID=your_chat_id_here

# Add your user ID for authorization
TELEGRAM_ALLOWED_USERS=your_user_id_here

# Ollama (local LLM)
OLLAMA_URL=http://localhost:11434

# OpenAI (optional, for /gpt commands)
OPENAI_API_KEY=sk-...

# GitHub
GITHUB_TOKEN=your_github_token
```

**Example:**
```env
TELEGRAM_BOT_TOKEN=7995397831:AAEVEF1TMAqrgvkWWgGzWGhHarKiTBEMg-Y
TELEGRAM_CHAT_ID=123456789
TELEGRAM_ALLOWED_USERS=123456789
OLLAMA_URL=http://localhost:11434
OPENAI_API_KEY=sk-proj-abc123...
```

## Running the Bot

### Start Ollama (if not running)

```powershell
# In one terminal
ollama serve
```

### Start the Bot

```powershell
# In another terminal
cd C:\Projects\flyto2
.\venv\Scripts\Activate.ps1

python scripts/telegram_bot.py
```

You should see:
```
Starting Flyto2 Telegram Bot...
✅ Bot started successfully!
Allowed users: ['123456789']
Ollama URL: http://localhost:11434
OpenAI configured: True

Bot is running... Press Ctrl+C to stop.
```

## First Conversation

### 1. Start Chat

Open Telegram, search for `@Flyto2_Bot`, send:
```
/start
```

You'll see:
```
🤖 Flyto2 AI Assistant

Hi! I'm your hybrid AI assistant.

Current mode: auto

Available commands:
...
```

### 2. Test Local LLM

```
You: What is Flyto2?

Bot: [Ollama (Local)]
Flyto2 is a workflow automation engine with Level 4
self-evolving capabilities. It can automatically improve
module quality through AI-driven testing and deployment.
```

### 3. Test OpenAI

```
You: /gpt Help me refactor the deployment_manager.py
     with dependency injection and clean architecture

Bot: [OpenAI GPT-4]
Here's a refactored version using dependency injection...
[detailed code]
```

### 4. Test Flyto2 Integration

```
You: /status

Bot: 📊 Flyto2 Quality Status

Modules: 21
• Above 98%: 21 ✅
• 95-98%: 0 ⚠️
• Below 95%: 0 🚨

Auto-merge approved: 21

Last updated: 2025-12-01T00:43:00Z
```

## Command Reference

### Model Switching

```
/mode local      - Always use Ollama (free)
/mode openai     - Always use OpenAI (costs money)
/mode auto       - Hybrid: Ollama by default, /gpt for complex
/mode status     - Show current mode and stats
```

### Asking Questions

```
/ask <question>  - Ask using current model
/gpt <question>  - Force OpenAI for this specific question
<message>        - Just chat normally (uses current mode)
```

### Flyto2 Workflows

```
/status          - Quick quality overview
/quality         - Detailed quality report with all modules
```

## Usage Patterns

### Pattern 1: Daily Check-ins (Ollama)

```
You: What changed in the last 24h?
Bot: [Ollama] Summary of recent commits...

You: Show quality status
Bot: Running /status...
     21 modules, all 100% ✅
```

**Cost: $0 (free)**

### Pattern 2: Complex Decisions (OpenAI)

```
You: /gpt Should I enable auto-rollback now?
     Analyze all risks and give recommendation.

Bot: [OpenAI GPT-4]
     Based on your current state:
     - 2 weeks of stability
     - Zero regressions
     - All modules at 100%

     Recommendation: YES, enable auto-rollback
     Risks: [detailed analysis]
     Mitigation: [specific steps]
```

**Cost: ~$0.10-0.30**

### Pattern 3: Hybrid Workflow

```
You: /mode auto

You: What's the current pass rate?
Bot: [Ollama] All 21 modules at 100%

You: Should I refactor deployment_manager?
Bot: [Ollama] Basic suggestion...
     Confidence: 60%
     Want deeper analysis? Try /gpt

You: /gpt yes, analyze refactoring options
Bot: [OpenAI] Comprehensive analysis...
```

**Cost: Mostly free, ~$0.20 for OpenAI part**

## Running as Background Service

### Option 1: Keep Terminal Open

```powershell
# Simple way - just keep the terminal running
python scripts/telegram_bot.py
```

### Option 2: Windows Service (Advanced)

```powershell
# Install NSSM
winget install NSSM

# Create service
nssm install Flyto2Bot "C:\Projects\flyto2\venv\Scripts\python.exe" `
  "C:\Projects\flyto2\scripts\telegram_bot.py"

nssm set Flyto2Bot AppDirectory "C:\Projects\flyto2"

# Start service
nssm start Flyto2Bot

# Check status
nssm status Flyto2Bot
```

### Option 3: PowerShell Background Job

Create `scripts/start_bot.ps1`:
```powershell
cd C:\Projects\flyto2
.\venv\Scripts\Activate.ps1
python scripts/telegram_bot.py
```

Then:
```powershell
Start-Process powershell -ArgumentList "-File scripts/start_bot.ps1" -WindowStyle Hidden
```

## Troubleshooting

### Ollama Not Responding

```powershell
# Check if Ollama is running
curl http://localhost:11434

# If not, start it
ollama serve

# Check if model is pulled
ollama list

# Pull model if missing
ollama pull llama3.2
```

### Bot Not Responding

1. Check bot is running: Look for "Bot is running..." message
2. Check your user ID is in TELEGRAM_ALLOWED_USERS
3. Check .env file exists and is loaded
4. Check terminal for error messages

### "Unauthorized access" Message

Your user ID is not in TELEGRAM_ALLOWED_USERS:

```env
# Add your ID (get from @userinfobot)
TELEGRAM_ALLOWED_USERS=123456789
```

### OpenAI Not Working

```env
# Make sure key is set
OPENAI_API_KEY=sk-proj-...

# Test manually
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```

## Cost Tracking

The bot tracks your usage:

```
You: /mode status

Bot: Current Mode: auto

Today's Stats:
• Ollama queries: 45 (free)
• OpenAI queries: 3
• Estimated savings: $6.75
```

**Approximate costs:**
- Ollama (local): $0
- OpenAI GPT-4: ~$0.10-0.30 per complex question

## Next Steps

1. ✅ Bot running and responding
2. ⏳ Test `/status` and `/quality` commands
3. ⏳ Try `/mode` switching
4. ⏳ Use `/gpt` for a complex task
5. ⏳ Set up as background service
6. ⏳ Add more Flyto2 workflow integrations

## Advanced: Add More Commands

Edit `scripts/telegram_bot.py` to add:

```python
async def improve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /improve <module>"""
    module_id = context.args[0]

    # Run improvement workflow
    result = subprocess.run([
        'python', '-m', 'src.cli.main',
        'workflows/meta/continuous_improvement_agent.yaml',
        '--params', f'module_id={module_id}'
    ], capture_output=True)

    # Send result
    await update.message.reply_text(f"Improvement triggered for {module_id}")

# Register handler
app.add_handler(CommandHandler("improve", improve_command))
```

Then use:
```
/improve string.split
```

---

**You're all set!** Your AI assistant is running and ready to help with Flyto2. 🚀
