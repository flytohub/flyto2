"""
Advanced File Operations Modules

Provides extended file manipulation capabilities.
"""
import os
import shutil
from typing import Any, Dict
from ...base import BaseModule
from ...registry import register_module


@register_module(
    module_id='file.delete',
    version='1.0.0',
    category='file',
    subcategory='operations',
    tags=['file', 'delete', 'remove'],
    label='Delete File',
    label_key='modules.file.delete.label',
    description='Delete a file from the filesystem',
    description_key='modules.file.delete.description',
    icon='Trash2',
    color='#EF4444',

    # Connection types
    input_types=['file_path', 'text'],
    output_types=['boolean'],

    # Phase 2: Execution settings
    timeout=5,
    retryable=False,  # Don't retry deletes
    concurrent_safe=False,  # File operations not thread-safe

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=['file.delete'],

    params_schema={
        'file_path': {
            'type': 'string',
            'label': 'File Path',
            'label_key': 'modules.file.delete.params.file_path.label',
            'description': 'Path to the file to delete',
            'description_key': 'modules.file.delete.params.file_path.description',
            'required': True
        },
        'ignore_missing': {
            'type': 'boolean',
            'label': 'Ignore Missing',
            'label_key': 'modules.file.delete.params.ignore_missing.label',
            'description': 'Do not raise error if file does not exist',
            'description_key': 'modules.file.delete.params.ignore_missing.description',
            'default': False,
            'required': False
        }
    },
    output_schema={
        'deleted': {'type': 'boolean'},
        'file_path': {'type': 'string'}
    },
    examples=[
        {
            'title': 'Delete temporary file',
            'params': {
                'file_path': '/tmp/temp.txt',
                'ignore_missing': True
            }
        },
        {
            'title': 'Delete log file',
            'params': {
                'file_path': 'logs/app.log'
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class FileDeleteModule(BaseModule):
    """Delete File Module"""

    def validate_params(self):
        self.file_path = self.params.get('file_path')
        self.ignore_missing = self.params.get('ignore_missing', False)

        if not self.file_path:
            raise ValueError("file_path is required")

    async def execute(self) -> Any:
        try:
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
                return {
                    "deleted": True,
                    "file_path": self.file_path
                }
            elif self.ignore_missing:
                return {
                    "deleted": False,
                    "file_path": self.file_path
                }
            else:
                raise FileNotFoundError(f"File not found: {self.file_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to delete file: {str(e)}")


@register_module(
    module_id='file.move',
    version='1.0.0',
    category='file',
    subcategory='operations',
    tags=['file', 'move', 'rename'],
    label='Move File',
    label_key='modules.file.move.label',
    description='Move or rename a file',
    description_key='modules.file.move.description',
    icon='Move',
    color='#8B5CF6',

    # Connection types
    input_types=['file_path', 'text'],
    output_types=['file_path', 'text'],

    # Phase 2: Execution settings
    timeout=10,
    retryable=False,
    concurrent_safe=False,

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=['file.read', 'file.write'],

    params_schema={
        'source': {
            'type': 'string',
            'label': 'Source Path',
            'label_key': 'modules.file.move.params.source.label',
            'description': 'Path to the source file',
            'description_key': 'modules.file.move.params.source.description',
            'required': True
        },
        'destination': {
            'type': 'string',
            'label': 'Destination Path',
            'label_key': 'modules.file.move.params.destination.label',
            'description': 'Path to the destination',
            'description_key': 'modules.file.move.params.destination.description',
            'required': True
        }
    },
    output_schema={
        'moved': {'type': 'boolean'},
        'source': {'type': 'string'},
        'destination': {'type': 'string'}
    },
    examples=[
        {
            'title': 'Move file to archive',
            'params': {
                'source': 'data/input.csv',
                'destination': 'archive/input_2024.csv'
            }
        },
        {
            'title': 'Rename file',
            'params': {
                'source': 'report.txt',
                'destination': 'report_final.txt'
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class FileMoveModule(BaseModule):
    """Move File Module"""

    def validate_params(self):
        self.source = self.params.get('source')
        self.destination = self.params.get('destination')

        if not self.source or not self.destination:
            raise ValueError("source and destination are required")

    async def execute(self) -> Any:
        try:
            if not os.path.exists(self.source):
                raise FileNotFoundError(f"Source file not found: {self.source}")

            # Create destination directory if needed
            dest_dir = os.path.dirname(self.destination)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)

            shutil.move(self.source, self.destination)

            return {
                "moved": True,
                "source": self.source,
                "destination": self.destination
            }
        except Exception as e:
            raise RuntimeError(f"Failed to move file: {str(e)}")


@register_module(
    module_id='file.copy',
    version='1.0.0',
    category='file',
    subcategory='operations',
    tags=['file', 'copy', 'duplicate'],
    label='Copy File',
    label_key='modules.file.copy.label',
    description='Copy a file to another location',
    description_key='modules.file.copy.description',
    icon='Copy',
    color='#10B981',

    # Connection types
    input_types=['file_path', 'text'],
    output_types=['file_path', 'text'],

    # Phase 2: Execution settings
    timeout=30,  # Large files may take time
    retryable=True,
    max_retries=2,
    concurrent_safe=False,

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=['file.read', 'file.write'],

    params_schema={
        'source': {
            'type': 'string',
            'label': 'Source Path',
            'label_key': 'modules.file.copy.params.source.label',
            'description': 'Path to the source file',
            'description_key': 'modules.file.copy.params.source.description',
            'required': True
        },
        'destination': {
            'type': 'string',
            'label': 'Destination Path',
            'label_key': 'modules.file.copy.params.destination.label',
            'description': 'Path to copy the file to',
            'description_key': 'modules.file.copy.params.destination.description',
            'required': True
        },
        'overwrite': {
            'type': 'boolean',
            'label': 'Overwrite',
            'label_key': 'modules.file.copy.params.overwrite.label',
            'description': 'Overwrite destination if it exists',
            'description_key': 'modules.file.copy.params.overwrite.description',
            'default': False,
            'required': False
        }
    },
    output_schema={
        'copied': {'type': 'boolean'},
        'source': {'type': 'string'},
        'destination': {'type': 'string'},
        'size': {'type': 'number'}
    },
    examples=[
        {
            'title': 'Backup file',
            'params': {
                'source': 'data/important.csv',
                'destination': 'backup/important.csv',
                'overwrite': True
            }
        },
        {
            'title': 'Duplicate configuration',
            'params': {
                'source': 'config.yaml',
                'destination': 'config.backup.yaml'
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class FileCopyModule(BaseModule):
    """Copy File Module"""

    def validate_params(self):
        self.source = self.params.get('source')
        self.destination = self.params.get('destination')
        self.overwrite = self.params.get('overwrite', False)

        if not self.source or not self.destination:
            raise ValueError("source and destination are required")

    async def execute(self) -> Any:
        try:
            if not os.path.exists(self.source):
                raise FileNotFoundError(f"Source file not found: {self.source}")

            if os.path.exists(self.destination) and not self.overwrite:
                raise FileExistsError(f"Destination already exists: {self.destination}")

            # Create destination directory if needed
            dest_dir = os.path.dirname(self.destination)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)

            shutil.copy2(self.source, self.destination)
            file_size = os.path.getsize(self.destination)

            return {
                "copied": True,
                "source": self.source,
                "destination": self.destination,
                "size": file_size
            }
        except Exception as e:
            raise RuntimeError(f"Failed to copy file: {str(e)}")
