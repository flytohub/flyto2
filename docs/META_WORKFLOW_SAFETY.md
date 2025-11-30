# Meta-Workflow Safety Guide

## Core Safety Principles

### 1. Never Modify Production Directly

Meta-workflows must NEVER write to production workflow paths.

**Protected Paths:**
```
workflows/*.yaml           - PROTECTED
workflows/meta/*.yaml      - PROTECTED
```

**Allowed Paths:**
```
workflows/_generated/      - AI-generated workflows
workflows/_refactored/     - Refactored versions
workflows/_improved/       - Autonomous improvements
workflows/_analysis/       - Analysis reports
workflows/_validation/     - Validation results
workflows/_reports/        - Pipeline reports
workflows/_learning/       - Learning reports
```

### 2. Require Human Review

All AI-generated changes require human approval before production use.

**Approval Process:**
1. AI generates workflow
2. Validation runs automatically
3. Report created with details
4. Human reviews changes
5. Manual approval required
6. Only then merge to production

### 3. Validation Before Execution

Never execute AI-generated workflows without validation.

**Validation Steps:**
```yaml
steps:
  # Generate
  - id: generate
    module: ai.openai.chat

  # Validate syntax
  - id: validate_yaml
    module: data.yaml.validate

  # Validate modules exist
  - id: validate_modules
    module: meta.validate_modules

  # Only save if valid
  - id: save
    if: "${validate_modules.valid == true}"
    module: data.file.write
```

### 4. Audit Trail Required

Every meta-workflow execution must create audit trail.

**Audit Requirements:**
- Timestamp in all filenames
- Full input/output logged
- Model and provider recorded
- Reasoning steps saved
- Original preserved

## Security Checklist

Before running meta-workflows in production:

### Environment Security

- [ ] API keys stored in environment variables only
- [ ] No secrets in workflow YAML files
- [ ] GitHub token has minimal required permissions
- [ ] Slack webhooks are for non-sensitive channels
- [ ] File permissions restrict workflow directory access

### Workflow Safety

- [ ] Meta-workflows write to isolated directories only
- [ ] No direct modification of production workflows
- [ ] All changes require PR and review
- [ ] Validation runs before any file write
- [ ] Rollback plan exists for failed improvements

### AI Safety

- [ ] AI prompts do not expose sensitive data
- [ ] Generated code reviewed before execution
- [ ] LLM provider rate limits configured
- [ ] Cost monitoring enabled for cloud LLMs
- [ ] Local LLM used for sensitive operations

## Common Risks and Mitigations

### Risk: AI Generates Malicious Code

**Scenario:** AI generates workflow that deletes files or exposes secrets

**Mitigation:**
```yaml
steps:
  - id: security_scan
    module: ai.openai.chat
    params:
      system_message: "You are a security auditor. Identify security issues."
      prompt: |
        Review this generated workflow for security issues:
        ${generated_workflow}

        Flag any:
        - File deletions
        - Secret exposure
        - Unrestricted network access
        - Command injection risks
```

### Risk: Infinite Loop of Improvements

**Scenario:** Meta-workflow continuously modifies same workflow

**Mitigation:**
- Set max iterations limit
- Require quality score improvement threshold
- Track modification history
- Human approval gate

```yaml
parameters:
  max_improvement_iterations:
    type: number
    default: 3
    description: "Stop after N improvement attempts"

  min_quality_improvement:
    type: number
    default: 10
    description: "Require at least 10 point quality improvement"
```

### Risk: Resource Exhaustion

**Scenario:** Meta-workflow uses all API quota or compute

**Mitigation:**
```yaml
steps:
  - id: check_quota
    module: meta.check_api_quota

  - id: improve
    if: "${check_quota.remaining > 1000}"
    module: agent.autonomous
    timeout: 300  # 5 minute timeout
```

### Risk: Data Leakage

**Scenario:** Sensitive data included in AI prompts or logs

**Mitigation:**
```yaml
steps:
  - id: sanitize_logs
    module: data.string.replace
    params:
      text: "${workflow_content}"
      patterns:
        - pattern: "api_key:.*"
          replacement: "api_key: REDACTED"
        - pattern: "password:.*"
          replacement: "password: REDACTED"

  - id: analyze_safe
    module: ai.openai.chat
    params:
      prompt: "${sanitize_logs.result}"
```

## Validation Requirements

### YAML Structure Validation

```yaml
steps:
  - id: validate_structure
    module: ai.openai.chat
    params:
      model: "gpt-3.5-turbo"
      temperature: 0
      prompt: |
        Validate this YAML structure:
        ${generated_yaml}

        Check:
        1. Valid YAML syntax
        2. Required fields present (name, steps)
        3. Step IDs are unique
        4. Module IDs follow pattern
        5. Parameter types match schema

        Output JSON:
        {
          "valid": true/false,
          "errors": [],
          "warnings": []
        }
```

### Module Existence Validation

```yaml
steps:
  - id: read_registry
    module: data.file.read
    params:
      file_path: "docs/MODULES.md"

  - id: validate_modules
    module: ai.openai.chat
    params:
      prompt: |
        Module Registry:
        ${read_registry.content}

        Generated Workflow:
        ${generated_yaml}

        Verify all module IDs in workflow exist in registry.
        Output: { "valid": boolean, "unknown_modules": [] }
```

### Parameter Validation

```yaml
steps:
  - id: validate_params
    module: ai.openai.chat
    params:
      prompt: |
        For each step, verify:
        1. Required parameters present
        2. Parameter types correct
        3. Values within valid ranges
        4. References to previous steps valid

        Output validation report.
```

## Sandbox Testing

Always test generated workflows in sandbox before production.

### Sandbox Environment Setup

```yaml
parameters:
  environment:
    type: string
    default: "production"
    description: "Environment: sandbox or production"

steps:
  - id: use_test_credentials
    if: "${params.environment == 'sandbox'}"
    module: core.env.set
    params:
      OPENAI_API_KEY: "${env.OPENAI_TEST_KEY}"
      SLACK_WEBHOOK_URL: "${env.SLACK_TEST_WEBHOOK}"

  - id: dry_run
    module: meta.execute_workflow
    params:
      workflow: "${generated_workflow}"
      dry_run: true
```

### Test Data Isolation

```yaml
steps:
  - id: use_test_data
    if: "${params.environment == 'sandbox'}"
    module: data.file.read
    params:
      file_path: "test_data/sample.json"

  - id: use_production_data
    if: "${params.environment == 'production'}"
    module: data.file.read
    params:
      file_path: "${params.data_source}"
```

## Rate Limiting

### API Rate Limits

```yaml
steps:
  - id: check_rate_limit
    module: core.utility.delay
    params:
      duration: 1  # 1 second between AI calls

  - id: call_ai
    module: ai.openai.chat
    timeout: 30
    max_retries: 3
```

### Cost Controls

```yaml
parameters:
  max_cost_per_run:
    type: number
    default: 1.0
    description: "Max USD per meta-workflow run"

steps:
  - id: estimate_cost
    module: meta.estimate_cost
    params:
      workflow: "${target_workflow}"
      model: "${params.model}"

  - id: proceed_if_affordable
    if: "${estimate_cost.total_usd < params.max_cost_per_run}"
    module: agent.autonomous
```

## Emergency Procedures

### Stop Runaway Workflows

If meta-workflow is causing issues:

```bash
# Find running processes
ps aux | grep "src.cli.main"

# Kill specific workflow
kill -9 <PID>

# Or kill all flyto2 processes
pkill -f "src.cli.main"
```

### Rollback Changes

If AI-generated workflow breaks production:

```bash
# Revert file
git checkout HEAD -- workflows/broken_workflow.yaml

# Or rollback to previous commit
git revert <commit_hash>

# Emergency: reset to last good state
git reset --hard <last_good_commit>
```

### Disable Meta-Workflows

Add circuit breaker to meta-workflows:

```yaml
steps:
  - id: check_circuit_breaker
    module: data.file.read
    params:
      file_path: "config/meta_enabled.txt"

  - id: exit_if_disabled
    if: "${check_circuit_breaker.content != 'enabled'}"
    module: core.utility.fail
    params:
      message: "Meta-workflows disabled via circuit breaker"
```

Disable:
```bash
echo "disabled" > config/meta_enabled.txt
```

## Monitoring and Alerts

### Success Rate Monitoring

```yaml
steps:
  - id: track_success
    module: data.file.append
    params:
      file_path: "metrics/meta_workflow_success.log"
      content: |
        ${timestamp},${workflow_name},${success},${quality_score}

  - id: alert_if_low_success
    module: notification.slack.send_message
    if: "${success_rate < 0.7}"
    params:
      text: "WARNING: Meta-workflow success rate below 70%"
```

### Quality Degradation Alerts

```yaml
steps:
  - id: compare_quality
    module: meta.compare_quality
    params:
      original: workflows/example.yaml
      improved: workflows/_improved/example.yaml

  - id: alert_if_worse
    if: "${compare_quality.quality_delta < 0}"
    module: notification.slack.send_message
    params:
      text: "WARNING: Improvement made workflow worse"
```

## Best Practices Summary

1. **Isolation:** Write to separate directories only
2. **Validation:** Always validate before use
3. **Review:** Human approval required
4. **Audit:** Complete audit trail
5. **Testing:** Sandbox test first
6. **Limits:** Set rate and cost limits
7. **Monitoring:** Track success and quality
8. **Rollback:** Always have rollback plan
9. **Security:** Scan for security issues
10. **Documentation:** Document all changes

## Compliance Checklist

Before deploying meta-workflows to production:

- [ ] Security review completed
- [ ] Audit trail mechanism tested
- [ ] Rollback procedure documented
- [ ] Rate limits configured
- [ ] Cost controls enabled
- [ ] Validation gates implemented
- [ ] Human approval process defined
- [ ] Monitoring dashboards created
- [ ] Emergency procedures documented
- [ ] Team trained on safety protocols

## Contact

For security concerns: security@flyto2.example.com

For safety questions: Open issue on GitHub
