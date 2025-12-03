"""
KnowledgeExtractor - Long-term Knowledge Extraction and Retrieval System
Extracts knowledge from successful tasks, PR reviews, and failure cases, stores to Qdrant vector database
"""
import os
import yaml
import uuid
import requests
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from pathlib import Path
import logging

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    print("⚠️ Qdrant not installed. Knowledge features will be limited.")

try:
    from src.core.retrieval.enhanced_retrieval import EnhancedRetrieval
    ENHANCED_RETRIEVAL_AVAILABLE = True
except ImportError:
    ENHANCED_RETRIEVAL_AVAILABLE = False

logger = logging.getLogger(__name__)


class KnowledgeType:
    """Knowledge type constants"""
    SPEC = "spec"  # Module specifications
    MODULE = "module"  # Atomic modules
    LESSON = "lesson"  # Lessons learned
    ERROR_LOG = "error_log"  # Error records
    TASK_EXAMPLE = "task_example"  # Successful task examples (Phase 3.3)


class ModuleStatus:
    """Module status constants for versioning"""
    DRAFT = "draft"  # Under development, not ready for use
    ACTIVE = "active"  # Current production version
    DEPRECATED = "deprecated"  # Old version, no longer recommended


class KnowledgeExtractor:
    """
    Knowledge Extraction and Retrieval System

    Features:
    1. Extract module combination experience from successful tasks
    2. Extract code quality lessons from PR reviews
    3. Extract error patterns from failure cases
    4. Provide enhanced retrieval (Query Rewrite + MMR + Hybrid Search)
    5. Manage long-term knowledge base (Qdrant)
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize KnowledgeExtractor

        Args:
            config_path: Path to config file, defaults to config/memory_config.yaml
        """
        if not QDRANT_AVAILABLE:
            raise ImportError("Qdrant not installed. Install with: pip install qdrant-client")

        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent.parent / "config" / "memory_config.yaml"

        self.config = self._load_config(config_path)

        # Qdrant setup
        self.collection_name = self.config['knowledge']['vector_db']['collection_name']
        self.qdrant_client = None
        self._init_qdrant()

        # Embedding setup
        self.embed_model = self.config['knowledge']['vector_db']['vector']['model']
        self.embed_endpoint = self.config['embedding']['endpoint']
        self.embed_timeout = self.config['embedding']['timeout']

        # Enhanced retrieval
        self.enhanced_retrieval = None
        if ENHANCED_RETRIEVAL_AVAILABLE:
            try:
                # Use vector_config.yaml (shared config)
                vector_config_path = Path(__file__).parent.parent.parent.parent / "config" / "vector_config.yaml"
                if vector_config_path.exists():
                    self.enhanced_retrieval = EnhancedRetrieval(vector_config_path)
            except Exception as e:
                logger.warning(f"Enhanced retrieval not available: {e}")

        logger.info(f"KnowledgeExtractor initialized with collection: {self.collection_name}")

    def _load_config(self, config_path: Path) -> Dict:
        """Load configuration file (supports environment variable substitution)"""
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # Replace environment variables
            import re
            def replace_env(match):
                var_name = match.group(1)
                default = match.group(2) if match.group(2) else None
                value = os.getenv(var_name, default)
                if value is None:
                    logger.warning(f"Environment variable {var_name} not set, using default: {default}")
                    return default or ""
                return value

            content = re.sub(r'\$\{([A-Z_]+)(?::([^\}]+))?\}', replace_env, content)
            return yaml.safe_load(content)

    def _init_qdrant(self):
        """Initialize Qdrant vector database"""
        try:
            qdrant_url = self.config['knowledge']['vector_db']['url']
            qdrant_api_key = self.config['knowledge']['vector_db']['api_key']

            # Connect to Qdrant
            if qdrant_api_key:
                self.qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
            else:
                self.qdrant_client = QdrantClient(url=qdrant_url)

            # Create collection (if not exists)
            collections = self.qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                vector_dim = self.config['knowledge']['vector_db']['vector']['dimension']

                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=vector_dim,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")

                # Create payload indexes
                self._create_payload_indexes()

        except Exception as e:
            logger.error(f"Qdrant initialization failed: {e}")
            raise

    def _create_payload_indexes(self):
        """Create payload indexes for efficient filtering"""
        try:
            from qdrant_client.models import PayloadSchemaType

            indexes = [
                ("metadata.knowledge_type", "Knowledge type"),
                ("metadata.category", "Category"),
                ("metadata.module_id", "Module ID"),
                ("metadata.user_id", "User ID"),
                ("metadata.timestamp", "Timestamp"),
                ("metadata.version", "Module version"),
                ("metadata.status", "Module status (draft/active/deprecated)")
            ]

            for field_name, description in indexes:
                try:
                    self.qdrant_client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name=field_name,
                        field_schema=PayloadSchemaType.KEYWORD
                    )
                    logger.info(f"Created index: {field_name} ({description})")
                except Exception as e:
                    logger.warning(f"Index {field_name} may already exist: {e}")

        except Exception as e:
            logger.error(f"Failed to create payload indexes: {e}")

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding vector for text"""
        try:
            response = requests.post(
                self.embed_endpoint,
                json={"model": self.embed_model, "prompt": text},
                timeout=self.embed_timeout
            )

            if response.status_code == 200:
                return response.json()['embedding']
            else:
                raise Exception(f"Embedding API error: {response.status_code}")

        except Exception as e:
            logger.error(f"Failed to get embedding: {e}")
            raise

    # ============================================================
    # Knowledge Storage
    # ============================================================

    def store_spec(self, module_name: str, category: str, spec_content: str,
                   metadata: Optional[Dict] = None) -> str:
        """
        Store module specification

        Args:
            module_name: Module name
            category: Category (atomic | third_party | composite)
            spec_content: Specification content
            metadata: Additional metadata

        Returns:
            point_id: Qdrant point ID
        """
        knowledge_id = f"spec_{uuid.uuid4().hex[:16]}"

        payload_metadata = {
            "knowledge_type": KnowledgeType.SPEC,
            "module_name": module_name,
            "category": category,
            "timestamp": datetime.now().isoformat()
        }

        if metadata:
            payload_metadata.update(metadata)

        return self._store_knowledge(
            knowledge_id=knowledge_id,
            content=spec_content,
            metadata=payload_metadata
        )

    def store_module(self, module_id: str, category: str, subcategory: str,
                     description: str, parameters: Dict, returns: Dict,
                     code_example: Optional[str] = None,
                     version: str = "1.0.0",
                     status: str = ModuleStatus.ACTIVE,
                     metadata: Optional[Dict] = None) -> str:
        """
        Store atomic module information with versioning support

        Args:
            module_id: Module ID (e.g., "browser.click")
            category: Category (atomic | third_party | composite)
            subcategory: Subcategory (browser | array | string, etc.)
            description: Module description
            parameters: Parameter descriptions
            returns: Return value descriptions
            code_example: Code example
            version: Version string (e.g., "1.0.0", "2.1.3")
            status: Module status (draft | active | deprecated)
            metadata: Additional metadata

        Returns:
            point_id: Qdrant point ID
        """
        # Auto-deprecate old versions when storing new ACTIVE version
        if status == ModuleStatus.ACTIVE:
            self._deprecate_old_versions(module_id, exclude_version=version)

        knowledge_id = f"module_{uuid.uuid4().hex[:16]}"

        # Combine content (for embedding)
        import json
        content_parts = [
            f"Module: {module_id}",
            f"Version: {version}",
            f"Category: {category}/{subcategory}",
            f"Description: {description}",
            f"Parameters: {json.dumps(parameters, ensure_ascii=False)}",
            f"Returns: {json.dumps(returns, ensure_ascii=False)}"
        ]

        if code_example:
            content_parts.append(f"Example:\n{code_example}")

        content = "\n".join(content_parts)

        payload_metadata = {
            "knowledge_type": KnowledgeType.MODULE,
            "module_id": module_id,
            "version": version,
            "status": status,
            "category": category,
            "subcategory": subcategory,
            "parameters": parameters,
            "returns": returns,
            "timestamp": datetime.now().isoformat()
        }

        if code_example:
            payload_metadata["code_example"] = code_example

        if metadata:
            payload_metadata.update(metadata)

        return self._store_knowledge(
            knowledge_id=knowledge_id,
            content=content,
            metadata=payload_metadata
        )

    def store_lesson(self, task_description: str, modules_used: List[str],
                     outcome: str, quality_score: float,
                     pr_url: Optional[str] = None,
                     metadata: Optional[Dict] = None) -> str:
        """
        Store successful lesson learned

        Args:
            task_description: Task description
            modules_used: List of modules used
            outcome: Outcome description
            quality_score: Quality score (0-1)
            pr_url: PR link
            metadata: Additional metadata

        Returns:
            point_id: Qdrant point ID
        """
        knowledge_id = f"lesson_{uuid.uuid4().hex[:16]}"

        content = f"""Task: {task_description}

Modules used: {', '.join(modules_used)}

Outcome: {outcome}

Quality score: {quality_score}
"""

        if pr_url:
            content += f"\nPR: {pr_url}"

        payload_metadata = {
            "knowledge_type": KnowledgeType.LESSON,
            "task_description": task_description,
            "modules_used": modules_used,
            "quality_score": quality_score,
            "timestamp": datetime.now().isoformat()
        }

        if pr_url:
            payload_metadata["pr_url"] = pr_url

        if metadata:
            payload_metadata.update(metadata)

        return self._store_knowledge(
            knowledge_id=knowledge_id,
            content=content,
            metadata=payload_metadata
        )

    def store_error_log(self, error_type: str, failed_modules: List[str],
                        root_cause: str, task_context: str,
                        metadata: Optional[Dict] = None) -> str:
        """
        Store failure case

        Args:
            error_type: Error type
            failed_modules: Failed modules
            root_cause: Root cause
            task_context: Task context
            metadata: Additional metadata

        Returns:
            point_id: Qdrant point ID
        """
        knowledge_id = f"error_{uuid.uuid4().hex[:16]}"

        content = f"""Error type: {error_type}

Failed modules: {', '.join(failed_modules)}

Root cause: {root_cause}

Task context: {task_context}
"""

        payload_metadata = {
            "knowledge_type": KnowledgeType.ERROR_LOG,
            "error_type": error_type,
            "failed_modules": failed_modules,
            "timestamp": datetime.now().isoformat()
        }

        if metadata:
            payload_metadata.update(metadata)

        return self._store_knowledge(
            knowledge_id=knowledge_id,
            content=content,
            metadata=payload_metadata
        )

    def store_successful_task(
        self,
        task_description: str,
        plan: Dict,
        execution_result: Dict,
        job_id: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Store successful task execution as reusable example (Phase 3.3)

        Args:
            task_description: Original user task
            plan: Execution plan that worked
            execution_result: What happened
            job_id: Job ID for reference
            metadata: Additional metadata

        Returns:
            knowledge_id: ID of stored knowledge

        Example:
            >>> knowledge.store_successful_task(
            ...     task_description="Check Google Form for empty columns",
            ...     plan={"steps": [...]},
            ...     execution_result={"status": "success", "empty_columns": 3},
            ...     job_id="job_abc123"
            ... )
        """
        import json
        knowledge_id = f"task_example_{uuid.uuid4().hex[:16]}"

        # Build content for embedding
        content = f"""Task: {task_description}

Solution approach:
{json.dumps(plan, indent=2, ensure_ascii=False)}

Result: {execution_result.get('status', 'unknown')}
Success rate: {execution_result.get('success_rate', 'N/A')}
"""

        # Build metadata
        payload_metadata = {
            'knowledge_type': KnowledgeType.TASK_EXAMPLE,
            'task_description': task_description,
            'plan': plan,
            'result': execution_result,
            'job_id': job_id,
            'timestamp': datetime.now().isoformat()
        }

        if metadata:
            payload_metadata.update(metadata)

        logger.info(f"Storing successful task example: {knowledge_id}")
        return self._store_knowledge(
            knowledge_id=knowledge_id,
            content=content,
            metadata=payload_metadata
        )

    def _store_knowledge(self, knowledge_id: str, content: str, metadata: Dict) -> str:
        """
        Store knowledge to Qdrant

        Args:
            knowledge_id: Knowledge ID
            content: Content (for embedding)
            metadata: Metadata

        Returns:
            point_id: Qdrant point ID
        """
        try:
            # Generate embedding
            embedding = self._get_embedding(content)

            # Generate point ID
            point_id = abs(hash(knowledge_id)) % (10 ** 9)

            # Store to Qdrant
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload={
                            "knowledge_id": knowledge_id,
                            "content": content,
                            "metadata": metadata
                        }
                    )
                ]
            )

            logger.info(f"Stored knowledge: {knowledge_id} (type: {metadata.get('knowledge_type')})")
            return knowledge_id

        except Exception as e:
            logger.error(f"Failed to store knowledge: {e}")
            raise

    # ============================================================
    # Knowledge Retrieval
    # ============================================================

    def search_modules(self, query: str, category: Optional[str] = None,
                       subcategory: Optional[str] = None,
                       status: str = ModuleStatus.ACTIVE,
                       limit: int = 5) -> List[Dict]:
        """
        Search relevant modules (returns latest ACTIVE version by default)

        Args:
            query: Query description (natural language)
            category: Category filter (atomic | third_party | composite)
            subcategory: Subcategory filter (browser | array, etc.)
            status: Status filter (active | draft | deprecated), default: active
            limit: Number of results

        Returns:
            List of modules
        """
        metadata_filter = {
            "knowledge_type": KnowledgeType.MODULE,
            "status": status
        }

        if category:
            metadata_filter["category"] = category
        if subcategory:
            metadata_filter["subcategory"] = subcategory

        return self._search_knowledge(
            query=query,
            metadata_filter=metadata_filter,
            limit=limit
        )

    def search_lessons(self, query: str, min_quality_score: float = 0.7,
                       limit: int = 5) -> List[Dict]:
        """
        Search relevant lessons learned

        Args:
            query: Query description
            min_quality_score: Minimum quality score
            limit: Number of results

        Returns:
            List of lessons
        """
        results = self._search_knowledge(
            query=query,
            metadata_filter={"knowledge_type": KnowledgeType.LESSON},
            limit=limit * 2  # Get more to filter
        )

        # Filter by quality score
        filtered = [
            r for r in results
            if r.get('metadata', {}).get('quality_score', 0) >= min_quality_score
        ]

        return filtered[:limit]

    def search_error_patterns(self, query: str, error_type: Optional[str] = None,
                              limit: int = 5) -> List[Dict]:
        """
        Search relevant error patterns

        Args:
            query: Query description
            error_type: Error type filter
            limit: Number of results

        Returns:
            List of error records
        """
        metadata_filter = {"knowledge_type": KnowledgeType.ERROR_LOG}

        if error_type:
            metadata_filter["error_type"] = error_type

        return self._search_knowledge(
            query=query,
            metadata_filter=metadata_filter,
            limit=limit
        )

    def search_similar_tasks(self, task_description: str, limit: int = 3) -> List[Dict]:
        """
        Find similar successfully completed tasks (Phase 3.3)

        Args:
            task_description: User's task description
            limit: Number of results to return

        Returns:
            List of similar task examples with metadata

        Example:
            >>> results = knowledge.search_similar_tasks(
            ...     task_description="Check spreadsheet for missing data",
            ...     limit=3
            ... )
            >>> for task in results:
            ...     print(f"Similar: {task['metadata']['task_description']}")
            ...     print(f"Plan: {task['metadata']['plan']}")
        """
        metadata_filter = {"knowledge_type": KnowledgeType.TASK_EXAMPLE}

        logger.info(f"Searching for similar tasks: {task_description[:50]}...")
        results = self._search_knowledge(
            query=task_description,
            metadata_filter=metadata_filter,
            limit=limit
        )

        logger.info(f"Found {len(results)} similar task examples")
        return results

    def _search_knowledge(self, query: str, metadata_filter: Dict,
                          limit: int = 5) -> List[Dict]:
        """
        Low-level knowledge retrieval (using enhanced retrieval)

        Args:
            query: Query text
            metadata_filter: Metadata filter conditions
            limit: Number of results

        Returns:
            List of retrieval results
        """
        try:
            if self.enhanced_retrieval:
                # Use enhanced retrieval
                results = self.enhanced_retrieval.retrieve(
                    query=query,
                    qdrant_client=self.qdrant_client,
                    collection_name=self.collection_name,
                    embedding_function=self._get_embedding,
                    metadata_filter=metadata_filter,
                    context=""  # Knowledge retrieval doesn't need conversation context
                )

                # Convert format
                return [
                    {
                        'content': r.get('content', ''),
                        'metadata': r.get('metadata', {}),
                        'score': r.get('score', 0.0)
                    }
                    for r in results[:limit]
                ]

            else:
                # Fallback to simple retrieval
                embedding = self._get_embedding(query)

                # Build filter
                filter_conditions = []
                for key, value in metadata_filter.items():
                    filter_conditions.append(
                        FieldCondition(
                            key=f"metadata.{key}",
                            match=MatchValue(value=value)
                        )
                    )

                search_filter = Filter(must=filter_conditions) if filter_conditions else None

                # Execute search
                search_results = self.qdrant_client.query_points(
                    collection_name=self.collection_name,
                    query=embedding,
                    query_filter=search_filter,
                    limit=limit
                ).points

                # Convert format
                return [
                    {
                        'content': point.payload.get('content', ''),
                        'metadata': point.payload.get('metadata', {}),
                        'score': point.score
                    }
                    for point in search_results
                ]

        except Exception as e:
            logger.error(f"Knowledge search failed: {e}")
            return []

    # ============================================================
    # Batch Operations
    # ============================================================

    def batch_store_modules(self, modules: List[Dict]) -> List[str]:
        """
        Batch store modules

        Args:
            modules: List of module data

        Returns:
            List of knowledge_ids
        """
        knowledge_ids = []

        for module in modules:
            try:
                knowledge_id = self.store_module(
                    module_id=module['module_id'],
                    category=module['category'],
                    subcategory=module['subcategory'],
                    description=module['description'],
                    parameters=module['parameters'],
                    returns=module['returns'],
                    code_example=module.get('code_example'),
                    metadata=module.get('metadata')
                )
                knowledge_ids.append(knowledge_id)

            except Exception as e:
                logger.error(f"Failed to store module {module.get('module_id')}: {e}")

        logger.info(f"Batch stored {len(knowledge_ids)}/{len(modules)} modules")
        return knowledge_ids

    # ============================================================
    # Statistics and Maintenance
    # ============================================================

    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        try:
            collection_info = self.qdrant_client.get_collection(self.collection_name)

            stats = {
                'total_knowledge': collection_info.points_count,
                'vector_dimension': collection_info.config.params.vectors.size,
                'distance_metric': collection_info.config.params.vectors.distance
            }

            # Statistics by type (requires iterating all points, may be slow)
            # Simplified implementation here, only return total count

            return stats

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}

    def cleanup_old_errors(self, days: int = 90):
        """Clean up old error records"""
        try:
            from datetime import timedelta

            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_str = cutoff_date.isoformat()

            # Qdrant doesn't support direct deletion by timestamp, needs scroll + delete
            # Simplified implementation here, leave for future optimization

            logger.info(f"Error logs older than {days} days should be cleaned (not implemented)")

        except Exception as e:
            logger.error(f"Failed to cleanup old errors: {e}")

    # ============================================================
    # Module Versioning Management
    # ============================================================

    def get_module_versions(self, module_id: str) -> List[Dict]:
        """
        Get all versions of a specific module

        Args:
            module_id: Module ID (e.g., "browser.click")

        Returns:
            List of module versions, sorted by timestamp (newest first)
        """
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue

            # Search for all versions of this module
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="metadata.knowledge_type",
                        match=MatchValue(value=KnowledgeType.MODULE)
                    ),
                    FieldCondition(
                        key="metadata.module_id",
                        match=MatchValue(value=module_id)
                    )
                ]
            )

            # Scroll through all matching points
            results = []
            offset = None

            while True:
                scroll_result = self.qdrant_client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=filter_condition,
                    limit=100,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )

                points, next_offset = scroll_result

                for point in points:
                    metadata = point.payload.get('metadata', {})
                    results.append({
                        'point_id': point.id,
                        'knowledge_id': point.payload.get('knowledge_id'),
                        'version': metadata.get('version', 'unknown'),
                        'status': metadata.get('status', 'unknown'),
                        'timestamp': metadata.get('timestamp'),
                        'metadata': metadata
                    })

                if next_offset is None:
                    break

                offset = next_offset

            # Sort by timestamp (newest first)
            results.sort(key=lambda x: x['timestamp'], reverse=True)

            logger.info(f"Found {len(results)} versions for module {module_id}")
            return results

        except Exception as e:
            logger.error(f"Failed to get module versions: {e}")
            return []

    def update_module_status(self, module_id: str, version: str, new_status: str) -> bool:
        """
        Update status of a specific module version

        Args:
            module_id: Module ID
            version: Version string
            new_status: New status (draft | active | deprecated)

        Returns:
            Success boolean
        """
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue

            # Find the specific version
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="metadata.knowledge_type",
                        match=MatchValue(value=KnowledgeType.MODULE)
                    ),
                    FieldCondition(
                        key="metadata.module_id",
                        match=MatchValue(value=module_id)
                    ),
                    FieldCondition(
                        key="metadata.version",
                        match=MatchValue(value=version)
                    )
                ]
            )

            # Scroll to find matching points
            scroll_result = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                scroll_filter=filter_condition,
                limit=10,
                with_payload=True,
                with_vectors=False
            )

            points, _ = scroll_result

            if not points:
                logger.warning(f"Module {module_id} version {version} not found")
                return False

            # Update status for all matching points (should be only 1)
            for point in points:
                # Get current payload
                current_payload = point.payload

                # Update status in metadata
                current_payload['metadata']['status'] = new_status

                # Update point in Qdrant
                self.qdrant_client.set_payload(
                    collection_name=self.collection_name,
                    payload=current_payload,
                    points=[point.id]
                )

                logger.info(f"Updated {module_id} v{version} status to {new_status}")

            return True

        except Exception as e:
            logger.error(f"Failed to update module status: {e}")
            return False

    def _deprecate_old_versions(self, module_id: str, exclude_version: str):
        """
        Deprecate all active versions except the specified one

        Args:
            module_id: Module ID
            exclude_version: Version to exclude from deprecation
        """
        try:
            versions = self.get_module_versions(module_id)

            for version_info in versions:
                version = version_info['version']
                current_status = version_info['status']

                # Skip the version we want to keep
                if version == exclude_version:
                    continue

                # Deprecate if currently active
                if current_status == ModuleStatus.ACTIVE:
                    self.update_module_status(module_id, version, ModuleStatus.DEPRECATED)
                    logger.info(f"Auto-deprecated {module_id} v{version}")

        except Exception as e:
            logger.error(f"Failed to deprecate old versions: {e}")


# ============================================================
# Global Instance Management
# ============================================================

_knowledge_extractor_instance: Optional[KnowledgeExtractor] = None


def get_knowledge_extractor() -> KnowledgeExtractor:
    """Get KnowledgeExtractor singleton"""
    global _knowledge_extractor_instance
    if _knowledge_extractor_instance is None:
        _knowledge_extractor_instance = KnowledgeExtractor()
    return _knowledge_extractor_instance
