#!/usr/bin/env python3
"""
Ingest English-Only Knowledge Base - Enterprise Grade
NO CHINESE ALLOWED
"""
import os
import sys
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from openai import OpenAI

# Config
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COLLECTION_NAME = "flyto2_knowledge"

# OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def chunk_text(text: str, chunk_size: int = 1000) -> List[str]:
    """Split text into chunks by paragraphs"""
    # Split by double newline (paragraphs)
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) < chunk_size:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def verify_english_only(text: str) -> bool:
    """Verify text is English only - NO CHINESE"""
    # Check for Chinese characters
    chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')

    if chinese_chars > 0:
        return False

    return True

def get_embedding(text: str) -> List[float]:
    """Generate OpenAI embedding"""
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def extract_category(chunk: str) -> str:
    """Extract category from chunk content"""
    chunk_lower = chunk.lower()

    if "yaml" in chunk_lower or "workflow" in chunk_lower:
        return "workflow"
    elif "module" in chunk_lower and ("browser" in chunk_lower or "api" in chunk_lower):
        return "module"
    elif "architecture" in chunk_lower or "layer" in chunk_lower:
        return "architecture"
    elif "error" in chunk_lower or "debug" in chunk_lower:
        return "debugging"
    elif "test" in chunk_lower:
        return "testing"
    else:
        return "general"

def ingest_guide(guide_path: str):
    """Ingest English-only guide"""
    print(f"\n📖 Reading: {guide_path}")

    with open(guide_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Verify English only
    if not verify_english_only(content):
        print("❌ FAILED: Document contains Chinese characters!")
        print("   NO CHINESE ALLOWED in knowledge base!")
        return False

    print("✅ Verified: English only")

    # Split into chunks
    chunks = chunk_text(content, chunk_size=800)
    print(f"   Split into {len(chunks)} chunks")

    # Connect to Qdrant
    print(f"\n🔗 Connecting to Qdrant Cloud...")
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        timeout=30
    )

    # Ensure collection exists
    try:
        client.get_collection(COLLECTION_NAME)
        print(f"   ✓ Collection '{COLLECTION_NAME}' exists")
    except Exception:
        print(f"   Creating collection '{COLLECTION_NAME}'...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )

    # Ingest chunks
    print(f"\n📥 Ingesting chunks...")
    points = []
    point_id = 1

    for i, chunk in enumerate(chunks):
        print(f"   [{i+1}/{len(chunks)}] Processing...", end='\r')

        # Verify chunk is English only
        if not verify_english_only(chunk):
            print(f"\n⚠️  Skipping chunk {i+1}: Contains Chinese")
            continue

        # Extract category
        category = extract_category(chunk)

        # Generate embedding
        vector = get_embedding(chunk)

        # Create point
        point = PointStruct(
            id=point_id,
            vector=vector,
            payload={
                "content": chunk,
                "source": os.path.basename(guide_path),
                "chunk_id": i,
                "category": category,
                "language": "en",  # ENGLISH ONLY
                "importance": 1.0  # High priority
            }
        )
        points.append(point)
        point_id += 1

        # Batch upload (every 50)
        if len(points) >= 50:
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
            points = []

    # Upload remaining
    if points:
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )

    print(f"\n   ✅ Ingested {point_id - 1} chunks (English only)")
    return True

def main():
    print("=" * 60)
    print("🚀 English-Only Knowledge Base Ingestion")
    print("   NO CHINESE ALLOWED - Enterprise Grade")
    print("=" * 60)

    # Check config
    if not all([QDRANT_URL, QDRANT_API_KEY, OPENAI_API_KEY]):
        print("❌ Missing configuration:")
        print(f"   QDRANT_URL: {'✓' if QDRANT_URL else '✗'}")
        print(f"   QDRANT_API_KEY: {'✓' if QDRANT_API_KEY else '✗'}")
        print(f"   OPENAI_API_KEY: {'✓' if OPENAI_API_KEY else '✗'}")
        return 1

    # Ingest English knowledge base
    guide_path = Path(__file__).parent.parent / "ENGLISH_KNOWLEDGE_BASE.md"

    if not guide_path.exists():
        print(f"❌ Guide not found: {guide_path}")
        return 1

    try:
        success = ingest_guide(str(guide_path))

        if not success:
            return 1

        print("\n" + "=" * 60)
        print("✅ ENGLISH-ONLY KNOWLEDGE BASE READY!")
        print("=" * 60)
        print("\nAI Agent now knows (English only):")
        print("  ✓ How to create YAML workflows")
        print("  ✓ How to add atomic modules")
        print("  ✓ Project architecture")
        print("  ✓ Module catalog (120+ modules)")
        print("  ✓ Common patterns")
        print("  ✓ Troubleshooting")
        print("\n  NO CHINESE - Enterprise Grade ✅")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
