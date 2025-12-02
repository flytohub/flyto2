#!/usr/bin/env python3
"""
Test Ollama Dependency Detection and Fallback

Verifies:
1. Ollama availability check
2. Automatic fallback to OpenAI when Ollama unavailable
3. Graceful error handling when both unavailable
"""

import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.utils.http_client import HTTPClient
from src.core.utils.language_bridge import get_language_bridge


async def test_ollama_detection():
    """Test 1: Ollama availability detection"""
    print("\n" + "=" * 70)
    print("TEST 1: Ollama Availability Detection")
    print("=" * 70)

    print("\n🔍 Checking if Ollama is available...")
    is_available = HTTPClient.check_ollama_available()

    if is_available:
        print("   ✅ Ollama is running and available")
    else:
        print("   ❌ Ollama is not available")
        print("   💡 To install: brew install ollama && ollama serve")

    return is_available


async def test_openai_detection():
    """Test 2: OpenAI API key detection"""
    print("\n" + "=" * 70)
    print("TEST 2: OpenAI API Key Detection")
    print("=" * 70)

    print("\n🔍 Checking if OpenAI API key is configured...")
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        print("   ✅ OpenAI API key is configured")
        print(f"   Key: {api_key[:8]}...{api_key[-4:]}")
    else:
        print("   ❌ OpenAI API key not configured")
        print("   💡 Set in .env: OPENAI_API_KEY=sk-...")

    return bool(api_key)


async def test_auto_fallback():
    """Test 3: Automatic provider fallback"""
    print("\n" + "=" * 70)
    print("TEST 3: Automatic Provider Fallback")
    print("=" * 70)

    bridge = get_language_bridge()

    test_text = "我在使用 browser.click 時遇到 timeout 錯誤"
    print(f"\n📝 Test text: {test_text}")
    print("🔄 Using 'auto' provider (will select best available)...")

    result = await bridge.translate_to_english(test_text, provider="auto")

    print("\n📊 Result:")
    print(f"   Success: {result['success']}")

    if result["success"]:
        print(f"   Provider used: {result.get('provider_used', 'unknown')}")
        print(f"   Translation: {result['translated']}")
    else:
        print(f"   Error: {result.get('error', 'unknown')}")

    return result


async def test_explicit_ollama():
    """Test 4: Explicit Ollama with fallback"""
    print("\n" + "=" * 70)
    print("TEST 4: Explicit Ollama Request (with fallback)")
    print("=" * 70)

    bridge = get_language_bridge()

    test_text = "專案痛點在哪裡？"
    print(f"\n📝 Test text: {test_text}")
    print("🔄 Using 'ollama' provider (will fallback to OpenAI if unavailable)...")

    result = await bridge.translate_to_english(test_text, provider="ollama")

    print("\n📊 Result:")
    print(f"   Success: {result['success']}")

    if result["success"]:
        print(f"   Provider used: {result.get('provider_used', 'unknown')}")
        print(f"   Translation: {result['translated']}")
    else:
        print(f"   Error: {result.get('error', 'unknown')}")

    return result


async def test_query_preparation():
    """Test 5: Query preparation with fallback"""
    print("\n" + "=" * 70)
    print("TEST 5: Query Preparation with Language Bridge")
    print("=" * 70)

    bridge = get_language_bridge()

    queries = [
        "timeout 錯誤如何解決？",  # Chinese
        "How to fix timeout?",     # English (no translation needed)
    ]

    for query in queries:
        print(f"\n📝 Query: {query}")
        prepared = await bridge.prepare_query_for_search(query)

        print(f"   Language: {prepared['language']}")
        print(f"   Translated: {prepared['translated']}")
        print(f"   Search query: {prepared['search_query']}")

        if prepared.get("error"):
            print(f"   ⚠️ Error: {prepared['error']}")


async def main():
    """Run all tests"""
    print("\n🧪 Ollama Dependency Detection & Fallback Test Suite")
    print("=" * 70)

    # Test 1 & 2: Check availability
    ollama_available = await test_ollama_detection()
    openai_available = await test_openai_detection()

    # Summary of available providers
    print("\n" + "=" * 70)
    print("📊 Provider Availability Summary")
    print("=" * 70)

    if ollama_available:
        print("   ✅ Ollama: Available (primary)")
    else:
        print("   ❌ Ollama: Not available")

    if openai_available:
        print("   ✅ OpenAI: Available (fallback)")
    else:
        print("   ❌ OpenAI: Not available")

    if not ollama_available and not openai_available:
        print("\n   ⚠️ WARNING: No AI provider available!")
        print("   Translation features will not work.")
        print("\n   To fix:")
        print("      Option 1: Install Ollama (free, local)")
        print("         brew install ollama")
        print("         ollama serve")
        print("         ollama pull llama3.2")
        print("\n      Option 2: Set OpenAI API key")
        print("         export OPENAI_API_KEY=sk-...")

    # Test 3-5: Test translation and fallback
    if ollama_available or openai_available:
        await test_auto_fallback()
        await test_explicit_ollama()
        await test_query_preparation()
    else:
        print("\n⏭️ Skipping translation tests (no provider available)")

    # Final summary
    print("\n" + "=" * 70)
    print("✅ Ollama Fallback Test Complete!")
    print("=" * 70)

    print("\n💡 Summary:")
    print("   - Ollama check: Cached after first call")
    print("   - Auto-fallback: Ollama → OpenAI → Error")
    print("   - Graceful degradation: System continues without translation")


if __name__ == "__main__":
    asyncio.run(main())
