#!/usr/bin/env python3
"""
Ingest Implementation Guides into VectorDB

Usage:
    python scripts/ingest_implementation_guides.py          # Initial ingestion
    python scripts/ingest_implementation_guides.py --force  # Force re-ingest
    python scripts/ingest_implementation_guides.py --query "How to implement Planner?"
"""

import asyncio
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.knowledge.doc_ingestion import (
    DocumentIngestionEngine,
    SelfAwarenessSystem,
    get_self_awareness
)


async def ingest_guides(force: bool = False):
    """Ingest implementation guides"""
    print("📚 Ingesting Implementation Guides into VectorDB\n")

    engine = DocumentIngestionEngine()
    await engine.ingest_all_guides(force=force)

    print("\n✅ Ingestion complete!")
    print("\nYou can now query the guides:")
    print('  python scripts/ingest_implementation_guides.py --query "How to implement Planner?"')


async def query_guides(question: str):
    """Query implementation guides"""
    print(f"🤔 Question: {question}\n")

    system = get_self_awareness()
    result = await system.ask_self(question)

    if result["success"]:
        print("📖 Answer:\n")
        print(result["answer"])
        print(f"\n📚 Sources: {', '.join(result['sources'])}")
    else:
        print(f"❌ Error: {result.get('error')}")


async def check_status():
    """Check ingestion status"""
    print("📊 Implementation Guide Status\n")

    system = get_self_awareness()
    await system.initialize()

    # Query some test questions
    test_questions = [
        "VectorDB Schema",
        "Evolution Pipeline",
        "RAG configuration"
    ]

    print("Testing knowledge base with sample queries:\n")

    for q in test_questions:
        result = await system.ask_self(q)
        status = "✓" if result["success"] else "✗"
        print(f"  {status} {q}")

    print("\n✅ Knowledge base is operational")


async def main():
    parser = argparse.ArgumentParser(description="Ingest and query implementation guides")
    parser.add_argument("--force", action="store_true", help="Force re-ingest even if already ingested")
    parser.add_argument("--query", type=str, help="Query implementation guides")
    parser.add_argument("--status", action="store_true", help="Check ingestion status")

    args = parser.parse_args()

    if args.query:
        await query_guides(args.query)
    elif args.status:
        await check_status()
    else:
        await ingest_guides(force=args.force)


if __name__ == "__main__":
    asyncio.run(main())
