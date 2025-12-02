"""
Solution Archiver Module - Archive successful solutions

Atomic responsibility: Store and log successful solutions
Extracted from: ai_error_solver.py lines 419-496, 646-664
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from src.core.utils.vector_db_manager import vector_store
from src.core.utils.translator import translate_to_english
from src.core.utils.notifier import notify


class SolutionArchiverModule:
    """
    Archive successful solutions to vector DB and log files

    Single responsibility: Persist successful solutions for future reference
    """

    @staticmethod
    async def archive(
        error: str,
        error_type: str,
        error_record: Dict[str, Any],
        ai_solution: Dict[str, Any],
        project_root: Optional[Path] = None,
        notify_callback: Optional[callable] = None
    ):
        """
        Archive successful solution

        Args:
            error: Error message
            error_type: Error type
            error_record: Complete error record with attempts
            ai_solution: AI solution that worked
            project_root: Project root directory
            notify_callback: Optional notification callback
        """
        # Store to vector DB (in English)
        await SolutionArchiverModule._store_to_vector_db(
            error=error,
            error_type=error_type,
            ai_solution=ai_solution,
            notify_callback=notify_callback
        )

        # Store to log file (original language)
        await SolutionArchiverModule._store_to_log(
            error_record=error_record,
            project_root=project_root
        )

    @staticmethod
    async def _store_to_vector_db(
        error: str,
        error_type: str,
        ai_solution: Dict[str, Any],
        notify_callback: Optional[callable] = None
    ):
        """Store successful solution to vector DB (in English)"""
        try:
            await notify("🌐 Translating to English for vector DB...", notify_callback)

            # Translate all content to English
            error_en = await translate_to_english(error, context="error")
            analysis_en = await translate_to_english(
                ai_solution['structured'].get('error_analysis', 'N/A'),
                context="error"
            )
            solution_summary_en = await translate_to_english(
                ai_solution['structured'].get('solution_summary', 'N/A'),
                context="solution"
            )
            explanation_en = await translate_to_english(
                ai_solution['structured'].get('explanation', 'N/A'),
                context="solution"
            )

            # Create comprehensive knowledge entry (ALL IN ENGLISH)
            content = f"""
AI Error Solution (SUCCESS)

Error Type: {error_type}
Error: {error_en}

AI Analysis: {analysis_en}

Solution Type: {ai_solution['structured'].get('solution_type', 'N/A')}
Solution: {solution_summary_en}

Commands Executed:
{chr(10).join(f"  - {cmd}" for cmd in ai_solution['structured'].get('commands', []))}

Explanation: {explanation_en}

This solution was AI-generated and successfully resolved the error.
""".strip()

            # Store to vector DB
            await vector_store(
                content=content,
                metadata={
                    "source": "ai_error_solver",
                    "category": "successful_solution",
                    "error_type": error_type,
                    "solution_success": True,
                    "solution_data": ai_solution['structured'],
                    "original_error": error,  # Keep original for reference
                    "timestamp": datetime.now().isoformat()
                }
            )

            await notify("💾 Solution stored to vector DB (English)", notify_callback)

        except Exception as e:
            print(f"⚠️ Failed to store solution to vector DB: {e}")

    @staticmethod
    async def _store_to_log(
        error_record: Dict[str, Any],
        project_root: Optional[Path] = None
    ):
        """Save error record to log file"""
        try:
            if project_root is None:
                project_root = Path.cwd()

            solution_log = project_root / "metrics" / "ai_solutions.json"
            solution_log.parent.mkdir(exist_ok=True)

            # Load existing log
            if solution_log.exists():
                with open(solution_log, 'r') as f:
                    log_data = json.load(f)
            else:
                log_data = {"solutions": []}

            # Add new record
            log_data["solutions"].append(error_record)

            # Save
            with open(solution_log, 'w') as f:
                json.dump(log_data, f, indent=2)

        except Exception as e:
            print(f"⚠️ Failed to save error record: {e}")
