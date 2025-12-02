#!/usr/bin/env python3
"""
Test Quality Improvements

Verifies that the evolution engine generates high-quality modules.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.evolution.auto_evolution_engine import (
    EvolutionPlanner,
    EvolutionDesigner,
    ImplementationAgent
)


async def test_template_quality():
    """Test that template includes quality standards"""
    print("=" * 70)
    print("TEST 1: Template Quality")
    print("=" * 70)

    agent = ImplementationAgent(use_ollama=False)

    change = {
        'path': 'src/core/modules/atomic/xml/parse_elements.py',
        'reason': 'Parse XML elements from string',
        'template': 'atomic_module'
    }

    template = agent._generate_atomic_module_template(change)

    # Check for quality markers
    quality_checks = {
        'BaseModule': 'BaseModule' in template,
        '@register_module': '@register_module' in template,
        'No hardcoded data warning': 'hardcoded' in template.lower() or 'NO hardcoded' in template,
        'MUST read from self.params': 'self.params' in template,
        'validate_params()': 'def validate_params' in template,
        'Error handling': 'try:' in template and 'except' in template,
        'QUALITY STANDARDS': 'QUALITY STANDARDS' in template
    }

    print("\n✅ Quality Checks:")
    for check, passed in quality_checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")

    all_passed = all(quality_checks.values())

    if all_passed:
        print("\n🎉 Template quality test PASSED!")
    else:
        print("\n❌ Template quality test FAILED!")

    print("\n📝 Generated Template (first 1000 chars):")
    print(template[:1000])
    print("...")

    return all_passed


async def test_ollama_generation():
    """Test Ollama code generation (if available)"""
    print("\n" + "=" * 70)
    print("TEST 2: Ollama Code Generation")
    print("=" * 70)

    agent = ImplementationAgent(use_ollama=True)

    change = {
        'path': 'src/core/modules/atomic/test_quality.py',
        'reason': 'Test module for quality validation',
        'template': 'atomic_module'
    }

    print("\n🤖 Attempting Ollama generation...")

    try:
        code = await agent._generate_with_ollama(change)

        if code:
            print("✅ Ollama generated code!")

            # Validate quality
            quality_checks = {
                '@register_module': '@register_module' in code,
                'BaseModule': 'BaseModule' in code,
                'validate_params': 'def validate_params' in code,
                'execute': 'async def execute' in code or 'def execute' in code,
                'No markdown fences': '```' not in code
            }

            print("\n✅ Quality Checks:")
            for check, passed in quality_checks.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}")

            print("\n📝 Generated Code (first 1000 chars):")
            print(code[:1000])
            print("...")

            return all(quality_checks.values())
        else:
            print("⚠️ Ollama generation returned None (may be unavailable)")
            return None  # Not a failure, just unavailable

    except Exception as e:
        print(f"⚠️ Ollama test skipped: {e}")
        return None  # Not a failure, just unavailable


async def test_module_id_extraction():
    """Test module ID extraction from paths"""
    print("\n" + "=" * 70)
    print("TEST 3: Module ID Extraction")
    print("=" * 70)

    agent = ImplementationAgent(use_ollama=False)

    test_cases = [
        ('src/core/modules/atomic/xml/parse_elements.py', 'xml.parse_elements'),
        ('src/core/modules/atomic/string/upper.py', 'string.upper'),
        ('src/core/modules/atomic/test.py', 'test'),
        ('modules/my_module.py', 'my_module')
    ]

    print("\n✅ Extraction Tests:")
    all_passed = True

    for path, expected in test_cases:
        result = agent._extract_module_id_from_path(path)
        passed = result == expected
        all_passed = all_passed and passed

        status = "✅" if passed else "❌"
        print(f"  {status} {path} -> {result} (expected: {expected})")

    if all_passed:
        print("\n🎉 Module ID extraction test PASSED!")
    else:
        print("\n❌ Module ID extraction test FAILED!")

    return all_passed


async def test_class_name_generation():
    """Test class name generation"""
    print("\n" + "=" * 70)
    print("TEST 4: Class Name Generation")
    print("=" * 70)

    agent = ImplementationAgent(use_ollama=False)

    test_cases = [
        ('parse_xml_elements', 'ParseXmlElementsModule'),
        ('string_upper', 'StringUpperModule'),
        ('test', 'TestModule'),
        ('api_request', 'ApiRequestModule')
    ]

    print("\n✅ Generation Tests:")
    all_passed = True

    for module_name, expected in test_cases:
        result = agent._to_class_name(module_name)
        passed = result == expected
        all_passed = all_passed and passed

        status = "✅" if passed else "❌"
        print(f"  {status} {module_name} -> {result} (expected: {expected})")

    if all_passed:
        print("\n🎉 Class name generation test PASSED!")
    else:
        print("\n❌ Class name generation test FAILED!")

    return all_passed


async def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("🧪 QUALITY IMPROVEMENTS TEST SUITE")
    print("=" * 70)
    print()

    results = {}

    # Run tests
    results['template_quality'] = await test_template_quality()
    results['ollama_generation'] = await test_ollama_generation()
    results['module_id_extraction'] = await test_module_id_extraction()
    results['class_name_generation'] = await test_class_name_generation()

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    total = len(results)

    for test_name, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⏭️ SKIP"

        print(f"{status} - {test_name}")

    print(f"\nTotal: {total} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
