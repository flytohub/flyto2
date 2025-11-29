"""
Base Module Class
"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseModule(ABC):
    """Base class for all modules"""

    # Module metadata
    module_id: str = ""
    module_name: str = ""
    module_description: str = ""

    # Permission requirements
    required_permission: str = ""

    def __init__(self, params: Dict[str, Any], context: Dict[str, Any]):
        self.params = params
        self.context = context
        self.validate_params()

    @abstractmethod
    def validate_params(self):
        """Validate parameters"""
        pass

    @abstractmethod
    async def execute(self) -> Any:
        """Execute module"""
        pass

    async def run(self) -> Any:
        """Execute moduleWrapper method for"""
        return await self.execute()

    def get_metadata(self) -> Dict[str, Any]:
        """GetModule metadata"""
        return {
            "id": self.module_id,
            "name": self.module_name,
            "description": self.module_description,
            "required_permission": self.required_permission
        }
