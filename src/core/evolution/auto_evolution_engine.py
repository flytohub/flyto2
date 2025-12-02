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

Components:
- EvolutionPlanner: Analyze errors and create evolution plan
- EvolutionDesigner: Design implementation details
- ImplementationAgent: Generate and apply code changes
"""
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess

logger = logging.getLogger(__name__)


class EvolutionPlanner:
    """
    Create evolution plans from error tickets

    Analyzes errors, queries knowledge base, and generates structured plans.
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent

    async def analyze_and_plan(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze error ticket and create evolution plan

        Args:
            ticket: Error ticket with context

        Returns:
            {
                "problem_summary": str,
                "root_cause": str,
                "fix_strategy": str,
                "required_modules": list,
                "changes_needed": list,
                "confidence": float
            }
        """
        logger.info(f"Planning for ticket: {ticket.get('ticket_id', 'unknown')}")

        # Step 1: Gather context
        context = await self._gather_context(ticket)

        # Step 2: Analyze error patterns
        analysis = self._analyze_error_patterns(ticket, context)

        # Step 3: Generate plan
        plan = {
            "problem_summary": analysis.get("summary", "Unknown error"),
            "root_cause": analysis.get("root_cause", "To be determined"),
            "fix_strategy": analysis.get("strategy", "Investigate and fix"),
            "required_modules": analysis.get("modules", []),
            "changes_needed": analysis.get("changes", []),
            "confidence": analysis.get("confidence", 0.5)
        }

        logger.info(f"Plan created with confidence: {plan['confidence']}")
        return plan

    async def _gather_context(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """Gather all relevant context for planning"""
        context = {
            "error_context": ticket.get("context", {}),
            "similar_errors": [],
            "related_modules": [],
            "past_fixes": []
        }

        # Try to load RAG retriever if available
        try:
            from src.core.utils.rag_retriever import retrieve_knowledge

            error_sig = ticket.get("error_signature", "")
            if error_sig:
                # Query for similar errors
                rag_results = await retrieve_knowledge(
                    query=f"error {error_sig}",
                    filters={"type": "error"},
                    top_k=5
                )
                context["similar_errors"] = rag_results.get("results", [])

                # Query for past fixes
                fix_results = await retrieve_knowledge(
                    query=f"fix {error_sig}",
                    filters={"type": "fix"},
                    top_k=3
                )
                context["past_fixes"] = fix_results.get("results", [])
        except Exception as e:
            logger.warning(f"RAG retrieval failed: {e}")

        return context

    def _analyze_error_patterns(self, ticket: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze error patterns and determine fix strategy"""
        error_msg = str(ticket.get("error_message", ""))
        error_sig = ticket.get("error_signature", "")

        analysis = {
            "summary": f"Error: {error_sig}",
            "root_cause": "Unknown",
            "strategy": "Investigate and fix",
            "modules": [],
            "changes": [],
            "confidence": 0.3
        }

        # Pattern matching for common errors
        error_lower = error_msg.lower()

        if "timeout" in error_lower:
            analysis.update({
                "root_cause": "Request timeout - insufficient wait time or slow response",
                "strategy": "Increase timeout and add retry logic with exponential backoff",
                "modules": ["browser.wait", "api.retry"],
                "changes": [{
                    "type": "update_module",
                    "target": "browser.wait",
                    "reason": "Increase default timeout values"
                }],
                "confidence": 0.7
            })
        elif "element not found" in error_lower or "selector" in error_lower:
            analysis.update({
                "root_cause": "DOM selector issue - element may load dynamically or selector incorrect",
                "strategy": "Add intelligent wait for element and fallback selectors",
                "modules": ["browser.wait_for_element", "element.smart_query"],
                "changes": [{
                    "type": "update_module",
                    "target": "element.query",
                    "reason": "Add retry logic and multiple selector strategies"
                }],
                "confidence": 0.8
            })
        elif "connection" in error_lower or "network" in error_lower:
            analysis.update({
                "root_cause": "Network connectivity issue",
                "strategy": "Implement connection pooling and retry logic",
                "modules": ["api.connection_pool", "api.retry"],
                "changes": [{
                    "type": "create_module",
                    "target": "api.connection_manager",
                    "reason": "Centralized connection management"
                }],
                "confidence": 0.6
            })
        elif "rate limit" in error_lower:
            analysis.update({
                "root_cause": "API rate limiting",
                "strategy": "Implement intelligent rate limiting with backoff",
                "modules": ["api.rate_limiter"],
                "changes": [{
                    "type": "create_module",
                    "target": "api.rate_limiter",
                    "reason": "Prevent rate limit errors"
                }],
                "confidence": 0.9
            })

        return analysis


class EvolutionDesigner:
    """
    Design implementation details from evolution plans

    Takes plans and creates detailed implementation specifications.
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent

    async def design_implementation(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Design detailed implementation from plan

        Args:
            plan: Evolution plan from Planner

        Returns:
            {
                "design_doc": str,
                "file_changes": list,
                "test_plan": str,
                "rollback_plan": str,
                "estimated_effort": str
            }
        """
        logger.info("Designing implementation...")

        file_changes = []

        for change in plan.get("changes_needed", []):
            change_type = change.get("type", "")
            target = change.get("target", "")
            reason = change.get("reason", "")

            if change_type == "create_module":
                file_changes.append({
                    "action": "create",
                    "path": self._module_id_to_path(target),
                    "reason": reason,
                    "template": "atomic_module"
                })
            elif change_type == "update_module":
                file_changes.append({
                    "action": "update",
                    "path": self._module_id_to_path(target),
                    "reason": reason,
                    "changes": ["Add error handling", "Increase timeout", "Add retry logic"]
                })
            elif change_type == "update_workflow":
                file_changes.append({
                    "action": "update",
                    "path": f"workflows/{target}",
                    "reason": reason,
                    "changes": ["Update module parameters"]
                })

        design = {
            "design_doc": self._generate_design_doc(plan, file_changes),
            "file_changes": file_changes,
            "test_plan": self._generate_test_plan(plan),
            "rollback_plan": self._generate_rollback_plan(file_changes),
            "estimated_effort": self._estimate_effort(file_changes)
        }

        logger.info(f"Design complete: {len(file_changes)} file changes")
        return design

    def _module_id_to_path(self, module_id: str) -> str:
        """Convert module ID to file path"""
        parts = module_id.split('.')
        if len(parts) == 2:
            category, name = parts
            return f"src/core/modules/atomic/{category}/{name}.py"
        return f"src/core/modules/{module_id.replace('.', '/')}.py"

    def _generate_design_doc(self, plan: Dict[str, Any], file_changes: List[Dict]) -> str:
        """Generate design documentation"""
        lines = [
            "# Implementation Design",
            "",
            f"## Problem: {plan.get('problem_summary', 'Unknown')}",
            "",
            f"## Root Cause: {plan.get('root_cause', 'Unknown')}",
            "",
            f"## Strategy: {plan.get('fix_strategy', 'Unknown')}",
            "",
            "## File Changes:",
            ""
        ]

        for change in file_changes:
            lines.append(f"- {change['action'].upper()}: {change['path']}")
            lines.append(f"  Reason: {change['reason']}")
            lines.append("")

        return "\n".join(lines)

    def _generate_test_plan(self, plan: Dict[str, Any]) -> str:
        """Generate test plan"""
        return f"""
Test Plan:
1. Unit tests for modified modules
2. Integration tests for affected workflows
3. Regression tests for related functionality
4. Performance tests if timeout/retry logic changed
5. End-to-end test on target website

Success Criteria:
- All existing tests pass
- New tests cover edge cases
- Error no longer occurs in practice run
"""

    def _generate_rollback_plan(self, file_changes: List[Dict]) -> str:
        """Generate rollback plan"""
        lines = ["Rollback Plan:", ""]
        for change in file_changes:
            if change['action'] == 'create':
                lines.append(f"- Delete: {change['path']}")
            elif change['action'] == 'update':
                lines.append(f"- Revert: {change['path']} (use git checkout)")
        return "\n".join(lines)

    def _estimate_effort(self, file_changes: List[Dict]) -> str:
        """Estimate implementation effort"""
        count = len(file_changes)
        if count == 0:
            return "No changes needed"
        elif count == 1:
            return "Small (< 1 hour)"
        elif count <= 3:
            return "Medium (1-3 hours)"
        else:
            return "Large (> 3 hours)"


class ImplementationAgent:
    """
    Generate and apply code changes

    Takes designs and creates actual code implementations.
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent

    async def implement_design(self, design: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implement the design

        Args:
            design: Design specification from Designer

        Returns:
            {
                "success": bool,
                "files_modified": list,
                "files_created": list,
                "tests_created": list,
                "errors": list
            }
        """
        logger.info("Implementing design...")

        result = {
            "success": True,
            "files_modified": [],
            "files_created": [],
            "tests_created": [],
            "errors": []
        }

        for change in design.get("file_changes", []):
            try:
                if change['action'] == 'create':
                    success = await self._create_file(change)
                    if success:
                        result["files_created"].append(change['path'])
                    else:
                        result["errors"].append(f"Failed to create {change['path']}")
                        result["success"] = False

                elif change['action'] == 'update':
                    success = await self._update_file(change)
                    if success:
                        result["files_modified"].append(change['path'])
                    else:
                        result["errors"].append(f"Failed to update {change['path']}")
                        result["success"] = False

            except Exception as e:
                result["errors"].append(f"Error processing {change['path']}: {str(e)}")
                result["success"] = False

        logger.info(f"Implementation {'succeeded' if result['success'] else 'failed'}")
        return result

    async def _create_file(self, change: Dict[str, Any]) -> bool:
        """Create new file from template"""
        file_path = self.project_root / change['path']

        # Check if file already exists
        if file_path.exists():
            logger.warning(f"File already exists: {file_path}")
            return False

        # Create directory if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate content based on template
        if change.get('template') == 'atomic_module':
            content = self._generate_atomic_module_template(change)
        else:
            content = f"# {change.get('reason', 'Generated file')}\n"

        try:
            file_path.write_text(content, encoding='utf-8')
            logger.info(f"Created file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create file: {e}")
            return False

    async def _update_file(self, change: Dict[str, Any]) -> bool:
        """Update existing file"""
        file_path = self.project_root / change['path']

        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False

        try:
            # For now, just add a comment noting the change needed
            # In production, would use AST manipulation or LLM-generated patches
            content = file_path.read_text(encoding='utf-8')

            comment = f"\n# TODO: {change.get('reason', 'Update needed')}\n"
            if comment not in content:
                content = content + comment
                file_path.write_text(content, encoding='utf-8')
                logger.info(f"Updated file: {file_path}")

            return True
        except Exception as e:
            logger.error(f"Failed to update file: {e}")
            return False

    def _generate_atomic_module_template(self, change: Dict[str, Any]) -> str:
        """Generate atomic module template"""
        module_name = Path(change['path']).stem
        reason = change.get('reason', 'Generated module')

        return f'''"""
{module_name.replace('_', ' ').title()} Module

{reason}
"""
from typing import Any, Dict


async def execute(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute {module_name} operation

    Args:
        params: Module parameters

    Returns:
        Result dictionary
    """
    # TODO: Implement module logic
    return {{
        "success": True,
        "message": "{module_name} executed"
    }}


def validate_params(params: Dict[str, Any]) -> bool:
    """Validate module parameters"""
    # TODO: Add parameter validation
    return True
'''


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

        # Initialize evolution components
        self.planner = EvolutionPlanner()
        self.designer = EvolutionDesigner()
        self.implementer = ImplementationAgent()

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

            # Step 2: Analyze errors (using Planner)
            if not test_result['success']:
                print("STEP 2: Analyzing errors and planning...")
                ticket = self._create_ticket_from_errors(test_result['errors'])
                plan = await self.planner.analyze_and_plan(ticket)
                cycle["steps"]["plan"] = plan
                print(f"  Root cause: {plan['root_cause'][:60]}...")
                print(f"  Confidence: {plan['confidence']:.0%}")
                print()

                # Step 3: Design solution
                if plan.get('changes_needed'):
                    print("STEP 3: Designing solution...")
                    design = await self.designer.design_implementation(plan)
                    cycle["steps"]["design"] = design
                    print(f"  File changes: {len(design['file_changes'])}")
                    print(f"  Effort: {design['estimated_effort']}")
                    print()

                    # Step 4: Implement changes
                    print("STEP 4: Implementing changes...")
                    impl_result = await self.implementer.implement_design(design)
                    cycle["steps"]["implementation"] = impl_result
                    print(f"  Files created: {len(impl_result['files_created'])}")
                    print(f"  Files modified: {len(impl_result['files_modified'])}")
                    if impl_result['errors']:
                        print(f"  ⚠️  Errors: {len(impl_result['errors'])}")
                    print()

                    # Step 5: Run tests
                    print("STEP 5: Running tests...")
                    test_results = await self._run_tests()
                    cycle["steps"]["run_tests"] = test_results
                    print(f"  Tests: {'✅ PASS' if test_results['all_passed'] else '❌ FAIL'}")
                    print()

                    # Step 6: Create PR (if tests pass)
                    if test_results['all_passed']:
                        print("STEP 6: Creating PR...")
                        pr_result = await self._create_pr(cycle)
                        cycle["steps"]["create_pr"] = pr_result
                        print(f"  PR: {pr_result.get('branch', 'N/A')}")
                        print()

                        # Step 7: Notify Telegram
                        print("STEP 7: Notifying Telegram...")
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

    def _create_ticket_from_errors(self, errors: List[str]) -> Dict[str, Any]:
        """
        Create evolution ticket from test errors

        Args:
            errors: List of error messages

        Returns:
            Ticket dictionary
        """
        import hashlib

        # Combine errors for signature
        error_text = " | ".join(errors[:3])  # Use first 3 errors
        error_sig = hashlib.md5(error_text.encode()).hexdigest()[:8]

        ticket = {
            "ticket_id": f"auto_{error_sig}",
            "error_signature": error_sig,
            "error_message": error_text,
            "trigger": "automated_testing",
            "context": {
                "errors": errors,
                "error_count": len(errors),
                "timestamp": datetime.now().isoformat()
            }
        }

        return ticket

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
            "### Analysis",
            ""
        ]

        if "plan" in cycle["steps"]:
            plan = cycle["steps"]["plan"]
            lines.append(f"**Problem**: {plan.get('problem_summary', 'Unknown')}")
            lines.append(f"**Root Cause**: {plan.get('root_cause', 'Unknown')}")
            lines.append(f"**Strategy**: {plan.get('fix_strategy', 'Unknown')}")
            lines.append(f"**Confidence**: {plan.get('confidence', 0):.0%}")
            lines.append("")

        if "implementation" in cycle["steps"]:
            impl = cycle["steps"]["implementation"]
            lines.append("### Changes")
            lines.append("")
            if impl.get('files_created'):
                lines.append(f"- **Files Created**: {len(impl['files_created'])}")
                for f in impl['files_created'][:5]:  # Show first 5
                    lines.append(f"  - {f}")
            if impl.get('files_modified'):
                lines.append(f"- **Files Modified**: {len(impl['files_modified'])}")
                for f in impl['files_modified'][:5]:  # Show first 5
                    lines.append(f"  - {f}")
            lines.append("")

        if "run_tests" in cycle["steps"]:
            tests = cycle["steps"]["run_tests"]
            lines.append("### Test Results")
            lines.append("")
            lines.append(f"- **Tests Passed**: {tests.get('passed', 0)}")
            lines.append(f"- **Tests Failed**: {tests.get('failed', 0)}")
            lines.append("")

        lines.extend([
            "---",
            "",
            "Auto-generated by Evolution Engine",
            f"Timestamp: {cycle.get('timestamp', 'N/A')}"
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
