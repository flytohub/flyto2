#!/usr/bin/env python3
"""
Deployment History Manager for Level 4 Self-Evolving System

Manages:
- Module version tracking
- Deployment history
- Snapshot backups
- Rollback operations
"""
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class DeploymentManager:
    """Manages module deployments, snapshots, and rollbacks"""

    def __init__(
        self,
        history_file: str = "metrics/module_deployment_history.json",
        snapshots_dir: str = "metrics/snapshots"
    ):
        self.history_file = Path(history_file)
        self.snapshots_dir = Path(snapshots_dir)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

    def load_history(self) -> Dict[str, Any]:
        """Load deployment history"""
        if not self.history_file.exists():
            return {
                "modules": {},
                "global_stats": {
                    "total_deployments": 0,
                    "ai_deployments": 0,
                    "human_deployments": 0,
                    "successful_deployments": 0,
                    "rollbacks": 0,
                    "rollback_rate": 0.0
                }
            }

        with open(self.history_file) as f:
            return json.load(f)

    def save_history(self, history: Dict[str, Any]):
        """Save deployment history"""
        history['_last_updated'] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)

    def get_git_commit_hash(self) -> str:
        """Get current git commit hash"""
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()

    def get_module_version(self, module_id: str, file_path: str) -> str:
        """Extract version from module file"""
        # Read module file and find @register_module decorator
        with open(file_path) as f:
            content = f.read()

        # Simple regex to find version in decorator
        import re
        match = re.search(r'version=["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
        return "1.0.0"  # Default version

    def create_snapshot(
        self,
        module_id: str,
        file_path: str,
        version: str,
        commit: str
    ) -> str:
        """Create snapshot backup of module file"""
        # Create module-specific snapshot directory
        module_snapshot_dir = self.snapshots_dir / module_id.replace('.', '_')
        module_snapshot_dir.mkdir(parents=True, exist_ok=True)

        # Create snapshot filename: version_commit.py
        snapshot_filename = f"{version}_{commit}.py"
        snapshot_path = module_snapshot_dir / snapshot_filename

        # Copy file to snapshot
        shutil.copy2(file_path, snapshot_path)

        return str(snapshot_path)

    def record_deployment(
        self,
        module_id: str,
        file_path: str,
        deployed_by: str,  # "ai_agent" or "human"
        pre_deploy_pass_rate: float,
        post_deploy_pass_rate: Optional[float] = None,
        status: str = "active"
    ) -> Dict[str, Any]:
        """Record a new deployment"""
        history = self.load_history()

        # Get version and commit info
        version = self.get_module_version(module_id, file_path)
        commit = self.get_git_commit_hash()

        # Create snapshot
        snapshot_path = self.create_snapshot(module_id, file_path, version, commit)

        # Get previous version if exists
        previous_version = None
        if module_id in history['modules']:
            deployments = history['modules'][module_id].get('deployment_history', [])
            if deployments:
                previous_version = deployments[0]['version']

        # Create deployment record
        deployment_record = {
            "version": version,
            "commit": commit,
            "deployed_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "deployed_by": deployed_by,
            "pre_deploy_pass_rate": pre_deploy_pass_rate,
            "post_deploy_pass_rate": post_deploy_pass_rate,
            "status": status,
            "rollback_available": True,
            "previous_version": previous_version
        }

        # Initialize module if not exists
        if module_id not in history['modules']:
            history['modules'][module_id] = {
                "current_version": version,
                "current_commit": commit,
                "deployment_history": [],
                "snapshots": {}
            }

        # Update current version
        history['modules'][module_id]['current_version'] = version
        history['modules'][module_id]['current_commit'] = commit

        # Add to deployment history (prepend - newest first)
        history['modules'][module_id]['deployment_history'].insert(0, deployment_record)

        # Add snapshot info
        history['modules'][module_id]['snapshots'][version] = {
            "file_path": file_path,
            "backup_path": snapshot_path,
            "created_at": deployment_record['deployed_at']
        }

        # Update global stats
        history['global_stats']['total_deployments'] += 1
        if deployed_by == "ai_agent":
            history['global_stats']['ai_deployments'] += 1
        else:
            history['global_stats']['human_deployments'] += 1

        history['global_stats']['successful_deployments'] += 1
        history['global_stats']['last_deployment'] = deployment_record['deployed_at']

        # Calculate rollback rate
        total = history['global_stats']['total_deployments']
        rollbacks = history['global_stats']['rollbacks']
        history['global_stats']['rollback_rate'] = rollbacks / total if total > 0 else 0.0

        # Save history
        self.save_history(history)

        return deployment_record

    def get_rollback_target(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Get the version to rollback to"""
        history = self.load_history()

        if module_id not in history['modules']:
            return None

        deployments = history['modules'][module_id]['deployment_history']
        if len(deployments) < 2:
            return None  # No previous version to rollback to

        # Current is deployments[0], previous is deployments[1]
        previous = deployments[1]

        return {
            "version": previous['version'],
            "commit": previous['commit'],
            "snapshot_path": history['modules'][module_id]['snapshots'][previous['version']]['backup_path'],
            "module_file_path": history['modules'][module_id]['snapshots'][previous['version']]['file_path']
        }

    def execute_rollback(
        self,
        module_id: str,
        reason: str,
        current_pass_rate: float
    ) -> Dict[str, Any]:
        """Execute rollback to previous version"""
        history = self.load_history()

        # Get rollback target
        target = self.get_rollback_target(module_id)
        if not target:
            raise ValueError(f"No rollback target available for {module_id}")

        # Restore snapshot
        shutil.copy2(target['snapshot_path'], target['module_file_path'])

        # Create rollback record
        rollback_record = {
            "rolled_back_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "from_version": history['modules'][module_id]['current_version'],
            "to_version": target['version'],
            "reason": reason,
            "current_pass_rate": current_pass_rate
        }

        # Update deployment history
        current_deployment = history['modules'][module_id]['deployment_history'][0]
        current_deployment['status'] = 'rolled_back'
        current_deployment['rollback_record'] = rollback_record

        # Update current version
        history['modules'][module_id]['current_version'] = target['version']
        history['modules'][module_id]['current_commit'] = target['commit']

        # Update previous deployment status to active
        history['modules'][module_id]['deployment_history'][1]['status'] = 'active'

        # Update global stats
        history['global_stats']['rollbacks'] += 1
        history['global_stats']['last_rollback'] = rollback_record['rolled_back_at']

        # Recalculate rollback rate
        total = history['global_stats']['total_deployments']
        rollbacks = history['global_stats']['rollbacks']
        history['global_stats']['rollback_rate'] = rollbacks / total if total > 0 else 0.0

        # Save history
        self.save_history(history)

        return rollback_record

    def get_modules_in_monitoring_window(self, hours: int = 24) -> List[str]:
        """Get modules deployed within monitoring window"""
        history = self.load_history()
        now = datetime.utcnow()
        module_ids = []

        for module_id, module_data in history['modules'].items():
            deployments = module_data.get('deployment_history', [])
            if not deployments:
                continue

            latest = deployments[0]
            if latest['status'] != 'active':
                continue

            deployed_at = datetime.fromisoformat(latest['deployed_at'].replace('Z', '+00:00'))
            hours_since = (now - deployed_at.replace(tzinfo=None)).total_seconds() / 3600

            if hours_since <= hours:
                module_ids.append(module_id)

        return module_ids

    def update_post_deploy_pass_rate(
        self,
        module_id: str,
        pass_rate: float
    ):
        """Update post-deployment pass rate"""
        history = self.load_history()

        if module_id not in history['modules']:
            return

        deployments = history['modules'][module_id]['deployment_history']
        if deployments:
            deployments[0]['post_deploy_pass_rate'] = pass_rate

        self.save_history(history)

    def get_deployment_info(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Get current deployment info for a module"""
        history = self.load_history()

        if module_id not in history['modules']:
            return None

        module_data = history['modules'][module_id]
        deployments = module_data.get('deployment_history', [])

        if not deployments:
            return None

        return {
            "module_id": module_id,
            "current_version": module_data['current_version'],
            "current_commit": module_data['current_commit'],
            "latest_deployment": deployments[0],
            "total_deployments": len(deployments),
            "rollback_available": len(deployments) >= 2
        }

    def cleanup_old_snapshots(self, retention_days: int = 90):
        """Remove snapshots older than retention period"""
        history = self.load_history()
        now = datetime.utcnow()
        removed_count = 0

        for module_id, module_data in history['modules'].items():
            snapshots = module_data.get('snapshots', {})
            versions_to_remove = []

            for version, snapshot_info in snapshots.items():
                created_at = datetime.fromisoformat(
                    snapshot_info['created_at'].replace('Z', '+00:00')
                )
                days_old = (now - created_at.replace(tzinfo=None)).days

                if days_old > retention_days:
                    # Remove snapshot file
                    snapshot_path = Path(snapshot_info['backup_path'])
                    if snapshot_path.exists():
                        snapshot_path.unlink()
                        removed_count += 1

                    versions_to_remove.append(version)

            # Remove from history
            for version in versions_to_remove:
                del snapshots[version]

        self.save_history(history)
        return removed_count


def main():
    """CLI interface for deployment manager"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python scripts/deployment_manager.py <command> [args]")
        print("\nCommands:")
        print("  record <module_id> <file_path> <deployed_by> <pass_rate>")
        print("  rollback <module_id> <reason> <current_pass_rate>")
        print("  info <module_id>")
        print("  monitoring-window [hours]")
        print("  cleanup [retention_days]")
        sys.exit(1)

    manager = DeploymentManager()
    command = sys.argv[1]

    if command == "record":
        module_id = sys.argv[2]
        file_path = sys.argv[3]
        deployed_by = sys.argv[4]
        pass_rate = float(sys.argv[5])

        record = manager.record_deployment(
            module_id, file_path, deployed_by, pass_rate
        )
        print(json.dumps(record, indent=2))

    elif command == "rollback":
        module_id = sys.argv[2]
        reason = sys.argv[3]
        current_pass_rate = float(sys.argv[4])

        record = manager.execute_rollback(module_id, reason, current_pass_rate)
        print(json.dumps(record, indent=2))

    elif command == "info":
        module_id = sys.argv[2]
        info = manager.get_deployment_info(module_id)
        print(json.dumps(info, indent=2))

    elif command == "monitoring-window":
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        modules = manager.get_modules_in_monitoring_window(hours)
        print(json.dumps(modules, indent=2))

    elif command == "cleanup":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 90
        removed = manager.cleanup_old_snapshots(days)
        print(f"Removed {removed} old snapshots")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
