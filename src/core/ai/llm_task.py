"""
LLM Task Definitions
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import uuid


@dataclass
class LLMTask:
    """Represents a task for LLM to solve"""

    task_id: str = ""
    task_type: str = "analysis"  # "code_generation", "analysis", "planning", etc.
    prompt: str = ""
    system_prompt: str = ""
    expected_format: str = "json"  # "json", "text", "diff"
    expected_schema: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.task_id:
            self.task_id = str(uuid.uuid4())[:8]


@dataclass
class LLMResult:
    """Represents LLM result"""

    task_id: str
    provider: str  # "ollama", "openai", "claude"
    raw_response: str
    success: bool
    parsed_data: Dict[str, Any] = field(default_factory=dict)
    validation_errors: List[str] = field(default_factory=list)
