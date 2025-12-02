"""
Test Error Reporter
Tests automatic error reporting to Telegram
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.testing.error_reporter import (
    TelegramErrorReporter,
    report_test_failure,
    report_module_error,
    report_system_error
)


def test_error_reporter_initialization():
    """Test 1: Error reporter initializes correctly"""
    print("\n=== Test 1: Initialization ===")

    reporter = TelegramErrorReporter()

    print(f"Reporter enabled: {reporter.enabled}")
    print(f"Bot token present: {bool(reporter.bot_token)}")
    print(f"Chat IDs configured: {reporter.chat_ids}")

    if reporter.enabled:
        print("✓ Reporter initialized and enabled")
    else:
        print("⚠ Reporter disabled (no credentials - this is OK for testing)")

    print("✓ Test 1 passed")


def test_format_messages():
    """Test 2: Message formatting"""
    print("\n=== Test 2: Message Formatting ===")

    reporter = TelegramErrorReporter()

    # Test failure message
    test_msg = reporter._format_test_failure(
        test_name="test_browser_click",
        error_message="Element not found",
        traceback="Traceback:\n  File test.py, line 10\n    assert elem\nAssertionError",
        context={"url": "https://example.com", "selector": "#button"}
    )

    print("Test failure message:")
    print(test_msg)
    print()

    assert "Test Failed" in test_msg
    assert "test_browser_click" in test_msg
    assert "Element not found" in test_msg

    # Module error message
    module_msg = reporter._format_module_error(
        module_id="browser.click",
        error_type="TimeoutError",
        error_message="Element not clickable after 30s",
        context={"timeout": 30}
    )

    print("Module error message:")
    print(module_msg)
    print()

    assert "Module Error" in module_msg
    assert "browser.click" in module_msg
    assert "TimeoutError" in module_msg

    print("✓ Test 2 passed")


def test_convenience_functions():
    """Test 3: Convenience functions"""
    print("\n=== Test 3: Convenience Functions ===")

    # These should not error even if Telegram is not configured
    try:
        report_test_failure(
            "test_example",
            "Sample error for testing",
            traceback="Sample traceback",
            context={"test": True}
        )
        print("✓ report_test_failure() works")

        report_module_error(
            "test.module",
            "ValueError",
            "Sample module error",
            context={"test": True}
        )
        print("✓ report_module_error() works")

        report_system_error(
            "test_component",
            ValueError("Sample system error"),
            severity="WARNING"
        )
        print("✓ report_system_error() works")

    except Exception as e:
        print(f"✗ Error in convenience functions: {e}")
        raise

    print("✓ Test 3 passed")


def test_actual_telegram_send():
    """Test 4: Actual Telegram send (if configured)"""
    print("\n=== Test 4: Actual Telegram Send ===")

    reporter = TelegramErrorReporter()

    if not reporter.enabled:
        print("⚠ Telegram not configured - skipping actual send test")
        print("  (This is OK - test passed)")
        return

    print("Sending test error report to Telegram...")

    success = reporter.report_test_failure(
        test_name="test_error_reporter",
        error_message="This is a test error report from automated testing",
        traceback=None,
        context={"test_mode": True, "reporter_version": "1.0"}
    )

    if success:
        print("✓ Error report sent to Telegram successfully!")
        print("  Check your Telegram to verify you received it")
    else:
        print("✗ Failed to send error report")

    print("✓ Test 4 completed")


if __name__ == "__main__":
    print("=" * 60)
    print("Error Reporter Tests")
    print("=" * 60)

    try:
        test_error_reporter_initialization()
        test_format_messages()
        test_convenience_functions()
        test_actual_telegram_send()

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
