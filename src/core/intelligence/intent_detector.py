"""
Intelligent Intent Detection - Using LLM instead of programmatic logic
Let AI determine what the user wants to do, not regex
"""
import json
import requests
from typing import Dict, Any, Optional


class IntelligentIntentDetector:
    """Use LLM to intelligently determine user intent"""

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url

    async def detect_intent(self, user_message: str, conversation_history: str = "") -> Dict[str, Any]:
        """
        Let Ollama determine user intent
        No regex, no if-else, let AI decide
        """

        detection_prompt = f"""You are an intent detection expert. Carefully analyze the user message and determine the intent.

User message: {user_message}

# Detection steps (check in order):

## Step 1: Check if "task_execution" (HIGH PRIORITY - Check FIRST)
If the message requests to PERFORM/EXECUTE an action (not create a tool), intent = "task_execution":
- "download/get/fetch/scrape + [something]"
- "go to/visit/open + [website/URL] + extract/get/download"
- "help me + [action verb] + [target]"
- Any request to DO something NOW (not create a tool for future use)

Examples of task_execution:
- "Download dog images and convert to SVG" -> task_execution
- "Go to amazon.com and find iPhone prices" -> task_execution
- "Scrape news from BBC website" -> task_execution
- "Get me the weather for Tokyo" -> task_execution
- "Extract all links from example.com" -> task_execution
- "Help me download YouTube video" -> task_execution

NOT task_execution:
- "Create a tool to download images" -> create_tool (wants to BUILD a tool)
- "Make an image downloader" -> create_tool (wants to CREATE something)

## Step 2: Check if "create tool"
If the message wants to CREATE/BUILD a tool for future use, intent = "create_tool":
- "create/make/build/write/add + [tool/module/function]"
- "I need/want/can you make + a + [XX tool/XX converter]"

Examples of create_tool:
- "Create an image compression tool" -> create_tool
- "I need a PDF converter" -> create_tool
- "Make a JSON validator" -> create_tool
- "Can you make a URL shortener" -> create_tool
- "Write a CSV parser tool" -> create_tool
- "Help me create a password generator" -> create_tool
- "make a video compressor" -> create_tool

## Step 3: Check if "search"
If the message contains explicit search action, intent = "search":
- Starts with or contains: "search/find/look up/Google"
- "help me search/find/look for"
- Any explicit request to search for information

Examples of search:
- "Search Python tutorials" -> search
- "Help me find React info" -> search
- "Look for machine learning resources" -> search
- "Google the latest news" -> search
- "Search for Node.js best practices" -> search
- "Find FastAPI documentation" -> search

NOT search:
- "I want to know how Docker works" -> conversation (asking question)
- "What is machine learning?" -> conversation (asking question)
- "How do I use this?" -> help

## Step 4: Check if "help"
If user doesn't know how to use or needs instructions, intent = "help":
- "how to use/how do I use/don't know how"
- "help"

## Step 5: Other cases
All other cases -> intent = "conversation"

# Output format (ONLY JSON):
{{
  "intent": "task_execution|create_tool|search|help|conversation",
  "confidence": 0.8-1.0,
  "description": "One sentence description",
  "parameters": {{"query": "..." or "tool_description": "..." or "task": "..."}},
  "reasoning": "Reasoning for the decision"
}}

**Determine intent for: {user_message}**"""

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

                # Parse JSON
                try:
                    intent_data = json.loads(result_text)
                    return intent_data
                except json.JSONDecodeError:
                    # If JSON parsing fails, try to extract JSON portion
                    import re
                    json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                    if json_match:
                        intent_data = json.loads(json_match.group(0))
                        return intent_data

                    # Complete failure, return default
                    return {
                        "intent": "conversation",
                        "confidence": 0.5,
                        "description": "Unable to determine intent, treating as general conversation",
                        "parameters": {},
                        "reasoning": "JSON parsing failed"
                    }

        except Exception as e:
            print(f"Warning: Intent detection failed: {e}")

        # Default behavior on failure
        return {
            "intent": "conversation",
            "confidence": 0.3,
            "description": "Defaulting to general conversation",
            "parameters": {},
            "reasoning": f"API call failed: {str(e)}"
        }

    def should_create_tool(self, intent_data: Dict[str, Any]) -> bool:
        """Determine if tool should be created"""
        return (
            intent_data.get('intent') == 'create_tool' and
            intent_data.get('confidence', 0) > 0.6
        )

    def should_search(self, intent_data: Dict[str, Any]) -> bool:
        """Determine if search should be performed"""
        return (
            intent_data.get('intent') == 'search' and
            intent_data.get('confidence', 0) > 0.6
        )

    def get_search_query(self, intent_data: Dict[str, Any]) -> str:
        """Get search keyword"""
        params = intent_data.get('parameters', {})
        return params.get('query', '')

    def get_tool_description(self, intent_data: Dict[str, Any]) -> str:
        """Get tool description"""
        params = intent_data.get('parameters', {})
        return params.get('tool_description', '')


# Test
async def test_intent_detection():
    """Test intelligent intent detection"""
    detector = IntelligentIntentDetector()

    test_cases = [
        # General conversation
        "Hello",
        "How's the weather today?",
        "My name is John",

        # Search intent
        "Search Python tutorials",
        "Help me find React latest version",
        "Look for machine learning resources",

        # Create tool
        "Create an image compression tool",
        "I need a PDF converter",
        "Can you make an email sending function",

        # Ambiguous cases
        "How do I use this?",
        "What features are available?",
    ]

    print("Intelligent Intent Detection Test\n")
    print("=" * 80)

    for i, test_msg in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_msg}")
        intent = await detector.detect_intent(test_msg)

        print(f"  Intent: {intent['intent']}")
        print(f"  Confidence: {intent['confidence']:.0%}")
        print(f"  Description: {intent['description']}")
        if intent.get('parameters'):
            print(f"  Parameters: {intent['parameters']}")
        print(f"  Reasoning: {intent['reasoning']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_intent_detection())
