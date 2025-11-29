"""
Advanced Math Operations Modules

Provides extended mathematical operations.
"""
from typing import Any, Dict
from ...base import BaseModule
from ...registry import register_module
import math


@register_module(
    module_id='math.round',
    version='1.0.0',
    category='math',
    subcategory='operations',
    tags=['math', 'round', 'number'],
    label='Round Number',
    label_key='modules.math.round.label',
    description='Round number to specified decimal places',
    description_key='modules.math.round.description',
    icon='Circle',
    color='#3B82F6',

    # Connection types
    input_types=['number'],
    output_types=['number'],

    # Phase 2: Execution settings
    timeout=None,
    retryable=False,
    concurrent_safe=True,

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=[],

    params_schema={
        'number': {
            'type': 'number',
            'label': 'Number',
            'label_key': 'modules.math.round.params.number.label',
            'description': 'Number to round',
            'description_key': 'modules.math.round.params.number.description',
            'required': True
        },
        'decimals': {
            'type': 'number',
            'label': 'Decimal Places',
            'label_key': 'modules.math.round.params.decimals.label',
            'description': 'Number of decimal places (default: 0)',
            'description_key': 'modules.math.round.params.decimals.description',
            'default': 0,
            'min': 0,
            'required': False
        }
    },
    output_schema={
        'result': {'type': 'number'},
        'original': {'type': 'number'}
    },
    examples=[
        {
            'title': 'Round to integer',
            'params': {
                'number': 3.14159,
                'decimals': 0
            }
        },
        {
            'title': 'Round to 2 decimals',
            'params': {
                'number': 3.14159,
                'decimals': 2
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class MathRoundModule(BaseModule):
    """Math Round Module"""

    def validate_params(self):
        self.number = self.params.get('number')
        self.decimals = self.params.get('decimals', 0)

        if self.number is None:
            raise ValueError("number is required")

    async def execute(self) -> Any:
        result = round(self.number, self.decimals)

        return {
            "result": result,
            "original": self.number
        }


@register_module(
    module_id='math.floor',
    version='1.0.0',
    category='math',
    subcategory='operations',
    tags=['math', 'floor', 'number'],
    label='Floor Number',
    label_key='modules.math.floor.label',
    description='Round number down to nearest integer',
    description_key='modules.math.floor.description',
    icon='ArrowDown',
    color='#3B82F6',

    # Connection types
    input_types=['number'],
    output_types=['number'],

    # Phase 2: Execution settings
    timeout=None,
    retryable=False,
    concurrent_safe=True,

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=[],

    params_schema={
        'number': {
            'type': 'number',
            'label': 'Number',
            'label_key': 'modules.math.floor.params.number.label',
            'description': 'Number to floor',
            'description_key': 'modules.math.floor.params.number.description',
            'required': True
        }
    },
    output_schema={
        'result': {'type': 'number'},
        'original': {'type': 'number'}
    },
    examples=[
        {
            'title': 'Floor positive number',
            'params': {
                'number': 3.7
            }
        },
        {
            'title': 'Floor negative number',
            'params': {
                'number': -2.3
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class MathFloorModule(BaseModule):
    """Math Floor Module"""

    def validate_params(self):
        self.number = self.params.get('number')

        if self.number is None:
            raise ValueError("number is required")

    async def execute(self) -> Any:
        result = math.floor(self.number)

        return {
            "result": result,
            "original": self.number
        }


@register_module(
    module_id='math.ceil',
    version='1.0.0',
    category='math',
    subcategory='operations',
    tags=['math', 'ceil', 'ceiling', 'number'],
    label='Ceiling Number',
    label_key='modules.math.ceil.label',
    description='Round number up to nearest integer',
    description_key='modules.math.ceil.description',
    icon='ArrowUp',
    color='#3B82F6',

    # Connection types
    input_types=['number'],
    output_types=['number'],

    # Phase 2: Execution settings
    timeout=None,
    retryable=False,
    concurrent_safe=True,

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=[],

    params_schema={
        'number': {
            'type': 'number',
            'label': 'Number',
            'label_key': 'modules.math.ceil.params.number.label',
            'description': 'Number to ceil',
            'description_key': 'modules.math.ceil.params.number.description',
            'required': True
        }
    },
    output_schema={
        'result': {'type': 'number'},
        'original': {'type': 'number'}
    },
    examples=[
        {
            'title': 'Ceiling positive number',
            'params': {
                'number': 3.2
            }
        },
        {
            'title': 'Ceiling negative number',
            'params': {
                'number': -2.7
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class MathCeilModule(BaseModule):
    """Math Ceiling Module"""

    def validate_params(self):
        self.number = self.params.get('number')

        if self.number is None:
            raise ValueError("number is required")

    async def execute(self) -> Any:
        result = math.ceil(self.number)

        return {
            "result": result,
            "original": self.number
        }


@register_module(
    module_id='math.abs',
    version='1.0.0',
    category='math',
    subcategory='operations',
    tags=['math', 'absolute', 'abs', 'number'],
    label='Absolute Value',
    label_key='modules.math.abs.label',
    description='Get absolute value of a number',
    description_key='modules.math.abs.description',
    icon='Maximize2',
    color='#3B82F6',

    # Connection types
    input_types=['number'],
    output_types=['number'],

    # Phase 2: Execution settings
    timeout=None,
    retryable=False,
    concurrent_safe=True,

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=[],

    params_schema={
        'number': {
            'type': 'number',
            'label': 'Number',
            'label_key': 'modules.math.abs.params.number.label',
            'description': 'Number to get absolute value',
            'description_key': 'modules.math.abs.params.number.description',
            'required': True
        }
    },
    output_schema={
        'result': {'type': 'number'},
        'original': {'type': 'number'},
        'was_negative': {'type': 'boolean'}
    },
    examples=[
        {
            'title': 'Absolute of negative',
            'params': {
                'number': -42
            }
        },
        {
            'title': 'Absolute of positive',
            'params': {
                'number': 42
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class MathAbsModule(BaseModule):
    """Math Absolute Value Module"""

    def validate_params(self):
        self.number = self.params.get('number')

        if self.number is None:
            raise ValueError("number is required")

    async def execute(self) -> Any:
        result = abs(self.number)

        return {
            "result": result,
            "original": self.number,
            "was_negative": self.number < 0
        }


@register_module(
    module_id='math.power',
    version='1.0.0',
    category='math',
    subcategory='operations',
    tags=['math', 'power', 'exponent', 'number'],
    label='Power/Exponent',
    label_key='modules.math.power.label',
    description='Raise number to a power',
    description_key='modules.math.power.description',
    icon='Zap',
    color='#3B82F6',

    # Connection types
    input_types=['number'],
    output_types=['number'],

    # Phase 2: Execution settings
    timeout=None,
    retryable=False,
    concurrent_safe=True,

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=[],

    params_schema={
        'base': {
            'type': 'number',
            'label': 'Base',
            'label_key': 'modules.math.power.params.base.label',
            'description': 'Base number',
            'description_key': 'modules.math.power.params.base.description',
            'required': True
        },
        'exponent': {
            'type': 'number',
            'label': 'Exponent',
            'label_key': 'modules.math.power.params.exponent.label',
            'description': 'Power to raise to',
            'description_key': 'modules.math.power.params.exponent.description',
            'required': True
        }
    },
    output_schema={
        'result': {'type': 'number'},
        'base': {'type': 'number'},
        'exponent': {'type': 'number'}
    },
    examples=[
        {
            'title': 'Square a number',
            'params': {
                'base': 5,
                'exponent': 2
            }
        },
        {
            'title': 'Cube root',
            'params': {
                'base': 27,
                'exponent': 0.333333
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class MathPowerModule(BaseModule):
    """Math Power Module"""

    def validate_params(self):
        self.base = self.params.get('base')
        self.exponent = self.params.get('exponent')

        if self.base is None or self.exponent is None:
            raise ValueError("base and exponent are required")

    async def execute(self) -> Any:
        result = math.pow(self.base, self.exponent)

        return {
            "result": result,
            "base": self.base,
            "exponent": self.exponent
        }
