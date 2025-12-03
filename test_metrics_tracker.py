"""Quick test for metrics_tracker"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.meta.metrics_tracker import MetricsTracker

tracker = MetricsTracker("/tmp/test_metrics.json")
tracker.clear_metrics()

# Test recording
tracker.record_generation("test.module", True, 9.8, 1, [])
tracker.record_test_execution("test.module", 5, 0, 5, 1.5)
tracker.record_refinement("test.module", 8.5, 9.8, ["duplicate imports"])

# Test summary
summary = tracker.get_summary()
assert summary["total_generations"] == 1
assert summary["successful_generations"] == 1
assert summary["total_tests"] == 1
assert summary["total_refinements"] == 1

print("✅ All metrics tracker tests passed!")
sys.exit(0)
