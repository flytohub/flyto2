"""
Solution Executor Module - Execute AI-provided solutions safely

Atomic responsibility: Safe execution of solutions (commands)
Extracted from: ai_error_solver.py lines 369-417
"""

import subprocess
from pathlib import Path
from typing import Any, Dict, Optional
from src.core.utils.notifier import notify


class SolutionExecutorModule:
    """
    Execute AI-provided solutions safely

    Single responsibility: Run commands with timeout and error handling
    """

    @staticmethod
    async def execute(
        solution: Dict[str, Any],
        project_root: Optional[Path] = None,
        notify_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Execute AI-provided solution

        Args:
            solution: Solution dict with "commands" list
            project_root: Project root directory
            notify_callback: Optional notification callback

        Returns:
            {
                "success": bool,
                "commands_executed": int,
                "error": str,  # If failed
                "stderr": str   # If failed
            }
        """
        if project_root is None:
            project_root = Path.cwd()

        commands = solution.get("commands", [])

        if not commands:
            return {"success": False, "error": "No commands to execute"}

        await notify(f"⚙️ Executing {len(commands)} commands...", notify_callback)

        for cmd in commands:
            # Parse command
            if isinstance(cmd, str):
                cmd_str = cmd
                cmd_parts = cmd.split()
            else:
                cmd_parts = cmd
                cmd_str = " ".join(cmd)

            await notify(f"  $ {cmd_str}", notify_callback)

            try:
                result = subprocess.run(
                    cmd_parts,
                    cwd=project_root,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes max per command
                )

                if result.returncode != 0:
                    await notify(f"  ❌ Failed: {result.stderr[:200]}", notify_callback)
                    return {
                        "success": False,
                        "error": f"Command failed: {cmd_str}",
                        "stderr": result.stderr
                    }

                await notify(f"  ✅ Success", notify_callback)

            except subprocess.TimeoutExpired:
                await notify(f"  ❌ Timeout", notify_callback)
                return {
                    "success": False,
                    "error": f"Command timeout: {cmd_str}"
                }

            except Exception as e:
                await notify(f"  ❌ Error: {e}", notify_callback)
                return {"success": False, "error": str(e)}

        return {"success": True, "commands_executed": len(commands)}
