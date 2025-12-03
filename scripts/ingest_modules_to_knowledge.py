#!/usr/bin/env python3
"""
Ingest Atomic Modules into Knowledge Base
Scans src/core/modules/atomic/ directory, extracts module information and stores to Qdrant
"""
import os
import sys
import ast
import inspect
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv

# Add project path
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()

from src.core.memory.knowledge_extractor import get_knowledge_extractor

print("=" * 80)
print("Ingest Atomic Modules to Knowledge Base")
print("=" * 80)


def extract_module_info_from_file(file_path: Path) -> List[Dict]:
    """
    Extract module information from Python file

    Args:
        file_path: Path to Python file

    Returns:
        List of module information dictionaries
    """
    modules = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse AST
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if inherits from BaseModule
                is_module = any(
                    isinstance(base, ast.Name) and base.id == 'BaseModule'
                    for base in node.bases
                )

                if not is_module:
                    continue

                # Extract class information
                module_info = {
                    'class_name': node.name,
                    'file_path': str(file_path),
                    'description': ast.get_docstring(node) or "",
                    'parameters': {},
                    'returns': {}
                }

                # Extract class attributes
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                attr_name = target.name

                                # Extract module_name, module_description, etc.
                                if attr_name in ['module_name', 'module_description']:
                                    if isinstance(item.value, ast.Constant):
                                        module_info[attr_name] = item.value.value

                # Extract validate_params method to understand parameters
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == 'validate_params':
                        # Simple extraction (needs more complex AST analysis for complete parameter extraction)
                        params_code = ast.get_source_segment(content, item)
                        module_info['validate_params_code'] = params_code

                modules.append(module_info)

    except Exception as e:
        print(f"⚠️ Unable to parse {file_path}: {e}")

    return modules


def scan_atomic_modules(base_path: Path) -> List[Dict]:
    """
    Scan all atomic modules

    Args:
        base_path: Atomic modules root directory

    Returns:
        List of modules
    """
    all_modules = []

    # Scan all .py files
    for py_file in base_path.rglob("*.py"):
        # Exclude __init__.py and test files
        if py_file.name == "__init__.py" or py_file.name.startswith("test_"):
            continue

        modules = extract_module_info_from_file(py_file)
        all_modules.extend(modules)

    return all_modules


def determine_module_id(file_path: str, class_name: str) -> str:
    """
    Determine module_id based on file path and class name

    Examples:
    - src/core/modules/atomic/browser/click.py → browser.click
    - src/core/modules/atomic/array/map.py → array.map
    """
    path = Path(file_path)

    # Extract subdirectory where class is located
    parts = path.parts

    # Find parts after 'atomic'
    try:
        atomic_index = parts.index('atomic')
        subcategory = parts[atomic_index + 1] if atomic_index + 1 < len(parts) else ""

        # Use filename as module name (without .py)
        module_name = path.stem

        if subcategory and module_name:
            return f"{subcategory}.{module_name}"
        else:
            return module_name

    except ValueError:
        # If 'atomic' not found, use filename directly
        return path.stem


def ingest_modules_to_knowledge(modules: List[Dict]) -> int:
    """
    Ingest modules into knowledge base

    Args:
        modules: List of modules

    Returns:
        Number of successfully ingested modules
    """
    knowledge = get_knowledge_extractor()
    success_count = 0

    for module in modules:
        try:
            # Determine module_id
            module_id = determine_module_id(
                module['file_path'],
                module['class_name']
            )

            # Extract subcategory
            path_parts = Path(module['file_path']).parts
            try:
                atomic_index = path_parts.index('atomic')
                subcategory = path_parts[atomic_index + 1] if atomic_index + 1 < len(path_parts) else "other"
            except ValueError:
                subcategory = "other"

            # Combine description
            description = module.get('module_description') or module.get('description') or f"{module['class_name']} module"

            # Store to knowledge base
            knowledge_id = knowledge.store_module(
                module_id=module_id,
                category="atomic",
                subcategory=subcategory,
                description=description,
                parameters=module.get('parameters', {}),
                returns=module.get('returns', {}),
                code_example=None,  # Can be supplemented later
                metadata={
                    'class_name': module['class_name'],
                    'file_path': module['file_path'],
                    'source': 'auto_ingestion'
                }
            )

            print(f"✅ {module_id} ({subcategory})")
            success_count += 1

        except Exception as e:
            print(f"❌ Ingestion failed: {module.get('class_name', 'Unknown')} - {e}")

    return success_count


# ============================================================
# Manually Defined Core Modules (supplement info that AST cannot extract)
# ============================================================

CORE_MODULES = [
    {
        'module_id': 'browser.launch',
        'category': 'atomic',
        'subcategory': 'browser',
        'description': 'Launch browser instance',
        'parameters': {
            'headless': {'type': 'boolean', 'description': 'Headless mode', 'default': True},
            'browser_type': {'type': 'string', 'description': 'Browser type', 'default': 'chromium'}
        },
        'returns': {
            'browser': {'type': 'object', 'description': 'Browser instance'}
        },
        'code_example': '''
- id: launch_browser
  module: browser.launch
  params:
    headless: false
    browser_type: chromium
'''
    },
    {
        'module_id': 'browser.goto',
        'category': 'atomic',
        'subcategory': 'browser',
        'description': 'Navigate to specified URL',
        'parameters': {
            'url': {'type': 'string', 'description': 'Target URL'},
            'timeout': {'type': 'number', 'description': 'Timeout in milliseconds', 'default': 30000}
        },
        'returns': {
            'success': {'type': 'boolean', 'description': 'Whether navigation succeeded'}
        },
        'code_example': '''
- id: navigate
  module: browser.goto
  params:
    url: https://example.com
    timeout: 30000
'''
    },
    {
        'module_id': 'browser.click',
        'category': 'atomic',
        'subcategory': 'browser',
        'description': 'Click page element',
        'parameters': {
            'selector': {'type': 'string', 'description': 'CSS selector'},
            'timeout': {'type': 'number', 'description': 'Timeout in milliseconds', 'default': 5000}
        },
        'returns': {
            'success': {'type': 'boolean', 'description': 'Whether click succeeded'}
        },
        'code_example': '''
- id: click_button
  module: browser.click
  params:
    selector: "#submit-button"
'''
    },
    {
        'module_id': 'browser.type',
        'category': 'atomic',
        'subcategory': 'browser',
        'description': 'Type text into element',
        'parameters': {
            'selector': {'type': 'string', 'description': 'CSS selector'},
            'text': {'type': 'string', 'description': 'Text to type'},
            'delay': {'type': 'number', 'description': 'Key press delay in milliseconds', 'default': 0}
        },
        'returns': {
            'success': {'type': 'boolean', 'description': 'Whether typing succeeded'}
        },
        'code_example': '''
- id: fill_input
  module: browser.type
  params:
    selector: "input[name='email']"
    text: user@example.com
'''
    },
    {
        'module_id': 'browser.extract',
        'category': 'atomic',
        'subcategory': 'browser',
        'description': 'Extract data from page',
        'parameters': {
            'fields': {'type': 'array', 'description': 'Field configuration list'},
            'multiple': {'type': 'boolean', 'description': 'Whether to extract multiple items', 'default': False}
        },
        'returns': {
            'data': {'type': 'object/array', 'description': 'Extracted data'}
        },
        'code_example': '''
- id: extract_data
  module: browser.extract
  params:
    multiple: true
    fields:
      - name: title
        selector: h1.title
      - name: price
        selector: span.price
'''
    },
    {
        'module_id': 'loop',
        'category': 'atomic',
        'subcategory': 'control',
        'description': 'Execute steps in a loop',
        'parameters': {
            'count': {'type': 'number', 'description': 'Number of iterations'},
            'steps': {'type': 'array', 'description': 'List of steps to execute'}
        },
        'returns': {
            'iterations': {'type': 'number', 'description': 'Actual number of iterations executed'}
        },
        'code_example': '''
- id: loop_pages
  module: loop
  params:
    count: 5
    steps:
      - module: browser.click
        params:
          selector: ".next-button"
'''
    },
    {
        'module_id': 'array.map',
        'category': 'atomic',
        'subcategory': 'array',
        'description': 'Transform each element of array',
        'parameters': {
            'array': {'type': 'array', 'description': 'Input array'},
            'transform': {'type': 'string', 'description': 'Transform expression'}
        },
        'returns': {
            'result': {'type': 'array', 'description': 'Transformed array'}
        },
        'code_example': '''
- id: transform_data
  module: array.map
  params:
    array: ${extracted_data}
    transform: "item.price * 0.8"
'''
    },
    {
        'module_id': 'csv_write',
        'category': 'atomic',
        'subcategory': 'data',
        'description': 'Write data to CSV file',
        'parameters': {
            'data': {'type': 'array', 'description': 'Data array'},
            'filename': {'type': 'string', 'description': 'File name'},
            'headers': {'type': 'array', 'description': 'Column headers', 'optional': True}
        },
        'returns': {
            'filepath': {'type': 'string', 'description': 'File path'}
        },
        'code_example': '''
- id: save_csv
  module: csv_write
  params:
    data: ${extracted_data}
    filename: output.csv
'''
    },
]


def ingest_core_modules():
    """Ingest core modules (manually defined)"""
    knowledge = get_knowledge_extractor()
    success_count = 0

    print("\n[Ingest Core Modules - Manually Defined]")
    print("-" * 80)

    for module in CORE_MODULES:
        try:
            knowledge_id = knowledge.store_module(
                module_id=module['module_id'],
                category=module['category'],
                subcategory=module['subcategory'],
                description=module['description'],
                parameters=module['parameters'],
                returns=module['returns'],
                code_example=module.get('code_example'),
                metadata={'source': 'core_manual'}
            )

            print(f"✅ {module['module_id']}")
            success_count += 1

        except Exception as e:
            print(f"❌ Ingestion failed: {module['module_id']} - {e}")

    return success_count


# ============================================================
# Main Program
# ============================================================

if __name__ == "__main__":
    print("\n[Stage 1: Scan Atomic Modules Directory]")
    print("-" * 80)

    atomic_path = Path(__file__).parent.parent / "src" / "core" / "modules" / "atomic"

    if not atomic_path.exists():
        print(f"❌ Atomic modules directory not found: {atomic_path}")
        sys.exit(1)

    print(f"Scanning directory: {atomic_path}")

    # Scan modules
    modules = scan_atomic_modules(atomic_path)
    print(f"✅ Found {len(modules)} module classes")

    # Show first 5
    for i, module in enumerate(modules[:5], 1):
        print(f"   [{i}] {module['class_name']} - {module['file_path']}")

    if len(modules) > 5:
        print(f"   ... and {len(modules) - 5} more")

    # Ingest to knowledge base
    print("\n[Stage 2: Ingest Auto-Scanned Modules]")
    print("-" * 80)

    auto_count = ingest_modules_to_knowledge(modules)
    print(f"\n✅ Successfully ingested {auto_count}/{len(modules)} auto-scanned modules")

    # Ingest core modules (manually defined)
    print("\n[Stage 3: Ingest Core Modules (Manually Defined)]")
    print("-" * 80)

    core_count = ingest_core_modules()
    print(f"\n✅ Successfully ingested {core_count}/{len(CORE_MODULES)} core modules")

    # Summary
    print("\n" + "=" * 80)
    print("Ingestion Summary")
    print("=" * 80)
    print(f"✅ Auto-scanned: {auto_count} modules")
    print(f"✅ Manually defined: {core_count} modules")
    print(f"✅ Total: {auto_count + core_count} modules ingested to knowledge base")

    # Test retrieval
    print("\n[Verification: Test Knowledge Base Retrieval]")
    print("-" * 80)

    knowledge = get_knowledge_extractor()

    test_queries = [
        "How to click a button on web page?",
        "How to extract data from web page?",
        "How to handle array data?"
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        results = knowledge.search_modules(query, limit=3)
        for i, result in enumerate(results, 1):
            module_id = result['metadata'].get('module_id', 'Unknown')
            score = result['score']
            print(f"   [{i}] {module_id} (relevance: {score:.3f})")

    print("\n" + "=" * 80)
    print("✅ Module ingestion complete! Knowledge base ready!")
    print("=" * 80)
