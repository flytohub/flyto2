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
