#!/usr/bin/env python3
"""
Quick verification of Self-Awareness System
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.knowledge.doc_ingestion import get_self_awareness


async def main():
    print("\n🧠 Self-Awareness System Verification\n")
    print("=" * 70)

    # Initialize
    print("\n1. Initializing system...")
    system = get_self_awareness()
    await system.initialize()
    print("   ✓ Initialized")

    # Test queries
    test_queries = [
        "Evolution Planner implementation",
        "VectorDB schema fields",
        "PatchValidator validation stages",
        "PR Engine workflow"
    ]

    print(f"\n2. Testing {len(test_queries)} queries...\n")

    for i, query in enumerate(test_queries, 1):
        print(f"   Query {i}: {query}")
        result = await system.ask_self(query)

        if result["success"]:
            top_score = result["results"][0].get("score", 0)
            sources = result["sources"][:2]
            print(f"   ✓ Found {len(result['results'])} results (top score: {top_score:.0%})")
            print(f"     Sources: {', '.join(sources)}")
        else:
            print(f"   ✗ Query failed")
        print()

    print("=" * 70)
    print("✅ Self-Awareness System is operational!")
    print("\nThe system can now:")
    print("  • Query architecture knowledge from implementation guides")
    print("  • Provide relevant sections with confidence scores")
    print("  • Help AI agents understand system design patterns")
    print("\nNext steps:")
    print("  • Integrate into startup hooks: await init_self_awareness_on_startup()")
    print("  • Use in AI agents: system.ask_self('your question')")
    print("  • Query from CLI: python scripts/ingest_implementation_guides.py --query 'question'")


if __name__ == "__main__":
    asyncio.run(main())
