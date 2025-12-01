#!/usr/bin/env python3
"""
Add last_stable and allow_auto_rollback fields to all modules in module_quality.json
"""
import json
import subprocess
from pathlib import Path


def get_current_commit():
    """Get current git commit hash"""
    result = subprocess.run(
        ['git', 'rev-parse', '--short', 'HEAD'],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout.strip()


def main():
    metrics_file = Path("metrics/module_quality.json")

    # Load metrics
    with open(metrics_file) as f:
        metrics = json.load(f)

    current_commit = get_current_commit()

    # Update each module
    for module_id, module_data in metrics['modules'].items():
        # Add allow_auto_rollback if not exists
        if 'allow_auto_rollback' not in module_data:
            module_data['allow_auto_rollback'] = True

        # Add last_stable if not exists
        if 'last_stable' not in module_data:
            module_data['last_stable'] = {
                "commit_sha": current_commit,
                "pr_number": None,
                "baseline_pass_rate_at_merge": module_data.get('recent_pass_rate', 1.0),
                "merged_at": module_data.get('last_tested', '2025-12-01T00:43:00Z')
            }

    # Save updated metrics
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"Updated {len(metrics['modules'])} modules")
    print(f"Current commit: {current_commit}")
    print("\nAdded fields:")
    print("  - allow_auto_rollback (default: true)")
    print("  - last_stable.commit_sha")
    print("  - last_stable.pr_number")
    print("  - last_stable.baseline_pass_rate_at_merge")
    print("  - last_stable.merged_at")


if __name__ == '__main__':
    main()
