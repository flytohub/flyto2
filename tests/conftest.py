"""
Pytest configuration for tests
Ensures project root is in Python path
"""
import sys
from pathlib import Path

# Add project root to Python path
# Since this is in tests/, go up one level to project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
