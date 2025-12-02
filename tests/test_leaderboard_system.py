#!/usr/bin/env python3
"""
Test Leaderboard System
Tests all leaderboard features: accuracy, stability, evolution, and historical comparison
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_accuracy_leaderboard():
    """Test 1: Accuracy Leaderboard"""
    print("\n=== Test 1: Accuracy Leaderboard ===")

    from src.core.leaderboard import MetricsTracker

    tracker = MetricsTracker()

    # Record accuracy for multiple modules
    test_data = [
        ("browser.click", 95.0, 98.0, 2.0),
        ("browser.extract", 90.0, 92.0, 5.0),
        ("string.parse", 98.0, 99.0, 1.0),
        ("data.transform", 88.0, 90.0, 8.0),
    ]

    for module_id, completeness, correctness, error_rate in test_data:
        tracker.record_accuracy(module_id, completeness, correctness, error_rate)

    # Get leaderboard
    leaderboard = tracker.get_accuracy_leaderboard(5)

    print(f"\nTop {len(leaderboard)} Accuracy Leaders:")
    for i, metric in enumerate(leaderboard, 1):
        print(f"{i}. {metric.module_id}")
        print(f"   Overall Accuracy: {metric.overall_accuracy:.1f}%")
        print(f"   Completeness: {metric.data_completeness:.1f}%")
        print(f"   Correctness: {metric.format_correctness:.1f}%")
        print(f"   Error Rate: {metric.error_rate:.1f}%")

    # Verify
    assert len(leaderboard) >= 4  # At least our 4 test modules
    assert leaderboard[0].overall_accuracy > 0  # Has data

    print("✅ Test 1 PASSED")
    return True


def test_stability_leaderboard():
    """Test 2: Stability Leaderboard"""
    print("\n=== Test 2: Stability Leaderboard ===")

    from src.core.leaderboard import MetricsTracker

    tracker = MetricsTracker()

    # Simulate stability events
    modules = ["browser.click", "api.fetch", "string.parse"]

    for module_id in modules:
        # Record successful runs
        for _ in range(10):
            tracker.record_stability(module_id, success=True, runtime_hours=0.1)

        # Record some failures and recoveries
        tracker.record_stability(module_id, success=False)
        tracker.record_stability(module_id, success=True, recovered_from_error=True)

    # Get leaderboard
    leaderboard = tracker.get_stability_leaderboard(5)

    print(f"\nTop {len(leaderboard)} Stability Leaders:")
    for i, metric in enumerate(leaderboard, 1):
        print(f"{i}. {metric.module_id}")
        print(f"   Stability Score: {metric.stability_score:.1f}")
        print(f"   Max Streak: {metric.max_consecutive_successes}")
        print(f"   Recovery Rate: {metric.error_recovery_rate:.1f}%")
        print(f"   Uptime: {metric.uptime_hours:.1f}h")

    # Verify
    assert len(leaderboard) >= 3  # At least our 3 test modules
    assert all(m.stability_score > 0 for m in leaderboard)

    print("✅ Test 2 PASSED")
    return True


def test_evolution_leaderboard():
    """Test 3: Evolution Index Leaderboard"""
    print("\n=== Test 3: Evolution Index Leaderboard ===")

    from src.core.leaderboard import MetricsTracker

    tracker = MetricsTracker()

    # Record evolution metrics
    tracker.record_evolution(
        "system_v1",
        modules_added=5,
        test_coverage_growth=10.5,
        bugs_fixed=8,
        fix_time_hours=2.5
    )

    tracker.record_evolution(
        "system_v2",
        modules_added=3,
        test_coverage_growth=5.0,
        bugs_fixed=12,
        fix_time_hours=1.8
    )

    # Get leaderboard
    leaderboard = tracker.get_evolution_leaderboard(5)

    print(f"\nTop {len(leaderboard)} Evolution Leaders:")
    for i, metric in enumerate(leaderboard, 1):
        print(f"{i}. {metric.module_id}")
        print(f"   Evolution Index: {metric.evolution_index:.1f}")
        print(f"   Modules Added: +{metric.modules_added}")
        print(f"   Coverage Growth: +{metric.test_coverage_growth:.1f}%")
        print(f"   Bugs Fixed: {metric.bugs_fixed}")
        print(f"   Avg Fix Time: {metric.avg_fix_time_hours:.1f}h")

    # Verify
    assert len(leaderboard) >= 2  # At least our 2 test systems
    assert all(m.evolution_index > 0 for m in leaderboard)

    print("✅ Test 3 PASSED")
    return True


def test_historical_comparison():
    """Test 4: Historical Comparison"""
    print("\n=== Test 4: Historical Comparison ===")

    from src.core.leaderboard import MetricsTracker, HistoricalComparison

    tracker = MetricsTracker()
    history = HistoricalComparison()

    # Create baseline snapshot
    for module_id in ["module_a", "module_b"]:
        tracker.record_accuracy(module_id, 85.0, 88.0, 10.0)
        tracker.record_stability(module_id, success=True, runtime_hours=0.5)

    snapshot1 = history.capture_snapshot("week_1")
    print(f"\nCaptured snapshot: {snapshot1}")

    # Simulate improvements
    for module_id in ["module_a", "module_b"]:
        tracker.record_accuracy(module_id, 95.0, 97.0, 3.0)
        tracker.record_stability(module_id, success=True, runtime_hours=1.0)

    snapshot2 = history.capture_snapshot("week_2")
    print(f"Captured snapshot: {snapshot2}")

    # Compare periods
    comparisons = history.compare_periods(snapshot1, snapshot2)

    print(f"\nComparisons found: {len(comparisons)}")
    for comp in comparisons:
        change_icon = "📈" if comp.trend == "up" else "📉" if comp.trend == "down" else "➡️"
        print(f"{change_icon} {comp.metric_name}")
        print(f"   Previous: {comp.previous_value:.2f}")
        print(f"   Current: {comp.current_value:.2f}")
        print(f"   Change: {comp.change:+.2f} ({comp.change_percent:+.1f}%)")

    # Generate report
    report = history.generate_comparison_report(snapshot1, snapshot2)
    print(f"\n{report}")

    # Verify
    assert len(comparisons) > 0
    assert any(c.is_improvement for c in comparisons)

    print("✅ Test 4 PASSED")
    return True


def test_comprehensive_report():
    """Test 5: Comprehensive Leaderboard Report"""
    print("\n=== Test 5: Comprehensive Report ===")

    from src.core.leaderboard import MetricsTracker

    tracker = MetricsTracker()

    # Add some sample data
    tracker.record_accuracy("test_module", 92.0, 95.0, 5.0)
    tracker.record_stability("test_module", success=True, runtime_hours=2.0)
    tracker.record_evolution("test_system", modules_added=2, bugs_fixed=5, fix_time_hours=3.0)

    # Generate comprehensive report
    report = tracker.generate_report()

    print(f"\n{report}")

    # Verify
    assert "COMPREHENSIVE LEADERBOARD REPORT" in report
    assert "ACCURACY" in report
    assert "STABILITY" in report
    assert "EVOLUTION" in report

    print("✅ Test 5 PASSED")
    return True


def main():
    """Run all tests"""
    print("=" * 70)
    print("Leaderboard System Tests")
    print("=" * 70)

    tests = [
        test_accuracy_leaderboard,
        test_stability_leaderboard,
        test_evolution_leaderboard,
        test_historical_comparison,
        test_comprehensive_report
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    print("\n" + "=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("✅ ALL TESTS PASSED")
        return 0
    else:
        print(f"❌ {total - passed} tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
