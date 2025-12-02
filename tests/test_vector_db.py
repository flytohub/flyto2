"""
Test Vector Database Functionality
Tests connector, embeddings, and knowledge store
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.modules.atomic.vector import (
    VectorDBConnector,
    EmbeddingGenerator,
    KnowledgeStore
)


def test_connector():
    """Test vector database connector"""
    print("\n=== Test 1: Vector DB Connector ===")

    connector = VectorDBConnector(mode="local", path="./test_qdrant")

    # Connect
    connected = connector.connect()
    print(f"✓ Connected: {connected}")

    # Get stats
    stats = connector.get_stats()
    print(f"✓ Stats: {stats}")

    # Get collections
    collections = connector.get_collections()
    print(f"✓ Collections: {collections}")

    connector.disconnect()
    print("✓ Disconnected")

    return connector


def test_embeddings():
    """Test embedding generation"""
    print("\n=== Test 2: Embedding Generation ===")

    generator = EmbeddingGenerator(provider="local")

    # Single text
    text = "This is a test of the embedding system"
    embedding = generator.generate(text)
    print(f"✓ Generated embedding: dimension={len(embedding)}")

    # Batch
    texts = [
        "First test sentence",
        "Second test sentence",
        "Third test sentence"
    ]
    embeddings = generator.generate_batch(texts)
    print(f"✓ Generated {len(embeddings)} embeddings")

    # Stats
    stats = generator.get_stats()
    print(f"✓ Stats: {stats}")

    return generator


def test_knowledge_store():
    """Test knowledge storage and retrieval"""
    print("\n=== Test 3: Knowledge Storage & Retrieval ===")

    # Setup
    connector = VectorDBConnector(mode="local", path="./test_qdrant")
    connector.connect()

    store = KnowledgeStore(
        connector=connector,
        collection_name="test_knowledge",
        embedding_provider="local"
    )

    # Store single entry
    entry_id = store.store(
        content="Flyto2 is a workflow automation engine",
        metadata={
            "category": "project_info",
            "source": "documentation"
        }
    )
    print(f"✓ Stored entry: {entry_id}")

    # Store batch
    entries = [
        {
            "content": "Python is the main programming language",
            "metadata": {"category": "technical", "topic": "language"}
        },
        {
            "content": "Qdrant is used for vector storage",
            "metadata": {"category": "technical", "topic": "database"}
        },
        {
            "content": "Atomic modules enable workflow composition",
            "metadata": {"category": "architecture", "topic": "design"}
        }
    ]
    ids = store.store_batch(entries)
    print(f"✓ Stored {len(ids)} entries in batch")

    # Search
    results = store.search("workflow automation", top_k=3)
    print(f"✓ Search results: {len(results)} found")
    for i, result in enumerate(results, 1):
        print(f"  {i}. Score: {result['score']:.3f} - {result['content'][:50]}...")

    # Search with filter
    filtered_results = store.search(
        "programming",
        top_k=2,
        filters={"category": "technical"}
    )
    print(f"✓ Filtered search: {len(filtered_results)} results")

    # List entries
    all_entries = store.list_entries(limit=10)
    print(f"✓ Listed {len(all_entries)} entries")

    # Update entry
    updated = store.update(
        entry_id=entry_id,
        metadata={"category": "project_info", "updated": True}
    )
    print(f"✓ Updated entry: {updated}")

    # Delete entry
    deleted = store.delete(entry_id)
    print(f"✓ Deleted entry: {deleted}")

    # Stats
    stats = store.get_stats()
    print(f"✓ Stats: {stats}")

    connector.disconnect()

    return store


def test_project_knowledge():
    """Test storing actual project knowledge"""
    print("\n=== Test 4: Store Project Knowledge ===")

    connector = VectorDBConnector(mode="local", path="./test_qdrant")
    connector.connect()

    store = KnowledgeStore(
        connector=connector,
        collection_name="flyto2_project",
        embedding_provider="local"
    )

    # Project knowledge entries
    project_knowledge = [
        {
            "content": "Flyto2 is an open-source workflow automation platform with YAML-based workflows and atomic module architecture",
            "metadata": {"category": "overview", "priority": "high"}
        },
        {
            "content": "Atomic modules are single-responsibility, independently testable components that can be combined into workflows",
            "metadata": {"category": "architecture", "concept": "atomic_modules"}
        },
        {
            "content": "The system supports three-tier LLM architecture: Ollama for local, OpenAI for complex tasks, and Human for decisions",
            "metadata": {"category": "ai", "concept": "three_tier"}
        },
        {
            "content": "Vector database integration uses Qdrant for knowledge storage with semantic search capabilities",
            "metadata": {"category": "features", "component": "vector_db"}
        },
        {
            "content": "Rate limiting is handled with exponential backoff and respects Retry-After headers",
            "metadata": {"category": "api", "module": "rate_limiter"}
        },
        {
            "content": "Competition system includes speed races, accuracy races, strategy comparisons, and stress testing",
            "metadata": {"category": "training", "system": "competition"}
        },
        {
            "content": "Proxy rotation supports round-robin, random, and least-used strategies for distributed requests",
            "metadata": {"category": "api", "module": "proxy_manager"}
        },
        {
            "content": "Anti-bot detection identifies captcha, cloudflare, and rate limiting with confidence scoring",
            "metadata": {"category": "api", "module": "anti_bot"}
        },
        {
            "content": "Headless browser management provides default, performance, and stealth modes with resource blocking",
            "metadata": {"category": "browser", "module": "headless_manager"}
        },
        {
            "content": "Connection pooling optimizes concurrent HTTP requests with configurable limits and keepalive",
            "metadata": {"category": "api", "module": "connection_pool"}
        }
    ]

    ids = store.store_batch(project_knowledge)
    print(f"✓ Stored {len(ids)} project knowledge entries")

    # Test semantic search
    queries = [
        "How does workflow automation work?",
        "What is the AI architecture?",
        "How to handle rate limits?",
        "Browser automation features?"
    ]

    for query in queries:
        results = store.search(query, top_k=2)
        print(f"\n  Query: '{query}'")
        if results:
            print(f"  → {results[0]['content'][:80]}...")
            print(f"    (score: {results[0]['score']:.3f})")

    connector.disconnect()
    print("\n✓ Project knowledge test complete")


def run_all_tests():
    """Run all vector database tests"""
    print("=" * 60)
    print("Vector Database Tests")
    print("=" * 60)

    try:
        test_connector()
        test_embeddings()
        test_knowledge_store()
        test_project_knowledge()

        print("\n" + "=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
