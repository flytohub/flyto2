"""
HTML Analyzer - Advanced HTML Structure Analysis

Provides deep analysis capabilities for HTML documents:
1. DOM tree analysis
2. Semantic structure detection
3. Data table extraction
4. Form field identification
5. Link graph analysis
6. Meta information extraction
"""

import re
from typing import Any, Dict, List, Optional
from collections import Counter
from bs4 import BeautifulSoup, Tag


class HTMLAnalyzer:
    """
    Advanced HTML analysis engine
    """

    def __init__(self, html_content: str):
        """
        Initialize analyzer with HTML content

        Args:
            html_content: Raw HTML string
        """
        self.html = html_content
        self.soup = BeautifulSoup(html_content, 'html.parser')

    def analyze_structure(self) -> Dict[str, Any]:
        """
        Comprehensive structure analysis

        Returns:
            Complete structure analysis results
        """
        return {
            "dom_stats": self._analyze_dom(),
            "semantic_sections": self._detect_semantic_sections(),
            "data_tables": self._extract_tables(),
            "forms": self._analyze_forms(),
            "links": self._analyze_links(),
            "media": self._analyze_media(),
            "meta_info": self._extract_meta_info(),
            "readability": self._calculate_readability()
        }

    def _analyze_dom(self) -> Dict[str, Any]:
        """Analyze DOM tree structure"""
        all_tags = self.soup.find_all()

        tag_counts = Counter(tag.name for tag in all_tags)

        # Calculate tree depth
        max_depth = 0
        for tag in all_tags:
            depth = len(list(tag.parents))
            max_depth = max(max_depth, depth)

        # Find repeated structures
        class_patterns = Counter()
        for tag in all_tags:
            if tag.get('class'):
                classes = ' '.join(tag['class'])
                class_patterns[classes] += 1

        return {
            "total_elements": len(all_tags),
            "tag_distribution": dict(tag_counts.most_common(20)),
            "max_depth": max_depth,
            "unique_classes": len(set(c for tag in all_tags if tag.get('class') for c in tag['class'])),
            "repeated_classes": {k: v for k, v in class_patterns.items() if v > 3}
        }

    def _detect_semantic_sections(self) -> List[Dict[str, Any]]:
        """Detect semantic HTML5 sections"""
        semantic_tags = ['header', 'nav', 'main', 'article', 'section', 'aside', 'footer']

        sections = []
        for tag_name in semantic_tags:
            elements = self.soup.find_all(tag_name)
            if elements:
                for idx, elem in enumerate(elements):
                    sections.append({
                        "type": tag_name,
                        "index": idx,
                        "has_heading": bool(elem.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
                        "child_count": len(elem.find_all()),
                        "text_length": len(elem.get_text(strip=True)),
                        "classes": elem.get('class', []),
                        "id": elem.get('id')
                    })

        return sections

    def _extract_tables(self) -> List[Dict[str, Any]]:
        """Extract and analyze data tables"""
        tables = []

        for idx, table in enumerate(self.soup.find_all('table')):
            headers = []
            rows = []

            # Extract headers
            thead = table.find('thead')
            if thead:
                header_row = thead.find('tr')
                if header_row:
                    headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]

            # If no thead, try first row
            if not headers:
                first_row = table.find('tr')
                if first_row:
                    headers = [th.get_text(strip=True) for th in first_row.find_all('th')]

            # Extract data rows
            tbody = table.find('tbody') or table
            for row in tbody.find_all('tr'):
                cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                if cells and cells != headers:  # Skip header row if included in tbody
                    rows.append(cells)

            tables.append({
                "index": idx,
                "headers": headers,
                "row_count": len(rows),
                "column_count": len(headers) if headers else (len(rows[0]) if rows else 0),
                "sample_rows": rows[:3],  # First 3 rows as sample
                "has_thead": bool(thead),
                "classes": table.get('class', []),
                "id": table.get('id')
            })

        return tables

    def _analyze_forms(self) -> List[Dict[str, Any]]:
        """Analyze form structures"""
        forms = []

        for idx, form in enumerate(self.soup.find_all('form')):
            fields = []

            # Extract all input fields
            for input_elem in form.find_all(['input', 'textarea', 'select']):
                field_info = {
                    "type": input_elem.name,
                    "name": input_elem.get('name'),
                    "id": input_elem.get('id'),
                    "required": input_elem.get('required') is not None,
                    "placeholder": input_elem.get('placeholder')
                }

                if input_elem.name == 'input':
                    field_info["input_type"] = input_elem.get('type', 'text')
                elif input_elem.name == 'select':
                    options = [opt.get_text(strip=True) for opt in input_elem.find_all('option')]
                    field_info["options"] = options[:10]  # First 10 options

                fields.append(field_info)

            forms.append({
                "index": idx,
                "action": form.get('action'),
                "method": form.get('method', 'get').upper(),
                "field_count": len(fields),
                "fields": fields,
                "has_submit": bool(form.find(['button', 'input'], type='submit')),
                "classes": form.get('class', []),
                "id": form.get('id')
            })

        return forms

    def _analyze_links(self) -> Dict[str, Any]:
        """Analyze link structure"""
        links = self.soup.find_all('a', href=True)

        internal_links = []
        external_links = []
        anchor_links = []

        for link in links:
            href = link['href']
            text = link.get_text(strip=True)

            if href.startswith('#'):
                anchor_links.append({"href": href, "text": text})
            elif href.startswith('http://') or href.startswith('https://'):
                external_links.append({"href": href, "text": text})
            else:
                internal_links.append({"href": href, "text": text})

        return {
            "total": len(links),
            "internal": len(internal_links),
            "external": len(external_links),
            "anchors": len(anchor_links),
            "external_domains": list(set(self._extract_domain(link["href"]) for link in external_links)),
            "sample_internal": internal_links[:5],
            "sample_external": external_links[:5]
        }

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        match = re.match(r'https?://([^/]+)', url)
        return match.group(1) if match else url

    def _analyze_media(self) -> Dict[str, Any]:
        """Analyze media elements"""
        images = self.soup.find_all('img')
        videos = self.soup.find_all('video')
        audios = self.soup.find_all('audio')

        return {
            "images": {
                "count": len(images),
                "with_alt": sum(1 for img in images if img.get('alt')),
                "formats": list(set(self._get_file_extension(img.get('src', '')) for img in images if img.get('src'))),
                "sample": [{"src": img.get('src'), "alt": img.get('alt')} for img in images[:3]]
            },
            "videos": {
                "count": len(videos),
                "sources": [video.get('src') for video in videos if video.get('src')][:3]
            },
            "audios": {
                "count": len(audios),
                "sources": [audio.get('src') for audio in audios if audio.get('src')][:3]
            }
        }

    def _get_file_extension(self, url: str) -> str:
        """Extract file extension from URL"""
        match = re.search(r'\.([a-zA-Z0-9]+)(?:\?|$)', url)
        return match.group(1).lower() if match else 'unknown'

    def _extract_meta_info(self) -> Dict[str, Any]:
        """Extract meta information"""
        meta_info = {
            "title": self.soup.title.string if self.soup.title else None,
            "description": None,
            "keywords": None,
            "author": None,
            "og_tags": {},
            "twitter_tags": {},
            "other_meta": []
        }

        for meta in self.soup.find_all('meta'):
            name = meta.get('name', '').lower()
            property_val = meta.get('property', '').lower()
            content = meta.get('content', '')

            if name == 'description':
                meta_info["description"] = content
            elif name == 'keywords':
                meta_info["keywords"] = content
            elif name == 'author':
                meta_info["author"] = content
            elif property_val.startswith('og:'):
                meta_info["og_tags"][property_val] = content
            elif name.startswith('twitter:'):
                meta_info["twitter_tags"][name] = content
            elif content:
                meta_info["other_meta"].append({"name": name or property_val, "content": content[:100]})

        return meta_info

    def _calculate_readability(self) -> Dict[str, Any]:
        """Calculate content readability metrics"""
        # Get all text content
        text = self.soup.get_text()

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Count elements
        word_count = len(text.split())
        char_count = len(text)
        sentence_count = len(re.findall(r'[.!?]+', text))

        # Count paragraphs
        paragraphs = self.soup.find_all('p')
        para_count = len(paragraphs)

        # Heading hierarchy
        headings = {
            'h1': len(self.soup.find_all('h1')),
            'h2': len(self.soup.find_all('h2')),
            'h3': len(self.soup.find_all('h3')),
            'h4': len(self.soup.find_all('h4')),
            'h5': len(self.soup.find_all('h5')),
            'h6': len(self.soup.find_all('h6'))
        }

        return {
            "word_count": word_count,
            "char_count": char_count,
            "sentence_count": sentence_count if sentence_count > 0 else 1,
            "paragraph_count": para_count,
            "avg_words_per_sentence": word_count / sentence_count if sentence_count > 0 else 0,
            "avg_words_per_paragraph": word_count / para_count if para_count > 0 else 0,
            "heading_distribution": headings,
            "has_proper_hierarchy": headings['h1'] > 0
        }

    def find_data_patterns(self) -> List[Dict[str, Any]]:
        """
        Find repeating data patterns (potential list items, products, articles)

        Returns:
            List of detected patterns with selectors
        """
        patterns = []

        # Common container patterns
        container_selectors = [
            ('div', re.compile(r'(item|product|card|article|post|entry)', re.I)),
            ('li', re.compile(r'(item|product|result)', re.I)),
            ('article', None),
            ('tr', None)
        ]

        for tag_name, class_pattern in container_selectors:
            if class_pattern:
                containers = self.soup.find_all(tag_name, class_=class_pattern)
            else:
                containers = self.soup.find_all(tag_name)

            # Group by similar structure
            structure_groups = {}
            for container in containers:
                # Create structure signature
                signature = self._get_structure_signature(container)
                if signature not in structure_groups:
                    structure_groups[signature] = []
                structure_groups[signature].append(container)

            # Report groups with 3+ similar elements
            for signature, group in structure_groups.items():
                if len(group) >= 3:
                    first_elem = group[0]
                    patterns.append({
                        "tag": tag_name,
                        "class": first_elem.get('class', []),
                        "count": len(group),
                        "structure_signature": signature,
                        "sample_content": self._extract_sample_content(first_elem),
                        "css_selector": self._generate_css_selector(first_elem)
                    })

        return patterns

    def _get_structure_signature(self, elem: Tag) -> str:
        """Generate structure signature for grouping similar elements"""
        child_tags = [child.name for child in elem.find_all() if isinstance(child, Tag)]
        return ','.join(sorted(set(child_tags)))

    def _extract_sample_content(self, elem: Tag) -> Dict[str, Any]:
        """Extract sample content from element"""
        return {
            "headings": [h.get_text(strip=True)[:50] for h in elem.find_all(['h1', 'h2', 'h3', 'h4'])[:2]],
            "links": [{"text": a.get_text(strip=True)[:30], "href": a.get('href')} for a in elem.find_all('a', href=True)[:2]],
            "images": [img.get('src') for img in elem.find_all('img', src=True)[:2]],
            "text_sample": elem.get_text(strip=True)[:100]
        }

    def _generate_css_selector(self, elem: Tag) -> str:
        """Generate CSS selector for element"""
        selector_parts = [elem.name]

        if elem.get('id'):
            selector_parts.append(f"#{elem['id']}")
        elif elem.get('class'):
            selector_parts.append('.' + '.'.join(elem['class'][:2]))

        return ''.join(selector_parts)

    def extract_json_ld(self) -> List[Dict[str, Any]]:
        """Extract JSON-LD structured data"""
        import json

        json_ld_scripts = self.soup.find_all('script', type='application/ld+json')

        structured_data = []
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                structured_data.append(data)
            except (json.JSONDecodeError, AttributeError):
                pass

        return structured_data
