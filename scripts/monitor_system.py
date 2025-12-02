#!/usr/bin/env python3
"""
System Monitor for Flyto2 V4

Monitors key system metrics and health indicators.
"""

import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class SystemMonitor:
    """Monitor system health and metrics"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.metrics = {}

    async def collect_metrics(self) -> Dict[str, Any]:
        """Collect all system metrics"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "errors": await self._get_error_metrics(),
            "evolution": await self._get_evolution_metrics(),
            "modules": self._get_module_metrics(),
            "system": self._get_system_metrics()
        }

        self.metrics = metrics
        return metrics

    async def _get_error_metrics(self) -> Dict[str, Any]:
        """Get error statistics"""
        try:
            from src.core.evolution import get_error_center

            error_center = get_error_center()
            stats = error_center.get_error_statistics(hours=24)

            return {
                "total_errors_24h": stats.get('total_errors', 0),
                "unique_signatures": len(stats.get('error_by_signature', {})),
                "error_rate": stats.get('total_errors', 0) / 24.0,
                "top_errors": stats.get('most_common_errors', [])[:3]
            }
        except Exception as e:
            return {"error": str(e)}

    async def _get_evolution_metrics(self) -> Dict[str, Any]:
        """Get evolution pipeline metrics"""
        try:
            from src.core.evolution import get_evolution_orchestrator

            orchestrator = get_evolution_orchestrator()
            tickets = orchestrator.list_tickets(limit=50)

            # Count by status
            status_counts = {}
            for ticket in tickets:
                status = ticket.status.value
                status_counts[status] = status_counts.get(status, 0) + 1

            return {
                "total_tickets": len(tickets),
                "by_status": status_counts,
                "recent_tickets": len([t for t in tickets[:10]])
            }
        except Exception as e:
            return {"error": str(e)}

    def _get_module_metrics(self) -> Dict[str, Any]:
        """Get module catalog metrics"""
        try:
            from src.core.modules.registry import get_catalog_manager

            catalog = get_catalog_manager()
            stats = catalog.get_statistics()

            return {
                "total_modules": stats.get('total_modules', 0),
                "by_category": stats.get('by_category', {}),
                "by_status": stats.get('by_status', {})
            }
        except Exception as e:
            return {"error": str(e)}

    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system-level metrics"""
        metrics = {}

        # Try to get psutil metrics
        try:
            import psutil
            metrics["cpu_percent"] = psutil.cpu_percent(interval=1)
            metrics["memory_percent"] = psutil.virtual_memory().percent
            metrics["disk_percent"] = psutil.disk_usage('/').percent
        except ImportError:
            metrics["psutil_status"] = "not installed"
        except Exception as e:
            metrics["psutil_error"] = str(e)

        # Always check Ollama health (independent of psutil)
        metrics["ollama_status"] = self._check_ollama_health()

        return metrics

    def _check_ollama_health(self) -> Dict[str, Any]:
        """Check Ollama service health"""
        try:
            from src.core.utils.http_client import HTTPClient
            import requests
            import os

            # Force fresh check
            HTTPClient.reset_ollama_check()
            is_available = HTTPClient.check_ollama_available()

            if is_available:
                # Get more detailed info
                ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
                try:
                    response = requests.get(f"{ollama_url}/api/tags", timeout=2)
                    models = response.json().get('models', [])
                    return {
                        "status": "healthy",
                        "url": ollama_url,
                        "models_count": len(models),
                        "models": [m.get('name', 'unknown') for m in models[:3]]
                    }
                except Exception as e:
                    return {
                        "status": "available_but_error",
                        "url": ollama_url,
                        "error": str(e)
                    }
            else:
                ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
                return {
                    "status": "unavailable",
                    "url": ollama_url,
                    "message": "Ollama service not running or unreachable"
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def print_summary(self):
        """Print metrics summary"""
        if not self.metrics:
            print("No metrics collected")
            return

        print("=" * 60)
        print(f"Flyto2 System Monitor - {self.metrics['timestamp']}")
        print("=" * 60)
        print()

        # Errors
        errors = self.metrics.get('errors', {})
        if 'error' not in errors:
            print("ERRORS (24h)")
            print(f"  Total: {errors.get('total_errors_24h', 0)}")
            print(f"  Unique: {errors.get('unique_signatures', 0)}")
            print(f"  Rate: {errors.get('error_rate', 0):.2f}/hour")

            top_errors = errors.get('top_errors', [])
            if top_errors:
                print(f"  Top Issues:")
                for sig, count in top_errors:
                    print(f"    - {sig[:30]}: {count}")
        else:
            print(f"ERRORS: {errors['error']}")
        print()

        # Evolution
        evolution = self.metrics.get('evolution', {})
        if 'error' not in evolution:
            print("EVOLUTION PIPELINE")
            print(f"  Total Tickets: {evolution.get('total_tickets', 0)}")

            status_counts = evolution.get('by_status', {})
            if status_counts:
                print(f"  By Status:")
                for status, count in status_counts.items():
                    print(f"    {status}: {count}")
        else:
            print(f"EVOLUTION: {evolution['error']}")
        print()

        # Modules
        modules = self.metrics.get('modules', {})
        if 'error' not in modules:
            print("MODULES")
            print(f"  Total: {modules.get('total_modules', 0)}")

            by_category = modules.get('by_category', {})
            if by_category:
                print(f"  Top Categories:")
                for cat, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"    {cat}: {count}")
        else:
            print(f"MODULES: {modules['error']}")
        print()

        # System
        system = self.metrics.get('system', {})
        print("SYSTEM RESOURCES")

        # CPU, Memory, Disk (if psutil available)
        if 'cpu_percent' in system:
            print(f"  CPU: {system.get('cpu_percent', 0):.1f}%")
            print(f"  Memory: {system.get('memory_percent', 0):.1f}%")
            print(f"  Disk: {system.get('disk_percent', 0):.1f}%")
        elif 'psutil_status' in system:
            print(f"  psutil: {system['psutil_status']}")

        # Ollama status (always show)
        ollama = system.get('ollama_status', {})
        if ollama:
            status = ollama.get('status', 'unknown')
            if status == 'healthy':
                print(f"  Ollama: OK ({ollama.get('models_count', 0)} models)")
                if ollama.get('models'):
                    print(f"    Models: {', '.join(ollama['models'])}")
            elif status == 'unavailable':
                print("  Ollama: NOT RUNNING")
            else:
                print(f"  Ollama: {status}")
                if 'error' in ollama:
                    print(f"    Error: {ollama['error']}")
        print()

        print("=" * 60)

    def save_metrics(self, filepath: str = "logs/metrics.jsonl"):
        """Save metrics to JSONL file"""
        if not self.metrics:
            return

        metrics_file = self.project_root / filepath
        metrics_file.parent.mkdir(parents=True, exist_ok=True)

        with open(metrics_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(self.metrics) + '\n')


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Monitor Flyto2 system health')
    parser.add_argument(
        '--save',
        action='store_true',
        help='Save metrics to logs/metrics.jsonl'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output JSON instead of summary'
    )

    args = parser.parse_args()

    monitor = SystemMonitor()

    print("Collecting metrics...")
    metrics = await monitor.collect_metrics()

    if args.json:
        print(json.dumps(metrics, indent=2))
    else:
        monitor.print_summary()

    if args.save:
        monitor.save_metrics()
        print("Metrics saved to logs/metrics.jsonl")

    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
