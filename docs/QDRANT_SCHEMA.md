# Qdrant Vector Database Schema & RAG Design

**World-Class RAG System for Flyto2 Self-Evolving AI Agent**

## 🎯 Design Goals

1. **AI can find knowledge instantly** - First-time retrieval success
2. **Multilingual support** - Chinese input → English search → Accurate results
3. **Structured queries** - Reproducible across different LLMs
4. **Self-evolving** - Learn from every error, practice, success

---

## 📊 Qdrant Collection Schema

### Collection: `flyto2_project_knowledge`

```json
{
  "id": "uuid-v4",
  "content": "Pure text content (no code, no debug logs)",
  "embedding": [384-dimensional vector],
  "metadata": {
    "language": "zh" | "en",
    "category": "practice" | "error" | "success" | "proposal" | "module" | "pain_point" | "architecture" | "status" | "issues" | "feature" | "philosophy",
    "source": "daily_practice" | "speed_race" | "analysis" | "human_note" | "ai_generated" | "sync",
    "module_id": "browser.click" | null,
    "tags": ["scraping", "browser", "timeout"],
    "importance": 0.0 ~ 1.0,
    "is_translated": true | false,
    "original_language": "zh" | "en" | null,
    "created_at": "2025-12-02T10:00:00Z",
    "updated_at": "2025-12-02T10:00:00Z"
  }
}
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | UUID v4 |
| `content` | string | ✅ | Pure text, no code blocks |
| `embedding` | vector | ✅ | 384-dim (local model) or 1536-dim (OpenAI) |
| **Metadata** | | | |
| `language` | enum | ✅ | "zh" or "en" |
| `category` | enum | ✅ | See categories below |
| `source` | string | ✅ | Where this knowledge came from |
| `module_id` | string | ❌ | Related module (e.g., "browser.click") |
| `tags` | array | ❌ | Keywords for filtering |
| `importance` | float | ❌ | 0.0 ~ 1.0, higher = more important |
| `is_translated` | bool | ❌ | True if translated from another language |
| `original_language` | string | ❌ | Original language if translated |
| `created_at` | datetime | ✅ | ISO 8601 timestamp |
| `updated_at` | datetime | ✅ | ISO 8601 timestamp |

---

## 📁 Categories

### Core Categories

1. **`practice`** - Daily practice experiences
   - Example: "Successfully scraped data using browser.extract"
   - Importance: 0.6 ~ 0.8

2. **`error`** - Error solutions and fixes
   - Example: "ModuleNotFoundError: playwright → Solution: pip install playwright"
   - Importance: 0.7 ~ 0.9

3. **`success`** - Successful workflows and patterns
   - Example: "Best practice for handling dynamic content"
   - Importance: 0.8 ~ 1.0

4. **`proposal`** - Improvement proposals
   - Example: "Proposal: Add retry mechanism to browser.click"
   - Importance: 0.5 ~ 0.7

5. **`module`** - Module documentation and usage
   - Example: "browser.click parameters: selector, timeout, force"
   - Importance: 0.9 ~ 1.0

### Meta Categories

6. **`pain_point`** - Project pain points and blockers
   - Example: "Ollama not running blocks all AI features"
   - Importance: 0.9 ~ 1.0

7. **`architecture`** - Architecture design and decisions
   - Example: "Atomic module system with AI-first philosophy"
   - Importance: 0.8 ~ 0.9

8. **`status`** - Project status and assessment
   - Example: "Test results: 1/3 passing, Ollama blocker"
   - Importance: 0.7 ~ 0.8

9. **`issues`** - Known issues tracker
   - Example: "P0: Ollama not running (CRITICAL)"
   - Importance: 0.8 ~ 1.0

10. **`feature`** - Feature implementation details
    - Example: "Perfect Flow Bot with three-way error resolution"
    - Importance: 0.7 ~ 0.9

11. **`philosophy`** - Project philosophy and principles
    - Example: "No hardcoded error handling - all errors go to AI"
    - Importance: 0.9 ~ 1.0

---

## 🌉 Language Bridge Layer (LBL)

### The Problem

- **Chinese embedding**: Low precision, limited training data
- **English embedding**: High precision, vast training data
- **Vector mismatch**: Chinese query can't find English knowledge

### The Solution

**All queries → English → Vectorize → Search**

```
Chinese Input: "如何修復 timeout 錯誤？"
    ↓
Language Detection: zh
    ↓
Semantic Translation: "How to fix timeout error?"
    ↓
Vectorize (EN): [0.123, 0.456, ...]
    ↓
Search Qdrant
    ↓
Return Results (can be zh or en)
```

### Implementation

```python
from src.core.utils.rag_retriever import retrieve_knowledge

# Chinese query (auto-translates)
results = await retrieve_knowledge("如何修復 Ollama 錯誤？")

# English query (direct search)
results = await retrieve_knowledge("How to fix Ollama error?")
```

---

## 🀄 Bilingual Storage Strategy

### Strategy: Store Both Versions

When storing Chinese content:
1. Store **original Chinese** (for keyword search)
2. Store **English translation** (for semantic search)

### Example

**Input**:
```python
content = "我在使用 browser.click 時遇到 timeout 錯誤"
metadata = {"category": "error", "module_id": "browser.click"}
```

**Stored in Qdrant**:

Entry 1 (Chinese):
```json
{
  "content": "我在使用 browser.click 時遇到 timeout 錯誤",
  "metadata": {
    "language": "zh",
    "category": "error",
    "module_id": "browser.click",
    "is_translated": false
  }
}
```

Entry 2 (English):
```json
{
  "content": "Encountered timeout error when using browser.click",
  "metadata": {
    "language": "en",
    "category": "error",
    "module_id": "browser.click",
    "is_translated": true,
    "original_language": "zh"
  }
}
```

### Implementation

```python
from src.core.utils.language_bridge import get_language_bridge

bridge = get_language_bridge()

# Create bilingual entries
entries = await bridge.create_bilingual_entry(
    content="你的中文內容",
    metadata={"category": "practice", "module_id": "browser.click"}
)

# Store all entries to Qdrant
from src.core.utils.vector_db_manager import vector_store

for entry in entries:
    await vector_store(entry["content"], entry["metadata"])
```

---

## 🔍 Three-Step Retrieval Format

### Format

```
[RETRIEVE KNOWLEDGE]
query: natural language query
filters:
  language: en
  category: error
  module_id: browser.click
  importance: {"$gte": 0.7}
top_k: 5
[/RETRIEVE]
```

### Why This Format?

1. **Structured** - Clear, parseable, reproducible
2. **LLM-agnostic** - Works with Ollama, OpenAI, Claude, Gemini
3. **Filterable** - Precise results with metadata filtering
4. **Debuggable** - Easy to see what AI is querying

### Example Usage

```python
from src.core.utils.rag_retriever import execute_structured_query

request = """
[RETRIEVE KNOWLEDGE]
query: How to fix browser timeout errors?
filters:
  category: error
  module_id: browser.click
  importance: {"$gte": 0.7}
top_k: 5
[/RETRIEVE]
"""

results = await execute_structured_query(request)
```

### AI Prompt Integration

```
You are Flyto2 AI Agent. When you need knowledge:

1. Use [RETRIEVE KNOWLEDGE] format
2. Specify filters to narrow results
3. Use retrieved knowledge to answer user

Example:
User: "How do I fix timeout in browser.click?"

You:
[RETRIEVE KNOWLEDGE]
query: browser.click timeout error solution
filters:
  category: error
  module_id: browser.click
top_k: 3
[/RETRIEVE]

[System returns results]

You: Based on retrieved knowledge, here's how to fix...
```

---

## 🚀 Quick Start

### 1. Store Knowledge (Bilingual)

```python
from src.core.utils.language_bridge import get_language_bridge
from src.core.utils.vector_db_manager import vector_store

bridge = get_language_bridge()

# Store Chinese content (auto-creates EN version)
entries = await bridge.create_bilingual_entry(
    content="我在 browser.click 時遇到 timeout，解決方法是增加等待時間",
    metadata={
        "category": "practice",
        "source": "daily_practice",
        "module_id": "browser.click",
        "tags": ["browser", "timeout", "solution"],
        "importance": 0.8
    }
)

for entry in entries:
    await vector_store(entry["content"], entry["metadata"])
```

### 2. Retrieve Knowledge (Any Language)

```python
from src.core.utils.rag_retriever import retrieve_knowledge

# Chinese query (auto-translates to EN)
results = await retrieve_knowledge(
    query="如何修復 browser timeout？",
    filters={"category": "error", "module_id": "browser.click"},
    top_k=5
)

# English query (direct search)
results = await retrieve_knowledge(
    query="How to fix browser timeout?",
    filters={"category": "error"},
    top_k=5
)
```

### 3. Use Structured Format

```python
from src.core.utils.rag_retriever import execute_structured_query

request = """
[RETRIEVE KNOWLEDGE]
query: Ollama blocker solutions
filters:
  category: pain_point
  priority: P0
top_k: 3
[/RETRIEVE]
"""

results = await execute_structured_query(request)
```

---

## 📈 Importance Scoring Guide

| Score | Meaning | Examples |
|-------|---------|----------|
| **1.0** | Critical knowledge | Module API docs, Critical blockers |
| **0.9** | Very important | Architecture decisions, P0 issues |
| **0.8** | Important | Successful patterns, Common errors |
| **0.7** | Useful | Good practices, P1 issues |
| **0.6** | Informative | Learning notes, P2 issues |
| **0.5** | Reference | Ideas, proposals |
| **< 0.5** | Low priority | Experimental, unverified |

---

## 🏗️ Collection Indices

**Required Indices** (for fast filtering):

1. `metadata.language` - Language filtering
2. `metadata.category` - Category filtering
3. `metadata.module_id` - Module-specific queries
4. `metadata.importance` - Importance-based sorting
5. `metadata.created_at` - Time-based queries

### Qdrant Configuration

```python
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

client = QdrantClient(path="./qdrant_storage")

# Create collection with indices
client.create_collection(
    collection_name="flyto2_project_knowledge",
    vectors_config=VectorParams(
        size=384,  # Local embedding model
        distance=Distance.COSINE
    )
)

# Payload indices for fast filtering
client.create_payload_index(
    collection_name="flyto2_project_knowledge",
    field_name="language",
    field_schema="keyword"
)

client.create_payload_index(
    collection_name="flyto2_project_knowledge",
    field_name="category",
    field_schema="keyword"
)

client.create_payload_index(
    collection_name="flyto2_project_knowledge",
    field_name="module_id",
    field_schema="keyword"
)
```

---

## 🌍 Why This Design is World-Class

### 1. Multilingual RAG Without Quality Loss
- Chinese users get same precision as English users
- No vector mismatch issues
- Semantic search, not keyword matching

### 2. LLM-Agnostic Structured Queries
- Works with Ollama, OpenAI, Claude, Gemini
- Reproducible across model changes
- Easy debugging and monitoring

### 3. Self-Evolving Knowledge Base
- Every error solution → Stored
- Every practice → Learned
- Every success → Remembered
- System gets smarter over time

### 4. Production-Ready Filtering
- Fast metadata indices
- Precise category/module filtering
- Importance-based ranking
- Time-based queries

### 5. Developer-Friendly
- Simple API: `retrieve_knowledge("query")`
- Bilingual storage: Automatic
- Translation: Automatic
- Just use it, it works

---

## 📚 References

### Files Created

1. **`src/core/utils/language_bridge.py`** - Language Bridge Layer
2. **`src/core/utils/rag_retriever.py`** - RAG Retriever with structured queries
3. **`scripts/test_language_bridge.py`** - Test suite
4. **`docs/QDRANT_SCHEMA.md`** - This document

### Example Usage

See `/scripts/test_language_bridge.py` for complete examples.

### Future Enhancements

1. **Multi-LLM Translation** - Ensemble translation (Ollama + OpenAI + Claude)
2. **Confidence Scoring** - Rate translation quality before storing
3. **Automatic Tagging** - AI-generated tags for better filtering
4. **Collaborative Learning** - Share anonymized solutions with community
5. **Real-time Sync** - Auto-sync successful workflows to knowledge base

---

## 🎯 Summary

**You now have**:
- ✅ World-class Qdrant schema
- ✅ Language Bridge Layer (zh ↔ en)
- ✅ Bilingual storage (automatic)
- ✅ Structured query format
- ✅ RAG-ready architecture

**Your AI can now**:
- Find knowledge in any language
- Learn from every experience
- Evolve continuously
- Never forget solutions

**This is the foundation** for Flyto2 to become a truly self-evolving AI agent.

---

<div align="center">

**Flyto2: Self-Evolving AI Agent with World-Class RAG**

[GitHub](https://github.com/flytohub/flyto2) • [Documentation](../README.md)

</div>
