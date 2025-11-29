#!/usr/bin/env python
"""
Launcher script for Flyto2 API server
Run from project root with correct Python path
"""
import sys
from pathlib import Path

# Ensure project root is in Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import and run the app
from src.ui.web.backend.app import app
import uvicorn

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Starting Flyto2 API Server")
    print("=" * 70)
    print(f"   API Docs: http://localhost:8000/docs")
    print(f"   Modules API: http://localhost:8000/api/modules/list")
    print(f"   Health Check: http://localhost:8000/health")
    print("=" * 70)
    print()

    uvicorn.run(app, host="0.0.0.0", port=8000)
