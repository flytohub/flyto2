#!/usr/bin/env python3
"""
Test Language Bridge Layer + RAG Retriever

Demonstrates:
1. Language detection (zh/en)
2. Chinese → English translation
3. Multilingual vector search
4. Structured query format
5. Bilingual entry creation
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.utils.language_bridge import get_language_bridge
from src.core.utils.rag_retriever import retrieve_knowledge, execute_structured_query


async def test_language_detection():
    """Test 1: Language Detection"""
    print("\n" + "=" * 70)
    print("TEST 1: Language Detection")
    print("=" * 70)

    bridge = get_language_bridge()

    test_cases = [
        "How to fix timeout error in browser module?",
        "如何修復瀏覽器模組的 timeout 錯誤？",
        "browser.click timeout issue",
        "我在抓取 yahoo.tw 時遇到問題",
        "Encountered ModuleNotFoundError: playwright"
    ]

    for text in test_cases:
        lang = bridge.detect_language(text)
        print(f"\nText: {text}")
        print(f"  → Detected: {lang}")


async def test_translation():
    """Test 2: Chinese → English Translation"""
    print("\n" + "=" * 70)
    print("TEST 2: Chinese → English Translation")
    print("=" * 70)

    bridge = get_language_bridge()

    chinese_texts = [
        "如何修復 timeout 錯誤？",
        "我在使用 browser.click 時遇到元素找不到的問題",
        "爬蟲執行失敗，顯示 ModuleNotFoundError",
        "Perfect Flow Bot 的三個錯誤處理選項"
    ]

    for text in chinese_texts:
        print(f"\nChinese: {text}")
        result = await bridge.translate_to_english(text)

        if result["success"]:
            print(f"  → English: {result['translated']}")
        else:
            print(f"  → Error: {result.get('error')}")


async def test_query_preparation():
    """Test 3: Query Preparation for Search"""
    print("\n" + "=" * 70)
    print("TEST 3: Query Preparation with Language Bridge")
    print("=" * 70)

    bridge = get_language_bridge()

    queries = [
        "timeout error in browser",  # English
        "如何修復 Ollama 未運行的問題？",  # Chinese
        "What are all the modules?",  # English
        "專案的痛點在哪裡？"  # Chinese
    ]

    for query in queries:
        print(f"\nOriginal Query: {query}")
        prepared = await bridge.prepare_query_for_search(query)

        print(f"  Language: {prepared['language']}")
        print(f"  Translated: {prepared['translated']}")
        print(f"  Search Query: {prepared['search_query']}")


async def test_vector_search():
    """Test 4: Multilingual Vector Search"""
    print("\n" + "=" * 70)
    print("TEST 4: Multilingual Vector Search")
    print("=" * 70)

    # Test English query
    print("\n📍 English Query: 'Ollama blocker'")
    results = await retrieve_knowledge(
        query="Ollama not running blocker",
        top_k=2
    )

    if results["success"]:
        print(f"  Found: {results['total']} results")
        print(f"  Original query: {results['query']['original']}")
        print(f"  Search query: {results['query']['search_query']}")

        for i, result in enumerate(results["results"][:2], 1):
            print(f"\n  Result {i}:")
            print(f"    Score: {result.get('score', 0):.4f}")
            print(f"    Content: {result.get('content', '')[:100]}...")
    else:
        print(f"  ❌ Search failed: {results.get('error')}")

    # Test Chinese query (will auto-translate)
    print("\n📍 Chinese Query: 'Ollama 為什麼是 blocker？'")
    results = await retrieve_knowledge(
        query="Ollama 為什麼是 critical blocker？",
        top_k=2
    )

    if results["success"]:
        print(f"  Found: {results['total']} results")
        print(f"  Original query (zh): {results['query']['original']}")
        print(f"  Search query (en): {results['query']['search_query']}")
        print(f"  Translated: {results['query']['translated']}")

        for i, result in enumerate(results["results"][:2], 1):
            print(f"\n  Result {i}:")
            print(f"    Score: {result.get('score', 0):.4f}")
            print(f"    Content: {result.get('content', '')[:100]}...")
    else:
        print(f"  ❌ Search failed: {results.get('error')}")


async def test_structured_query():
    """Test 5: Structured Query Format"""
    print("\n" + "=" * 70)
    print("TEST 5: Structured [RETRIEVE KNOWLEDGE] Format")
    print("=" * 70)

    request = """[RETRIEVE KNOWLEDGE]
query: What are the critical pain points?
filters:
  category: pain_point
  priority: P0
top_k: 3
[/RETRIEVE]"""

    print("\nStructured Request:")
    print(request)
    print("\nExecuting...")

    results = await execute_structured_query(request)

    if results["success"]:
        print(f"\n✅ Found: {results['total']} results")

        for i, result in enumerate(results["results"], 1):
            metadata = result.get("metadata", {})
            print(f"\n  Result {i}:")
            print(f"    Category: {metadata.get('category', 'N/A')}")
            print(f"    Priority: {metadata.get('priority', 'N/A')}")
            print(f"    Score: {result.get('score', 0):.4f}")
            print(f"    Content: {result.get('content', '')[:150]}...")
    else:
        print(f"\n❌ Query failed: {results.get('error')}")


async def test_bilingual_entry():
    """Test 6: Bilingual Entry Creation"""
    print("\n" + "=" * 70)
    print("TEST 6: Bilingual Entry Creation")
    print("=" * 70)

    bridge = get_language_bridge()

    # Chinese content
    content = "我在使用 browser.click 時遇到 timeout 錯誤，解決方法是增加等待時間"
    metadata = {
        "category": "practice",
        "source": "daily_practice",
        "module_id": "browser.click",
        "importance": 0.8
    }

    print(f"\nOriginal Content (zh):")
    print(f"  {content}")

    entries = await bridge.create_bilingual_entry(content, metadata)

    print(f"\nCreated {len(entries)} entries:")

    for i, entry in enumerate(entries, 1):
        lang = entry["metadata"]["language"]
        is_translated = entry["metadata"].get("is_translated", False)

        print(f"\nEntry {i}:")
        print(f"  Language: {lang}")
        print(f"  Translated: {is_translated}")
        print(f"  Content: {entry['content'][:100]}...")


async def main():
    """Run all tests"""
    print("\n🧪 Language Bridge + RAG Retriever Test Suite")
    print("=" * 70)

    tests = [
        ("Language Detection", test_language_detection),
        ("Translation (zh→en)", test_translation),
        ("Query Preparation", test_query_preparation),
        ("Vector Search (Multilingual)", test_vector_search),
        ("Structured Query Format", test_structured_query),
        ("Bilingual Entry Creation", test_bilingual_entry),
    ]

    for i, (name, test_func) in enumerate(tests, 1):
        try:
            print(f"\n\n{'='*70}")
            print(f"Running Test {i}/6: {name}")
            print(f"{'='*70}")

            await test_func()

            print(f"\n✅ Test {i} passed")

        except Exception as e:
            print(f"\n❌ Test {i} failed: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 70)
    print("🎉 Test Suite Complete!")
    print("=" * 70)

    print("\n💡 How to use in your code:")
    print("""
# 1. Simple retrieval (any language)
from src.core.utils.rag_retriever import retrieve_knowledge

# Chinese query (auto-translates to EN)
results = await retrieve_knowledge("如何修復 Ollama 錯誤？")

# English query (direct search)
results = await retrieve_knowledge("How to fix Ollama error?")

# 2. Structured query
from src.core.utils.rag_retriever import execute_structured_query

request = '''
[RETRIEVE KNOWLEDGE]
query: browser timeout errors
filters:
  category: error
  module_id: browser.click
top_k: 5
[/RETRIEVE]
'''

results = await execute_structured_query(request)

# 3. Store bilingual entries
from src.core.utils.language_bridge import get_language_bridge

bridge = get_language_bridge()
entries = await bridge.create_bilingual_entry(
    content="你的中文內容",
    metadata={"category": "practice", "module_id": "browser.click"}
)

# Store both zh and en versions to Qdrant
for entry in entries:
    await vector_store(entry["content"], entry["metadata"])
""")


if __name__ == "__main__":
    asyncio.run(main())
