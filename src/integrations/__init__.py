"""
Third-party Integrations Package

This package contains optional integrations with third-party services.
Each integration can be installed separately.

Available Integrations:
- OpenAI (openai_integration) - Requires: pip install openai
- More integrations coming soon...

Usage:
    # Install integration dependencies
    pip install openai  # For OpenAI integration

    # Import and use
    from src.integrations import openai_integration
"""

def load_integration(name: str):
    """
    Load an integration by name

    Args:
        name: Integration name (e.g., 'openai', 'anthropic')

    Returns:
        Integration module or None if not available
    """
    try:
        if name == 'openai':
            from . import openai_integration
            return openai_integration
        else:
            return None
    except ImportError as e:
        print(f"Warning: Integration '{name}' not available. Install dependencies: pip install {name}")
        return None

__all__ = ['load_integration']
