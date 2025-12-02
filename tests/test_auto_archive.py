"""
Test Auto-Archive Functionality
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.modules.atomic.vector import (
    VectorDBConnector,
    KnowledgeStore,
    ExperienceArchiver,
    AutoArchiveTrigger
)


def test_auto_archive():
    """Test experience auto-archiving"""
    print("\n=== Test: Experience Auto-Archiving ===")

    # Setup
    connector = VectorDBConnector(mode="local", path="./test_qdrant")
    connector.connect()

    store = KnowledgeStore(
        connector=connector,
        collection_name="test_auto_archive",
        embedding_provider="local"
    )

    archiver = ExperienceArchiver(store)

    # Test 1: Archive practice result
    practice_result = {
        "status": "success",
        "steps": ["step1", "step2", "step3"],
        "duration": 12.5,
        "errors": []
    }

    id1 = archiver.archive_practice_result(
        website="https://example.com",
        result=practice_result,
        analysis="Successfully extracted data from example.com"
    )
    print(f"✓ Archived practice result: {id1}")

    # Test 2: Archive speed race
    race_result = {
        "rounds": 5,
        "stats": {
            "best_time": 8.2,
            "avg_time": 9.5,
            "success_rate": 100.0
        }
    }

    id2 = archiver.archive_speed_race(
        task_name="fetch_products",
        race_result=race_result
    )
    print(f"✓ Archived speed race: {id2}")

    # Test 3: Archive error
    id3 = archiver.archive_error(
        module_id="browser.click",
        error_type="TimeoutError",
        error_message="Element not found within timeout",
        context={"selector": "#submit-btn", "timeout": 30},
        solution="Increase timeout to 60 seconds"
    )
    print(f"✓ Archived error: {id3}")

    # Test 4: Archive success pattern
    id4 = archiver.archive_success_pattern(
        strategy_name="wait_before_click",
        success_rate=95.5,
        description="Wait 2 seconds before clicking to ensure element is ready",
        use_cases=["dynamic_content", "ajax_loaded_elements"]
    )
    print(f"✓ Archived success pattern: {id4}")

    # Test 5: Archive module improvement
    id5 = archiver.archive_module_improvement(
        module_id="browser.extract",
        version="2.1.0",
        changes="Added support for nested selectors",
        impact="Enables extracting deeply nested data structures"
    )
    print(f"✓ Archived module improvement: {id5}")

    # Test 6: Search archived experiences
    results = store.search("timeout error", top_k=2)
    print(f"\n✓ Search 'timeout error': {len(results)} results")
    if results:
        print(f"  → {results[0]['content'][:80]}...")
        print(f"    Score: {results[0]['score']:.3f}")

    # Test 7: Auto-archive trigger
    trigger = AutoArchiveTrigger(archiver)

    trigger.on_practice_complete(
        website="https://test.com",
        result=practice_result
    )
    print("\n✓ Auto-trigger on practice complete")

    trigger.on_module_error(
        module_id="test.module",
        error=ValueError("Test error")
    )
    print("✓ Auto-trigger on module error")

    # Stats
    stats = archiver.get_archive_stats()
    print(f"\n✓ Archive stats: {stats['total_archived']} entries")

    connector.disconnect()
    print("\n✓ All auto-archive tests passed!")
    return True


if __name__ == "__main__":
    try:
        test_auto_archive()
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
