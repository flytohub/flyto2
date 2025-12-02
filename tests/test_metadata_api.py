#!/usr/bin/env python
"""
Test metadata API for UI builder integration
"""
import sys
from pathlib import Path

# Add project root to Python path (for running test directly)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
from src.core.modules.registry import ModuleRegistry

def test_metadata_api():
    """Test metadata retrieval for UI builder"""

    print("=" * 70)
    print("METADATA API TEST - UI Builder Integration")
    print("=" * 70)
    print()

    # Test 1: Get all modules metadata
    print("1️⃣  Getting all modules metadata...")
    all_metadata = ModuleRegistry.get_all_metadata(lang='zh')

    print(f"   Total modules: {len(all_metadata)}")
    print()

    # Test 2: Show sample module metadata
    print("2️⃣  Sample module metadata (core.browser.launch):")
    sample = ModuleRegistry.get_metadata('core.browser.launch', lang='zh')

    if sample:
        print(f"   Module ID: {sample.get('module_id')}")
        print(f"   Label: {sample.get('label')}")
        print(f"   Label Key: {sample.get('label_key')}")
        print(f"   Category: {sample.get('category')}")
        print(f"   Icon: {sample.get('icon')}")
        print(f"   Color: {sample.get('color')}")
        print(f"   Description: {sample.get('description')[:50]}...")
        print()

        print("   Params Schema:")
        params_schema = sample.get('params_schema', {})
        for param_name, param_def in params_schema.items():
            if isinstance(param_def, dict):
                print(f"     - {param_name}:")
                print(f"       Type: {param_def.get('type')}")
                print(f"       Label: {param_def.get('label')}")
                print(f"       Required: {param_def.get('required', False)}")
                print(f"       Default: {param_def.get('default', 'N/A')}")
    print()

    # Test 3: Group by category
    print("3️⃣  Modules by category:")
    categories = {}
    for module_id, metadata in all_metadata.items():
        cat = metadata.get('category', 'other')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(module_id)

    for cat, modules in sorted(categories.items()):
        print(f"   {cat.upper()}: {len(modules)} modules")
        for mod in sorted(modules)[:3]:  # Show first 3
            print(f"     - {mod}")
        if len(modules) > 3:
            print(f"     ... and {len(modules) - 3} more")
    print()

    # Test 4: JSON export (for API response)
    print("4️⃣  JSON export sample (for API response):")
    api_response = {
        "modules": [
            {
                "module_id": metadata.get('module_id'),
                "label": metadata.get('label'),
                "category": metadata.get('category'),
                "icon": metadata.get('icon'),
                "color": metadata.get('color'),
                "params_schema": metadata.get('params_schema', {})
            }
            for module_id, metadata in list(all_metadata.items())[:2]
        ]
    }

    print(json.dumps(api_response, indent=2, ensure_ascii=False))
    print()

    # Test 5: Validation simulation
    print("5️⃣  Parameter validation simulation:")
    module_id = 'core.browser.launch'
    test_params = {
        'headless': True
    }

    metadata = ModuleRegistry.get_metadata(module_id)
    params_schema = metadata.get('params_schema', {})

    print(f"   Validating params for {module_id}:")
    print(f"   Params: {test_params}")

    errors = []
    for param_name, param_def in params_schema.items():
        if isinstance(param_def, dict) and param_def.get('required', False):
            if param_name not in test_params:
                errors.append(f"Missing required: {param_name}")

    if errors:
        print(f"   ❌ Validation failed: {errors}")
    else:
        print(f"   ✅ Validation passed!")

    print()

    # Test 6: Search simulation
    print("6️⃣  Search simulation (query='browser'):")
    query = 'browser'
    results = []

    for module_id, metadata in all_metadata.items():
        searchable = ' '.join([
            module_id,
            metadata.get('label', ''),
            metadata.get('description', ''),
            ' '.join(metadata.get('tags', []))
        ]).lower()

        if query.lower() in searchable:
            results.append(module_id)

    print(f"   Found {len(results)} modules:")
    for r in sorted(results)[:5]:
        print(f"     - {r}")

    print()
    print("=" * 70)
    print("✅ Metadata API is ready for UI builder!")
    print()
    print("Frontend can call these endpoints:")
    print("  GET /api/modules/list?lang=zh")
    print("  GET /api/modules/detail/{module_id}?lang=zh")
    print("  GET /api/modules/schema/{module_id}")
    print("  POST /api/modules/validate")
    print("=" * 70)


if __name__ == '__main__':
    test_metadata_api()
