#!/usr/bin/env python3
"""
Module Template Generator

Creates a new module with all required fields pre-filled according to
the Module Specification.

Usage:
    python scripts/create_module.py \\
        --category data \\
        --subcategory xml \\
        --action parse \\
        --label "Parse XML"

This will create: src/core/modules/third_party/data/xml_parser.py
"""

import argparse
import sys
from pathlib import Path
from textwrap import dedent


MODULE_TEMPLATE = '''"""
{description}
"""

from typing import Any, Dict
from ...base import BaseModule
from ...registry import register_module


@register_module(
    # Identity
    module_id='{module_id}',
    version='1.0.0',

    # Classification
    category='{category}',
    subcategory='{subcategory}',
    tags={tags},

    # Display
    label='{label}',
    label_key='{label_key}',
    description='{description}',
    description_key='{description_key}',

    # Visual
    icon='{icon}',
    color='{color}',

    # Connection types (IMPORTANT: Define what this module accepts/produces)
    input_types={input_types},
    output_types={output_types},

    # Schema
    params_schema={{
        {params_schema}
    }},
    output_schema={{
        {output_schema}
    }},

    # Documentation
    examples=[
        {{
            'title': '{example_title}',
            'title_key': '{example_title_key}',
            'params': {{
                {example_params}
            }}
        }}
    ],
    author='Flyto2 Team',
    license='MIT'
)
async def {function_name}(context):
    """
    {function_docstring}

    Args:
        context: Execution context containing params, config, etc.

    Returns:
        Dict with outputs defined in output_schema
    """
    params = context['params']

    # TODO: Implement your module logic here
    # Example:
    # data = params['input']
    # result = process_data(data)

    return {{
        # TODO: Return outputs matching output_schema
        # Example:
        # 'result': result,
        # 'success': True,
    }}
'''


def generate_module(
    category: str,
    subcategory: str,
    action: str,
    label: str,
    description: str = None,
    icon: str = 'Box',
    color: str = '#6B7280',
) -> str:
    """Generate module code from template"""

    # Generate derived values
    module_id = f'{category}.{subcategory}.{action}'
    function_name = f'{subcategory}_{action}'.replace('.', '_')
    label_key = f'modules.{category}.{subcategory}.{action}.label'
    description_key = f'modules.{category}.{subcategory}.{action}.description'

    if not description:
        description = f'{label} module'

    # Generate tags
    tags = [category, subcategory, action, 'integration' if category in ['ai', 'notification', 'database'] else 'atomic']

    # Default input/output types (user should customize)
    input_types = "['text']"
    output_types = "['json']"

    # Default params (user should customize)
    params_schema = """'input': {
            'type': 'string',
            'label': 'Input',
            'label_key': 'modules.{category}.{subcategory}.{action}.params.input.label',
            'description': 'Input data',
            'description_key': 'modules.{category}.{subcategory}.{action}.params.input.description',
            'required': True,
        }""".format(category=category, subcategory=subcategory, action=action)

    # Default output
    output_schema = """'result': {
            'type': 'object',
            'description': 'Processing result',
        }"""

    # Example
    example_title = f'{label} example'
    example_title_key = f'modules.{category}.{subcategory}.{action}.examples.basic.title'
    example_params = "'input': 'example value'"

    function_docstring = description

    return MODULE_TEMPLATE.format(
        module_id=module_id,
        category=category,
        subcategory=subcategory,
        tags=str(tags),
        label=label,
        label_key=label_key,
        description=description,
        description_key=description_key,
        icon=icon,
        color=color,
        input_types=input_types,
        output_types=output_types,
        params_schema=params_schema,
        output_schema=output_schema,
        example_title=example_title,
        example_title_key=example_title_key,
        example_params=example_params,
        function_name=function_name,
        function_docstring=function_docstring,
    )


def get_output_path(category: str, subcategory: str, action: str) -> Path:
    """Determine output file path based on category"""
    root = Path(__file__).parent.parent
    modules_dir = root / 'src' / 'core' / 'modules'

    # Determine if atomic or third_party
    atomic_categories = {'browser', 'data', 'utility', 'file', 'string', 'array', 'math'}

    if category in atomic_categories:
        base_dir = modules_dir / 'atomic' / category
    else:
        base_dir = modules_dir / 'third_party' / category

    # Create directory if needed
    base_dir.mkdir(parents=True, exist_ok=True)

    # Filename
    filename = f'{subcategory}_{action}.py'.replace('.', '_')
    return base_dir / filename


def main():
    parser = argparse.ArgumentParser(
        description='Generate a new Flyto2 module from template'
    )
    parser.add_argument(
        '--category',
        required=True,
        help='Module category (e.g., data, notification, ai)'
    )
    parser.add_argument(
        '--subcategory',
        required=True,
        help='Module subcategory (e.g., json, slack, openai)'
    )
    parser.add_argument(
        '--action',
        required=True,
        help='Module action (e.g., parse, send_message, chat)'
    )
    parser.add_argument(
        '--label',
        required=True,
        help='Human-readable label (e.g., "Parse JSON")'
    )
    parser.add_argument(
        '--description',
        help='Module description (optional)'
    )
    parser.add_argument(
        '--icon',
        default='Box',
        help='Lucide icon name (default: Box)'
    )
    parser.add_argument(
        '--color',
        default='#6B7280',
        help='Hex color code (default: #6B7280)'
    )
    parser.add_argument(
        '--output',
        help='Custom output path (optional)'
    )

    args = parser.parse_args()

    # Generate module code
    code = generate_module(
        category=args.category,
        subcategory=args.subcategory,
        action=args.action,
        label=args.label,
        description=args.description,
        icon=args.icon,
        color=args.color,
    )

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = get_output_path(args.category, args.subcategory, args.action)

    # Check if file exists
    if output_path.exists():
        print(f"Error: File already exists: {output_path}")
        print("Use --output to specify a different path")
        sys.exit(1)

    # Write file
    output_path.write_text(code)

    print(f"✓ Created module: {output_path}")
    print(f"\nModule ID: {args.category}.{args.subcategory}.{args.action}")
    print(f"Label: {args.label}")
    print(f"\nNext steps:")
    print(f"1. Edit {output_path}")
    print(f"2. Customize params_schema, output_schema, and implementation")
    print(f"3. Add i18n translations to i18n/en.json")
    print(f"4. Run: python scripts/lint_modules.py {output_path}")
    print(f"5. Test your module")
    print(f"6. Submit PR")


if __name__ == '__main__':
    main()
