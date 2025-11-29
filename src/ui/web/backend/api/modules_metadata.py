"""
Modules Metadata API
Provides module definitions for UI builder (similar to Swagger/n8n)
"""
from fastapi import APIRouter, Query, Body
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from src.core.modules.registry import ModuleRegistry

router = APIRouter(prefix="/api/modules", tags=["modules"])


class ValidateRequest(BaseModel):
    """Request model for parameter validation"""
    module_id: str
    params: Dict[str, Any]


@router.get("/list")
async def get_modules_list(
    category: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    lang: str = "en"
) -> Dict[str, Any]:
    """
    Get all available modules with their metadata

    Similar to Swagger API docs, this endpoint provides all module definitions
    for the UI builder to dynamically generate forms.

    Args:
        category: Filter by category (e.g., "browser", "api", "ai")
        tags: Filter by tags
        lang: Language for i18n (en, zh, ja)

    Returns:
        {
            "modules": [
                {
                    "module_id": "core.browser.launch",
                    "label": "Launch Browser",
                    "label_key": "modules.browser.launch.label",
                    "description": "...",
                    "category": "browser",
                    "icon": "Monitor",
                    "color": "#4A90E2",
                    "params_schema": {...},
                    "output_schema": {...}
                }
            ],
            "count": 20,
            "categories": ["browser", "api", "ai"]
        }
    """
    # Get all metadata with filters
    all_metadata = ModuleRegistry.get_all_metadata(
        category=category,
        tags=tags,
        lang=lang
    )

    # Convert to list
    modules = list(all_metadata.values())

    # Extract unique categories
    categories = list(set(m.get('category', 'other') for m in modules))

    return {
        "modules": modules,
        "count": len(modules),
        "categories": sorted(categories)
    }


@router.get("/detail/{module_id}")
async def get_module_detail(
    module_id: str,
    lang: str = "en"
) -> Dict[str, Any]:
    """
    Get detailed metadata for a specific module

    Args:
        module_id: Module identifier (e.g., "core.browser.launch")
        lang: Language for i18n

    Returns:
        Complete module metadata including params schema
    """
    metadata = ModuleRegistry.get_metadata(module_id, lang=lang)

    if not metadata:
        return {
            "error": "Module not found",
            "module_id": module_id
        }

    return metadata


@router.get("/categories")
async def get_categories() -> Dict[str, Any]:
    """
    Get all available module categories

    Returns:
        {
            "categories": [
                {
                    "id": "browser",
                    "label": "Browser Automation",
                    "count": 9,
                    "icon": "Monitor"
                }
            ]
        }
    """
    all_metadata = ModuleRegistry.get_all_metadata()

    # Group by category
    category_groups = {}
    for module_id, metadata in all_metadata.items():
        cat = metadata.get('category', 'other')
        if cat not in category_groups:
            category_groups[cat] = []
        category_groups[cat].append(metadata)

    # Build category info
    categories = []
    for cat_id, modules in category_groups.items():
        # Determine icon from first module
        icon = modules[0].get('icon', 'Folder')

        categories.append({
            'id': cat_id,
            'label': cat_id.capitalize(),
            'count': len(modules),
            'icon': icon
        })

    return {
        "categories": sorted(categories, key=lambda x: x['id'])
    }


@router.get("/schema/{module_id}")
async def get_module_schema(
    module_id: str,
    lang: str = "en"
) -> Dict[str, Any]:
    """
    Get parameter schema for a module (for form generation)

    Similar to JSON Schema / OpenAPI spec

    Args:
        module_id: Module identifier
        lang: Language for i18n

    Returns:
        {
            "params_schema": {
                "url": {
                    "type": "string",
                    "label": "URL",
                    "description": "Target URL to navigate",
                    "required": true,
                    "placeholder": "https://example.com"
                }
            },
            "output_schema": {...}
        }
    """
    metadata = ModuleRegistry.get_metadata(module_id, lang=lang)

    if not metadata:
        return {
            "error": "Module not found",
            "module_id": module_id
        }

    return {
        "params_schema": metadata.get('params_schema', {}),
        "output_schema": metadata.get('output_schema', {})
    }


@router.post("/validate")
async def validate_module_params(
    request: ValidateRequest
) -> Dict[str, Any]:
    """
    Validate module parameters against schema

    Args:
        request: Validation request containing module_id and params

    Returns:
        {
            "valid": true/false,
            "errors": [...] if invalid
        }
    """
    module_id = request.module_id
    params = request.params
    metadata = ModuleRegistry.get_metadata(module_id)

    if not metadata:
        return {
            "valid": False,
            "errors": [f"Module not found: {module_id}"]
        }

    params_schema = metadata.get('params_schema', {})
    errors = []

    # Check required params
    for param_name, param_def in params_schema.items():
        if isinstance(param_def, dict) and param_def.get('required', False):
            if param_name not in params:
                errors.append(f"Missing required parameter: {param_name}")

    # Type validation (basic)
    for param_name, param_value in params.items():
        if param_name in params_schema:
            param_def = params_schema[param_name]
            if isinstance(param_def, dict):
                expected_type = param_def.get('type')
                if expected_type:
                    # Basic type checking
                    if expected_type == 'string' and not isinstance(param_value, str):
                        errors.append(f"{param_name}: expected string, got {type(param_value).__name__}")
                    elif expected_type == 'number' and not isinstance(param_value, (int, float)):
                        errors.append(f"{param_name}: expected number, got {type(param_value).__name__}")
                    elif expected_type == 'boolean' and not isinstance(param_value, bool):
                        errors.append(f"{param_name}: expected boolean, got {type(param_value).__name__}")

    return {
        "valid": len(errors) == 0,
        "errors": errors if errors else None
    }


@router.get("/search")
async def search_modules(
    query: str,
    lang: str = "en"
) -> Dict[str, Any]:
    """
    Search modules by name, description, or tags

    Args:
        query: Search query
        lang: Language for i18n

    Returns:
        Matching modules
    """
    all_metadata = ModuleRegistry.get_all_metadata(lang=lang)
    query_lower = query.lower()

    results = []
    for module_id, metadata in all_metadata.items():
        # Search in module_id, label, description, tags
        searchable_text = ' '.join([
            module_id,
            metadata.get('label', ''),
            metadata.get('description', ''),
            ' '.join(metadata.get('tags', []))
        ]).lower()

        if query_lower in searchable_text:
            results.append(metadata)

    return {
        "results": results,
        "count": len(results),
        "query": query
    }
