# Module Quality System

## Overview

The Module Quality System ensures Flyto2 maintains high quality standards while allowing AI-driven continuous improvement. It prevents quality degradation through automated testing, classification, and strict quality gates.

## Core Principles

### 1. Test-Driven Quality

Quality is measured objectively through automated tests, not subjective evaluation.

### 2. 98% Success Rate Gate

For atomic modules to be auto-merged, they must maintain ≥98% success rate over the last 50 runs.

### 3. Category-Based Permissions

- Atomic: AI can auto-modify
- Third-party: AI proposes, human reviews
- Composed: Human-controlled only

### 4. No Regression Policy

New versions must perform equal or better than baseline. Any regression is rejected.

### 5. Continuous Monitoring

All modules tracked continuously. Telegram alerts for critical issues.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Module Quality System                     │
└─────────────────────────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼───────┐  ┌────────▼────────┐
│ Classification │  │  Test System   │  │  Quality Gate   │
│                │  │                │  │                 │
│ - Atomic       │  │ - Test         │  │ - 98% check     │
│ - Third-party  │  │   workflows    │  │ - Regression    │
│ - Composed     │  │ - Assertions   │  │   check         │
│                │  │ - Coverage     │  │ - Auto/manual   │
└────────┬───────┘  └────────┬───────┘  └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                    ┌────────▼─────────┐
                    │  Metrics Store   │
                    │                  │
                    │ module_quality   │
                    │     .json        │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │   Telegram       │
                    │  Notifications   │
                    └──────────────────┘
```

## Components

### 1. Module Classification

**File:** `docs/MODULE_CATEGORIES.md`

Defines three categories with specific rules:

**Atomic Modules**
- Pure functions, no external dependencies
- Standard library only
- No network calls, no database access
- Fast execution (< 100ms typical)
- Examples: string.split, array.map, math.sum

**Third-Party Modules**
- External API integrations
- Cloud services, databases, browser
- Network-dependent
- Examples: ai.openai.chat, notification.telegram, browser.launch

**Composed Modules**
- Orchestrate multiple modules
- Business logic workflows
- Examples: agent.autonomous, agent.chain_of_thought

**Classification Rules:**
- Import restrictions (atomic cannot import external libs)
- Naming conventions (category must match prefix)
- Dependency graph validation (atomic cannot call third-party)

### 2. Test System

**Test Modules:** `src/core/modules/atomic/test_utilities.py`

Seven assertion modules:
- `test.assert_equal` - Value equality
- `test.assert_true` - Boolean condition
- `test.assert_contains` - Collection membership
- `test.assert_greater_than` - Numeric comparison
- `test.assert_length` - Collection size
- `test.assert_not_null` - Null check

**Test Workflows:** `tests/modules/*.yaml`

Each module has a test workflow:
```yaml
name: "Test string.split Module"

steps:
  - id: test_basic_split
    module: string.split
    params:
      text: "a,b,c"
      separator: ","

  - id: assert_length
    module: test.assert_length
    params:
      collection: "${test_basic_split.parts}"
      expected_length: 3
```

Tests validate:
- Basic functionality
- Edge cases
- Error handling
- Input validation

### 3. Quality Metrics

**File:** `metrics/module_quality.json`

Tracks for each module:
```json
{
  "string.split": {
    "category": "atomic",
    "total_runs": 120,
    "success_runs": 119,
    "fail_runs": 1,
    "recent_pass_rate": 0.991,
    "last_50_runs": {
      "success": 49,
      "fail": 1,
      "pass_rate": 0.98
    },
    "last_result": "pass",
    "last_tested": "2025-12-01T08:00:00Z",
    "average_execution_ms": 2.5,
    "error_types": {
      "ValueError": 1
    },
    "ai_modifications": {
      "total_proposals": 2,
      "accepted": 1,
      "rejected": 1
    },
    "quality_trend": "stable",
    "auto_merge_approved": true
  }
}
```

**Key Metrics:**
- `recent_pass_rate`: Success rate over last 50 runs (critical for gate)
- `auto_merge_approved`: Boolean, true only if ≥98% pass rate
- `quality_trend`: stable, improving, degrading, needs_attention
- `ai_modifications`: Track proposal acceptance rate

**Quality Thresholds:**
```json
{
  "atomic_pass_threshold": 0.98,
  "third_party_pass_threshold": 0.95,
  "composed_pass_threshold": 0.95,
  "auto_merge_minimum": 0.98,
  "alert_threshold": 0.90,
  "critical_threshold": 0.85
}
```

### 4. Quality Gate Pipeline

**Workflow:** `workflows/meta/module_quality_pipeline.yaml`

The core enforcement mechanism. Flow:

```
1. Check module category
   ↓
2. Verify atomic category (fail if not)
   ↓
3. Find test workflow (fail if missing)
   ↓
4. Run baseline tests (get current pass rate)
   ↓
5. Run improved version tests (50 runs)
   ↓
6. Calculate new pass rate
   ↓
7. GATE DECISION
   ├─ new_pass_rate >= 0.98? (YES/NO)
   ├─ new_pass_rate >= baseline? (YES/NO)
   ├─ category == atomic? (YES/NO)
   └─ tests ran successfully? (YES/NO)
   ↓
8. ALL YES → PASS: Create PR, update metrics, notify success
   ↓
9. ANY NO → FAIL: Reject, keep old version, notify failure
```

**Gate Criteria (ALL must pass):**
1. New pass rate ≥ 98%
2. New pass rate ≥ baseline pass rate (no regression)
3. Module category is atomic
4. All tests executed successfully

**Outcomes:**

**PASS:**
- Update module_quality.json
- Create GitHub PR (if auto_pr=true)
- Send Telegram success notification
- Mark module for potential auto-merge

**FAIL:**
- Keep original module
- Log failure reason
- Send Telegram failure notification
- Increment rejected proposals counter

### 5. Validation Workflow

**Workflow:** `workflows/meta/validate_modules.yaml`

Comprehensive module health check:

1. Read classification rules
2. List all modules from registry
3. AI classifies each module
4. Identify naming/import/dependency violations
5. Map modules to test workflows
6. Generate classification report
7. Generate quality summary
8. Send Telegram notification (optional)

**Outputs:**
- `workflows/_reports/module_classification_TIMESTAMP.json`
- `workflows/_reports/quality_report_TIMESTAMP.md`

Run regularly (daily or on-demand) to monitor overall system health.

### 6. Telegram Notifications

**Workflow:** `workflows/meta/quality_telegram_report.yaml`

Two notification types:

**Type 1: Daily Summary**
```
Flyto2 Module Quality Report

OVERALL HEALTH
Total: 105
Above 98%: 63
95-98%: 35
Below 95%: 5
Critical: 2

CRITICAL ISSUES
- ai.openai.chat: 91% (rate limit errors)
- agent.autonomous: 92% (LLM failures)

TRENDS
Improving: 8
Stable: 90
Degrading: 7

RECOMMENDED ACTIONS
1. Investigate ai.openai.chat retry logic
2. Add fallback for agent.autonomous
```

**Type 2: Critical Alerts**
Triggered when:
- Module drops below 90% (alert threshold)
- Module drops below 85% (critical threshold)
- Quality gate failure
- New violations detected

## Workflows

### Complete Workflow List

1. **validate_modules.yaml** - Module classification and health check
2. **module_quality_pipeline.yaml** - 98% quality gate enforcement
3. **quality_telegram_report.yaml** - Telegram notifications
4. **autonomous_improve.yaml** - AI-driven improvement (updated)
5. **full_improvement_pipeline.yaml** - Complete improvement flow

### Typical Usage Patterns

#### Pattern 1: Daily Health Check

```bash
python -m src.cli.main workflows/meta/validate_modules.yaml \
  --param send_telegram=true \
  --param telegram_bot_token=$TG_TOKEN \
  --param telegram_chat_id=$TG_CHAT
```

**When:** Daily at 2am (scheduled)
**Purpose:** Monitor overall system health
**Output:** Classification report + Telegram summary

#### Pattern 2: AI Module Improvement

```bash
# Step 1: AI proposes improvement
python -m src.cli.main workflows/meta/autonomous_improve.yaml \
  --param target_module=string.split \
  --param focus_area=performance

# Step 2: Quality gate validation
python -m src.cli.main workflows/meta/module_quality_pipeline.yaml \
  --param target_module=string.split \
  --param improved_module_path=_generated/modules/string_split_v2.py \
  --param test_runs=50 \
  --param auto_pr=true \
  --param telegram_notify=true
```

**When:** On-demand or triggered by error logs
**Purpose:** Improve specific module with quality verification
**Outcome:** PR created if gate passed, rejected if failed

#### Pattern 3: Full Pipeline

```bash
python -m src.cli.main workflows/meta/full_improvement_pipeline.yaml \
  --param use_quality_gate=true \
  --param telegram_notify=true
```

**When:** Weekly improvement cycle
**Purpose:** Comprehensive improvement with strict gating
**Flow:**
1. Analyze all modules
2. Identify improvement candidates
3. Generate improvements
4. Run quality gate for each
5. Create PRs for passed improvements
6. Send summary report

#### Pattern 4: Quality Report Only

```bash
python -m src.cli.main workflows/meta/quality_telegram_report.yaml \
  --param telegram_bot_token=$TG_TOKEN \
  --param telegram_chat_id=$TG_CHAT \
  --param report_type=summary
```

**When:** On-demand or after deployments
**Purpose:** Get current quality snapshot
**Output:** Telegram message with key metrics

## Quality Gate in Detail

### Decision Logic

```python
def evaluate_quality_gate(module_data):
    # Criterion 1: 98% threshold
    meets_threshold = new_pass_rate >= 0.98

    # Criterion 2: No regression
    no_regression = new_pass_rate >= baseline_pass_rate

    # Criterion 3: Atomic category
    category_allowed = category == "atomic"

    # Criterion 4: Tests successful
    tests_passed = total_runs > 0 and failures == 0

    # ALL must be true
    gate_passed = (
        meets_threshold and
        no_regression and
        category_allowed and
        tests_passed
    )

    return gate_passed
```

### Example Scenarios

**Scenario 1: Clear Pass**
```
Module: string.split
Category: atomic ✓
Baseline: 98.5%
New: 99.0% ✓
Runs: 50, Passed: 49, Failed: 1 ✓
Gate: PASS
Action: Create PR, update metrics
```

**Scenario 2: Below Threshold**
```
Module: array.filter
Category: atomic ✓
Baseline: 97.0%
New: 97.5% ✗ (< 98%)
Runs: 50, Passed: 48, Failed: 2
Gate: FAIL
Reason: New pass rate 97.5% below 98% threshold
Action: Reject, notify failure
```

**Scenario 3: Regression**
```
Module: math.sum
Category: atomic ✓
Baseline: 99.5%
New: 98.5% ✗ (regression)
Runs: 50, Passed: 49, Failed: 1
Gate: FAIL
Reason: Regression from 99.5% to 98.5%
Action: Reject, even though above 98%
```

**Scenario 4: Wrong Category**
```
Module: ai.openai.chat
Category: third_party ✗
Baseline: 95.0%
New: 96.0%
Gate: FAIL
Reason: Third-party modules require manual review
Action: Create PR but no auto-merge
```

### Gate Bypass

Only for emergencies, requires manual override:

```bash
# Emergency fix without gate
python -m src.cli.main workflows/meta/module_quality_pipeline.yaml \
  --param target_module=critical.module \
  --param bypass_gate=true \
  --param require_manual_approval=true
```

Use sparingly. All bypasses logged and reviewed.

## Best Practices

### 1. Write Tests First

Before creating a module, create its test workflow:

```yaml
# tests/modules/new_module_test.yaml
name: "Test new.module"

steps:
  - id: test_basic
    module: new.module
    params:
      input: "test"

  - id: assert_output
    module: test.assert_not_null
    params:
      value: "${test_basic.result}"
```

### 2. Keep Atomic Modules Pure

Atomic modules should be:
- Deterministic (same input → same output)
- Fast (< 100ms)
- No side effects (except local file ops)
- No external dependencies

### 3. Test Edge Cases

Don't just test happy path:

```yaml
steps:
  # Happy path
  - id: test_normal
    module: string.split
    params:
      text: "a,b,c"
      separator: ","

  # Edge cases
  - id: test_empty
    module: string.split
    params:
      text: ""
      separator: ","

  - id: test_no_separator
    module: string.split
    params:
      text: "noseparator"
      separator: ","

  - id: test_multiple_separators
    module: string.split
    params:
      text: "a,,b,,c"
      separator: ","
```

### 4. Monitor Trends

Don't just look at current pass rate, watch trends:

```json
{
  "quality_trend": "degrading",
  "recent_changes": [
    {"date": "2025-11-28", "pass_rate": 99.0},
    {"date": "2025-11-30", "pass_rate": 98.5},
    {"date": "2025-12-01", "pass_rate": 98.0}
  ]
}
```

Degrading trend → investigate before it drops below 98%.

### 5. Review Rejected Proposals

When AI proposal is rejected:
1. Read the gate report
2. Understand why it failed
3. Check if test is too strict
4. Check if improvement approach was wrong
5. Learn and improve prompts

### 6. Incremental Improvements

Don't try to fix everything at once:
- Improve one module at a time
- Validate before moving to next
- Build confidence in the system

## Maintenance

### Daily Tasks

1. **Check Telegram summary** (2 minutes)
   - Any critical alerts?
   - Any modules degrading?

2. **Review gate failures** (5 minutes)
   - Read failure reports
   - Identify patterns
   - Update improvement strategies

### Weekly Tasks

1. **Run full validation** (10 minutes)
   ```bash
   python -m src.cli.main workflows/meta/validate_modules.yaml
   ```

2. **Review quality trends** (15 minutes)
   - Which modules improving?
   - Which modules degrading?
   - Any category violations?

3. **Update test coverage** (20 minutes)
   - Add tests for new modules
   - Improve tests for flaky modules

### Monthly Tasks

1. **Audit metrics file** (30 minutes)
   - Verify data consistency
   - Archive old metrics
   - Clean up stale data

2. **Review thresholds** (20 minutes)
   - Is 98% still appropriate?
   - Should third-party threshold change?
   - Any special cases?

3. **System health report** (30 minutes)
   - Overall quality trend
   - AI proposal acceptance rate
   - Test coverage status
   - Improvement opportunities

## Troubleshooting

### Issue: Module failing tests randomly

**Symptoms:** Pass rate fluctuates, sometimes passes, sometimes fails

**Diagnosis:**
1. Check if module has external dependencies (network, time, random)
2. Review error types in metrics
3. Look for flaky test assertions

**Solution:**
- Make tests deterministic
- Mock external dependencies
- Use fixed test data
- Increase test runs to identify flakiness

### Issue: Quality gate always rejects improvements

**Symptoms:** AI proposals always fail gate, even when code looks good

**Diagnosis:**
1. Check if baseline pass rate is already 100%
2. Review test strictness
3. Check if test data is too narrow

**Solution:**
- Expand test cases
- Allow for minor variations
- Review if baseline is artificially high
- Consider lowering threshold for specific modules

### Issue: Telegram not receiving notifications

**Symptoms:** Workflows complete but no Telegram message

**Diagnosis:**
1. Check bot token validity
2. Verify chat ID
3. Check if bot is in chat
4. Review Telegram API errors

**Solution:**
```bash
# Test Telegram directly
python -m src.cli.main workflows/meta/quality_telegram_report.yaml \
  --param telegram_bot_token=$TG_TOKEN \
  --param telegram_chat_id=$TG_CHAT \
  --param report_type=summary
```

### Issue: Metrics file corrupted

**Symptoms:** JSON parse errors, missing data

**Diagnosis:**
1. Validate JSON structure
2. Check file permissions
3. Review recent updates

**Solution:**
```bash
# Validate JSON
cat metrics/module_quality.json | python -m json.tool

# Restore from backup
cp metrics/module_quality_backup.json metrics/module_quality.json

# Regenerate from scratch
python -m src.cli.main workflows/meta/validate_modules.yaml \
  --param update_metrics=true
```

## Integration with CI/CD

### GitHub Actions

```yaml
name: Module Quality Check

on:
  pull_request:
    paths:
      - 'src/core/modules/**'

jobs:
  quality-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Run Quality Gate
        run: |
          python -m src.cli.main workflows/meta/module_quality_pipeline.yaml \
            --param target_module=${{ github.event.pull_request.title }} \
            --param improved_module_path=${{ github.event.pull_request.head.ref }} \
            --param test_runs=50

      - name: Check Gate Status
        run: |
          if [ $? -ne 0 ]; then
            echo "Quality gate failed"
            exit 1
          fi
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check if any module files changed
if git diff --cached --name-only | grep -q 'src/core/modules/'; then
    echo "Module files changed, running quality validation..."
    python -m src.cli.main workflows/meta/validate_modules.yaml

    if [ $? -ne 0 ]; then
        echo "Quality validation failed. Commit rejected."
        exit 1
    fi
fi
```

## Future Enhancements

### Planned Features

1. **Auto-test Generation**
   - AI generates test cases from module specs
   - Comprehensive coverage automatically

2. **Performance Benchmarking**
   - Track execution time trends
   - Performance regression detection

3. **Cross-module Testing**
   - Test module interactions
   - Integration test suites

4. **A/B Testing**
   - Run old and new versions in parallel
   - Compare real-world performance

5. **Quality Predictions**
   - ML model predicts which modules likely to degrade
   - Proactive intervention

## Summary

The Module Quality System provides:

- Objective quality measurement through automated tests
- 98% success rate gate for atomic modules
- Category-based permissions (atomic auto, others manual)
- No regression policy
- Continuous monitoring via Telegram
- Complete audit trail

This ensures AI improvements enhance the codebase without introducing bugs, maintaining Flyto2's reliability while enabling continuous evolution.

Key files:
- `docs/MODULE_CATEGORIES.md` - Classification rules
- `metrics/module_quality.json` - Quality metrics
- `workflows/meta/validate_modules.yaml` - Health check
- `workflows/meta/module_quality_pipeline.yaml` - Quality gate
- `workflows/meta/quality_telegram_report.yaml` - Notifications
- `tests/modules/*.yaml` - Test workflows
- `src/core/modules/atomic/test_utilities.py` - Assertion modules

The system is self-maintaining: add a module, add its test, everything else is automatic.
