#!/usr/bin/env python3
"""
Safety Manager for Flyto2 Level 4 Self-Evolving System

Enforces safety boundaries:
- Kill switch
- Module blacklist/whitelist
- Rate limiting
- Human review requirements
"""
import json
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class SafetyManager:
    """Manages safety controls for AI automation"""

    def __init__(self, config_path: str = "config/safety.yaml"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.rate_limit_tracker_file = Path("metrics/rate_limits.json")

    def load_config(self) -> Dict:
        """Load safety configuration"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Safety config not found: {self.config_path}")

        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def reload_config(self):
        """Reload configuration (for live updates)"""
        self.config = self.load_config()

    # ============================================
    # Kill Switch
    # ============================================

    def is_automation_enabled(self) -> bool:
        """Check if AI automation is globally enabled"""
        return self.config['kill_switch']['ai_automation_enabled']

    def is_auto_merge_enabled(self) -> bool:
        """Check if auto-merge is enabled"""
        return (
            self.config['kill_switch']['ai_automation_enabled'] and
            self.config['kill_switch']['auto_merge_enabled']
        )

    def is_auto_rollback_enabled(self) -> bool:
        """Check if auto-rollback is enabled"""
        return (
            self.config['kill_switch']['ai_automation_enabled'] and
            self.config['kill_switch']['auto_rollback_enabled']
        )

    def is_continuous_improvement_enabled(self) -> bool:
        """Check if continuous improvement is enabled"""
        return (
            self.config['kill_switch']['ai_automation_enabled'] and
            self.config['kill_switch']['continuous_improvement_enabled']
        )

    def activate_kill_switch(self, reason: str, modified_by: str = "system"):
        """Emergency shutdown - disable all AI automation"""
        self.config['kill_switch']['ai_automation_enabled'] = False
        self.config['kill_switch']['last_modified'] = datetime.utcnow().isoformat()
        self.config['kill_switch']['modified_by'] = modified_by

        # Save config
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)

        # Log to audit trail
        self._log_audit("KILL_SWITCH_ACTIVATED", {
            "reason": reason,
            "modified_by": modified_by,
            "timestamp": datetime.utcnow().isoformat()
        })

        return {
            "status": "killed",
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }

    # ============================================
    # Module Access Control
    # ============================================

    def can_auto_merge(self, module_id: str) -> Tuple[bool, str]:
        """
        Check if module can be auto-merged
        Returns: (allowed, reason)
        """
        # Check kill switch first
        if not self.is_auto_merge_enabled():
            return False, "Auto-merge disabled (kill switch)"

        strategy = self.config['module_access']['strategy']
        blacklist = self.config['module_access']['blacklist']
        allowlist = self.config['module_access']['allowlist']

        # Check blacklist
        if self._matches_pattern(module_id, blacklist):
            return False, f"Module in blacklist"

        # Check whitelist (if strategy is whitelist)
        if strategy == "whitelist":
            if not self._matches_pattern(module_id, allowlist):
                return False, f"Module not in allowlist (whitelist mode)"

        return True, "OK"

    def requires_human_review(self, module_id: str) -> bool:
        """Check if module requires human review even if tests pass"""
        review_list = self.config['module_access']['require_human_review']
        return self._matches_pattern(module_id, review_list)

    def _matches_pattern(self, module_id: str, patterns: List[str]) -> bool:
        """Check if module_id matches any pattern (supports wildcards)"""
        import fnmatch
        for pattern in patterns:
            if fnmatch.fnmatch(module_id, pattern):
                return True
        return False

    # ============================================
    # Rate Limiting
    # ============================================

    def load_rate_tracker(self) -> Dict:
        """Load rate limit tracking data"""
        if not self.rate_limit_tracker_file.exists():
            return {
                "auto_merges": [],
                "rollbacks": [],
                "last_rollback": None
            }

        with open(self.rate_limit_tracker_file) as f:
            return json.load(f)

    def save_rate_tracker(self, tracker: Dict):
        """Save rate limit tracking data"""
        self.rate_limit_tracker_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.rate_limit_tracker_file, 'w') as f:
            json.dump(tracker, f, indent=2)

    def check_rate_limit(self, action: str) -> Tuple[bool, str]:
        """
        Check if action is within rate limits
        Returns: (allowed, reason)
        """
        tracker = self.load_rate_tracker()
        now = datetime.utcnow()

        if action == "auto_merge":
            merges = [
                datetime.fromisoformat(m['timestamp'])
                for m in tracker.get('auto_merges', [])
            ]

            # Check hourly limit
            hour_ago = now - timedelta(hours=1)
            recent_hour = sum(1 for m in merges if m > hour_ago)
            max_hour = self.config['rate_limits']['max_auto_merges_per_hour']

            if recent_hour >= max_hour:
                return False, f"Rate limit exceeded: {recent_hour}/{max_hour} merges in last hour"

            # Check daily limit
            day_ago = now - timedelta(days=1)
            recent_day = sum(1 for m in merges if m > day_ago)
            max_day = self.config['rate_limits']['max_auto_merges_per_day']

            if recent_day >= max_day:
                return False, f"Rate limit exceeded: {recent_day}/{max_day} merges in last day"

            # Check weekly limit
            week_ago = now - timedelta(weeks=1)
            recent_week = sum(1 for m in merges if m > week_ago)
            max_week = self.config['rate_limits']['max_auto_merges_per_week']

            if recent_week >= max_week:
                return False, f"Rate limit exceeded: {recent_week}/{max_week} merges in last week"

        elif action == "rollback":
            # Check rollback cooldown
            last_rollback = tracker.get('last_rollback')
            if last_rollback:
                last_time = datetime.fromisoformat(last_rollback)
                cooldown_minutes = self.config['rate_limits']['rollback_cooldown_minutes']
                cooldown_until = last_time + timedelta(minutes=cooldown_minutes)

                if now < cooldown_until:
                    remaining = (cooldown_until - now).total_seconds() / 60
                    return False, f"Rollback cooldown active: {remaining:.1f} minutes remaining"

            # Check rollback limits
            rollbacks = [
                datetime.fromisoformat(r['timestamp'])
                for r in tracker.get('rollbacks', [])
            ]

            hour_ago = now - timedelta(hours=1)
            recent_hour = sum(1 for r in rollbacks if r > hour_ago)
            max_hour = self.config['rate_limits']['max_rollbacks_per_hour']

            if recent_hour >= max_hour:
                return False, f"Too many rollbacks: {recent_hour}/{max_hour} in last hour"

            day_ago = now - timedelta(days=1)
            recent_day = sum(1 for r in rollbacks if r > day_ago)
            max_day = self.config['rate_limits']['max_rollbacks_per_day']

            if recent_day >= max_day:
                return False, f"Too many rollbacks: {recent_day}/{max_day} in last day"

        return True, "OK"

    def record_action(self, action: str, module_id: str, metadata: Dict = None):
        """Record an action for rate limiting"""
        tracker = self.load_rate_tracker()

        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "module_id": module_id,
            "metadata": metadata or {}
        }

        if action == "auto_merge":
            tracker.setdefault('auto_merges', []).append(record)

            # Keep only last 7 days
            week_ago = datetime.utcnow() - timedelta(days=7)
            tracker['auto_merges'] = [
                m for m in tracker['auto_merges']
                if datetime.fromisoformat(m['timestamp']) > week_ago
            ]

        elif action == "rollback":
            tracker.setdefault('rollbacks', []).append(record)
            tracker['last_rollback'] = record['timestamp']

            # Keep only last 7 days
            week_ago = datetime.utcnow() - timedelta(days=7)
            tracker['rollbacks'] = [
                r for r in tracker['rollbacks']
                if datetime.fromisoformat(r['timestamp']) > week_ago
            ]

        self.save_rate_tracker(tracker)

    # ============================================
    # Dry-run Mode
    # ============================================

    def is_dry_run_enabled(self) -> bool:
        """Check if global dry-run mode is enabled"""
        return self.config['dry_run']['enabled']

    def should_create_pr_instead(self) -> bool:
        """In dry-run, should create PR instead of merge?"""
        return (
            self.is_dry_run_enabled() and
            self.config['dry_run']['create_pr_instead_of_merge']
        )

    # ============================================
    # Quality Gates
    # ============================================

    def get_auto_merge_threshold(self) -> float:
        """Get minimum pass rate for auto-merge"""
        return self.config['quality_gates']['auto_merge_threshold']

    def get_min_test_runs(self) -> int:
        """Get minimum required test runs"""
        return self.config['quality_gates']['min_test_runs']

    def should_rollback(
        self,
        baseline_pass_rate: float,
        current_pass_rate: float,
        consecutive_failures: int = 0
    ) -> Tuple[bool, str]:
        """Determine if rollback should be triggered"""
        triggers = self.config['quality_gates']['rollback_triggers']

        # Check absolute minimum
        min_rate = triggers['absolute_pass_rate_minimum']
        if current_pass_rate < min_rate:
            return True, f"Pass rate {current_pass_rate:.2%} below minimum {min_rate:.2%}"

        # Check degradation
        drop_threshold = triggers['pass_rate_drop_threshold']
        drop = baseline_pass_rate - current_pass_rate
        if drop > drop_threshold:
            return True, f"Pass rate dropped {drop:.2%} (threshold: {drop_threshold:.2%})"

        # Check consecutive failures
        max_consecutive = triggers['consecutive_failures']
        if consecutive_failures >= max_consecutive:
            return True, f"{consecutive_failures} consecutive failures (max: {max_consecutive})"

        return False, "OK"

    # ============================================
    # Audit Trail
    # ============================================

    def _log_audit(self, event: str, data: Dict):
        """Log event to audit trail"""
        if not self.config['audit']['log_all_ai_actions']:
            return

        log_file = Path(self.config['audit']['log_file'])
        log_file.parent.mkdir(parents=True, exist_ok=True)

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "data": data
        }

        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    # ============================================
    # Validation
    # ============================================

    def validate_deployment(
        self,
        module_id: str,
        pass_rate: float,
        test_runs: int,
        deployed_by: str = "ai_agent"
    ) -> Tuple[bool, str]:
        """
        Comprehensive validation before deployment
        Returns: (allowed, reason)
        """
        # Check kill switch
        if not self.is_auto_merge_enabled():
            return False, "Auto-merge disabled (kill switch)"

        # Check dry-run mode
        if self.is_dry_run_enabled() and deployed_by == "ai_agent":
            return False, "Dry-run mode enabled (create PR instead)"

        # Check module access
        can_merge, reason = self.can_auto_merge(module_id)
        if not can_merge:
            return False, reason

        # Check quality gates
        threshold = self.get_auto_merge_threshold()
        if pass_rate < threshold:
            return False, f"Pass rate {pass_rate:.2%} below threshold {threshold:.2%}"

        min_runs = self.get_min_test_runs()
        if test_runs < min_runs:
            return False, f"Only {test_runs} test runs (minimum: {min_runs})"

        # Check rate limits
        within_limit, reason = self.check_rate_limit("auto_merge")
        if not within_limit:
            return False, reason

        # Check human review requirement
        if self.requires_human_review(module_id):
            return False, f"Module requires human review (create PR instead)"

        return True, "OK"


# ============================================
# CLI Interface
# ============================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Flyto2 Safety Manager")
    parser.add_argument('action', choices=[
        'check',
        'kill',
        'revive',
        'validate',
        'status'
    ])
    parser.add_argument('--module', help="Module ID")
    parser.add_argument('--pass-rate', type=float, help="Pass rate")
    parser.add_argument('--test-runs', type=int, help="Number of test runs")
    parser.add_argument('--reason', help="Reason for action")
    parser.add_argument('--by', default="human", help="Who is performing action")

    args = parser.parse_args()

    manager = SafetyManager()

    if args.action == 'kill':
        result = manager.activate_kill_switch(
            reason=args.reason or "Manual kill switch activation",
            modified_by=args.by
        )
        print(json.dumps(result, indent=2))

    elif args.action == 'status':
        status = {
            "automation_enabled": manager.is_automation_enabled(),
            "auto_merge_enabled": manager.is_auto_merge_enabled(),
            "auto_rollback_enabled": manager.is_auto_rollback_enabled(),
            "continuous_improvement_enabled": manager.is_continuous_improvement_enabled(),
            "dry_run_enabled": manager.is_dry_run_enabled()
        }
        print(json.dumps(status, indent=2))

    elif args.action == 'validate':
        if not args.module or args.pass_rate is None or args.test_runs is None:
            print("Error: --module, --pass-rate, and --test-runs required")
            return 1

        allowed, reason = manager.validate_deployment(
            module_id=args.module,
            pass_rate=args.pass_rate,
            test_runs=args.test_runs
        )

        result = {
            "allowed": allowed,
            "reason": reason,
            "module_id": args.module,
            "pass_rate": args.pass_rate,
            "test_runs": args.test_runs
        }
        print(json.dumps(result, indent=2))

        return 0 if allowed else 1

    elif args.action == 'check':
        if not args.module:
            print("Error: --module required")
            return 1

        can_merge, reason = manager.can_auto_merge(args.module)
        requires_review = manager.requires_human_review(args.module)

        result = {
            "module_id": args.module,
            "can_auto_merge": can_merge,
            "reason": reason,
            "requires_human_review": requires_review
        }
        print(json.dumps(result, indent=2))

    return 0


if __name__ == "__main__":
    exit(main())
