#!/usr/bin/env python3
"""
Quick Ingest - 快速將實現指南塞進 Qdrant
企業級多語言支持
"""
import os
import sys
from pathlib import Path
from typing import List, Dict
import asyncio

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from openai import OpenAI

# 配置
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COLLECTION_NAME = "flyto2_project_knowledge"

# OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def chunk_text(text: str, chunk_size: int = 1000) -> List[str]:
    """將文本切分成chunks"""
    # 按段落切分
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

def detect_language(text: str) -> str:
    """檢測文本語言 (企業級)"""
    # Count Chinese characters
    chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    total_chars = len(text.strip())

    if total_chars == 0:
        return "en"

    # If more than 20% are Chinese characters, mark as Chinese
    chinese_ratio = chinese_chars / total_chars
    if chinese_ratio > 0.2:
        return "zh"
    else:
        return "en"

def get_embedding(text: str) -> List[float]:
    """使用 OpenAI 生成 embedding"""
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def ingest_guide(guide_path: str):
    """Ingest 單一指南文件"""
    print(f"\n📖 Reading: {guide_path}")

    with open(guide_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 切分
    chunks = chunk_text(content)
    print(f"   Split into {len(chunks)} chunks")

    # 連接 Qdrant
    print(f"\n🔗 Connecting to Qdrant Cloud...")
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        timeout=30
    )

    # 確保 collection 存在
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

    for i, chunk in enumerate(chunks):
        print(f"   [{i+1}/{len(chunks)}] Generating embedding...", end='\r')

        # 檢測語言 (企業級)
        language = detect_language(chunk)

        # 生成 embedding
        vector = get_embedding(chunk)

        # 創建 point
        point = PointStruct(
            id=i + 1,
            vector=vector,
            payload={
                "content": chunk,
                "source": os.path.basename(guide_path),
                "chunk_id": i,
                "category": "implementation_guide",
                "language": language,  # 正確檢測: "zh" or "en"
                "importance": 1.0  # 高優先級知識
            }
        )
        points.append(point)

        # 批次上傳（每50個）
        if len(points) >= 50:
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
            points = []

    # 上傳剩餘的
    if points:
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )

    print(f"\n   ✅ Ingested {len(chunks)} chunks")

def main():
    print("=" * 60)
    print("🚀 Quick Ingest - Enterprise Knowledge Base")
    print("=" * 60)

    # 檢查配置
    if not all([QDRANT_URL, QDRANT_API_KEY, OPENAI_API_KEY]):
        print("❌ Missing configuration:")
        print(f"   QDRANT_URL: {'✓' if QDRANT_URL else '✗'}")
        print(f"   QDRANT_API_KEY: {'✓' if QDRANT_API_KEY else '✗'}")
        print(f"   OPENAI_API_KEY: {'✓' if OPENAI_API_KEY else '✗'}")
        return 1

    # Ingest 實現指南
    guide_path = Path(__file__).parent.parent / "IMPLEMENTATION_GUIDE_V4.md"

    if not guide_path.exists():
        print(f"❌ Guide not found: {guide_path}")
        return 1

    try:
        ingest_guide(str(guide_path))

        print("\n" + "=" * 60)
        print("✅ Ingest Complete!")
        print("=" * 60)
        print("\nAI Agent now knows:")
        print("  • How to create workflows (YAML)")
        print("  • How to add atomic modules")
        print("  • Project architecture")
        print("  • Evolution system usage")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
