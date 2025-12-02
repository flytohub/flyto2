#!/usr/bin/env python3
"""
Scheduled Tasks Runner

Runs periodic maintenance tasks:
- Debug analysis
- Module catalog update
- System health check
"""

import sys
import asyncio
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


async def run_debug_analysis(hours: int = 24):
    """Run system debug analysis"""
    from src.core.evolution import get_debug_engine

    print(f"[{datetime.now()}] Running debug analysis (last {hours}h)...")

    try:
        engine = get_debug_engine()
        report = await engine.analyze_system_health(hours=hours)

        health_score = report.get('health_score', 0)
        priority_issues = report.get('priority_issues', [])

        print(f"  Health Score: {health_score:.1f}/100")
        print(f"  Priority Issues: {len(priority_issues)}")

        if priority_issues:
            print(f"  Top Issues:")
            for issue in priority_issues[:3]:
                sig = issue.get('signature', 'unknown')[:30]
                count = issue.get('count', 0)
                print(f"    - {sig}: {count} occurrences")

        return True

    except Exception as e:
        print(f"  Error: {e}")
        return False


def update_module_catalog():
    """Update module catalog"""
    from src.core.modules.registry import get_catalog_manager

    print(f"[{datetime.now()}] Updating module catalog...")

    try:
        catalog = get_catalog_manager()

        # Export catalog
        catalog.export_to_json_file("modules/catalog.json", lang='en')

        stats = catalog.get_statistics()
        print(f"  Total Modules: {stats.get('total_modules', 0)}")
        print(f"  Last Updated: {stats.get('last_updated', 'unknown')}")

        return True

    except Exception as e:
        print(f"  Error: {e}")
        return False


async def check_evolution_tickets():
    """Check active evolution tickets"""
    from src.core.evolution import get_evolution_orchestrator

    print(f"[{datetime.now()}] Checking evolution tickets...")

    try:
        orchestrator = get_evolution_orchestrator()

        # List recent tickets
        tickets = orchestrator.list_tickets(limit=10)

        print(f"  Recent Tickets: {len(tickets)}")

        if tickets:
            # Count by status
            status_counts = {}
            for ticket in tickets:
                status = ticket.status.value
                status_counts[status] = status_counts.get(status, 0) + 1

            for status, count in status_counts.items():
                print(f"    {status}: {count}")

        return True

    except Exception as e:
        print(f"  Error: {e}")
        return False


async def main():
    parser = argparse.ArgumentParser(description='Run scheduled maintenance tasks')
    parser.add_argument(
        '--task',
        choices=['debug', 'catalog', 'tickets', 'all'],
        default='all',
        help='Task to run'
    )
    parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='Hours for debug analysis (default: 24)'
    )

    args = parser.parse_args()

    print("=" * 50)
    print("Flyto2 Scheduled Tasks")
    print("=" * 50)
    print()

    success = True

    if args.task in ['debug', 'all']:
        success = success and await run_debug_analysis(args.hours)
        print()

    if args.task in ['catalog', 'all']:
        success = success and update_module_catalog()
        print()

    if args.task in ['tickets', 'all']:
        success = success and await check_evolution_tickets()
        print()

    print("=" * 50)
    if success:
        print("All tasks completed successfully")
    else:
        print("Some tasks failed")

    return 0 if success else 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
