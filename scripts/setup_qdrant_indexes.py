#!/usr/bin/env python3
"""
Setup Qdrant Collection with Enterprise-Grade Indexes

Creates proper indexes for metadata filtering in Qdrant Cloud
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType


def setup_collection():
    """Create or update collection with proper indexes"""

    print("🔧 Setting up Qdrant collection with indexes...")
    print()

    # Connect to cloud Qdrant
    client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )

    collection_name = "flyto2_knowledge"
    vector_size = 1536  # OpenAI/Ollama embedding size

    # Check if collection exists
    collections = client.get_collections()
    collection_exists = any(col.name == collection_name for col in collections.collections)

    if collection_exists:
        print(f"📦 Collection '{collection_name}' already exists")
        print("   Updating indexes...")
    else:
        print(f"📦 Creating collection '{collection_name}'...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )
        print("   ✓ Collection created")

    # Create payload indexes for all filter fields
    print()
    print("🔍 Creating payload indexes...")

    indexes = [
        ("metadata.source", PayloadSchemaType.KEYWORD),
        ("metadata.type", PayloadSchemaType.KEYWORD),
        ("metadata.category", PayloadSchemaType.KEYWORD),
        ("metadata.importance", PayloadSchemaType.KEYWORD),
        ("metadata.status", PayloadSchemaType.KEYWORD),
        ("metadata.doc_source", PayloadSchemaType.KEYWORD),
        ("metadata.section_title", PayloadSchemaType.TEXT),
    ]

    for field_name, schema_type in indexes:
        try:
            client.create_payload_index(
                collection_name=collection_name,
                field_name=field_name,
                field_schema=schema_type
            )
            print(f"   ✓ Created index: {field_name} ({schema_type})")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"   ✓ Index exists: {field_name}")
            else:
                print(f"   ⚠ Warning for {field_name}: {str(e)}")

    # Get collection info
    print()
    print("📊 Collection Status:")
    info = client.get_collection(collection_name)
    print(f"   Vectors: {info.points_count}")
    print(f"   Vector size: {info.config.params.vectors.size}")
    print(f"   Distance: {info.config.params.vectors.distance}")

    print()
    print("✅ Setup complete!")
    print()
    print("Next steps:")
    print("  1. Ingest documents: python scripts/ingest_implementation_guides.py")
    print("  2. Query knowledge: python scripts/ingest_implementation_guides.py --query 'your question'")


if __name__ == "__main__":
    try:
        setup_collection()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
