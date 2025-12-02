"""
Recommendation Generator Module - Generate scraping recommendations

Atomic responsibility: Generate actionable scraping recommendations
Extracted from: daily_practice.py lines 200-227
"""

from typing import Any, Dict, List


class RecommendationGeneratorModule:
    """
    Generate scraping recommendations based on website analysis

    Single responsibility: Provide actionable scraping guidance
    """

    @staticmethod
    def generate(analysis: Dict[str, Any]) -> List[str]:
        """
        Generate scraping recommendations based on analysis

        Args:
            analysis: Website analysis results containing:
                - robots_txt: Robots.txt analysis
                - structure: HTML structure info
                - patterns: Detected patterns

        Returns:
            List of recommendation strings with emojis
        """
        recommendations = []

        # Check robots.txt
        robots_txt = analysis.get("robots_txt", {})
        if robots_txt.get("status") == "not_found":
            recommendations.append("✅ No robots.txt found - scraping generally allowed")
        elif robots_txt.get("crawl_delay"):
            delay = robots_txt["crawl_delay"]
            recommendations.append(
                f"⚠️ Respect crawl-delay: {delay} seconds between requests"
            )

        # Check for disallowed paths
        if robots_txt.get("disallowed_paths"):
            count = len(robots_txt["disallowed_paths"])
            recommendations.append(
                f"🚫 {count} paths disallowed by robots.txt - avoid these"
            )

        # Structure recommendations
        structure = analysis.get("structure", {})
        if structure.get("tables", 0) > 0:
            recommendations.append(
                f"📊 Found {structure['tables']} table(s) - structured data available"
            )

        if structure.get("lists", {}).get("ul", 0) > 5:
            recommendations.append(
                "📝 Multiple lists detected - good for list extraction"
            )

        if structure.get("forms", 0) > 0:
            recommendations.append(
                f"📋 Found {structure['forms']} form(s) - may require interaction"
            )

        # Pattern-based recommendations
        patterns = structure.get("patterns", {})
        if patterns.get("product_containers"):
            recommendations.append(
                "🛒 Product containers detected - e-commerce site"
            )
        if patterns.get("article_containers"):
            recommendations.append(
                "📰 Article containers detected - content site"
            )
        if patterns.get("pagination"):
            recommendations.append(
                "📄 Pagination detected - multi-page scraping possible"
            )

        # Meta information recommendations
        if structure.get("has_meta_og"):
            recommendations.append(
                "🔍 Open Graph meta tags found - rich metadata available"
            )

        if structure.get("has_json_ld"):
            recommendations.append(
                "📦 JSON-LD structured data found - easy extraction possible"
            )

        # Default recommendation if nothing specific found
        if not recommendations:
            recommendations.append(
                "ℹ️ Basic HTML structure - standard scraping approach recommended"
            )

        return recommendations

    @staticmethod
    def generate_strategy(analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate detailed scraping strategy

        Args:
            analysis: Website analysis results

        Returns:
            Strategy dict with approach, selectors, warnings
        """
        strategy = {
            "approach": "standard",  # standard, api, dynamic, form_based
            "selectors": [],
            "warnings": [],
            "techniques": []
        }

        patterns = analysis.get("structure", {}).get("patterns", {})

        # Determine approach
        if patterns.get("product_containers"):
            strategy["approach"] = "product_listing"
            strategy["techniques"].append("container_iteration")

        elif patterns.get("article_containers"):
            strategy["approach"] = "content_extraction"
            strategy["techniques"].append("article_parsing")

        elif analysis.get("structure", {}).get("has_json_ld"):
            strategy["approach"] = "structured_data"
            strategy["techniques"].append("json_ld_extraction")

        # Add selectors based on patterns
        for container_type, containers in patterns.items():
            if containers and container_type != "pagination":
                strategy["selectors"].append({
                    "type": container_type,
                    "selector": containers[0] if isinstance(containers, list) else containers
                })

        # Add warnings
        robots_txt = analysis.get("robots_txt", {})
        if robots_txt.get("crawl_delay"):
            strategy["warnings"].append(
                f"Rate limit required: {robots_txt['crawl_delay']}s"
            )

        if analysis.get("structure", {}).get("forms", 0) > 0:
            strategy["warnings"].append(
                "Site may require form interaction or login"
            )

        return strategy
