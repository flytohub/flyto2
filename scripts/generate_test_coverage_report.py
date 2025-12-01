#!/usr/bin/env python3
"""
Generate detailed test coverage report for all modules
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.modules.registry import ModuleRegistry
import yaml


def load_tested_modules():
    """Load all modules that have tests"""
    test_dir = PROJECT_ROOT / "workflows" / "_test"
    tested_modules = set()

    if not test_dir.exists():
        return tested_modules

    for test_file in test_dir.glob("test_*.yaml"):
        try:
            with open(test_file, 'r') as f:
                workflow = yaml.safe_load(f)
                for step in workflow.get('steps', []):
                    module_id = step.get('module_id') or step.get('module')
                    if module_id:
                        tested_modules.add(module_id)
        except Exception as e:
            print(f"Warning: Could not parse {test_file.name}: {e}")

    return tested_modules


def categorize_modules(all_modules, tested_modules):
    """Categorize modules by prefix and test status"""
    categories = {}

    for module_id in all_modules.keys():
        prefix = module_id.split('.')[0]
        if prefix not in categories:
            categories[prefix] = {
                'tested': [],
                'untested': []
            }

        if module_id in tested_modules:
            categories[prefix]['tested'].append(module_id)
        else:
            categories[prefix]['untested'].append(module_id)

    return categories


def needs_external_api(module_id):
    """Determine if module needs external API/token"""
    api_indicators = [
        'api.', 'openai', 'anthropic', 'gemini',
        'slack', 'discord', 'telegram', 'email',
        'twilio', 'stripe', 'github', 'notion',
        'airtable', 'sheets', 'db.', 'cloud.',
        'aws', 'gcs', 'azure', 'mongodb', 'postgresql',
        'mysql', 'redis'
    ]

    module_lower = module_id.lower()
    return any(indicator in module_lower for indicator in api_indicators)


def main():
    print("=" * 70)
    print(" Test Coverage Report - Flyto2 Module System")
    print("=" * 70)
    print()

    # Load data
    registry = ModuleRegistry()
    all_modules = registry.get_all_metadata()
    tested_modules = load_tested_modules()

    total = len(all_modules)
    tested_count = len(tested_modules)
    untested_count = total - tested_count
    coverage = tested_count / total if total > 0 else 0

    # Summary
    print(f"Total Modules:        {total}")
    print(f"Modules Tested:       {tested_count} ({coverage:.1%})")
    print(f"Modules Untested:     {untested_count} ({(1-coverage):.1%})")
    print()

    # Categorize
    categories = categorize_modules(all_modules, tested_modules)

    # Show by category
    print("=" * 70)
    print(" Coverage by Category")
    print("=" * 70)
    print()
    print(f"{'Category':<20} {'Tested':<10} {'Untested':<10} {'Coverage':<10}")
    print("-" * 70)

    for cat in sorted(categories.keys()):
        tested = len(categories[cat]['tested'])
        untested = len(categories[cat]['untested'])
        cat_total = tested + untested
        cat_coverage = tested / cat_total if cat_total > 0 else 0
        print(f"{cat:<20} {tested:<10} {untested:<10} {cat_coverage:>8.1%}")

    print()

    # Detailed untested modules
    print("=" * 70)
    print(" Untested Modules by Category")
    print("=" * 70)
    print()

    for cat in sorted(categories.keys()):
        untested = sorted(categories[cat]['untested'])
        if untested:
            print(f"\n{cat.upper()} ({len(untested)} untested):")
            print("-" * 70)
            for mod_id in untested:
                needs_api = needs_external_api(mod_id)
                status = "[Needs API token]" if needs_api else "[Can test]"
                print(f"  {status:<20} {mod_id}")

    print()
    print("=" * 70)
    print(" Recommendations")
    print("=" * 70)
    print()

    # Count modules that need API vs can be tested
    untested_list = [m for m in all_modules.keys() if m not in tested_modules]
    needs_api_list = [m for m in untested_list if needs_external_api(m)]
    can_test_list = [m for m in untested_list if not needs_external_api(m)]

    print(f"Untested modules that CAN be tested now:  {len(can_test_list)}")
    print(f"Untested modules that NEED API tokens:    {len(needs_api_list)}")
    print()

    if can_test_list:
        print("Priority: Add tests for these modules first:")
        for mod_id in can_test_list[:10]:
            print(f"  • {mod_id}")
        if len(can_test_list) > 10:
            print(f"  ... and {len(can_test_list) - 10} more")

    print()
    print("For API-dependent modules, consider:")
    print("  1. Mock testing (simulate API responses)")
    print("  2. Optional real testing (if user provides tokens)")
    print("  3. Integration test suite (separate from unit tests)")
    print()

    # Save report
    report_file = PROJECT_ROOT / "TEST_COVERAGE_REPORT.md"
    with open(report_file, 'w') as f:
        f.write("# Test Coverage Report\n\n")
        f.write(f"**Generated:** {Path(__file__).name}\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- **Total Modules:** {total}\n")
        f.write(f"- **Tested:** {tested_count} ({coverage:.1%})\n")
        f.write(f"- **Untested:** {untested_count}\n\n")

        f.write(f"## Untested Modules\n\n")
        for cat in sorted(categories.keys()):
            untested = sorted(categories[cat]['untested'])
            if untested:
                f.write(f"### {cat.upper()}\n\n")
                for mod_id in untested:
                    needs_api = needs_external_api(mod_id)
                    status = "🔑 Needs API" if needs_api else "✅ Can test"
                    f.write(f"- {status} `{mod_id}`\n")
                f.write("\n")

    print(f"Report saved to: {report_file}")


if __name__ == "__main__":
    main()
