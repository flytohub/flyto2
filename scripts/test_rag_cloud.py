#!/usr/bin/env python3
"""
Test RAG with Cloud Qdrant - English Only
"""
import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from src.core.modules.atomic.vector import close_global_connector, get_connector
from src.core.modules.atomic.vector.knowledge_store import KnowledgeStore

async def main():
    print("=" * 60)
    print("🔍 Testing RAG with Cloud Qdrant (English Only)")
    print("=" * 60)

    # Close any existing connector
    close_global_connector()

    # Get env vars
    qdrant_url = os.getenv('QDRANT_URL')
    qdrant_api_key = os.getenv('QDRANT_API_KEY')
    openai_api_key = os.getenv('OPENAI_API_KEY')

    print(f'\n📋 Configuration:')
    print(f'   QDRANT_URL: {qdrant_url[:50] if qdrant_url else "NOT SET"}...')
    print(f'   QDRANT_API_KEY: {"SET" if qdrant_api_key else "NOT SET"}')
    print(f'   OPENAI_API_KEY: {"SET" if openai_api_key else "NOT SET"}')

    if not all([qdrant_url, qdrant_api_key, openai_api_key]):
        print('\n❌ Missing configuration!')
        return 1

    # Create connector
    print(f'\n🔗 Connecting to Cloud Qdrant...')
    connector = get_connector(mode='cloud', url=qdrant_url, api_key=qdrant_api_key)

    print(f'   Connected: {connector.is_connected()}')

    stats = connector.get_stats()
    print(f'   Collections: {stats.get("collections", [])}')

    # Create knowledge store
    print(f'\n📚 Creating Knowledge Store...')
    store = KnowledgeStore(
        connector=connector,
        collection_name='flyto2_knowledge',
        embedding_provider='openai'
    )

    store_stats = store.get_stats()
    print(f'   Collection: {store_stats.get("collection")}')
    print(f'   Total entries: {store_stats.get("total_entries")}')
    print(f'   Embedding: {store_stats.get("embedding_model")}')

    # Test search
    print(f'\n🔍 Testing Search...')
    queries = [
        "How to create YAML workflow?",
        "What atomic modules are available?",
        "How to add a new module?"
    ]

    for query in queries:
        print(f'\n   Query: "{query}"')
        results = store.search(query=query, top_k=2)

        if results:
            for i, r in enumerate(results, 1):
                print(f'      {i}. Score: {r["score"]:.3f} | Lang: {r["metadata"].get("language", "N/A")} | Cat: {r["metadata"].get("category", "N/A")}')
                print(f'         {r["content"][:80]}...')
        else:
            print(f'      No results')

    print("\n" + "=" * 60)
    print("✅ RAG Test Complete!")
    print("=" * 60)

    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
