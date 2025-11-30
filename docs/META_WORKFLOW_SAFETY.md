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

All AI-generated workflows must pass validation before use. The validation system checks multiple aspects of workflow correctness.

### What Validation Checks

The `validate_workflow.yaml` meta-workflow performs comprehensive checks:

#### 1. YAML Syntax Validation

**Checks:**
- Valid YAML format
- Proper indentation
- No syntax errors
- Correct data types

**Fails when:**
- Invalid YAML syntax
- Malformed structure
- Incorrect indentation
- Type mismatches

**Example Failure:**
```yaml
steps:
  - id: step1
  module: test  # ERROR: Missing indentation
```

#### 2. Required Fields Validation

**Checks:**
- Workflow has `name` field
- Workflow has `steps` array
- Each step has `id` field
- Each step has `module` field
- Each step has `params` object

**Fails when:**
- Missing required top-level fields
- Steps array is empty
- Step missing id or module
- Invalid field types

**Example Failure:**
```yaml
name: "Test Workflow"
# ERROR: Missing steps field
```

#### 3. Step ID Uniqueness

**Checks:**
- All step IDs are unique
- No duplicate IDs in workflow
- IDs follow naming conventions

**Fails when:**
- Duplicate step IDs found
- ID contains invalid characters
- ID is empty or null

**Example Failure:**
```yaml
steps:
  - id: fetch_data
    module: api.http.get
  - id: fetch_data  # ERROR: Duplicate ID
    module: data.csv.write
```

#### 4. Module Existence Validation

**Checks:**
- All module IDs exist in registry
- Module IDs follow naming pattern
- Module IDs are correctly formatted

**Fails when:**
- Module ID not found in registry
- Typo in module name
- Invalid module ID format
- Using deprecated modules

**Example Failure:**
```yaml
steps:
  - id: send_email
    module: email.send  # ERROR: Should be notification.email.send
```

#### 5. Parameter Schema Validation

**Checks:**
- Required parameters present
- Parameter types correct
- Values within valid ranges
- Enum values are valid options

**Fails when:**
- Missing required parameters
- Wrong parameter types
- Values out of range
- Invalid enum values

**Example Failure:**
```yaml
steps:
  - id: delay
    module: core.utility.delay
    params:
      duration: "5"  # ERROR: Should be number, not string
```

#### 6. Variable Reference Validation

**Checks:**
- References to previous steps valid
- Step exists before reference
- Variable paths are correct
- No circular dependencies

**Fails when:**
- Referencing non-existent step
- Forward references (step not yet defined)
- Invalid variable path syntax
- Circular step dependencies

**Example Failure:**
```yaml
steps:
  - id: step1
    module: data.string.uppercase
    params:
      text: "${step2.output}"  # ERROR: step2 not defined yet
  - id: step2
    module: data.string.lowercase
```

#### 7. Conditional Logic Validation

**Checks:**
- `if` conditions are valid expressions
- Referenced variables exist
- Boolean logic is correct
- No syntax errors in conditions

**Fails when:**
- Invalid condition syntax
- Undefined variables in condition
- Type errors in comparisons
- Malformed boolean expressions

**Example Failure:**
```yaml
steps:
  - id: conditional_step
    module: core.utility.delay
    if: "${undefined_var == true}"  # ERROR: undefined_var not defined
```

#### 8. Security Validation

**Checks:**
- No hardcoded secrets
- No exposed credentials
- Safe file paths
- No command injection risks

**Fails when:**
- API keys in YAML
- Passwords in params
- Absolute paths to sensitive files
- Dangerous shell commands

**Example Failure:**
```yaml
steps:
  - id: auth
    module: api.http.post
    params:
      headers:
        Authorization: "Bearer sk-1234567890"  # ERROR: Hardcoded secret
```

### Validation Severity Levels

Validation issues are categorized by severity:

#### Critical Errors

Block workflow execution completely:
- Invalid YAML syntax
- Missing required fields
- Non-existent modules
- Security violations

#### Errors

Should be fixed before production:
- Missing required parameters
- Invalid parameter types
- Broken variable references
- Duplicate step IDs

#### Warnings

Should be reviewed but not blocking:
- Deprecated module usage
- Suboptimal patterns
- Missing error handling
- Performance concerns

### Validation Output Format

Validation returns structured JSON:

```json
{
  "valid": false,
  "errors": [
    {
      "severity": "critical",
      "type": "module_not_found",
      "step_id": "send_email",
      "message": "Module 'email.send' does not exist",
      "suggestion": "Use 'notification.email.send' instead"
    }
  ],
  "warnings": [
    {
      "severity": "warning",
      "type": "missing_error_handling",
      "step_id": "api_call",
      "message": "No retry or error handling configured",
      "suggestion": "Add max_retries parameter"
    }
  ],
  "quality_score": 65
}
```

### Running Validation

#### Via Meta-Workflow

```bash
python -m src.cli.main workflows/meta/validate_workflow.yaml \
  --param target=workflows/_generated/my_workflow.yaml
```

#### Via CLI Alias (Coming Soon)

```bash
python -m src.cli.validate workflows/_generated/my_workflow.yaml
```

### Validation in Pipeline

Always validate before deployment:

```yaml
steps:
  - id: generate
    module: ai.openai.chat

  - id: save_generated
    module: data.file.write
    params:
      file_path: "workflows/_generated/new_workflow.yaml"

  - id: validate
    module: workflow.execute
    params:
      workflow_path: workflows/meta/validate_workflow.yaml
      params:
        target: "workflows/_generated/new_workflow.yaml"

  - id: only_proceed_if_valid
    if: "${validate.valid == true}"
    module: api.github.create_pr
```

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
