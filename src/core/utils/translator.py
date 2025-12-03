"""
Universal Translator for Vector DB Storage

Core principle:
- ALL content stored to vector DB must be in English
- User input may be Chinese → translate
- Error messages may be Chinese → translate
- AI responses may be Chinese → translate
- Preserve technical accuracy - don't lose meaning

Uses Ollama (free) for translation with technical context
"""

import os
import requests
from typing import Dict, List, Optional


class UniversalTranslator:
    """
    Universal translator for vector DB storage

    Ensures all content is in English for:
    - Better embedding quality
    - Universal searchability
    - Consistent knowledge base
    """

    def __init__(self):
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.cache = {}  # Simple cache to avoid re-translating

    async def translate_to_english(
        self,
        text: str,
        context: str = "general",
        preserve_technical: bool = True
    ) -> str:
        """
        Translate any text to English

        Args:
            text: Text to translate (Chinese or English)
            context: Context hint (error/solution/conversation/code)
            preserve_technical: Preserve technical terms accurately

        Returns:
            English translation (or original if already English)
        """
        # Check cache
        cache_key = f"{context}:{text[:100]}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Detect if already English (mostly)
        if self._is_mostly_english(text):
            return text

        # Build context-aware translation prompt
        system_prompt = self._build_translation_prompt(context, preserve_technical)

        try:
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": "llama3.2",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text}
                    ],
                    "stream": False
                },
                timeout=30
            )

            if response.status_code == 200:
                translation = response.json()['message']['content'].strip()

                # Cache the translation
                self.cache[cache_key] = translation

                return translation
            else:
                # Fallback: return original
                print(f"⚠️ Translation failed: {response.status_code}")
                return text

        except Exception as e:
            print(f"⚠️ Translation error: {e}")
            # Fallback: return original
            return text

    def _is_mostly_english(self, text: str) -> bool:
        """Check if text is mostly English (>80%)"""
        if not text:
            return True

        # Count English characters (ASCII) vs total
        english_chars = sum(1 for c in text if ord(c) < 128)
        total_chars = len(text)

        # If >80% ASCII, consider it English
        return (english_chars / total_chars) > 0.8 if total_chars > 0 else True

    def _build_translation_prompt(
        self,
        context: str,
        preserve_technical: bool
    ) -> str:
        """Build context-aware translation prompt"""

        base_prompt = "You are a professional translator specializing in technical documentation."

        context_instructions = {
            "error": """
Translate error messages to English.
Preserve:
- Error types (Exception, ValueError, etc.)
- File paths
- Module names
- Stack traces
- Technical terms
""",
            "solution": """
Translate solution descriptions to English.
Preserve:
- Command names (pip, playwright, git)
- Package names
- File paths
- Configuration keys
- Code snippets
""",
            "conversation": """
Translate conversational text to English.
Keep it natural but preserve:
- Technical terms
- Product names
- URLs
- Specific names
""",
            "code": """
Translate code comments and descriptions to English.
DO NOT translate:
- Variable names
- Function names
- Class names
- Code syntax
"""
        }

        instruction = context_instructions.get(context, context_instructions["general"])

        prompt = f"""{base_prompt}

{instruction}

IMPORTANT:
- Only output the translation
- No explanations or notes
- Preserve technical accuracy
- Keep the same tone and meaning
- If already in English, return as-is
"""

        return prompt

    async def translate_batch(
        self,
        texts: List[str],
        context: str = "general"
    ) -> List[str]:
        """Translate multiple texts efficiently"""
        translations = []

        for text in texts:
            translation = await self.translate_to_english(text, context)
            translations.append(translation)

        return translations

    async def translate_dict(
        self,
        data: Dict[str, str],
        context: str = "general"
    ) -> Dict[str, str]:
        """Translate all values in a dictionary"""
        translated = {}

        for key, value in data.items():
            if isinstance(value, str):
                translated[key] = await self.translate_to_english(value, context)
            else:
                translated[key] = value

        return translated


# Singleton instance
_translator = None

def get_translator() -> UniversalTranslator:
    """Get singleton translator instance"""
    global _translator
    if _translator is None:
        _translator = UniversalTranslator()
    return _translator


async def translate_to_english(
    text: str,
    context: str = "general",
    preserve_technical: bool = True
) -> str:
    """
    Convenience function for quick translation

    Args:
        text: Text to translate
        context: Context hint (error/solution/conversation/code)
        preserve_technical: Preserve technical terms

    Returns:
        English translation
    """
    translator = get_translator()
    return await translator.translate_to_english(text, context, preserve_technical)
