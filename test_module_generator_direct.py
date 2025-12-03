#!/usr/bin/env python3
"""
Direct test of ModuleGenerator to debug the "Exception" error
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.meta.module_generator import ModuleGenerator

# Test spec from GPT-4o
spec = {
    "module_id": "image.download",
    "description": "Download an image from a URL",
    "category": "image",
    "params": {
        "url": "str - Image URL to download",
        "output_path": "str - Path to save the downloaded image"
    },
    "returns": "dict with status and file_path",
    "implementation_code": """# Download image using requests
import requests

response = requests.get(self.url, timeout=30)
response.raise_for_status()

# Save to file
with open(self.output_path, 'wb') as f:
    f.write(response.content)

return {
    "status": "success",
    "file_path": self.output_path,
    "size_bytes": len(response.content)
}""",
    "suggested_imports": ["import requests"]
}

print("Testing ModuleGenerator with spec:")
print(f"  Module ID: {spec['module_id']}")
print(f"  Category: {spec['category']}")
print()

try:
    generator = ModuleGenerator()
    result = generator.generate_module(spec)

    if result["success"]:
        print("✅ SUCCESS!")
        print(f"  Module path: {result['module_path']}")
        print(f"  Test path: {result['test_path']}")
        print()
        print("Generated code preview:")
        print("=" * 80)
        print(result['code'][:500])
        print("...")
    else:
        print("❌ FAILED!")
        print("Errors:")
        for error in result.get("errors", []):
            print(f"  - {error}")

except Exception as e:
    print(f"❌ EXCEPTION: {e}")
    import traceback
    traceback.print_exc()
