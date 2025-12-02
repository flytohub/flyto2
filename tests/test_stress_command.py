#!/usr/bin/env python3
"""
Test Stress Command Implementation
Verifies the stress testing functionality works
"""
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


async def test_stress_functionality():
    """Test the core stress test functionality"""
    print("=" * 70)
    print("Testing Stress Command Functionality")
    print("=" * 70)
    print()

    from src.core.training.stress_test import StressTestEngine
    from src.core.engine.workflow_engine import WorkflowEngine

    async def run_operation(op_id, module_name, params):
        """Run a single operation"""
        workflow = {
            'workflow_name': f'stress_test_{op_id}',
            'steps': [{'step_id': f'op_{op_id}', 'module': module_name, 'params': params}]
        }
        engine = WorkflowEngine(workflow)
        result = await engine.execute()
        return result

    # Create test operations (just 10 for quick test)
    print("Creating 10 test operations...")
    operation_params = []
    operation_templates = [
        ('string.uppercase', {'text': 'test'}),
        ('string.lowercase', {'text': 'TEST'}),
        ('math.abs', {'number': -42.5}),
        ('array.sort', {'array': [3, 1, 4, 2], 'order': 'asc'}),
        ('object.keys', {'object': {'key1': 1, 'key2': 2}}),
    ]

    for i in range(10):
        module_name, base_params = operation_templates[i % len(operation_templates)]
        params = base_params.copy()
        if 'text' in params:
            params['text'] = f"{params['text']}_{i}"

        operation_params.append({
            'op_id': i,
            'module_name': module_name,
            'params': params
        })

    # Run stress test
    print("Running stress test...")
    engine = StressTestEngine(min_success_rate=95.0)

    async def operation_wrapper(op_id, module_name, params):
        return await run_operation(op_id, module_name, params)

    result = await engine.run_burst_test(
        operation=operation_wrapper,
        operation_params=operation_params,
        concurrency=10
    )

    # Generate and print report
    report = engine.generate_report(result)
    print(report)
    print()

    # Validate
    if engine.validate_result(result):
        print("✅ Test PASSED - Stress command functionality verified")
        return 0
    else:
        print("❌ Test FAILED - Stress test did not meet success criteria")
        return 1


async def main():
    """Main test runner"""
    try:
        exit_code = await test_stress_functionality()
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
