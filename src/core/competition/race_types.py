"""
Additional Race Types for Competition System
Extends SpeedRace with accuracy, strategy, battle, and stress race modes
"""
import asyncio
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from statistics import mean


class AccuracyRace:
    """
    Accuracy Race - Compete on extraction precision
    Measures how accurately modules extract target data
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.metrics_dir = self.project_root / "metrics"
        self.metrics_dir.mkdir(exist_ok=True)
        self.accuracy_log = self.metrics_dir / "accuracy_races.json"

    async def run_accuracy_race(
        self,
        task_name: str,
        extractor: Callable,
        test_cases: List[Dict[str, Any]],
        rounds: int = 3
    ) -> Dict[str, Any]:
        """
        Run accuracy race

        Args:
            task_name: Name of extraction task
            extractor: Async function that extracts data
            test_cases: List of test cases with expected results
            rounds: Number of rounds to run

        Returns:
            Race results with accuracy scores
        """
        results = []

        for round_num in range(rounds):
            round_start = time.time()
            correct = 0
            total = len(test_cases)

            for test_case in test_cases:
                try:
                    actual = await extractor(test_case['input'])
                    expected = test_case['expected']

                    if self._compare_results(actual, expected):
                        correct += 1
                except Exception:
                    pass  # Extraction failed counts as incorrect

            accuracy = (correct / total) * 100 if total > 0 else 0
            round_time = time.time() - round_start

            results.append({
                'round': round_num + 1,
                'accuracy': accuracy,
                'correct': correct,
                'total': total,
                'time': round_time
            })

        # Calculate statistics
        accuracies = [r['accuracy'] for r in results]
        avg_accuracy = mean(accuracies)
        best_accuracy = max(accuracies)

        race_result = {
            'task_name': task_name,
            'timestamp': datetime.now().isoformat(),
            'rounds': rounds,
            'results': results,
            'avg_accuracy': avg_accuracy,
            'best_accuracy': best_accuracy,
            'status': 'completed'
        }

        self._save_result(race_result)
        return race_result

    def _compare_results(self, actual: Any, expected: Any) -> bool:
        """Compare actual vs expected results"""
        if type(actual) != type(expected):
            return False
        if isinstance(actual, (list, dict)):
            return json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True)
        return actual == expected

    def _save_result(self, result: Dict[str, Any]):
        """Save race result to file"""
        results = []
        if self.accuracy_log.exists():
            with open(self.accuracy_log, 'r') as f:
                results = json.load(f)

        results.append(result)

        with open(self.accuracy_log, 'w') as f:
            json.dump(results, f, indent=2)


class StrategyRace:
    """
    Strategy Race - Compare Fast/Balanced/Safe strategies
    Tests different execution strategies for same task
    """

    STRATEGIES = {
        'fast': {'timeout': 5, 'retries': 0, 'parallel': True},
        'balanced': {'timeout': 15, 'retries': 2, 'parallel': True},
        'safe': {'timeout': 30, 'retries': 5, 'parallel': False}
    }

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.metrics_dir = self.project_root / "metrics"
        self.metrics_dir.mkdir(exist_ok=True)
        self.strategy_log = self.metrics_dir / "strategy_races.json"

    async def run_strategy_race(
        self,
        task_name: str,
        task_func: Callable,
        task_params: Dict[str, Any],
        rounds: int = 3
    ) -> Dict[str, Any]:
        """
        Run strategy comparison race

        Args:
            task_name: Name of task
            task_func: Async function to execute
            task_params: Parameters for task
            rounds: Number of rounds per strategy

        Returns:
            Comparison results across strategies
        """
        strategy_results = {}

        for strategy_name, config in self.STRATEGIES.items():
            results = []

            for round_num in range(rounds):
                try:
                    start_time = time.time()
                    result = await asyncio.wait_for(
                        task_func(**task_params, strategy_config=config),
                        timeout=config['timeout']
                    )
                    execution_time = time.time() - start_time

                    results.append({
                        'round': round_num + 1,
                        'success': True,
                        'time': execution_time,
                        'result': result
                    })
                except asyncio.TimeoutError:
                    results.append({
                        'round': round_num + 1,
                        'success': False,
                        'error': 'timeout'
                    })
                except Exception as e:
                    results.append({
                        'round': round_num + 1,
                        'success': False,
                        'error': str(e)
                    })

            # Calculate statistics
            successful = [r for r in results if r.get('success')]
            success_rate = (len(successful) / len(results)) * 100

            strategy_results[strategy_name] = {
                'config': config,
                'results': results,
                'success_rate': success_rate,
                'avg_time': mean([r['time'] for r in successful]) if successful else None
            }

        race_result = {
            'task_name': task_name,
            'timestamp': datetime.now().isoformat(),
            'strategies': strategy_results,
            'winner': self._determine_winner(strategy_results),
            'status': 'completed'
        }

        self._save_result(race_result)
        return race_result

    def _determine_winner(self, results: Dict[str, Any]) -> str:
        """Determine winning strategy based on success rate and speed"""
        best_strategy = None
        best_score = 0

        for strategy, data in results.items():
            # Score = success_rate + speed_bonus
            success = data['success_rate']
            speed_bonus = 0

            if data['avg_time'] is not None:
                # Faster = higher bonus (inverse time)
                speed_bonus = min(50, 100 / (data['avg_time'] + 1))

            score = success + speed_bonus

            if score > best_score:
                best_score = score
                best_strategy = strategy

        return best_strategy or 'none'

    def _save_result(self, result: Dict[str, Any]):
        """Save race result to file"""
        results = []
        if self.strategy_log.exists():
            with open(self.strategy_log, 'r') as f:
                results = json.load(f)

        results.append(result)

        with open(self.strategy_log, 'w') as f:
            json.dump(results, f, indent=2)


class ModuleBattle:
    """
    Module Battle - Head-to-head module comparison
    Two modules compete on same task
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.metrics_dir = self.project_root / "metrics"
        self.metrics_dir.mkdir(exist_ok=True)
        self.battle_log = self.metrics_dir / "module_battles.json"

    async def run_battle(
        self,
        module_a_name: str,
        module_a_func: Callable,
        module_b_name: str,
        module_b_func: Callable,
        test_params: Dict[str, Any],
        rounds: int = 5
    ) -> Dict[str, Any]:
        """
        Run module battle

        Args:
            module_a_name: Name of first module
            module_a_func: First module function
            module_b_name: Name of second module
            module_b_func: Second module function
            test_params: Parameters for both modules
            rounds: Number of rounds

        Returns:
            Battle results
        """
        module_a_wins = 0
        module_b_wins = 0
        draws = 0
        round_results = []

        for round_num in range(rounds):
            # Run both modules concurrently
            start_a = time.time()
            start_b = time.time()

            results = await asyncio.gather(
                module_a_func(**test_params),
                module_b_func(**test_params),
                return_exceptions=True
            )

            time_a = time.time() - start_a
            time_b = time.time() - start_b

            # Determine winner
            success_a = not isinstance(results[0], Exception)
            success_b = not isinstance(results[1], Exception)

            if success_a and not success_b:
                winner = module_a_name
                module_a_wins += 1
            elif success_b and not success_a:
                winner = module_b_name
                module_b_wins += 1
            elif success_a and success_b:
                # Both succeeded - faster wins
                if time_a < time_b:
                    winner = module_a_name
                    module_a_wins += 1
                elif time_b < time_a:
                    winner = module_b_name
                    module_b_wins += 1
                else:
                    winner = 'draw'
                    draws += 1
            else:
                winner = 'draw'
                draws += 1

            round_results.append({
                'round': round_num + 1,
                'module_a': {
                    'time': time_a,
                    'success': success_a,
                    'result': str(results[0])[:100] if success_a else str(results[0])
                },
                'module_b': {
                    'time': time_b,
                    'success': success_b,
                    'result': str(results[1])[:100] if success_b else str(results[1])
                },
                'winner': winner
            })

        battle_result = {
            'timestamp': datetime.now().isoformat(),
            'module_a': module_a_name,
            'module_b': module_b_name,
            'rounds': rounds,
            'results': round_results,
            'module_a_wins': module_a_wins,
            'module_b_wins': module_b_wins,
            'draws': draws,
            'overall_winner': self._determine_battle_winner(module_a_name, module_a_wins, module_b_name, module_b_wins, draws),
            'status': 'completed'
        }

        self._save_result(battle_result)
        return battle_result

    def _determine_battle_winner(self, name_a: str, wins_a: int, name_b: str, wins_b: int, draws: int) -> str:
        """Determine overall battle winner"""
        if wins_a > wins_b:
            return name_a
        elif wins_b > wins_a:
            return name_b
        else:
            return 'draw'

    def _save_result(self, result: Dict[str, Any]):
        """Save battle result to file"""
        results = []
        if self.battle_log.exists():
            with open(self.battle_log, 'r') as f:
                results = json.load(f)

        results.append(result)

        with open(self.battle_log, 'w') as f:
            json.dump(results, f, indent=2)


class StressRace:
    """
    Stress Race - Stability under high concurrency
    Tests which module maintains stability under load
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.metrics_dir = self.project_root / "metrics"
        self.metrics_dir.mkdir(exist_ok=True)
        self.stress_log = self.metrics_dir / "stress_races.json"

    async def run_stress_race(
        self,
        task_name: str,
        task_func: Callable,
        task_params: Dict[str, Any],
        concurrency_levels: List[int] = [10, 50, 100]
    ) -> Dict[str, Any]:
        """
        Run stress race at different concurrency levels

        Args:
            task_name: Name of task
            task_func: Async function to test
            task_params: Parameters for function
            concurrency_levels: List of concurrency levels to test

        Returns:
            Stress test results
        """
        level_results = {}

        for level in concurrency_levels:
            start_time = time.time()

            # Create concurrent tasks
            tasks = [task_func(**task_params) for _ in range(level)]

            # Execute all concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            execution_time = time.time() - start_time

            # Analyze results
            successful = sum(1 for r in results if not isinstance(r, Exception))
            failed = level - successful
            success_rate = (successful / level) * 100

            level_results[f'concurrency_{level}'] = {
                'level': level,
                'successful': successful,
                'failed': failed,
                'success_rate': success_rate,
                'total_time': execution_time,
                'throughput': level / execution_time if execution_time > 0 else 0
            }

        race_result = {
            'task_name': task_name,
            'timestamp': datetime.now().isoformat(),
            'concurrency_levels': concurrency_levels,
            'results': level_results,
            'max_stable_level': self._find_max_stable_level(level_results),
            'status': 'completed'
        }

        self._save_result(race_result)
        return race_result

    def _find_max_stable_level(self, results: Dict[str, Any]) -> int:
        """Find maximum concurrency level with >95% success rate"""
        max_level = 0

        for level_key, data in results.items():
            if data['success_rate'] >= 95.0:
                max_level = max(max_level, data['level'])

        return max_level

    def _save_result(self, result: Dict[str, Any]):
        """Save stress race result to file"""
        results = []
        if self.stress_log.exists():
            with open(self.stress_log, 'r') as f:
                results = json.load(f)

        results.append(result)

        with open(self.stress_log, 'w') as f:
            json.dump(results, f, indent=2)
