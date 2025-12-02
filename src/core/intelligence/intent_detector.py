"""
智能意圖檢測 - 使用 LLM 而非程式邏輯
讓 AI 自己判斷使用者想做什麼，而不是用 regex
"""
import json
import requests
from typing import Dict, Any, Optional


class IntelligentIntentDetector:
    """使用 LLM 智能判斷使用者意圖"""

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url

    async def detect_intent(self, user_message: str, conversation_history: str = "") -> Dict[str, Any]:
        """
        讓 Ollama 判斷使用者意圖
        不用 regex，不用 if-else，讓 AI 自己決定
        """

        detection_prompt = f"""你是意圖檢測專家。仔細分析使用者訊息，判斷意圖。

使用者訊息: {user_message}

# 判斷步驟（按順序檢查）:

## 步驟 1: 檢查是否為「建立工具」
如果訊息包含以下任一模式，則 intent = "create_tool":
- "建立/創建/做/寫/新增 + [工具/模組/功能]"
- "我需要/想要/能不能做 + 一個 + [XX工具/XX器]"
- "make/create/build + a + [tool/module]"

✅ create_tool 例子:
- "建立一個圖片壓縮工具" → create_tool
- "我需要一個 PDF 轉換器" → create_tool
- "做一個 JSON 驗證器" → create_tool
- "能不能做個 URL 縮短器" → create_tool
- "寫一個 CSV 解析工具" → create_tool
- "幫我建立密碼生成器" → create_tool
- "make a video compressor" → create_tool

## 步驟 2: 檢查是否為「搜尋」
如果訊息包含明確搜尋動作，則 intent = "search":
- 開頭或包含: "搜尋/查/找/Google/搜索/尋找"
- "幫我查/找一下/請查/查一下"
- 任何明確要求搜尋資訊的動作

✅ search 例子:
- "搜尋 Python 教學" → search
- "幫我查一下 React" → search
- "找一下機器學習資料" → search
- "Google 一下最新消息" → search
- "請查 Node.js 最佳實踐" → search
- "查一下 React hooks" → search
- "尋找 FastAPI 文檔" → search

❌ NOT search:
- "我想知道 Docker 怎麼用" → conversation (問問題)
- "什麼是機器學習？" → conversation (問問題)
- "這個怎麼用？" → help

## 步驟 3: 檢查是否為「幫助」
如果使用者不會用或需要說明，則 intent = "help":
- "怎麼用/如何用/不會用"
- "幫助/help"

## 步驟 4: 其他情況
所有其他情況 → intent = "conversation"

# 輸出格式 (ONLY JSON):
{{
  "intent": "create_tool|search|help|conversation",
  "confidence": 0.8-1.0,
  "description": "一句話描述",
  "parameters": {{"query": "..." 或 "tool_description": "..."}},
  "reasoning": "判斷理由"
}}

**判斷 {user_message}:**"""

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": detection_prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=30
            )

            if response.status_code == 200:
                result_text = response.json()['response']

                # 解析 JSON
                try:
                    intent_data = json.loads(result_text)
                    return intent_data
                except json.JSONDecodeError:
                    # 如果 JSON 解析失敗，嘗試提取 JSON 部分
                    import re
                    json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                    if json_match:
                        intent_data = json.loads(json_match.group(0))
                        return intent_data

                    # 完全失敗，返回預設
                    return {
                        "intent": "conversation",
                        "confidence": 0.5,
                        "description": "無法判斷意圖，當作一般對話",
                        "parameters": {},
                        "reasoning": "JSON 解析失敗"
                    }

        except Exception as e:
            print(f"⚠️ Intent detection failed: {e}")

        # 失敗時的預設行為
        return {
            "intent": "conversation",
            "confidence": 0.3,
            "description": "預設為一般對話",
            "parameters": {},
            "reasoning": f"API 呼叫失敗: {str(e)}"
        }

    def should_create_tool(self, intent_data: Dict[str, Any]) -> bool:
        """判斷是否應該建立工具"""
        return (
            intent_data.get('intent') == 'create_tool' and
            intent_data.get('confidence', 0) > 0.6
        )

    def should_search(self, intent_data: Dict[str, Any]) -> bool:
        """判斷是否應該搜尋"""
        return (
            intent_data.get('intent') == 'search' and
            intent_data.get('confidence', 0) > 0.6
        )

    def get_search_query(self, intent_data: Dict[str, Any]) -> str:
        """取得搜尋關鍵字"""
        params = intent_data.get('parameters', {})
        return params.get('query', '')

    def get_tool_description(self, intent_data: Dict[str, Any]) -> str:
        """取得工具描述"""
        params = intent_data.get('parameters', {})
        return params.get('tool_description', '')


# 測試
async def test_intent_detection():
    """測試智能意圖檢測"""
    detector = IntelligentIntentDetector()

    test_cases = [
        # 一般對話
        "你好",
        "今天天氣如何？",
        "我叫張三",

        # 搜尋意圖
        "搜尋 Python 教學",
        "幫我查一下 React 最新版本",
        "找一下機器學習的資料",

        # 建立工具
        "建立一個圖片壓縮工具",
        "我需要一個 PDF 轉換器",
        "能不能做個發送郵件的功能",

        # 模糊情況
        "這個怎麼用？",
        "有什麼功能？",
    ]

    print("智能意圖檢測測試\n")
    print("=" * 80)

    for i, test_msg in enumerate(test_cases, 1):
        print(f"\n測試 {i}: {test_msg}")
        intent = await detector.detect_intent(test_msg)

        print(f"  意圖: {intent['intent']}")
        print(f"  信心: {intent['confidence']:.0%}")
        print(f"  描述: {intent['description']}")
        if intent.get('parameters'):
            print(f"  參數: {intent['parameters']}")
        print(f"  推理: {intent['reasoning']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_intent_detection())
