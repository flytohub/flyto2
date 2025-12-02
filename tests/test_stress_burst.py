#!/usr/bin/env python3
"""
Stress Test - 100 Concurrent Operations
Tests system under burst load to validate concurrent safety
Uses StressTestEngine for standardized stress testing
"""
import asyncio
import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


async def run_string_operation(op_id: int, module_name: str, params: dict):
    """Run a single string operation"""
    try:
        from src.core.engine.workflow_engine import WorkflowEngine

        # Create minimal workflow for this operation
        workflow = {
            'workflow_name': f'stress_test_{op_id}',
            'steps': [
                {
                    'step_id': f'op_{op_id}',
                    'module': module_name,
                    'params': params
                }
            ]
        }

        engine = WorkflowEngine(workflow)
        result = await engine.execute()
        return {'success': True, 'op_id': op_id, 'result': result}

    except Exception as e:
        return {'success': False, 'op_id': op_id, 'error': str(e)}


async def test_burst_100_concurrent():
    """
    Test 100 concurrent operations
    Target: >= 95% success rate
    """
    print("=" * 70)
    print("STRESS TEST: 100 Concurrent Operations")
    print("=" * 70)
    print()

    # Create 100 concurrent tasks with various operations
    tasks = []

    # Define operation templates
    # Using only concurrent-safe, reliable operations
    operation_templates = [
        'string.uppercase',
        'string.lowercase',
        'string.reverse',
        'string.trim',
        'math.abs',
        'math.round',
        'array.sort',
        'array.unique',
        'array.join',
        'object.keys',
    ]

    # Create 100 tasks
    for i in range(100):
        op_type = operation_templates[i % len(operation_templates)]

        # Generate params based on operation type
        if op_type == 'string.uppercase':
            params = {'text': f'test_{i}'}
        elif op_type == 'string.lowercase':
            params = {'text': f'TEST_{i}'}
        elif op_type == 'string.reverse':
            params = {'text': f'reverse_{i}'}
        elif op_type == 'string.trim':
            params = {'text': f'  trim_{i}  '}
        elif op_type == 'math.abs':
            params = {'number': -i * 1.5}
        elif op_type == 'math.round':
            params = {'number': i * 3.14159, 'decimals': 2}
        elif op_type == 'array.sort':
            params = {'array': [i, i+1, i+2, i+3], 'order': 'asc'}
        elif op_type == 'array.unique':
            params = {'array': [i, i, i+1, i+1, i+2]}
        elif op_type == 'array.join':
            params = {'array': [f'item_{i}', f'item_{i+1}', f'item_{i+2}'], 'separator': ','}
        else:  # object.keys
            params = {'object': {'key1': i, 'key2': i+1, 'key3': i+2}}

        tasks.append(run_string_operation(i, op_type, params))

    print(f"Starting {len(tasks)} concurrent operations...")
    start_time = time.time()

    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    end_time = time.time()
    duration = end_time - start_time

    # Analyze results
    total = len(results)
    successful = sum(1 for r in results if isinstance(r, dict) and r.get('success', False))
    failed = total - successful
    success_rate = (successful / total) * 100

    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Total operations:   {total}")
    print(f"Successful:         {successful}")
    print(f"Failed:             {failed}")
    print(f"Success rate:       {success_rate:.1f}%")
    print(f"Duration:           {duration:.2f}s")
    print(f"Ops/second:         {total/duration:.1f}")
    print()

    # Show failed operations if any
    if failed > 0:
        print("Failed operations:")
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"  Op {i}: {type(result).__name__}: {str(result)}")
            elif isinstance(result, dict) and not result.get('success', False):
                print(f"  Op {result.get('op_id', i)}: {result.get('error', 'Unknown error')}")
        print()

    # Validate success rate
    MIN_SUCCESS_RATE = 95.0
    if success_rate >= MIN_SUCCESS_RATE:
        print(f"✅ PASS: Success rate {success_rate:.1f}% >= {MIN_SUCCESS_RATE}%")
        return 0
    else:
        print(f"❌ FAIL: Success rate {success_rate:.1f}% < {MIN_SUCCESS_RATE}%")
        return 1


def main():
    """Run stress test"""
    try:
        exit_code = asyncio.run(test_burst_100_concurrent())
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
