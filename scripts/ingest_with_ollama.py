#!/usr/bin/env python3
"""
Ingest documents to Qdrant using Ollama embeddings
English-only content - NO CHINESE ALLOWED
"""
import os
import sys
import re
import uuid
import requests
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Config
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
OLLAMA_URL = "http://localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text"
COLLECTION_NAME = "flyto2_ollama"  # New collection for Ollama embeddings
VECTOR_SIZE = 768  # nomic-embed-text dimension


def verify_english_only(text: str) -> bool:
    """Verify text contains no Chinese characters"""
    chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    return chinese_chars == 0


def get_ollama_embedding(text: str) -> Optional[List[float]]:
    """Generate embedding using Ollama"""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": EMBEDDING_MODEL, "prompt": text},
            timeout=60
        )
        response.raise_for_status()
        return response.json()["embedding"]
    except Exception as e:
        print(f"Ollama embedding error: {e}")
        return None


def chunk_text(text: str, max_chars: int = 1500) -> List[str]:
    """Split text into chunks by sections"""
    lines = text.split('\n')
    chunks = []
    current_chunk = []
    current_size = 0

    for line in lines:
        line_size = len(line) + 1

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

    if current_chunk:
        chunk_text = '\n'.join(current_chunk)
        if chunk_text.strip():
            chunks.append(chunk_text)

    return chunks


def extract_title(chunk: str) -> str:
    """Extract title from chunk"""
    lines = chunk.split('\n')
    for line in lines:
        if line.startswith('#'):
            return line.strip('#').strip()[:50]
    return "Section"


def ingest_file(client: QdrantClient, file_path: Path, category: str = "general") -> int:
    """Ingest a single file to Qdrant"""
    print(f"\n  Reading: {file_path.name}")

    content = file_path.read_text(encoding='utf-8')

    # Verify English only
    if not verify_english_only(content):
        print(f"    SKIPPED: Contains Chinese characters")
        return 0

    print(f"    Verified: English only ({len(content)} chars)")

    # Chunk content
    chunks = chunk_text(content, max_chars=1500)
    print(f"    Split into {len(chunks)} chunks")

    # Ingest chunks
    success_count = 0
    points = []

    for i, chunk in enumerate(chunks, 1):
        vector = get_ollama_embedding(chunk)
        if not vector:
            print(f"    [{i}/{len(chunks)}] FAILED: Could not generate embedding")
            continue

        title = extract_title(chunk)
        point_id = str(uuid.uuid4())

        point = PointStruct(
            id=point_id,
            vector=vector,
            payload={
                "content": chunk,
                "source": file_path.name,
                "category": category,
                "language": "en",
                "importance": 1.0,
                "chunk_index": i,
                "section": title
            }
        )
        points.append(point)
        success_count += 1
        print(f"    [{i}/{len(chunks)}] OK: {title[:40]}...")

    # Batch upload
    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)

    return success_count


def main():
    print("=" * 70)
    print("Ingesting Documents to Qdrant (Ollama Embeddings)")
    print("ENGLISH ONLY - NO CHINESE ALLOWED")
    print("=" * 70)

    # Check config
    if not QDRANT_URL or not QDRANT_API_KEY:
        print("ERROR: Missing Qdrant credentials in .env")
        return 1

    # Check Ollama
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        r.raise_for_status()
        print(f"Ollama: Running")
    except:
        print("ERROR: Ollama not running at localhost:11434")
        return 1

    # Connect to Qdrant
    print(f"\nConnecting to Qdrant Cloud...")
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=30)

    # Create/verify collection
    try:
        info = client.get_collection(COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' exists ({info.points_count} points)")
    except:
        print(f"Creating collection '{COLLECTION_NAME}'...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
        )

    # Files to ingest
    base_dir = Path(__file__).parent.parent

    files_to_ingest = [
        (base_dir / "ATOMIC_MODULE_STANDARDS.md", "atomic_module_standards"),
        (base_dir / "ENGLISH_KNOWLEDGE_BASE.md", "knowledge_base"),
        (base_dir / "CONTRIBUTING.md", "contributing"),
    ]

    # Also check for IMPLEMENTATION_GUIDE if translated
    impl_guide = base_dir / "IMPLEMENTATION_GUIDE_V4_EN.md"
    if impl_guide.exists():
        files_to_ingest.append((impl_guide, "implementation_guide"))

    print(f"\n{'=' * 70}")
    print(f"Ingesting {len(files_to_ingest)} files...")
    print(f"{'=' * 70}")

    total_chunks = 0

    for file_path, category in files_to_ingest:
        if file_path.exists():
            count = ingest_file(client, file_path, category)
            total_chunks += count
        else:
            print(f"\n  SKIP: {file_path.name} (not found)")

    print(f"\n{'=' * 70}")
    print(f"COMPLETE: {total_chunks} chunks ingested to '{COLLECTION_NAME}'")
    print(f"{'=' * 70}")

    return 0


if __name__ == "__main__":
    sys.exit(main())