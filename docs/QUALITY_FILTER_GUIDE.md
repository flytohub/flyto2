# Quality Filter Guide

Prevent knowledge base pollution with intelligent content filtering.

## Problem

Not all content is worth storing in the vector database:
- Debug print statements
- Trivial conversations ("ok", "yes", "thanks")
- Temporary files and cache
- Low-information content
- Repeated noise

Without filtering → Knowledge base becomes polluted → AI retrieves irrelevant results

## Solution: Quality Filter System

Three-layer filtering approach:

### 1. Content-Based Filtering

**QualityFilter** - General-purpose filter for all content types

Filters out:
- Empty content
- Too short content (< 50 chars, < 5 words)
- Debug statements (`print()`, `console.log`)
- Temporary markers (`TODO:`, `FIXME:`)
- Test artifacts
- Cache/compiled files
- Trivial responses ("ok", "yes", "hi")

Boosts importance for:
- Technical keywords (module, function, class, error, solution, etc.)
- Longer content (> 200 chars, > 500 chars)
- Code indicators (def, class, import, async, etc.)
- Important categories (error, solution, architecture, feature)
- High priority items

### 2. Conversation-Specific Filtering

**ConversationFilter** - Specialized for chat messages

Additional filtering:
- Early trivial exchanges (first 3 turns with < 20 chars)
- Chinese trivial responses ("ok", "good", "thanks", "understood")
- Emoticons only
- Continuation markers ("continue...")

Importance boosts:
- Assistant responses with code/implementation → +0.2
- User questions with "how", "why", "implement", "error", "bug" → +0.15

### 3. File Change Filtering

**FileChangeFilter** - Specialized for file system changes

Always excludes:
- Log files (`.log`)
- Cache files (`.cache`, `.pyc`, `__pycache__`)
- Lock files (`.lock`)
- Dependency locks (`package-lock.json`, `yarn.lock`)
- Editor configs (`.vscode`, `.idea`)

Prioritizes:
- Source code (`.py`, `.js`, `.ts`)
- Documentation (`.md`, `README`, `CHANGELOG`)
- Configuration (`.yaml`, `.json`)
- New files → +0.1 boost
- Deleted files → -0.2 penalty

## Quality Scoring

Each piece of content receives a quality score (0-1):

| Score Range | Meaning | Action |
|-------------|---------|--------|
| 0.0 - 0.2 | Very low quality | Always filtered |
| 0.3 - 0.4 | Low quality | Filtered by default |
| 0.5 - 0.6 | Medium quality | Passed |
| 0.7 - 0.8 | Good quality | Passed with boost |
| 0.9 - 1.0 | Excellent quality | Highest priority |

**Default threshold**: 0.3

## Usage

### Basic Usage

```python
from src.core.modules.atomic.vector import QualityFilter

qf = QualityFilter()

content = "Implemented new error handling module with retry logic"
should_archive, score, reason = qf.should_archive(content)

if should_archive:
    print(f"Archive with score: {score:.2f}")
else:
    print(f"Filtered: {reason}")
```

### With ExperienceArchiver

```python
from src.core.modules.atomic.vector import (
    VectorDBConnector,
    KnowledgeStore,
    ExperienceArchiver
)

connector = VectorDBConnector(mode="local")
connector.connect()

store = KnowledgeStore(
    connector=connector,
    collection_name="project_knowledge",
    embedding_provider="local"
)

# Quality filter enabled by default
archiver = ExperienceArchiver(
    knowledge_store=store,
    enable_quality_filter=True
)

# This will be archived (good content)
archiver.archive_error(
    module_id="browser.click",
    error_type="TimeoutError",
    error_message="Element not found after 30s timeout",
    solution="Added explicit wait and retry logic"
)

# This will be filtered (too short)
archiver.archive_error(
    module_id="test",
    error_type="Error",
    error_message="ok"
)  # Returns None - filtered
```

### Conversation Filtering

```python
from src.core.modules.atomic.vector.quality_filter import ConversationFilter

cf = ConversationFilter()

# Filter conversation messages
should_archive, score, reason = cf.should_archive_message(
    message="How do I implement error handling in the browser module?",
    role="user",
    turn_number=5
)

if should_archive:
    # Store this valuable conversation turn
    store_to_knowledge_base(message, score)
```

### File Change Filtering

```python
from src.core.modules.atomic.vector.quality_filter import FileChangeFilter

fcf = FileChangeFilter()

# Check if file change should be archived
should_archive, score, reason = fcf.should_archive_file_change(
    file_path="src/core/modules/browser.py",
    change_type="modified"
)

if should_archive:
    # Archive this important file change
    archive_file_change(file_path, score)
```

### Disable Filtering

```python
# Disable quality filter if you want to archive everything
archiver = ExperienceArchiver(
    knowledge_store=store,
    enable_quality_filter=False
)

# Now even trivial content will be archived
```

## Filter Statistics

Track filtering effectiveness:

```python
# Get archiver stats with filter metrics
stats = archiver.get_archive_stats()

print(stats)
# {
#     'total_archived': 100,
#     'collection': 'project_knowledge',
#     'provider': 'local',
#     'quality_filter': {
#         'total_evaluated': 150,
#         'passed': 100,
#         'filtered': 50,
#         'pass_rate': 0.67
#     }
# }

# Get filter stats directly
filter_stats = archiver.quality_filter.get_stats()
print(f"Pass rate: {filter_stats['pass_rate']:.1%}")
```

## Customizing Filters

### Adjust Thresholds

```python
qf = QualityFilter()

# Lower threshold = more permissive
qf.MIN_IMPORTANCE_SCORE = 0.2

# Higher minimum length
qf.MIN_CONTENT_LENGTH = 100
qf.MIN_WORDS = 10
```

### Add Custom Patterns

```python
qf = QualityFilter()

# Add custom exclude patterns
qf.EXCLUDE_PATTERNS.append(r'DEPRECATED')

# Add custom important keywords
qf.IMPORTANT_KEYWORDS.extend(['vector', 'embedding', 'qdrant'])
```

### Factory Function

```python
from src.core.modules.atomic.vector.quality_filter import create_filter

# Create specific filter type
general_filter = create_filter("default")
conversation_filter = create_filter("conversation")
file_filter = create_filter("file")
```

## Integration with Auto-Sync

Quality filter automatically works with auto-sync:

```bash
# Auto-sync with quality filtering enabled (default)
python scripts/auto_sync_knowledge.py --mode incremental

# The sync system uses ExperienceArchiver which has filtering enabled
```

When auto-sync detects file changes, quality filter prevents:
- Cache file updates from being stored
- Log file changes from polluting knowledge base
- Debug code changes from being archived
- Trivial commit messages from being stored

## Best Practices

### 1. Development Phase
- **Enable filtering** (default) to prevent debug noise
- Review filtered content periodically to ensure nothing important is lost
- Adjust thresholds if too much is filtered

### 2. Production
- **Keep filtering enabled** to maintain knowledge base quality
- Monitor pass rates (aim for 50-70%)
- Too high pass rate (> 90%) → filter may be too permissive
- Too low pass rate (< 30%) → filter may be too strict

### 3. Specialized Content
- Use **ConversationFilter** for chat/dialogue systems
- Use **FileChangeFilter** for git hook integrations
- Use **QualityFilter** for general content

### 4. Quality Score Usage
- Store quality_score in metadata for later filtering
- Query high-quality content first: `filters={"quality_score": {"gte": 0.7}}`
- Use score for ranking search results

## Examples

### Example 1: Preventing Debug Noise

```python
# Without filter
archiver = ExperienceArchiver(store, enable_quality_filter=False)
archiver.archive_error("test", "Error", "print(x)")
# Stores: "Error in test: | Type: Error | Message: print(x)"

# With filter
archiver = ExperienceArchiver(store, enable_quality_filter=True)
archiver.archive_error("test", "Error", "print(x)")
# Filtered: excluded_pattern:print\(
# Returns: None
```

### Example 2: Conversation Quality

```python
cf = ConversationFilter()

# Low-quality early exchange
cf.should_archive_message("ok", "user", turn_number=1)
# → (False, 0.1, "early_trivial")

# High-quality technical discussion
cf.should_archive_message(
    "How do I implement async error handling with retry logic?",
    "user",
    turn_number=10
)
# → (True, 0.80, "conversation_passed")
```

### Example 3: File Change Intelligence

```python
fcf = FileChangeFilter()

# Important: Source code
fcf.should_archive_file_change("src/core/browser.py", "modified")
# → (True, 0.80, "important_file")

# Unimportant: Cache
fcf.should_archive_file_change("__pycache__/module.pyc", "modified")
# → (False, 0.0, "excluded_file:\.pyc$")
```

## Monitoring

Check what's being filtered:

```bash
# Enable verbose filtering (prints filtered content)
# Already enabled in ExperienceArchiver - check console output

# Example output:
# Filtered practice result (score=0.10, reason=too_short)
# Filtered error log (score=0.20, reason=excluded_pattern:TODO:)
# Filtered success pattern (score=0.25, reason=low_importance)
```

## Performance

Quality filtering is fast:
- Content analysis: < 1ms per item
- Regex matching: Compiled patterns cached
- Minimal memory overhead
- No external API calls

**Recommendation**: Always enable for production use

## Troubleshooting

### Too much content filtered

```python
# Lower the threshold
qf.MIN_IMPORTANCE_SCORE = 0.2

# Or disable for specific content types
if content_type == "error_log":
    archiver.quality_filter = None
    archiver.archive_error(...)
    archiver.quality_filter = QualityFilter()
```

### Important content filtered

```python
# Check why it was filtered
should_archive, score, reason = qf.should_archive(content)
print(f"Filtered: {reason}, Score: {score}")

# Add metadata boost
metadata = {"category": "critical", "priority": "high"}
should_archive, score, reason = qf.should_archive(content, metadata)
# Critical/high priority items get +0.2 to +0.35 boost
```

### Filter not working

```python
# Ensure filter is enabled
assert archiver.quality_filter is not None

# Check stats
stats = archiver.quality_filter.get_stats()
print(stats)  # Should show some filtered items
```

Your knowledge base stays clean and AI gets high-quality context! 🎯
