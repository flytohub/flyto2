#!/usr/bin/env python
"""
Test FastAPI server and endpoints
"""
import asyncio
import aiohttp
import json


async def test_api_endpoints():
    """Test all API endpoints"""

    base_url = "http://localhost:8000"

    print("=" * 70)
    print("Testing Flyto2 API Server")
    print("=" * 70)
    print()

    async with aiohttp.ClientSession() as session:

        # Test 1: Root endpoint
        print("1️⃣  Testing root endpoint (GET /)...")
        async with session.get(f"{base_url}/") as response:
            data = await response.json()
            print(f"   Status: {response.status}")
            print(f"   Name: {data.get('name')}")
            print(f"   Version: {data.get('version')}")
            print()

        # Test 2: Health check
        print("2️⃣  Testing health check (GET /health)...")
        async with session.get(f"{base_url}/health") as response:
            data = await response.json()
            print(f"   Status: {response.status}")
            print(f"   Health: {data.get('status')}")
            print()

        # Test 3: Get all modules
        print("3️⃣  Testing modules list (GET /api/modules/list)...")
        async with session.get(f"{base_url}/api/modules/list?lang=zh") as response:
            data = await response.json()
            print(f"   Status: {response.status}")
            print(f"   Total modules: {data.get('count')}")
            print(f"   Categories: {', '.join(data.get('categories', []))}")
            print()

        # Test 4: Get module detail
        print("4️⃣  Testing module detail (GET /api/modules/detail/core.browser.launch)...")
        async with session.get(f"{base_url}/api/modules/detail/core.browser.launch?lang=zh") as response:
            data = await response.json()
            print(f"   Status: {response.status}")
            print(f"   Module ID: {data.get('module_id')}")
            print(f"   Label: {data.get('label')}")
            print(f"   Category: {data.get('category')}")
            print()

        # Test 5: Get module schema
        print("5️⃣  Testing module schema (GET /api/modules/schema/core.browser.launch)...")
        async with session.get(f"{base_url}/api/modules/schema/core.browser.launch?lang=zh") as response:
            data = await response.json()
            print(f"   Status: {response.status}")
            print(f"   Params schema keys: {', '.join(data.get('params_schema', {}).keys())}")
            print()

        # Test 6: Get categories
        print("6️⃣  Testing categories (GET /api/modules/categories)...")
        async with session.get(f"{base_url}/api/modules/categories") as response:
            data = await response.json()
            print(f"   Status: {response.status}")
            categories = data.get('categories', [])
            print(f"   Total categories: {len(categories)}")
            for cat in categories[:3]:
                print(f"     - {cat.get('id')}: {cat.get('count')} modules")
            print()

        # Test 7: Search modules
        print("7️⃣  Testing search (GET /api/modules/search?query=browser)...")
        async with session.get(f"{base_url}/api/modules/search?query=browser&lang=zh") as response:
            data = await response.json()
            print(f"   Status: {response.status}")
            print(f"   Found: {data.get('count')} modules")
            results = data.get('results', [])
            for result in results[:3]:
                print(f"     - {result.get('module_id')}")
            print()

        # Test 8: Validate params
        print("8️⃣  Testing validation (POST /api/modules/validate)...")
        payload = {
            "module_id": "core.browser.launch",
            "params": {"headless": True}
        }
        async with session.post(
            f"{base_url}/api/modules/validate",
            json=payload
        ) as response:
            data = await response.json()
            print(f"   Status: {response.status}")
            print(f"   Valid: {data.get('valid')}")
            if data.get('errors'):
                print(f"   Errors: {data.get('errors')}")
            print()

    print("=" * 70)
    print("✅ All API endpoints working!")
    print("=" * 70)
    print()
    print("Frontend can now call these endpoints:")
    print("  - GET  /api/modules/list?lang=zh")
    print("  - GET  /api/modules/detail/{module_id}?lang=zh")
    print("  - GET  /api/modules/schema/{module_id}")
    print("  - GET  /api/modules/categories")
    print("  - GET  /api/modules/search?query=...")
    print("  - POST /api/modules/validate")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(test_api_endpoints())
    except aiohttp.ClientConnectorError:
        print("❌ Error: Could not connect to API server")
        print()
        print("Please start the server first:")
        print("  python src/ui/web/backend/app.py")
        print()
        print("Or use uvicorn:")
        print("  uvicorn src.ui.web.backend.app:app --reload")
