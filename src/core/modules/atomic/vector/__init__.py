"""
Vector Database Module
Knowledge storage and retrieval with embeddings
"""
from .connector import VectorDBConnector, get_connector, close_global_connector
from .embeddings import EmbeddingGenerator, embed_text, embed_texts
from .knowledge_store import KnowledgeStore

__all__ = [
    "VectorDBConnector",
    "get_connector",
    "close_global_connector",
    "EmbeddingGenerator",
    "embed_text",
    "embed_texts",
    "KnowledgeStore"
]
