"""
Module Registry - Manage all available modules

Enhanced Features:
- Multi-language support (i18n)
- Version management
- Tags and categories
- Rich metadata for module marketplace
- Filtering and querying capabilities
"""
from typing import Dict, Type, Any, Optional, List
from .base import BaseModule


def _get_localized_value(value: Any, lang: str = 'en') -> str:
    """
    Extract localized string from value

    Supports:
    1. String: returns as-is
    2. Dict: {"en": "...", "zh": "...", "ja": "..."}

    Args:
        value: Value to process (string or dict)
        lang: Language code (en, zh, ja, es)

    Returns:
        Localized string, falls back to English if specified lang not found
    """
    if isinstance(value, str):
        return value
    elif isinstance(value, dict):
        # Try to get specified language
        if lang in value:
            return value[lang]
        # Fallback to English
        if 'en' in value:
            return value['en']
        # If no English, return first available
        return next(iter(value.values())) if value else ''
    return str(value) if value else ''


class ModuleRegistry:
    """
    Module Registry - Singleton Pattern

    Manages all registered modules and their metadata.
    Provides querying, filtering, and execution capabilities.
    """

    _instance = None
    _modules: Dict[str, Type[BaseModule]] = {}
    _metadata: Dict[str, Dict[str, Any]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, module_id: str, module_class: Type[BaseModule], metadata: Optional[Dict[str, Any]] = None):
        """
        Register a module

        Args:
            module_id: Unique module identifier (e.g., "browser.goto")
            module_class: Module class inheriting from BaseModule
            metadata: Module metadata (optional)
        """
        cls._modules[module_id] = module_class
        if metadata:
            # Ensure required fields
            metadata.setdefault('module_id', module_id)
            metadata.setdefault('version', '1.0.0')
            metadata.setdefault('category', module_id.split('.')[0])
            metadata.setdefault('tags', [])
            cls._metadata[module_id] = metadata
        print(f" Module registered: {module_id}")

    @classmethod
    def unregister(cls, module_id: str):
        """Remove a module from registry"""
        if module_id in cls._modules:
            del cls._modules[module_id]
            if module_id in cls._metadata:
                del cls._metadata[module_id]
            print(f" Module unregistered: {module_id}")

    @classmethod
    def get(cls, module_id: str) -> Type[BaseModule]:
        """
        Get module class by ID

        Args:
            module_id: Module identifier

        Returns:
            Module class

        Raises:
            ValueError: If module not found
        """
        if module_id not in cls._modules:
            raise ValueError(f"Module not found: {module_id}")
        return cls._modules[module_id]

    @classmethod
    def has(cls, module_id: str) -> bool:
        """Check if module exists"""
        return module_id in cls._modules

    @classmethod
    def list_all(cls) -> Dict[str, Type[BaseModule]]:
        """List all registered module classes"""
        return cls._modules.copy()

    @classmethod
    def get_all_metadata(
        cls,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        lang: str = 'en'
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get all module metadata (with optional filtering)

        Args:
            category: Filter by category (e.g., "browser", "data")
            tags: Filter by tags (module must have at least one matching tag)
            lang: Language code for localized fields

        Returns:
            Dict of module_id -> metadata
        """
        result = {}

        for module_id, metadata in cls._metadata.items():
            # Filter by category
            if category and metadata.get('category') != category:
                continue

            # Filter by tags
            if tags:
                module_tags = metadata.get('tags', [])
                if not any(tag in module_tags for tag in tags):
                    continue

            # Localize fields
            localized_metadata = cls._localize_metadata(metadata, lang)
            result[module_id] = localized_metadata

        return result

    @classmethod
    def get_metadata(cls, module_id: str, lang: str = 'en') -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific module

        Args:
            module_id: Module identifier
            lang: Language code

        Returns:
            Localized metadata or None if not found
        """
        metadata = cls._metadata.get(module_id)
        if not metadata:
            return None
        return cls._localize_metadata(metadata, lang)

    @classmethod
    def _localize_metadata(cls, metadata: Dict[str, Any], lang: str) -> Dict[str, Any]:
        """
        Localize metadata fields based on language

        Fields that support i18n: label, description, and nested labels in params_schema
        """
        result = metadata.copy()

        # Localize top-level fields
        if 'label' in result:
            result['label'] = _get_localized_value(result['label'], lang)
        if 'description' in result:
            result['description'] = _get_localized_value(result['description'], lang)

        # Localize params_schema labels
        if 'params_schema' in result:
            params = result['params_schema'].copy()
            for param_name, param_def in params.items():
                if isinstance(param_def, dict):
                    param_copy = param_def.copy()
                    if 'label' in param_copy:
                        param_copy['label'] = _get_localized_value(param_copy['label'], lang)
                    if 'description' in param_copy:
                        param_copy['description'] = _get_localized_value(param_copy['description'], lang)
                    if 'placeholder' in param_copy:
                        param_copy['placeholder'] = _get_localized_value(param_copy['placeholder'], lang)

                    # Localize select options
                    if 'options' in param_copy and isinstance(param_copy['options'], list):
                        localized_options = []
                        for opt in param_copy['options']:
                            if isinstance(opt, dict) and 'label' in opt:
                                opt_copy = opt.copy()
                                opt_copy['label'] = _get_localized_value(opt['label'], lang)
                                localized_options.append(opt_copy)
                            else:
                                localized_options.append(opt)
                        param_copy['options'] = localized_options

                    params[param_name] = param_copy
            result['params_schema'] = params

        return result

    @classmethod
    async def execute(cls, module_id: str, params: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """
        Execute a module

        Args:
            module_id: Module identifier
            params: Parameters to pass to module
            context: Execution context (shared state, browser instance, etc.)

        Returns:
            Module execution result
        """
        module_class = cls.get(module_id)
        module_instance = module_class(params, context)
        return await module_instance.execute()


def register_module(
    module_id: str,
    version: str = "1.0.0",
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    tags: Optional[List[str]] = None,

    # Labels (support i18n via dict or string)
    label: Optional[Any] = None,
    label_key: Optional[str] = None,  # i18n translation key
    description: Optional[Any] = None,
    description_key: Optional[str] = None,  # i18n translation key

    # Visual
    icon: Optional[str] = None,
    color: Optional[str] = None,

    # Connection types (for UI compatibility)
    input_types: Optional[List[str]] = None,
    output_types: Optional[List[str]] = None,
    can_receive_from: Optional[List[str]] = None,
    can_connect_to: Optional[List[str]] = None,

    # Schema
    params_schema: Optional[Dict[str, Any]] = None,
    output_schema: Optional[Dict[str, Any]] = None,

    # Execution settings (Phase 2)
    timeout: Optional[int] = None,  # Execution timeout in seconds
    retryable: bool = False,  # Whether the module can be retried on failure
    max_retries: int = 3,  # Maximum number of retry attempts
    concurrent_safe: bool = True,  # Whether module can run concurrently

    # Security settings (Phase 2)
    requires_credentials: bool = False,  # Whether module needs API keys/credentials
    handles_sensitive_data: bool = False,  # Whether module processes sensitive data
    required_permissions: Optional[List[str]] = None,  # Required permissions

    # Advanced
    requires: Optional[List[str]] = None,
    permissions: Optional[List[str]] = None,
    examples: Optional[List[Dict[str, Any]]] = None,
    docs_url: Optional[str] = None,
    author: Optional[str] = None,
    license: str = "MIT"
):
    """
    Module registration decorator

    Example:
        @register_module(
            module_id="browser.goto",
            version="1.0.0",
            category="browser",
            subcategory="browser",
            label={"en": "Go to URL", "zh": "Go to URL"},
            description={"en": "Navigate to URL", "zh": "Navigate to specified URL"},
            icon="Globe",
            color="#8B5CF6",
            input_types=["browser_instance"],
            output_types=["page_instance"],
            can_receive_from=["browser.launch"],
            can_connect_to=["browser.*", "element.*"],
            params_schema={
                "url": {
                    "type": "string",
                    "required": True,
                    "label": {"en": "URL", "zh": "URL"}
                }
            }
        )
        class BrowserGotoModule(BaseModule):
            async def execute(self):
                # Implementation
                pass

    Args:
        module_id: Unique identifier (e.g., "browser.goto")
        version: Semantic version (default: "1.0.0")
        category: Primary category (default: extracted from module_id)
        subcategory: Optional subcategory
        tags: List of tags for filtering
        label: Display name (string or i18n dict)
        label_key: i18n translation key for label
        description: Description (string or i18n dict)
        description_key: i18n translation key for description
        icon: Icon name (e.g., "Globe", "Keyboard")
        color: Hex color code
        input_types: List of accepted input types
        output_types: List of produced output types
        can_receive_from: List of module patterns this can receive from
        can_connect_to: List of module patterns this can connect to
        params_schema: Parameter definitions
        output_schema: Output structure definition
        timeout: Execution timeout in seconds (None = no timeout)
        retryable: Whether module can be retried on failure (default: False)
        max_retries: Maximum retry attempts if retryable (default: 3)
        concurrent_safe: Whether module can run concurrently (default: True)
        requires_credentials: Whether module needs API keys/credentials
        handles_sensitive_data: Whether module processes sensitive data
        required_permissions: List of required permissions
        requires: List of required module IDs
        permissions: Required permissions
        examples: Usage examples
        docs_url: Documentation URL
        author: Module author
        license: License (default: "MIT")
    """
    def decorator(module_class_or_func):
        # Check if it's a function or a class
        import inspect
        is_function = inspect.isfunction(module_class_or_func) or inspect.iscoroutinefunction(module_class_or_func)

        if is_function:
            # Wrap function in a class
            class FunctionModuleWrapper(BaseModule):
                """Wrapper to make function-based modules work with class-based engine"""

                def __init__(self, params: Dict[str, Any], context: Dict[str, Any]):
                    self.params = params
                    self.context = context

                def validate_params(self):
                    """Validation handled by function"""
                    pass

                async def execute(self) -> Any:
                    """Execute the wrapped function"""
                    # Build context dict for function
                    func_context = {
                        'params': self.params,
                        **self.context
                    }
                    return await module_class_or_func(func_context)

            FunctionModuleWrapper.module_id = module_id
            FunctionModuleWrapper.__name__ = f"{module_class_or_func.__name__}_Wrapper"
            FunctionModuleWrapper.__doc__ = module_class_or_func.__doc__
            module_class = FunctionModuleWrapper
        else:
            # It's already a class
            module_class = module_class_or_func
            module_class.module_id = module_id

        # Build metadata
        metadata = {
            "module_id": module_id,
            "version": version,
            "category": category or module_id.split('.')[0],
            "subcategory": subcategory,
            "tags": tags or [],
            "label": label or module_id,
            "label_key": label_key,  # i18n key
            "description": description or "",
            "description_key": description_key,  # i18n key
            "icon": icon,
            "color": color,
            "input_types": input_types or [],
            "output_types": output_types or [],
            "can_receive_from": can_receive_from or [],
            "can_connect_to": can_connect_to or [],
            "params_schema": params_schema or {},
            "output_schema": output_schema or {},
            # Phase 2: Execution settings
            "timeout": timeout,
            "retryable": retryable,
            "max_retries": max_retries,
            "concurrent_safe": concurrent_safe,
            # Phase 2: Security settings
            "requires_credentials": requires_credentials,
            "handles_sensitive_data": handles_sensitive_data,
            "required_permissions": required_permissions or [],
            # Advanced
            "requires": requires or [],
            "permissions": permissions or [],
            "examples": examples or [],
            "docs_url": docs_url,
            "author": author,
            "license": license
        }

        ModuleRegistry.register(module_id, module_class, metadata)
        return module_class

    return decorator
