#!/usr/bin/env python3
"""
Module Updater Script

Helps update existing modules to comply with new specification by adding:
- input_types
- output_types
- can_receive_from
- can_connect_to

Usage:
    python scripts/update_modules.py --dry-run  # Preview changes
    python scripts/update_modules.py            # Apply changes
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


# Type inference rules based on module patterns
TYPE_INFERENCE_RULES = {
    # Browser modules
    'browser.instance': {
        'input_types': [],
        'output_types': ['browser_instance'],
        'can_connect_to': ['browser.page.*', 'browser.element.*'],
    },
    'browser.page': {
        'input_types': ['browser_instance'],
        'output_types': ['page_instance', 'html', 'screenshot'],
        'can_receive_from': ['browser.instance.*'],
        'can_connect_to': ['file.*', 'data.*', 'cloud.*'],
    },
    'browser.element': {
        'input_types': ['page_instance', 'element'],
        'output_types': ['element', 'text'],
        'can_receive_from': ['browser.page.*'],
    },

    # Data modules
    'data.json': {
        'input_types': ['text', 'string'],
        'output_types': ['json', 'object'],
        'can_receive_from': ['file.read', 'api.http.*'],
        'can_connect_to': ['data.*', 'notification.*', 'file.*'],
    },
    'data.csv': {
        'input_types': ['text', 'file_path'],
        'output_types': ['array', 'object'],
        'can_connect_to': ['data.*', 'file.*'],
    },

    # File modules
    'file.read': {
        'input_types': [],
        'output_types': ['text', 'binary'],
        'can_connect_to': ['data.*', 'string.*'],
    },
    'file.write': {
        'input_types': ['text', 'binary', 'any'],
        'output_types': ['file_path'],
        'can_receive_from': ['data.*', 'browser.*', 'string.*'],
    },

    # Notification modules
    'notification': {
        'input_types': ['text', 'json', 'any'],
        'output_types': ['api_response'],
        'can_receive_from': ['data.*', 'api.*', 'string.*'],
    },

    # AI modules
    'ai': {
        'input_types': ['text', 'json'],
        'output_types': ['text', 'json'],
        'can_receive_from': ['data.*', 'file.*', 'browser.*'],
        'can_connect_to': ['data.*', 'notification.*', 'file.*'],
    },

    # API modules
    'api.http': {
        'input_types': [],
        'output_types': ['json', 'text', 'api_response'],
        'can_connect_to': ['data.*', 'notification.*', 'file.*'],
    },

    # Database modules
    'database': {
        'input_types': ['json', 'object'],
        'output_types': ['json', 'array'],
        'can_receive_from': ['data.*', 'api.*'],
        'can_connect_to': ['data.*', 'notification.*'],
    },
}


def infer_types_for_module(module_id: str, category: str) -> Dict[str, any]:
    """Infer input/output types based on module ID and category"""

    # Try exact match first
    for pattern, types in TYPE_INFERENCE_RULES.items():
        if module_id.startswith(pattern):
            return types.copy()

    # Fall back to category
    if category in TYPE_INFERENCE_RULES:
        return TYPE_INFERENCE_RULES[category].copy()

    # Default fallback
    return {
        'input_types': ['any'],
        'output_types': ['any'],
        'can_receive_from': [],
        'can_connect_to': [],
    }


def parse_module_file(file_path: Path) -> Tuple[str, Dict]:
    """Parse module file and extract @register_module metadata"""
    content = file_path.read_text()

    # Find @register_module decorator
    match = re.search(r'@register_module\((.*?)\)', content, re.DOTALL)
    if not match:
        return content, {}

    decorator_content = match.group(1)

    # Extract module_id
    module_id_match = re.search(r"module_id=['\"]([^'\"]+)['\"]", decorator_content)
    module_id = module_id_match.group(1) if module_id_match else None

    # Extract category
    category_match = re.search(r"category=['\"]([^'\"]+)['\"]", decorator_content)
    category = category_match.group(1) if category_match else None

    # Check if already has input_types
    has_input_types = 'input_types=' in decorator_content
    has_output_types = 'output_types=' in decorator_content

    return content, {
        'module_id': module_id,
        'category': category,
        'has_input_types': has_input_types,
        'has_output_types': has_output_types,
        'decorator_match': match,
    }


def add_types_to_module(content: str, metadata: Dict, dry_run: bool = True) -> str:
    """Add input_types, output_types, can_connect_to to module"""

    if metadata['has_input_types'] and metadata['has_output_types']:
        print(f"  ✓ Already has types")
        return content

    module_id = metadata['module_id']
    category = metadata['category']

    if not module_id or not category:
        print(f"  ⚠ Could not extract module_id or category")
        return content

    # Infer types
    inferred = infer_types_for_module(module_id, category)

    # Find insertion point (after color or icon field)
    decorator_match = metadata['decorator_match']
    decorator_start = decorator_match.start()
    decorator_end = decorator_match.end()
    decorator_content = content[decorator_start:decorator_end]

    # Find where to insert (after color line)
    color_match = re.search(r"(color=['\"]#[0-9A-F]{6}['\"],?\s*\n)", decorator_content, re.IGNORECASE)

    if not color_match:
        print(f"  ⚠ Could not find insertion point")
        return content

    insertion_point = decorator_start + color_match.end()

    # Build insertion text
    insertion_lines = []
    insertion_lines.append("\n    # Connection types")

    if not metadata['has_input_types'] and inferred['input_types']:
        insertion_lines.append(f"    input_types={inferred['input_types']},")

    if not metadata['has_output_types'] and inferred['output_types']:
        insertion_lines.append(f"    output_types={inferred['output_types']},")

    if inferred.get('can_receive_from'):
        insertion_lines.append(f"    can_receive_from={inferred['can_receive_from']},")

    if inferred.get('can_connect_to'):
        insertion_lines.append(f"    can_connect_to={inferred['can_connect_to']},")

    insertion_text = '\n'.join(insertion_lines)

    # Insert
    new_content = content[:insertion_point] + insertion_text + content[insertion_point:]

    print(f"  ✓ Added: {', '.join([k for k in ['input_types', 'output_types', 'can_receive_from', 'can_connect_to'] if inferred.get(k)])}")

    return new_content


def update_module_file(file_path: Path, dry_run: bool = True) -> bool:
    """Update a single module file"""
    print(f"\nProcessing: {file_path.name}")

    content, metadata = parse_module_file(file_path)

    if not metadata:
        print(f"  ⚠ No @register_module found")
        return False

    new_content = add_types_to_module(content, metadata, dry_run)

    if new_content != content:
        if not dry_run:
            file_path.write_text(new_content)
            print(f"  ✓ Updated")
        else:
            print(f"  ℹ Would update (dry-run)")
        return True
    else:
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Update modules to comply with specification')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying')
    parser.add_argument('files', nargs='*', help='Specific files to update (default: all)')

    args = parser.parse_args()

    root = Path(__file__).parent.parent
    modules_dir = root / 'src' / 'core' / 'modules'

    # Find module files
    if args.files:
        files_to_update = [Path(f) for f in args.files]
    else:
        files_to_update = []
        for path in modules_dir.rglob('*.py'):
            if '__pycache__' in str(path) or path.name in ['__init__.py', 'base.py', 'registry.py', 'validator.py']:
                continue
            files_to_update.append(path)

    print(f"{'DRY RUN - ' if args.dry_run else ''}Updating {len(files_to_update)} module files...\n")

    updated = 0
    for file_path in files_to_update:
        if update_module_file(file_path, dry_run=args.dry_run):
            updated += 1

    print(f"\n{'Would update' if args.dry_run else 'Updated'} {updated}/{len(files_to_update)} files")

    if args.dry_run:
        print("\nRun without --dry-run to apply changes")


if __name__ == '__main__':
    main()
