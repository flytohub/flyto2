# Vector Database Knowledge System

Fast AI onboarding via semantic search - understand the entire project in seconds instead of hours.

## Overview

This system enables ANY AI (Ollama, OpenAI, Claude, etc.) to instantly understand the Flyto2 project without reading thousands of lines of code. Knowledge is extracted from documentation and code, vectorized, and stored in Qdrant for semantic search.

## Quick Start

### 1. Aggregate Project Knowledge

```bash
# Using local embeddings (free, no API key needed)
python scripts/aggregate_project_knowledge.py --mode local --embeddings local

# Using OpenAI embeddings (requires OPENAI_API_KEY)
python scripts/aggregate_project_knowledge.py --mode local --embeddings openai

# Using Ollama embeddings (requires Ollama running)
python scripts/aggregate_project_knowledge.py --mode local --embeddings ollama
```

### 2. Query Knowledge Base

```bash
# Single query
python scripts/query_project_knowledge.py "How do atomic modules work?"

# Get more results
python scripts/query_project_knowledge.py "What is the AI architecture?" --top-k 5

# Interactive mode
python scripts/query_project_knowledge.py --interactive
```

## How It Works

### Knowledge Sources

The aggregator extracts knowledge from:

1. **CLAUDE.md** - Project instructions, architecture, concepts
2. **COMPLETE_FEATURE_CHECKLIST.md** - Feature status, implementations
3. **Module Docstrings** - Implementation details
4. **Core Knowledge** - Essential project facts

### Knowledge Schema

Each entry contains:
```python
{
    "content": "Knowledge text",
    "metadata": {
        "source": "CLAUDE.md",
        "category": "architecture|feature|module|...",
        "priority": "critical|high|normal",
        # ... additional context
    }
}
```

### Embedding Providers

Three options for generating embeddings:

1. **Local (sentence-transformers)**: Free, offline, 384 dimensions
   - Model: all-MiniLM-L6-v2
   - Best for: Development, testing, no API costs

2. **Ollama**: Free, local AI, 768 dimensions
   - Model: nomic-embed-text
   - Best for: Privacy, local deployment

3. **OpenAI**: High quality, 1536 dimensions
   - Model: text-embedding-3-small
   - Best for: Production, best accuracy

## Usage Examples

### For AI Assistants

When starting a new session:

```python
from src.core.modules.atomic.vector import VectorDBConnector, KnowledgeStore

# Connect to knowledge base
connector = VectorDBConnector(mode="local")
connector.connect()

store = KnowledgeStore(connector, "flyto2_project_knowledge")

# Get project overview
results = store.search("What is this project about?", top_k=3)
for r in results:
    print(r['content'])

# Understand specific features
results = store.search("How does the training system work?", top_k=2)
```

### For Developers

```bash
# Update knowledge base after major changes
python scripts/aggregate_project_knowledge.py --mode local --embeddings local

# Find relevant documentation
python scripts/query_project_knowledge.py "How to create a new atomic module?"

# Explore interactively
python scripts/query_project_knowledge.py --interactive
```

## Cloud Deployment

To use Qdrant Cloud:

1. Set environment variables:
   ```bash
   export QDRANT_URL="https://your-cluster.qdrant.io"
   export QDRANT_API_KEY="your-api-key"
   ```

2. Run with cloud mode:
   ```bash
   python scripts/aggregate_project_knowledge.py --mode cloud --embeddings openai
   ```

## Knowledge Updates

Re-run aggregation after:
- Adding new features
- Updating documentation
- Creating new modules
- Major architecture changes

The script will update the knowledge base with latest information.

## Statistics

Current knowledge base:
- **91 entries** extracted from project
- **10 core concepts** - essential project facts
- **31 feature entries** - completed implementations
- **50 module entries** - code documentation

Coverage:
- Architecture ✓
- API Features ✓
- Training System ✓
- Testing Philosophy ✓
- Module Registry ✓

## Benefits

### For AI Sessions
- **Instant understanding** - no need to read entire codebase
- **Context-aware responses** - query relevant knowledge
- **Consistent knowledge** - same information across sessions

### For Development
- **Fast onboarding** - new developers understand project quickly
- **Documentation search** - find relevant docs semantically
- **Knowledge preservation** - project knowledge persists

### For Continuous Improvement
- **AI agents** can query knowledge before proposing changes
- **Automated testing** can reference expected behavior
- **Evolution tracking** by versioning knowledge base

## Technical Details

### Vector Database: Qdrant
- High-performance Rust implementation
- Supports local and cloud deployment
- HNSW indexing for fast similarity search

### Storage Location
- Local mode: `./qdrant_storage/`
- Cloud mode: Managed by Qdrant Cloud

### Performance
- Aggregation: ~30 seconds (91 entries, local embeddings)
- Query: <1 second (local), <2 seconds (cloud)
- Storage: ~100KB (compressed vectors)

## Future Enhancements

- Auto-aggregation on git push
- Knowledge versioning and diff
- Multi-language support
- RAG integration for AI proposals
- Knowledge graph visualization
