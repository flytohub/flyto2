"""
Module System - Core Registration and Execution
"""
from .registry import ModuleRegistry
from .base import BaseModule

# Import all core modules to trigger registration
from . import browser_modules
from . import api_modules
from . import atomic  # Atomic Modules

# Optional: Import third-party integrations if available
try:
    from src.integrations import openai_integration
except ImportError:
    pass  # OpenAI integration not installed

__all__ = ['ModuleRegistry', 'BaseModule']
