"""
Self-Healing Practice Engine - AI Agent with Auto-Recovery

This engine wraps DailyPracticeEngine with self-healing capabilities:
1. Detects errors
2. Attempts automatic fixes
3. Consults AI (with vector DB context) if auto-fix fails
4. Executes AI solution
5. Stores successful solutions to vector DB
6. Retries operation

NEVER GIVES UP - keeps trying until success or max retries reached
"""

import asyncio
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import os

from .daily_practice import DailyPracticeEngine


class SelfHealingPracticeEngine:
    """
    Self-healing practice engine that never gives up
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.base_engine = DailyPracticeEngine(self.project_root)
        self.max_retries = 3
        self.healing_log = self.project_root / "metrics" / "self_healing.json"
        self.healing_log.parent.mkdir(exist_ok=True)

    async def analyze_website(self, url: str, notify_callback=None) -> Dict[str, Any]:
        """
        Analyze website with self-healing

        Args:
            url: Target URL
            notify_callback: Optional callback for progress updates

        Returns:
            Analysis result (guaranteed to succeed or provide solution)
        """
        for attempt in range(1, self.max_retries + 1):
            await self._notify(notify_callback, f"🔄 Analysis attempt {attempt}/{self.max_retries}: {url}")

            # Try analysis
            result = await self.base_engine.analyze_website(url)

            # Check for errors
            if not result.get("errors"):
                await self._notify(notify_callback, f"✅ Analysis successful: {url}")
                return result

            # Has errors - try to heal
            errors = result["errors"]
            await self._notify(notify_callback, f"❌ Errors detected: {len(errors)} errors")

            for error in errors:
                await self._notify(notify_callback, f"🔍 Analyzing error: {error[:100]}...")

                # AI Error Solver handles everything:
                # 1. Query vector DB for past solutions
                # 2. If found + high similarity → use it
                # 3. Else → ask AI
                # 4. Execute solution
                # 5. Store if successful
                # 6. Train similarity
                fix_result = await self._try_automatic_fix(error, notify_callback)

                if fix_result["success"]:
                    await self._notify(notify_callback, f"✅ Error resolved!")
                    # Retry the analysis
                    continue
                else:
                    await self._notify(notify_callback, f"❌ Could not resolve error")
                    # Try next attempt anyway (maybe transient error)

        # Max retries reached
        await self._notify(notify_callback, f"❌ Max retries reached. Logging for human review.")
        await self._log_unsolved_problem(url, result)

        return result

    async def _try_automatic_fix(self, error: str, notify_callback=None) -> Dict[str, Any]:
        """
        Use AI to fix ANY error - NO HARDCODED LOGIC

        Returns:
            Fix result with success status and action taken
        """
        from src.core.healing.ai_error_solver import AIErrorSolver

        # Create AI solver
        solver = AIErrorSolver(self.project_root)

        # Build context
        context = {
            "operation": "website_analysis",
            "error_source": "DailyPracticeEngine",
            "project": "Flyto2 autonomous training"
        }

        # Ask AI to solve
        result = await solver.solve_error(
            Exception(error),
            context,
            notify_callback
        )

        if result["success"]:
            return {
                "success": True,
                "action": "AI-provided solution",
                "output": str(result)
            }
        else:
            return {
                "success": False,
                "action": "AI solution failed",
                "error": result.get("error", "Unknown")
            }

    async def _consult_ai(self, error: str, context: str, notify_callback=None) -> Dict[str, Any]:
        """
        Consult AI (Ollama/Claude/ChatGPT) with vector DB context

        Args:
            error: Error message
            context: Additional context (URL, etc.)
            notify_callback: Progress callback

        Returns:
            AI solution
        """
        # Step 1: Query vector DB for similar problems
        await self._notify(notify_callback, "📚 Querying vector DB for similar problems...")
        similar_solutions = await self._query_similar_solutions(error)

        # Step 2: Build context for AI
        project_context = await self._get_project_context()

        # Step 3: Ask AI
        prompt = self._build_ai_prompt(error, context, similar_solutions, project_context)

        # Try Ollama first (free)
        ollama_result = await self._ask_ollama(prompt, notify_callback)
        if ollama_result["success"]:
            return ollama_result

        # Fallback: Could try OpenAI/Claude here if configured
        await self._notify(notify_callback, "⚠️ Ollama unavailable, no fallback configured")

        return {"success": False, "error": "No AI available"}

    async def _query_similar_solutions(self, error: str) -> List[Dict[str, Any]]:
        """Query vector DB for similar past solutions"""
        try:
            from src.core.modules.atomic.vector import VectorDBConnector, KnowledgeStore, KnowledgeSearch

            connector = VectorDBConnector(mode="local")
            connector.connect()

            store = KnowledgeStore(
                connector=connector,
                collection_name="flyto2_project_knowledge",
                embedding_provider="local"
            )

            search = KnowledgeSearch(knowledge_store=store)

            # Search for similar errors/solutions
            results = search.search_with_score_threshold(
                query=f"error solution: {error}",
                min_score=0.6,
                top_k=3
            )

            connector.disconnect()

            return results

        except Exception as e:
            print(f"⚠️ Vector DB query failed: {e}")
            return []

    async def _get_project_context(self) -> str:
        """Get project context for AI"""
        context = """
Flyto2 Project Context:

**Architecture**: Atomic module system
- Modules are small, reusable components
- Located in: src/core/modules/atomic/
- Categories: browser, string, array, math, object, file, datetime, data, utility

**Technology Stack**:
- Python 3.x with asyncio
- Playwright for browser automation
- YAML-based workflows
- Vector database (Qdrant/ChromaDB) for knowledge storage

**Common Modules**:
- browser.launch: Launch browser
- browser.goto: Navigate to URL
- browser.extract: Extract data from page
- browser.click, browser.type, browser.wait: Browser interactions

**Error Handling Philosophy**:
- Never give up on errors
- Auto-fix when possible
- Generate missing modules if needed
- Learn from every solution

**Project Root**: {project_root}
""".format(project_root=str(self.project_root))

        return context

    def _build_ai_prompt(
        self,
        error: str,
        context: str,
        similar_solutions: List[Dict],
        project_context: str
    ) -> str:
        """Build comprehensive prompt for AI"""
        prompt = f"""{project_context}

**Current Error**:
{error}

**Context**: {context}

**Similar Past Solutions**:
"""

        if similar_solutions:
            for i, sol in enumerate(similar_solutions, 1):
                content = sol.get('content', '')[:300]
                prompt += f"\n{i}. {content}\n"
        else:
            prompt += "\nNo similar solutions found in knowledge base.\n"

        prompt += """

**Your Task**:
Analyze this error and provide a solution. Return your response as JSON:

{
  "error_type": "category of error (e.g., missing_dependency, configuration, code_bug)",
  "root_cause": "explanation of what's wrong",
  "solution": "step-by-step solution",
  "commands": ["list", "of", "shell commands to run"],
  "needs_code_change": true/false,
  "code_changes": {
    "file_path": "path/to/file.py",
    "changes": "description of code changes needed"
  }
}

Be concise but complete. Focus on actionable solutions.
"""

        return prompt

    async def _ask_ollama(self, prompt: str, notify_callback=None) -> Dict[str, Any]:
        """Ask Ollama for solution"""
        try:
            import requests

            ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")

            await self._notify(notify_callback, "🤖 Asking Ollama...")

            response = requests.post(
                f"{ollama_url}/api/chat",
                json={
                    "model": "llama3.2",
                    "messages": [
                        {"role": "system", "content": "You are an expert DevOps engineer. Always respond with valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False
                },
                timeout=120
            )

            if response.status_code == 200:
                content = response.json()['message']['content']

                # Extract JSON
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    solution = json.loads(json_match.group())

                    return {
                        "success": True,
                        "solution": content,
                        "structured": solution,
                        "source": "ollama"
                    }

            return {"success": False, "error": f"Ollama returned status {response.status_code}"}

        except Exception as e:
            await self._notify(notify_callback, f"⚠️ Ollama error: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_solution(self, ai_solution: Dict[str, Any], notify_callback=None) -> Dict[str, Any]:
        """Execute AI-provided solution"""
        structured = ai_solution.get("structured", {})

        if not structured:
            return {"success": False, "error": "No structured solution provided"}

        # Execute commands
        commands = structured.get("commands", [])

        if commands:
            await self._notify(notify_callback, f"⚙️ Executing {len(commands)} commands...")

            for cmd in commands:
                await self._notify(notify_callback, f"  $ {cmd}")

                try:
                    # Parse command
                    if isinstance(cmd, str):
                        cmd_parts = cmd.split()
                    else:
                        cmd_parts = cmd

                    result = subprocess.run(
                        cmd_parts,
                        cwd=self.project_root,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )

                    if result.returncode != 0:
                        await self._notify(notify_callback, f"  ❌ Command failed: {result.stderr[:200]}")
                        return {
                            "success": False,
                            "error": f"Command failed: {cmd}",
                            "stderr": result.stderr
                        }

                    await self._notify(notify_callback, f"  ✅ Success")

                except Exception as e:
                    await self._notify(notify_callback, f"  ❌ Error: {e}")
                    return {"success": False, "error": str(e)}

        # TODO: Handle code changes if needed
        if structured.get("needs_code_change"):
            await self._notify(notify_callback, "⚠️ Code changes needed - requires human review")
            # For now, log it
            # In future, could use AI to generate code changes

        return {"success": True, "commands_executed": len(commands)}

    async def _store_solution(self, error: str, solution: Dict[str, Any], source: str):
        """Store successful solution to vector DB"""
        try:
            from src.core.modules.atomic.vector import VectorDBConnector, KnowledgeStore

            connector = VectorDBConnector(mode="local")
            connector.connect()

            store = KnowledgeStore(
                connector=connector,
                collection_name="flyto2_project_knowledge",
                embedding_provider="local"
            )

            content = f"""
Self-Healing Solution

Error: {error}

Solution Source: {source}
Action Taken: {solution.get('action', solution.get('solution', 'N/A')[:500])}

Status: SUCCESS

This solution was automatically discovered and executed by the self-healing system.
Future instances of this error can be resolved using this approach.
""".strip()

            store.add_entry(
                content=content,
                metadata={
                    "source": "self_healing_practice",
                    "category": "error_solution",
                    "solution_source": source,
                    "timestamp": datetime.now().isoformat(),
                    "auto_resolved": True
                }
            )

            connector.disconnect()
            print(f"✅ Solution stored to vector DB")

        except Exception as e:
            print(f"⚠️ Failed to store solution: {e}")

    async def _log_unsolved_problem(self, url: str, result: Dict[str, Any]):
        """Log unsolved problem for human review"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "errors": result.get("errors", []),
            "attempts": self.max_retries,
            "status": "unsolved",
            "needs_human_review": True
        }

        # Load existing log
        if self.healing_log.exists():
            with open(self.healing_log, 'r') as f:
                log_data = json.load(f)
        else:
            log_data = {"unsolved_problems": []}

        log_data["unsolved_problems"].append(log_entry)

        # Save
        with open(self.healing_log, 'w') as f:
            json.dump(log_data, f, indent=2)

        print(f"📝 Unsolved problem logged to {self.healing_log}")

    async def _notify(self, callback, message: str):
        """Send notification"""
        if callback:
            await callback(message)
        print(message)
