"""
Advanced String Operations Modules

Provides extended string manipulation capabilities.
"""
from typing import Any, Dict
from ...base import BaseModule
from ...registry import register_module


@register_module(
    module_id='string.trim',
    version='1.0.0',
    category='string',
    subcategory='transform',
    tags=['string', 'trim', 'whitespace'],
    label='Trim String',
    label_key='modules.string.trim.label',
    description='Remove leading and trailing whitespace',
    description_key='modules.string.trim.description',
    icon='Scissors',
    color='#F59E0B',

    # Connection types
    input_types=['text', 'string'],
    output_types=['text', 'string'],

    # Phase 2: Execution settings
    timeout=None,  # Instant operation
    retryable=False,
    concurrent_safe=True,  # Stateless operation

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=[],

    params_schema={
        'text': {
            'type': 'string',
            'label': 'Text',
            'label_key': 'modules.string.trim.params.text.label',
            'description': 'Text to trim',
            'description_key': 'modules.string.trim.params.text.description',
            'required': True
        },
        'characters': {
            'type': 'string',
            'label': 'Characters',
            'label_key': 'modules.string.trim.params.characters.label',
            'description': 'Specific characters to trim (default: whitespace)',
            'description_key': 'modules.string.trim.params.characters.description',
            'required': False
        }
    },
    output_schema={
        'result': {'type': 'string'},
        'original_length': {'type': 'number'},
        'trimmed_length': {'type': 'number'}
    },
    examples=[
        {
            'title': 'Trim whitespace',
            'params': {
                'text': '  Hello World  '
            }
        },
        {
            'title': 'Trim specific characters',
            'params': {
                'text': '***Important***',
                'characters': '*'
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class StringTrimModule(BaseModule):
    """Trim String Module"""

    def validate_params(self):
        self.text = self.params.get('text', '')
        self.characters = self.params.get('characters')

    async def execute(self) -> Any:
        original_length = len(self.text)

        if self.characters:
            result = self.text.strip(self.characters)
        else:
            result = self.text.strip()

        return {
            "result": result,
            "original_length": original_length,
            "trimmed_length": len(result)
        }


@register_module(
    module_id='string.lowercase',
    version='1.0.0',
    category='string',
    subcategory='transform',
    tags=['string', 'lowercase', 'case'],
    label='Lowercase String',
    label_key='modules.string.lowercase.label',
    description='Convert string to lowercase',
    description_key='modules.string.lowercase.description',
    icon='ArrowDown',
    color='#3B82F6',

    # Connection types
    input_types=['text', 'string'],
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
        'text': {
            'type': 'string',
            'label': 'Text',
            'label_key': 'modules.string.lowercase.params.text.label',
            'description': 'Text to convert to lowercase',
            'description_key': 'modules.string.lowercase.params.text.description',
            'required': True
        }
    },
    output_schema={
        'result': {'type': 'string'}
    },
    examples=[
        {
            'title': 'Convert to lowercase',
            'params': {
                'text': 'Hello WORLD'
            }
        },
        {
            'title': 'Normalize email',
            'params': {
                'text': 'User@Example.COM'
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class StringLowercaseModule(BaseModule):
    """Lowercase String Module"""

    def validate_params(self):
        self.text = self.params.get('text', '')

    async def execute(self) -> Any:
        return {
            "result": self.text.lower()
        }


@register_module(
    module_id='string.uppercase',
    version='1.0.0',
    category='string',
    subcategory='transform',
    tags=['string', 'uppercase', 'case'],
    label='Uppercase String',
    label_key='modules.string.uppercase.label',
    description='Convert string to uppercase',
    description_key='modules.string.uppercase.description',
    icon='ArrowUp',
    color='#EF4444',

    # Connection types
    input_types=['text', 'string'],
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
        'text': {
            'type': 'string',
            'label': 'Text',
            'label_key': 'modules.string.uppercase.params.text.label',
            'description': 'Text to convert to uppercase',
            'description_key': 'modules.string.uppercase.params.text.description',
            'required': True
        }
    },
    output_schema={
        'result': {'type': 'string'}
    },
    examples=[
        {
            'title': 'Convert to uppercase',
            'params': {
                'text': 'Hello World'
            }
        },
        {
            'title': 'Make heading',
            'params': {
                'text': 'important notice'
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class StringUppercaseModule(BaseModule):
    """Uppercase String Module"""

    def validate_params(self):
        self.text = self.params.get('text', '')

    async def execute(self) -> Any:
        return {
            "result": self.text.upper()
        }


@register_module(
    module_id='string.titlecase',
    version='1.0.0',
    category='string',
    subcategory='transform',
    tags=['string', 'titlecase', 'case'],
    label='Title Case String',
    label_key='modules.string.titlecase.label',
    description='Convert string to title case',
    description_key='modules.string.titlecase.description',
    icon='Type',
    color='#8B5CF6',

    # Connection types
    input_types=['text', 'string'],
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
        'text': {
            'type': 'string',
            'label': 'Text',
            'label_key': 'modules.string.titlecase.params.text.label',
            'description': 'Text to convert to title case',
            'description_key': 'modules.string.titlecase.params.text.description',
            'required': True
        }
    },
    output_schema={
        'result': {'type': 'string'}
    },
    examples=[
        {
            'title': 'Convert to title case',
            'params': {
                'text': 'hello world from flyto2'
            }
        },
        {
            'title': 'Format name',
            'params': {
                'text': 'john doe'
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class StringTitlecaseModule(BaseModule):
    """Title Case String Module"""

    def validate_params(self):
        self.text = self.params.get('text', '')

    async def execute(self) -> Any:
        return {
            "result": self.text.title()
        }
