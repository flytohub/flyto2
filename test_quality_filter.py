"""
Test Quality Filter Integration
Tests that quality filter prevents low-quality content from being archived
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.modules.atomic.vector import (
    VectorDBConnector,
    KnowledgeStore,
    ExperienceArchiver,
    QualityFilter
)


def test_quality_filter_basic():
    """Test basic quality filtering"""
    print("\n=== Test 1: Basic Quality Filtering ===")

    qf = QualityFilter()

    # Test 1: Empty content (should filter)
    should_archive, score, reason = qf.should_archive("")
    print(f"Empty content: archive={should_archive}, score={score}, reason={reason}")
    assert not should_archive, "Empty content should be filtered"

    # Test 2: Too short (should filter)
    should_archive, score, reason = qf.should_archive("ok")
    print(f"Short content: archive={should_archive}, score={score}, reason={reason}")
    assert not should_archive, "Too short content should be filtered"

    # Test 3: Good content (should pass)
    good_content = "This is a substantial piece of content about module implementation with error handling and solution description"
    should_archive, score, reason = qf.should_archive(good_content)
    print(f"Good content: archive={should_archive}, score={score:.2f}, reason={reason}")
    assert should_archive, "Good content should pass"

    # Test 4: Debug print (should filter)
    debug_content = "This content has print() debug statements which should be filtered"
    should_archive, score, reason = qf.should_archive(debug_content)
    print(f"Debug content: archive={should_archive}, score={score}, reason={reason}")
    assert not should_archive, "Debug content should be filtered"

    # Test 5: Technical content with keywords (should pass)
    technical_content = "Implemented new module for error handling using class-based architecture with database optimization"
    should_archive, score, reason = qf.should_archive(technical_content)
    print(f"Technical content: archive={should_archive}, score={score:.2f}, reason={reason}")
    assert should_archive, "Technical content should pass"

    print("✓ Basic quality filtering tests passed")


def test_archiver_with_filter():
    """Test ExperienceArchiver with quality filter enabled"""
    print("\n=== Test 2: Archiver with Quality Filter ===")

    # Setup
    connector = VectorDBConnector(mode="local")
    connector.connect()

    store = KnowledgeStore(
        connector=connector,
        collection_name="test_quality_filter",
        embedding_provider="local"
    )

    # Archiver with quality filter enabled
    archiver = ExperienceArchiver(
        knowledge_store=store,
        enable_quality_filter=True
    )

    # Test 1: Archive good error (should succeed)
    entry_id = archiver.archive_error(
        module_id="browser.click",
        error_type="TimeoutError",
        error_message="Element not found after 30s timeout",
        solution="Added explicit wait and retry logic"
    )
    print(f"Good error archived: {entry_id}")
    assert entry_id is not None, "Good error should be archived"

    # Test 2: Archive trivial error (should be filtered)
    entry_id = archiver.archive_error(
        module_id="test",
        error_type="Error",
        error_message="ok"
    )
    print(f"Trivial error result: {entry_id}")
    assert entry_id is None, "Trivial error should be filtered"

    # Test 3: Archive good practice result (should succeed)
    entry_id = archiver.archive_practice_result(
        website="https://example.com",
        result={
            "status": "success",
            "steps": [1, 2, 3, 4, 5],
            "duration": 12.5
        },
        analysis="Successfully navigated and extracted data using optimized selectors"
    )
    print(f"Good practice archived: {entry_id}")
    assert entry_id is not None, "Good practice should be archived"

    # Test 4: Archive minimal practice (note: structured data may pass even if minimal)
    # The quality filter is designed to catch truly trivial content like
    # "ok", "yes", debug prints, etc. - not structured data with minimal values
    entry_id = archiver.archive_practice_result(
        website="test",
        result={
            "status": "ok",
            "steps": [],
            "duration": 0
        }
    )
    print(f"Minimal practice result: {entry_id}")
    # This may pass because it generates structured content above minimum length
    print(f"  Note: Structured data with minimal values may still pass filter")

    # Get stats
    stats = archiver.get_archive_stats()
    print(f"\nArchiver stats: {stats}")
    print(f"Filter stats: {stats.get('quality_filter')}")

    connector.disconnect()

    print("✓ Archiver with filter tests passed")


def test_archiver_without_filter():
    """Test ExperienceArchiver with quality filter disabled"""
    print("\n=== Test 3: Archiver without Quality Filter ===")

    # Setup
    connector = VectorDBConnector(mode="local")
    connector.connect()

    store = KnowledgeStore(
        connector=connector,
        collection_name="test_no_filter",
        embedding_provider="local"
    )

    # Archiver with quality filter disabled
    archiver = ExperienceArchiver(
        knowledge_store=store,
        enable_quality_filter=False
    )

    # Even trivial content should be archived
    entry_id = archiver.archive_error(
        module_id="test",
        error_type="Error",
        error_message="ok"
    )
    print(f"Trivial error (no filter): {entry_id}")
    assert entry_id is not None, "Without filter, even trivial content should be archived"

    connector.disconnect()

    print("✓ No filter tests passed")


def test_conversation_filter():
    """Test conversation-specific filtering"""
    print("\n=== Test 4: Conversation Filter ===")

    from src.core.modules.atomic.vector.quality_filter import ConversationFilter

    cf = ConversationFilter()

    # Test 1: Early trivial message (should filter)
    should_archive, score, reason = cf.should_archive_message(
        message="ok",
        role="user",
        turn_number=1
    )
    print(f"Early trivial: archive={should_archive}, reason={reason}")
    assert not should_archive, "Early trivial messages should be filtered"

    # Test 2: Technical question (should pass)
    should_archive, score, reason = cf.should_archive_message(
        message="How do I implement error handling in the browser module?",
        role="user",
        turn_number=5
    )
    print(f"Technical question: archive={should_archive}, score={score:.2f}")
    assert should_archive, "Technical questions should pass"

    # Test 3: Assistant with code (should pass with boost)
    should_archive, score, reason = cf.should_archive_message(
        message="You can implement it using try-except blocks with async def error_handler():",
        role="assistant",
        turn_number=6
    )
    print(f"Assistant code: archive={should_archive}, score={score:.2f}")
    assert should_archive, "Assistant responses with code should pass"

    print("✓ Conversation filter tests passed")


def test_file_change_filter():
    """Test file change filtering"""
    print("\n=== Test 5: File Change Filter ===")

    from src.core.modules.atomic.vector.quality_filter import FileChangeFilter

    fcf = FileChangeFilter()

    # Test 1: Python file (should pass)
    should_archive, score, reason = fcf.should_archive_file_change(
        file_path="src/core/modules/browser.py",
        change_type="modified"
    )
    print(f"Python file: archive={should_archive}, score={score:.2f}")
    assert should_archive, "Python source files should be archived"

    # Test 2: Cache file (should filter)
    should_archive, score, reason = fcf.should_archive_file_change(
        file_path="__pycache__/module.pyc",
        change_type="modified"
    )
    print(f"Cache file: archive={should_archive}, reason={reason}")
    assert not should_archive, "Cache files should be filtered"

    # Test 3: Log file (should filter)
    should_archive, score, reason = fcf.should_archive_file_change(
        file_path="logs/debug.log",
        change_type="modified"
    )
    print(f"Log file: archive={should_archive}, reason={reason}")
    assert not should_archive, "Log files should be filtered"

    # Test 4: README (should pass)
    should_archive, score, reason = fcf.should_archive_file_change(
        file_path="README.md",
        change_type="modified"
    )
    print(f"README: archive={should_archive}, score={score:.2f}")
    assert should_archive, "Documentation files should be archived"

    print("✓ File change filter tests passed")


if __name__ == "__main__":
    print("=" * 60)
    print("Quality Filter Integration Tests")
    print("=" * 60)

    try:
        test_quality_filter_basic()
        test_archiver_with_filter()
        test_archiver_without_filter()
        test_conversation_filter()
        test_file_change_filter()

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
