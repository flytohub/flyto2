# Knowledge Base Auto-Sync Guide

Automatically keep vector database synchronized with project changes.

## Problem

Project evolves constantly:
- New modules added
- Documentation updated
- Features changed
- Tests modified

→ Vector database becomes outdated
→ AI gets stale information

## Solution: 4 Auto-Sync Methods

### 1. Git Hook (Recommended for Development)

**Auto-sync after every commit**

Setup:
```bash
python scripts/setup_auto_sync.py
# Choose option 1
```

How it works:
- Hook triggers after `git commit`
- Detects changed files since last sync
- Updates only changed entries
- Fast (~5 seconds)

Best for:
- Active development
- Frequent commits
- Immediate sync needs

### 2. Windows Task Scheduler (Recommended for Windows)

**Periodic sync (e.g., daily)**

Setup:
```bash
python scripts/setup_auto_sync.py
# Choose option 2
```

Or manual:
1. Run setup to create PowerShell script
2. Open Task Scheduler (Win+R → `taskschd.msc`)
3. Import task from `scripts/knowledge_sync_task.xml`
4. Or create manually:
   - Action: `powershell.exe`
   - Arguments: `-ExecutionPolicy Bypass -File "scripts/run_knowledge_sync.ps1"`
   - Trigger: Daily at preferred time

Best for:
- Stable projects
- Scheduled maintenance
- Low resource usage

### 3. Cron Job (Linux/Mac)

**Hourly sync**

Setup:
```bash
python scripts/setup_auto_sync.py
# Choose option 3

# Or manually add to crontab:
crontab -e

# Add this line (runs hourly):
0 * * * * cd /path/to/flyto2 && python scripts/auto_sync_knowledge.py --mode incremental >> logs/knowledge_sync.log 2>&1
```

Best for:
- Linux/Mac servers
- Background automation
- Reliable periodic updates

### 4. File Watcher (Real-time Sync)

**Watches files and syncs immediately**

Start watcher:
```bash
# Check every 60 seconds (default)
python scripts/auto_sync_knowledge.py --mode watch

# Check every 5 minutes
python scripts/auto_sync_knowledge.py --mode watch --interval 300
```

Windows shortcut:
```bash
# Creates start_file_watcher.bat
python scripts/setup_auto_sync.py
# Choose option 4
```

Best for:
- Critical real-time needs
- Development with live AI
- When immediate sync required

**Note**: Uses continuous CPU, not recommended for battery

## Sync Modes

### Incremental Sync (Default)

Only syncs changed files:
```bash
python scripts/auto_sync_knowledge.py --mode incremental
```

- Fast (< 10 seconds)
- Low resource usage
- Tracks file hashes
- Detects changes automatically

### Full Sync

Re-aggregates entire knowledge base:
```bash
python scripts/auto_sync_knowledge.py --mode full
```

- Slower (~30 seconds)
- Complete refresh
- Useful after major changes
- Resets all file hashes

## Embedding Providers

Choose embedding provider:
```bash
# Local (free, offline)
python scripts/auto_sync_knowledge.py --embeddings local

# Ollama (local AI)
python scripts/auto_sync_knowledge.py --embeddings ollama

# OpenAI (best quality, requires API key)
python scripts/auto_sync_knowledge.py --embeddings openai
```

## Recommended Setup

### For Active Development
```bash
# 1. Git hook for immediate sync
python scripts/setup_auto_sync.py  # Option 1

# 2. Daily full sync via scheduler
python scripts/setup_auto_sync.py  # Option 2 or 3

# Result: Fast incremental + periodic full refresh
```

### For Windows + Ollama

**Option A: Scheduled Sync**
```bash
# Setup daily sync with Ollama
1. python scripts/setup_auto_sync.py  # Option 2
2. Modify PowerShell script:
   Change: --embeddings local
   To: --embeddings ollama
```

**Option B: Background Watcher with Ollama**
```bash
# Run file watcher with Ollama
python scripts/auto_sync_knowledge.py --mode watch --interval 300 --embeddings ollama

# Runs in background, checks every 5 minutes
# Uses Ollama for embeddings (local, free)
```

### For Stable Projects
```bash
# Weekly full sync
# Add to Task Scheduler/Cron with --mode full
```

## Monitoring

Check sync log:
```bash
# View recent syncs
cat logs/knowledge_sync.log

# Watch in real-time
tail -f logs/knowledge_sync.log
```

View sync state:
```bash
# See which files were synced
cat .knowledge_sync_state.json
```

## Manual Sync

Anytime:
```bash
# Quick incremental
python scripts/auto_sync_knowledge.py

# Full refresh
python scripts/auto_sync_knowledge.py --mode full
```

## Troubleshooting

### Sync not running
- Check Task Scheduler/Cron is active
- Verify script paths are absolute
- Check logs for errors

### Using too much CPU
- Increase watch interval (--interval 600 for 10 min)
- Use scheduled sync instead
- Switch to git hook only

### Vector DB not updating
- Run manual full sync
- Check embedding provider is available
- Verify Qdrant is running

## Performance

| Mode | Speed | CPU | Frequency |
|------|-------|-----|-----------|
| Incremental | 5-10s | Low | On change |
| Full | 30-60s | Medium | Daily/Weekly |
| Watch (60s) | Varies | Low-Medium | Real-time |
| Git Hook | 5-10s | Low | On commit |

## Best Practices

1. **Development**: Git hook + daily full sync
2. **Production**: Scheduled incremental (hourly/daily)
3. **Real-time needs**: File watcher (5-10 min interval)
4. **Low resource**: Git hook only
5. **Windows + Ollama**: Task scheduler with Ollama embeddings

## Example: Complete Windows Setup

```bash
# 1. Setup auto-sync
python scripts/setup_auto_sync.py
# Choose: 5 (Setup All)

# 2. Configure Task Scheduler
# - Opens automatically
# - Set to run daily at 2 AM
# - Uses local embeddings (free)

# 3. Start file watcher (optional)
# - Double-click: scripts/start_file_watcher.bat
# - Runs in background
# - Checks every 5 minutes

# Result:
# ✓ Git commits → immediate sync
# ✓ Daily 2 AM → full refresh
# ✓ File watcher → real-time updates
# ✓ All automatic, no manual intervention
```

Your Ollama on Windows can now continuously organize and feed knowledge automatically! 🎯

## Quality Filtering

Auto-sync includes intelligent quality filtering to prevent knowledge base pollution.

### What Gets Filtered

Automatically excluded:
- Debug statements (`print()`, `console.log`)
- Trivial responses ("ok", "yes", "thanks")
- Cache and temporary files
- Short/low-information content
- Test artifacts and compiled files

### Filter Modes

**Enabled by default** - Recommended for all use cases:
```bash
# Quality filtering enabled (default)
python scripts/auto_sync_knowledge.py --mode incremental
```

**Disable if needed** - Archives everything:
```bash
# Edit auto_sync_knowledge.py to disable filter
# Change: enable_quality_filter=True
# To: enable_quality_filter=False
```

### Quality Metrics

Monitor filtering effectiveness:
```bash
# Check what's being filtered (console output)
python scripts/auto_sync_knowledge.py --mode incremental

# Example output:
# Filtered practice result (score=0.10, reason=too_short)
# ✓ Synced 5 entries (2 filtered)
```

### Benefits

1. **Cleaner Knowledge Base** - Only valuable content stored
2. **Better AI Retrieval** - Relevant results, no noise
3. **Lower Costs** - Fewer embeddings = less API cost
4. **Faster Search** - Smaller vector DB = faster queries

**See**: `docs/QUALITY_FILTER_GUIDE.md` for detailed configuration

Your knowledge base stays clean while auto-syncing! 🎯
