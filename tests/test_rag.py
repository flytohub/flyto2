"""
Test RAG (Retrieval-Augmented Generation)
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.modules.atomic.vector import (
    VectorDBConnector,
    KnowledgeStore,
    ExperienceArchiver,
    RAGRetriever,
    RAGFormatter,
    RAGPipeline
)


def setup_test_knowledge():
    """Setup test knowledge base"""
    connector = VectorDBConnector(mode="local", path="./test_qdrant")
    connector.connect()

    store = KnowledgeStore(
        connector=connector,
        collection_name="test_rag",
        embedding_provider="local"
    )

    archiver = ExperienceArchiver(store)

    # Add test experiences
    archiver.archive_error(
        module_id="browser.click",
        error_type="TimeoutError",
        error_message="Element not found within timeout",
        solution="Increase timeout to 60 seconds or use explicit wait"
    )

    archiver.archive_success_pattern(
        strategy_name="wait_before_action",
        success_rate=95.0,
        description="Wait 2 seconds before performing action to ensure page stability",
        use_cases=["dynamic_content", "ajax_loaded"]
    )

    archiver.archive_practice_result(
        website="https://example.com",
        result={
            "status": "success",
            "steps": ["navigate", "extract", "validate"],
            "duration": 10.5
        },
        analysis="Successfully extracted product data using CSS selectors"
    )

    archiver.archive_module_improvement(
        module_id="browser.extract",
        version="2.1.0",
        changes="Added support for nested selectors and regex patterns",
        impact="Enables extracting complex nested data structures"
    )

    return connector, store


def test_rag_retrieval():
    """Test RAG retrieval"""
    print("\n=== Test: RAG Retrieval ===")

    connector, store = setup_test_knowledge()
    retriever = RAGRetriever(store)

    # Test 1: Retrieve for module proposal
    results = retriever.retrieve_for_module_proposal(
        proposed_module="browser.smart_click",
        description="Click with automatic retry and wait",
        top_k=3
    )
    print(f"✓ Module proposal retrieval: {len(results)} results")

    # Test 2: Retrieve for error analysis
    results = retriever.retrieve_for_error_analysis(
        module_id="browser.click",
        error_message="timeout waiting for element",
        top_k=3
    )
    print(f"✓ Error analysis retrieval: {len(results)} results")
    if results:
        print(f"  → Best match: {results[0]['content'][:60]}...")
        print(f"    Score: {results[0]['score']:.3f}")

    # Test 3: Retrieve for optimization
    results = retriever.retrieve_for_optimization(
        optimization_target="page load speed",
        context="reduce wait times",
        top_k=3
    )
    print(f"✓ Optimization retrieval: {len(results)} results")

    # Test 4: Retrieve for website practice
    results = retriever.retrieve_for_website_practice(
        website="example.com",
        task="extract product information",
        top_k=3
    )
    print(f"✓ Website practice retrieval: {len(results)} results")

    # Test 5: Multi-category retrieval
    results = retriever.retrieve_multi_category(
        query="browser automation techniques",
        categories=["error", "success", "module"],
        top_k_per_category=2
    )
    print(f"✓ Multi-category retrieval: {len(results)} categories")
    for category, items in results.items():
        print(f"  - {category}: {len(items)} results")

    connector.disconnect()
    return True


def test_rag_formatting():
    """Test RAG formatting"""
    print("\n=== Test: RAG Formatting ===")

    connector, store = setup_test_knowledge()
    formatter = RAGFormatter()

    # Get some test memories
    results = store.search("browser click timeout", top_k=2)

    # Test 1: Markdown format
    markdown = formatter.format_for_prompt(results, format_style="markdown")
    print("✓ Markdown formatting:")
    print(markdown[:200] + "...")

    # Test 2: Text format
    text = formatter.format_for_prompt(results, format_style="text")
    print("\n✓ Text formatting:")
    print(text[:150] + "...")

    # Test 3: JSON format
    json_str = formatter.format_for_prompt(results, format_style="json")
    print(f"\n✓ JSON formatting: {len(json_str)} characters")

    connector.disconnect()
    return True


def test_rag_pipeline():
    """Test complete RAG pipeline"""
    print("\n=== Test: RAG Pipeline ===")

    connector, store = setup_test_knowledge()
    pipeline = RAGPipeline(store)

    # Test 1: Augment context for error
    context = pipeline.augment_context(
        query="browser.click: timeout error",
        context_type="error",
        top_k=2
    )
    print("✓ Error context augmentation:")
    print(context[:200] + "...")

    # Test 2: Build augmented prompt
    base_prompt = "How can I fix this timeout issue in browser.click?"
    augmented = pipeline.build_augmented_prompt(
        base_prompt=base_prompt,
        query="browser.click timeout",
        context_type="error",
        top_k=2
    )
    print(f"\n✓ Augmented prompt built: {len(augmented)} characters")
    print("  First 150 chars:", augmented[:150] + "...")

    # Test 3: Generic context
    context = pipeline.augment_context(
        query="successful automation strategies",
        context_type="generic",
        top_k=3
    )
    print(f"\n✓ Generic context: {len(context)} characters")

    connector.disconnect()
    print("\n✓ All RAG pipeline tests passed!")
    return True


if __name__ == "__main__":
    try:
        test_rag_retrieval()
        test_rag_formatting()
        test_rag_pipeline()

        print("\n" + "=" * 60)
        print("✓ All RAG tests passed successfully!")
        print("=" * 60)
        sys.exit(0)

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
