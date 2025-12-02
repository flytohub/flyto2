"""
Query Project Knowledge
Fast AI onboarding via semantic search of project knowledge

Usage:
  python scripts/query_project_knowledge.py "How do atomic modules work?"
  python scripts/query_project_knowledge.py "What is the AI architecture?" --top-k 5
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.modules.atomic.vector import (
    VectorDBConnector,
    KnowledgeStore
)


def query_knowledge(
    query: str,
    top_k: int = 3,
    collection: str = "flyto2_project_knowledge",
    mode: str = "local"
):
    """
    Query project knowledge base

    Args:
        query: Search query
        top_k: Number of results to return
        collection: Collection name
        mode: Database mode
    """
    print(f"\nQuery: {query}")
    print("-" * 60)

    # Connect to database
    connector = VectorDBConnector(mode=mode)
    connector.connect()

    # Create knowledge store
    store = KnowledgeStore(
        connector=connector,
        collection_name=collection,
        embedding_provider="local"
    )

    # Search
    results = store.search(query, top_k=top_k)

    if not results:
        print("No results found.")
        return

    # Display results
    for i, result in enumerate(results, 1):
        print(f"\n[Result {i}] (Score: {result['score']:.3f})")
        print(f"{result['content']}")

        if result.get('metadata'):
            meta = result['metadata']
            print(f"  Source: {meta.get('source', 'unknown')}")
            print(f"  Category: {meta.get('category', 'unknown')}")

    connector.disconnect()


def interactive_mode(collection: str = "flyto2_project_knowledge"):
    """
    Interactive query mode

    Args:
        collection: Collection name
    """
    print("=" * 60)
    print("Flyto2 Project Knowledge Query (Interactive Mode)")
    print("=" * 60)
    print("Type your questions or 'quit' to exit")
    print("-" * 60)

    connector = VectorDBConnector(mode="local")
    connector.connect()

    store = KnowledgeStore(
        connector=connector,
        collection_name=collection,
        embedding_provider="local"
    )

    # Show stats
    stats = store.get_stats()
    print(f"\nKnowledge Base: {stats['total_entries']} entries")
    print(f"Provider: {stats['embedding_provider']}")
    print(f"Dimension: {stats['vector_dimension']}")

    while True:
        try:
            query = input("\n> ").strip()

            if query.lower() in ['quit', 'exit', 'q']:
                break

            if not query:
                continue

            results = store.search(query, top_k=2)

            if not results:
                print("No results found.")
                continue

            for i, result in enumerate(results, 1):
                print(f"\n[{i}] {result['content'][:200]}...")
                print(f"    Score: {result['score']:.3f} | Source: {result['metadata'].get('source', 'unknown')}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    connector.disconnect()
    print("\nGoodbye!")


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Query project knowledge base"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Search query (omit for interactive mode)"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of results to return"
    )
    parser.add_argument(
        "--collection",
        default="flyto2_project_knowledge",
        help="Collection name"
    )
    parser.add_argument(
        "--mode",
        choices=["local", "cloud"],
        default="local",
        help="Database mode"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enter interactive mode"
    )

    args = parser.parse_args()

    if args.interactive or not args.query:
        interactive_mode(collection=args.collection)
    else:
        query_knowledge(
            query=args.query,
            top_k=args.top_k,
            collection=args.collection,
            mode=args.mode
        )


if __name__ == "__main__":
    main()
