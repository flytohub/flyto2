"""
Document Ingestion System - Ingest implementation guides into VectorDB

Converts IMPLEMENTATION_GUIDE_V4.md and supplements into searchable vectors

Enterprise-grade configuration management with .env support
"""

import logging
import hashlib
import os
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from src.core.modules.atomic.vector.knowledge_store import KnowledgeStore as AtomicKnowledgeStore
from src.core.modules.atomic.vector.connector import VectorDBConnector
from src.core.knowledge.vector_schema import (
    VectorType, VectorCategory, VectorImportance,
    VectorStatus, VectorSource
)

logger = logging.getLogger(__name__)


class DocumentIngestionEngine:
    """Ingest implementation guides into vector database"""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()

        # Initialize knowledge store with cloud Qdrant
        mode = os.getenv("QDRANT_MODE", "cloud")  # Default to cloud
        self.connector = VectorDBConnector(
            mode=mode,
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        self.connector.connect()

        embedding_provider = os.getenv("EMBEDDING_PROVIDER", "local")
        self.knowledge_store = AtomicKnowledgeStore(
            connector=self.connector,
            collection_name="flyto2_knowledge",
            embedding_provider=embedding_provider
        )

        # Documents to ingest
        self.implementation_docs = [
            self.project_root / "IMPLEMENTATION_GUIDE_V4.md",
            self.project_root / "IMPLEMENTATION_GUIDE_V4_CRITICAL_SUPPLEMENTS.md"
        ]

    async def ingest_all_guides(self, force: bool = False):
        """
        Ingest all implementation guides into VectorDB

        Args:
            force: If True, re-ingest even if already ingested
        """
        logger.info("Starting implementation guide ingestion")

        total_chunks = 0

        for doc_path in self.implementation_docs:
            if not doc_path.exists():
                logger.warning(f"Document not found: {doc_path}")
                continue

            logger.info(f"Processing: {doc_path.name}")

            # Parse document into chunks
            chunks = self._parse_markdown_document(doc_path)

            logger.info(f"  Found {len(chunks)} sections")

            # Ingest each chunk
            for chunk in chunks:
                self._ingest_chunk(chunk, doc_path)
                total_chunks += 1

        logger.info(f"✅ Ingestion complete: {total_chunks} chunks added")

    def _parse_markdown_document(self, doc_path: Path) -> List[Dict[str, Any]]:
        """Parse markdown document into logical chunks"""
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()

        chunks = []
        current_section = None
        current_content = []
        current_level = 0

        for line in content.split('\n'):
            # Detect headers
            if line.startswith('##'):
                # Save previous section
                if current_section:
                    chunks.append({
                        'title': current_section,
                        'content': '\n'.join(current_content).strip(),
                        'level': current_level,
                        'doc_source': doc_path.name
                    })

                # Start new section
                current_level = len(line.split()[0])  # Count #'s
                current_section = line.lstrip('#').strip()
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_section:
            chunks.append({
                'title': current_section,
                'content': '\n'.join(current_content).strip(),
                'level': current_level,
                'doc_source': doc_path.name
            })

        return chunks

    def _ingest_chunk(self, chunk: Dict, doc_path: Path):
        """Ingest a single document chunk into VectorDB"""

        # Determine chunk type and category
        chunk_type, chunk_category = self._classify_chunk(chunk)

        # Build content for embedding
        content = f"""# {chunk['title']}

{chunk['content'][:2000]}"""  # Limit content size

        # Create metadata
        metadata = {
            "type": chunk_type.value,
            "category": chunk_category.value,
            "importance": self._determine_importance(chunk),
            "status": VectorStatus.ACTIVE.value,
            "source": VectorSource.DOCUMENTATION.value,
            "timestamp": datetime.now().isoformat(),
            "doc_source": chunk['doc_source'],
            "section_title": chunk['title'],
            "section_level": chunk['level']
        }

        # Store in VectorDB (sync call)
        self.knowledge_store.store(
            content=content,
            metadata=metadata
        )

    def _classify_chunk(self, chunk: Dict) -> tuple:
        """Classify chunk into type and category"""
        title = chunk['title'].lower()
        content = chunk['content'].lower()

        # Determine type
        if 'planner' in title or 'designer' in title or 'implementation' in title:
            chunk_type = VectorType.MODULE
        elif 'validator' in title or 'pr engine' in title or 'webhook' in title:
            chunk_type = VectorType.MODULE
        elif 'schema' in title or 'config' in title:
            chunk_type = VectorType.ARCHITECTURE
        elif 'pain point' in title or 'problem' in title:
            chunk_type = VectorType.PAIN_POINT
        elif 'best practice' in title or 'pattern' in title:
            chunk_type = VectorType.PRACTICE
        else:
            chunk_type = VectorType.ARCHITECTURE

        # Determine category
        if 'telegram' in title or 'tg bot' in title:
            category = VectorCategory.GENERAL
        elif 'vector' in title or 'qdrant' in title or 'rag' in title:
            category = VectorCategory.VECTOR_DB
        elif 'ollama' in title or 'llm' in title or 'prompt' in title:
            category = VectorCategory.OLLAMA
        elif 'evolution' in title or 'ticket' in title or 'pr' in title:
            category = VectorCategory.EVOLUTION
        elif 'browser' in content:
            category = VectorCategory.BROWSER
        elif 'crawler' in content:
            category = VectorCategory.CRAWLER
        else:
            category = VectorCategory.GENERAL

        return chunk_type, category

    def _determine_importance(self, chunk: Dict) -> str:
        """Determine chunk importance based on content"""
        title = chunk['title'].lower()

        # Critical sections
        if any(word in title for word in ['critical', 'must', 'required', 'essential']):
            return VectorImportance.CRITICAL.value

        # High importance sections
        if any(word in title for word in ['core', 'main', 'primary', 'key']):
            return VectorImportance.HIGH.value

        # Code implementations are high importance
        if '```python' in chunk['content'] or 'class ' in chunk['content']:
            return VectorImportance.HIGH.value

        # Default to medium
        return VectorImportance.MEDIUM.value


class SelfAwarenessSystem:
    """
    Self-Awareness System - Query architecture knowledge on startup
    """

    def __init__(self):
        # Use cloud Qdrant
        mode = os.getenv("QDRANT_MODE", "cloud")  # Default to cloud
        self.connector = VectorDBConnector(
            mode=mode,
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        self.connector.connect()

        embedding_provider = os.getenv("EMBEDDING_PROVIDER", "local")
        self.knowledge_store = AtomicKnowledgeStore(
            connector=self.connector,
            collection_name="flyto2_knowledge",
            embedding_provider=embedding_provider
        )
        self.is_initialized = False

    async def initialize(self):
        """Initialize self-awareness on system startup"""
        logger.info("🧠 Initializing Self-Awareness System...")

        # Check if implementation guides are in VectorDB
        # (simplified check - just mark as initialized)
        self.is_initialized = True
        logger.info("✅ Self-Awareness System ready")

    async def ask_self(self, question: str) -> Dict[str, Any]:
        """
        Ask the system about its own architecture

        Args:
            question: Question about implementation

        Returns:
            Answer with sources
        """
        if not self.is_initialized:
            await self.initialize()

        logger.info(f"🤔 Self-query: {question}")

        # Search knowledge store
        results = self.knowledge_store.search(
            query=question,
            filters={"source": VectorSource.DOCUMENTATION.value},
            top_k=5
        )

        if not results:
            return {
                "success": False,
                "error": "No relevant architecture knowledge found"
            }

        # Format answer from top results
        answer_parts = []
        sources = []

        for i, result in enumerate(results[:3], 1):
            # Result is a dict with keys: id, content, metadata, timestamp, score
            content = result.get("content", "")
            metadata = result.get("metadata", {})
            section_title = metadata.get("section_title", "Unknown")
            score = result.get("score", 0.0)

            answer_parts.append(f"""
**{i}. {section_title}** (relevance: {score:.0%})

{content[:500]}...
""")
            sources.append(section_title)

        answer = {
            "success": True,
            "question": question,
            "answer": "\n".join(answer_parts),
            "sources": sources,
            "results": results  # Include raw results
        }

        logger.info(f"✓ Found answer from {len(sources)} sources")

        return answer


# Global singleton
_self_awareness = None

def get_self_awareness() -> SelfAwarenessSystem:
    """Get global self-awareness system"""
    global _self_awareness
    if _self_awareness is None:
        _self_awareness = SelfAwarenessSystem()
    return _self_awareness


async def init_self_awareness_on_startup():
    """Called on system startup to initialize self-awareness"""
    system = get_self_awareness()
    await system.initialize()
