"""
Auto-Sync Knowledge Base
Automatically updates vector database when project files change

Supports:
- File watcher mode (real-time updates)
- Scheduled mode (periodic updates)
- Git hook mode (on commit/push)
- Incremental updates (only changed files)
"""
import sys
import time
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Set, Dict, Any
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.modules.atomic.vector import (
    VectorDBConnector,
    KnowledgeStore,
    ExperienceArchiver
)


class KnowledgeSyncer:
    """
    Automatically syncs project knowledge to vector database
    """

    def __init__(
        self,
        collection_name: str = "flyto2_project_knowledge",
        embedding_provider: str = "local"
    ):
        """
        Initialize syncer

        Args:
            collection_name: Vector DB collection name
            embedding_provider: Embedding provider
        """
        self.collection_name = collection_name
        self.embedding_provider = embedding_provider
        self.state_file = project_root / ".knowledge_sync_state.json"
        self.file_hashes = self.load_state()

    def load_state(self) -> Dict[str, str]:
        """Load last sync state"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {}

    def save_state(self):
        """Save sync state"""
        with open(self.state_file, 'w') as f:
            json.dump(self.file_hashes, f, indent=2)

    def get_file_hash(self, file_path: Path) -> str:
        """Get file content hash"""
        try:
            content = file_path.read_bytes()
            return hashlib.md5(content).hexdigest()
        except Exception:
            return ""

    def get_monitored_files(self) -> Set[Path]:
        """Get list of files to monitor"""
        files = set()

        # Documentation
        for pattern in ["*.md", "*.txt"]:
            files.update(project_root.glob(pattern))

        # Module files
        module_dirs = [
            project_root / "src/core/modules/atomic",
            project_root / "src/core/training",
            project_root / "src/core/competition",
            project_root / "src/core/modules"
        ]

        for module_dir in module_dirs:
            if module_dir.exists():
                files.update(module_dir.rglob("*.py"))

        return files

    def detect_changes(self) -> Set[Path]:
        """Detect changed files since last sync"""
        changed = set()
        current_files = self.get_monitored_files()

        for file_path in current_files:
            current_hash = self.get_file_hash(file_path)
            old_hash = self.file_hashes.get(str(file_path))

            if current_hash != old_hash:
                changed.add(file_path)
                self.file_hashes[str(file_path)] = current_hash

        return changed

    def sync_incremental(self) -> Dict[str, Any]:
        """
        Sync only changed files

        Returns:
            Sync statistics
        """
        print("🔍 Detecting changes...")
        changed_files = self.detect_changes()

        if not changed_files:
            print("✓ No changes detected")
            return {"status": "no_changes", "files_changed": 0}

        print(f"📝 Found {len(changed_files)} changed files")

        # Connect to vector DB
        connector = VectorDBConnector(mode="local")
        connector.connect()

        store = KnowledgeStore(
            connector=connector,
            collection_name=self.collection_name,
            embedding_provider=self.embedding_provider
        )

        archiver = ExperienceArchiver(store)

        # Process each changed file
        new_entries = 0

        for file_path in changed_files:
            try:
                relative_path = file_path.relative_to(project_root)
                print(f"  → {relative_path}")

                # Archive as module improvement
                archiver.archive_module_improvement(
                    module_id=str(relative_path),
                    version=datetime.now().strftime("%Y.%m.%d"),
                    changes=f"Updated {file_path.name}",
                    impact="Project file updated"
                )

                new_entries += 1

            except Exception as e:
                print(f"  ✗ Error processing {file_path}: {e}")
                continue

        # Save state
        self.save_state()

        connector.disconnect()

        print(f"✓ Synced {new_entries} entries")

        return {
            "status": "success",
            "files_changed": len(changed_files),
            "entries_added": new_entries,
            "timestamp": datetime.now().isoformat()
        }

    def sync_full(self) -> Dict[str, Any]:
        """
        Full re-aggregation of all project knowledge

        Returns:
            Sync statistics
        """
        print("🔄 Running full knowledge aggregation...")

        # Run the full aggregation script
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                str(project_root / "scripts/aggregate_project_knowledge.py"),
                "--mode", "local",
                "--embeddings", self.embedding_provider
            ],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✓ Full aggregation complete")

            # Update all file hashes
            for file_path in self.get_monitored_files():
                self.file_hashes[str(file_path)] = self.get_file_hash(file_path)

            self.save_state()

            return {
                "status": "success",
                "type": "full",
                "timestamp": datetime.now().isoformat()
            }
        else:
            print(f"✗ Aggregation failed: {result.stderr}")
            return {"status": "error", "error": result.stderr}


class FileWatcher:
    """
    Watch files for changes and auto-sync
    """

    def __init__(self, syncer: KnowledgeSyncer, interval: int = 60):
        """
        Initialize file watcher

        Args:
            syncer: KnowledgeSyncer instance
            interval: Check interval in seconds
        """
        self.syncer = syncer
        self.interval = interval

    def start(self):
        """Start watching for changes"""
        print("=" * 60)
        print("Knowledge Base Auto-Sync (File Watcher Mode)")
        print("=" * 60)
        print(f"Checking for changes every {self.interval} seconds")
        print("Press Ctrl+C to stop")
        print("-" * 60)

        try:
            while True:
                self.syncer.sync_incremental()
                time.sleep(self.interval)

        except KeyboardInterrupt:
            print("\n\n✓ File watcher stopped")


def scheduled_sync(syncer: KnowledgeSyncer, mode: str = "incremental"):
    """
    Run scheduled sync (called by cron/task scheduler)

    Args:
        syncer: KnowledgeSyncer instance
        mode: 'incremental' or 'full'
    """
    print(f"🕐 Scheduled sync ({mode}) - {datetime.now()}")

    if mode == "full":
        result = syncer.sync_full()
    else:
        result = syncer.sync_incremental()

    print(f"✓ Sync complete: {result}")

    # Log to file
    log_file = project_root / "logs/knowledge_sync.log"
    log_file.parent.mkdir(exist_ok=True)

    with open(log_file, 'a') as f:
        f.write(f"{datetime.now().isoformat()} - {mode}: {result}\n")


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description="Auto-sync project knowledge to vector database"
    )
    parser.add_argument(
        "--mode",
        choices=["watch", "incremental", "full", "scheduled"],
        default="incremental",
        help="Sync mode"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Watch interval in seconds (watch mode only)"
    )
    parser.add_argument(
        "--embeddings",
        choices=["local", "ollama", "openai"],
        default="local",
        help="Embedding provider"
    )

    args = parser.parse_args()

    syncer = KnowledgeSyncer(embedding_provider=args.embeddings)

    if args.mode == "watch":
        # File watcher mode (real-time)
        watcher = FileWatcher(syncer, interval=args.interval)
        watcher.start()

    elif args.mode == "incremental":
        # Incremental sync (only changed files)
        result = syncer.sync_incremental()
        print(f"\nResult: {json.dumps(result, indent=2)}")

    elif args.mode == "full":
        # Full re-aggregation
        result = syncer.sync_full()
        print(f"\nResult: {json.dumps(result, indent=2)}")

    elif args.mode == "scheduled":
        # Scheduled sync (called by cron/task scheduler)
        scheduled_sync(syncer, mode="incremental")


if __name__ == "__main__":
    main()
