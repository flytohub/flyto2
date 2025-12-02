"""
Daily Practice Engine - AI Self-Training System

This engine allows the AI agent to practice on real websites daily:
1. Analyze website structure (robots.txt, HTML structure)
2. Infer data schema automatically
3. Execute small-scale scraping (10-20 items)
4. Analyze errors and learn
5. Generate practice reports

Auto-generated practice sessions are logged to metrics/daily_practice.json
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


class DailyPracticeEngine:
    """
    AI agent daily practice engine for self-improvement
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.metrics_dir = self.project_root / "metrics"
        self.metrics_dir.mkdir(exist_ok=True)
        self.practice_log = self.metrics_dir / "daily_practice.json"

    async def analyze_website(self, url: str) -> Dict[str, Any]:
        """
        Analyze website structure and constraints

        Args:
            url: Target website URL

        Returns:
            Analysis results including robots.txt, structure, and recommendations
        """
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        analysis = {
            "url": url,
            "base_url": base_url,
            "timestamp": datetime.now().isoformat(),
            "robots_txt": None,
            "structure": {},
            "recommendations": [],
            "errors": []
        }

        # Step 1: Check robots.txt
        try:
            robots_url = urljoin(base_url, "/robots.txt")
            async with aiohttp.ClientSession() as session:
                async with session.get(robots_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        robots_content = await response.text()
                        analysis["robots_txt"] = self._parse_robots_txt(robots_content)
                    else:
                        analysis["robots_txt"] = {"status": "not_found"}
        except Exception as e:
            analysis["errors"].append(f"Failed to fetch robots.txt: {str(e)}")
            analysis["robots_txt"] = {"status": "error", "error": str(e)}

        # Step 2: Analyze HTML structure
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                await page.goto(url, wait_until="networkidle", timeout=30000)

                # Get page content
                html_content = await page.content()
                soup = BeautifulSoup(html_content, 'html.parser')

                # Analyze structure
                analysis["structure"] = {
                    "title": soup.title.string if soup.title else None,
                    "meta_tags": len(soup.find_all('meta')),
                    "headings": {
                        "h1": len(soup.find_all('h1')),
                        "h2": len(soup.find_all('h2')),
                        "h3": len(soup.find_all('h3'))
                    },
                    "links": len(soup.find_all('a')),
                    "images": len(soup.find_all('img')),
                    "forms": len(soup.find_all('form')),
                    "tables": len(soup.find_all('table')),
                    "lists": {
                        "ul": len(soup.find_all('ul')),
                        "ol": len(soup.find_all('ol'))
                    }
                }

                # Detect common patterns
                analysis["structure"]["patterns"] = self._detect_patterns(soup)

                await browser.close()

        except Exception as e:
            analysis["errors"].append(f"Failed to analyze HTML structure: {str(e)}")

        # Step 3: Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)

        return analysis

    def _parse_robots_txt(self, content: str) -> Dict[str, Any]:
        """Parse robots.txt content"""
        rules = {
            "user_agents": {},
            "sitemaps": [],
            "crawl_delay": None
        }

        current_agent = None
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if line.lower().startswith('user-agent:'):
                current_agent = line.split(':', 1)[1].strip()
                if current_agent not in rules["user_agents"]:
                    rules["user_agents"][current_agent] = {"allow": [], "disallow": []}

            elif line.lower().startswith('disallow:') and current_agent:
                path = line.split(':', 1)[1].strip()
                if path:
                    rules["user_agents"][current_agent]["disallow"].append(path)

            elif line.lower().startswith('allow:') and current_agent:
                path = line.split(':', 1)[1].strip()
                if path:
                    rules["user_agents"][current_agent]["allow"].append(path)

            elif line.lower().startswith('crawl-delay:'):
                delay = line.split(':', 1)[1].strip()
                rules["crawl_delay"] = float(delay)

            elif line.lower().startswith('sitemap:'):
                sitemap = line.split(':', 1)[1].strip()
                rules["sitemaps"].append(sitemap)

        return rules

    def _detect_patterns(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Detect common HTML patterns for data extraction"""
        patterns = {
            "article_containers": [],
            "product_containers": [],
            "list_containers": [],
            "pagination": None,
            "common_classes": []
        }

        # Detect article patterns
        article_tags = soup.find_all(['article', 'div'], class_=re.compile(r'(article|post|entry)', re.I))
        if article_tags:
            patterns["article_containers"] = [str(tag.get('class')) for tag in article_tags[:3]]

        # Detect product patterns
        product_tags = soup.find_all(['div', 'li'], class_=re.compile(r'(product|item|card)', re.I))
        if product_tags:
            patterns["product_containers"] = [str(tag.get('class')) for tag in product_tags[:3]]

        # Detect list patterns
        list_containers = soup.find_all(['ul', 'ol'], class_=True)
        if list_containers:
            patterns["list_containers"] = [str(tag.get('class')) for tag in list_containers[:3]]

        # Detect pagination
        pagination = soup.find(['nav', 'div'], class_=re.compile(r'(pagination|pager)', re.I))
        if pagination:
            patterns["pagination"] = str(pagination.get('class'))

        # Find most common classes (potential data containers)
        all_classes = []
        for tag in soup.find_all(class_=True):
            classes = tag.get('class', [])
            all_classes.extend(classes)

        from collections import Counter
        class_counts = Counter(all_classes)
        patterns["common_classes"] = [cls for cls, count in class_counts.most_common(10)]

        return patterns

    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate scraping recommendations based on analysis"""
        recommendations = []

        # Check robots.txt
        if analysis.get("robots_txt", {}).get("status") == "not_found":
            recommendations.append("✅ No robots.txt found - scraping generally allowed")
        elif analysis.get("robots_txt", {}).get("crawl_delay"):
            delay = analysis["robots_txt"]["crawl_delay"]
            recommendations.append(f"⚠️ Respect crawl-delay: {delay} seconds between requests")

        # Structure recommendations
        structure = analysis.get("structure", {})
        if structure.get("tables", 0) > 0:
            recommendations.append(f"📊 Found {structure['tables']} table(s) - structured data available")

        if structure.get("lists", {}).get("ul", 0) > 5:
            recommendations.append("📝 Multiple lists detected - good for list extraction")

        patterns = structure.get("patterns", {})
        if patterns.get("product_containers"):
            recommendations.append("🛒 Product containers detected - e-commerce site")
        if patterns.get("article_containers"):
            recommendations.append("📰 Article containers detected - content site")
        if patterns.get("pagination"):
            recommendations.append("📄 Pagination detected - multi-page scraping possible")

        return recommendations

    async def infer_schema(self, url: str, sample_size: int = 5) -> Dict[str, Any]:
        """
        Automatically infer data schema by analyzing sample elements

        Args:
            url: Target website URL
            sample_size: Number of sample elements to analyze

        Returns:
            Inferred schema with field types and extraction rules
        """
        schema = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "detected_fields": {},
            "extraction_rules": [],
            "confidence": 0.0,
            "errors": []
        }

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                await page.goto(url, wait_until="networkidle", timeout=30000)
                html_content = await page.content()
                soup = BeautifulSoup(html_content, 'html.parser')

                # Try to find repeating container patterns
                containers = self._find_repeating_containers(soup, sample_size)

                if containers:
                    # Analyze first container to infer schema
                    first_container = containers[0]
                    schema["detected_fields"] = self._extract_field_types(first_container)
                    schema["extraction_rules"] = self._generate_extraction_rules(containers)
                    schema["confidence"] = self._calculate_confidence(containers)
                else:
                    schema["errors"].append("No repeating containers found")

                await browser.close()

        except Exception as e:
            schema["errors"].append(f"Schema inference failed: {str(e)}")

        return schema

    def _find_repeating_containers(self, soup: BeautifulSoup, limit: int = 5) -> List[Any]:
        """Find repeating HTML containers (products, articles, etc.)"""
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

    def _extract_field_types(self, container: Any) -> Dict[str, str]:
        """Extract field types from a sample container"""
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

    def _generate_extraction_rules(self, containers: List[Any]) -> List[Dict[str, str]]:
        """Generate CSS selector rules for extraction"""
        rules = []

        if not containers:
            return rules

        # Analyze first container to generate rules
        first = containers[0]

        # Extract class-based selectors
        if first.get('class'):
            container_class = ' '.join(first['class'])
            rules.append({
                "type": "container",
                "selector": f".{first['class'][0]}",
                "description": "Main data container"
            })

        # Common sub-elements
        sub_elements = [
            ('a', 'link'),
            ('img', 'image'),
            ('h1, h2, h3', 'title'),
            ('.price, [class*="price"]', 'price')
        ]

        for selector, field_type in sub_elements:
            element = first.select_one(selector)
            if element:
                rules.append({
                    "type": field_type,
                    "selector": selector,
                    "attribute": "href" if field_type == "link" else ("src" if field_type == "image" else "text")
                })

        return rules

    def _calculate_confidence(self, containers: List[Any]) -> float:
        """Calculate confidence score for schema inference"""
        if len(containers) < 3:
            return 0.3

        # Check structural similarity
        structures = [len(str(c)) for c in containers]
        avg_length = sum(structures) / len(structures)
        variance = sum((l - avg_length) ** 2 for l in structures) / len(structures)

        # Low variance = high confidence
        if variance < 1000:
            return 0.9
        elif variance < 5000:
            return 0.7
        else:
            return 0.5

    async def execute_practice(self, url: str, max_items: int = 10) -> Dict[str, Any]:
        """
        Execute a complete practice session

        Args:
            url: Target website URL
            max_items: Maximum items to scrape (default 10-20)

        Returns:
            Practice results with scraped data, errors, and learnings
        """
        practice_result = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "analysis": {},
            "schema": {},
            "scraped_data": [],
            "errors": [],
            "learnings": [],
            "success_rate": 0.0,
            "status": "started"
        }

        try:
            # Step 1: Analyze website
            practice_result["analysis"] = await self.analyze_website(url)

            # Step 2: Infer schema
            practice_result["schema"] = await self.infer_schema(url, sample_size=5)

            # Step 3: Execute small-scale scraping
            if practice_result["schema"].get("extraction_rules"):
                scrape_result = await self._scrape_items(
                    url,
                    practice_result["schema"]["extraction_rules"],
                    max_items
                )
                practice_result["scraped_data"] = scrape_result["items"]
                practice_result["errors"].extend(scrape_result["errors"])

            # Step 4: Analyze errors and generate learnings
            practice_result["learnings"] = self._analyze_and_learn(practice_result)

            # Step 5: Calculate success rate
            total_attempts = max_items
            successful = len(practice_result["scraped_data"])
            practice_result["success_rate"] = successful / total_attempts if total_attempts > 0 else 0.0

            practice_result["status"] = "completed"

        except Exception as e:
            practice_result["errors"].append(f"Practice session failed: {str(e)}")
            practice_result["status"] = "failed"

        # Log practice session
        self._log_practice_session(practice_result)

        return practice_result

    async def _scrape_items(self, url: str, extraction_rules: List[Dict], max_items: int) -> Dict[str, Any]:
        """Execute actual scraping based on extraction rules"""
        result = {
            "items": [],
            "errors": []
        }

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                await page.goto(url, wait_until="networkidle", timeout=30000)
                html_content = await page.content()
                soup = BeautifulSoup(html_content, 'html.parser')

                # Find container selector
                container_rule = next((r for r in extraction_rules if r["type"] == "container"), None)
                if not container_rule:
                    result["errors"].append("No container rule found")
                    await browser.close()
                    return result

                containers = soup.select(container_rule["selector"])[:max_items]

                for idx, container in enumerate(containers):
                    item = {"_index": idx + 1}

                    for rule in extraction_rules:
                        if rule["type"] == "container":
                            continue

                        try:
                            element = container.select_one(rule["selector"])
                            if element:
                                if rule["attribute"] == "text":
                                    item[rule["type"]] = element.get_text(strip=True)
                                else:
                                    item[rule["type"]] = element.get(rule["attribute"])
                        except Exception as e:
                            result["errors"].append(f"Field extraction error: {str(e)}")

                    result["items"].append(item)

                await browser.close()

        except Exception as e:
            result["errors"].append(f"Scraping failed: {str(e)}")

        return result

    def _analyze_and_learn(self, practice_result: Dict[str, Any]) -> List[str]:
        """Analyze practice session and generate learnings"""
        learnings = []

        # Learning 1: Success rate analysis
        success_rate = practice_result.get("success_rate", 0.0)
        if success_rate >= 0.8:
            learnings.append("✅ High success rate - extraction rules work well")
        elif success_rate >= 0.5:
            learnings.append("⚠️ Moderate success rate - rules need refinement")
        else:
            learnings.append("❌ Low success rate - need better pattern detection")

        # Learning 2: Error pattern analysis
        errors = practice_result.get("errors", [])
        if "timeout" in str(errors).lower():
            learnings.append("🐌 Timeout errors detected - may need longer wait times")
        if "selector" in str(errors).lower():
            learnings.append("🎯 Selector errors - CSS selectors may be incorrect")
        if not errors:
            learnings.append("✨ No errors - clean execution")

        # Learning 3: Data quality
        scraped_data = practice_result.get("scraped_data", [])
        if scraped_data:
            fields_per_item = [len(item) for item in scraped_data]
            avg_fields = sum(fields_per_item) / len(fields_per_item)
            if avg_fields >= 5:
                learnings.append(f"📊 Rich data extraction - avg {avg_fields:.1f} fields per item")
            else:
                learnings.append(f"📝 Sparse data - only {avg_fields:.1f} fields per item on average")

        # Learning 4: Schema confidence
        schema_confidence = practice_result.get("schema", {}).get("confidence", 0.0)
        if schema_confidence >= 0.8:
            learnings.append("🎯 High confidence in detected schema")
        elif schema_confidence >= 0.5:
            learnings.append("🤔 Moderate confidence - schema may need validation")
        else:
            learnings.append("❓ Low confidence - manual schema definition recommended")

        return learnings

    def _log_practice_session(self, practice_result: Dict[str, Any]):
        """Log practice session to metrics file"""
        # Load existing log
        if self.practice_log.exists():
            with open(self.practice_log, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
        else:
            log_data = {"sessions": [], "total_sessions": 0}

        # Add new session
        log_data["sessions"].append(practice_result)
        log_data["total_sessions"] += 1

        # Save updated log
        with open(self.practice_log, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

    def get_practice_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent practice history"""
        if not self.practice_log.exists():
            return []

        with open(self.practice_log, 'r', encoding='utf-8') as f:
            log_data = json.load(f)

        sessions = log_data.get("sessions", [])
        return sessions[-limit:]

    def get_practice_stats(self) -> Dict[str, Any]:
        """Get overall practice statistics"""
        if not self.practice_log.exists():
            return {"total_sessions": 0, "avg_success_rate": 0.0}

        with open(self.practice_log, 'r', encoding='utf-8') as f:
            log_data = json.load(f)

        sessions = log_data.get("sessions", [])
        if not sessions:
            return {"total_sessions": 0, "avg_success_rate": 0.0}

        success_rates = [s.get("success_rate", 0.0) for s in sessions]

        return {
            "total_sessions": len(sessions),
            "avg_success_rate": sum(success_rates) / len(success_rates),
            "last_session": sessions[-1].get("timestamp") if sessions else None,
            "total_items_scraped": sum(len(s.get("scraped_data", [])) for s in sessions),
            "total_errors": sum(len(s.get("errors", [])) for s in sessions)
        }
