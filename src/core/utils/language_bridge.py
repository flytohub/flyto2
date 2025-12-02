"""
Language Bridge Layer (LBL) - 語言橋接層

Purpose: Bridge Chinese ↔ English for vector search
- Detect language automatically
- Translate zh → en for semantic search
- Ensure embedding consistency
- Enable multilingual RAG

Critical for Flyto2 Self-Evolving AI Agent
"""

from typing import Dict, Any, Optional, List
import re


class LanguageBridge:
    """
    Language Bridge Layer for multilingual vector search

    Workflow:
    1. Detect language (zh/en)
    2. If zh → Semantic EN translation
    3. Vectorize using EN
    4. Search Qdrant
    5. Return results in original language
    """

    def __init__(self):
        self.supported_languages = ["zh", "en"]

    def detect_language(self, text: str) -> str:
        """
        Fast language detection

        Args:
            text: Input text

        Returns:
            'zh' or 'en'
        """
        # Simple heuristic: Check for Chinese characters
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)

        if len(chinese_chars) > len(text) * 0.3:  # 30% Chinese
            return "zh"
        else:
            return "en"

    async def translate_to_english(self, text: str, provider: str = "ollama") -> Dict[str, Any]:
        """
        Semantic translation zh → en for vector search

        NOT word-by-word translation, but semantic meaning preservation

        Args:
            text: Chinese text
            provider: 'ollama' or 'openai'

        Returns:
            {
                "success": bool,
                "translated": str (English),
                "original": str (Chinese)
            }
        """
        from src.core.utils.http_client import HTTPClient

        # Build translation prompt
        prompt = f"""Translate this Chinese text to English, preserving semantic meaning for technical search:

Chinese: {text}

English (semantic, technical):"""

        system_prompt = """You are a technical translator. Translate Chinese to English while:
1. Preserving technical terms (browser, timeout, error, module, etc.)
2. Keeping semantic meaning for vector search
3. Short and concise
4. Return ONLY the English translation, no explanation"""

        try:
            if provider == "ollama":
                response = await HTTPClient.ask_ollama(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    model="llama3.2",
                    timeout=30
                )
            else:
                # OpenAI fallback
                response = await HTTPClient.ask_openai(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    timeout=30
                )

            if response["success"]:
                translated = response["content"].strip()

                return {
                    "success": True,
                    "translated": translated,
                    "original": text
                }
            else:
                return {
                    "success": False,
                    "error": response.get("error", "Translation failed"),
                    "original": text
                }

        except Exception as e:
            # Fallback: Return original if translation fails
            return {
                "success": False,
                "error": str(e),
                "original": text
            }

    async def prepare_query_for_search(
        self,
        query: str,
        auto_translate: bool = True
    ) -> Dict[str, Any]:
        """
        Prepare query for Qdrant search with language bridge

        Workflow:
        1. Detect language
        2. If zh → Translate to en
        3. Return search-ready query

        Args:
            query: User input query (any language)
            auto_translate: Auto translate zh → en

        Returns:
            {
                "original": str,
                "search_query": str (always EN for embedding),
                "language": "zh" or "en",
                "translated": bool
            }
        """
        # Detect language
        lang = self.detect_language(query)

        if lang == "en":
            # Already English, use directly
            return {
                "original": query,
                "search_query": query,
                "language": "en",
                "translated": False
            }

        elif lang == "zh" and auto_translate:
            # Chinese → Need translation for embedding
            translation_result = await self.translate_to_english(query)

            if translation_result["success"]:
                return {
                    "original": query,
                    "search_query": translation_result["translated"],
                    "language": "zh",
                    "translated": True
                }
            else:
                # Translation failed, use original (lower precision)
                return {
                    "original": query,
                    "search_query": query,
                    "language": "zh",
                    "translated": False,
                    "error": translation_result.get("error")
                }
        else:
            # No translation requested
            return {
                "original": query,
                "search_query": query,
                "language": lang,
                "translated": False
            }

    async def create_bilingual_entry(
        self,
        content: str,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create bilingual entries for Qdrant storage

        Strategy:
        - If content is zh → Create both zh and en versions
        - If content is en → Store only en version

        Args:
            content: Original content
            metadata: Metadata dict

        Returns:
            List of entries to store (1 or 2)
        """
        lang = self.detect_language(content)
        entries = []

        if lang == "zh":
            # Chinese content → Create both versions

            # 1. Original Chinese entry
            zh_entry = {
                "content": content,
                "metadata": {
                    **metadata,
                    "language": "zh",
                    "is_translated": False
                }
            }
            entries.append(zh_entry)

            # 2. English translated entry
            translation = await self.translate_to_english(content)

            if translation["success"]:
                en_entry = {
                    "content": translation["translated"],
                    "metadata": {
                        **metadata,
                        "language": "en",
                        "is_translated": True,
                        "original_language": "zh"
                    }
                }
                entries.append(en_entry)

        else:
            # English content → Store only en
            en_entry = {
                "content": content,
                "metadata": {
                    **metadata,
                    "language": "en",
                    "is_translated": False
                }
            }
            entries.append(en_entry)

        return entries


# Singleton instance
_bridge = None

def get_language_bridge() -> LanguageBridge:
    """Get singleton Language Bridge instance"""
    global _bridge
    if _bridge is None:
        _bridge = LanguageBridge()
    return _bridge


# Convenience functions
async def detect_language(text: str) -> str:
    """Quick language detection"""
    bridge = get_language_bridge()
    return bridge.detect_language(text)


async def translate_zh_to_en(text: str) -> str:
    """Quick translation zh → en"""
    bridge = get_language_bridge()
    result = await bridge.translate_to_english(text)
    return result.get("translated", text) if result["success"] else text


async def prepare_search_query(query: str) -> Dict[str, Any]:
    """Prepare query with language bridge"""
    bridge = get_language_bridge()
    return await bridge.prepare_query_for_search(query)
