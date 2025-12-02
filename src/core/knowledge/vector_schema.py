"""
VectorDB Schema - Simplified version for document ingestion

Defines metadata schema for vectors stored in Qdrant
"""

from typing import Dict, Any
from datetime import datetime
from enum import Enum


class VectorType(str, Enum):
    """Vector content type"""
    ERROR = "error"
    FIX = "fix"
    MODULE = "module"
    PRACTICE = "practice"
    ARCHITECTURE = "architecture"
    PAIN_POINT = "pain_point"


class VectorCategory(str, Enum):
    """Vector category (domain)"""
    BROWSER = "browser"
    CRAWLER = "crawler"
    OLLAMA = "ollama"
    VECTOR_DB = "vector_db"
    EVOLUTION = "evolution"
    DEPENDENCY = "dependency"
    GENERAL = "general"


class VectorImportance(str, Enum):
    """Importance level for prioritization"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class VectorStatus(str, Enum):
    """Vector status for lifecycle management"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class VectorSource(str, Enum):
    """Where this vector came from"""
    MANUAL = "manual"
    ERROR_SOLVER = "error_solver"
    EVOLUTION_PIPELINE = "evolution_pipeline"
    TRAINING = "training"
    DOCUMENTATION = "documentation"


def create_module_metadata(
    module_id: str,
    category: VectorCategory,
    importance: VectorImportance = VectorImportance.MEDIUM
) -> Dict[str, Any]:
    """Create metadata for module documentation vectors"""
    return {
        "type": VectorType.MODULE.value,
        "category": category.value,
        "importance": importance.value,
        "status": VectorStatus.ACTIVE.value,
        "source": VectorSource.DOCUMENTATION.value,
        "timestamp": datetime.now().isoformat(),
        "module_id": module_id
    }
