"""
Startup Hooks - Initialize systems on Flyto2 startup

Runs:
1. Self-Awareness System (ingest implementation guides)
2. Module Catalog refresh
3. Health checks
"""

import asyncio
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


async def run_all_startup_hooks():
    """Run all startup hooks in sequence"""
    logger.info("🚀 Running startup hooks...")

    hooks = [
        ("Self-Awareness System", init_self_awareness),
        ("Module Catalog", refresh_module_catalog),
        ("System Health Check", run_health_check)
    ]

    for name, hook_func in hooks:
        try:
            logger.info(f"  ▸ {name}...")
            await hook_func()
            logger.info(f"  ✓ {name} ready")
        except Exception as e:
            logger.error(f"  ✗ {name} failed: {e}")

    logger.info("✅ All startup hooks complete\n")


async def init_self_awareness():
    """Initialize self-awareness system with implementation guides"""
    from src.core.knowledge.doc_ingestion import get_self_awareness

    system = get_self_awareness()
    await system.initialize()


async def refresh_module_catalog():
    """Refresh module catalog"""
    try:
        from src.core.catalog.catalog_manager import get_catalog_manager

        catalog = get_catalog_manager()
        await catalog.refresh()
    except Exception as e:
        logger.warning(f"Module catalog not available: {e}")


async def run_health_check():
    """Run basic health checks"""
    # Check Qdrant connection
    try:
        from src.core.knowledge.knowledge_store import KnowledgeStore

        store = KnowledgeStore()
        # Basic connectivity check
        # await store.health_check()
    except Exception as e:
        logger.warning(f"VectorDB health check failed: {e}")


# Entry point for main.py or CLI
if __name__ == "__main__":
    asyncio.run(run_all_startup_hooks())
