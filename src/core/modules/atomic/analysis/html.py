"""
HTML Analysis Modules - Advanced HTML Structure Analysis

Provides workflow-callable modules for HTML analysis
"""

from src.core.modules.base import BaseModule
from src.core.modules.registry import register_module
from src.core.analysis.html_analyzer import HTMLAnalyzer
from typing import Any, Dict


@register_module('analysis.html.structure')
class AnalyzeHTMLStructure(BaseModule):
    """
    Analyze HTML structure comprehensively

    Parameters:
        html (str): HTML content to analyze

    Returns:
        Complete structure analysis including DOM, semantic sections, tables, forms, links, media
    """

    module_name = "AnalyzeHTMLStructure"
    module_description = "Comprehensive HTML structure analysis"

    def validate_params(self):
        """Validate and extract parameters"""
        if "html" not in self.params:
            raise ValueError("Missing required parameter: html")
        self.html = self.params["html"]

    async def execute(self) -> Any:
        """
        Analyze HTML structure

        Returns:
            Structure analysis results
        """
        try:
            analyzer = HTMLAnalyzer(self.html)
            result = analyzer.analyze_structure()

            return result

        except Exception as e:
            raise RuntimeError(f"HTML structure analysis failed: {str(e)}")


@register_module('analysis.html.find_patterns')
class FindDataPatterns(BaseModule):
    """
    Find repeating data patterns in HTML

    Parameters:
        html (str): HTML content to analyze

    Returns:
        Detected patterns with CSS selectors
    """

    module_name = "FindDataPatterns"
    module_description = "Find repeating data patterns (products, articles, list items)"

    def validate_params(self):
        """Validate and extract parameters"""
        if "html" not in self.params:
            raise ValueError("Missing required parameter: html")
        self.html = self.params["html"]

    async def execute(self) -> Any:
        """
        Find data patterns

        Returns:
            List of detected patterns
        """
        try:
            analyzer = HTMLAnalyzer(self.html)
            patterns = analyzer.find_data_patterns()

            return {
                "patterns": patterns,
                "pattern_count": len(patterns),
                "total_items": sum(p["count"] for p in patterns),
                "recommended_pattern": patterns[0] if patterns else None
            }

        except Exception as e:
            raise RuntimeError(f"Pattern detection failed: {str(e)}")


@register_module('analysis.html.extract_tables')
class ExtractTables(BaseModule):
    """
    Extract data tables from HTML

    Parameters:
        html (str): HTML content to analyze

    Returns:
        Extracted tables with headers and data
    """

    module_name = "ExtractTables"
    module_description = "Extract and analyze data tables"

    def validate_params(self):
        """Validate and extract parameters"""
        if "html" not in self.params:
            raise ValueError("Missing required parameter: html")
        self.html = self.params["html"]

    async def execute(self) -> Any:
        """
        Extract tables

        Returns:
            Table data
        """
        try:
            analyzer = HTMLAnalyzer(self.html)
            structure = analyzer.analyze_structure()
            tables = structure.get("data_tables", [])

            return {
                "tables": tables,
                "table_count": len(tables),
                "has_headers": sum(1 for t in tables if t["headers"]),
                "total_rows": sum(t["row_count"] for t in tables)
            }

        except Exception as e:
            raise RuntimeError(f"Table extraction failed: {str(e)}")


@register_module('analysis.html.extract_forms')
class ExtractForms(BaseModule):
    """
    Analyze form structures in HTML

    Parameters:
        html (str): HTML content to analyze

    Returns:
        Form structures with fields and metadata
    """

    module_name = "ExtractForms"
    module_description = "Extract and analyze form structures"

    def validate_params(self):
        """Validate and extract parameters"""
        if "html" not in self.params:
            raise ValueError("Missing required parameter: html")
        self.html = self.params["html"]

    async def execute(self) -> Any:
        """
        Extract forms

        Returns:
            Form data
        """
        try:
            analyzer = HTMLAnalyzer(self.html)
            structure = analyzer.analyze_structure()
            forms = structure.get("forms", [])

            return {
                "forms": forms,
                "form_count": len(forms),
                "total_fields": sum(f["field_count"] for f in forms),
                "required_fields": sum(
                    sum(1 for field in f["fields"] if field.get("required"))
                    for f in forms
                )
            }

        except Exception as e:
            raise RuntimeError(f"Form extraction failed: {str(e)}")


@register_module('analysis.html.extract_metadata')
class ExtractMetadata(BaseModule):
    """
    Extract meta information from HTML

    Parameters:
        html (str): HTML content to analyze

    Returns:
        Meta tags, Open Graph, Twitter Cards, and other metadata
    """

    module_name = "ExtractMetadata"
    module_description = "Extract meta information and structured data"

    def validate_params(self):
        """Validate and extract parameters"""
        if "html" not in self.params:
            raise ValueError("Missing required parameter: html")
        self.html = self.params["html"]

    async def execute(self) -> Any:
        """
        Extract metadata

        Returns:
            Metadata
        """
        try:
            analyzer = HTMLAnalyzer(self.html)
            structure = analyzer.analyze_structure()
            meta_info = structure.get("meta_info", {})

            # Also extract JSON-LD
            json_ld = analyzer.extract_json_ld()

            return {
                "meta_info": meta_info,
                "json_ld": json_ld,
                "has_og_tags": bool(meta_info.get("og_tags")),
                "has_twitter_tags": bool(meta_info.get("twitter_tags")),
                "structured_data_count": len(json_ld)
            }

        except Exception as e:
            raise RuntimeError(f"Metadata extraction failed: {str(e)}")


@register_module('analysis.html.analyze_readability')
class AnalyzeReadability(BaseModule):
    """
    Analyze content readability metrics

    Parameters:
        html (str): HTML content to analyze

    Returns:
        Readability metrics including word count, sentences, paragraphs
    """

    module_name = "AnalyzeReadability"
    module_description = "Calculate content readability metrics"

    def validate_params(self):
        """Validate and extract parameters"""
        if "html" not in self.params:
            raise ValueError("Missing required parameter: html")
        self.html = self.params["html"]

    async def execute(self) -> Any:
        """
        Analyze readability

        Returns:
            Readability metrics
        """
        try:
            analyzer = HTMLAnalyzer(self.html)
            structure = analyzer.analyze_structure()
            readability = structure.get("readability", {})

            return readability

        except Exception as e:
            raise RuntimeError(f"Readability analysis failed: {str(e)}")
