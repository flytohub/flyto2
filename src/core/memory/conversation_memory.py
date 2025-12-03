"""
Conversation Memory System - Short-term + Long-term Memory
Uses Qdrant vector database for RAG
"""
import os
import json
import yaml
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    print("Warning: Qdrant not installed. Memory features will be limited.")

# Enhanced retrieval module
try:
    from src.core.retrieval.enhanced_retrieval import EnhancedRetrieval
    ENHANCED_RETRIEVAL_AVAILABLE = True
except ImportError:
    ENHANCED_RETRIEVAL_AVAILABLE = False
    print("Warning: Enhanced retrieval not available.")


class ConversationMemory:
    """
    Complete conversation memory system
    - Short-term memory: Current session conversation history
    - Long-term memory: Persisted to Qdrant vector database
    """

    def __init__(self, user_id: str, use_qdrant: bool = True):
        self.user_id = user_id
        self.use_qdrant = use_qdrant and QDRANT_AVAILABLE

        # Short-term memory (session memory)
        self.conversation_history: List[Dict[str, str]] = []
        self.max_short_term = 10  # Keep last 10 messages

        # Load configuration
        config_path = Path(__file__).parent.parent.parent.parent / "config" / "vector_config.yaml"
        self.config = None
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)

        # Qdrant client (long-term memory)
        self.qdrant_client = None
        self.collection_name = "flyto2_memory"  # Unified collection name

        # Enhanced retriever
        self.enhanced_retrieval = None
        if ENHANCED_RETRIEVAL_AVAILABLE and self.config:
            try:
                self.enhanced_retrieval = EnhancedRetrieval(config_path)
            except Exception as e:
                print(f"Warning: Failed to initialize enhanced retrieval: {e}")

        # System Prompt template
        self.system_prompt_template = self._load_system_prompt_template()

        if self.use_qdrant:
            self._init_qdrant()

    def _load_system_prompt_template(self) -> str:
        """Load System Prompt template"""
        template_path = Path(__file__).parent.parent.parent.parent / "config" / "prompts" / "ollama_system_prompt.txt"

        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Default template
            return """You are Flyto2 Bot assistant.

Basic rules:
- Answer honestly
- If you don't know something, say "I'm not sure"
- Don't fabricate information
- Keep it concise

Conversation memory:
{context}
"""

    def _init_qdrant(self):
        """Initialize Qdrant vector database (cloud only - local Qdrant is NOT supported)"""
        try:
            # Check environment variables (cloud Qdrant required)
            qdrant_url = os.getenv("QDRANT_URL")
            qdrant_api_key = os.getenv("QDRANT_API_KEY")

            if not qdrant_url:
                print("⚠️ Warning: QDRANT_URL not set. Memory features will be limited.")
                print("   Local Qdrant is NOT supported. Please set up cloud Qdrant.")
                self.use_qdrant = False
                return

            if not qdrant_api_key:
                print("⚠️ Warning: QDRANT_API_KEY not set. Memory features will be limited.")
                self.use_qdrant = False
                return

            # Connect to cloud Qdrant
            self.qdrant_client = QdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key
            )

            # Create collection (if doesn't exist)
            collections = self.qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                # Get vector dimension from config
                vector_dim = 384  # Default
                if self.config and 'vector_db' in self.config:
                    vector_dim = self.config['vector_db']['vector'].get('dimension', 384)

                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=vector_dim,
                        distance=Distance.COSINE
                    )
                )
                print(f"Created Qdrant collection: {self.collection_name}")

        except Exception as e:
            print(f"Warning: Qdrant initialization failed: {e}")
            self.qdrant_client = None
            self.use_qdrant = False

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        Add message to memory
        role: 'user' or 'assistant'
        content: Message content
        metadata: Additional metadata
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        # Short-term memory
        self.conversation_history.append(message)

        # Limit short-term memory size
        if len(self.conversation_history) > self.max_short_term:
            self.conversation_history = self.conversation_history[-self.max_short_term:]

        # Long-term memory (vector database)
        # Filter user questions: only store statements and assistant responses, not questions
        is_user_question = (
            role == "user" and
            (content.endswith('?') or content.endswith('?'))
        )

        if self.use_qdrant and self.qdrant_client and not is_user_question:
            self._store_to_qdrant(message)

    def _store_to_qdrant(self, message: Dict[str, str]):
        """Store message to Qdrant vector database"""
        try:
            # Generate embedding (using Ollama's embedding model)
            import requests

            # Get embedding model from config
            embed_model = "nomic-embed-text"  # Default
            if self.config and 'vector_db' in self.config:
                embed_model = self.config['vector_db']['vector'].get('model', 'nomic-embed-text')

            embed_response = requests.post(
                "http://localhost:11434/api/embeddings",
                json={
                    "model": embed_model,
                    "prompt": message['content']
                },
                timeout=10
            )

            if embed_response.status_code == 200:
                embedding = embed_response.json()['embedding']

                # Store to Qdrant (with full metadata)
                point_id = hash(message['timestamp'] + message['content']) % (10 ** 8)

                # Build standard metadata
                payload_metadata = {
                    "project": "flyto2",
                    "type": "conversation",
                    "user_id": self.user_id,
                    "timestamp": message['timestamp']
                }

                # Merge custom metadata
                if message.get('metadata'):
                    payload_metadata.update(message['metadata'])

                self.qdrant_client.upsert(
                    collection_name=self.collection_name,
                    points=[
                        PointStruct(
                            id=point_id,
                            vector=embedding,
                            payload={
                                "content": message['content'],
                                "role": message['role'],
                                "metadata": payload_metadata
                            }
                        )
                    ]
                )
        except Exception as e:
            print(f"Warning: Failed to store to Qdrant: {e}")

    def get_recent_history(self, limit: int = 5) -> List[Dict[str, str]]:
        """Get recent conversation history (short-term memory)"""
        return self.conversation_history[-limit:]

    def search_similar(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Search similar historical conversations (long-term memory RAG)
        Using vector similarity search
        """
        if not self.use_qdrant or not self.qdrant_client:
            return []

        try:
            # Generate query embedding
            import requests

            embed_response = requests.post(
                "http://localhost:11434/api/embeddings",
                json={
                    "model": "nomic-embed-text",
                    "prompt": query
                },
                timeout=10
            )

            if embed_response.status_code != 200:
                return []

            query_embedding = embed_response.json()['embedding']

            # Vector search (Qdrant v1.16+ uses query_points instead of search)
            search_results = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=limit
            ).points

            # Convert results
            similar_messages = []
            for result in search_results:
                similar_messages.append({
                    "content": result.payload['content'],
                    "role": result.payload['role'],
                    "timestamp": result.payload['timestamp'],
                    "score": result.score
                })

            return similar_messages

        except Exception as e:
            print(f"Warning: Qdrant search failed: {e}")
            return []

    def get_context_for_ollama(self, current_query: str, include_rag: bool = True) -> str:
        """
        Prepare complete context for Ollama
        Includes: short-term memory + RAG-retrieved long-term memory
        """
        context_parts = []

        # 1. Short-term memory (recent conversations)
        recent = self.get_recent_history(limit=5)
        if recent:
            context_parts.append("Recent conversations:")
            for msg in recent:
                role_name = "User" if msg['role'] == 'user' else "Assistant"
                context_parts.append(f"{role_name}: {msg['content']}")

        # 2. Long-term memory RAG (related historical conversations)
        if include_rag:
            if self.enhanced_retrieval and self.qdrant_client:
                # Use enhanced retrieval
                try:
                    # Metadata filter (only retrieve current user's conversations)
                    metadata_filter = {
                        "user_id": self.user_id,
                        "type": "conversation"
                    }

                    # Embedding function
                    def embed_fn(text: str) -> List[float]:
                        import requests
                        embed_model = "nomic-embed-text"
                        if self.config and 'vector_db' in self.config:
                            embed_model = self.config['vector_db']['vector'].get('model', 'nomic-embed-text')

                        response = requests.post(
                            "http://localhost:11434/api/embeddings",
                            json={"model": embed_model, "prompt": text},
                            timeout=10
                        )
                        if response.status_code == 200:
                            return response.json()['embedding']
                        return []

                    # Execute enhanced retrieval
                    recent_context = "\n".join([f"{m['role']}: {m['content']}" for m in recent])

                    results = self.enhanced_retrieval.retrieve(
                        query=current_query,
                        qdrant_client=self.qdrant_client,
                        collection_name=self.collection_name,
                        embedding_function=embed_fn,
                        context=recent_context,
                        metadata_filter=metadata_filter
                    )

                    if results:
                        context_parts.append("\nRelated historical memories:")
                        for result in results:
                            content = result.get('content', '')
                            score = result.get('score', 0.0)
                            context_parts.append(f"- {content} (relevance: {score:.2f})")

                except Exception as e:
                    print(f"Warning: Enhanced retrieval failed, falling back to simple search: {e}")
                    # Fallback to simple search
                    similar = self.search_similar(current_query, limit=3)
                    if similar:
                        context_parts.append("\nRelated historical conversations:")
                        for msg in similar:
                            role_name = "User" if msg['role'] == 'user' else "Assistant"
                            context_parts.append(f"{role_name}: {msg['content']} (similarity: {msg['score']:.2f})")
            else:
                # Fallback to original simple search
                similar = self.search_similar(current_query, limit=3)
                if similar:
                    context_parts.append("\nRelated historical conversations:")
                    for msg in similar:
                        role_name = "User" if msg['role'] == 'user' else "Assistant"
                        context_parts.append(f"{role_name}: {msg['content']} (similarity: {msg['score']:.2f})")

        return "\n".join(context_parts)

    def get_system_prompt(self, current_query: str, include_rag: bool = True) -> str:
        """
        Get complete System Prompt (template + context)

        Returns:
            Complete system prompt string
        """
        # Get context
        context = self.get_context_for_ollama(current_query, include_rag)

        # Fill in template
        system_prompt = self.system_prompt_template.replace("{context}", context)

        return system_prompt

    def clear_short_term(self):
        """Clear short-term memory"""
        self.conversation_history = []

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        stats = {
            "short_term_messages": len(self.conversation_history),
            "qdrant_enabled": self.use_qdrant,
        }

        if self.use_qdrant and self.qdrant_client:
            try:
                collection_info = self.qdrant_client.get_collection(self.collection_name)
                stats["long_term_messages"] = collection_info.points_count
            except:
                stats["long_term_messages"] = 0

        return stats


# Global memory manager
_memory_instances: Dict[str, ConversationMemory] = {}


def get_memory(user_id: str) -> ConversationMemory:
    """Get or create user's memory instance"""
    if user_id not in _memory_instances:
        _memory_instances[user_id] = ConversationMemory(user_id)
    return _memory_instances[user_id]


def clear_memory(user_id: str):
    """Clear user's memory"""
    if user_id in _memory_instances:
        _memory_instances[user_id].clear_short_term()
