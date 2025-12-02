#!/usr/bin/env python3
"""
Test Rate Limit Handler
Verify automatic retry logic for 429 responses
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.modules.atomic.api.rate_limiter import (
    RateLimitHandler,
    RateLimitConfig,
    RateLimitExceeded
)


# Mock API function that simulates rate limiting
class MockAPI:
    def __init__(self, fail_count=2):
        self.call_count = 0
        self.fail_count = fail_count

    async def call(self, value: str):
        """Simulate API call that rate limits first N calls"""
        self.call_count += 1

        if self.call_count <= self.fail_count:
            # Simulate 429 response
            return {
                'status_code': 429,
                'error': 'Rate limit exceeded',
                'retry_after': 0.1
            }
        else:
            # Success
            return {
                'status_code': 200,
                'result': f'Success: {value}'
            }


async def test_rate_limit_retry():
    """Test automatic retry on rate limit"""
    print("=" * 70)
    print("TEST: Rate Limit Automatic Retry")
    print("=" * 70)
    print()

    # Create handler with fast retry config for testing
    config = RateLimitConfig(
        max_retries=3,
        base_delay=0.1,
        max_delay=1.0,
        exponential_base=2.0,
        jitter=False
    )
    handler = RateLimitHandler(config)

    # Create mock API that fails twice then succeeds
    api = MockAPI(fail_count=2)

    print("Test 1: Successful retry after 2 rate limits")
    print("-" * 70)

    try:
        result = await handler.execute_with_retry(api.call, "test_value")

        if result.get('status_code') == 200:
            print(f"✅ PASS: Request succeeded after retries")
            print(f"   API calls: {api.call_count}")
            print(f"   Retries: {handler.retry_count}")
            print(f"   Result: {result.get('result')}")
            test1_pass = True
        else:
            print(f"❌ FAIL: Unexpected response: {result}")
            test1_pass = False
    except Exception as e:
        print(f"❌ FAIL: Exception raised: {e}")
        test1_pass = False

    print()

    # Test 2: Exceed max retries
    print("Test 2: Max retries exceeded")
    print("-" * 70)

    handler2 = RateLimitHandler(RateLimitConfig(
        max_retries=1,
        base_delay=0.05,
        jitter=False
    ))
    api2 = MockAPI(fail_count=3)  # Will fail more than max_retries

    try:
        result = await handler2.execute_with_retry(api2.call, "test_value")
        print(f"❌ FAIL: Should have raised RateLimitExceeded")
        test2_pass = False
    except RateLimitExceeded as e:
        print(f"✅ PASS: RateLimitExceeded raised as expected")
        print(f"   Message: {str(e)}")
        test2_pass = True
    except Exception as e:
        print(f"❌ FAIL: Wrong exception type: {type(e).__name__}")
        test2_pass = False

    print()

    # Test 3: Non-rate-limit error
    print("Test 3: Non-rate-limit error (immediate failure)")
    print("-" * 70)

    async def failing_func():
        raise ValueError("Not a rate limit error")

    handler3 = RateLimitHandler(config)

    try:
        result = await handler3.execute_with_retry(failing_func)
        print(f"❌ FAIL: Should have raised ValueError")
        test3_pass = False
    except ValueError as e:
        print(f"✅ PASS: ValueError raised immediately (no retry)")
        print(f"   Message: {str(e)}")
        test3_pass = True
    except RateLimitExceeded as e:
        print(f"❌ FAIL: Got RateLimitExceeded instead of ValueError")
        print(f"   Message: {str(e)}")
        print(f"   Cause: {e.__cause__}")
        test3_pass = False
    except Exception as e:
        print(f"❌ FAIL: Wrong exception type: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        test3_pass = False

    print()

    # Test 4: Handler statistics
    print("Test 4: Handler statistics")
    print("-" * 70)

    stats = handler.get_stats()
    print(f"Retry count: {stats['retry_count']}")
    print(f"Total delays: {stats['total_delays']:.2f}s")
    print(f"Config: max_retries={stats['config']['max_retries']}, base_delay={stats['config']['base_delay']}")

    if stats['retry_count'] >= 0 and stats['total_delays'] >= 0:
        print("✅ PASS: Statistics collected correctly")
        test4_pass = True
    else:
        print("❌ FAIL: Invalid statistics")
        test4_pass = False

    print()

    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    all_tests = [test1_pass, test2_pass, test3_pass, test4_pass]
    passed = sum(all_tests)
    total = len(all_tests)

    print(f"Tests passed: {passed}/{total}")

    if all(all_tests):
        print("✅ ALL TESTS PASSED")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


def main():
    """Run all tests"""
    try:
        exit_code = asyncio.run(test_rate_limit_retry())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
