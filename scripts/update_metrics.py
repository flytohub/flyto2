#!/usr/bin/env python3
"""
Update module_quality.json from test results
"""
import json
import sys
from datetime import datetime
from pathlib import Path

def update_metrics(results_file, metrics_file):
    """Update metrics from test results"""

    # Read test results
    results = {}
    with open(results_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(',')
            if len(parts) == 4:
                module_id, success, fail, rate = parts
                results[module_id] = {
                    'success': int(success),
                    'fail': int(fail),
                    'rate': float(rate)
                }

    # Read existing metrics
    with open(metrics_file) as f:
        metrics = json.load(f)

    # Update timestamp
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    metrics['_last_updated'] = now

    # Update each module
    for module_id, result in results.items():
        if module_id not in metrics['modules']:
            # New module
            metrics['modules'][module_id] = {
                'category': 'atomic',
                'total_runs': 0,
                'success_runs': 0,
                'fail_runs': 0,
                'recent_pass_rate': 0.0,
                'last_50_runs': {
                    'success': 0,
                    'fail': 0,
                    'pass_rate': 0.0
                },
                'last_result': 'unknown',
                'last_tested': now,
                'average_execution_ms': 150,
                'error_types': {},
                'ai_modifications': {
                    'total_proposals': 0,
                    'accepted': 0,
                    'rejected': 0,
                    'last_proposal': None
                },
                'quality_trend': 'stable',
                'auto_merge_approved': False
            }

        module = metrics['modules'][module_id]

        # Update runs
        module['total_runs'] += result['success'] + result['fail']
        module['success_runs'] += result['success']
        module['fail_runs'] += result['fail']
        module['recent_pass_rate'] = result['rate']
        module['last_result'] = 'pass' if result['success'] > 0 else 'fail'
        module['last_tested'] = now

        # Update last 50 runs (simplified - just use recent rate)
        module['last_50_runs'] = {
            'success': result['success'],
            'fail': result['fail'],
            'pass_rate': result['rate']
        }

        # Update auto-merge approval
        module['auto_merge_approved'] = result['rate'] >= 0.98

        # Update quality trend
        if result['rate'] >= 0.98:
            module['quality_trend'] = 'stable'
        elif result['rate'] >= 0.95:
            module['quality_trend'] = 'needs_attention'
        else:
            module['quality_trend'] = 'degrading'

    # Update summary
    modules = metrics['modules']
    metrics['summary'] = {
        'total_modules': len(modules),
        'atomic_modules': sum(1 for m in modules.values() if m['category'] == 'atomic'),
        'third_party_modules': sum(1 for m in modules.values() if m['category'] == 'third_party'),
        'composed_modules': sum(1 for m in modules.values() if m['category'] == 'composed'),
        'modules_above_98': sum(1 for m in modules.values() if m['recent_pass_rate'] >= 0.98),
        'modules_95_to_98': sum(1 for m in modules.values() if 0.95 <= m['recent_pass_rate'] < 0.98),
        'modules_below_95': sum(1 for m in modules.values() if m['recent_pass_rate'] < 0.95),
        'auto_merge_approved_count': sum(1 for m in modules.values() if m.get('auto_merge_approved', False)),
        'last_validation_run': now
    }

    # Write updated metrics
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"Updated {len(results)} modules")
    print(f"Total modules: {metrics['summary']['total_modules']}")
    print(f"Above 98%: {metrics['summary']['modules_above_98']}")
    print(f"95-98%: {metrics['summary']['modules_95_to_98']}")
    print(f"Below 95%: {metrics['summary']['modules_below_95']}")
    print(f"Auto-merge approved: {metrics['summary']['auto_merge_approved_count']}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/update_metrics.py <results_file>")
        sys.exit(1)

    results_file = sys.argv[1]
    metrics_file = "metrics/module_quality.json"

    update_metrics(results_file, metrics_file)
