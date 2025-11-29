"""
File Operation Modules
Basic file system operations
"""

from typing import Any, Dict
from ...base import BaseModule
from ...registry import register_module
import os
import shutil


@register_module(
    module_id='file.read',
    version='1.0.0',
    category='atomic',
    subcategory='file',
    tags=['file', 'io', 'read', 'atomic'],
    label='Read File',
    label_key='modules.file.read.label',
    description='Read content from a file',
    description_key='modules.file.read.description',
    icon='FileText',
    color='#6B7280',

    # Connection types
    output_types=['text', 'binary'],
    can_connect_to=['data.*', 'string.*'],

    # Phase 2: Execution settings
    timeout=30,  # File reads can timeout on network filesystems
    retryable=True,  # Can retry failed reads
    max_retries=2,
    concurrent_safe=True,  # Reading different files is safe

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=True,  # Files may contain sensitive data
    required_permissions=['file.read'],

    params_schema={
        'path': {
            'type': 'string',
            'label': 'File Path',
            'label_key': 'modules.file.read.params.path.label',
            'description': 'Path to the file to read',
            'description_key': 'modules.file.read.params.path.description',
            'required': True,
            'placeholder': '/path/to/file.txt'
        },
        'encoding': {
            'type': 'string',
            'label': 'Encoding',
            'label_key': 'modules.file.read.params.encoding.label',
            'description': 'File encoding',
            'description_key': 'modules.file.read.params.encoding.description',
            'default': 'utf-8',
            'required': False
        }
    },
    output_schema={
        'content': {
            'type': 'string',
            'description': 'File content'
        },
        'size': {
            'type': 'number',
            'description': 'File size in bytes'
        }
    },
    examples=[
        {
            'title': 'Read text file',
            'title_key': 'modules.file.read.examples.text.title',
            'params': {
                'path': '/tmp/data.txt',
                'encoding': 'utf-8'
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
async def file_read(context):
    """Read file content"""
    params = context['params']
    path = params['path']
    encoding = params.get('encoding', 'utf-8')

    with open(path, 'r', encoding=encoding) as f:
        content = f.read()

    size = os.path.getsize(path)

    return {
        'content': content,
        'size': size
    }


@register_module(
    module_id='file.write',
    version='1.0.0',
    category='atomic',
    subcategory='file',
    tags=['file', 'io', 'write', 'atomic'],
    label='Write File',
    label_key='modules.file.write.label',
    description='Write content to a file',
    description_key='modules.file.write.description',
    icon='FileText',
    color='#6B7280',

    # Phase 2: Execution settings
    timeout=30,  # File writes can timeout on network filesystems
    retryable=False,  # Don't retry writes (could cause duplicates)
    concurrent_safe=False,  # Writing to same file is not thread-safe

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=True,  # File content may be sensitive
    required_permissions=['file.write'],

    params_schema={
        'path': {
            'type': 'string',
            'label': 'File Path',
            'label_key': 'modules.file.write.params.path.label',
            'description': 'Path to the file to write',
            'description_key': 'modules.file.write.params.path.description',
            'required': True,
            'placeholder': '/path/to/file.txt'
        },
        'content': {
            'type': 'string',
            'label': 'Content',
            'label_key': 'modules.file.write.params.content.label',
            'description': 'Content to write',
            'description_key': 'modules.file.write.params.content.description',
            'required': True,
            'multiline': True
        },
        'encoding': {
            'type': 'string',
            'label': 'Encoding',
            'label_key': 'modules.file.write.params.encoding.label',
            'description': 'File encoding',
            'description_key': 'modules.file.write.params.encoding.description',
            'default': 'utf-8',
            'required': False
        },
        'mode': {
            'type': 'string',
            'label': 'Write Mode',
            'label_key': 'modules.file.write.params.mode.label',
            'description': 'Write mode: overwrite or append',
            'description_key': 'modules.file.write.params.mode.description',
            'default': 'overwrite',
            'required': False,
            'options': [
                {'value': 'overwrite', 'label': 'Overwrite'},
                {'value': 'append', 'label': 'Append'}
            ]
        }
    },
    output_schema={
        'path': {
            'type': 'string',
            'description': 'File path'
        },
        'bytes_written': {
            'type': 'number',
            'description': 'Number of bytes written'
        }
    },
    examples=[
        {
            'title': 'Write text file',
            'title_key': 'modules.file.write.examples.text.title',
            'params': {
                'path': '/tmp/output.txt',
                'content': 'Hello World',
                'mode': 'overwrite'
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
async def file_write(context):
    """Write file content"""
    params = context['params']
    path = params['path']
    content = params['content']
    encoding = params.get('encoding', 'utf-8')
    mode = 'w' if params.get('mode', 'overwrite') == 'overwrite' else 'a'

    with open(path, mode, encoding=encoding) as f:
        bytes_written = f.write(content)

    return {
        'path': path,
        'bytes_written': len(content.encode(encoding))
    }


@register_module(
    module_id='file.exists',
    version='1.0.0',
    category='atomic',
    subcategory='file',
    tags=['file', 'io', 'check', 'atomic'],
    label='Check File Exists',
    label_key='modules.file.exists.label',
    description='Check if a file or directory exists',
    description_key='modules.file.exists.description',
    icon='FileSearch',
    color='#6B7280',

    # Phase 2: Execution settings
    # No timeout needed - file existence check is instant
    retryable=True,  # Can retry if filesystem temporarily unavailable
    max_retries=2,
    concurrent_safe=True,  # Stateless check operation

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=['file.read'],

    params_schema={
        'path': {
            'type': 'string',
            'label': 'Path',
            'label_key': 'modules.file.exists.params.path.label',
            'description': 'Path to check',
            'description_key': 'modules.file.exists.params.path.description',
            'required': True,
            'placeholder': '/path/to/file'
        }
    },
    output_schema={
        'exists': {
            'type': 'boolean',
            'description': 'Whether path exists'
        },
        'is_file': {
            'type': 'boolean',
            'description': 'Whether path is a file'
        },
        'is_directory': {
            'type': 'boolean',
            'description': 'Whether path is a directory'
        }
    },
    examples=[
        {
            'title': 'Check file exists',
            'title_key': 'modules.file.exists.examples.check.title',
            'params': {
                'path': '/tmp/data.txt'
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
async def file_exists(context):
    """Check if file exists"""
    params = context['params']
    path = params['path']

    exists = os.path.exists(path)
    is_file = os.path.isfile(path) if exists else False
    is_directory = os.path.isdir(path) if exists else False

    return {
        'exists': exists,
        'is_file': is_file,
        'is_directory': is_directory
    }
