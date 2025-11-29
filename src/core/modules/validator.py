"""
Module Metadata Validator

Enforces strict standards for @register_module to ensure:
- Consistent naming conventions
- UI compatibility
- Professional quality
- Predictable behavior
"""

import re
from typing import Dict, List, Any, Optional
import json


class ValidationError(Exception):
    """Module validation failed"""
    pass


class ModuleValidator:
    """Validates module metadata against specification"""

    # Allowed categories (from MODULE_SPECIFICATION.md)
    ALLOWED_CATEGORIES = {
        # Atomic modules
        'browser', 'data', 'utility', 'file', 'string', 'array', 'math',
        # Third-party integrations
        'ai', 'notification', 'database', 'cloud', 'productivity', 'api', 'developer',
        # Legacy/special
        'element', 'flow',  # Existing modules
        # Future
        'workflow',
    }

    # Standard input/output types
    STANDARD_TYPES = {
        # Data types
        'text', 'json', 'html', 'xml', 'csv', 'binary',
        # Resource types
        'url', 'file_path', 'image', 'screenshot',
        # Browser types
        'browser_instance', 'page_instance', 'element',
        # API types
        'api_response', 'webhook',
        # Special
        'any',
    }

    # Valid Lucide icon names (subset - add more as needed)
    VALID_ICONS = {
        'Braces', 'Code', 'FileText', 'Database', 'Cloud', 'Mail',
        'MessageSquare', 'Bell', 'Search', 'Filter', 'Calculator',
        'Globe', 'Link', 'Image', 'File', 'Folder', 'Hash',
        'Type', 'AlignLeft', 'List', 'Grid', 'Layers', 'Box',
        'Package', 'Archive', 'Download', 'Upload', 'Send', 'Zap',
        'Play', 'Pause', 'Square', 'Circle', 'Triangle', 'Star',
        'Heart', 'Flag', 'Bookmark', 'Tag', 'Clock', 'Calendar',
        'User', 'Users', 'Shield', 'Lock', 'Key', 'Settings',
        'Tool', 'Wrench', 'Sliders', 'ToggleLeft', 'Check', 'X',
        'Plus', 'Minus', 'ArrowRight', 'ArrowLeft', 'ArrowUp', 'ArrowDown',
        'ChevronRight', 'ChevronLeft', 'ChevronsRight', 'ChevronsLeft',
        'Eye', 'EyeOff', 'Camera', 'Video', 'Mic', 'Volume2',
        'Cpu', 'HardDrive', 'Server', 'Terminal', 'Code2', 'GitBranch',
        'Smartphone', 'Laptop', 'Monitor', 'Tablet', 'Watch',
    }

    def __init__(self, strict_mode: bool = True):
        """
        Initialize validator

        Args:
            strict_mode: If True, raise errors. If False, return warnings.
        """
        self.strict_mode = strict_mode
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self, metadata: Dict[str, Any]) -> bool:
        """
        Validate module metadata

        Args:
            metadata: Module metadata dictionary

        Returns:
            True if valid, False otherwise

        Raises:
            ValidationError: If strict_mode and validation fails
        """
        self.errors = []
        self.warnings = []

        # Run all validation checks
        self._validate_module_id(metadata)
        self._validate_version(metadata)
        self._validate_category(metadata)
        self._validate_labels(metadata)
        self._validate_visual(metadata)
        self._validate_types(metadata)
        self._validate_schemas(metadata)
        self._validate_i18n(metadata)
        self._validate_examples(metadata)
        self._validate_metadata_fields(metadata)

        # Check results
        if self.errors:
            error_msg = '\n'.join([f'  - {e}' for e in self.errors])
            if self.strict_mode:
                raise ValidationError(f'Module validation failed:\n{error_msg}')
            return False

        return True

    def _validate_module_id(self, metadata: Dict[str, Any]):
        """Validate module_id format: category.subcategory.action"""
        module_id = metadata.get('module_id', '')

        # Check format: lowercase with dots
        if not re.match(r'^[a-z]+\.[a-z0-9_]+\.[a-z0-9_]+$', module_id):
            self.errors.append(
                f"module_id '{module_id}' must match format: category.subcategory.action "
                f"(lowercase, dots, underscores allowed in action)"
            )

        # Check parts
        parts = module_id.split('.')
        if len(parts) != 3:
            self.errors.append(
                f"module_id '{module_id}' must have exactly 3 parts: category.subcategory.action"
            )
        else:
            category, subcategory, action = parts

            # Category must match metadata
            if metadata.get('category') != category:
                self.errors.append(
                    f"module_id category '{category}' doesn't match metadata category '{metadata.get('category')}'"
                )

    def _validate_version(self, metadata: Dict[str, Any]):
        """Validate semantic version"""
        version = metadata.get('version', '')

        if not re.match(r'^\d+\.\d+\.\d+$', version):
            self.errors.append(
                f"version '{version}' must be semantic version (e.g., '1.0.0')"
            )

    def _validate_category(self, metadata: Dict[str, Any]):
        """Validate category is in allowed list"""
        category = metadata.get('category', '')

        if category not in self.ALLOWED_CATEGORIES:
            self.errors.append(
                f"category '{category}' not allowed. Must be one of: {', '.join(sorted(self.ALLOWED_CATEGORIES))}"
            )

        # Subcategory must be lowercase
        subcategory = metadata.get('subcategory', '')
        if not subcategory.islower():
            self.errors.append(
                f"subcategory '{subcategory}' must be lowercase"
            )

    def _validate_labels(self, metadata: Dict[str, Any]):
        """Validate label format and content"""
        label = metadata.get('label', '')

        # Must be Title Case
        if not self._is_title_case(label):
            self.errors.append(
                f"label '{label}' must be Title Case (e.g., 'Send Slack Message')"
            )

        # Must be 2-5 words
        word_count = len(label.split())
        if word_count < 2 or word_count > 5:
            self.warnings.append(
                f"label '{label}' should be 2-5 words (currently {word_count})"
            )

        # Description length
        description = metadata.get('description', '')
        if len(description) < 10:
            self.errors.append(
                f"description must be at least 10 characters (currently {len(description)})"
            )
        elif len(description) > 200:
            self.warnings.append(
                f"description should be under 200 characters (currently {len(description)})"
            )

    def _validate_visual(self, metadata: Dict[str, Any]):
        """Validate icon and color"""
        # Icon must be valid Lucide icon
        icon = metadata.get('icon', '')
        if icon not in self.VALID_ICONS:
            self.warnings.append(
                f"icon '{icon}' may not be a valid Lucide icon. "
                f"Recommended: {', '.join(list(self.VALID_ICONS)[:10])}..."
            )

        # Color must be valid hex
        color = metadata.get('color', '')
        if not re.match(r'^#[0-9A-F]{6}$', color, re.IGNORECASE):
            self.errors.append(
                f"color '{color}' must be valid hex color (e.g., '#FF5733')"
            )

    def _validate_types(self, metadata: Dict[str, Any]):
        """Validate input/output types"""
        input_types = metadata.get('input_types', [])
        output_types = metadata.get('output_types', [])

        # Check if types are valid
        for t in input_types:
            if t not in self.STANDARD_TYPES:
                self.warnings.append(
                    f"input_type '{t}' is not a standard type. "
                    f"Consider using: {', '.join(list(self.STANDARD_TYPES)[:10])}..."
                )

        for t in output_types:
            if t not in self.STANDARD_TYPES:
                self.warnings.append(
                    f"output_type '{t}' is not a standard type."
                )

    def _validate_schemas(self, metadata: Dict[str, Any]):
        """Validate params and output schemas"""
        params_schema = metadata.get('params_schema', {})
        output_schema = metadata.get('output_schema', {})

        # Check params_schema structure
        if not isinstance(params_schema, dict):
            self.errors.append("params_schema must be a dictionary")
        else:
            for param_name, param_def in params_schema.items():
                if not isinstance(param_def, dict):
                    self.errors.append(
                        f"params_schema['{param_name}'] must be a dictionary"
                    )
                else:
                    # Check required fields
                    if 'type' not in param_def:
                        self.errors.append(
                            f"params_schema['{param_name}'] missing 'type' field"
                        )
                    if 'label' not in param_def:
                        self.warnings.append(
                            f"params_schema['{param_name}'] missing 'label' field"
                        )

        # Check output_schema structure
        if not isinstance(output_schema, dict):
            self.errors.append("output_schema must be a dictionary")

    def _validate_i18n(self, metadata: Dict[str, Any]):
        """Validate i18n keys"""
        label_key = metadata.get('label_key', '')
        description_key = metadata.get('description_key', '')

        # Check format: modules.category.subcategory.action.field
        i18n_pattern = r'^modules\.[a-z]+\.[a-z0-9_]+\.[a-z0-9_]+\.(label|description)$'

        if not re.match(i18n_pattern, label_key):
            self.errors.append(
                f"label_key '{label_key}' must match format: "
                f"modules.category.subcategory.action.label"
            )

        if not re.match(i18n_pattern, description_key):
            self.errors.append(
                f"description_key '{description_key}' must match format: "
                f"modules.category.subcategory.action.description"
            )

    def _validate_examples(self, metadata: Dict[str, Any]):
        """Validate examples"""
        examples = metadata.get('examples', [])

        if not examples or len(examples) < 1:
            self.errors.append("Must have at least 1 example")

        for i, example in enumerate(examples):
            if not isinstance(example, dict):
                self.errors.append(f"examples[{i}] must be a dictionary")
            else:
                if 'title' not in example:
                    self.warnings.append(f"examples[{i}] missing 'title'")
                if 'params' not in example:
                    self.errors.append(f"examples[{i}] missing 'params'")

    def _validate_metadata_fields(self, metadata: Dict[str, Any]):
        """Validate required metadata fields"""
        required_fields = [
            'module_id', 'version', 'category', 'subcategory', 'tags',
            'label', 'label_key', 'description', 'description_key',
            'icon', 'color', 'params_schema', 'output_schema',
            'examples', 'author', 'license'
        ]

        for field in required_fields:
            if field not in metadata:
                self.errors.append(f"Required field '{field}' is missing")

        # Tags must have 2-5 items
        tags = metadata.get('tags', [])
        if len(tags) < 2:
            self.warnings.append("Should have at least 2 tags")
        elif len(tags) > 5:
            self.warnings.append("Should have at most 5 tags")

    def _is_title_case(self, text: str) -> bool:
        """Check if text is in Title Case"""
        if not text:
            return False

        # Allow common exceptions
        exceptions = {'a', 'an', 'the', 'and', 'or', 'but', 'for', 'to', 'in', 'on', 'at'}

        words = text.split()
        for i, word in enumerate(words):
            # First word must be capitalized
            if i == 0:
                if not word[0].isupper():
                    return False
            else:
                # Other words: either capitalized or an exception
                if word.lower() not in exceptions and not word[0].isupper():
                    return False

        return True

    def get_report(self) -> str:
        """Get validation report as string"""
        report = []

        if self.errors:
            report.append("Errors:")
            for error in self.errors:
                report.append(f"  ✗ {error}")

        if self.warnings:
            report.append("Warnings:")
            for warning in self.warnings:
                report.append(f"  ⚠ {warning}")

        if not self.errors and not self.warnings:
            report.append("✓ All checks passed")

        return '\n'.join(report)


def validate_module(metadata: Dict[str, Any], strict: bool = True) -> bool:
    """
    Convenience function to validate module metadata

    Args:
        metadata: Module metadata dictionary
        strict: If True, raise on errors. If False, return warnings.

    Returns:
        True if valid, False otherwise
    """
    validator = ModuleValidator(strict_mode=strict)
    return validator.validate(metadata)
