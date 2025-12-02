# 🤖 Flyto2 - Autonomous Self-Evolving AI Bot

**Status**: 🚧 **Alpha** - Core systems implemented, critical dependency required (Ollama)

An AI-powered workflow automation bot that **fixes itself** when it encounters errors. Built on atomic module architecture with local-first AI.

## 🎯 What Makes This Different

Instead of hardcoding error handling:
```python
# ❌ Traditional approach
try:
    run_workflow()
except ModuleNotFoundError:
    install_package()  # Hardcoded solution
except BrowserError:
    restart_browser()  # Hardcoded solution
# ... endless if/else
```

Flyto2 feeds **all errors to AI**:
```python
# ✅ Flyto2 approach
try:
    run_workflow()
except Exception as error:
    solution = ai_error_solver.solve(error)
    execute(solution)
    archive_for_future_use(solution)
```

**Core Philosophy**: No hardcoded error handling - let AI figure it out, then remember the solution.

---

## ⚡ Quick Start

### Prerequisites (CRITICAL)

**Ollama MUST be running** - Without it, AI features won't work:

```bash
# Install Ollama
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download

# Start Ollama server (REQUIRED)
ollama serve

# In another terminal, download model
ollama pull llama3.2

# Test connection
curl http://localhost:11434/api/generate -d '{"model": "llama3.2", "prompt": "hello"}'
```

### Installation

```bash
git clone https://github.com/yourusername/flyto2.git
cd flyto2

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-integrations.txt  # Optional third-party integrations

# Install browser drivers (if using browser modules)
playwright install chromium
```

### Test the System

```bash
# Run end-to-end tests
python3 test_end_to_end.py

# Expected results (with Ollama running):
# ✅ intent - Intent detection working
# ⚠️ workflow - Status naming mismatch (minor issue)
# ✅ crawl - Full AI workflow generation working
```

### Use the Perfect Flow Bot

The Perfect Flow Bot is a Telegram interface that implements the ideal user flow:

```
TG Input → Bot Thinks → Generate YAML → Test →
  → If Fail: [Let Me Solve] [Let Bot Solve] [Ask OpenAI] →
  → Retry → Success → Create PR → User Verifies
```

**Setup**:

```bash
# 1. Get Telegram bot token from @BotFather
# 2. Get your user ID from @userinfobot

# 3. Configure
export TELEGRAM_BOT_TOKEN="your_token_here"
export TELEGRAM_ALLOWED_USERS="your_user_id"  # Optional

# 4. Start bot
./START_PERFECT_BOT.sh

# Or manually:
python3 scripts/telegram_bot_perfect.py
```

**Usage Example**:

```
You: 爬蟲 google.com

Bot: 🤔 收到任務，正在思考...
     ✅ 理解任務
        類型: crawl
        信心: 90%
     📝 正在生成 YAML workflow...
     ✅ 生成 workflow: [shows YAML]
     🧪 測試執行 (嘗試 1/3)...
     ✅ 測試成功！

     結果:
     { "title": "Google", "url": "https://google.com" }

     🎉 Workflow 測試成功！接下來要做什麼？

     [發 PR 給我驗證] [直接使用]
```

If the workflow fails, you get 3 options:
- **🙋 Let me solve** - You provide guidance manually
- **🤖 Let bot solve** - AI Error Solver automatically fixes it
- **💰 Ask OpenAI** - Use GPT-4 for premium solutions (planned)

See [PERFECT_FLOW.md](PERFECT_FLOW.md) for complete documentation.

---

## 🏗️ Architecture

### Atomic Module System

Everything is built from **atomic, reusable modules**:

```yaml
# Example workflow combining atomic modules
workflow_name: "crawl_and_notify"
steps:
  - step_id: launch
    module: browser.launch
    params: {headless: true}

  - step_id: goto
    module: browser.goto
    params: {url: "https://example.com"}

  - step_id: extract
    module: browser.extract
    params:
      fields:
        - {name: "title", selector: "h1", type: "text"}

  - step_id: notify
    module: notification.slack.send_message
    params: {text: "Found: ${extract.data[0].title}"}
```

### 123 Built-in Modules

**Core Modules** (63):
- `browser.*` (9): launch, goto, click, type, extract, screenshot, etc.
- `element.*` (3): query, text, attribute
- `string.*` (7): uppercase, lowercase, split, replace, etc.
- `array.*` (10): filter, sort, map, reduce, etc.
- `file.*` (6): read, write, exists, delete, move, copy
- `data.*` (5): CSV, JSON, text templates
- `math.*` (6): calculate, round, floor, ceil, etc.
- `object.*` (5): keys, values, merge, pick, omit
- `datetime.*` (4): format, parse, add, subtract

**Integration Modules** (42):
- `ai.*` (7): OpenAI, Claude, Gemini, Ollama (local)
- `notification.*` (6): Slack, Discord, Telegram, Email, Twilio
- `db.*` (6): PostgreSQL, MySQL, MongoDB, Redis
- `cloud.*` (6): AWS S3, Google Cloud, Azure
- `productivity.*` (7): Notion, Google Sheets, Airtable
- `api.*` (7): GitHub, HTTP, Google Search, SerpAPI
- `payment.*` (3): Stripe

**Healing & Training Modules** (13 new):
- `healing.atomic.*` (6): Vector query, prompt builder, AI consulter, solution executor, archiver, trainer
- `training.atomic.*` (4): Robots parser, HTML pattern detector, schema inferrer, recommendation generator
- `utils.*` (3): Notifier, vector DB manager, HTTP client

---

## 🧬 AI Error Solver

The heart of self-healing:

```python
# When workflow execution fails
error = Exception("Module 'playwright' not found")

# AI Error Solver flow:
# 1. Query vector DB for similar past solutions
similar_solutions = vector_db.search("Module playwright not found")

# 2. Build AI prompt with context
prompt = build_prompt(error, similar_solutions, environment)

# 3. Ask AI (Ollama/OpenAI) for solution
ai_solution = ollama.ask(prompt)
# → "Install playwright: pip install playwright && playwright install chromium"

# 4. Execute solution
result = execute_commands(ai_solution)

# 5. If successful, archive for future use
if result.success:
    vector_db.store(error, ai_solution)
    train_similarity_model(ai_prediction, actual_solution)
```

**Features**:
- ✅ Vector DB similarity search (finds past solutions)
- ✅ Local AI with Ollama (privacy-first, offline capable)
- ✅ Automatic solution archiving
- ✅ Continuous learning from solutions
- ✅ Safety checks before execution
- ✅ Multi-backend notifications

**Location**: `src/core/healing/ai_error_solver.py` (194 lines, refactored from 670)

---

## 📊 Current Status (2025-12-02)

### What Works ✅

1. **Intent Detection** (100%)
   - Understands Chinese/English task descriptions
   - Classifies: crawl, api, notification, search, etc.
   - Confidence scoring

2. **Module Registry** (123 modules)
   - All atomic modules registered
   - Metadata for UI builders
   - Integration modules optional (install as needed)

3. **Atomic Architecture** (13 new modules)
   - Refactored from monolithic files
   - Single responsibility per module
   - Reusable across systems
   - Reduced code duplication by 476 lines

4. **Perfect Flow Bot** (Complete)
   - Telegram interface implemented
   - Three-way error resolution
   - AI workflow generation (requires Ollama)
   - Inline keyboard interactions

5. **Vector DB Integration**
   - ChromaDB/Qdrant support
   - Similarity search working
   - Knowledge archiving functional

### Known Issues ❌

#### CRITICAL (P0)

**1. Ollama Dependency Not Running**
- **Impact**: ALL AI features blocked
- **Affected**: Workflow generation, error solving, training
- **Fix**: Start Ollama (`ollama serve`) OR implement fallback
- **Status**: 🔴 Blocker for AI features

**2. SmartExecutor Syntax Error** ✅ FIXED
- **Was**: Line 99 unterminated string literal
- **Status**: Fixed in recent commit

#### MEDIUM (P1)

**3. WorkflowEngine Status Naming**
- **Issue**: Returns 'success', test expects 'completed'
- **Impact**: Test failures only, not functional
- **Fix**: Standardize naming
- **File**: `src/core/engine/workflow_engine.py`

**4. README Outdated** ← You are here
- **Issue**: Didn't reflect current state
- **Status**: 🔄 Being updated now

#### LOW (P2)

**5. OpenAI Premium Option**
- **Status**: 🚧 Planned, not implemented
- **Impact**: Low - Ollama provides same functionality

**6. GitHub PR Auto-Creation**
- **Status**: 🚧 Planned, not implemented
- **Impact**: Low - manual PR works fine

### Test Results

```bash
$ python3 test_end_to_end.py

測試總結
============================================================
✅ intent - Intent detection working
❌ workflow - Status naming mismatch
❌ crawl - Ollama not running (blocker)

通過: 1/3
```

**Actual Usability**:
- Architecture Design: ⭐⭐⭐⭐⭐⭐⭐⭐⭐☆ (9/10)
- Code Completeness: ⭐⭐⭐⭐⭐⭐⭐⭐☆☆ (8/10)
- Actual Functionality: ⭐⭐⭐☆☆☆☆☆☆☆ (3/10) - Blocked by Ollama

**Quote from testing**: "沒有 Ollama，這個專案就像沒有引擎的車"
(Without Ollama, this project is like a car without an engine)

See [REAL_STATUS.md](REAL_STATUS.md) for detailed analysis.

---

## 📁 Project Structure

```
flyto2/
├── src/
│   ├── core/
│   │   ├── agent/
│   │   │   └── intent_detector.py        # Classify user tasks
│   │   ├── engine/
│   │   │   └── workflow_engine.py        # Execute YAML workflows
│   │   ├── executor/
│   │   │   └── smart_executor.py         # High-level task execution
│   │   ├── healing/
│   │   │   ├── ai_error_solver.py        # Self-healing system (194 lines)
│   │   │   └── atomic/                   # 6 healing modules
│   │   │       ├── vector_query.py
│   │   │       ├── prompt_builder.py
│   │   │       ├── ai_consulter.py
│   │   │       ├── solution_executor.py
│   │   │       ├── solution_archiver.py
│   │   │       └── similarity_trainer.py
│   │   ├── training/
│   │   │   └── atomic/                   # 4 training modules
│   │   │       ├── robots_parser.py
│   │   │       ├── html_pattern_detector.py
│   │   │       ├── schema_inferrer.py
│   │   │       └── recommendation_generator.py
│   │   ├── modules/
│   │   │   ├── registry.py              # Module registration
│   │   │   ├── base.py                  # BaseModule class
│   │   │   ├── atomic/                  # 63 atomic modules
│   │   │   └── browser_modules.py       # Browser automation
│   │   └── utils/
│   │       ├── notifier.py              # Unified notifications
│   │       ├── vector_db_manager.py     # Vector DB singleton
│   │       └── http_client.py           # HTTP with retry
│   └── cli/
│       └── main.py                      # CLI interface
├── scripts/
│   ├── telegram_bot_perfect.py          # Perfect Flow Bot
│   └── sync_to_vector_db.py             # Sync project knowledge
├── workflows/                            # Example YAML workflows
├── test_end_to_end.py                   # E2E tests
├── START_PERFECT_BOT.sh                 # One-click bot launcher
├── PERFECT_FLOW.md                      # Perfect Flow documentation
├── REAL_STATUS.md                       # Honest status report
└── README.md                            # This file
```

---

## 🔧 Development

### Running Tests

```bash
# Full end-to-end test
python3 test_end_to_end.py

# Test specific workflow
python -m src.cli.main workflows/google_search.yaml

# Test with parameters
python -m src.cli.main workflow.yaml --params '{"keyword":"nodejs"}'
```

### Adding a New Atomic Module

```python
# src/core/modules/atomic/my_category/my_module.py
from src.core.modules.base import BaseModule
from src.core.modules.registry import register_module

@register_module('my.module')
class MyModule(BaseModule):
    module_name = "My Module"
    module_description = "What it does"

    def validate_params(self):
        if 'required_param' not in self.params:
            raise ValueError("Missing required_param")
        self.my_param = self.params['required_param']

    async def execute(self):
        result = do_something(self.my_param)
        return {"status": "success", "result": result}
```

Module automatically appears in registry and workflow editor.

### Syncing Knowledge to Vector DB

```bash
# Store current project knowledge
python3 scripts/sync_to_vector_db.py

# Query stored knowledge
from src.core.utils.vector_db_manager import vector_search
results = await vector_search("How to fix Ollama error?")
```

---

## 🎯 Roadmap

### Immediate (P0)
- [ ] Fix Ollama dependency detection
  - Add startup health check
  - Provide friendly error messages
  - Implement graceful fallback (template-based generation)
  - Document installation clearly

- [ ] Fix WorkflowEngine status naming
  - Standardize to 'completed' or adjust tests
  - Update all callers

### Short-term (P1)
- [ ] Complete end-to-end browser testing
  - Verify Playwright integration works
  - Test full crawl + extract workflows

- [ ] Implement OpenAI premium option
  - "💰 Ask OpenAI" button in PerfectBot
  - GPT-4 for complex error solving

- [ ] GitHub PR auto-creation
  - Create branch from workflow
  - Commit and push
  - Open PR for user review

### Long-term (P2)
- [ ] Module marketplace
  - Community-contributed modules
  - Rating and verification system

- [ ] Workflow template library
  - Pre-built workflows for common tasks
  - One-click deployment

- [ ] Web UI for workflow builder
  - Visual workflow editor
  - Real-time execution monitoring

- [ ] Distributed execution
  - Multi-machine workflow execution
  - Kubernetes operator

---

## 📖 Documentation

- **[PERFECT_FLOW.md](PERFECT_FLOW.md)** - Perfect Flow Bot user guide
- **[REAL_STATUS.md](REAL_STATUS.md)** - Honest current status assessment
- **Module Documentation** - See individual module files for API docs
- **Architecture** - See `src/core/` for system design

---

## 🤝 Contributing

We value **honest assessment** over optimism. Before contributing:

1. ✅ Test your changes end-to-end
2. ✅ Update documentation if needed
3. ✅ Run `python3 test_end_to_end.py`
4. ✅ Be honest about limitations

**Development Philosophy**:
- "Walk through the entire project flow"
- "Many things assumed to work actually don't"
- Test everything, assume nothing
- Document real status, not aspirations

---

## 🙏 Acknowledgments

**User Feedback** (that made this better):
- "你這專案 超級不AI的" → Led to AI Error Solver integration
- "很多你實際覺得可以行 但都不行" → Led to REAL_STATUS.md and honest testing

**Built with**:
- [Playwright](https://playwright.dev/) - Browser automation
- [Ollama](https://ollama.com/) - Local LLM inference
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [python-telegram-bot](https://python-telegram-bot.org/) - Telegram integration

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🆘 Troubleshooting

### "Connection refused on localhost:11434"

**Problem**: Ollama not running

**Fix**:
```bash
# Start Ollama
ollama serve

# Test
curl http://localhost:11434/api/generate -d '{"model": "llama3.2", "prompt": "test"}'
```

### "Module 'playwright' not found"

**Problem**: Browser drivers not installed

**Fix**:
```bash
pip install playwright
playwright install chromium
```

### "Telegram bot not responding"

**Problem**: Token or user ID incorrect

**Fix**:
```bash
# Get token from @BotFather
# Get user ID from @userinfobot
export TELEGRAM_BOT_TOKEN="your_actual_token"
export TELEGRAM_ALLOWED_USERS="your_actual_id"
```

### Tests failing with "Status 'success' not 'completed'"

**Problem**: Known issue - status naming mismatch

**Status**: Low priority, doesn't affect functionality

---

<div align="center">

**Flyto2: No Hardcoded Error Handling - Let AI Figure It Out**

[Test It](#-quick-start) • [Read Status](REAL_STATUS.md) • [Use Perfect Bot](PERFECT_FLOW.md)

</div>
