"""
對話記憶系統 - 短期 + 長期記憶
使用 Qdrant 向量資料庫做 RAG
"""
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    print("⚠️ Qdrant not installed. Memory features will be limited.")


class ConversationMemory:
    """
    完整的對話記憶系統
    - 短期記憶: 當前會話的對話歷史
    - 長期記憶: 持久化到 Qdrant 向量資料庫
    """

    def __init__(self, user_id: str, use_qdrant: bool = True):
        self.user_id = user_id
        self.use_qdrant = use_qdrant and QDRANT_AVAILABLE

        # 短期記憶 (session memory)
        self.conversation_history: List[Dict[str, str]] = []
        self.max_short_term = 10  # 保留最近 10 條訊息

        # Qdrant 客戶端 (長期記憶)
        self.qdrant_client = None
        self.collection_name = f"user_{user_id}_conversations"

        if self.use_qdrant:
            self._init_qdrant()

    def _init_qdrant(self):
        """初始化 Qdrant 向量資料庫"""
        try:
            # 檢查環境變數
            qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
            qdrant_api_key = os.getenv("QDRANT_API_KEY")

            # 連接 Qdrant
            if qdrant_api_key:
                self.qdrant_client = QdrantClient(
                    url=qdrant_url,
                    api_key=qdrant_api_key
                )
            else:
                # 本地 Qdrant (無需 API key)
                self.qdrant_client = QdrantClient(url=qdrant_url)

            # 建立 collection (如果不存在)
            collections = self.qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=384,  # nomic-embed-text 的維度
                        distance=Distance.COSINE
                    )
                )
                print(f"✅ Created Qdrant collection: {self.collection_name}")

        except Exception as e:
            print(f"⚠️ Qdrant initialization failed: {e}")
            self.qdrant_client = None
            self.use_qdrant = False

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        添加訊息到記憶
        role: 'user' or 'assistant'
        content: 訊息內容
        metadata: 額外的元數據
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        # 短期記憶
        self.conversation_history.append(message)

        # 限制短期記憶大小
        if len(self.conversation_history) > self.max_short_term:
            self.conversation_history = self.conversation_history[-self.max_short_term:]

        # 長期記憶 (向量資料庫)
        if self.use_qdrant and self.qdrant_client:
            self._store_to_qdrant(message)

    def _store_to_qdrant(self, message: Dict[str, str]):
        """儲存訊息到 Qdrant 向量資料庫"""
        try:
            # 生成 embedding (使用 Ollama 的 embedding 模型)
            import requests

            embed_response = requests.post(
                "http://localhost:11434/api/embeddings",
                json={
                    "model": "nomic-embed-text",
                    "prompt": message['content']
                },
                timeout=10
            )

            if embed_response.status_code == 200:
                embedding = embed_response.json()['embedding']

                # 儲存到 Qdrant
                point_id = hash(message['timestamp'] + message['content']) % (10 ** 8)

                self.qdrant_client.upsert(
                    collection_name=self.collection_name,
                    points=[
                        PointStruct(
                            id=point_id,
                            vector=embedding,
                            payload={
                                "role": message['role'],
                                "content": message['content'],
                                "timestamp": message['timestamp'],
                                "metadata": message.get('metadata', {})
                            }
                        )
                    ]
                )
        except Exception as e:
            print(f"⚠️ Failed to store to Qdrant: {e}")

    def get_recent_history(self, limit: int = 5) -> List[Dict[str, str]]:
        """取得最近的對話歷史 (短期記憶)"""
        return self.conversation_history[-limit:]

    def search_similar(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        搜尋相似的歷史對話 (長期記憶 RAG)
        使用向量相似度搜尋
        """
        if not self.use_qdrant or not self.qdrant_client:
            return []

        try:
            # 生成 query embedding
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

            # 向量搜尋
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit
            )

            # 轉換結果
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
            print(f"⚠️ Qdrant search failed: {e}")
            return []

    def get_context_for_ollama(self, current_query: str, include_rag: bool = True) -> str:
        """
        為 Ollama 準備完整的上下文
        包含：短期記憶 + RAG 檢索的長期記憶
        """
        context_parts = []

        # 1. 短期記憶 (最近的對話)
        recent = self.get_recent_history(limit=5)
        if recent:
            context_parts.append("最近的對話:")
            for msg in recent:
                role_name = "使用者" if msg['role'] == 'user' else "助手"
                context_parts.append(f"{role_name}: {msg['content']}")

        # 2. 長期記憶 RAG (相關的歷史對話)
        if include_rag:
            similar = self.search_similar(current_query, limit=3)
            if similar:
                context_parts.append("\n相關的歷史對話:")
                for msg in similar:
                    role_name = "使用者" if msg['role'] == 'user' else "助手"
                    context_parts.append(f"{role_name}: {msg['content']} (相似度: {msg['score']:.2f})")

        return "\n".join(context_parts)

    def clear_short_term(self):
        """清除短期記憶"""
        self.conversation_history = []

    def get_stats(self) -> Dict[str, Any]:
        """取得記憶統計資訊"""
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


# 全域記憶管理器
_memory_instances: Dict[str, ConversationMemory] = {}


def get_memory(user_id: str) -> ConversationMemory:
    """取得或建立使用者的記憶實例"""
    if user_id not in _memory_instances:
        _memory_instances[user_id] = ConversationMemory(user_id)
    return _memory_instances[user_id]


def clear_memory(user_id: str):
    """清除使用者的記憶"""
    if user_id in _memory_instances:
        _memory_instances[user_id].clear_short_term()
