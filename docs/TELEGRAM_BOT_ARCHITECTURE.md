# Telegram Bot Architecture - Flyto2 AI Assistant

## Overview

A hybrid Telegram bot that serves as your AI assistant + project manager + remote control for Flyto2.

**Key Features:**
- Default to local LLM (Ollama) for cheap daily conversations
- Switch to OpenAI on-demand for complex tasks
- Direct integration with Flyto2 workflows
- Progress tracking and quality monitoring
- Human-in-the-loop for all critical decisions

## Architecture Diagram

```
┌─────────────┐
│  Telegram   │ ← Your phone/desktop
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│     Flyto2 Telegram Bot Server      │
│  (Python + python-telegram-bot)     │
│                                     │
│  ┌──────────────────────────────┐  │
│  │   Command Router             │  │
│  │  /mode, /ask, /gpt, /status  │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │   Model Switcher             │  │
│  │  local | openai | auto       │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │   Conversation State         │  │
│  │  In-memory session tracking  │  │
│  └──────────────────────────────┘  │
└───┬────────────────────────────┬───┘
    │                            │
    ▼                            ▼
┌───────────┐              ┌────────────────┐
│  Ollama   │              │  Flyto2 Engine │
│  (Local)  │              │  CLI Workflows │
└───────────┘              └────────────────┘
    │                            │
    ▼                            ▼
┌───────────┐              ┌────────────────┐
│ OpenAI API│              │ Quality Metrics│
│ (Fallback)│              │ Deployment Logs│
└───────────┘              └────────────────┘
```

## Model Modes

### 1. Local Mode (Default)
- All questions go to Ollama
- Fast, free, unlimited
- Good for: daily chat, simple queries, progress updates

### 2. OpenAI Mode
- All questions go to OpenAI GPT-4
- High quality, costs money
- Good for: complex refactoring, architecture design, critical decisions

### 3. Auto Mode (Recommended)
- Default to Ollama
- Use `/gpt` prefix to invoke OpenAI for specific questions
- Best balance of cost and quality

## Command Design

### Model Control

```
/mode local      - Switch to local LLM only
/mode openai     - Switch to OpenAI only
/mode auto       - Default local, /gpt for OpenAI (recommended)
/mode status     - Show current model and stats
```

### Conversation

```
/ask <question>  - Ask using current model
/gpt <question>  - Force OpenAI for this question only
/chat            - Enter chat mode (continuous conversation)
```

### Flyto2 Integration

```
/status          - Show current quality metrics
/quality         - Detailed quality report for all modules
/improve <module>- Trigger AI improvement for module
/rollbacks       - Show recent rollback history
/test <module>   - Run quality tests for module
/report [today|week] - Activity summary
```

### Progress Tracking

```
/progress        - Show current work progress
/todo add <task> - Add task to tracking
/todo list       - List all tasks
/todo done <id>  - Mark task complete
```

## Usage Examples

### Example 1: Daily Chat (Local LLM)

```
You: What did we change yesterday?
Bot: [Using Ollama] Yesterday you committed:
     - Level 4 auto-merge infrastructure
     - Windows setup guide
     - 3 new meta workflows

You: Show me quality stats
Bot: Running /status...
     21 modules, all at 100% pass rate ✅
```

### Example 2: Complex Task (OpenAI)

```
You: /gpt Help me refactor deployment_manager.py to use
     dependency injection and add comprehensive docstrings

Bot: [Using OpenAI GPT-4]
     Here's a refactored version with clean architecture...
     [detailed code with explanations]
```

### Example 3: Hybrid Workflow

```
You: Should I enable auto-rollback now?
Bot: [Using Ollama] Based on your metrics:
     - All modules stable for 2 weeks
     - Zero regressions detected
     - Confidence: 70%

     This is a critical decision. Want me to
     analyze deeper with /gpt?

You: /gpt yes analyze risks
Bot: [Using OpenAI] Deep analysis of auto-rollback risks...
     [detailed risk assessment]
```

### Example 4: Workflow Integration

```
You: /improve string.split
Bot: Triggering autonomous improvement workflow...
     - Analyzing string.split quality (98%)
     - Generating improvement proposal
     - Running quality gate tests
     - Result: PASS (100%)
     - Created PR #456

     Ready to auto-merge? Reply 'yes' or 'review'
```

## State Management

### Conversation State (In-Memory)

```python
{
  "user_id": 123456789,
  "current_model": "auto",  # local | openai | auto
  "conversation_history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "active_workflow": None,
  "pending_confirmations": [],
  "session_stats": {
    "local_queries": 45,
    "openai_queries": 3,
    "cost_saved": "$2.40"
  }
}
```

### Persistent Storage (Optional, Future)

- SQLite for conversation history
- Progress tracking with tasks
- Cost tracking and budgets

## Integration with Flyto2

### How Bot Calls Workflows

```python
# Bot receives: /status
# Bot executes:
result = subprocess.run([
    'python', '-m', 'src.cli.main',
    'workflows/meta/validate_modules.yaml'
], capture_output=True)

# Bot parses result and formats for Telegram
summary = parse_workflow_output(result.stdout)
send_message(chat_id, summary)
```

### Workflow Results → Telegram

```python
# Parse JSON output from workflow
output = json.loads(result.stdout)

# Format for human reading
message = f"""
✅ Quality Status

Modules: {output['total_modules']}
Above 98%: {output['modules_above_98']}
Warnings: {output['modules_95_98']}
"""

send_markdown(chat_id, message)
```

## Cost Management

### Track Costs Per Session

```python
# Approximate costs
OLLAMA_COST_PER_TOKEN = 0.0  # Free
OPENAI_GPT4_INPUT = 0.00003  # $0.03 per 1K tokens
OPENAI_GPT4_OUTPUT = 0.00006  # $0.06 per 1K tokens

# Show savings
You: /mode status
Bot: Current mode: auto
     Today:
     - Ollama queries: 23 (free)
     - OpenAI queries: 2 ($0.18)
     - Estimated savings: $3.45
```

### Budget Alerts

```python
# Optional: Set daily budget
/budget set 5.0   # $5/day max
Bot: Budget set to $5/day. I'll warn you at $4.
```

## Security

### Token Management

```python
# .env file
TELEGRAM_BOT_TOKEN=7995397831:AAEVEF1TMAqrgvkWWgGzWGhHarKiTBEMg-Y
TELEGRAM_ALLOWED_USERS=123456789,987654321  # Your chat IDs only
OLLAMA_URL=http://localhost:11434
OPENAI_API_KEY=sk-...
```

### User Validation

```python
def is_authorized(update):
    user_id = update.effective_user.id
    allowed = os.getenv('TELEGRAM_ALLOWED_USERS').split(',')
    return str(user_id) in allowed
```

## Deployment Options

### Option 1: Same Machine as Flyto2

```
Windows PC:
├── Ollama (port 11434)
├── Flyto2 project
└── Bot script (always running)
```

**Start bot:**
```powershell
.\venv\Scripts\Activate.ps1
python scripts/telegram_bot.py
```

### Option 2: Cloud Deployment

```
Cloud VM:
├── Docker container (Ollama + Bot)
├── Flyto2 project
└── Persistent storage for metrics
```

### Option 3: Split Architecture

```
Local PC:          Cloud:
├── Ollama         ├── Bot Server
└── Development    └── Flyto2 Production
```

## Error Handling

### Graceful Degradation

```python
# If Ollama is down
if not ollama_available():
    send_message("Ollama unavailable, using OpenAI as fallback")
    response = openai_chat(prompt)

# If workflow fails
try:
    result = run_workflow(workflow_path)
except Exception as e:
    send_message(f"Workflow failed: {e}")
    send_message("Want me to help debug? Reply 'yes'")
```

## Future Enhancements

### Voice Notes Support
- Send voice message → Speech-to-Text → LLM → Text response

### Image Analysis
- Send screenshot → Vision model → Analysis

### Scheduled Summaries
- Daily digest at 9 AM
- Weekly progress report
- Monthly quality trends

### Multi-User Support
- Team chat mode
- Shared workflows
- Role-based permissions

## Implementation Priority

### Phase 1: MVP (Week 1)
- [x] Basic bot setup
- [ ] Model switching (/mode local/openai/auto)
- [ ] Simple /ask and /gpt commands
- [ ] /status integration

### Phase 2: Workflow Integration (Week 2)
- [ ] /quality, /improve, /rollbacks
- [ ] Workflow result formatting
- [ ] Error handling

### Phase 3: Progress Tracking (Week 3)
- [ ] /progress, /todo commands
- [ ] Session state persistence
- [ ] Cost tracking

### Phase 4: Advanced Features (Week 4+)
- [ ] Conversation history
- [ ] Budget management
- [ ] Voice/image support

## Quick Start

```powershell
# Install dependencies
pip install python-telegram-bot ollama openai

# Start Ollama
ollama serve

# Pull a model
ollama pull llama3.2

# Run bot
python scripts/telegram_bot.py
```

Then in Telegram:
```
/start
/mode auto
/ask Show me current quality status
/gpt Help me design a rollback strategy
```

---

This architecture gives you:
- 💰 95% cost savings (local LLM for most tasks)
- 🎯 High quality when needed (OpenAI on-demand)
- 🤖 Full Flyto2 control from phone
- 📊 Progress tracking built-in
- 🔒 Secure and private
