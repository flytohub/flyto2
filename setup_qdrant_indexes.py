#!/usr/bin/env python3
"""
Setup Qdrant Collection Payload Indexes
For supporting metadata filtering
"""
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PayloadSchemaType

# Load environment variables
load_dotenv()

print("=" * 80)
print("Qdrant Payload Index Setup")
print("=" * 80)

# Connect to Qdrant (cloud only - local Qdrant is NOT supported)
print("\n[1] Connecting to cloud Qdrant...")
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

print(f"   URL: {qdrant_url}")
print("   Connected successfully")

# Collection name
collection_name = "flyto2_memory"

# Check collection exists
print(f"\n[2] Checking collection '{collection_name}'...")
try:
    collection_info = client.get_collection(collection_name)
    print(f"   Collection exists")
    print(f"   Points count: {collection_info.points_count}")
except Exception as e:
    print(f"   Error: Collection does not exist: {e}")
    exit(1)

# Create payload indexes
print(f"\n[3] Creating Payload Indexes...")

# Index for metadata.user_id (keyword)
print("   [3a] Creating metadata.user_id (keyword) index...")
try:
    client.create_payload_index(
        collection_name=collection_name,
        field_name="metadata.user_id",
        field_schema=PayloadSchemaType.KEYWORD
    )
    print("   metadata.user_id index created")
except Exception as e:
    print(f"   Warning: Index may already exist or creation failed: {e}")

# Index for metadata.type (keyword)
print("   [3b] Creating metadata.type (keyword) index...")
try:
    client.create_payload_index(
        collection_name=collection_name,
        field_name="metadata.type",
        field_schema=PayloadSchemaType.KEYWORD
    )
    print("   metadata.type index created")
except Exception as e:
    print(f"   Warning: Index may already exist or creation failed: {e}")

# Index for metadata.project (keyword)
print("   [3c] Creating metadata.project (keyword) index...")
try:
    client.create_payload_index(
        collection_name=collection_name,
        field_name="metadata.project",
        field_schema=PayloadSchemaType.KEYWORD
    )
    print("   metadata.project index created")
except Exception as e:
    print(f"   Warning: Index may already exist or creation failed: {e}")

# Index for metadata.timestamp (keyword or text)
print("   [3d] Creating metadata.timestamp (keyword) index...")
try:
    client.create_payload_index(
        collection_name=collection_name,
        field_name="metadata.timestamp",
        field_schema=PayloadSchemaType.KEYWORD
    )
    print("   metadata.timestamp index created")
except Exception as e:
    print(f"   Warning: Index may already exist or creation failed: {e}")

# Verify indexes
print(f"\n[4] Verifying Indexes...")
try:
    collection_info = client.get_collection(collection_name)
    print("   Collection info:")
    print(f"   Indexed fields: {list(collection_info.payload_schema.keys())}")
except Exception as e:
    print(f"   Warning: Unable to get collection info: {e}")

print("\n" + "=" * 80)
print("Payload Indexes setup complete!")
print("=" * 80)
print("\nYou can now use metadata filtering:")
print("   - metadata.user_id")
print("   - metadata.type")
print("   - metadata.project")
print("   - metadata.timestamp")
print("\nPlease run the test script again to verify functionality.")
