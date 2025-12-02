"""
Speed Race Modules - Wrapper for SpeedRace Engine

Allows workflows to execute speed races
"""

from src.core.modules.base import BaseModule
from src.core.modules.registry import register_module
from src.core.competition.speed_race import SpeedRace
from typing import Any, Dict


@register_module('competition.speed_race.run')
class RunSpeedRace(BaseModule):
    """
    Run a speed race competition

    Parameters:
        task_name (str): Name of the task being raced
        workflow_path (str): Path to workflow file
        rounds (int): Number of race rounds (default: 5)
        warmup_rounds (int): Number of warmup rounds (default: 1)
        params (dict): Workflow parameters (optional)

    Returns:
        Race results with timing statistics
    """

    module_name = "RunSpeedRace"
    module_description = "Execute a speed race competition"

    def validate_params(self):
        """Validate and extract parameters"""
        if "task_name" not in self.params:
            raise ValueError("Missing required parameter: task_name")
        if "workflow_path" not in self.params:
            raise ValueError("Missing required parameter: workflow_path")

        self.task_name = self.params["task_name"]
        self.workflow_path = self.params["workflow_path"]
        self.rounds = self.params.get("rounds", 5)
        self.warmup_rounds = self.params.get("warmup_rounds", 1)
        self.workflow_params = self.params.get("params", None)

    async def execute(self) -> Any:
        """
        Execute speed race

        Returns:
            Race results
        """
        try:
            engine = SpeedRace()
            result = await engine.run_race(
                task_name=self.task_name,
                workflow_path=self.workflow_path,
                params=self.workflow_params,
                rounds=self.rounds,
                warmup_rounds=self.warmup_rounds
            )

            return result

        except Exception as e:
            raise RuntimeError(f"Speed race failed: {str(e)}")


@register_module('competition.speed_race.leaderboard')
class GetLeaderboard(BaseModule):
    """
    Get speed race leaderboard

    Parameters:
        task_name (str): Filter by task name (optional)

    Returns:
        Leaderboard entries sorted by best time
    """

    module_name = "GetLeaderboard"
    module_description = "Get speed race leaderboard"

    def validate_params(self):
        """Validate and extract parameters"""
        self.task_name = self.params.get("task_name", None)

    async def execute(self) -> Any:
        """
        Get leaderboard

        Returns:
            Leaderboard data
        """
        try:
            engine = SpeedRace()
            leaderboard = engine.get_leaderboard(task_name=self.task_name)

            return {
                "leaderboard": leaderboard,
                "entry_count": len(leaderboard)
            }

        except Exception as e:
            raise RuntimeError(f"Failed to get leaderboard: {str(e)}")


@register_module('competition.speed_race.history')
class GetRaceHistory(BaseModule):
    """
    Get race history

    Parameters:
        task_name (str): Filter by task name (optional)
        limit (int): Maximum number of races to return (default: 10)

    Returns:
        List of race results
    """

    module_name = "GetRaceHistory"
    module_description = "Get speed race history"

    def validate_params(self):
        """Validate and extract parameters"""
        self.task_name = self.params.get("task_name", None)
        self.limit = self.params.get("limit", 10)

    async def execute(self) -> Any:
        """
        Get race history

        Returns:
            Race history
        """
        try:
            engine = SpeedRace()
            history = engine.get_race_history(task_name=self.task_name, limit=self.limit)

            return {
                "history": history,
                "race_count": len(history)
            }

        except Exception as e:
            raise RuntimeError(f"Failed to get race history: {str(e)}")


@register_module('competition.speed_race.compare')
class CompareRaces(BaseModule):
    """
    Compare multiple races

    Parameters:
        task_name (str): Task name to compare
        race_ids (list): Specific race indices to compare (optional)

    Returns:
        Comparison results
    """

    module_name = "CompareRaces"
    module_description = "Compare multiple speed races"

    def validate_params(self):
        """Validate and extract parameters"""
        if "task_name" not in self.params:
            raise ValueError("Missing required parameter: task_name")

        self.task_name = self.params["task_name"]
        self.race_ids = self.params.get("race_ids", None)

    async def execute(self) -> Any:
        """
        Compare races

        Returns:
            Comparison data
        """
        try:
            engine = SpeedRace()
            comparison = engine.compare_races(task_name=self.task_name, race_ids=self.race_ids)

            return comparison

        except Exception as e:
            raise RuntimeError(f"Failed to compare races: {str(e)}")
