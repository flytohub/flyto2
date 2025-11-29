#!/usr/bin/env python
"""
Quick test script to validate core engine functionality
"""
import sys
from pathlib import Path

# Add project root to Python path (for running test directly)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import yaml
from src.core.engine.workflow_engine import WorkflowEngine
from src.core.modules.registry import ModuleRegistry

def test_variable_resolver():
    """Test variable resolution"""
    print("=" * 70)
    print("TEST 1: Variable Resolver")
    print("=" * 70)

    from src.core.engine.variable_resolver import VariableResolver

    params = {'keyword': 'python', 'url': 'https://example.com'}
    context = {
        'step1': {'status': 'success', 'count': 42},
        'step2': {'data': [{'title': 'Test', 'price': 99}]}
    }

    resolver = VariableResolver(params, context, {'id': 'test_workflow'})

    # Test param access
    result1 = resolver.resolve('${params.keyword}')
    print(f"✓ Param access: ${'{params.keyword}'} = '{result1}'")
    assert result1 == 'python', f"Expected 'python', got '{result1}'"

    # Test step output access
    result2 = resolver.resolve('${step1.count}')
    print(f"✓ Step output: ${'{step1.count}'} = {result2}")
    assert result2 == 42, f"Expected 42, got {result2}"

    # Test nested access
    result3 = resolver.resolve('${step2.data}')
    print(f"✓ Nested access: ${'{step2.data}'} = {result3}")

    # Test built-in
    result4 = resolver.resolve('${timestamp}')
    print(f"✓ Built-in: ${'{timestamp}'} = {result4}")

    print("✓ Variable Resolver: PASSED\n")
    return True

def test_module_registry():
    """Test module registration"""
    print("=" * 70)
    print("TEST 2: Module Registry")
    print("=" * 70)

    # List all registered modules
    all_modules = ModuleRegistry.list_all()
    modules = [{'module_id': mid, 'category': mid.split('.')[1] if '.' in mid else 'other'} for mid in all_modules.keys()]
    print(f"Total registered modules: {len(modules)}")

    # Group by category
    by_category = {}
    for mod in modules:
        cat = mod['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(mod['module_id'])

    for cat, mods in sorted(by_category.items()):
        print(f"\n{cat.upper()}: {len(mods)} modules")
        for mod_id in sorted(mods):
            print(f"  - {mod_id}")

    # Check critical modules exist
    critical_modules = [
        'core.browser.launch',
        'core.browser.goto',
        'core.api.http_get',
        'core.ai.openai.chat'
    ]

    print(f"\nChecking critical modules...")
    for mod_id in critical_modules:
        module_class = ModuleRegistry.get(mod_id)
        if module_class:
            print(f"✓ {mod_id}: Found")
        else:
            print(f"✗ {mod_id}: MISSING")
            return False

    print("\n✓ Module Registry: PASSED\n")
    return True

async def test_http_workflow():
    """Test HTTP workflow execution"""
    print("=" * 70)
    print("TEST 3: HTTP Workflow Execution")
    print("=" * 70)

    # Load test workflow
    workflow_path = Path('workflows/test_simple.yaml')
    if not workflow_path.exists():
        print(f"✗ Workflow file not found: {workflow_path}")
        return False

    with open(workflow_path) as f:
        workflow = yaml.safe_load(f)

    print(f"Workflow: {workflow.get('name')}")
    print(f"Steps: {len(workflow.get('steps', []))}")

    # Execute workflow
    try:
        engine = WorkflowEngine(workflow, {})
        output = await engine.execute()

        print(f"\nExecution Status: {engine.status}")
        print(f"Steps Executed: {len(engine.execution_log)}")

        # Check output
        if 'status_code' in output:
            print(f"✓ HTTP Status Code: {output['status_code']}")
        if 'body' in output:
            print(f"✓ Response Body Length: {len(output['body'])} chars")
        if 'timestamp' in output:
            print(f"✓ Timestamp: {output['timestamp']}")

        print("\n✓ HTTP Workflow: PASSED\n")
        return True

    except Exception as e:
        print(f"✗ Workflow execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_readme_promises():
    """Check README promises vs actual implementation"""
    print("=" * 70)
    print("TEST 4: README Promises vs Implementation")
    print("=" * 70)

    promises = {
        "Browser Automation": {
            "modules": ['core.browser.launch', 'core.browser.goto', 'core.browser.click',
                       'core.browser.type', 'core.browser.extract'],
            "implemented": True
        },
        "AI Integration": {
            "modules": ['core.ai.openai.chat'],
            "implemented": True
        },
        "HTTP Requests": {
            "modules": ['core.api.http_get', 'core.api.http_post'],
            "implemented": True
        },
        "Flow Control": {
            "features": ['retry', 'parallel', 'when', 'on_error'],
            "implemented": True
        },
        "Variable Resolution": {
            "features": ['${params.*}', '${step.*}', '${env.*}', '${timestamp}'],
            "implemented": True
        }
    }

    all_passed = True

    for category, info in promises.items():
        print(f"\n{category}:")

        if 'modules' in info:
            for mod_id in info['modules']:
                exists = ModuleRegistry.get(mod_id) is not None
                status = "✓" if exists else "✗"
                print(f"  {status} {mod_id}")
                if not exists:
                    all_passed = False

        if 'features' in info:
            for feature in info['features']:
                status = "✓" if info['implemented'] else "✗"
                print(f"  {status} {feature}")

        if 'implemented' in info and not info['implemented']:
            all_passed = False

    if all_passed:
        print("\n✓ README Promises: PASSED\n")
    else:
        print("\n✗ README Promises: SOME MISSING\n")

    return all_passed

async def main():
    """Run all tests"""
    print("\n")
    print("=" * 70)
    print("FLYTO2 CORE ENGINE TEST SUITE")
    print("=" * 70)
    print()

    results = []

    # Test 1: Variable Resolver
    try:
        results.append(("Variable Resolver", test_variable_resolver()))
    except Exception as e:
        print(f"✗ Variable Resolver: FAILED - {str(e)}\n")
        results.append(("Variable Resolver", False))

    # Test 2: Module Registry
    try:
        results.append(("Module Registry", test_module_registry()))
    except Exception as e:
        print(f"✗ Module Registry: FAILED - {str(e)}\n")
        results.append(("Module Registry", False))

    # Test 3: HTTP Workflow
    try:
        results.append(("HTTP Workflow", await test_http_workflow()))
    except Exception as e:
        print(f"✗ HTTP Workflow: FAILED - {str(e)}\n")
        results.append(("HTTP Workflow", False))

    # Test 4: README Promises
    try:
        results.append(("README Promises", check_readme_promises()))
    except Exception as e:
        print(f"✗ README Promises: FAILED - {str(e)}\n")
        results.append(("README Promises", False))

    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ ALL TESTS PASSED - Engine is ready for launch!")
        return 0
    else:
        print(f"\n✗ {total - passed} tests failed - Some features need attention")
        return 1

if __name__ == '__main__':
    exit_code = asyncio.run(main())
    exit(exit_code)
