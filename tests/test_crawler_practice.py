#!/usr/bin/env python
"""
Crawler Practice Test - Test existing crawler with real websites
"""
import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.training.daily_practice import DailyPracticeEngine


async def test_crawler_on_real_sites():
    """Test crawler on real websites"""

    print("=" * 70)
    print("CRAWLER PRACTICE TEST")
    print("=" * 70)
    print()

    engine = DailyPracticeEngine()

    # Test sites (start with simple ones)
    test_sites = [
        "https://example.com",  # Very simple
        "https://httpbin.org/html",  # Test HTML
        "https://books.toscrape.com",  # Practice scraping site
    ]

    for i, url in enumerate(test_sites, 1):
        print(f"{i}. Testing: {url}")
        print("-" * 70)

        try:
            # Analyze website
            analysis = await engine.analyze_website(url)

            print(f"   Status: {'✅ SUCCESS' if not analysis['errors'] else '❌ ERRORS'}")
            print(f"   Title: {analysis['structure'].get('title', 'N/A')}")
            print(f"   Robots.txt: {analysis['robots_txt'].get('status', 'N/A')}")

            if analysis['errors']:
                print(f"   Errors:")
                for error in analysis['errors']:
                    print(f"     - {error}")

            if analysis['recommendations']:
                print(f"   Recommendations:")
                for rec in analysis['recommendations'][:3]:
                    print(f"     - {rec}")

            print()

        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)}")
            print()

    print("=" * 70)
    print("Practice completed! Check metrics/daily_practice.json")
    print("=" * 70)


if __name__ == '__main__':
    asyncio.run(test_crawler_on_real_sites())
