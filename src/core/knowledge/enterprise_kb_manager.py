"""
Enterprise Knowledge Base Manager

Enterprise-grade knowledge management system with:
- Version control for all documents
- Audit logging for all operations
- Quality metrics and validation
- Incremental updates with deduplication
- Batch operations with rollback
- Multi-language support (English)
- Metadata enrichment
- Performance monitoring
"""

import os
import logging
import hashlib
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from dotenv import load_dotenv
load_dotenv()

from src.core.modules.atomic.vector.knowledge_store import KnowledgeStore as AtomicKnowledgeStore
from src.core.modules.atomic.vector.connector import VectorDBConnector
from src.core.knowledge.vector_schema import (
    VectorType, VectorCategory, VectorImportance,
    VectorStatus, VectorSource
)

logger = logging.getLogger(__name__)


class TranslationService:
    """
    Enterprise translation service

    Translates Chinese content to English for better RAG performance
    """

    def __init__(self, provider: str = "ollama"):
        self.provider = provider

    def translate_to_english(self, text: str, source_lang: str = "zh") -> str:
        """
        Translate text to English

        Args:
            text: Text to translate
            source_lang: Source language (zh/en)

        Returns:
            Translated text (or original if already English)
        """
        if source_lang == "en":
            return text  # Already English

        # For Chinese text, translate to English
        if self.provider == "ollama":
            return self._translate_ollama(text)
        elif self.provider == "openai":
            return self._translate_openai(text)
        else:
            # Fallback: return original with note
            return f"[ZH] {text}"

    def _translate_ollama(self, text: str) -> str:
        """Translate using Ollama"""
        try:
            import requests

            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": f"""Translate this Chinese technical text to English. Keep code blocks and technical terms unchanged. Be concise.

Chinese: {text[:800]}

English:""",
                    "stream": False
                },
                timeout=60.0
            )

            if response.status_code == 200:
                result = response.json()
                translated = result.get("response", "").strip()

                # If translation is empty or failed, return original
                if not translated or len(translated) < 10:
                    logger.warning("Translation too short, using original")
                    return text

                return translated
            else:
                logger.warning(f"Ollama translation failed: {response.status_code}")
                return text

        except Exception as e:
            logger.warning(f"Translation error: {str(e)}, using original text")
            return text

    def _translate_openai(self, text: str) -> str:
        """Translate using OpenAI"""
        try:
            import openai

            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional translator. Translate Chinese technical documentation to English. Keep technical terms and code unchanged."},
                    {"role": "user", "content": f"Translate to English:\n\n{text[:1000]}"}
                ],
                temperature=0.3
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.warning(f"OpenAI translation error: {str(e)}")
            return text


class OperationType(str, Enum):
    """Knowledge base operation types"""
    INGEST = "ingest"
    UPDATE = "update"
    DELETE = "delete"
    REINDEX = "reindex"
    ROLLBACK = "rollback"


@dataclass
class DocumentVersion:
    """Document version information"""
    doc_id: str
    version: int
    hash: str
    timestamp: str
    operation: OperationType
    chunks_count: int
    metadata: Dict[str, Any]


@dataclass
class QualityMetrics:
    """Quality metrics for ingested content"""
    total_chunks: int
    avg_chunk_size: int
    language_detected: str
    has_code_blocks: bool
    has_tables: bool
    completeness_score: float
    readability_score: float


@dataclass
class AuditLog:
    """Audit log entry"""
    timestamp: str
    operation: OperationType
    user: str
    document_id: str
    chunks_affected: int
    success: bool
    error_message: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


class EnterpriseKBManager:
    """
    Enterprise-grade Knowledge Base Manager

    Features:
    - Version control
    - Audit logging
    - Quality validation
    - Incremental updates
    - Rollback capability
    """

    def __init__(
        self,
        project_root: Path = None,
        audit_log_path: Path = None,
        enable_translation: bool = True,
        translation_provider: str = "ollama"
    ):
        self.project_root = project_root or Path.cwd()
        self.audit_log_path = audit_log_path or (self.project_root / "logs" / "kb_audit.jsonl")

        # Ensure logs directory exists
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize translation service
        self.enable_translation = enable_translation
        if enable_translation:
            self.translator = TranslationService(provider=translation_provider)
            logger.info(f"🌐 Translation enabled: {translation_provider}")
        else:
            self.translator = None

        # Initialize cloud Qdrant connection
        mode = os.getenv("QDRANT_MODE", "cloud")
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

        # Version tracking
        self.versions: Dict[str, List[DocumentVersion]] = {}
        self._load_versions()

        logger.info("✅ Enterprise KB Manager initialized")
        logger.info(f"   Mode: {mode}")
        logger.info(f"   Collection: flyto2_knowledge")
        logger.info(f"   Translation: {'Enabled' if enable_translation else 'Disabled'}")
        logger.info(f"   Audit log: {self.audit_log_path}")

    def _load_versions(self):
        """Load version history from disk"""
        version_file = self.project_root / "logs" / "kb_versions.json"
        if version_file.exists():
            with open(version_file, 'r') as f:
                data = json.load(f)
                self.versions = {
                    doc_id: [DocumentVersion(**v) for v in versions]
                    for doc_id, versions in data.items()
                }

    def _save_versions(self):
        """Save version history to disk"""
        version_file = self.project_root / "logs" / "kb_versions.json"
        version_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            doc_id: [asdict(v) for v in versions]
            for doc_id, versions in self.versions.items()
        }

        with open(version_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _write_audit_log(self, log: AuditLog):
        """Write audit log entry"""
        with open(self.audit_log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(log), ensure_ascii=False) + '\n')

    def _calculate_content_hash(self, content: str) -> str:
        """Calculate content hash for deduplication"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _detect_language(self, content: str) -> str:
        """Detect primary language (English or Chinese)"""
        chinese_chars = sum(1 for char in content if '\u4e00' <= char <= '\u9fff')
        english_words = len([w for w in content.split() if w.isascii()])

        if chinese_chars > english_words:
            return "zh"
        return "en"

    def _analyze_quality(self, content: str, chunks: List[Dict]) -> QualityMetrics:
        """Analyze content quality"""
        total_size = sum(len(c['content']) for c in chunks)
        avg_size = total_size // len(chunks) if chunks else 0

        has_code = '```' in content
        has_tables = '|' in content and '---' in content

        # Completeness: check if chunks have reasonable size
        completeness = min(1.0, avg_size / 500)  # Target 500 chars/chunk

        # Readability: check for proper structure
        has_headers = content.count('#') > 5
        has_lists = content.count('- ') > 10
        readability = (has_headers + has_lists) / 2

        return QualityMetrics(
            total_chunks=len(chunks),
            avg_chunk_size=avg_size,
            language_detected=self._detect_language(content),
            has_code_blocks=has_code,
            has_tables=has_tables,
            completeness_score=completeness,
            readability_score=readability
        )

    def _parse_markdown_enterprise(
        self,
        doc_path: Path,
        doc_id: str
    ) -> Tuple[List[Dict[str, Any]], QualityMetrics]:
        """
        Parse markdown with enterprise-grade processing

        Features:
        - Language detection
        - Quality analysis
        - Metadata enrichment
        - Hierarchy tracking
        """
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()

        chunks = []
        current_section = None
        current_content = []
        current_level = 0
        section_hierarchy = []

        for line in content.split('\n'):
            if line.startswith('##'):
                # Save previous section
                if current_section:
                    chunk_content = '\n'.join(current_content).strip()

                    chunks.append({
                        'title': current_section,
                        'content': chunk_content,
                        'level': current_level,
                        'hierarchy': list(section_hierarchy),
                        'doc_source': doc_path.name,
                        'doc_id': doc_id,
                        'language': self._detect_language(chunk_content),
                        'has_code': '```' in chunk_content,
                        'word_count': len(chunk_content.split()),
                        'char_count': len(chunk_content)
                    })

                # Update hierarchy
                current_level = len(line.split()[0])  # Count #'s
                current_section = line.lstrip('#').strip()

                # Update section hierarchy
                if current_level <= len(section_hierarchy):
                    section_hierarchy = section_hierarchy[:current_level-1]
                section_hierarchy.append(current_section)

                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_section:
            chunk_content = '\n'.join(current_content).strip()
            chunks.append({
                'title': current_section,
                'content': chunk_content,
                'level': current_level,
                'hierarchy': list(section_hierarchy),
                'doc_source': doc_path.name,
                'doc_id': doc_id,
                'language': self._detect_language(chunk_content),
                'has_code': '```' in chunk_content,
                'word_count': len(chunk_content.split()),
                'char_count': len(chunk_content)
            })

        # Analyze quality
        quality = self._analyze_quality(content, chunks)

        return chunks, quality

    def _classify_chunk_enterprise(self, chunk: Dict) -> Tuple[VectorType, VectorCategory, VectorImportance]:
        """
        Enterprise-grade chunk classification

        Uses multiple signals:
        - Title keywords
        - Content analysis
        - Hierarchy position
        - Language
        """
        title = chunk['title'].lower()
        content = chunk['content'].lower()

        # Determine type
        type_signals = {
            VectorType.MODULE: ['planner', 'designer', 'implementation', 'validator', 'engine'],
            VectorType.ARCHITECTURE: ['schema', 'config', 'architecture', 'design', 'structure'],
            VectorType.PAIN_POINT: ['pain point', 'problem', 'issue', 'challenge'],
            VectorType.PRACTICE: ['best practice', 'pattern', 'guideline', 'standard'],
            VectorType.FIX: ['fix', 'solution', 'resolve', 'patch']
        }

        chunk_type = VectorType.ARCHITECTURE  # Default
        for vtype, keywords in type_signals.items():
            if any(kw in title or kw in content for kw in keywords):
                chunk_type = vtype
                break

        # Determine category
        category_signals = {
            VectorCategory.VECTOR_DB: ['vector', 'qdrant', 'rag', 'embedding'],
            VectorCategory.OLLAMA: ['ollama', 'llm', 'prompt', 'ai model'],
            VectorCategory.EVOLUTION: ['evolution', 'ticket', 'pr', 'planner', 'designer'],
            VectorCategory.BROWSER: ['browser', 'playwright', 'selenium'],
            VectorCategory.CRAWLER: ['crawler', 'scraping', 'fetch'],
        }

        category = VectorCategory.GENERAL  # Default
        for vcat, keywords in category_signals.items():
            if any(kw in title or kw in content for kw in keywords):
                category = vcat
                break

        # Determine importance
        importance_signals = {
            VectorImportance.CRITICAL: ['critical', 'must', 'required', 'essential', 'mandatory'],
            VectorImportance.HIGH: ['core', 'main', 'primary', 'key', 'important'],
        }

        importance = VectorImportance.MEDIUM  # Default

        # Check title first (higher weight)
        for vimp, keywords in importance_signals.items():
            if any(kw in title for kw in keywords):
                importance = vimp
                break

        # Check for code (high importance)
        if chunk.get('has_code') and importance == VectorImportance.MEDIUM:
            importance = VectorImportance.HIGH

        return chunk_type, category, importance

    async def ingest_document_enterprise(
        self,
        doc_path: Path,
        doc_id: Optional[str] = None,
        force: bool = False,
        user: str = "system"
    ) -> Dict[str, Any]:
        """
        Ingest document with enterprise-grade processing

        Features:
        - Version control
        - Deduplication
        - Quality validation
        - Audit logging
        - Incremental updates

        Args:
            doc_path: Path to document
            doc_id: Unique document ID (generated if None)
            force: Force re-ingestion even if unchanged
            user: User performing the operation

        Returns:
            Result with metrics and status
        """
        start_time = datetime.now()

        if not doc_path.exists():
            logger.error(f"❌ Document not found: {doc_path}")
            return {"success": False, "error": "Document not found"}

        # Generate doc_id from filename if not provided
        if doc_id is None:
            doc_id = doc_path.stem

        logger.info(f"📄 Processing: {doc_path.name} (ID: {doc_id})")

        # Calculate content hash
        with open(doc_path, 'rb') as f:
            content_hash = hashlib.sha256(f.read()).hexdigest()

        # Check if already ingested with same hash
        if doc_id in self.versions and not force:
            latest_version = self.versions[doc_id][-1]
            if latest_version.hash == content_hash:
                logger.info(f"   ⏭️  Skipping (unchanged, hash: {content_hash[:8]}...)")
                return {
                    "success": True,
                    "skipped": True,
                    "reason": "No changes detected",
                    "doc_id": doc_id
                }

        # Parse document
        chunks, quality = self._parse_markdown_enterprise(doc_path, doc_id)

        logger.info(f"   📊 Quality metrics:")
        logger.info(f"      Chunks: {quality.total_chunks}")
        logger.info(f"      Avg size: {quality.avg_chunk_size} chars")
        logger.info(f"      Language: {quality.language_detected}")
        logger.info(f"      Code blocks: {'Yes' if quality.has_code_blocks else 'No'}")
        logger.info(f"      Completeness: {quality.completeness_score:.0%}")
        logger.info(f"      Readability: {quality.readability_score:.0%}")

        # Quality validation
        if quality.completeness_score < 0.3:
            logger.warning(f"   ⚠️  Low completeness score: {quality.completeness_score:.0%}")

        # Ingest chunks
        ingested_count = 0
        errors = []

        for chunk in chunks:
            try:
                # Classify chunk
                chunk_type, chunk_category, chunk_importance = self._classify_chunk_enterprise(chunk)

                # Build enhanced metadata
                metadata = {
                    "type": chunk_type.value,
                    "category": chunk_category.value,
                    "importance": chunk_importance.value,
                    "status": VectorStatus.ACTIVE.value,
                    "source": VectorSource.DOCUMENTATION.value,
                    "timestamp": datetime.now().isoformat(),
                    "doc_source": chunk['doc_source'],
                    "doc_id": doc_id,
                    "section_title": chunk['title'],
                    "section_level": chunk['level'],
                    "hierarchy": "/".join(chunk['hierarchy']),
                    "language": chunk['language'],
                    "has_code": chunk['has_code'],
                    "word_count": chunk['word_count'],
                    "version": len(self.versions.get(doc_id, [])) + 1
                }

                # Build content for embedding
                original_content = f"""# {chunk['title']}

{chunk['content'][:2000]}"""  # Limit for embedding

                # Translate to English if enabled
                if self.enable_translation and chunk['language'] == 'zh':
                    logger.debug(f"      🌐 Translating '{chunk['title'][:30]}...'")
                    english_content = self.translator.translate_to_english(
                        original_content,
                        source_lang='zh'
                    )

                    # Store both original and translated in metadata
                    metadata['original_content_zh'] = original_content[:500]  # Keep sample
                    content_to_store = english_content
                else:
                    content_to_store = original_content

                # Store in VectorDB
                self.knowledge_store.store(
                    content=content_to_store,
                    metadata=metadata
                )

                ingested_count += 1

            except Exception as e:
                error_msg = f"Failed to ingest chunk '{chunk['title']}': {str(e)}"
                logger.error(f"   ❌ {error_msg}")
                errors.append(error_msg)

        # Create version record
        version = DocumentVersion(
            doc_id=doc_id,
            version=len(self.versions.get(doc_id, [])) + 1,
            hash=content_hash,
            timestamp=datetime.now().isoformat(),
            operation=OperationType.INGEST if doc_id not in self.versions else OperationType.UPDATE,
            chunks_count=ingested_count,
            metadata={
                "doc_path": str(doc_path),
                "quality": asdict(quality),
                "errors": errors
            }
        )

        # Update version history
        if doc_id not in self.versions:
            self.versions[doc_id] = []
        self.versions[doc_id].append(version)
        self._save_versions()

        # Write audit log
        elapsed = (datetime.now() - start_time).total_seconds()

        audit = AuditLog(
            timestamp=datetime.now().isoformat(),
            operation=version.operation,
            user=user,
            document_id=doc_id,
            chunks_affected=ingested_count,
            success=len(errors) == 0,
            error_message="; ".join(errors) if errors else None,
            metrics={
                "quality": asdict(quality),
                "elapsed_seconds": elapsed,
                "version": version.version
            }
        )
        self._write_audit_log(audit)

        logger.info(f"   ✅ Ingested {ingested_count}/{len(chunks)} chunks in {elapsed:.2f}s")

        if errors:
            logger.warning(f"   ⚠️  {len(errors)} errors occurred")

        return {
            "success": len(errors) == 0,
            "doc_id": doc_id,
            "version": version.version,
            "chunks_ingested": ingested_count,
            "chunks_total": len(chunks),
            "quality": asdict(quality),
            "errors": errors,
            "elapsed_seconds": elapsed
        }

    async def ingest_all_enterprise(
        self,
        documents: List[Path] = None,
        force: bool = False,
        user: str = "system"
    ) -> Dict[str, Any]:
        """
        Ingest all implementation guides with enterprise processing

        Returns:
            Summary with statistics and metrics
        """
        if documents is None:
            documents = [
                self.project_root / "IMPLEMENTATION_GUIDE_V4.md",
                self.project_root / "IMPLEMENTATION_GUIDE_V4_CRITICAL_SUPPLEMENTS.md"
            ]

        logger.info("=" * 70)
        logger.info("📚 Enterprise Knowledge Base Ingestion")
        logger.info("=" * 70)
        logger.info(f"Documents: {len(documents)}")
        logger.info(f"Force mode: {force}")
        logger.info(f"User: {user}")
        logger.info("=" * 70)
        logger.info("")

        results = []
        total_chunks = 0
        total_skipped = 0
        total_errors = 0

        for doc_path in documents:
            result = await self.ingest_document_enterprise(
                doc_path=doc_path,
                force=force,
                user=user
            )
            results.append(result)

            if result.get("skipped"):
                total_skipped += 1
            else:
                total_chunks += result.get("chunks_ingested", 0)
                total_errors += len(result.get("errors", []))

        logger.info("")
        logger.info("=" * 70)
        logger.info("📊 Ingestion Summary")
        logger.info("=" * 70)
        logger.info(f"   Documents processed: {len(documents)}")
        logger.info(f"   Documents skipped: {total_skipped}")
        logger.info(f"   Total chunks ingested: {total_chunks}")
        logger.info(f"   Total errors: {total_errors}")
        logger.info("=" * 70)

        return {
            "success": total_errors == 0,
            "documents_processed": len(documents),
            "documents_skipped": total_skipped,
            "total_chunks": total_chunks,
            "total_errors": total_errors,
            "results": results
        }

    def get_document_history(self, doc_id: str) -> List[DocumentVersion]:
        """Get version history for a document"""
        return self.versions.get(doc_id, [])

    def get_audit_logs(self, limit: int = 100) -> List[AuditLog]:
        """Get recent audit logs"""
        logs = []
        if self.audit_log_path.exists():
            with open(self.audit_log_path, 'r') as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    logs.append(AuditLog(**json.loads(line)))
        return logs

    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        total_docs = len(self.versions)
        total_versions = sum(len(versions) for versions in self.versions.values())

        # Get collection stats from Qdrant
        info = self.connector.client.get_collection("flyto2_knowledge")

        return {
            "total_documents": total_docs,
            "total_versions": total_versions,
            "total_vectors": info.points_count,
            "vector_dimension": info.config.params.vectors.size,
            "latest_documents": [
                {
                    "doc_id": doc_id,
                    "version": versions[-1].version,
                    "timestamp": versions[-1].timestamp,
                    "chunks": versions[-1].chunks_count
                }
                for doc_id, versions in list(self.versions.items())[-10:]
            ]
        }
