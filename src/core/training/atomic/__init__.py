"""
Training Atomic Modules - Atomic components for autonomous training

Each module handles ONE specific concern:
- robots_parser: Parse and analyze robots.txt files
- html_pattern_detector: Detect HTML patterns for data extraction
- schema_inferrer: Infer data schema from HTML samples
- recommendation_generator: Generate scraping recommendations
"""

from .robots_parser import RobotsParserModule
from .html_pattern_detector import HtmlPatternDetectorModule
from .schema_inferrer import SchemaInferrerModule
from .recommendation_generator import RecommendationGeneratorModule

__all__ = [
    'RobotsParserModule',
    'HtmlPatternDetectorModule',
    'SchemaInferrerModule',
    'RecommendationGeneratorModule'
]
