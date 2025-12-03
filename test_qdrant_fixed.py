"""Test Qdrant connection after fix"""
import asyncio
from src.core.modules.atomic.vector.connector import VectorDBConnector

async def test_query():
    """Test querying knowledge base"""
    from src.core.executor.smart_executor import SmartExecutor

    print("=" * 80)
    print("🧪 TESTING QDRANT CONNECTION AFTER FIX")
    print("=" * 80)

    # Test 1: Direct connector test
    print("\n1️⃣ Testing direct VectorDBConnector...")
    connector = VectorDBConnector()
    print(f"   Mode: {connector.mode}")
    print(f"   URL configured: {connector.url is not None}")

    try:
        result = connector.connect()
        print(f"   ✅ Connection successful!")
        collections = connector.client.get_collections()
        print(f"   ✅ Found {len(collections.collections)} collections")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return

    # Test 2: Query knowledge base through SmartExecutor
    print("\n2️⃣ Testing knowledge base query via SmartExecutor...")
    executor = SmartExecutor()

    try:
        # This method internally creates VectorDBConnector and queries
        kb_result = await executor._query_knowledge_base("How to create image module?")
        print(f"   ✅ Knowledge base query successful!")
        print(f"   Result length: {len(str(kb_result)) if kb_result else 0}")
    except Exception as e:
        print(f"   ❌ Knowledge base query failed: {e}")
        return

    print("\n" + "=" * 80)
    print("🎉 ALL TESTS PASSED - QDRANT IS FULLY WORKING!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_query())
