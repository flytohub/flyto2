#!/usr/bin/env python3
"""
Check Qdrant Vector Database Status

Verifies:
1. Qdrant connection
2. Collections exist
3. Data count in each collection
4. Sample queries
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.modules.atomic.vector import VectorDBConnector, KnowledgeStore, KnowledgeSearch


async def check_qdrant():
    """Check Qdrant connection and data"""

    print("🔍 Checking Qdrant Vector Database Status")
    print("=" * 60)

    try:
        # 1. Connect to Qdrant
        print("\n1️⃣ Connecting to Qdrant...")
        connector = VectorDBConnector(mode="local")
        connector.connect()

        if connector.is_connected():
            print("   ✅ Connected to Qdrant (local mode)")
            print(f"   📁 Storage: {connector.path}")
        else:
            print("   ❌ Failed to connect to Qdrant")
            return False

        # 2. List all collections (using client directly)
        print("\n2️⃣ Listing collections...")
        collections_response = connector.client.get_collections()
        collections = [coll.name for coll in collections_response.collections]

        if not collections:
            print("   ⚠️ No collections found")
            print("   💡 Run: python3 scripts/sync_to_vector_db.py")
            return False

        print(f"   ✅ Found {len(collections)} collection(s):")
        for coll in collections:
            print(f"      - {coll}")

        # 3. Check each collection
        print("\n3️⃣ Checking collection data...")

        for collection_name in collections:
            try:
                # Get collection info
                info = connector.client.get_collection(collection_name)
                count = info.points_count

                print(f"\n   📦 Collection: {collection_name}")
                print(f"      Points: {count}")
                print(f"      Vector size: {info.config.params.vectors.size}")

                if count == 0:
                    print(f"      ⚠️ Empty collection")
                    continue

                # Try a sample search
                store = KnowledgeStore(
                    connector=connector,
                    collection_name=collection_name,
                    embedding_provider="local"
                )

                search = KnowledgeSearch(knowledge_store=store)
                results = search.search(query="Ollama", top_k=3)

                if results:
                    print(f"      ✅ Sample search returned {len(results)} results")
                    print(f"      Top result:")
                    top = results[0]
                    content = top.get("content", "")[:100]
                    score = top.get("score", 0)
                    metadata = top.get("metadata", {})
                    print(f"         Score: {score:.4f}")
                    print(f"         Category: {metadata.get('category', 'N/A')}")
                    print(f"         Content: {content}...")
                else:
                    print(f"      ⚠️ Sample search returned no results")

            except Exception as e:
                print(f"      ❌ Error checking collection: {e}")

        # 4. Test specific queries
        print("\n4️⃣ Testing specific queries...")

        test_queries = [
            "Ollama dependency",
            "Perfect Flow Bot",
            "AI Error Solver",
            "atomic modules",
            "test results",
        ]

        # Use first collection for queries
        target_collection = collections[0]
        print(f"   Using collection: {target_collection}\n")

        for query in test_queries:
            try:
                store = KnowledgeStore(
                    connector=connector,
                    collection_name=target_collection,
                    embedding_provider="local"
                )
                search = KnowledgeSearch(knowledge_store=store)
                results = search.search(query=query, top_k=1)

                if results:
                    score = results[0].get("score", 0)
                    category = results[0].get("metadata", {}).get("category", "N/A")
                    print(f"   ✅ '{query}': Found (score: {score:.4f}, category: {category})")
                else:
                    print(f"   ⚠️ '{query}': No results")

            except Exception as e:
                print(f"   ❌ '{query}': Error - {e}")

        # 5. Show detailed data samples
        print("\n5️⃣ Sample stored data...")

        try:
            store = KnowledgeStore(
                connector=connector,
                collection_name=target_collection,
                embedding_provider="local"
            )
            search = KnowledgeSearch(knowledge_store=store)
            results = search.search(query="project status", top_k=3)

            for i, result in enumerate(results, 1):
                metadata = result.get("metadata", {})
                content = result.get("content", "")
                print(f"\n   [{i}] Category: {metadata.get('category', 'N/A')}")
                print(f"       Type: {metadata.get('type', 'N/A')}")
                print(f"       Score: {result.get('score', 0):.4f}")
                print(f"       Content preview: {content[:150]}...")

        except Exception as e:
            print(f"   ❌ Error getting samples: {e}")

        # Summary
        print("\n" + "=" * 60)
        print("✅ Qdrant Status Check Complete!")
        print(f"\n📊 Summary:")
        print(f"   - Collections: {len(collections)}")
        for coll in collections:
            info = connector.client.get_collection(coll)
            print(f"   - {coll}: {info.points_count} points")
        print(f"\n📁 Storage location: {connector.path}")
        print(f"🔧 Mode: Local (embedded)")

        connector.disconnect()
        return True

    except Exception as e:
        print(f"\n❌ Error checking Qdrant: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    success = await check_qdrant()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
