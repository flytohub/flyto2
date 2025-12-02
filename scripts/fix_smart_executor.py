"""
Fix Smart Executor to use AI Error Solver

This script adds AI error solving capability to smart_executor.py
"""

import re
from pathlib import Path

def fix_smart_executor():
    """Add AI Error Solver integration to smart_executor"""

    file_path = Path(__file__).parent.parent / "src/core/executor/smart_executor.py"

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already fixed
    if "AIErrorSolver" in content:
        print("✅ SmartExecutor already has AI Error Solver integration")
        return

    # Find the error handling section
    pattern = r'(if attempt < self\.max_retries:\s+# Step 3: Analyze error)'

    if not re.search(pattern, content):
        print("❌ Could not find error handling section")
        return

    # Replace with AI Error Solver integration
    replacement = '''if attempt < self.max_retries:
                    # USE AI ERROR SOLVER
                    await self._notify(notify_callback, "\\n🤖 Consulting AI for solution...")

                    from src.core.healing.ai_error_solver import AIErrorSolver

                    solver = AIErrorSolver(project_root=self.project_root)

                    error_context = {
                        "operation": "workflow_generation" if not attempt_result["workflow_generated"] else "workflow_execution",
                        "task_description": task_description,
                        "attempt": attempt,
                        "workflow": workflow if workflow else None
                    }

                    solution_result = await solver.solve_error(
                        Exception(error_msg),
                        error_context,
                        notify_callback
                    )

                    if solution_result.get("success"):
                        await self._notify(notify_callback, "✅ AI solved it, retrying...")
                        continue

                    # Fallback: Step 3: Analyze error'''

    content = re.sub(pattern, replacement, content)

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ SmartExecutor fixed! Now uses AI Error Solver")

if __name__ == "__main__":
    fix_smart_executor()
