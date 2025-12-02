"""
Schema Inferrer Module - Infer data schema from HTML samples

Atomic responsibility: Automatically infer data structure from HTML
Extracted from: daily_practice.py lines 277-398
"""

import re
from typing import Any, Dict, List
from bs4 import BeautifulSoup


class SchemaInferrerModule:
    """
    Infer data schema from HTML samples

    Single responsibility: Detect repeating containers and extract field types
    """

    @staticmethod
    def find_repeating_containers(
        soup: BeautifulSoup,
        limit: int = 5
    ) -> List[Any]:
        """
        Find repeating HTML containers (products, articles, etc.)

        Args:
            soup: BeautifulSoup instance
            limit: Maximum number of containers to return

        Returns:
            List of container elements
        """
        # Common container patterns
        patterns = [
            ('div', re.compile(r'(product|item|card|article|post)', re.I)),
            ('li', re.compile(r'(product|item|card)', re.I)),
            ('article', None),
            ('tr', None)  # Table rows
        ]

        for tag, class_pattern in patterns:
            if class_pattern:
                containers = soup.find_all(tag, class_=class_pattern, limit=limit * 2)
            else:
                containers = soup.find_all(tag, limit=limit * 2)

            # Filter out containers that are too small (likely not data containers)
            valid_containers = [c for c in containers if len(str(c)) > 100]

            if len(valid_containers) >= 3:  # Need at least 3 to confirm pattern
                return valid_containers[:limit]

        return []

    @staticmethod
    def extract_field_types(container: Any) -> Dict[str, str]:
        """
        Extract field types from a sample container

        Args:
            container: BeautifulSoup element

        Returns:
            Dict of field_name: field_type
        """
        fields = {}

        # Look for common patterns
        # Titles/headings
        for tag in ['h1', 'h2', 'h3', 'h4', 'strong', 'b']:
            element = container.find(tag)
            if element and element.get_text(strip=True):
                fields[f"{tag}_text"] = "string"

        # Links
        links = container.find_all('a', href=True)
        if links:
            fields["link_url"] = "url"
            fields["link_text"] = "string"

        # Images
        images = container.find_all('img', src=True)
        if images:
            fields["image_url"] = "url"
            fields["image_alt"] = "string"

        # Prices (common in e-commerce)
        price_patterns = re.compile(r'(price|cost|amount)', re.I)
        price_element = container.find(class_=price_patterns)
        if price_element:
            fields["price"] = "number"

        # Dates
        date_patterns = re.compile(r'(date|time|published)', re.I)
        date_element = container.find(class_=date_patterns)
        if date_element:
            fields["date"] = "datetime"

        # Generic text fields
        text_divs = container.find_all('div', class_=True)
        for i, div in enumerate(text_divs[:3]):  # Limit to first 3
            text = div.get_text(strip=True)
            if text and len(text) > 10:
                fields[f"text_field_{i+1}"] = "string"

        return fields

    @staticmethod
    def generate_extraction_rules(containers: List[Any]) -> List[Dict[str, str]]:
        """
        Generate CSS selector rules for extraction

        Args:
            containers: List of container elements

        Returns:
            List of extraction rule dicts
        """
        if not containers:
            return []

        rules = []
        sample = containers[0]

        # Generate rules for common elements
        # Title rule
        for tag in ['h1', 'h2', 'h3', 'h4']:
            element = sample.find(tag)
            if element:
                rules.append({
                    "field": f"{tag}_title",
                    "selector": tag,
                    "type": "text"
                })
                break

        # Link rule
        link = sample.find('a', href=True)
        if link:
            # Try to generate specific selector
            if link.get('class'):
                selector = f"a.{link['class'][0]}"
            else:
                selector = "a[href]"

            rules.append({
                "field": "link",
                "selector": selector,
                "type": "attribute",
                "attribute": "href"
            })

        # Image rule
        img = sample.find('img', src=True)
        if img:
            if img.get('class'):
                selector = f"img.{img['class'][0]}"
            else:
                selector = "img[src]"

            rules.append({
                "field": "image",
                "selector": selector,
                "type": "attribute",
                "attribute": "src"
            })

        # Price rule
        price_patterns = re.compile(r'(price|cost|amount)', re.I)
        price_element = sample.find(class_=price_patterns)
        if price_element and price_element.get('class'):
            rules.append({
                "field": "price",
                "selector": f".{price_element['class'][0]}",
                "type": "text"
            })

        return rules

    @staticmethod
    def calculate_confidence(containers: List[Any]) -> float:
        """
        Calculate confidence score for schema inference

        Args:
            containers: List of container elements

        Returns:
            Confidence score (0.0-1.0)
        """
        if not containers:
            return 0.0

        # Base confidence on number of similar containers found
        count = len(containers)
        if count >= 10:
            base_confidence = 0.9
        elif count >= 5:
            base_confidence = 0.7
        elif count >= 3:
            base_confidence = 0.5
        else:
            base_confidence = 0.3

        # Boost confidence if containers are very similar
        if count >= 2:
            # Compare first two containers' structure
            first_html = str(containers[0])
            second_html = str(containers[1])

            # Simple similarity check (same length range)
            len_ratio = min(len(first_html), len(second_html)) / max(len(first_html), len(second_html))

            if len_ratio > 0.9:  # Very similar length
                base_confidence += 0.1

        return min(base_confidence, 1.0)

    @staticmethod
    def infer_schema(soup: BeautifulSoup, sample_size: int = 5) -> Dict[str, Any]:
        """
        Complete schema inference from HTML

        Args:
            soup: BeautifulSoup instance
            sample_size: Number of sample containers to analyze

        Returns:
            Complete schema inference result
        """
        # Find repeating containers
        containers = SchemaInferrerModule.find_repeating_containers(soup, limit=sample_size)

        if not containers:
            return {
                "detected_fields": {},
                "extraction_rules": [],
                "confidence": 0.0,
                "container_count": 0,
                "status": "no_pattern_found"
            }

        # Extract field types from first container
        fields = SchemaInferrerModule.extract_field_types(containers[0])

        # Generate extraction rules
        rules = SchemaInferrerModule.generate_extraction_rules(containers)

        # Calculate confidence
        confidence = SchemaInferrerModule.calculate_confidence(containers)

        return {
            "detected_fields": fields,
            "extraction_rules": rules,
            "confidence": confidence,
            "container_count": len(containers),
            "status": "success"
        }
