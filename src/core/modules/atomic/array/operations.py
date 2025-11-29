"""
Array Operation Modules
Array data manipulation and transformation
"""

from typing import Any, Dict
from ...base import BaseModule
from ...registry import register_module


@register_module(
    module_id='array.filter',
    version='1.0.0',
    category='atomic',
    subcategory='array',
    tags=['array', 'filter', 'data', 'atomic'],
    label='Filter Array',
    label_key='modules.array.filter.label',
    description='Filter array elements by condition',
    description_key='modules.array.filter.description',
    icon='Filter',
    color='#10B981',

    # Connection types
    input_types=['any'],
    output_types=['any'],    params_schema={
        'array': {
            'type': 'array',
            'label': 'Array',
            'label_key': 'modules.array.filter.params.array.label',
            'description': 'Array to filter',
            'description_key': 'modules.array.filter.params.array.description',
            'required': True
        },
        'condition': {
            'type': 'string',
            'label': 'Condition',
            'label_key': 'modules.array.filter.params.condition.label',
            'description': 'Filter condition (gt, lt, eq, ne, contains)',
            'description_key': 'modules.array.filter.params.condition.description',
            'required': True,
            'options': [
                {'value': 'gt', 'label': 'Greater Than'},
                {'value': 'lt', 'label': 'Less Than'},
                {'value': 'eq', 'label': 'Equal'},
                {'value': 'ne', 'label': 'Not Equal'},
                {'value': 'contains', 'label': 'Contains'}
            ]
        },
        'value': {
            'type': 'string',
            'label': 'Value',
            'label_key': 'modules.array.filter.params.value.label',
            'description': 'Value to compare against',
            'description_key': 'modules.array.filter.params.value.description',
            'required': True
        }
    },
    output_schema={
        'filtered': {
            'type': 'array',
            'description': 'Filtered array'
        },
        'count': {
            'type': 'number',
            'description': 'Number of items in filtered array'
        }
    },
    examples=[
        {
            'title': 'Filter numbers greater than 5',
            'title_key': 'modules.array.filter.examples.numbers.title',
            'params': {
                'array': [1, 5, 10, 15, 3],
                'condition': 'gt',
                'value': '5'
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
async def array_filter(context):
    """Filter array by condition"""
    params = context['params']
    array = params['array']
    condition = params['condition']
    value = params['value']

    # Try to convert value to number if possible
    try:
        value = float(value)
    except (ValueError, TypeError):
        pass

    filtered = []
    for item in array:
        if condition == 'gt':
            if isinstance(item, (int, float)) and isinstance(value, (int, float)) and item > value:
                filtered.append(item)
        elif condition == 'lt':
            if isinstance(item, (int, float)) and isinstance(value, (int, float)) and item < value:
                filtered.append(item)
        elif condition == 'eq':
            if item == value:
                filtered.append(item)
        elif condition == 'ne':
            if item != value:
                filtered.append(item)
        elif condition == 'contains':
            if isinstance(item, str) and isinstance(value, str) and value in item:
                filtered.append(item)

    return {
        'filtered': filtered,
        'count': len(filtered)
    }


@register_module(
    module_id='array.sort',
    version='1.0.0',
    category='atomic',
    subcategory='array',
    tags=['array', 'sort', 'data', 'atomic'],
    label='Sort Array',
    label_key='modules.array.sort.label',
    description='Sort array elements in ascending or descending order',
    description_key='modules.array.sort.description',
    icon='ArrowUpDown',
    color='#10B981',
    params_schema={
        'array': {
            'type': 'array',
            'label': 'Array',
            'label_key': 'modules.array.sort.params.array.label',
            'description': 'Array to sort',
            'description_key': 'modules.array.sort.params.array.description',
            'required': True
        },
        'order': {
            'type': 'string',
            'label': 'Order',
            'label_key': 'modules.array.sort.params.order.label',
            'description': 'Sort order',
            'description_key': 'modules.array.sort.params.order.description',
            'default': 'asc',
            'required': False,
            'options': [
                {'value': 'asc', 'label': 'Ascending'},
                {'value': 'desc', 'label': 'Descending'}
            ]
        }
    },
    output_schema={
        'sorted': {
            'type': 'array',
            'description': 'Sorted array'
        },
        'count': {
            'type': 'number',
            'description': 'Number of items'
        }
    },
    examples=[
        {
            'title': 'Sort numbers ascending',
            'title_key': 'modules.array.sort.examples.ascending.title',
            'params': {
                'array': [5, 2, 8, 1, 9],
                'order': 'asc'
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
async def array_sort(context):
    """Sort array elements"""
    params = context['params']
    array = params['array']
    order = params.get('order', 'asc')

    sorted_array = sorted(array, reverse=(order == 'desc'))

    return {
        'sorted': sorted_array,
        'count': len(sorted_array)
    }


@register_module(
    module_id='array.unique',
    version='1.0.0',
    category='atomic',
    subcategory='array',
    tags=['array', 'unique', 'dedupe', 'atomic'],
    label='Array Unique',
    label_key='modules.array.unique.label',
    description='Remove duplicate values from array',
    description_key='modules.array.unique.description',
    icon='Layers',
    color='#10B981',
    params_schema={
        'array': {
            'type': 'array',
            'label': 'Array',
            'label_key': 'modules.array.unique.params.array.label',
            'description': 'Array to deduplicate',
            'description_key': 'modules.array.unique.params.array.description',
            'required': True
        },
        'preserve_order': {
            'type': 'boolean',
            'label': 'Preserve Order',
            'label_key': 'modules.array.unique.params.preserve_order.label',
            'description': 'Maintain original order of elements',
            'description_key': 'modules.array.unique.params.preserve_order.description',
            'default': True,
            'required': False
        }
    },
    output_schema={
        'unique': {
            'type': 'array',
            'description': 'Array with unique values'
        },
        'count': {
            'type': 'number',
            'description': 'Number of unique items'
        },
        'duplicates_removed': {
            'type': 'number',
            'description': 'Number of duplicates removed'
        }
    },
    examples=[
        {
            'title': 'Remove duplicates',
            'title_key': 'modules.array.unique.examples.simple.title',
            'params': {
                'array': [1, 2, 2, 3, 4, 3, 5],
                'preserve_order': True
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
async def array_unique(context):
    """Remove duplicate values from array"""
    params = context['params']
    array = params['array']
    preserve_order = params.get('preserve_order', True)

    original_count = len(array)

    if preserve_order:
        seen = set()
        unique = []
        for item in array:
            # Handle unhashable types
            try:
                if item not in seen:
                    seen.add(item)
                    unique.append(item)
            except TypeError:
                # For unhashable types, do linear search
                if item not in unique:
                    unique.append(item)
    else:
        unique = list(set(array))

    return {
        'unique': unique,
        'count': len(unique),
        'duplicates_removed': original_count - len(unique)
    }
