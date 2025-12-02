#!/usr/bin/env python3
"""
清空雲端 Qdrant - NO CHINESE ALLOWED
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from qdrant_client import QdrantClient

QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')

def main():
    print("=" * 60)
    print("🗑️  CLEARING CLOUD QDRANT - NO CHINESE ALLOWED")
    print("=" * 60)

    if not QDRANT_URL or not QDRANT_API_KEY:
        print("❌ Missing Qdrant config!")
        return 1

    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=30)

        # List all collections
        collections = client.get_collections().collections
        print(f'\n📋 Found {len(collections)} collections:')
        for c in collections:
            print(f'   - {c.name}')

        # Delete all collections
        for c in collections:
            print(f'\n🗑️  Deleting: {c.name}')
            client.delete_collection(c.name)
            print(f'   ✅ Deleted')

        print("\n" + "=" * 60)
        print("✅ CLOUD QDRANT CLEANED - Ready for English-only data")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
