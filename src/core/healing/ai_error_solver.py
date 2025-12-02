"""
AI Error Solver - Universal error resolution using AI (Refactored)

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

REFACTORED: Now uses atomic modules for each concern
- Reduced from 670 lines to ~150 lines
- Each responsibility is in its own atomic module
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from src.core.healing.atomic import (
    VectorQueryModule,
    PromptBuilderModule,
    AIConsulterModule,
    SolutionExecutorModule,
    SimilarityTrainerModule,
    SolutionArchiverModule
)
from src.core.utils.notifier import Notifier


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
        # Initialize notifier
        notifier = Notifier(callback=notify_callback)

        error_str = str(error)
        error_type = type(error).__name__

        await notifier.notify(f"❌ Error: {error_type}")
        await notifier.notify(f"📝 Recording error context...")

        # Build error record
        error_record = {
            "error": error_str,
            "error_type": error_type,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "attempts": []
        }

        # Step 1: Query vector DB for similar solutions
        await notifier.notify("🔍 Searching vector DB for similar solutions...")

        similar_solutions = await VectorQueryModule.query_similar_solutions(
            error=error_str,
            error_type=error_type,
            min_score=0.5,
            top_k=5
        )

        if similar_solutions:
            await notifier.notify(f"📚 Found {len(similar_solutions)} similar past solutions")

            # Check if any has high similarity
            best_match = similar_solutions[0]
            similarity = best_match.get("similarity", 0.0)

            if similarity > 0.8:
                await notifier.notify(f"✨ High similarity ({similarity:.0%}) - using proven solution")

                # Use proven solution directly
                solution = best_match.get("solution_data", {})
                result = await SolutionExecutorModule.execute(
                    solution=solution,
                    project_root=self.project_root,
                    notify_callback=notify_callback
                )

                error_record["attempts"].append({
                    "source": "vector_db",
                    "similarity": similarity,
                    "solution": solution,
                    "result": "success" if result["success"] else "failed"
                })

                if result["success"]:
                    await notifier.notify("✅ Proven solution worked!")
                    return result

                await notifier.notify("⚠️ Proven solution failed, asking AI...")
        else:
            await notifier.notify("📭 No similar solutions found in vector DB")

        # Step 2: Build prompt and ask AI for solution
        await notifier.notify("🤖 Consulting AI for solution...")

        prompt = PromptBuilderModule.build_error_resolution_prompt(
            error=error_str,
            error_type=error_type,
            context=context,
            similar_solutions=similar_solutions
        )

        ai_solution = await AIConsulterModule.consult(
            prompt=prompt,
            notify_callback=notify_callback
        )

        if not ai_solution["success"]:
            await notifier.notify("❌ AI consultation failed")
            return {"success": False, "error": "AI consultation failed"}

        await notifier.notify(f"💡 AI provided solution: {ai_solution['summary']}")

        # Step 3: Execute AI's solution
        result = await SolutionExecutorModule.execute(
            solution=ai_solution["structured"],
            project_root=self.project_root,
            notify_callback=notify_callback
        )

        error_record["attempts"].append({
            "source": "ai",
            "ai_response": ai_solution["full_response"],
            "solution": ai_solution["structured"],
            "result": "success" if result["success"] else "failed"
        })

        # Step 4: If successful, archive and train
        if result["success"]:
            await notifier.notify("✅ AI solution worked!")

            # Archive successful solution
            await SolutionArchiverModule.archive(
                error=error_str,
                error_type=error_type,
                error_record=error_record,
                ai_solution=ai_solution,
                project_root=self.project_root,
                notify_callback=notify_callback
            )

            # Train similarity
            await SimilarityTrainerModule.train(
                error=error_str,
                ai_solution=ai_solution,
                execution_result=result,
                notify_callback=notify_callback
            )
        else:
            await notifier.notify("❌ AI solution failed")

        return result
