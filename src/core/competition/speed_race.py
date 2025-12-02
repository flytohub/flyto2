"""
Speed Race Engine - Performance Competition System

Allows AI agent to compete against itself to improve speed:
1. Execute same task multiple times
2. Track execution time for each run
3. Compare performance across runs
4. Identify bottlenecks
5. Record best times (leaderboard)
"""

import asyncio
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from statistics import mean, median


class SpeedRace:
    """
    Speed racing engine for performance optimization
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize speed race engine

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.metrics_dir = self.project_root / "metrics"
        self.metrics_dir.mkdir(exist_ok=True)
        self.race_log = self.metrics_dir / "speed_races.json"

    async def run_race(
        self,
        task_name: str,
        workflow_path: str,
        params: Optional[Dict[str, Any]] = None,
        rounds: int = 5,
        warmup_rounds: int = 1
    ) -> Dict[str, Any]:
        """
        Run a speed race

        Args:
            task_name: Name of the task being raced
            workflow_path: Path to workflow file
            params: Workflow parameters
            rounds: Number of race rounds
            warmup_rounds: Number of warmup rounds (not counted)

        Returns:
            Race results with timing statistics
        """
        import subprocess
        import sys

        results = {
            "task_name": task_name,
            "workflow_path": workflow_path,
            "timestamp": datetime.now().isoformat(),
            "rounds": rounds,
            "warmup_rounds": warmup_rounds,
            "timings": [],
            "warmup_timings": [],
            "stats": {},
            "errors": [],
            "status": "started"
        }

        cli_script = self.project_root / "src" / "cli" / "main.py"

        # Warmup rounds
        print(f"🔥 Running {warmup_rounds} warmup round(s)...")
        for i in range(warmup_rounds):
            try:
                start_time = time.time()

                cmd = [sys.executable, str(cli_script), workflow_path]
                if params:
                    for key, value in params.items():
                        cmd.extend(["--param", f"{key}={value}"])

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 min timeout
                    cwd=self.project_root,
                    env={**subprocess.os.environ, "PYTHONPATH": str(self.project_root)}
                )

                elapsed = time.time() - start_time

                if result.returncode == 0:
                    results["warmup_timings"].append(elapsed)
                    print(f"  Warmup {i+1}/{warmup_rounds}: {elapsed:.2f}s ✓")
                else:
                    print(f"  Warmup {i+1}/{warmup_rounds}: Failed")
                    results["errors"].append(f"Warmup {i+1} failed: {result.stderr[:200]}")

            except subprocess.TimeoutExpired:
                results["errors"].append(f"Warmup {i+1} timeout")
            except Exception as e:
                results["errors"].append(f"Warmup {i+1} error: {str(e)}")

        # Race rounds
        print(f"\n🏁 Starting speed race: {rounds} rounds...")
        for i in range(rounds):
            try:
                start_time = time.time()

                cmd = [sys.executable, str(cli_script), workflow_path]
                if params:
                    for key, value in params.items():
                        cmd.extend(["--param", f"{key}={value}"])

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=self.project_root,
                    env={**subprocess.os.environ, "PYTHONPATH": str(self.project_root)}
                )

                elapsed = time.time() - start_time

                if result.returncode == 0:
                    results["timings"].append(elapsed)
                    print(f"  Round {i+1}/{rounds}: {elapsed:.2f}s ✓")
                else:
                    print(f"  Round {i+1}/{rounds}: Failed")
                    results["errors"].append(f"Round {i+1} failed: {result.stderr[:200]}")

            except subprocess.TimeoutExpired:
                results["errors"].append(f"Round {i+1} timeout")
                print(f"  Round {i+1}/{rounds}: Timeout ✗")
            except Exception as e:
                results["errors"].append(f"Round {i+1} error: {str(e)}")
                print(f"  Round {i+1}/{rounds}: Error ✗")

        # Calculate statistics
        if results["timings"]:
            timings = results["timings"]
            results["stats"] = {
                "best_time": min(timings),
                "worst_time": max(timings),
                "avg_time": mean(timings),
                "median_time": median(timings),
                "total_time": sum(timings),
                "success_rate": len(timings) / rounds,
                "speedup": max(timings) / min(timings) if min(timings) > 0 else 1.0
            }
            results["status"] = "completed"

            print(f"\n📊 Race Statistics:")
            print(f"  Best time:    {results['stats']['best_time']:.2f}s")
            print(f"  Worst time:   {results['stats']['worst_time']:.2f}s")
            print(f"  Average:      {results['stats']['avg_time']:.2f}s")
            print(f"  Median:       {results['stats']['median_time']:.2f}s")
            print(f"  Success rate: {results['stats']['success_rate']:.1%}")
            print(f"  Speedup:      {results['stats']['speedup']:.2f}x")
        else:
            results["status"] = "failed"
            print("\n❌ Race failed - no successful runs")

        # Log race results
        self._log_race(results)

        return results

    def _log_race(self, race_result: Dict[str, Any]):
        """Log race results to metrics file"""
        # Load existing log
        if self.race_log.exists():
            with open(self.race_log, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
        else:
            log_data = {"races": [], "total_races": 0}

        # Add new race
        log_data["races"].append(race_result)
        log_data["total_races"] += 1

        # Save updated log
        with open(self.race_log, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

    def get_race_history(self, task_name: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get race history

        Args:
            task_name: Filter by task name (optional)
            limit: Maximum number of races to return

        Returns:
            List of race results
        """
        if not self.race_log.exists():
            return []

        with open(self.race_log, 'r', encoding='utf-8') as f:
            log_data = json.load(f)

        races = log_data.get("races", [])

        # Filter by task name if specified
        if task_name:
            races = [r for r in races if r.get("task_name") == task_name]

        return races[-limit:]

    def get_leaderboard(self, task_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get leaderboard (best times per task)

        Args:
            task_name: Filter by task name (optional)

        Returns:
            Leaderboard entries sorted by best time
        """
        if not self.race_log.exists():
            return []

        with open(self.race_log, 'r', encoding='utf-8') as f:
            log_data = json.load(f)

        races = log_data.get("races", [])

        # Group by task name
        task_bests = {}
        for race in races:
            if race.get("status") != "completed":
                continue

            t_name = race.get("task_name")
            if task_name and t_name != task_name:
                continue

            best_time = race.get("stats", {}).get("best_time")
            if not best_time:
                continue

            if t_name not in task_bests or best_time < task_bests[t_name]["best_time"]:
                task_bests[t_name] = {
                    "task_name": t_name,
                    "best_time": best_time,
                    "avg_time": race.get("stats", {}).get("avg_time"),
                    "timestamp": race.get("timestamp"),
                    "rounds": race.get("rounds")
                }

        # Sort by best time
        leaderboard = sorted(task_bests.values(), key=lambda x: x["best_time"])

        return leaderboard

    def compare_races(self, task_name: str, race_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Compare multiple races for the same task

        Args:
            task_name: Task name to compare
            race_ids: Specific race indices to compare (optional, compares last 5 if not specified)

        Returns:
            Comparison results
        """
        races = self.get_race_history(task_name=task_name, limit=100)

        if race_ids:
            races = [races[i] for i in race_ids if i < len(races)]
        else:
            races = races[-5:]  # Last 5 races

        if not races:
            return {"error": "No races found for comparison"}

        comparison = {
            "task_name": task_name,
            "race_count": len(races),
            "races": [],
            "improvement": {}
        }

        for idx, race in enumerate(races):
            if race.get("status") == "completed":
                comparison["races"].append({
                    "index": idx,
                    "timestamp": race.get("timestamp"),
                    "best_time": race.get("stats", {}).get("best_time"),
                    "avg_time": race.get("stats", {}).get("avg_time"),
                    "success_rate": race.get("stats", {}).get("success_rate")
                })

        # Calculate improvement
        if len(comparison["races"]) >= 2:
            first = comparison["races"][0]
            last = comparison["races"][-1]

            comparison["improvement"] = {
                "best_time_change": last["best_time"] - first["best_time"],
                "avg_time_change": last["avg_time"] - first["avg_time"],
                "speedup": first["best_time"] / last["best_time"] if last["best_time"] > 0 else 1.0,
                "improved": last["best_time"] < first["best_time"]
            }

        return comparison
