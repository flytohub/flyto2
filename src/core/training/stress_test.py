"""
Stress Test Engine
Provides reusable stress testing capabilities for workflows and modules
"""
import asyncio
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime


@dataclass
class StressTestResult:
    """Results from a stress test execution"""
    total: int
    successful: int
    failed: int
    duration: float
    ops_per_second: float
    success_rate: float
    errors: List[Dict[str, Any]]


class StressTestEngine:
    """
    Engine for running stress tests on workflows and modules
    """

    def __init__(self, min_success_rate: float = 95.0):
        """
        Initialize stress test engine

        Args:
            min_success_rate: Minimum acceptable success rate (0-100)
        """
        self.min_success_rate = min_success_rate
        self.results_history = []

    async def run_burst_test(
        self,
        operation: Callable,
        operation_params: List[Dict[str, Any]],
        concurrency: int = 100
    ) -> StressTestResult:
        """
        Run burst test with specified concurrency

        Args:
            operation: Async function to test
            operation_params: List of parameter dicts for each operation
            concurrency: Number of concurrent operations

        Returns:
            StressTestResult with test outcomes
        """
        if len(operation_params) < concurrency:
            raise ValueError(f"Need at least {concurrency} parameter sets for {concurrency} concurrent operations")

        # Create tasks
        tasks = []
        for i in range(concurrency):
            params = operation_params[i]
            tasks.append(self._run_single_operation(operation, params, i))

        # Execute all concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.time() - start_time

        # Analyze results
        successful = sum(1 for r in results if isinstance(r, dict) and r.get('success', False))
        failed = concurrency - successful
        success_rate = (successful / concurrency) * 100
        ops_per_second = concurrency / duration if duration > 0 else 0

        # Collect errors
        errors = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                errors.append({
                    'op_id': i,
                    'error_type': type(result).__name__,
                    'error_message': str(result)
                })
            elif isinstance(result, dict) and not result.get('success', False):
                errors.append({
                    'op_id': i,
                    'error': result.get('error', 'Unknown error')
                })

        # Create result object
        test_result = StressTestResult(
            total=concurrency,
            successful=successful,
            failed=failed,
            duration=duration,
            ops_per_second=ops_per_second,
            success_rate=success_rate,
            errors=errors
        )

        # Save to history
        self.results_history.append({
            'timestamp': datetime.now().isoformat(),
            'result': test_result
        })

        return test_result

    async def _run_single_operation(
        self,
        operation: Callable,
        params: Dict[str, Any],
        op_id: int
    ) -> Dict[str, Any]:
        """Run a single operation and return result"""
        try:
            result = await operation(**params)
            return {
                'success': True,
                'op_id': op_id,
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'op_id': op_id,
                'error': str(e)
            }

    def validate_result(self, result: StressTestResult) -> bool:
        """
        Validate if test result meets success criteria

        Args:
            result: StressTestResult to validate

        Returns:
            True if success rate meets minimum threshold
        """
        return result.success_rate >= self.min_success_rate

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get aggregate statistics from all test runs

        Returns:
            Dictionary with aggregate stats
        """
        if not self.results_history:
            return {
                'total_tests': 0,
                'avg_success_rate': 0.0,
                'avg_ops_per_second': 0.0
            }

        success_rates = [h['result'].success_rate for h in self.results_history]
        ops_per_sec = [h['result'].ops_per_second for h in self.results_history]

        return {
            'total_tests': len(self.results_history),
            'avg_success_rate': sum(success_rates) / len(success_rates),
            'avg_ops_per_second': sum(ops_per_sec) / len(ops_per_sec),
            'min_success_rate': min(success_rates),
            'max_success_rate': max(success_rates)
        }

    def generate_report(self, result: StressTestResult) -> str:
        """
        Generate human-readable test report

        Args:
            result: StressTestResult to report on

        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 70)
        report.append("STRESS TEST REPORT")
        report.append("=" * 70)
        report.append(f"Total operations:   {result.total}")
        report.append(f"Successful:         {result.successful}")
        report.append(f"Failed:             {result.failed}")
        report.append(f"Success rate:       {result.success_rate:.1f}%")
        report.append(f"Duration:           {result.duration:.2f}s")
        report.append(f"Ops/second:         {result.ops_per_second:.1f}")
        report.append("")

        if result.errors:
            report.append(f"Errors ({len(result.errors)}):")
            for error in result.errors[:10]:  # Show first 10 errors
                report.append(f"  Op {error.get('op_id')}: {error.get('error', error.get('error_message', 'Unknown'))}")
            if len(result.errors) > 10:
                report.append(f"  ... and {len(result.errors) - 10} more")
            report.append("")

        # Validation
        is_valid = self.validate_result(result)
        if is_valid:
            report.append(f"✅ PASS: Success rate {result.success_rate:.1f}% >= {self.min_success_rate}%")
        else:
            report.append(f"❌ FAIL: Success rate {result.success_rate:.1f}% < {self.min_success_rate}%")

        return "\n".join(report)
