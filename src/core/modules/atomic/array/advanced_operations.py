"""
Advanced Array Operations Modules

Provides extended array manipulation capabilities.
"""
from typing import Any, Dict, List
from ...base import BaseModule
from ...registry import register_module


@register_module(
    module_id='array.map',
    version='1.0.0',
    category='array',
    subcategory='transform',
    tags=['array', 'map', 'transform'],
    label='Array Map',
    label_key='modules.array.map.label',
    description='Transform each element in an array',
    description_key='modules.array.map.description',
    icon='MapPin',
    color='#8B5CF6',

    # Connection types
    input_types=['array', 'json'],
    output_types=['array', 'json'],

    # Phase 2: Execution settings
    timeout=None,
    retryable=False,
    concurrent_safe=True,

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=[],

    params_schema={
        'array': {
            'type': 'array',
            'label': 'Array',
            'label_key': 'modules.array.map.params.array.label',
            'description': 'Input array to transform',
            'description_key': 'modules.array.map.params.array.description',
            'required': True
        },
        'operation': {
            'type': 'select',
            'label': 'Operation',
            'label_key': 'modules.array.map.params.operation.label',
            'description': 'Transformation to apply',
            'description_key': 'modules.array.map.params.operation.description',
            'options': [
                {'label': 'Multiply', 'value': 'multiply'},
                {'label': 'Add', 'value': 'add'},
                {'label': 'Extract field', 'value': 'extract'},
                {'label': 'To uppercase', 'value': 'uppercase'},
                {'label': 'To lowercase', 'value': 'lowercase'}
            ],
            'required': True
        },
        'value': {
            'type': 'any',
            'label': 'Value',
            'label_key': 'modules.array.map.params.value.label',
            'description': 'Value for operation (number for math, field name for extract)',
            'description_key': 'modules.array.map.params.value.description',
            'required': False
        }
    },
    output_schema={
        'result': {'type': 'array'},
        'length': {'type': 'number'}
    },
    examples=[
        {
            'title': 'Multiply numbers',
            'params': {
                'array': [1, 2, 3, 4, 5],
                'operation': 'multiply',
                'value': 2
            }
        },
        {
            'title': 'Extract field from objects',
            'params': {
                'array': [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}],
                'operation': 'extract',
                'value': 'name'
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class ArrayMapModule(BaseModule):
    """Array Map Module"""

    def validate_params(self):
        self.array = self.params.get('array', [])
        self.operation = self.params.get('operation')
        self.value = self.params.get('value')

        if not isinstance(self.array, list):
            raise ValueError("array must be a list")

    async def execute(self) -> Any:
        result = []

        for item in self.array:
            if self.operation == 'multiply':
                result.append(item * (self.value or 1))
            elif self.operation == 'add':
                result.append(item + (self.value or 0))
            elif self.operation == 'extract':
                if isinstance(item, dict) and self.value:
                    result.append(item.get(self.value))
                else:
                    result.append(None)
            elif self.operation == 'uppercase':
                result.append(str(item).upper())
            elif self.operation == 'lowercase':
                result.append(str(item).lower())
            else:
                result.append(item)

        return {
            "result": result,
            "length": len(result)
        }


@register_module(
    module_id='array.reduce',
    version='1.0.0',
    category='array',
    subcategory='aggregate',
    tags=['array', 'reduce', 'aggregate'],
    label='Array Reduce',
    label_key='modules.array.reduce.label',
    description='Reduce array to single value',
    description_key='modules.array.reduce.description',
    icon='TrendingDown',
    color='#EF4444',

    # Connection types
    input_types=['array', 'json'],
    output_types=['any'],

    # Phase 2: Execution settings
    timeout=None,
    retryable=False,
    concurrent_safe=True,

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=[],

    params_schema={
        'array': {
            'type': 'array',
            'label': 'Array',
            'label_key': 'modules.array.reduce.params.array.label',
            'description': 'Input array to reduce',
            'description_key': 'modules.array.reduce.params.array.description',
            'required': True
        },
        'operation': {
            'type': 'select',
            'label': 'Operation',
            'label_key': 'modules.array.reduce.params.operation.label',
            'description': 'Reduction operation',
            'description_key': 'modules.array.reduce.params.operation.description',
            'options': [
                {'label': 'Sum', 'value': 'sum'},
                {'label': 'Product', 'value': 'product'},
                {'label': 'Average', 'value': 'average'},
                {'label': 'Min', 'value': 'min'},
                {'label': 'Max', 'value': 'max'},
                {'label': 'Join', 'value': 'join'}
            ],
            'required': True
        },
        'separator': {
            'type': 'string',
            'label': 'Separator',
            'label_key': 'modules.array.reduce.params.separator.label',
            'description': 'Separator for join operation',
            'description_key': 'modules.array.reduce.params.separator.description',
            'default': ',',
            'required': False
        }
    },
    output_schema={
        'result': {'type': 'any'},
        'operation': {'type': 'string'}
    },
    examples=[
        {
            'title': 'Sum numbers',
            'params': {
                'array': [1, 2, 3, 4, 5],
                'operation': 'sum'
            }
        },
        {
            'title': 'Join strings',
            'params': {
                'array': ['Hello', 'World', 'from', 'Flyto2'],
                'operation': 'join',
                'separator': ' '
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class ArrayReduceModule(BaseModule):
    """Array Reduce Module"""

    def validate_params(self):
        self.array = self.params.get('array', [])
        self.operation = self.params.get('operation')
        self.separator = self.params.get('separator', ',')

        if not isinstance(self.array, list):
            raise ValueError("array must be a list")

    async def execute(self) -> Any:
        if not self.array:
            return {"result": None, "operation": self.operation}

        result = None

        if self.operation == 'sum':
            result = sum(self.array)
        elif self.operation == 'product':
            result = 1
            for item in self.array:
                result *= item
        elif self.operation == 'average':
            result = sum(self.array) / len(self.array)
        elif self.operation == 'min':
            result = min(self.array)
        elif self.operation == 'max':
            result = max(self.array)
        elif self.operation == 'join':
            result = self.separator.join(str(item) for item in self.array)

        return {
            "result": result,
            "operation": self.operation
        }


@register_module(
    module_id='array.join',
    version='1.0.0',
    category='array',
    subcategory='transform',
    tags=['array', 'join', 'string'],
    label='Array Join',
    label_key='modules.array.join.label',
    description='Join array elements into string',
    description_key='modules.array.join.description',
    icon='Link',
    color='#10B981',

    # Connection types
    input_types=['array'],
    output_types=['text', 'string'],

    # Phase 2: Execution settings
    timeout=None,
    retryable=False,
    concurrent_safe=True,

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=[],

    params_schema={
        'array': {
            'type': 'array',
            'label': 'Array',
            'label_key': 'modules.array.join.params.array.label',
            'description': 'Array to join',
            'description_key': 'modules.array.join.params.array.description',
            'required': True
        },
        'separator': {
            'type': 'string',
            'label': 'Separator',
            'label_key': 'modules.array.join.params.separator.label',
            'description': 'String to insert between elements',
            'description_key': 'modules.array.join.params.separator.description',
            'default': ',',
            'required': False
        }
    },
    output_schema={
        'result': {'type': 'string'}
    },
    examples=[
        {
            'title': 'Join with comma',
            'params': {
                'array': ['apple', 'banana', 'cherry'],
                'separator': ', '
            }
        },
        {
            'title': 'Join with newline',
            'params': {
                'array': ['Line 1', 'Line 2', 'Line 3'],
                'separator': '\n'
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class ArrayJoinModule(BaseModule):
    """Array Join Module"""

    def validate_params(self):
        self.array = self.params.get('array', [])
        self.separator = self.params.get('separator', ',')

        if not isinstance(self.array, list):
            raise ValueError("array must be a list")

    async def execute(self) -> Any:
        result = self.separator.join(str(item) for item in self.array)

        return {
            "result": result
        }


@register_module(
    module_id='array.flatten',
    version='1.0.0',
    category='array',
    subcategory='transform',
    tags=['array', 'flatten', 'nested'],
    label='Array Flatten',
    label_key='modules.array.flatten.label',
    description='Flatten nested arrays into single array',
    description_key='modules.array.flatten.description',
    icon='Layers',
    color='#8B5CF6',

    # Connection types
    input_types=['array'],
    output_types=['array'],

    # Phase 2: Execution settings
    timeout=None,
    retryable=False,
    concurrent_safe=True,

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=[],

    params_schema={
        'array': {
            'type': 'array',
            'label': 'Array',
            'label_key': 'modules.array.flatten.params.array.label',
            'description': 'Nested array to flatten',
            'description_key': 'modules.array.flatten.params.array.description',
            'required': True
        },
        'depth': {
            'type': 'number',
            'label': 'Depth',
            'label_key': 'modules.array.flatten.params.depth.label',
            'description': 'Depth level to flatten (default: 1, use -1 for infinite)',
            'description_key': 'modules.array.flatten.params.depth.description',
            'default': 1,
            'required': False
        }
    },
    output_schema={
        'result': {'type': 'array'},
        'length': {'type': 'number'}
    },
    examples=[
        {
            'title': 'Flatten one level',
            'params': {
                'array': [[1, 2], [3, 4], [5, 6]],
                'depth': 1
            }
        },
        {
            'title': 'Flatten all levels',
            'params': {
                'array': [[1, [2, [3, [4]]]]],
                'depth': -1
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class ArrayFlattenModule(BaseModule):
    """Array Flatten Module"""

    def validate_params(self):
        self.array = self.params.get('array', [])
        self.depth = self.params.get('depth', 1)

        if not isinstance(self.array, list):
            raise ValueError("array must be a list")

    async def execute(self) -> Any:
        def flatten(arr, depth):
            if depth == 0:
                return arr

            result = []
            for item in arr:
                if isinstance(item, list):
                    if depth == -1:
                        result.extend(flatten(item, -1))
                    else:
                        result.extend(flatten(item, depth - 1))
                else:
                    result.append(item)
            return result

        result = flatten(self.array, self.depth)

        return {
            "result": result,
            "length": len(result)
        }


@register_module(
    module_id='array.chunk',
    version='1.0.0',
    category='array',
    subcategory='transform',
    tags=['array', 'chunk', 'split', 'batch'],
    label='Array Chunk',
    label_key='modules.array.chunk.label',
    description='Split array into chunks of specified size',
    description_key='modules.array.chunk.description',
    icon='Grid',
    color='#8B5CF6',

    # Connection types
    input_types=['array'],
    output_types=['array'],

    # Phase 2: Execution settings
    timeout=None,
    retryable=False,
    concurrent_safe=True,

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=[],

    params_schema={
        'array': {
            'type': 'array',
            'label': 'Array',
            'label_key': 'modules.array.chunk.params.array.label',
            'description': 'Array to chunk',
            'description_key': 'modules.array.chunk.params.array.description',
            'required': True
        },
        'size': {
            'type': 'number',
            'label': 'Chunk Size',
            'label_key': 'modules.array.chunk.params.size.label',
            'description': 'Size of each chunk',
            'description_key': 'modules.array.chunk.params.size.description',
            'required': True,
            'min': 1
        }
    },
    output_schema={
        'result': {'type': 'array'},
        'chunks': {'type': 'number'}
    },
    examples=[
        {
            'title': 'Chunk into groups of 3',
            'params': {
                'array': [1, 2, 3, 4, 5, 6, 7, 8, 9],
                'size': 3
            }
        },
        {
            'title': 'Batch process items',
            'params': {
                'array': ['a', 'b', 'c', 'd', 'e'],
                'size': 2
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class ArrayChunkModule(BaseModule):
    """Array Chunk Module"""

    def validate_params(self):
        self.array = self.params.get('array', [])
        self.size = self.params.get('size')

        if not isinstance(self.array, list):
            raise ValueError("array must be a list")

        if not self.size or self.size < 1:
            raise ValueError("size must be a positive number")

    async def execute(self) -> Any:
        result = []

        for i in range(0, len(self.array), self.size):
            result.append(self.array[i:i + self.size])

        return {
            "result": result,
            "chunks": len(result)
        }


@register_module(
    module_id='array.intersection',
    version='1.0.0',
    category='array',
    subcategory='set',
    tags=['array', 'intersection', 'common'],
    label='Array Intersection',
    label_key='modules.array.intersection.label',
    description='Find common elements between arrays',
    description_key='modules.array.intersection.description',
    icon='Intersect',
    color='#8B5CF6',

    # Connection types
    input_types=['array'],
    output_types=['array'],

    # Phase 2: Execution settings
    timeout=None,
    retryable=False,
    concurrent_safe=True,

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=[],

    params_schema={
        'arrays': {
            'type': 'array',
            'label': 'Arrays',
            'label_key': 'modules.array.intersection.params.arrays.label',
            'description': 'Arrays to find intersection',
            'description_key': 'modules.array.intersection.params.arrays.description',
            'required': True
        }
    },
    output_schema={
        'result': {'type': 'array'},
        'length': {'type': 'number'}
    },
    examples=[
        {
            'title': 'Find common elements',
            'params': {
                'arrays': [[1, 2, 3, 4], [2, 3, 5], [2, 3, 6]]
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class ArrayIntersectionModule(BaseModule):
    """Array Intersection Module"""

    def validate_params(self):
        self.arrays = self.params.get('arrays', [])

        if not isinstance(self.arrays, list) or len(self.arrays) < 2:
            raise ValueError("arrays must be a list with at least 2 arrays")

    async def execute(self) -> Any:
        # Convert first array to set
        result = set(self.arrays[0])

        # Intersect with remaining arrays
        for arr in self.arrays[1:]:
            result = result.intersection(set(arr))

        result_list = list(result)

        return {
            "result": result_list,
            "length": len(result_list)
        }


@register_module(
    module_id='array.difference',
    version='1.0.0',
    category='array',
    subcategory='set',
    tags=['array', 'difference', 'subtract'],
    label='Array Difference',
    label_key='modules.array.difference.label',
    description='Find elements in first array not in others',
    description_key='modules.array.difference.description',
    icon='Minus',
    color='#8B5CF6',

    # Connection types
    input_types=['array'],
    output_types=['array'],

    # Phase 2: Execution settings
    timeout=None,
    retryable=False,
    concurrent_safe=True,

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=[],

    params_schema={
        'array': {
            'type': 'array',
            'label': 'Array',
            'label_key': 'modules.array.difference.params.array.label',
            'description': 'Base array',
            'description_key': 'modules.array.difference.params.array.description',
            'required': True
        },
        'subtract': {
            'type': 'array',
            'label': 'Subtract Arrays',
            'label_key': 'modules.array.difference.params.subtract.label',
            'description': 'Arrays to subtract from base',
            'description_key': 'modules.array.difference.params.subtract.description',
            'required': True
        }
    },
    output_schema={
        'result': {'type': 'array'},
        'length': {'type': 'number'}
    },
    examples=[
        {
            'title': 'Find unique elements',
            'params': {
                'array': [1, 2, 3, 4, 5],
                'subtract': [[2, 4], [5]]
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class ArrayDifferenceModule(BaseModule):
    """Array Difference Module"""

    def validate_params(self):
        self.array = self.params.get('array', [])
        self.subtract = self.params.get('subtract', [])

        if not isinstance(self.array, list):
            raise ValueError("array must be a list")

        if not isinstance(self.subtract, list):
            raise ValueError("subtract must be a list of arrays")

    async def execute(self) -> Any:
        result = set(self.array)

        # Subtract all arrays
        for arr in self.subtract:
            if isinstance(arr, list):
                result = result.difference(set(arr))

        result_list = list(result)

        return {
            "result": result_list,
            "length": len(result_list)
        }
