"""
Intent Detector - Determines if message is a task or conversation
"""
import re
from typing import Dict, Any, Optional


class IntentDetector:
    """
    Detect user intent from natural language
    """

    def __init__(self):
        # Task keywords that indicate user wants action
        self.task_keywords = [
            # Crawling/scraping
            r'爬[取得]?',
            r'抓[取]?',
            r'scrape',
            r'crawl',
            r'fetch',
            r'get.*from',
            r'extract.*from',

            # Searching
            r'搜[尋索]',
            r'找[尋]?',
            r'查[找詢]?',
            r'search',
            r'find',
            r'look.*for',

            # Actions
            r'幫我',
            r'請',
            r'help me',
            r'can you',
            r'could you',

            # Direct commands
            r'download',
            r'save',
            r'export',
        ]

        # URL patterns
        self.url_pattern = r'https?://[^\s]+'

    def detect(self, message: str) -> Dict[str, Any]:
        """
        Detect intent from message

        Args:
            message: User message

        Returns:
            Intent info with type, confidence, and extracted params
        """
        message_lower = message.lower()

        result = {
            "type": "conversation",  # conversation or task
            "confidence": 0.0,
            "task_type": None,  # crawl, search, download, etc.
            "params": {}
        }

        # Check for URLs (strong signal for task)
        urls = re.findall(self.url_pattern, message)
        if urls:
            result["params"]["urls"] = urls
            result["confidence"] += 0.4

        # Check for task keywords
        task_matches = 0
        for pattern in self.task_keywords:
            if re.search(pattern, message_lower):
                task_matches += 1

        if task_matches > 0:
            result["confidence"] += 0.3 * min(task_matches, 2)

        # Determine if it's a task
        if result["confidence"] >= 0.4:
            result["type"] = "task"

            # Determine task type
            if any(re.search(p, message_lower) for p in [r'爬', r'抓', r'crawl', r'scrape']):
                result["task_type"] = "crawl"
            elif any(re.search(p, message_lower) for p in [r'搜', r'找', r'查', r'search', r'find']):
                result["task_type"] = "search"
            elif any(re.search(p, message_lower) for p in [r'download', r'下載']):
                result["task_type"] = "download"
            else:
                result["task_type"] = "general"

            # Extract search query
            if result["task_type"] in ["search", "crawl"]:
                # Try to extract what to search for
                search_patterns = [
                    r'(?:找|搜|search|find|look for)\s*(?:商品|product)?\s*[：:"]?\s*(.+?)(?:\s|$)',
                    r'(?:查|find)\s+(.+?)(?:\s+in\s+|\s+on\s+|$)',
                ]

                for pattern in search_patterns:
                    match = re.search(pattern, message_lower)
                    if match:
                        query = match.group(1).strip()
                        # Clean up query
                        query = re.sub(r'https?://[^\s]+', '', query).strip()
                        if query:
                            result["params"]["query"] = query
                            break

        return result
