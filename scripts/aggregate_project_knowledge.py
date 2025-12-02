"""
Project Knowledge Aggregation Script
Aggregates project knowledge into vector database for fast AI onboarding

This enables future AI sessions to understand the project instantly
without reading the entire codebase.
"""
import sys
from pathlib import Path
import re
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.modules.atomic.vector import (
    VectorDBConnector,
    KnowledgeStore
)


class ProjectKnowledgeAggregator:
    """
    Aggregates project knowledge from various sources
    """

    def __init__(self, collection_name: str = "flyto2_project_knowledge"):
        """
        Initialize knowledge aggregator

        Args:
            collection_name: Vector DB collection name
        """
        self.collection_name = collection_name
        self.knowledge_entries = []

    def extract_from_claude_md(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Extract knowledge from CLAUDE.md (project instructions)

        Args:
            file_path: Path to CLAUDE.md

        Returns:
            List of knowledge entries
        """
        if not file_path.exists():
            return []

        content = file_path.read_text(encoding='utf-8')
        entries = []

        # Extract overview
        overview_match = re.search(
            r'## Project Overview\s+(.*?)(?=##|\Z)',
            content,
            re.DOTALL
        )
        if overview_match:
            entries.append({
                "content": f"Project Overview: {overview_match.group(1).strip()}",
                "metadata": {
                    "source": "CLAUDE.md",
                    "category": "overview",
                    "priority": "critical"
                }
            })

        # Extract architecture sections
        sections = [
            ("Architecture", "architecture"),
            ("Core Concepts", "concepts"),
            ("Development Commands", "commands"),
            ("API Endpoints", "api"),
            ("Module Development", "development")
        ]

        for section_name, category in sections:
            section_match = re.search(
                rf'## {section_name}\s+(.*?)(?=##|\Z)',
                content,
                re.DOTALL
            )
            if section_match:
                section_content = section_match.group(1).strip()
                # Split into paragraphs for better granularity
                paragraphs = [p.strip() for p in section_content.split('\n\n') if p.strip()]
                for para in paragraphs[:10]:  # Limit to avoid too many entries
                    if len(para) > 50:  # Skip very short paragraphs
                        entries.append({
                            "content": f"{section_name}: {para}",
                            "metadata": {
                                "source": "CLAUDE.md",
                                "category": category,
                                "section": section_name
                            }
                        })

        return entries

    def extract_from_checklist(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Extract knowledge from COMPLETE_FEATURE_CHECKLIST.md

        Args:
            file_path: Path to checklist

        Returns:
            List of knowledge entries
        """
        if not file_path.exists():
            return []

        content = file_path.read_text(encoding='utf-8')
        entries = []

        # Extract summary table (looks for first table after Quick Summary heading)
        summary_match = re.search(
            r'##\s+📈\s+[^\n]+(.*?)---',
            content,
            re.DOTALL
        )
        if summary_match:
            entries.append({
                "content": f"Project Status Summary: {summary_match.group(1).strip()}",
                "metadata": {
                    "source": "COMPLETE_FEATURE_CHECKLIST.md",
                    "category": "status",
                    "priority": "high"
                }
            })

        # Extract completed features (marked with ✅)
        completed_sections = re.findall(
            r'### ✅ ([\d.]+) (.+?)\n(.*?)(?=###|\Z)',
            content,
            re.DOTALL
        )

        for section_num, title, content_text in completed_sections[:30]:  # Limit entries
            # Clean title
            title_clean = re.sub(r'\(.*?\)', '', title).strip()

            # Extract implementation info
            impl_match = re.search(r'\*\*Implementation\*\*: `(.+?)`', content_text)
            impl = impl_match.group(1) if impl_match else "unknown"

            # Extract features
            features_match = re.search(r'\*\*Features\*\*:(.*?)(?=\*\*|$)', content_text, re.DOTALL)
            features = features_match.group(1).strip() if features_match else ""

            summary = f"Feature {section_num} - {title_clean}: Implementation at {impl}. {features[:200]}"

            entries.append({
                "content": summary,
                "metadata": {
                    "source": "COMPLETE_FEATURE_CHECKLIST.md",
                    "category": "feature",
                    "section": section_num,
                    "status": "complete",
                    "implementation": impl
                }
            })

        return entries

    def extract_module_knowledge(self) -> List[Dict[str, Any]]:
        """
        Extract knowledge from atomic modules

        Returns:
            List of knowledge entries
        """
        entries = []
        module_dirs = [
            project_root / "src/core/modules/atomic",
            project_root / "src/core/training",
            project_root / "src/core/competition"
        ]

        for module_dir in module_dirs:
            if not module_dir.exists():
                continue

            for py_file in module_dir.rglob("*.py"):
                if py_file.name.startswith("_"):
                    continue

                try:
                    content = py_file.read_text(encoding='utf-8')

                    # Extract module docstring
                    docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                    if docstring_match:
                        docstring = docstring_match.group(1).strip()

                        # Extract class names
                        classes = re.findall(r'class (\w+):', content)

                        relative_path = py_file.relative_to(project_root)

                        entries.append({
                            "content": f"Module {relative_path}: {docstring}. Classes: {', '.join(classes)}",
                            "metadata": {
                                "source": str(relative_path),
                                "category": "module",
                                "type": "implementation",
                                "classes": classes
                            }
                        })
                except Exception:
                    continue

        return entries[:50]  # Limit to avoid too many entries

    def create_core_knowledge_entries(self) -> List[Dict[str, Any]]:
        """
        Create essential knowledge entries about the project

        Returns:
            List of core knowledge entries
        """
        return [
            {
                "content": "Flyto2 is an open-source workflow automation platform with YAML-based workflows and atomic module architecture. It enables building complex automation workflows by combining single-responsibility atomic modules.",
                "metadata": {
                    "source": "core_knowledge",
                    "category": "overview",
                    "priority": "critical"
                }
            },
            {
                "content": "Atomic Module Architecture: Each module has single responsibility, is independently testable, and has zero coupling. Modules are registered via @register_module decorator and auto-discovered at runtime.",
                "metadata": {
                    "source": "core_knowledge",
                    "category": "architecture",
                    "concept": "atomic_modules"
                }
            },
            {
                "content": "Three-Tier AI System: Uses Ollama for local/free operations, OpenAI for complex tasks requiring high accuracy, and Human for critical decisions. This optimizes cost and reliability.",
                "metadata": {
                    "source": "core_knowledge",
                    "category": "ai",
                    "concept": "three_tier"
                }
            },
            {
                "content": "Self-Evolution System: AI can analyze gaps, propose new modules, generate code and tests, await human approval, and auto-integrate into the system. Continuous improvement is core to the design.",
                "metadata": {
                    "source": "core_knowledge",
                    "category": "evolution",
                    "concept": "self_improvement"
                }
            },
            {
                "content": "Vector Database Integration: Uses Qdrant for knowledge storage with semantic search. Supports local and cloud deployment. Embeddings generated via OpenAI, Ollama, or local sentence-transformers.",
                "metadata": {
                    "source": "core_knowledge",
                    "category": "features",
                    "component": "vector_db"
                }
            },
            {
                "content": "Training System: Daily Practice engine (training.practice) provides autonomous training on real websites. Speed Race system (competition.speed_race) enables performance optimization competitions.",
                "metadata": {
                    "source": "core_knowledge",
                    "category": "training",
                    "system": "practice_and_competition"
                }
            },
            {
                "content": "Module Registry: Centralized registry tracks all atomic modules with metadata (name, description, parameters, permissions). Currently 129+ registered modules across 13 categories.",
                "metadata": {
                    "source": "core_knowledge",
                    "category": "architecture",
                    "component": "registry"
                }
            },
            {
                "content": "API Optimization: Includes rate limiting with exponential backoff, proxy rotation (round-robin/random/least-used), anti-bot detection, headless browser management, and connection pooling.",
                "metadata": {
                    "source": "core_knowledge",
                    "category": "api",
                    "features": "optimization"
                }
            },
            {
                "content": "Telegram Bot Interface: Provides interactive control via /practice, /competition, /auto commands with inline keyboards and real-time progress updates.",
                "metadata": {
                    "source": "core_knowledge",
                    "category": "interface",
                    "component": "telegram_bot"
                }
            },
            {
                "content": "Testing Philosophy: Every module must be independently testable. Test coverage tracked in COMPLETE_FEATURE_CHECKLIST.md. Currently 21 test files with 100% pass rate on 27 modules.",
                "metadata": {
                    "source": "core_knowledge",
                    "category": "testing",
                    "philosophy": "comprehensive"
                }
            }
        ]

    def aggregate_all(self) -> List[Dict[str, Any]]:
        """
        Aggregate knowledge from all sources

        Returns:
            Complete list of knowledge entries
        """
        print("Aggregating project knowledge...")

        # Core knowledge
        entries = self.create_core_knowledge_entries()
        print(f"  ✓ Added {len(entries)} core knowledge entries")

        # CLAUDE.md
        claude_entries = self.extract_from_claude_md(
            project_root / "CLAUDE.md"
        )
        entries.extend(claude_entries)
        print(f"  ✓ Extracted {len(claude_entries)} entries from CLAUDE.md")

        # COMPLETE_FEATURE_CHECKLIST.md
        checklist_entries = self.extract_from_checklist(
            project_root / "COMPLETE_FEATURE_CHECKLIST.md"
        )
        entries.extend(checklist_entries)
        print(f"  ✓ Extracted {len(checklist_entries)} entries from checklist")

        # Module knowledge
        module_entries = self.extract_module_knowledge()
        entries.extend(module_entries)
        print(f"  ✓ Extracted {len(module_entries)} module entries")

        print(f"\nTotal knowledge entries: {len(entries)}")
        return entries

    def store_in_vector_db(
        self,
        entries: List[Dict[str, Any]],
        mode: str = "local",
        embedding_provider: str = "local"
    ):
        """
        Store knowledge entries in vector database

        Args:
            entries: Knowledge entries to store
            mode: Database mode (local or cloud)
            embedding_provider: Embedding provider (local, ollama, openai)
        """
        print(f"\nConnecting to vector database (mode: {mode}, embeddings: {embedding_provider})...")

        connector = VectorDBConnector(mode=mode)
        connector.connect()
        print("  ✓ Connected to vector database")

        store = KnowledgeStore(
            connector=connector,
            collection_name=self.collection_name,
            embedding_provider=embedding_provider
        )
        print(f"  ✓ Initialized knowledge store: {self.collection_name}")

        print(f"\nStoring {len(entries)} knowledge entries...")
        ids = store.store_batch(entries)
        print(f"  ✓ Stored {len(ids)} entries successfully")

        # Verify storage
        stats = store.get_stats()
        print(f"\nKnowledge Store Statistics:")
        print(f"  - Collection: {stats['collection']}")
        print(f"  - Total entries: {stats['total_entries']}")
        print(f"  - Embedding provider: {stats['embedding_provider']}")
        print(f"  - Vector dimension: {stats['vector_dimension']}")

        # Test search
        print(f"\nTesting semantic search...")
        test_queries = [
            "What is the architecture?",
            "How do atomic modules work?",
            "What AI models are supported?"
        ]

        for query in test_queries:
            results = store.search(query, top_k=1)
            if results:
                print(f"  Q: {query}")
                print(f"  A: {results[0]['content'][:100]}...")
                print(f"     (score: {results[0]['score']:.3f})")

        connector.disconnect()
        print("\n✓ Knowledge aggregation complete!")


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Aggregate project knowledge into vector database"
    )
    parser.add_argument(
        "--mode",
        choices=["local", "cloud"],
        default="local",
        help="Vector database mode"
    )
    parser.add_argument(
        "--embeddings",
        choices=["local", "ollama", "openai"],
        default="local",
        help="Embedding provider"
    )
    parser.add_argument(
        "--collection",
        default="flyto2_project_knowledge",
        help="Collection name"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Flyto2 Project Knowledge Aggregation")
    print("=" * 60)
    print(f"Mode: {args.mode}")
    print(f"Embeddings: {args.embeddings}")
    print(f"Collection: {args.collection}")
    print("=" * 60)

    aggregator = ProjectKnowledgeAggregator(collection_name=args.collection)

    # Aggregate knowledge
    entries = aggregator.aggregate_all()

    # Store in vector database
    aggregator.store_in_vector_db(
        entries,
        mode=args.mode,
        embedding_provider=args.embeddings
    )

    print("\n" + "=" * 60)
    print("Future AI sessions can now query this knowledge base")
    print("to understand the project without reading all code!")
    print("=" * 60)


if __name__ == "__main__":
    main()
