#!/usr/bin/env python3
"""
Ingest Atomic Module Standards to Qdrant
English-only content for AI to learn from
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from src.core.modules.atomic.vector import get_connector
from src.core.modules.atomic.vector.knowledge_store import KnowledgeStore
from openai import OpenAI

def verify_english_only(text: str) -> bool:
    """Verify text contains no Chinese characters"""
    chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    return chinese_chars == 0

def chunk_text(text: str, max_chars: int = 1500) -> list:
    """Split text into chunks by sections"""
    lines = text.split('\n')
    chunks = []
    current_chunk = []
    current_size = 0

    for line in lines:
        line_size = len(line) + 1  # +1 for newline

        # Start new chunk if:
        # 1. Line starts with ## (major section)
        # 2. Current chunk would exceed max_chars
        if (line.startswith('##') and current_chunk) or \
           (current_size + line_size > max_chars and current_chunk):
            chunk_text = '\n'.join(current_chunk)
            if chunk_text.strip():
                chunks.append(chunk_text)
            current_chunk = [line]
            current_size = line_size
        else:
            current_chunk.append(line)
            current_size += line_size

    # Add remaining chunk
    if current_chunk:
        chunk_text = '\n'.join(current_chunk)
        if chunk_text.strip():
            chunks.append(chunk_text)

    return chunks

def main():
    print("=" * 70)
    print("📚 Ingesting Atomic Module Standards to Qdrant")
    print("=" * 70)
    print()

    # Load file
    file_path = Path("ATOMIC_MODULE_STANDARDS.md")
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return 1

    print(f"📄 Reading: {file_path}")
    content = file_path.read_text(encoding='utf-8')

    # Verify English only
    if not verify_english_only(content):
        print("❌ REJECTED: File contains Chinese characters!")
        print("   CRITICAL: Only English content allowed in Qdrant")
        return 1

    print(f"✅ Verified: 100% English content ({len(content)} chars)")

    # Chunk content
    chunks = chunk_text(content, max_chars=1500)
    print(f"✓ Split into {len(chunks)} chunks")
    print()

    # Connect to Qdrant
    print("━" * 70)
    print("🔌 Connecting to Qdrant Cloud...")
    print("━" * 70)

    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    if not qdrant_url or not qdrant_api_key:
        print("❌ Qdrant credentials not found in .env")
        return 1

    connector = get_connector(
        mode="cloud",
        url=qdrant_url,
        api_key=qdrant_api_key
    )

    # Use OpenAI for embeddings (existing collection requires 1536 dims)
    # Ollama is used for code generation, but OpenAI needed for vector search
    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "openai")

    store = KnowledgeStore(
        connector=connector,
        collection_name='flyto2_knowledge',
        embedding_provider=embedding_provider
    )

    print(f"✓ Connected to: {qdrant_url}")
    print()

    # Ingest chunks
    print("━" * 70)
    print("📦 Ingesting Standards to Knowledge Base...")
    print("━" * 70)
    print()

    success_count = 0

    for i, chunk in enumerate(chunks, 1):
        # Extract title from chunk (first line with #)
        lines = chunk.split('\n')
        title = next((line.strip('#').strip() for line in lines if line.startswith('#')), f"Section {i}")

        metadata = {
            "source": "ATOMIC_MODULE_STANDARDS.md",
            "category": "atomic_module_standards",
            "language": "en",
            "importance": 1.0,  # Critical for AI to understand
            "chunk_index": i,
            "section": title
        }

        try:
            entry_id = store.store(content=chunk, metadata=metadata)
            success_count += 1
            print(f"   {i}/{len(chunks)} ✓ {title[:50]}... → {entry_id}")
        except Exception as e:
            print(f"   {i}/{len(chunks)} ✗ Failed: {e}")

    print()
    print("=" * 70)
    print(f"✅ Ingestion Complete: {success_count}/{len(chunks)} chunks stored")
    print("=" * 70)
    print()
    print("📊 Summary:")
    print(f"   Source: {file_path}")
    print(f"   Collection: flyto2_knowledge")
    print(f"   Chunks: {success_count}")
    print(f"   Language: English only")
    print(f"   Category: atomic_module_standards")
    print()
    print("AI can now learn atomic module standards from knowledge base!")

    return 0 if success_count == len(chunks) else 1

if __name__ == "__main__":
    sys.exit(main())
