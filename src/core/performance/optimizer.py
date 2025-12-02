"""
Performance Optimizer
Analyzes module performance and suggests optimizations
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from statistics import mean, median


class PerformanceOptimizer:
    """
    Analyzer for module performance with auto-suggestions
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.metrics_dir = self.project_root / "metrics"
        self.quality_file = self.metrics_dir / "module_quality.json"

        # Performance thresholds (ms)
        self.SLOW_THRESHOLD = 500
        self.VERY_SLOW_THRESHOLD = 2000
        self.OPTIMAL_THRESHOLD = 100

    def analyze_module_performance(self, module_id: str) -> Dict[str, Any]:
        """
        Analyze performance of a specific module

        Args:
            module_id: Module identifier

        Returns:
            Analysis with suggestions
        """
        if not self.quality_file.exists():
            return {"error": "No quality metrics found"}

        with open(self.quality_file) as f:
            data = json.load(f)

        module_data = data.get("modules", {}).get(module_id, {})
        if not module_data:
            return {"error": f"Module {module_id} not found"}

        avg_time = module_data.get("average_execution_ms", 0)

        analysis = {
            "module_id": module_id,
            "average_execution_ms": avg_time,
            "performance_rating": self._rate_performance(avg_time),
            "suggestions": self._generate_suggestions(module_id, module_data)
        }

        return analysis

    def find_slow_modules(self, threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Find all slow modules

        Args:
            threshold: Custom threshold in ms (default: SLOW_THRESHOLD)

        Returns:
            List of slow modules with suggestions
        """
        threshold = threshold or self.SLOW_THRESHOLD

        if not self.quality_file.exists():
            return []

        with open(self.quality_file) as f:
            data = json.load(f)

        slow_modules = []
        for module_id, module_data in data.get("modules", {}).items():
            avg_time = module_data.get("average_execution_ms", 0)
            if avg_time > threshold:
                slow_modules.append({
                    "module_id": module_id,
                    "average_execution_ms": avg_time,
                    "performance_rating": self._rate_performance(avg_time),
                    "suggestions": self._generate_suggestions(module_id, module_data)
                })

        # Sort by execution time (slowest first)
        slow_modules.sort(key=lambda x: x["average_execution_ms"], reverse=True)

        return slow_modules

    def generate_optimization_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive optimization report

        Returns:
            Full performance analysis with recommendations
        """
        if not self.quality_file.exists():
            return {"error": "No quality metrics found"}

        with open(self.quality_file) as f:
            data = json.load(f)

        modules = data.get("modules", {})

        # Calculate statistics
        execution_times = [m.get("average_execution_ms", 0) for m in modules.values() if m.get("average_execution_ms")]

        if not execution_times:
            return {"error": "No execution time data available"}

        slow_modules = self.find_slow_modules()
        very_slow_modules = [m for m in slow_modules if m["average_execution_ms"] > self.VERY_SLOW_THRESHOLD]
        optimal_modules = [m_id for m_id, m in modules.items() if m.get("average_execution_ms", 0) < self.OPTIMAL_THRESHOLD]

        report = {
            "summary": {
                "total_modules": len(modules),
                "modules_with_metrics": len(execution_times),
                "average_execution_ms": mean(execution_times),
                "median_execution_ms": median(execution_times),
                "slowest_module_ms": max(execution_times),
                "fastest_module_ms": min(execution_times)
            },
            "performance_categories": {
                "optimal": len(optimal_modules),
                "acceptable": len(execution_times) - len(slow_modules) - len(optimal_modules),
                "slow": len(slow_modules) - len(very_slow_modules),
                "very_slow": len(very_slow_modules)
            },
            "top_10_slow_modules": slow_modules[:10],
            "recommendations": self._generate_global_recommendations(slow_modules)
        }

        return report

    def _rate_performance(self, avg_time: float) -> str:
        """Rate module performance"""
        if avg_time < self.OPTIMAL_THRESHOLD:
            return "optimal"
        elif avg_time < self.SLOW_THRESHOLD:
            return "acceptable"
        elif avg_time < self.VERY_SLOW_THRESHOLD:
            return "slow"
        else:
            return "very_slow"

    def _generate_suggestions(self, module_id: str, module_data: Dict) -> List[str]:
        """Generate optimization suggestions for a module"""
        suggestions = []
        avg_time = module_data.get("average_execution_ms", 0)
        category = module_data.get("category", "")

        if avg_time > self.VERY_SLOW_THRESHOLD:
            suggestions.append("CRITICAL: Module execution time exceeds 2 seconds")
            suggestions.append("Consider adding caching mechanism")
            suggestions.append("Profile code to identify bottlenecks")

        if avg_time > self.SLOW_THRESHOLD:
            suggestions.append("Module is slower than optimal")

            # Category-specific suggestions
            if "browser" in module_id:
                suggestions.append("Consider using faster selectors")
                suggestions.append("Reduce wait times if possible")
                suggestions.append("Use headless mode for better performance")
            elif "api" in module_id or "http" in module_id:
                suggestions.append("Add connection pooling")
                suggestions.append("Implement response caching")
                suggestions.append("Consider parallel requests")
            elif "db" in module_id or "database" in module_id:
                suggestions.append("Add database query caching")
                suggestions.append("Optimize database indexes")
                suggestions.append("Use connection pooling")
            elif "file" in module_id:
                suggestions.append("Consider buffered I/O")
                suggestions.append("Add file caching for frequently accessed files")
            else:
                suggestions.append("Review algorithm complexity")
                suggestions.append("Consider adding memoization")

        # Check failure rate
        fail_rate = module_data.get("fail_runs", 0) / max(module_data.get("total_runs", 1), 1)
        if fail_rate > 0.1:
            suggestions.append(f"High failure rate ({fail_rate:.1%}) - improve error handling")

        return suggestions

    def _generate_global_recommendations(self, slow_modules: List[Dict]) -> List[str]:
        """Generate system-wide optimization recommendations"""
        recommendations = []

        if len(slow_modules) > 10:
            recommendations.append("Multiple slow modules detected - consider system-wide optimization")

        # Analyze module categories
        categories = {}
        for module in slow_modules:
            cat = module["module_id"].split(".")[0]
            categories[cat] = categories.get(cat, 0) + 1

        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            if count > 3:
                recommendations.append(f"{cat} modules are frequently slow - review {cat} implementation")

        if slow_modules:
            recommendations.append("Enable performance profiling for detailed analysis")
            recommendations.append("Consider implementing module-level caching")
            recommendations.append("Review and optimize slowest modules first")

        return recommendations


# Global optimizer instance
_global_optimizer = None

def get_optimizer() -> PerformanceOptimizer:
    """Get or create global optimizer instance"""
    global _global_optimizer
    if _global_optimizer is None:
        _global_optimizer = PerformanceOptimizer()
    return _global_optimizer
