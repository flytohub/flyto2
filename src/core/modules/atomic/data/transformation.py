"""
Data Processing Modules
Handle CSV, JSON, text processing, data transformation, etc.
"""
from typing import Any, Dict
from ...base import BaseModule
from ...registry import register_module
import json
import csv
import io
import os


@register_module(
    module_id='data.csv.read',
    version='1.0.0',
    category='data',
    tags=['data', 'csv', 'file', 'read', 'parser'],
    label='Read CSV File',
    label_key='modules.data.csv.read.label',
    description='Read and parse CSV file into array of objects',
    description_key='modules.data.csv.read.description',
    icon='FileText',
    color='#10B981',

    # Connection types
    input_types=['text', 'file_path'],
    output_types=['array', 'object'],
    can_connect_to=['data.*', 'file.*'],

    # Phase 2: Execution settings
    timeout=30,  # File reads can timeout on network filesystems
    retryable=True,  # Can retry failed reads
    max_retries=2,
    concurrent_safe=True,  # Reading different files is safe

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=True,  # CSV files may contain sensitive data
    required_permissions=['file.read'],

    params_schema={
        'file_path': {
            'type': 'string',
            'label': 'File Path',
            'label_key': 'modules.data.csv.read.params.file_path.label',
            'description': 'Path to CSV file',
            'description_key': 'modules.data.csv.read.params.file_path.description',
            'placeholder': '/path/to/data.csv',
            'required': True
        },
        'delimiter': {
            'type': 'string',
            'label': 'Delimiter',
            'label_key': 'modules.data.csv.read.params.delimiter.label',
            'description': 'CSV delimiter character',
            'description_key': 'modules.data.csv.read.params.delimiter.description',
            'default': ',',
            'placeholder': ',',
            'required': False
        },
        'encoding': {
            'type': 'string',
            'label': 'Encoding',
            'label_key': 'modules.data.csv.read.params.encoding.label',
            'description': 'File encoding',
            'description_key': 'modules.data.csv.read.params.encoding.description',
            'default': 'utf-8',
            'placeholder': 'utf-8',
            'required': False
        },
        'skip_header': {
            'type': 'boolean',
            'label': 'Skip Header',
            'label_key': 'modules.data.csv.read.params.skip_header.label',
            'description': 'Skip first row (header)',
            'description_key': 'modules.data.csv.read.params.skip_header.description',
            'default': False,
            'required': False
        }
    },
    output_schema={
        'status': {'type': 'string', 'description': 'Operation status'},
        'data': {'type': 'array', 'description': 'Array of row objects'},
        'rows': {'type': 'number', 'description': 'Number of rows'},
        'columns': {'type': 'array', 'description': 'Column names'}
    },
    examples=[
        {
            'name': 'Read CSV file',
            'params': {
                'file_path': 'data/users.csv',
                'delimiter': ',',
                'encoding': 'utf-8'
            },
            'expected_output': {
                'status': 'success',
                'data': [
                    {'name': 'John', 'age': '30', 'city': 'NYC'},
                    {'name': 'Jane', 'age': '25', 'city': 'LA'}
                ],
                'rows': 2
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class CSVReadModule(BaseModule):
    """Read CSV file and parse into array"""

    module_name = "Read CSV File"
    module_description = "Read and parse CSV file into array of objects"

    def validate_params(self):
        if 'file_path' not in self.params or not self.params['file_path']:
            raise ValueError("Missing required parameter: file_path")

        self.file_path = self.params['file_path']
        self.delimiter = self.params.get('delimiter', ',')
        self.encoding = self.params.get('encoding', 'utf-8')
        self.skip_header = self.params.get('skip_header', False)

    async def execute(self) -> Any:
        try:
            if not os.path.exists(self.file_path):
                return {
                    'status': 'error',
                    'message': f'File not found: {self.file_path}'
                }

            with open(self.file_path, 'r', encoding=self.encoding) as csvfile:
                reader = csv.DictReader(csvfile, delimiter=self.delimiter)

                if self.skip_header:
                    next(reader, None)  # Skip header row

                data = list(reader)
                columns = reader.fieldnames or []

                return {
                    'status': 'success',
                    'data': data,
                    'rows': len(data),
                    'columns': columns
                }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to read CSV: {str(e)}'
            }


@register_module(
    module_id='data.csv.write',
    version='1.0.0',
    category='data',
    tags=['data', 'csv', 'file', 'write', 'export'],
    label='Write CSV File',
    label_key='modules.data.csv.write.label',
    description='Write array of objects to CSV file',
    description_key='modules.data.csv.write.description',
    icon='Save',
    color='#10B981',

    # Phase 2: Execution settings
    timeout=30,  # File writes can timeout on network filesystems
    retryable=False,  # Don't retry writes (could cause duplicates)
    concurrent_safe=False,  # Writing to same file is not thread-safe

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=True,  # CSV data may be sensitive
    required_permissions=['file.write'],

    params_schema={
        'file_path': {
            'type': 'string',
            'label': 'File Path',
            'label_key': 'modules.data.csv.write.params.file_path.label',
            'description': 'Output CSV file path',
            'description_key': 'modules.data.csv.write.params.file_path.description',
            'placeholder': '/path/to/output.csv',
            'required': True
        },
        'data': {
            'type': 'array',
            'label': 'Data',
            'label_key': 'modules.data.csv.write.params.data.label',
            'description': 'Array of objects to write',
            'description_key': 'modules.data.csv.write.params.data.description',
            'required': True
        },
        'delimiter': {
            'type': 'string',
            'label': 'Delimiter',
            'label_key': 'modules.data.csv.write.params.delimiter.label',
            'description': 'CSV delimiter character',
            'description_key': 'modules.data.csv.write.params.delimiter.description',
            'default': ',',
            'required': False
        },
        'encoding': {
            'type': 'string',
            'label': 'Encoding',
            'label_key': 'modules.data.csv.write.params.encoding.label',
            'description': 'File encoding',
            'description_key': 'modules.data.csv.write.params.encoding.description',
            'default': 'utf-8',
            'required': False
        }
    },
    output_schema={
        'status': {'type': 'string'},
        'file_path': {'type': 'string'},
        'rows_written': {'type': 'number'}
    },
    examples=[
        {
            'name': 'Write CSV file',
            'params': {
                'file_path': 'output/results.csv',
                'data': [
                    {'name': 'John', 'score': 95},
                    {'name': 'Jane', 'score': 87}
                ]
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class CSVWriteModule(BaseModule):
    """Write array to CSV file"""

    module_name = "Write CSV File"
    module_description = "Write array of objects to CSV file"

    def validate_params(self):
        if 'file_path' not in self.params or not self.params['file_path']:
            raise ValueError("Missing required parameter: file_path")
        if 'data' not in self.params or not isinstance(self.params['data'], list):
            raise ValueError("Missing or invalid parameter: data (must be array)")

        self.file_path = self.params['file_path']
        self.data = self.params['data']
        self.delimiter = self.params.get('delimiter', ',')
        self.encoding = self.params.get('encoding', 'utf-8')

    async def execute(self) -> Any:
        try:
            if not self.data:
                return {
                    'status': 'error',
                    'message': 'Cannot write empty data array'
                }

            # Create directory if not exists
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

            # Get column names from first object
            fieldnames = list(self.data[0].keys())

            with open(self.file_path, 'w', encoding=self.encoding, newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=self.delimiter)
                writer.writeheader()
                writer.writerows(self.data)

            return {
                'status': 'success',
                'file_path': self.file_path,
                'rows_written': len(self.data)
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to write CSV: {str(e)}'
            }


@register_module(
    module_id='data.json.parse',
    version='1.0.0',
    category='data',
    tags=['data', 'json', 'parse', 'transform'],
    label='Parse JSON',
    label_key='modules.data.json.parse.label',
    description='Parse JSON string into object',
    description_key='modules.data.json.parse.description',
    icon='Code',
    color='#F59E0B',

    # Phase 2: Execution settings
    # No timeout - JSON parsing is instant
    retryable=False,  # Parse errors won't fix themselves
    concurrent_safe=True,  # Stateless operation

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=[],

    params_schema={
        'json_string': {
            'type': 'text',
            'label': 'JSON String',
            'label_key': 'modules.data.json.parse.params.json_string.label',
            'description': 'JSON string to parse',
            'description_key': 'modules.data.json.parse.params.json_string.description',
            'placeholder': '{"name": "John", "age": 30}',
            'required': True
        }
    },
    output_schema={
        'status': {'type': 'string'},
        'data': {'type': 'object', 'description': 'Parsed object'}
    },
    examples=[
        {
            'name': 'Parse JSON string',
            'params': {
                'json_string': '{"name": "John", "age": 30}'
            },
            'expected_output': {
                'status': 'success',
                'data': {'name': 'John', 'age': 30}
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class JSONParseModule(BaseModule):
    """Parse JSON string"""

    module_name = "Parse JSON"
    module_description = "Parse JSON string into object"

    def validate_params(self):
        if 'json_string' not in self.params:
            raise ValueError("Missing required parameter: json_string")
        self.json_string = self.params['json_string']

    async def execute(self) -> Any:
        try:
            data = json.loads(self.json_string)
            return {
                'status': 'success',
                'data': data
            }
        except json.JSONDecodeError as e:
            return {
                'status': 'error',
                'message': f'Invalid JSON: {str(e)}'
            }


@register_module(
    module_id='data.json.stringify',
    version='1.0.0',
    category='data',
    tags=['data', 'json', 'stringify', 'serialize'],
    label='JSON Stringify',
    label_key='modules.data.json.stringify.label',
    description='Convert object to JSON string',
    description_key='modules.data.json.stringify.description',
    icon='FileCode',
    color='#F59E0B',

    # Phase 2: Execution settings
    # No timeout - JSON stringify is instant
    retryable=False,  # Serialization errors won't fix themselves
    concurrent_safe=True,  # Stateless operation

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=[],

    params_schema={
        'data': {
            'type': 'object',
            'label': 'Data',
            'label_key': 'modules.data.json.stringify.params.data.label',
            'description': 'Object to stringify',
            'description_key': 'modules.data.json.stringify.params.data.description',
            'required': True
        },
        'pretty': {
            'type': 'boolean',
            'label': 'Pretty Print',
            'label_key': 'modules.data.json.stringify.params.pretty.label',
            'description': 'Format with indentation',
            'description_key': 'modules.data.json.stringify.params.pretty.description',
            'default': False,
            'required': False
        },
        'indent': {
            'type': 'number',
            'label': 'Indent Size',
            'label_key': 'modules.data.json.stringify.params.indent.label',
            'description': 'Indentation spaces (if pretty=true)',
            'description_key': 'modules.data.json.stringify.params.indent.description',
            'default': 2,
            'min': 1,
            'max': 8,
            'required': False
        }
    },
    output_schema={
        'status': {'type': 'string'},
        'json': {'type': 'string', 'description': 'JSON string'}
    },
    examples=[
        {
            'name': 'Stringify object',
            'params': {
                'data': {'name': 'John', 'age': 30},
                'pretty': True
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class JSONStringifyModule(BaseModule):
    """Convert object to JSON string"""

    module_name = "JSON Stringify"
    module_description = "Convert object to JSON string"

    def validate_params(self):
        if 'data' not in self.params:
            raise ValueError("Missing required parameter: data")

        self.data = self.params['data']
        self.pretty = self.params.get('pretty', False)
        self.indent = self.params.get('indent', 2)

    async def execute(self) -> Any:
        try:
            if self.pretty:
                json_str = json.dumps(self.data, indent=self.indent, ensure_ascii=False)
            else:
                json_str = json.dumps(self.data, ensure_ascii=False)

            return {
                'status': 'success',
                'json': json_str
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to stringify: {str(e)}'
            }


@register_module(
    module_id='data.text.template',
    version='1.0.0',
    category='data',
    tags=['data', 'text', 'template', 'string', 'format'],
    label='Text Template',
    label_key='modules.data.text.template.label',
    description='Fill text template with variables',
    description_key='modules.data.text.template.description',
    icon='FileText',
    color='#8B5CF6',

    # Phase 2: Execution settings
    # No timeout - template filling is instant
    retryable=False,  # Template errors won't fix themselves
    concurrent_safe=True,  # Stateless operation

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=[],

    params_schema={
        'template': {
            'type': 'text',
            'label': 'Template',
            'label_key': 'modules.data.text.template.params.template.label',
            'description': 'Text template with {variable} placeholders',
            'description_key': 'modules.data.text.template.params.template.description',
            'placeholder': 'Hello {name}, you have {count} messages.',
            'required': True
        },
        'variables': {
            'type': 'object',
            'label': 'Variables',
            'label_key': 'modules.data.text.template.params.variables.label',
            'description': 'Object with variable values',
            'description_key': 'modules.data.text.template.params.variables.description',
            'placeholder': {'name': 'John', 'count': 5},
            'required': True
        }
    },
    output_schema={
        'status': {'type': 'string'},
        'result': {'type': 'string', 'description': 'Filled template'}
    },
    examples=[
        {
            'name': 'Fill template',
            'params': {
                'template': 'Hello {name}, you scored {score} points!',
                'variables': {'name': 'Alice', 'score': 95}
            },
            'expected_output': {
                'status': 'success',
                'result': 'Hello Alice, you scored 95 points!'
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class TextTemplateModule(BaseModule):
    """Fill text template with variables"""

    module_name = "Text Template"
    module_description = "Replace {placeholders} in template with variable values"

    def validate_params(self):
        if 'template' not in self.params or not self.params['template']:
            raise ValueError("Missing required parameter: template")
        if 'variables' not in self.params or not isinstance(self.params['variables'], dict):
            raise ValueError("Missing or invalid parameter: variables (must be object)")

        self.template = self.params['template']
        self.variables = self.params['variables']

    async def execute(self) -> Any:
        try:
            result = self.template.format(**self.variables)
            return {
                'status': 'success',
                'result': result
            }
        except KeyError as e:
            return {
                'status': 'error',
                'message': f'Missing variable in template: {str(e)}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Template error: {str(e)}'
            }
