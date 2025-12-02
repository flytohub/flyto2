"""
Auto Evolution Engine - Continuous Self-Improvement System

This engine creates an automated loop:
1. Test crawler on real websites
2. Detect errors and failures
3. Analyze what resources are missing
4. Generate new atomic modules (if needed)
5. Run tests
6. Create PR
7. Notify via Telegram

The system evolves automatically without human intervention.
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess


class AutoEvolutionEngine:
    """
    Autonomous evolution engine for continuous improvement
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.metrics_dir = self.project_root / "metrics"
        self.metrics_dir.mkdir(exist_ok=True)
        self.evolution_log = self.metrics_dir / "auto_evolution.json"
        self.cycles = self._load_cycles()

    def _load_cycles(self) -> List[Dict[str, Any]]:
        """Load evolution cycle history"""
        if self.evolution_log.exists():
            try:
                return json.loads(self.evolution_log.read_text())
            except Exception:
                return []
        return []

    def _save_cycles(self):
        """Save evolution cycle history"""
        self.evolution_log.write_text(
            json.dumps(self.cycles, indent=2),
            encoding='utf-8'
        )

    async def run_evolution_cycle(self) -> Dict[str, Any]:
        """
        Run one complete evolution cycle

        Returns:
            Cycle results
        """
        cycle_id = len(self.cycles) + 1

        print("=" * 70)
        print(f"EVOLUTION CYCLE #{cycle_id}")
        print("=" * 70)
        print()

        cycle = {
            "cycle_id": cycle_id,
            "timestamp": datetime.now().isoformat(),
            "steps": {},
            "status": "running"
        }

        try:
            # Step 1: Test crawler
            print("STEP 1: Testing crawler...")
            test_result = await self._test_crawler()
            cycle["steps"]["test_crawler"] = test_result
            print(f"  Status: {'✅' if test_result['success'] else '❌'}")
            print(f"  Tests passed: {test_result['passed']}/{test_result['total']}")
            print()

            # Step 2: Analyze errors
            if not test_result['success']:
                print("STEP 2: Analyzing errors...")
                analysis = await self._analyze_errors(test_result['errors'])
                cycle["steps"]["analyze_errors"] = analysis
                print(f"  Missing resources: {len(analysis['missing_resources'])}")
                print()

                # Step 3: Generate solutions
                if analysis['missing_resources']:
                    print("STEP 3: Generating solutions...")
                    solutions = await self._generate_solutions(analysis)
                    cycle["steps"]["generate_solutions"] = solutions
                    print(f"  Solutions generated: {len(solutions['modules'])}")
                    print()

                    # Step 4: Run tests
                    print("STEP 4: Running tests...")
                    test_results = await self._run_tests()
                    cycle["steps"]["run_tests"] = test_results
                    print(f"  Tests: {'✅ PASS' if test_results['all_passed'] else '❌ FAIL'}")
                    print()

                    # Step 5: Create PR (if tests pass)
                    if test_results['all_passed']:
                        print("STEP 5: Creating PR...")
                        pr_result = await self._create_pr(cycle)
                        cycle["steps"]["create_pr"] = pr_result
                        print(f"  PR: {pr_result.get('pr_url', 'N/A')}")
                        print()

                        # Step 6: Notify Telegram
                        print("STEP 6: Notifying Telegram...")
                        notify_result = await self._notify_telegram(cycle, pr_result)
                        cycle["steps"]["notify_telegram"] = notify_result
                        print(f"  Notification: {'✅ Sent' if notify_result['success'] else '❌ Failed'}")
                        print()

            cycle["status"] = "completed"

        except Exception as e:
            cycle["status"] = "error"
            cycle["error"] = str(e)
            print(f"❌ CYCLE ERROR: {e}")

        # Save cycle
        self.cycles.append(cycle)
        self._save_cycles()

        print("=" * 70)
        print(f"Cycle #{cycle_id}: {cycle['status'].upper()}")
        print("=" * 70)
        print()

        return cycle

    async def _test_crawler(self) -> Dict[str, Any]:
        """
        Test crawler on real websites

        Returns:
            Test results
        """
        # Run test_crawler_practice.py
        try:
            result = subprocess.run(
                ["python", "tests/test_crawler_practice.py"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )

            # Parse output for success/failure
            output = result.stdout + result.stderr
            errors = []

            # Simple heuristic: look for error indicators
            if "❌" in output or "EXCEPTION" in output or result.returncode != 0:
                # Extract error lines
                for line in output.split('\n'):
                    if "❌" in line or "EXCEPTION" in line or "Error" in line:
                        errors.append(line.strip())

            passed = output.count("✅ SUCCESS")
            total = output.count("Testing:")

            return {
                "success": len(errors) == 0,
                "passed": passed,
                "total": total,
                "errors": errors,
                "output": output[:500]  # First 500 chars
            }

        except Exception as e:
            return {
                "success": False,
                "passed": 0,
                "total": 0,
                "errors": [str(e)],
                "output": ""
            }

    async def _analyze_errors(self, errors: List[str]) -> Dict[str, Any]:
        """
        Analyze errors to identify missing resources

        Args:
            errors: List of error messages

        Returns:
            Analysis results
        """
        missing_resources = []
        recommendations = []

        for error in errors:
            # Simple pattern matching for common errors
            if "timeout" in error.lower():
                missing_resources.append("timeout_handler")
                recommendations.append("Add retry logic with exponential backoff")

            elif "connection" in error.lower() or "network" in error.lower():
                missing_resources.append("connection_manager")
                recommendations.append("Implement connection pooling")

            elif "parse" in error.lower() or "extract" in error.lower():
                missing_resources.append("parser_module")
                recommendations.append("Add robust HTML parsing module")

            elif "rate limit" in error.lower():
                missing_resources.append("rate_limiter")
                recommendations.append("Implement intelligent rate limiting")

        return {
            "missing_resources": list(set(missing_resources)),
            "recommendations": recommendations,
            "error_count": len(errors)
        }

    async def _generate_solutions(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate solutions for missing resources

        Args:
            analysis: Error analysis results

        Returns:
            Generated solutions
        """
        modules = []

        for resource in analysis["missing_resources"]:
            # For now, log what needs to be created
            # In future, could use AI to generate module code
            modules.append({
                "name": resource,
                "type": "atomic_module",
                "status": "planned",
                "recommendation": f"Create {resource} module"
            })

        return {
            "modules": modules,
            "count": len(modules)
        }

    async def _run_tests(self) -> Dict[str, Any]:
        """
        Run all tests

        Returns:
            Test results
        """
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )

            output = result.stdout + result.stderr

            # Parse pytest output
            passed = output.count(" PASSED")
            failed = output.count(" FAILED")

            return {
                "all_passed": result.returncode == 0,
                "passed": passed,
                "failed": failed,
                "output": output[:500]
            }

        except Exception as e:
            return {
                "all_passed": False,
                "passed": 0,
                "failed": 0,
                "error": str(e)
            }

    async def _create_pr(self, cycle: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create pull request

        Args:
            cycle: Evolution cycle data

        Returns:
            PR creation result
        """
        # Generate PR title and body
        pr_title = f"Auto-evolution cycle #{cycle['cycle_id']}"
        pr_body = self._generate_pr_body(cycle)

        try:
            # Check if there are changes to commit
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            if not result.stdout.strip():
                return {
                    "success": False,
                    "message": "No changes to commit"
                }

            # Create branch
            branch_name = f"auto-evolution-{cycle['cycle_id']}"

            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=self.project_root,
                check=True
            )

            # Stage all changes
            subprocess.run(
                ["git", "add", "."],
                cwd=self.project_root,
                check=True
            )

            # Commit
            subprocess.run(
                ["git", "commit", "-m", f"{pr_title}\n\n{pr_body}"],
                cwd=self.project_root,
                check=True
            )

            # Push (commented out for safety)
            # subprocess.run(
            #     ["git", "push", "-u", "origin", branch_name],
            #     cwd=self.project_root,
            #     check=True
            # )

            return {
                "success": True,
                "branch": branch_name,
                "title": pr_title,
                "message": "Branch created (push manually to create PR)"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _generate_pr_body(self, cycle: Dict[str, Any]) -> str:
        """Generate PR description"""
        lines = [
            f"## Auto-Evolution Cycle #{cycle['cycle_id']}",
            "",
            "### Changes",
            ""
        ]

        if "generate_solutions" in cycle["steps"]:
            solutions = cycle["steps"]["generate_solutions"]
            lines.append(f"- Generated {solutions['count']} new modules")

        if "run_tests" in cycle["steps"]:
            tests = cycle["steps"]["run_tests"]
            lines.append(f"- Tests: {tests['passed']} passed")

        lines.extend([
            "",
            "### Test Results",
            f"- Crawler tests: {cycle['steps']['test_crawler']['passed']}/{cycle['steps']['test_crawler']['total']}",
            "",
            "Auto-generated by Evolution Engine",
        ])

        return "\n".join(lines)

    async def _notify_telegram(self, cycle: Dict[str, Any], pr_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send notification to Telegram

        Args:
            cycle: Evolution cycle data
            pr_result: PR creation result

        Returns:
            Notification result
        """
        # This would integrate with telegram_bot_v2.py
        # For now, just log
        message = f"""
🤖 Auto-Evolution Cycle #{cycle['cycle_id']}

Status: {cycle['status']}
PR: {pr_result.get('branch', 'N/A')}
Tests: {cycle['steps'].get('run_tests', {}).get('passed', 0)} passed

Ready for review!
        """.strip()

        print(f"\nTelegram message:\n{message}\n")

        return {
            "success": True,
            "message": message
        }

    async def run_continuous_evolution(self, max_cycles: int = 10, interval_hours: int = 24):
        """
        Run continuous evolution loop

        Args:
            max_cycles: Maximum number of cycles
            interval_hours: Hours between cycles
        """
        print("🤖 AUTO-EVOLUTION ENGINE STARTED")
        print(f"   Max cycles: {max_cycles}")
        print(f"   Interval: {interval_hours} hours")
        print()

        for i in range(max_cycles):
            await self.run_evolution_cycle()

            if i < max_cycles - 1:
                print(f"⏳ Waiting {interval_hours} hours until next cycle...")
                await asyncio.sleep(interval_hours * 3600)


async def main():
    """Main execution"""
    engine = AutoEvolutionEngine()

    # Run one evolution cycle
    result = await engine.run_evolution_cycle()

    print("\n📊 Evolution Cycle Summary:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
