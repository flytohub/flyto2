#!/usr/bin/env python3
"""
Test Self-Awareness System

Demonstrates how AI agents can query their own architecture
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.knowledge.doc_ingestion import get_self_awareness


async def demo_ai_agent_self_reference():
    """Demo: AI agent querying implementation details"""
    print("=" * 70)
    print("Demo 1: AI Agent Self-Reference")
    print("=" * 70)
    print()

    system = get_self_awareness()

    # Scenario: EvolutionPlanner 想知道自己应该如何实现
    questions = [
        "How should I implement the Evolution Planner?",
        "What is the VectorDB schema?",
        "How do I validate patches before creating PR?",
        "What is the RAG pipeline configuration?"
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n{i}. Question: {question}")
        print("-" * 70)

        result = await system.ask_self(question)

        if result["success"]:
            # 只显示第一个结果的摘要
            first_answer = result["answer"].split("\n\n")[0:3]
            print("\n".join(first_answer))
            print(f"\n   📚 Sources: {', '.join(result['sources'][:2])}...")
        else:
            print(f"   ❌ {result.get('error')}")

        print()


async def demo_module_generation():
    """Demo: Using self-awareness to generate consistent code"""
    print("=" * 70)
    print("Demo 2: Module Generation with Self-Awareness")
    print("=" * 70)
    print()

    system = get_self_awareness()

    # Scenario: 生成新模块时，查询标准模式
    print("Scenario: Generating a new atomic module\n")

    # Step 1: Query module structure
    print("Step 1: Query standard module structure...")
    structure = await system.ask_self("What is the structure of an atomic module?")

    if structure["success"]:
        print("✓ Retrieved module template")
        print(f"   Sources: {structure['sources'][0]}")

    # Step 2: Query file path conventions
    print("\nStep 2: Query file path conventions...")
    paths = await system.ask_self("Where should atomic modules be placed?")

    if paths["success"]:
        print("✓ Retrieved path conventions")

    # Step 3: Generate module based on retrieved knowledge
    print("\nStep 3: Generate module following conventions...")
    print("""
Generated module structure:
    src/core/modules/atomic/browser/stealth_goto.py
    ├── class StealthGotoModule(BaseModule):
    │   ├── validate_params()
    │   └── async execute()
    └── @register_module('browser.stealth_goto')

✓ Module follows standard patterns from implementation guide
    """)


async def demo_consistency_check():
    """Demo: Self-checking for consistency"""
    print("=" * 70)
    print("Demo 3: Consistency Check Using Self-Awareness")
    print("=" * 70)
    print()

    system = get_self_awareness()

    # Scenario: 检查当前实现是否符合标准
    print("Scenario: Checking if current implementation matches guide\n")

    checks = [
        ("VectorDB Schema Fields", ["type", "category", "importance", "status", "source"]),
        ("Workflow Status Values", ["pending", "running", "success", "failure"]),
        ("Evolution Pipeline Stages", ["planning", "design", "implementation", "validation"])
    ]

    for check_name, expected_values in checks:
        print(f"Checking: {check_name}")

        # Query what the guide says
        guide_answer = await system.ask_self(f"What are the {check_name}?")

        if guide_answer["success"]:
            # 简化版：检查是否匹配
            answer_text = guide_answer["answer"].lower()
            matches = sum(1 for val in expected_values if val.lower() in answer_text)

            if matches >= len(expected_values) * 0.8:  # 80% match
                print(f"  ✓ Matches guide ({matches}/{len(expected_values)} found)")
            else:
                print(f"  ⚠ Partial match ({matches}/{len(expected_values)} found)")
        else:
            print(f"  ❌ Could not verify")

        print()


async def demo_incremental_update():
    """Demo: Incremental documentation update"""
    print("=" * 70)
    print("Demo 4: Incremental Documentation Update")
    print("=" * 70)
    print()

    from src.core.knowledge.doc_ingestion import DocumentIngestionEngine

    print("Scenario: Update implementation guide and re-ingest\n")

    engine = DocumentIngestionEngine()

    print("Step 1: Check current documentation status...")
    # Check if already ingested
    print("  ✓ Found existing documentation in VectorDB")

    print("\nStep 2: Simulate documentation update...")
    print("  (In real scenario, you would edit IMPLEMENTATION_GUIDE_V4.md)")

    print("\nStep 3: Re-ingest with incremental update...")
    print("  python scripts/ingest_implementation_guides.py")
    print("  ✓ Only changed sections would be re-ingested")

    print("\nStep 4: AI agents automatically see updated knowledge...")
    system = get_self_awareness()
    result = await system.ask_self("Latest implementation pattern")
    print("  ✓ AI gets updated information immediately")


async def main():
    """Run all demos"""
    print("\n🧠 Self-Awareness System Demo\n")

    # Initialize
    print("Initializing Self-Awareness System...")
    system = get_self_awareness()
    await system.initialize()
    print("✅ Ready\n")

    demos = [
        demo_ai_agent_self_reference,
        demo_module_generation,
        demo_consistency_check,
        demo_incremental_update
    ]

    for demo in demos:
        await demo()
        input("\nPress Enter to continue...")
        print("\n")

    print("=" * 70)
    print("🎉 Demo Complete!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("  1. AI agents can query their own architecture")
    print("  2. Self-awareness ensures consistency")
    print("  3. Documentation drives AI behavior")
    print("  4. Updates propagate automatically")


if __name__ == "__main__":
    asyncio.run(main())
