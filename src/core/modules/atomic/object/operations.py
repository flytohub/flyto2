"""
Object Operations Modules

Provides object/dictionary manipulation capabilities.
"""
from typing import Any, Dict
from ...base import BaseModule
from ...registry import register_module


@register_module(
    module_id='object.keys',
    version='1.0.0',
    category='data',
    subcategory='object',
    tags=['object', 'keys', 'dictionary'],
    label='Object Keys',
    label_key='modules.object.keys.label',
    description='Get all keys from an object',
    description_key='modules.object.keys.description',
    icon='Key',
    color='#F59E0B',

    # Connection types
    input_types=['json'],
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
        'object': {
            'type': 'json',
            'label': 'Object',
            'label_key': 'modules.object.keys.params.object.label',
            'description': 'Input object/dictionary',
            'description_key': 'modules.object.keys.params.object.description',
            'required': True
        }
    },
    output_schema={
        'keys': {'type': 'array'},
        'count': {'type': 'number'}
    },
    examples=[
        {
            'title': 'Get object keys',
            'params': {
                'object': {'name': 'John', 'age': 30, 'city': 'NYC'}
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class ObjectKeysModule(BaseModule):
    """Object Keys Module"""

    def validate_params(self):
        self.obj = self.params.get('object')

        if not isinstance(self.obj, dict):
            raise ValueError("object must be a dictionary")

    async def execute(self) -> Any:
        keys = list(self.obj.keys())

        return {
            "keys": keys,
            "count": len(keys)
        }


@register_module(
    module_id='object.values',
    version='1.0.0',
    category='data',
    subcategory='object',
    tags=['object', 'values', 'dictionary'],
    label='Object Values',
    label_key='modules.object.values.label',
    description='Get all values from an object',
    description_key='modules.object.values.description',
    icon='List',
    color='#F59E0B',

    # Connection types
    input_types=['json'],
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
        'object': {
            'type': 'json',
            'label': 'Object',
            'label_key': 'modules.object.values.params.object.label',
            'description': 'Input object/dictionary',
            'description_key': 'modules.object.values.params.object.description',
            'required': True
        }
    },
    output_schema={
        'values': {'type': 'array'},
        'count': {'type': 'number'}
    },
    examples=[
        {
            'title': 'Get object values',
            'params': {
                'object': {'name': 'John', 'age': 30, 'city': 'NYC'}
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class ObjectValuesModule(BaseModule):
    """Object Values Module"""

    def validate_params(self):
        self.obj = self.params.get('object')

        if not isinstance(self.obj, dict):
            raise ValueError("object must be a dictionary")

    async def execute(self) -> Any:
        values = list(self.obj.values())

        return {
            "values": values,
            "count": len(values)
        }


@register_module(
    module_id='object.merge',
    version='1.0.0',
    category='data',
    subcategory='object',
    tags=['object', 'merge', 'combine'],
    label='Object Merge',
    label_key='modules.object.merge.label',
    description='Merge multiple objects into one',
    description_key='modules.object.merge.description',
    icon='Merge',
    color='#F59E0B',

    # Connection types
    input_types=['json'],
    output_types=['json'],

    # Phase 2: Execution settings
    timeout=None,
    retryable=False,
    concurrent_safe=True,

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=[],

    params_schema={
        'objects': {
            'type': 'array',
            'label': 'Objects',
            'label_key': 'modules.object.merge.params.objects.label',
            'description': 'Array of objects to merge',
            'description_key': 'modules.object.merge.params.objects.description',
            'required': True
        }
    },
    output_schema={
        'result': {'type': 'json'}
    },
    examples=[
        {
            'title': 'Merge user data',
            'params': {
                'objects': [
                    {'name': 'John', 'age': 30},
                    {'city': 'NYC', 'country': 'USA'},
                    {'job': 'Engineer'}
                ]
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class ObjectMergeModule(BaseModule):
    """Object Merge Module"""

    def validate_params(self):
        self.objects = self.params.get('objects', [])

        if not isinstance(self.objects, list):
            raise ValueError("objects must be an array")

    async def execute(self) -> Any:
        result = {}

        for obj in self.objects:
            if isinstance(obj, dict):
                result.update(obj)

        return {
            "result": result
        }


@register_module(
    module_id='object.pick',
    version='1.0.0',
    category='data',
    subcategory='object',
    tags=['object', 'pick', 'select'],
    label='Object Pick',
    label_key='modules.object.pick.label',
    description='Pick specific keys from an object',
    description_key='modules.object.pick.description',
    icon='Check',
    color='#F59E0B',

    # Connection types
    input_types=['json'],
    output_types=['json'],

    # Phase 2: Execution settings
    timeout=None,
    retryable=False,
    concurrent_safe=True,

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=[],

    params_schema={
        'object': {
            'type': 'json',
            'label': 'Object',
            'label_key': 'modules.object.pick.params.object.label',
            'description': 'Input object',
            'description_key': 'modules.object.pick.params.object.description',
            'required': True
        },
        'keys': {
            'type': 'array',
            'label': 'Keys',
            'label_key': 'modules.object.pick.params.keys.label',
            'description': 'Keys to pick',
            'description_key': 'modules.object.pick.params.keys.description',
            'required': True
        }
    },
    output_schema={
        'result': {'type': 'json'}
    },
    examples=[
        {
            'title': 'Pick user fields',
            'params': {
                'object': {'name': 'John', 'age': 30, 'email': 'john@example.com', 'password': 'secret'},
                'keys': ['name', 'email']
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class ObjectPickModule(BaseModule):
    """Object Pick Module"""

    def validate_params(self):
        self.obj = self.params.get('object')
        self.keys = self.params.get('keys', [])

        if not isinstance(self.obj, dict):
            raise ValueError("object must be a dictionary")

        if not isinstance(self.keys, list):
            raise ValueError("keys must be an array")

    async def execute(self) -> Any:
        result = {key: self.obj[key] for key in self.keys if key in self.obj}

        return {
            "result": result
        }


@register_module(
    module_id='object.omit',
    version='1.0.0',
    category='data',
    subcategory='object',
    tags=['object', 'omit', 'exclude'],
    label='Object Omit',
    label_key='modules.object.omit.label',
    description='Omit specific keys from an object',
    description_key='modules.object.omit.description',
    icon='X',
    color='#F59E0B',

    # Connection types
    input_types=['json'],
    output_types=['json'],

    # Phase 2: Execution settings
    timeout=None,
    retryable=False,
    concurrent_safe=True,

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=[],

    params_schema={
        'object': {
            'type': 'json',
            'label': 'Object',
            'label_key': 'modules.object.omit.params.object.label',
            'description': 'Input object',
            'description_key': 'modules.object.omit.params.object.description',
            'required': True
        },
        'keys': {
            'type': 'array',
            'label': 'Keys',
            'label_key': 'modules.object.omit.params.keys.label',
            'description': 'Keys to omit',
            'description_key': 'modules.object.omit.params.keys.description',
            'required': True
        }
    },
    output_schema={
        'result': {'type': 'json'}
    },
    examples=[
        {
            'title': 'Omit sensitive fields',
            'params': {
                'object': {'name': 'John', 'age': 30, 'password': 'secret', 'ssn': '123-45-6789'},
                'keys': ['password', 'ssn']
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class ObjectOmitModule(BaseModule):
    """Object Omit Module"""

    def validate_params(self):
        self.obj = self.params.get('object')
        self.keys = self.params.get('keys', [])

        if not isinstance(self.obj, dict):
            raise ValueError("object must be a dictionary")

        if not isinstance(self.keys, list):
            raise ValueError("keys must be an array")

    async def execute(self) -> Any:
        result = {key: value for key, value in self.obj.items() if key not in self.keys}

        return {
            "result": result
        }
