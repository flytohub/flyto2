"""
Utility Modules
Helper modules for delays, random data, date/time operations, etc.
"""
from typing import Any, Dict
from ...base import BaseModule
from ...registry import register_module
import asyncio
import random
import string
from datetime import datetime, timedelta
import hashlib
import uuid


@register_module(
    module_id='utility.delay',
    version='1.0.0',
    category='utility',
    tags=['utility', 'delay', 'sleep', 'wait', 'timing'],
    label='Delay/Sleep',
    label_key='modules.utility.delay.label',
    description='Pause workflow execution for specified duration',
    description_key='modules.utility.delay.description',
    icon='Clock',
    color='#6B7280',

    # Connection types
    input_types=['any'],
    output_types=['any'],    params_schema={
        'duration_ms': {
            'type': 'number',
            'label': 'Duration (milliseconds)',
            'label_key': 'modules.utility.delay.params.duration_ms.label',
            'description': 'How long to wait in milliseconds',
            'description_key': 'modules.utility.delay.params.duration_ms.description',
            'placeholder': 1000,
            'default': 1000,
            'min': 0,
            'max': 3600000,  # Max 1 hour
            'required': False
        },
        'duration_seconds': {
            'type': 'number',
            'label': 'Duration (seconds)',
            'label_key': 'modules.utility.delay.params.duration_seconds.label',
            'description': 'Alternative: duration in seconds',
            'description_key': 'modules.utility.delay.params.duration_seconds.description',
            'placeholder': 1,
            'min': 0,
            'max': 3600,
            'required': False
        }
    },
    output_schema={
        'status': {'type': 'string'},
        'waited_ms': {'type': 'number', 'description': 'Actual wait time in ms'}
    },
    examples=[
        {
            'name': 'Wait 2 seconds',
            'params': {
                'duration_seconds': 2
            }
        },
        {
            'name': 'Wait 500ms',
            'params': {
                'duration_ms': 500
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class DelayModule(BaseModule):
    """Pause workflow execution"""

    module_name = "Delay/Sleep"
    module_description = "Pause workflow execution for specified duration"

    def validate_params(self):
        # Support both milliseconds and seconds
        self.duration_ms = self.params.get('duration_ms')
        self.duration_seconds = self.params.get('duration_seconds')

        if self.duration_ms is None and self.duration_seconds is None:
            self.duration_ms = 1000  # Default 1 second

        if self.duration_seconds is not None:
            self.duration_ms = self.duration_seconds * 1000

    async def execute(self) -> Any:
        await asyncio.sleep(self.duration_ms / 1000)

        return {
            'status': 'success',
            'waited_ms': self.duration_ms
        }


@register_module(
    module_id='utility.random.number',
    version='1.0.0',
    category='utility',
    tags=['utility', 'random', 'number', 'generator'],
    label='Random Number',
    label_key='modules.utility.random.number.label',
    description='Generate random number in range',
    description_key='modules.utility.random.number.description',
    icon='Shuffle',
    color='#EC4899',
    params_schema={
        'min': {
            'type': 'number',
            'label': 'Minimum',
            'label_key': 'modules.utility.random.number.params.min.label',
            'description': 'Minimum value (inclusive)',
            'description_key': 'modules.utility.random.number.params.min.description',
            'default': 0,
            'required': False
        },
        'max': {
            'type': 'number',
            'label': 'Maximum',
            'label_key': 'modules.utility.random.number.params.max.label',
            'description': 'Maximum value (inclusive)',
            'description_key': 'modules.utility.random.number.params.max.description',
            'default': 100,
            'required': False
        },
        'decimals': {
            'type': 'number',
            'label': 'Decimal Places',
            'label_key': 'modules.utility.random.number.params.decimals.label',
            'description': 'Number of decimal places (0 for integers)',
            'description_key': 'modules.utility.random.number.params.decimals.description',
            'default': 0,
            'min': 0,
            'max': 10,
            'required': False
        }
    },
    output_schema={
        'status': {'type': 'string'},
        'value': {'type': 'number', 'description': 'Random number'}
    },
    examples=[
        {
            'name': 'Random integer 1-100',
            'params': {
                'min': 1,
                'max': 100,
                'decimals': 0
            }
        },
        {
            'name': 'Random float 0-1',
            'params': {
                'min': 0,
                'max': 1,
                'decimals': 2
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class RandomNumberModule(BaseModule):
    """Generate random number"""

    module_name = "Random Number"
    module_description = "Generate random number in specified range"

    def validate_params(self):
        self.min = self.params.get('min', 0)
        self.max = self.params.get('max', 100)
        self.decimals = self.params.get('decimals', 0)

        if self.min > self.max:
            raise ValueError("min must be less than or equal to max")

    async def execute(self) -> Any:
        if self.decimals == 0:
            value = random.randint(int(self.min), int(self.max))
        else:
            value = random.uniform(self.min, self.max)
            value = round(value, self.decimals)

        return {
            'status': 'success',
            'value': value
        }


@register_module(
    module_id='utility.random.string',
    version='1.0.0',
    category='utility',
    tags=['utility', 'random', 'string', 'generator', 'uuid'],
    label='Random String',
    label_key='modules.utility.random.string.label',
    description='Generate random string or UUID',
    description_key='modules.utility.random.string.description',
    icon='Key',
    color='#EC4899',
    params_schema={
        'length': {
            'type': 'number',
            'label': 'Length',
            'label_key': 'modules.utility.random.string.params.length.label',
            'description': 'String length',
            'description_key': 'modules.utility.random.string.params.length.description',
            'default': 16,
            'min': 1,
            'max': 256,
            'required': False
        },
        'charset': {
            'type': 'select',
            'label': 'Character Set',
            'label_key': 'modules.utility.random.string.params.charset.label',
            'description': 'Which characters to use',
            'description_key': 'modules.utility.random.string.params.charset.description',
            'options': [
                {'value': 'alphanumeric', 'label': 'Alphanumeric (a-z, A-Z, 0-9)'},
                {'value': 'letters', 'label': 'Letters only (a-z, A-Z)'},
                {'value': 'lowercase', 'label': 'Lowercase letters (a-z)'},
                {'value': 'uppercase', 'label': 'Uppercase letters (A-Z)'},
                {'value': 'numbers', 'label': 'Numbers only (0-9)'},
                {'value': 'hex', 'label': 'Hexadecimal (0-9, a-f)'},
                {'value': 'uuid', 'label': 'UUID v4'}
            ],
            'default': 'alphanumeric',
            'required': False
        }
    },
    output_schema={
        'status': {'type': 'string'},
        'value': {'type': 'string', 'description': 'Random string'}
    },
    examples=[
        {
            'name': 'Random alphanumeric',
            'params': {
                'length': 16,
                'charset': 'alphanumeric'
            }
        },
        {
            'name': 'Generate UUID',
            'params': {
                'charset': 'uuid'
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class RandomStringModule(BaseModule):
    """Generate random string"""

    module_name = "Random String"
    module_description = "Generate random string or UUID"

    def validate_params(self):
        self.length = self.params.get('length', 16)
        self.charset = self.params.get('charset', 'alphanumeric')

    async def execute(self) -> Any:
        if self.charset == 'uuid':
            value = str(uuid.uuid4())
        else:
            # Define character sets
            charsets = {
                'alphanumeric': string.ascii_letters + string.digits,
                'letters': string.ascii_letters,
                'lowercase': string.ascii_lowercase,
                'uppercase': string.ascii_uppercase,
                'numbers': string.digits,
                'hex': string.hexdigits.lower()
            }

            chars = charsets.get(self.charset, charsets['alphanumeric'])
            value = ''.join(random.choice(chars) for _ in range(self.length))

        return {
            'status': 'success',
            'value': value
        }


@register_module(
    module_id='utility.datetime.now',
    version='1.0.0',
    category='utility',
    tags=['utility', 'datetime', 'time', 'date', 'timestamp'],
    label='Current Date/Time',
    label_key='modules.utility.datetime.now.label',
    description='Get current date and time',
    description_key='modules.utility.datetime.now.description',
    icon='Calendar',
    color='#3B82F6',
    params_schema={
        'format': {
            'type': 'select',
            'label': 'Format',
            'label_key': 'modules.utility.datetime.now.params.format.label',
            'description': 'Output format',
            'description_key': 'modules.utility.datetime.now.params.format.description',
            'options': [
                {'value': 'iso', 'label': 'ISO 8601 (2024-01-15T10:30:00)'},
                {'value': 'unix', 'label': 'Unix timestamp (seconds)'},
                {'value': 'unix_ms', 'label': 'Unix timestamp (milliseconds)'},
                {'value': 'date', 'label': 'Date only (2024-01-15)'},
                {'value': 'time', 'label': 'Time only (10:30:00)'},
                {'value': 'custom', 'label': 'Custom format'}
            ],
            'default': 'iso',
            'required': False
        },
        'custom_format': {
            'type': 'string',
            'label': 'Custom Format',
            'label_key': 'modules.utility.datetime.now.params.custom_format.label',
            'description': 'Python strftime format (if format=custom)',
            'description_key': 'modules.utility.datetime.now.params.custom_format.description',
            'placeholder': '%Y-%m-%d %H:%M:%S',
            'required': False
        },
        'timezone': {
            'type': 'string',
            'label': 'Timezone',
            'label_key': 'modules.utility.datetime.now.params.timezone.label',
            'description': 'Timezone (default: UTC)',
            'description_key': 'modules.utility.datetime.now.params.timezone.description',
            'placeholder': 'UTC',
            'default': 'UTC',
            'required': False
        }
    },
    output_schema={
        'status': {'type': 'string'},
        'datetime': {'type': 'string', 'description': 'Formatted date/time'},
        'timestamp': {'type': 'number', 'description': 'Unix timestamp'},
        'iso': {'type': 'string', 'description': 'ISO format'}
    },
    examples=[
        {
            'name': 'Get current ISO datetime',
            'params': {
                'format': 'iso'
            }
        },
        {
            'name': 'Get Unix timestamp',
            'params': {
                'format': 'unix'
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class DateTimeNowModule(BaseModule):
    """Get current date/time"""

    module_name = "Current Date/Time"
    module_description = "Get current date and time in various formats"

    def validate_params(self):
        self.format = self.params.get('format', 'iso')
        self.custom_format = self.params.get('custom_format', '%Y-%m-%d %H:%M:%S')
        self.timezone = self.params.get('timezone', 'UTC')

    async def execute(self) -> Any:
        now = datetime.utcnow()  # Always use UTC for consistency

        # Format output
        if self.format == 'iso':
            formatted = now.isoformat()
        elif self.format == 'unix':
            formatted = int(now.timestamp())
        elif self.format == 'unix_ms':
            formatted = int(now.timestamp() * 1000)
        elif self.format == 'date':
            formatted = now.strftime('%Y-%m-%d')
        elif self.format == 'time':
            formatted = now.strftime('%H:%M:%S')
        elif self.format == 'custom':
            formatted = now.strftime(self.custom_format)
        else:
            formatted = now.isoformat()

        return {
            'status': 'success',
            'datetime': formatted,
            'timestamp': int(now.timestamp()),
            'iso': now.isoformat()
        }


@register_module(
    module_id='utility.hash.md5',
    version='1.0.0',
    category='utility',
    tags=['utility', 'hash', 'md5', 'crypto', 'checksum'],
    label='MD5 Hash',
    label_key='modules.utility.hash.md5.label',
    description='Calculate MD5 hash of text',
    description_key='modules.utility.hash.md5.description',
    icon='Hash',
    color='#8B5CF6',
    params_schema={
        'text': {
            'type': 'text',
            'label': 'Text',
            'label_key': 'modules.utility.hash.md5.params.text.label',
            'description': 'Text to hash',
            'description_key': 'modules.utility.hash.md5.params.text.description',
            'placeholder': 'Hello World',
            'required': True
        },
        'encoding': {
            'type': 'string',
            'label': 'Encoding',
            'label_key': 'modules.utility.hash.md5.params.encoding.label',
            'description': 'Text encoding',
            'description_key': 'modules.utility.hash.md5.params.encoding.description',
            'default': 'utf-8',
            'required': False
        }
    },
    output_schema={
        'status': {'type': 'string'},
        'hash': {'type': 'string', 'description': 'MD5 hash (hexadecimal)'}
    },
    examples=[
        {
            'name': 'Hash text',
            'params': {
                'text': 'Hello World'
            },
            'expected_output': {
                'status': 'success',
                'hash': 'b10a8db164e0754105b7a99be72e3fe5'
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class HashMD5Module(BaseModule):
    """Calculate MD5 hash"""

    module_name = "MD5 Hash"
    module_description = "Calculate MD5 hash of text"

    def validate_params(self):
        if 'text' not in self.params:
            raise ValueError("Missing required parameter: text")

        self.text = self.params['text']
        self.encoding = self.params.get('encoding', 'utf-8')

    async def execute(self) -> Any:
        hash_obj = hashlib.md5(self.text.encode(self.encoding))
        hash_hex = hash_obj.hexdigest()

        return {
            'status': 'success',
            'hash': hash_hex
        }
