#!/usr/bin/env python3
"""
Reset Qdrant Collection
Delete old data and recreate a clean collection
"""
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType

load_dotenv()

print("=" * 80)
print("Reset Qdrant Collection")
print("=" * 80)

# Connect to Qdrant (cloud only - local Qdrant is NOT supported)
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")

if not qdrant_url:
    print("❌ ERROR: QDRANT_URL environment variable is required!")
    print("   Local Qdrant is NOT supported. Please set up cloud Qdrant.")
    print("   Run: python scripts/setup_cloud_qdrant.py")
    exit(1)

if not qdrant_api_key:
    print("❌ ERROR: QDRANT_API_KEY environment variable is required!")
    exit(1)

client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

collection_name = "flyto2_memory"

# Step 1: Delete old collection
print(f"\n[1] Deleting old collection '{collection_name}'...")
try:
    client.delete_collection(collection_name)
    print("   Old collection deleted")
except Exception as e:
    print(f"   Warning: Delete failed (may not exist): {e}")

# Step 2: Create new collection with 768 dimensions
print(f"\n[2] Creating new collection (768 dimensions)...")
try:
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE)
    )
    print("   New collection created successfully")
except Exception as e:
    print(f"   Error: Create failed: {e}")
    exit(1)

# Step 3: Create payload indexes
print(f"\n[3] Creating Payload Indexes...")

indexes = [
    ("metadata.user_id", "User ID"),
    ("metadata.type", "Content type"),
    ("metadata.project", "Project"),
    ("metadata.timestamp", "Timestamp")
]

for field_name, description in indexes:
    try:
        client.create_payload_index(
            collection_name=collection_name,
            field_name=field_name,
            field_schema=PayloadSchemaType.KEYWORD
        )
        print(f"   {field_name} ({description}) index created")
    except Exception as e:
        print(f"   Warning: {field_name} index creation failed: {e}")

# Step 4: Verify
print(f"\n[4] Verifying Collection...")
collection_info = client.get_collection(collection_name)
print(f"   Collection: {collection_name}")
print(f"   Vector size: {collection_info.config.params.vectors.size}")
print(f"   Distance: {collection_info.config.params.vectors.distance}")
print(f"   Points count: {collection_info.points_count}")
print(f"   Indexed fields: {list(collection_info.payload_schema.keys())}")

print("\n" + "=" * 80)
print("Collection reset complete!")
print("=" * 80)
