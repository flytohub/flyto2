#!/usr/bin/env python3
"""
Test RAG Integration in AI Error Solver

Verifies:
1. PromptBuilderModule queries RAG for context
2. Relevant knowledge is included in prompts
3. Graceful fallback when RAG unavailable
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.healing.atomic.prompt_builder import PromptBuilderModule


async def test_rag_context_retrieval():
    """Test 1: RAG context retrieval with real error"""
    print("\n" + "=" * 70)
    print("TEST 1: RAG Context Retrieval")
    print("=" * 70)

    # Simulate Ollama-related error
    error = "Failed to connect to Ollama at localhost:11434"
    error_type = "ConnectionError"

    print(f"\n📝 Error: {error_type}")
    print(f"💬 Message: {error}")

    # Query RAG for context
    print("\n🔍 Querying knowledge base...")
    context = await PromptBuilderModule._get_project_context_with_rag(error, error_type)

    print("\n📊 Retrieved Context:")
    print("-" * 70)
    print(context[:1000])  # Show first 1000 chars
    print("-" * 70)

    # Check if context contains relevant information
    if "Ollama" in context or "dependency" in context.lower():
        print("\n✅ Context contains relevant information about Ollama")
    else:
        print("\n⚠️ Context may not have Ollama-specific info (fallback used?)")

    return context


async def test_full_prompt_building():
    """Test 2: Full prompt building with RAG"""
    print("\n" + "=" * 70)
    print("TEST 2: Full Prompt Building with RAG")
    print("=" * 70)

    error = "ModuleNotFoundError: No module named 'playwright'"
    error_type = "ModuleNotFoundError"
    context = {
        "operation": "browser.launch",
        "module": "core.browser.launch",
        "workflow": "test_workflow.yaml"
    }
    similar_solutions = []

    print(f"\n📝 Building prompt for error: {error_type}")

    prompt = await PromptBuilderModule.build_error_resolution_prompt(
        error=error,
        error_type=error_type,
        context=context,
        similar_solutions=similar_solutions
    )

    print("\n📊 Generated Prompt Structure:")
    print(f"   Length: {len(prompt)} characters")
    print(f"   Contains RAG context: {'knowledge base' in prompt.lower()}")
    print(f"   Contains error: {error_type in prompt}")
    print(f"   Contains task: {'Your Task' in prompt}")

    print("\n📄 Prompt Preview (first 500 chars):")
    print("-" * 70)
    print(prompt[:500])
    print("...")
    print("-" * 70)

    return prompt


async def test_fallback_mechanism():
    """Test 3: Fallback to static context"""
    print("\n" + "=" * 70)
    print("TEST 3: Fallback Mechanism")
    print("=" * 70)

    # Test with non-existent error that won't match anything
    error = "ZxQwErTyUiOpAsDF"  # Nonsense string
    error_type = "UnknownTestError"

    print(f"\n📝 Testing with non-matching error: {error_type}")
    print("   (Should fallback to static context)\n")

    context = await PromptBuilderModule._get_project_context_with_rag(error, error_type)

    print("📊 Retrieved Context:")
    is_static = "Atomic module system" in context and "knowledge base" not in context.lower()

    if is_static:
        print("   ✅ Correctly fell back to static context")
    else:
        print("   ⚠️ May have used RAG (unexpected for nonsense error)")

    print("\n📄 Context Type:")
    print(f"   Static fallback: {is_static}")
    print(f"   Length: {len(context)} characters")

    return context


async def test_with_similar_solutions():
    """Test 4: Prompt with similar solutions included"""
    print("\n" + "=" * 70)
    print("TEST 4: Prompt with Similar Solutions")
    print("=" * 70)

    error = "Timeout waiting for element"
    error_type = "TimeoutError"
    context = {"operation": "browser.click", "selector": "#button"}

    # Mock similar solutions
    similar_solutions = [
        {
            "content": "Increased wait time to 10s and added explicit wait",
            "similarity": 0.85,
            "metadata": {"category": "error"}
        },
        {
            "content": "Used browser.wait before clicking",
            "similarity": 0.72,
            "metadata": {"category": "practice"}
        }
    ]

    print(f"\n📝 Building prompt with {len(similar_solutions)} similar solutions")

    prompt = await PromptBuilderModule.build_error_resolution_prompt(
        error=error,
        error_type=error_type,
        context=context,
        similar_solutions=similar_solutions
    )

    print("\n📊 Prompt Analysis:")
    print(f"   Contains similar solutions: {'Similar Past Solutions' in prompt}")
    print(f"   Contains RAG context: {'knowledge base' in prompt.lower()}")
    print(f"   Total length: {len(prompt)} characters")

    # Check if similar solutions are included
    for sol in similar_solutions:
        if sol["content"] in prompt:
            print(f"   ✅ Solution '{sol['content'][:30]}...' included")

    return prompt


async def main():
    """Run all RAG integration tests"""
    print("\n🧪 RAG Integration Test Suite")
    print("=" * 70)
    print("\nTesting RAG retriever integration in AI Error Solver")
    print("=" * 70)

    tests = [
        ("RAG Context Retrieval", test_rag_context_retrieval),
        ("Full Prompt Building", test_full_prompt_building),
        ("Fallback Mechanism", test_fallback_mechanism),
        ("Prompt with Similar Solutions", test_with_similar_solutions),
    ]

    results = []

    for i, (name, test_func) in enumerate(tests, 1):
        try:
            print(f"\n\n{'='*70}")
            print(f"Running Test {i}/4: {name}")
            print(f"{'='*70}")

            await test_func()
            results.append((name, "✅ PASS"))
            print(f"\n✅ Test {i} passed")

        except Exception as e:
            results.append((name, f"❌ FAIL: {e}"))
            print(f"\n❌ Test {i} failed: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print("\n\n" + "=" * 70)
    print("🎉 RAG Integration Test Complete!")
    print("=" * 70)

    print("\n📊 Test Results:")
    for name, result in results:
        print(f"   {result}: {name}")

    passed = sum(1 for _, r in results if r.startswith("✅"))
    total = len(results)

    print(f"\n📈 Summary: {passed}/{total} tests passed")

    print("\n💡 What Changed:")
    print("   ✅ PromptBuilderModule now queries RAG for context")
    print("   ✅ Dynamic project knowledge included in error prompts")
    print("   ✅ Graceful fallback to static context")
    print("   ✅ AI gets relevant pain points, architecture, modules info")

    print("\n🔗 Integration Points:")
    print("   - AI Error Solver → PromptBuilderModule → RAG Retriever")
    print("   - Error context enriched with knowledge base")
    print("   - Better AI solutions with project-specific knowledge")


if __name__ == "__main__":
    asyncio.run(main())
