"""
HTML Pattern Detector Module - Detect HTML patterns for data extraction

Atomic responsibility: Identify common HTML patterns
Extracted from: daily_practice.py lines 158-198
"""

import re
from collections import Counter
from typing import Any, Dict, List
from bs4 import BeautifulSoup


class HtmlPatternDetectorModule:
    """
    Detect HTML patterns for data extraction

    Single responsibility: Identify article/product/list containers and pagination
    """

    @staticmethod
    def detect(soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Detect common HTML patterns for data extraction

        Args:
            soup: BeautifulSoup instance

        Returns:
            {
                "article_containers": [class names...],
                "product_containers": [class names...],
                "list_containers": [class names...],
                "pagination": class name or None,
                "common_classes": [top 10 class names...]
            }
        """
        patterns = {
            "article_containers": [],
            "product_containers": [],
            "list_containers": [],
            "pagination": None,
            "common_classes": []
        }

        # Detect article patterns
        article_tags = soup.find_all(
            ['article', 'div'],
            class_=re.compile(r'(article|post|entry)', re.I)
        )
        if article_tags:
            patterns["article_containers"] = [
                str(tag.get('class')) for tag in article_tags[:3]
            ]

        # Detect product patterns
        product_tags = soup.find_all(
            ['div', 'li'],
            class_=re.compile(r'(product|item|card)', re.I)
        )
        if product_tags:
            patterns["product_containers"] = [
                str(tag.get('class')) for tag in product_tags[:3]
            ]

        # Detect list patterns
        list_containers = soup.find_all(['ul', 'ol'], class_=True)
        if list_containers:
            patterns["list_containers"] = [
                str(tag.get('class')) for tag in list_containers[:3]
            ]

        # Detect pagination
        pagination = soup.find(
            ['nav', 'div'],
            class_=re.compile(r'(pagination|pager)', re.I)
        )
        if pagination:
            patterns["pagination"] = str(pagination.get('class'))

        # Find most common classes (potential data containers)
        all_classes = []
        for tag in soup.find_all(class_=True):
            classes = tag.get('class', [])
            all_classes.extend(classes)

        class_counts = Counter(all_classes)
        patterns["common_classes"] = [
            cls for cls, count in class_counts.most_common(10)
        ]

        return patterns

    @staticmethod
    def find_data_containers(soup: BeautifulSoup, min_children: int = 3) -> List[Dict[str, Any]]:
        """
        Find potential data containers (repeating elements)

        Args:
            soup: BeautifulSoup instance
            min_children: Minimum number of similar children to be considered a container

        Returns:
            List of container info dicts
        """
        containers = []

        # Look for divs/sections with multiple similar children
        for parent in soup.find_all(['div', 'section', 'ul', 'ol']):
            children = parent.find_all(recursive=False)

            if len(children) >= min_children:
                # Check if children are similar (same tag, similar class)
                child_tags = [child.name for child in children]
                child_classes = [str(child.get('class', [])) for child in children]

                # If most children have same tag and class pattern
                tag_counter = Counter(child_tags)
                class_counter = Counter(child_classes)

                most_common_tag = tag_counter.most_common(1)[0]
                most_common_class = class_counter.most_common(1)[0]

                similarity_ratio = most_common_tag[1] / len(children)

                if similarity_ratio >= 0.7:  # 70% of children are similar
                    containers.append({
                        "parent_tag": parent.name,
                        "parent_class": str(parent.get('class', [])),
                        "child_tag": most_common_tag[0],
                        "child_class": most_common_class[0],
                        "count": len(children),
                        "similarity": similarity_ratio
                    })

        # Sort by count and similarity
        containers.sort(key=lambda x: (x['count'], x['similarity']), reverse=True)

        return containers
