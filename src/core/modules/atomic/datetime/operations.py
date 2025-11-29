"""
Datetime Operations Modules

Provides date and time manipulation capabilities.
"""
from typing import Any, Dict
from ...base import BaseModule
from ...registry import register_module
from datetime import datetime, timedelta
import time


@register_module(
    module_id='datetime.format',
    version='1.0.0',
    category='utility',
    subcategory='datetime',
    tags=['datetime', 'format', 'date', 'time'],
    label='Format DateTime',
    label_key='modules.datetime.format.label',
    description='Format datetime to string',
    description_key='modules.datetime.format.description',
    icon='Calendar',
    color='#8B5CF6',

    # Connection types
    input_types=['datetime', 'string'],
    output_types=['string', 'text'],

    # Phase 2: Execution settings
    timeout=None,
    retryable=False,
    concurrent_safe=True,

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=[],

    params_schema={
        'datetime': {
            'type': 'string',
            'label': 'DateTime',
            'label_key': 'modules.datetime.format.params.datetime.label',
            'description': 'DateTime to format (ISO format or "now")',
            'description_key': 'modules.datetime.format.params.datetime.description',
            'default': 'now',
            'required': False
        },
        'format': {
            'type': 'string',
            'label': 'Format',
            'label_key': 'modules.datetime.format.params.format.label',
            'description': 'strftime format string',
            'description_key': 'modules.datetime.format.params.format.description',
            'default': '%Y-%m-%d %H:%M:%S',
            'required': False
        }
    },
    output_schema={
        'result': {'type': 'string'},
        'timestamp': {'type': 'number'}
    },
    examples=[
        {
            'title': 'Format current time',
            'params': {
                'datetime': 'now',
                'format': '%Y-%m-%d %H:%M:%S'
            }
        },
        {
            'title': 'Custom date format',
            'params': {
                'datetime': '2024-01-15T10:30:00',
                'format': '%B %d, %Y'
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class DateTimeFormatModule(BaseModule):
    """DateTime Format Module"""

    def validate_params(self):
        self.datetime_str = self.params.get('datetime', 'now')
        self.format = self.params.get('format', '%Y-%m-%d %H:%M:%S')

    async def execute(self) -> Any:
        # Parse datetime
        if self.datetime_str == 'now':
            dt = datetime.now()
        else:
            # Try parsing ISO format
            try:
                dt = datetime.fromisoformat(self.datetime_str.replace('Z', '+00:00'))
            except:
                raise ValueError(f"Invalid datetime format: {self.datetime_str}")

        # Format datetime
        result = dt.strftime(self.format)
        timestamp = dt.timestamp()

        return {
            "result": result,
            "timestamp": timestamp
        }


@register_module(
    module_id='datetime.parse',
    version='1.0.0',
    category='utility',
    subcategory='datetime',
    tags=['datetime', 'parse', 'date', 'time'],
    label='Parse DateTime',
    label_key='modules.datetime.parse.label',
    description='Parse string to datetime',
    description_key='modules.datetime.parse.description',
    icon='Calendar',
    color='#8B5CF6',

    # Connection types
    input_types=['string', 'text'],
    output_types=['datetime', 'json'],

    # Phase 2: Execution settings
    timeout=None,
    retryable=False,
    concurrent_safe=True,

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=[],

    params_schema={
        'datetime_string': {
            'type': 'string',
            'label': 'DateTime String',
            'label_key': 'modules.datetime.parse.params.datetime_string.label',
            'description': 'DateTime string to parse',
            'description_key': 'modules.datetime.parse.params.datetime_string.description',
            'required': True
        },
        'format': {
            'type': 'string',
            'label': 'Format',
            'label_key': 'modules.datetime.parse.params.format.label',
            'description': 'strptime format string (leave empty for ISO)',
            'description_key': 'modules.datetime.parse.params.format.description',
            'required': False
        }
    },
    output_schema={
        'result': {'type': 'string'},
        'timestamp': {'type': 'number'},
        'year': {'type': 'number'},
        'month': {'type': 'number'},
        'day': {'type': 'number'},
        'hour': {'type': 'number'},
        'minute': {'type': 'number'},
        'second': {'type': 'number'}
    },
    examples=[
        {
            'title': 'Parse ISO format',
            'params': {
                'datetime_string': '2024-01-15T10:30:00'
            }
        },
        {
            'title': 'Parse custom format',
            'params': {
                'datetime_string': 'January 15, 2024',
                'format': '%B %d, %Y'
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class DateTimeParseModule(BaseModule):
    """DateTime Parse Module"""

    def validate_params(self):
        self.datetime_string = self.params.get('datetime_string')
        self.format = self.params.get('format')

        if not self.datetime_string:
            raise ValueError("datetime_string is required")

    async def execute(self) -> Any:
        # Parse datetime
        if self.format:
            dt = datetime.strptime(self.datetime_string, self.format)
        else:
            # Try ISO format
            try:
                dt = datetime.fromisoformat(self.datetime_string.replace('Z', '+00:00'))
            except:
                raise ValueError(f"Invalid datetime format: {self.datetime_string}")

        return {
            "result": dt.isoformat(),
            "timestamp": dt.timestamp(),
            "year": dt.year,
            "month": dt.month,
            "day": dt.day,
            "hour": dt.hour,
            "minute": dt.minute,
            "second": dt.second
        }


@register_module(
    module_id='datetime.add',
    version='1.0.0',
    category='utility',
    subcategory='datetime',
    tags=['datetime', 'add', 'date', 'time'],
    label='Add Time',
    label_key='modules.datetime.add.label',
    description='Add time to datetime',
    description_key='modules.datetime.add.description',
    icon='Plus',
    color='#8B5CF6',

    # Connection types
    input_types=['datetime', 'string'],
    output_types=['datetime', 'string'],

    # Phase 2: Execution settings
    timeout=None,
    retryable=False,
    concurrent_safe=True,

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=[],

    params_schema={
        'datetime': {
            'type': 'string',
            'label': 'DateTime',
            'label_key': 'modules.datetime.add.params.datetime.label',
            'description': 'DateTime to modify (ISO format or "now")',
            'description_key': 'modules.datetime.add.params.datetime.description',
            'default': 'now',
            'required': False
        },
        'days': {
            'type': 'number',
            'label': 'Days',
            'label_key': 'modules.datetime.add.params.days.label',
            'description': 'Days to add',
            'description_key': 'modules.datetime.add.params.days.description',
            'default': 0,
            'required': False
        },
        'hours': {
            'type': 'number',
            'label': 'Hours',
            'label_key': 'modules.datetime.add.params.hours.label',
            'description': 'Hours to add',
            'description_key': 'modules.datetime.add.params.hours.description',
            'default': 0,
            'required': False
        },
        'minutes': {
            'type': 'number',
            'label': 'Minutes',
            'label_key': 'modules.datetime.add.params.minutes.label',
            'description': 'Minutes to add',
            'description_key': 'modules.datetime.add.params.minutes.description',
            'default': 0,
            'required': False
        },
        'seconds': {
            'type': 'number',
            'label': 'Seconds',
            'label_key': 'modules.datetime.add.params.seconds.label',
            'description': 'Seconds to add',
            'description_key': 'modules.datetime.add.params.seconds.description',
            'default': 0,
            'required': False
        }
    },
    output_schema={
        'result': {'type': 'string'},
        'timestamp': {'type': 'number'}
    },
    examples=[
        {
            'title': 'Add 7 days',
            'params': {
                'datetime': 'now',
                'days': 7
            }
        },
        {
            'title': 'Add 2 hours 30 minutes',
            'params': {
                'datetime': '2024-01-15T10:00:00',
                'hours': 2,
                'minutes': 30
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class DateTimeAddModule(BaseModule):
    """DateTime Add Module"""

    def validate_params(self):
        self.datetime_str = self.params.get('datetime', 'now')
        self.days = self.params.get('days', 0)
        self.hours = self.params.get('hours', 0)
        self.minutes = self.params.get('minutes', 0)
        self.seconds = self.params.get('seconds', 0)

    async def execute(self) -> Any:
        # Parse datetime
        if self.datetime_str == 'now':
            dt = datetime.now()
        else:
            try:
                dt = datetime.fromisoformat(self.datetime_str.replace('Z', '+00:00'))
            except:
                raise ValueError(f"Invalid datetime format: {self.datetime_str}")

        # Add time
        delta = timedelta(
            days=self.days,
            hours=self.hours,
            minutes=self.minutes,
            seconds=self.seconds
        )
        result_dt = dt + delta

        return {
            "result": result_dt.isoformat(),
            "timestamp": result_dt.timestamp()
        }


@register_module(
    module_id='datetime.subtract',
    version='1.0.0',
    category='utility',
    subcategory='datetime',
    tags=['datetime', 'subtract', 'date', 'time'],
    label='Subtract Time',
    label_key='modules.datetime.subtract.label',
    description='Subtract time from datetime',
    description_key='modules.datetime.subtract.description',
    icon='Minus',
    color='#8B5CF6',

    # Connection types
    input_types=['datetime', 'string'],
    output_types=['datetime', 'string'],

    # Phase 2: Execution settings
    timeout=None,
    retryable=False,
    concurrent_safe=True,

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=[],

    params_schema={
        'datetime': {
            'type': 'string',
            'label': 'DateTime',
            'label_key': 'modules.datetime.subtract.params.datetime.label',
            'description': 'DateTime to modify (ISO format or "now")',
            'description_key': 'modules.datetime.subtract.params.datetime.description',
            'default': 'now',
            'required': False
        },
        'days': {
            'type': 'number',
            'label': 'Days',
            'label_key': 'modules.datetime.subtract.params.days.label',
            'description': 'Days to subtract',
            'description_key': 'modules.datetime.subtract.params.days.description',
            'default': 0,
            'required': False
        },
        'hours': {
            'type': 'number',
            'label': 'Hours',
            'label_key': 'modules.datetime.subtract.params.hours.label',
            'description': 'Hours to subtract',
            'description_key': 'modules.datetime.subtract.params.hours.description',
            'default': 0,
            'required': False
        },
        'minutes': {
            'type': 'number',
            'label': 'Minutes',
            'label_key': 'modules.datetime.subtract.params.minutes.label',
            'description': 'Minutes to subtract',
            'description_key': 'modules.datetime.subtract.params.minutes.description',
            'default': 0,
            'required': False
        },
        'seconds': {
            'type': 'number',
            'label': 'Seconds',
            'label_key': 'modules.datetime.subtract.params.seconds.label',
            'description': 'Seconds to subtract',
            'description_key': 'modules.datetime.subtract.params.seconds.description',
            'default': 0,
            'required': False
        }
    },
    output_schema={
        'result': {'type': 'string'},
        'timestamp': {'type': 'number'}
    },
    examples=[
        {
            'title': 'Subtract 7 days',
            'params': {
                'datetime': 'now',
                'days': 7
            }
        },
        {
            'title': 'Subtract 1 hour',
            'params': {
                'datetime': '2024-01-15T10:00:00',
                'hours': 1
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class DateTimeSubtractModule(BaseModule):
    """DateTime Subtract Module"""

    def validate_params(self):
        self.datetime_str = self.params.get('datetime', 'now')
        self.days = self.params.get('days', 0)
        self.hours = self.params.get('hours', 0)
        self.minutes = self.params.get('minutes', 0)
        self.seconds = self.params.get('seconds', 0)

    async def execute(self) -> Any:
        # Parse datetime
        if self.datetime_str == 'now':
            dt = datetime.now()
        else:
            try:
                dt = datetime.fromisoformat(self.datetime_str.replace('Z', '+00:00'))
            except:
                raise ValueError(f"Invalid datetime format: {self.datetime_str}")

        # Subtract time
        delta = timedelta(
            days=self.days,
            hours=self.hours,
            minutes=self.minutes,
            seconds=self.seconds
        )
        result_dt = dt - delta

        return {
            "result": result_dt.isoformat(),
            "timestamp": result_dt.timestamp()
        }
