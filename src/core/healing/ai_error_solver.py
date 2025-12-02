"""
AI Error Solver - Universal error resolution using AI

Core principle:
- NO hardcoded error handling
- ALL errors go to AI
- AI provides solutions
- Record attempts and results
- Train similarity matching
- Store only successful solutions

Flow:
1. Error occurs
2. Query vector DB for similar past solutions
3. If high similarity (>0.8) → use directly
4. Else → ask AI (with full context)
5. Execute AI's solution
6. Record: error + AI response + solution + result
7. If success → store to vector DB
8. Train: compare AI response vs actual working solution
9. Update similarity score
"""

import asyncio
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import os


class AIErrorSolver:
    """
    Universal AI-powered error solver

    - Query vector DB for past solutions
    - Consult AI with full context
    - Execute solutions
    - Train similarity matching
    - Never hardcode error handling
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.solution_log = self.project_root / "metrics" / "ai_solutions.json"
        self.solution_log.parent.mkdir(exist_ok=True)

    async def solve_error(
        self,
        error: Exception,
        context: Dict[str, Any],
        notify_callback=None
    ) -> Dict[str, Any]:
        """
        Solve any error using AI

        Args:
            error: The exception that occurred
            context: Full context (operation, params, stack trace, etc.)
            notify_callback: Progress notification callback

        Returns:
            Solution result with success status
        """
        error_str = str(error)
        error_type = type(error).__name__

        await self._notify(notify_callback, f"❌ Error: {error_type}")
        await self._notify(notify_callback, f"📝 Recording error context...")

        # Build error record
        error_record = {
            "error": error_str,
            "error_type": error_type,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "attempts": []
        }

        # Step 1: Query vector DB for similar solutions
        await self._notify(notify_callback, "🔍 Searching vector DB for similar solutions...")
        similar_solutions = await self._query_similar_solutions(error_str, error_type)

        if similar_solutions:
            await self._notify(notify_callback, f"📚 Found {len(similar_solutions)} similar past solutions")

            # Check if any has high similarity
            best_match = similar_solutions[0]
            similarity = best_match.get("similarity", 0.0)

            if similarity > 0.8:
                await self._notify(notify_callback, f"✨ High similarity ({similarity:.0%}) - using proven solution")

                # Use proven solution directly
                solution = best_match.get("solution_data", {})
                result = await self._execute_solution(solution, context, notify_callback)

                error_record["attempts"].append({
                    "source": "vector_db",
                    "similarity": similarity,
                    "solution": solution,
                    "result": "success" if result["success"] else "failed"
                })

                if result["success"]:
                    await self._notify(notify_callback, "✅ Proven solution worked!")
                    return result

                await self._notify(notify_callback, "⚠️ Proven solution failed, asking AI...")
        else:
            await self._notify(notify_callback, "📭 No similar solutions found in vector DB")

        # Step 2: Ask AI for solution
        await self._notify(notify_callback, "🤖 Consulting AI for solution...")
        ai_solution = await self._ask_ai_for_solution(
            error_str,
            error_type,
            context,
            similar_solutions,
            notify_callback
        )

        if not ai_solution["success"]:
            await self._notify(notify_callback, "❌ AI consultation failed")
            return {"success": False, "error": "AI consultation failed"}

        await self._notify(notify_callback, f"💡 AI provided solution: {ai_solution['summary']}")

        # Step 3: Execute AI's solution
        result = await self._execute_solution(
            ai_solution["structured"],
            context,
            notify_callback
        )

        error_record["attempts"].append({
            "source": "ai",
            "ai_response": ai_solution["full_response"],
            "solution": ai_solution["structured"],
            "result": "success" if result["success"] else "failed"
        })

        # Step 4: If successful, store and train
        if result["success"]:
            await self._notify(notify_callback, "✅ AI solution worked!")

            # Store successful solution
            await self._store_successful_solution(
                error_str,
                error_type,
                error_record,
                ai_solution,
                notify_callback
            )

            # Train similarity
            await self._train_similarity(
                error_str,
                ai_solution,
                result,
                notify_callback
            )
        else:
            await self._notify(notify_callback, "❌ AI solution failed")

        # Save error record
        await self._save_error_record(error_record)

        return result

    async def _query_similar_solutions(
        self,
        error: str,
        error_type: str
    ) -> List[Dict[str, Any]]:
        """Query vector DB for similar past successful solutions"""
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

            # Search for similar errors and their solutions
            results = search.search_with_score_threshold(
                query=f"error: {error_type} {error}",
                min_score=0.5,
                top_k=5
            )

            connector.disconnect()

            # Filter for successful solutions only
            solutions = []
            for result in results:
                metadata = result.get("metadata", {})
                if metadata.get("solution_success"):
                    solutions.append({
                        "similarity": result.get("score", 0.0),
                        "content": result.get("content", ""),
                        "solution_data": metadata.get("solution_data", {}),
                        "timestamp": metadata.get("timestamp")
                    })

            return solutions

        except Exception as e:
            print(f"⚠️ Vector DB query error: {e}")
            return []

    async def _ask_ai_for_solution(
        self,
        error: str,
        error_type: str,
        context: Dict[str, Any],
        similar_solutions: List[Dict[str, Any]],
        notify_callback=None
    ) -> Dict[str, Any]:
        """Ask AI to provide solution with full context"""

        # Build comprehensive prompt
        prompt = self._build_ai_prompt(error, error_type, context, similar_solutions)

        # Try Ollama
        result = await self._ask_ollama(prompt, notify_callback)

        if result["success"]:
            return result

        # TODO: Fallback to OpenAI/Claude if configured

        return {"success": False}

    def _build_ai_prompt(
        self,
        error: str,
        error_type: str,
        context: Dict[str, Any],
        similar_solutions: List[Dict[str, Any]]
    ) -> str:
        """Build comprehensive prompt for AI"""

        project_context = """
Flyto2 Project Context:

**Architecture**: Atomic module system
- Location: src/core/modules/atomic/
- Categories: browser, string, array, math, object, file, datetime, data, utility
- Modules are small, reusable Python classes
- Workflows are YAML-based

**Technology Stack**:
- Python 3.x with asyncio
- Playwright for browser automation
- YAML workflows
- Vector database (Qdrant/ChromaDB)
- Ollama for AI

**Philosophy**:
- Never give up on errors
- Self-healing and auto-recovery
- Learn from every solution
- Generate missing modules when needed

**Common Commands**:
- playwright install [browser]
- pip install [package]
- python -m [module]
"""

        prompt = f"""{project_context}

**Current Error**:
Type: {error_type}
Message: {error}

**Context**:
{json.dumps(context, indent=2)[:1000]}

**Similar Past Solutions**:
"""

        if similar_solutions:
            for i, sol in enumerate(similar_solutions[:3], 1):
                content = sol.get("content", "")[:300]
                similarity = sol.get("similarity", 0.0)
                prompt += f"\n{i}. (Similarity: {similarity:.0%})\n{content}\n"
        else:
            prompt += "\nNo similar solutions found in knowledge base.\n"

        prompt += """

**Your Task**:
Analyze this error and provide a practical solution.

Return your response as JSON:
{
  "error_analysis": "What caused this error",
  "solution_type": "command/code_change/configuration/install",
  "solution_summary": "Brief description",
  "commands": ["list", "of", "commands", "to", "run"],
  "code_changes": {
    "file": "path/to/file.py",
    "description": "what to change"
  },
  "explanation": "Why this solution works"
}

Be specific and actionable. Provide exact commands to run.
"""

        return prompt

    async def _ask_ollama(self, prompt: str, notify_callback=None) -> Dict[str, Any]:
        """Ask Ollama for solution"""
        try:
            import requests

            ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")

            response = requests.post(
                f"{ollama_url}/api/chat",
                json={
                    "model": "llama3.2",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert DevOps and Python engineer. Always respond with valid JSON."
                        },
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
                    structured = json.loads(json_match.group())

                    # Validate required fields
                    if "solution_summary" in structured:
                        return {
                            "success": True,
                            "full_response": content,
                            "structured": structured,
                            "summary": structured.get("solution_summary", "")
                        }

            return {"success": False, "error": "Invalid response from Ollama"}

        except Exception as e:
            await self._notify(notify_callback, f"⚠️ Ollama error: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_solution(
        self,
        solution: Dict[str, Any],
        context: Dict[str, Any],
        notify_callback=None
    ) -> Dict[str, Any]:
        """Execute the AI-provided solution"""

        commands = solution.get("commands", [])

        if not commands:
            return {"success": False, "error": "No commands to execute"}

        await self._notify(notify_callback, f"⚙️ Executing {len(commands)} commands...")

        for cmd in commands:
            if isinstance(cmd, str):
                cmd_str = cmd
                cmd_parts = cmd.split()
            else:
                cmd_parts = cmd
                cmd_str = " ".join(cmd)

            await self._notify(notify_callback, f"  $ {cmd_str}")

            try:
                result = subprocess.run(
                    cmd_parts,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode != 0:
                    await self._notify(notify_callback, f"  ❌ Failed: {result.stderr[:200]}")
                    return {
                        "success": False,
                        "error": f"Command failed: {cmd_str}",
                        "stderr": result.stderr
                    }

                await self._notify(notify_callback, f"  ✅ Success")

            except Exception as e:
                await self._notify(notify_callback, f"  ❌ Error: {e}")
                return {"success": False, "error": str(e)}

        return {"success": True, "commands_executed": len(commands)}

    async def _store_successful_solution(
        self,
        error: str,
        error_type: str,
        error_record: Dict[str, Any],
        ai_solution: Dict[str, Any],
        notify_callback=None
    ):
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

            # Create comprehensive knowledge entry
            content = f"""
AI Error Solution (SUCCESS)

Error Type: {error_type}
Error: {error}

AI Analysis: {ai_solution['structured'].get('error_analysis', 'N/A')}

Solution Type: {ai_solution['structured'].get('solution_type', 'N/A')}
Solution: {ai_solution['structured'].get('solution_summary', 'N/A')}

Commands Executed:
{chr(10).join(f"  - {cmd}" for cmd in ai_solution['structured'].get('commands', []))}

Explanation: {ai_solution['structured'].get('explanation', 'N/A')}

This solution was AI-generated and successfully resolved the error.
""".strip()

            store.add_entry(
                content=content,
                metadata={
                    "source": "ai_error_solver",
                    "category": "successful_solution",
                    "error_type": error_type,
                    "solution_success": True,
                    "solution_data": ai_solution['structured'],
                    "timestamp": datetime.now().isoformat()
                }
            )

            connector.disconnect()

            await self._notify(notify_callback, "💾 Solution stored to vector DB")

        except Exception as e:
            print(f"⚠️ Failed to store solution: {e}")

    async def _train_similarity(
        self,
        error: str,
        ai_solution: Dict[str, Any],
        result: Dict[str, Any],
        notify_callback=None
    ):
        """
        Train similarity matching

        Compare:
        - AI's full response
        - What actually worked

        Calculate similarity and store for future matching
        """
        # TODO: Implement similarity training
        # This would:
        # 1. Extract key points from AI response
        # 2. Compare with actual executed commands
        # 3. Calculate matching score
        # 4. Update vector DB with similarity score

        await self._notify(notify_callback, "📊 Training similarity matching...")

    async def _save_error_record(self, error_record: Dict[str, Any]):
        """Save error record to log file"""
        try:
            # Load existing log
            if self.solution_log.exists():
                with open(self.solution_log, 'r') as f:
                    log_data = json.load(f)
            else:
                log_data = {"solutions": []}

            # Add new record
            log_data["solutions"].append(error_record)

            # Save
            with open(self.solution_log, 'w') as f:
                json.dump(log_data, f, indent=2)

        except Exception as e:
            print(f"⚠️ Failed to save error record: {e}")

    async def _notify(self, callback, message: str):
        """Send notification"""
        if callback:
            await callback(message)
        print(message)
