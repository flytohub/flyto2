"""
Daily Practice Modules - Wrapper for DailyPracticeEngine

Allows workflows to execute practice sessions
"""

from src.core.modules.base import BaseModule
from src.core.modules.registry import register_module
from src.core.training.daily_practice import DailyPracticeEngine
from typing import Any, Dict


@register_module('training.practice.analyze')
class AnalyzeWebsiteModule(BaseModule):
    """
    Analyze website structure for practice

    Parameters:
        url (str): Target website URL

    Returns:
        Website analysis including robots.txt, structure, and recommendations
    """

    module_name = "AnalyzeWebsite"
    module_description = "Analyze website structure and constraints"

    def validate_params(self):
        """Validate and extract parameters"""
        if "url" not in self.params:
            raise ValueError("Missing required parameter: url")
        self.url = self.params["url"]

    async def execute(self) -> Any:
        """
        Analyze website

        Returns:
            Analysis results
        """
        try:
            engine = DailyPracticeEngine()
            result = await engine.analyze_website(self.url)

            return result

        except Exception as e:
            raise RuntimeError(f"Website analysis failed: {str(e)}")


@register_module('training.practice.infer_schema')
class InferSchemaModule(BaseModule):
    """
    Infer data schema from website

    Parameters:
        url (str): Target website URL
        sample_size (int): Number of sample elements to analyze (default: 5)

    Returns:
        Inferred schema with field types and extraction rules
    """

    module_name = "InferSchema"
    module_description = "Automatically infer data schema from website"

    def validate_params(self):
        """Validate and extract parameters"""
        if "url" not in self.params:
            raise ValueError("Missing required parameter: url")
        self.url = self.params["url"]
        self.sample_size = self.params.get("sample_size", 5)

    async def execute(self) -> Any:
        """
        Infer schema

        Returns:
            Schema inference results
        """
        try:
            engine = DailyPracticeEngine()
            result = await engine.infer_schema(self.url, self.sample_size)

            return result

        except Exception as e:
            raise RuntimeError(f"Schema inference failed: {str(e)}")


@register_module('training.practice.execute')
class ExecutePracticeModule(BaseModule):
    """
    Execute a complete practice session

    Parameters:
        url (str): Target website URL
        max_items (int): Maximum items to scrape (default: 10)

    Returns:
        Practice results with scraped data, errors, and learnings
    """

    module_name = "ExecutePractice"
    module_description = "Execute complete practice session"

    def validate_params(self):
        """Validate and extract parameters"""
        if "url" not in self.params:
            raise ValueError("Missing required parameter: url")
        self.url = self.params["url"]
        self.max_items = self.params.get("max_items", 10)

    async def execute(self) -> Any:
        """
        Execute practice session

        Returns:
            Complete practice results
        """
        try:
            engine = DailyPracticeEngine()
            result = await engine.execute_practice(self.url, self.max_items)

            return result

        except Exception as e:
            raise RuntimeError(f"Practice session failed: {str(e)}")


@register_module('training.practice.stats')
class GetPracticeStatsModule(BaseModule):
    """
    Get practice statistics

    Parameters:
        None

    Returns:
        Overall practice statistics
    """

    module_name = "GetPracticeStats"
    module_description = "Get overall practice statistics"

    def validate_params(self):
        """No parameters required"""
        pass

    async def execute(self) -> Any:
        """
        Get practice stats

        Returns:
            Practice statistics
        """
        try:
            engine = DailyPracticeEngine()
            result = engine.get_practice_stats()

            return result

        except Exception as e:
            raise RuntimeError(f"Failed to get practice stats: {str(e)}")


@register_module('training.practice.history')
class GetPracticeHistoryModule(BaseModule):
    """
    Get practice history

    Parameters:
        limit (int): Number of recent sessions to retrieve (default: 10)

    Returns:
        Recent practice sessions
    """

    module_name = "GetPracticeHistory"
    module_description = "Get recent practice history"

    def validate_params(self):
        """Validate and extract parameters"""
        self.limit = self.params.get("limit", 10)

    async def execute(self) -> Any:
        """
        Get practice history

        Returns:
            Recent practice sessions
        """
        try:
            engine = DailyPracticeEngine()
            result = engine.get_practice_history(self.limit)

            return result

        except Exception as e:
            raise RuntimeError(f"Failed to get practice history: {str(e)}")
