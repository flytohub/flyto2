# Flyto2 Integrated System Guide

**Philosophy**: Atomic modules with zero coupling, but united execution for continuous improvement

## 🎯 System Architecture

### The Big Picture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Telegram Bot (User Interface)                 │
│  /memory /practice /competition /auto /stats /status            │
└───────────────────┬─────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼────────┐    ┌────────▼─────────┐
│  Three-Tier AI │    │  Vector Database │
│  Ollama → You  │    │   Long-Term      │
│    → OpenAI    │    │     Memory       │
└───────┬────────┘    └────────┬─────────┘
        │                      │
        │    ┌─────────────────┴──────────────────┐
        │    │                                    │
┌───────▼────▼──────┐  ┌──────────────┐  ┌───────▼─────┐
│  Atomic Modules   │  │  Auto-Sync   │  │   Quality   │
│  149 independent  │  │  Git Hook    │  │   Filter    │
│  Zero coupling    │  │  File Watch  │  │  Pollution  │
└───────────────────┘  └──────────────┘  └─────────────┘
```

## 🔗 How Everything Connects

### 1. Atomic Modules (Zero Coupling)
**Location**: `src/core/modules/atomic/`

```python
# Each module is completely independent
from src.core.modules.atomic.browser import launch, goto, click
from src.core.modules.atomic.vector import search, store

# Modules don't know about each other
# Can be combined in ANY order in workflows
```

**Principle**: Write once, use everywhere

### 2. Vector Database (Persistent Memory)
**Location**: `src/core/modules/atomic/vector/`

```python
# Stores ALL experiences
- Daily practice results → knowledge base
- Speed race statistics → knowledge base
- Errors encountered → knowledge base
- Successful patterns → knowledge base
- Module improvements → knowledge base
```

**Integration Points**:
- Auto-archiving after every practice/race/error
- Quality filtering prevents pollution
- Auto-sync keeps it updated
- RAG provides context to AI

### 3. Telegram Bot (Control Center)
**Location**: `scripts/telegram_bot_v2.py`

```
User: /practice example.com
  ↓
Bot: Runs daily practice workflow
  ↓
Practice Engine: Uses atomic modules
  ↓
ExperienceArchiver: Stores result to vector DB
  ↓
QualityFilter: Filters low-quality content
  ↓
Bot: Reports back to user
  ↓
Vector DB: Now has new knowledge
```

### 4. Auto-Sync System (Continuous Updates)
**Location**: `scripts/auto_sync_knowledge.py`

```
Git Commit → Git Hook → Auto-Sync
  ↓
Detect changed files
  ↓
Filter quality (exclude cache, logs)
  ↓
Archive to vector database
  ↓
AI now knows about changes
```

**Modes**:
- Git Hook: Sync on every commit
- File Watcher: Real-time monitoring
- Scheduler: Daily/hourly sync

### 5. Quality Filter (Clean Knowledge)
**Location**: `src/core/modules/atomic/vector/quality_filter.py`

```
Content → QualityFilter → Decision
  ↓
- Empty? → Filter
- Debug print? → Filter
- Cache file? → Filter
- Technical content? → Pass (score 0.8)
- Has solution? → Pass (score 0.9)
  ↓
Only valuable knowledge stored
```

## 🚀 Complete Workflow Example

### Scenario: User wants AI to learn from practice

```
1. User: /practice github.com/trending

2. Telegram Bot:
   - Receives command
   - Triggers DailyPracticeEngine

3. Practice Engine:
   - Uses atomic modules (browser.*, analysis.*)
   - Analyzes website structure
   - Extracts data
   - Zero coupling - modules don't know each other

4. Experience Archiver:
   - Receives practice result
   - Passes through QualityFilter
   - Stores to vector database

5. Quality Filter:
   - Checks content length ✓
   - Checks for technical keywords ✓
   - Calculates importance score: 0.85 ✓
   - Decision: PASS

6. Vector Database:
   - Generates embedding (local/Ollama/OpenAI)
   - Stores with metadata
   - Now searchable by semantic similarity

7. Auto-Sync (background):
   - File watcher detects practice.py updated
   - Quality filter: source code → PASS
   - Archives module improvement

8. Next Time:
   User: How do I scrape trending repos?

   Bot → RAG System → Vector DB Search
     → Finds: "Daily Practice on github.com/trending: Success..."
     → Provides context to AI
     → AI: "Based on previous practice, here's how..."
```

## 📊 Integration Benefits

### Before Integration (Siloed)
```
Practice Engine ─┐
Speed Race      ─┤→ Separate systems
Error Handler   ─┤   No memory
Module Generator─┘   No learning
```

### After Integration (United)
```
Practice Engine ─┐
Speed Race      ─┤→ Vector Database ─→ Long-term Memory
Error Handler   ─┤   Quality Filter      Cross-session
Module Generator─┤   Auto-Sync           Continuous Learning
Telegram Bot    ─┘   RAG System          AI gets smarter
```

## 🔧 Windows Deployment

### One-Click Start

**PowerShell** (Recommended):
```powershell
./start_bot_with_memory.ps1
```

**Batch**:
```cmd
start_bot_with_memory.bat
```

### What Happens:
1. ✓ Checks Python installed
2. ✓ Installs dependencies (if needed)
3. ✓ Verifies .env configuration
4. ✓ Starts Qdrant vector database
5. ✓ Starts Telegram bot
6. ✓ All systems integrated and running

### Environment Setup (.env)
```bash
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_from_@BotFather
TELEGRAM_ALLOWED_USERS=your_telegram_user_id

# Optional (defaults work)
OLLAMA_URL=http://localhost:11434
QDRANT_URL=http://localhost:6333
```

## 🎮 Telegram Commands

### Memory Management
```
/memory help              - Show all commands
/memory search <query>    - Semantic search
/memory stats             - Knowledge base statistics
/memory recent [limit]    - Recent entries
/memory clear <days>      - Clear old entries
/memory export            - Export to JSON
```

### AI Control
```
/practice <url>           - Daily practice training
/competition             - Speed race & leaderboard
/auto                    - Auto-improvement mode
/stats                   - Usage & cost statistics
/status                  - Quality metrics
```

### Chat Intelligence
```
Just chat               - Ollama tries first (free)
Bot unsure             - Asks your guidance (free)
/gpt <question>        - Force OpenAI (paid)
/retry                 - Retry with OpenAI
```

## 🔄 Continuous Improvement Loop

```
1. User practices/competes
   ↓
2. Results archived to vector DB
   ↓
3. Quality filter prevents pollution
   ↓
4. AI searches knowledge for context (RAG)
   ↓
5. AI makes better decisions
   ↓
6. Success patterns archived
   ↓
7. Auto-sync updates knowledge
   ↓
8. REPEAT → AI gets smarter every day
```

## 💡 Design Philosophy

### Atomic Modules
- **Zero coupling**: Each module standalone
- **Pure functions**: Input → Output, no side effects
- **Composable**: Combine in any order
- **Testable**: Each module tested independently

### Integration Layer
- **Workflows**: Combine atomic modules
- **Vector DB**: Persistent memory across workflows
- **Quality Filter**: Automatic cleanup
- **Auto-Sync**: Continuous knowledge updates
- **Telegram**: Unified control interface

### Result
```
Atomic (程式邏輯) + Integration (執行層) =
  Strong AI Agent that continuously improves
```

## 📈 Monitoring Progress

### Vector Database Growth
```python
# Check knowledge accumulation
from src.core.modules.atomic.vector import KnowledgeManager

manager = KnowledgeManager(store)
stats = manager.get_statistics()

print(f"Total knowledge: {stats['total_entries']}")
print(f"Categories: {stats['categories']}")
print(f"Quality pass rate: {filter_stats['pass_rate']:.1%}")
```

### Telegram Stats
```
/stats

Shows:
- Ollama queries (free): 45
- Human guided (free): 5
- OpenAI queries (paid): 2
- Cost today: NT$15
- Saved: NT$1,200 ✅
```

## 🎯 Key Takeaways

1. **Atomic modules** = Zero coupling, maximum reusability
2. **Vector database** = Long-term memory, never forget
3. **Quality filter** = Clean knowledge, no pollution
4. **Auto-sync** = Always up-to-date
5. **Telegram bot** = Unified control
6. **RAG system** = Context-aware AI
7. **Integration** = Greater than sum of parts

## 🚀 Next Steps

### Daily Workflow
```bash
# Morning: Start bot on Windows
./start_bot_with_memory.ps1

# Throughout day: Practice and compete
Telegram: /practice new-site.com
Telegram: /competition

# Evening: Check progress
Telegram: /stats
Telegram: /memory stats

# Auto-sync runs continuously in background
# AI gets smarter automatically
```

### Knowledge Base Maintenance
```bash
# Weekly: Review and cleanup
Telegram: /memory clear 90  # Remove >90 days old

# Monthly: Export backup
Telegram: /memory export

# Anytime: Search knowledge
Telegram: /memory search error handling
```

## 💪 Why This Works

**Traditional AI**:
- Forgets after session ends
- Repeats same mistakes
- No accumulated wisdom
- Expensive (all queries to OpenAI)

**Flyto2 Integrated System**:
- ✅ Permanent memory (vector DB)
- ✅ Learns from mistakes (auto-archive)
- ✅ Accumulated wisdom (RAG context)
- ✅ Ultra-low cost (Three-Tier AI)
- ✅ Continuous improvement (auto-sync)
- ✅ Clean knowledge (quality filter)

Your AI agent becomes smarter every day, automatically! 🎯
