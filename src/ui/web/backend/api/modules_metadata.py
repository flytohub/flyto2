"""
Modules Metadata API
Provides module definitions for UI builder (similar to Swagger/n8n)
"""

from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from src.core.modules.registry import ModuleRegistry

router = APIRouter(prefix="/api/modules", tags=["modules"])


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class ModuleMetadata(BaseModel):
    """Normalized module metadata for UI / docs / search."""
    module_id: str
    label: Optional[str] = None
    label_key: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    tags: Optional[List[str]] = None
    params_schema: Dict[str, Any] = {}
    output_schema: Dict[str, Any] = {}

    class Config:
        # Allow extra keys from ModuleRegistry without exploding
        extra = "allow"


class ModulesListResponse(BaseModel):
    modules: List[ModuleMetadata]
    count: int
    categories: List[str]


class CategoryInfo(BaseModel):
    id: str
    label: str
    count: int
    icon: str


class CategoriesResponse(BaseModel):
    categories: List[CategoryInfo]


class ModuleSchemaResponse(BaseModel):
    params_schema: Dict[str, Any]
    output_schema: Dict[str, Any]


class ValidateRequest(BaseModel):
    """Request model for parameter validation"""
    module_id: str
    params: Dict[str, Any]


class ValidateResponse(BaseModel):
    valid: bool
    errors: Optional[List[str]] = None


class SearchResponse(BaseModel):
    results: List[ModuleMetadata]
    count: int
    query: str


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_module_or_404(module_id: str, lang: str = "en") -> Dict[str, Any]:
    """Fetch metadata or raise 404 if module does not exist."""
    metadata = ModuleRegistry.get_metadata(module_id, lang=lang)
    if not metadata:
        raise HTTPException(
            status_code=404,
            detail=f"Module not found: {module_id}",
        )
    return metadata


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/list", response_model=ModulesListResponse)
async def get_modules_list(
    category: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    lang: str = "en",
) -> ModulesListResponse:
    """
    Get all available modules with their metadata.

    Similar to Swagger API docs, this endpoint provides all module definitions
    for the UI builder to dynamically generate forms.

    Args:
        category: Filter by category (e.g., "browser", "api", "ai")
        tags: Filter by tags
        lang: Language for i18n (en, zh, ja)

    Returns:
        {
            "modules": [...],
            "count": 20,
            "categories": ["browser", "api", "ai"]
        }
    """
    # Get all metadata with filters
    all_metadata = ModuleRegistry.get_all_metadata(
        category=category,
        tags=tags,
        lang=lang,
    )

    modules: List[ModuleMetadata] = []
    for module_id, meta in all_metadata.items():
        # Ensure module_id is always present in the metadata object
        merged = {"module_id": module_id, **meta}
        modules.append(ModuleMetadata(**merged))

    # Extract unique categories (fallback to "other")
    categories = sorted({m.category or "other" for m in modules})

    return ModulesListResponse(
        modules=modules,
        count=len(modules),
        categories=categories,
    )


@router.get("/detail/{module_id}", response_model=ModuleMetadata)
async def get_module_detail(
    module_id: str,
    lang: str = "en",
) -> ModuleMetadata:
    """
    Get detailed metadata for a specific module.

    Args:
        module_id: Module identifier (e.g., "core.browser.launch")
        lang: Language for i18n

    Returns:
        Complete module metadata including params schema
    """
    metadata = _get_module_or_404(module_id, lang=lang)
    merged = {"module_id": module_id, **metadata}
    return ModuleMetadata(**merged)


@router.get("/categories", response_model=CategoriesResponse)
async def get_categories(
    lang: str = "en",
) -> CategoriesResponse:
    """
    Get all available module categories.

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
    all_metadata = ModuleRegistry.get_all_metadata(lang=lang)

    # Group by category
    category_groups: Dict[str, List[Dict[str, Any]]] = {}
    for module_id, metadata in all_metadata.items():
        cat = metadata.get("category", "other")
        category_groups.setdefault(cat, []).append(metadata)

    categories: List[CategoryInfo] = []
    for cat_id, modules in category_groups.items():
        first = modules[0]
        icon = first.get("icon", "Folder")
        # 如果未來有 i18n category label，可從 metadata 拿；暫時用 capitalize
        label = first.get("category_label") or cat_id.capitalize()

        categories.append(
            CategoryInfo(
                id=cat_id,
                label=label,
                count=len(modules),
                icon=icon,
            )
        )

    return CategoriesResponse(
        categories=sorted(categories, key=lambda x: x.id),
    )


@router.get("/schema/{module_id}", response_model=ModuleSchemaResponse)
async def get_module_schema(
    module_id: str,
    lang: str = "en",
) -> ModuleSchemaResponse:
    """
    Get parameter schema for a module (for form generation).

    Similar to JSON Schema / OpenAPI spec.

    Args:
        module_id: Module identifier
        lang: Language for i18n

    Returns:
        {
            "params_schema": {...},
            "output_schema": {...}
        }
    """
    metadata = _get_module_or_404(module_id, lang=lang)

    return ModuleSchemaResponse(
        params_schema=metadata.get("params_schema", {}) or {},
        output_schema=metadata.get("output_schema", {}) or {},
    )


@router.post("/validate", response_model=ValidateResponse)
async def validate_module_params(
    request: ValidateRequest,
) -> ValidateResponse:
    """
    Validate module parameters against schema.

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

    # 不帶 lang，表示用預設語言的 schema 來驗證
    metadata = _get_module_or_404(module_id, lang="en")

    params_schema: Dict[str, Any] = metadata.get("params_schema", {}) or {}
    errors: List[str] = []

    # 1) Check required params
    for param_name, param_def in params_schema.items():
        if isinstance(param_def, dict) and param_def.get("required", False):
            if param_name not in params:
                errors.append(f"Missing required parameter: {param_name}")

    # 2) Unknown params
    for param_name in params.keys():
        if param_name not in params_schema:
            errors.append(f"Unknown parameter: {param_name}")

    # 3) Basic type + enum validation
    for param_name, param_value in params.items():
        param_def = params_schema.get(param_name)
        if not isinstance(param_def, dict):
            continue

        expected_type = param_def.get("type")
        if expected_type:
            # Primitive types
            if expected_type == "string" and not isinstance(param_value, str):
                errors.append(
                    f"{param_name}: expected string, got {type(param_value).__name__}"
                )
            elif expected_type == "number" and not isinstance(
                param_value, (int, float)
            ):
                errors.append(
                    f"{param_name}: expected number, got {type(param_value).__name__}"
                )
            elif expected_type == "boolean" and not isinstance(param_value, bool):
                errors.append(
                    f"{param_name}: expected boolean, got {type(param_value).__name__}"
                )
            elif expected_type == "array" and not isinstance(param_value, list):
                errors.append(
                    f"{param_name}: expected array, got {type(param_value).__name__}"
                )

        # Enum validation
        allowed_values = param_def.get("enum")
        if allowed_values and param_value not in allowed_values:
            errors.append(
                f"{param_name}: value {param_value!r} is not in allowed set {allowed_values}"
            )

    return ValidateResponse(
        valid=len(errors) == 0,
        errors=errors or None,
    )


@router.get("/search", response_model=SearchResponse)
async def search_modules(
    query: str,
    lang: str = "en",
) -> SearchResponse:
    """
    Search modules by name, description, or tags.

    Args:
        query: Search query
        lang: Language for i18n

    Returns:
        Matching modules
    """
    all_metadata = ModuleRegistry.get_all_metadata(lang=lang)
    query_lower = query.lower()

    results: List[ModuleMetadata] = []
    for module_id, metadata in all_metadata.items():
        merged = {"module_id": module_id, **metadata}
        m = ModuleMetadata(**merged)

        searchable_text = " ".join(
            [
                m.module_id,
                m.label or "",
                m.description or "",
                " ".join(m.tags or []),
            ]
        ).lower()

        if query_lower in searchable_text:
            results.append(m)

    return SearchResponse(
        results=results,
        count=len(results),
        query=query,
    )
