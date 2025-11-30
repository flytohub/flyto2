# Parameter Design Best Practices

A comprehensive guide to designing flexible, reusable workflows with Flyto2's parameter system.

---

## Table of Contents

1. [When to Hardcode vs Use Parameters](#when-to-hardcode-vs-use-parameters)
2. [The Three Workflow Patterns](#the-three-workflow-patterns)
3. [Parameter Naming Conventions](#parameter-naming-conventions)
4. [Real-World Examples](#real-world-examples)
5. [Common Pitfalls](#common-pitfalls)
6. [Security Best Practices](#security-best-practices)

---

## When to Hardcode vs Use Parameters

### ✅ Use Hardcoded Values For:

**Technical Configuration** - Values that define how the workflow works:
```yaml
steps:
  - id: browser
    module: core.browser.launch
    params:
      headless: true          # ← Hardcoded: technical choice
      timeout_ms: 30000       # ← Hardcoded: workflow requirement
      viewport:
        width: 1920
        height: 1080
```

**Fixed Selectors** - DOM selectors that match your specific use case:
```yaml
steps:
  - id: extract
    module: core.browser.extract
    params:
      selector: "#search-results .item"  # ← Hardcoded: specific to Google
      fields:
        title:
          selector: "h3"                  # ← Hardcoded: known structure
```

**Workflow Logic** - Control flow and execution settings:
```yaml
steps:
  - id: api_call
    module: api.http.get
    retry:
      max_attempts: 3        # ← Hardcoded: reliability requirement
      delay_ms: 1000         # ← Hardcoded: workflow design
    on_error: continue       # ← Hardcoded: error handling strategy
```

### ✅ Use `${params.*}` For:

**Business Data** - Values that change based on what you're searching/processing:
```yaml
params:
  - name: keyword
    type: string
    required: true

steps:
  - id: search
    module: core.browser.type
    params:
      text: "${params.keyword}"  # ← Parameter: user input
```

**External Inputs** - File paths, URLs, IDs:
```yaml
params:
  - name: target_url
    type: string
    default: "https://example.com"

  - name: output_file
    type: string
    default: "results.csv"

steps:
  - id: navigate
    module: core.browser.goto
    params:
      url: "${params.target_url}"  # ← Parameter: configurable target

  - id: export
    module: data.csv.write
    params:
      file_path: "${params.output_file}"  # ← Parameter: user-defined path
```

**Quantitative Controls** - Limits, counts, ranges:
```yaml
params:
  - name: max_results
    type: number
    default: 10
    min: 1
    max: 100

steps:
  - id: extract
    module: core.browser.extract
    params:
      limit: "${params.max_results}"  # ← Parameter: user preference
```

### ✅ Use `${env.*}` For:

**Sensitive Information** - API keys, tokens, passwords:
```yaml
steps:
  - id: api_call
    module: api.http.get
    params:
      headers:
        Authorization: "Bearer ${env.GITHUB_TOKEN}"  # ← Environment: secret

  - id: notify
    module: notification.slack.send_message
    params:
      webhook_url: "${env.SLACK_WEBHOOK_URL}"  # ← Environment: secret
```

**Environment-Specific Configuration** - Different values per environment:
```yaml
steps:
  - id: database_query
    module: database.postgresql.query
    params:
      connection_string: "${env.DATABASE_URL}"  # ← Environment: varies by env
      # Production: postgresql://prod.example.com/db
      # Staging: postgresql://staging.example.com/db
      # Development: postgresql://localhost/dev_db
```

---

## The Three Workflow Patterns

### Pattern 1: Fixed Workflow (No Parameters)

**Use when:** Workflow does the same thing every time.

```yaml
name: "Daily Health Check"
description: "Check if production services are up"

# No params section - everything is hardcoded

steps:
  - id: check_api
    module: api.http.get
    params:
      url: "https://api.example.com/health"
      timeout_ms: 5000

  - id: check_database
    module: database.postgresql.query
    params:
      connection_string: "${env.DATABASE_URL}"
      query: "SELECT 1"

  - id: notify_if_down
    module: notification.slack.send_message
    if: "${check_api.status_code != 200 || check_database.error}"
    params:
      webhook_url: "${env.SLACK_WEBHOOK_URL}"
      text: "Production services are down!"
```

**Running:**
```bash
# Always the same
python -m src.cli.main workflows/health_check.yaml
```

**Advantages:**
- ✅ Simple to understand
- ✅ No configuration needed
- ✅ Perfect for scheduled tasks

---

### Pattern 2: Template Workflow (All Parameters)

**Use when:** Workflow is reusable for different inputs.

```yaml
name: "Google Search Template"
description: "Reusable Google search workflow"

# Define all configurable parameters
params:
  - name: keyword
    type: string
    required: true
    label: "Search Keyword"
    placeholder: "python tutorial"

  - name: max_results
    type: number
    default: 10
    min: 1
    max: 100
    label: "Maximum Results"

  - name: headless
    type: boolean
    default: false
    label: "Run Headless"

  - name: output_format
    type: string
    default: "json"
    enum: ["json", "csv", "txt"]
    label: "Output Format"

steps:
  - id: browser
    module: core.browser.launch
    params:
      headless: "${params.headless}"  # ← Configurable

  - id: search
    module: core.browser.type
    params:
      text: "${params.keyword}"  # ← Configurable

  - id: extract
    module: core.browser.extract
    params:
      limit: "${params.max_results}"  # ← Configurable

  - id: export
    module: data.${params.output_format}.write  # ← Dynamic module selection!
    params:
      data: "${extract.data}"
```

**Running (different ways):**
```bash
# Interactive mode
python -m src.cli.main workflows/google_search_template.yaml

# Quick test
python -m src.cli.main workflows/google_search_template.yaml \
  --param keyword="nodejs tutorial"

# Production config
python -m src.cli.main workflows/google_search_template.yaml \
  --params-file configs/prod_search.json

# CI/CD
python -m src.cli.main workflows/google_search_template.yaml \
  --param keyword="$SEARCH_TERM" \
  --param max_results=50 \
  --param headless=true
```

**Advantages:**
- ✅ Highly reusable
- ✅ Version-controlled parameters via JSON files
- ✅ Easy to test with different inputs

---

### Pattern 3: Hybrid Workflow (Sensible Defaults + Override)

**Use when:** Workflow works out-of-the-box but allows customization.

```yaml
name: "GitHub Issue Monitor"
description: "Monitor GitHub issues with sensible defaults"

params:
  # Required parameters (no defaults)
  - name: repo_owner
    type: string
    required: true
    label: "Repository Owner"

  - name: repo_name
    type: string
    required: true
    label: "Repository Name"

  # Optional parameters with defaults
  - name: state
    type: string
    default: "open"
    enum: ["open", "closed", "all"]

  - name: labels
    type: string
    default: "bug"

  - name: alert_threshold
    type: number
    default: 10

steps:
  - id: fetch_issues
    module: api.github.list_issues
    params:
      owner: "${params.repo_owner}"
      repo: "${params.repo_name}"
      state: "${params.state}"        # ← Default: "open"
      labels: "${params.labels}"      # ← Default: "bug"
      token: "${env.GITHUB_TOKEN}"    # ← Always from environment

  - id: notify
    module: notification.slack.send_message
    if: "${fetch_issues.count > params.alert_threshold}"
    params:
      webhook_url: "${env.SLACK_WEBHOOK_URL}"
      text: "Alert: ${fetch_issues.count} ${params.labels} issues in ${params.repo_owner}/${params.repo_name}"
```

**Running (progressive complexity):**
```bash
# Minimal (use defaults)
python -m src.cli.main workflows/github_monitor.yaml \
  --param repo_owner=facebook \
  --param repo_name=react

# Override some defaults
python -m src.cli.main workflows/github_monitor.yaml \
  --param repo_owner=facebook \
  --param repo_name=react \
  --param labels=security \
  --param alert_threshold=5

# Production with config file
python -m src.cli.main workflows/github_monitor.yaml \
  --params-file repos/react_monitoring.json \
  --env-file .env.production
```

**Advantages:**
- ✅ Works immediately with minimal input
- ✅ Flexible for advanced use cases
- ✅ Best of both worlds

---

## Parameter Naming Conventions

### Use Clear, Descriptive Names

**❌ Bad:**
```yaml
params:
  - name: k      # What is "k"?
  - name: num    # Number of what?
  - name: data   # Too generic
```

**✅ Good:**
```yaml
params:
  - name: keyword
  - name: max_results
  - name: user_data
```

### Use Consistent Naming Patterns

**Quantitative limits:** Use `max_*`, `min_*`, `limit_*`
```yaml
params:
  - name: max_results
  - name: max_retries
  - name: timeout_seconds
```

**Boolean flags:** Use `is_*`, `has_*`, `enable_*`
```yaml
params:
  - name: headless          # ← Simple boolean
  - name: enable_logging    # ← Explicit enable flag
  - name: is_production     # ← State check
```

**Identifiers:** Use `*_id`, `*_name`
```yaml
params:
  - name: user_id
  - name: repo_name
  - name: workflow_id
```

---

## Real-World Examples

### Example 1: Web Scraper (Template Pattern)

```yaml
name: "Generic Web Scraper"

params:
  - name: target_url
    type: string
    required: true

  - name: selector
    type: string
    required: true

  - name: output_file
    type: string
    default: "output_${timestamp}.json"

steps:
  - id: browser
    module: core.browser.launch
    params:
      headless: true  # ← Hardcoded: always headless in production

  - id: navigate
    module: core.browser.goto
    params:
      browser: "${browser.browser}"
      url: "${params.target_url}"  # ← Parameter: user-defined

  - id: extract
    module: core.browser.extract
    params:
      browser: "${browser.browser}"
      selector: "${params.selector}"  # ← Parameter: user-defined

  - id: save
    module: file.write
    params:
      file_path: "${params.output_file}"  # ← Parameter: user-defined
      content: "${extract.data}"
```

**Usage:**
```bash
# Scrape different sites with same workflow
python -m src.cli.main workflows/scraper.yaml \
  --param target_url=https://news.ycombinator.com \
  --param selector=".storylink"

python -m src.cli.main workflows/scraper.yaml \
  --param target_url=https://reddit.com/r/programming \
  --param selector=".title"
```

### Example 2: CI/CD Deployment (Hybrid Pattern)

```yaml
name: "Deploy to Environment"

params:
  - name: environment
    type: string
    required: true
    enum: ["dev", "staging", "production"]

  - name: build_number
    type: string
    required: true

  - name: skip_tests
    type: boolean
    default: false

  - name: notify_team
    type: boolean
    default: true

steps:
  - id: run_tests
    module: testing.run_tests
    if: "${!params.skip_tests}"  # ← Skip if flag is true
    params:
      test_suite: "integration"
      timeout_ms: 300000  # ← Hardcoded: 5 minutes max

  - id: deploy
    module: deployment.kubernetes.deploy
    params:
      namespace: "${params.environment}"
      image_tag: "v${params.build_number}"
      replicas: 3  # ← Hardcoded: always 3 replicas

  - id: notify_slack
    module: notification.slack.send_message
    if: "${params.notify_team}"
    params:
      webhook_url: "${env.SLACK_WEBHOOK_URL}"
      text: "Deployed build ${params.build_number} to ${params.environment}"
```

**Usage:**
```bash
# Development deploy (quick, skip tests)
python -m src.cli.main workflows/deploy.yaml \
  --param environment=dev \
  --param build_number=1234 \
  --param skip_tests=true \
  --param notify_team=false

# Production deploy (full process)
python -m src.cli.main workflows/deploy.yaml \
  --param environment=production \
  --param build_number=1234 \
  --env-file .env.production
```

---

## Common Pitfalls

### ❌ Pitfall 1: Over-Parameterization

**Bad:**
```yaml
params:
  - name: browser_headless
  - name: browser_width
  - name: browser_height
  - name: browser_timeout
  - name: search_selector
  - name: result_selector
  - name: title_selector
  # ... 20 more parameters
```

**Problem:** Too complex, hard to use, defeats the purpose.

**Solution:** Only parameterize what actually varies between runs.

```yaml
params:
  - name: keyword     # ← Varies every time
  - name: max_results # ← Sometimes varies

steps:
  - id: browser
    module: core.browser.launch
    params:
      headless: true     # ← Always the same, hardcode it
      width: 1920        # ← Always the same, hardcode it
      height: 1080       # ← Always the same, hardcode it
```

### ❌ Pitfall 2: Secrets in Parameters

**Bad:**
```yaml
params:
  - name: api_key      # ❌ DON'T DO THIS
    type: string
```

```bash
# ❌ Secrets visible in command history!
python -m src.cli.main workflow.yaml --param api_key=sk_live_xxxxx
```

**Solution:** Always use environment variables for secrets.

```yaml
steps:
  - id: api_call
    module: api.http.get
    params:
      headers:
        Authorization: "Bearer ${env.API_KEY}"  # ✅ From environment
```

```bash
# ✅ Secrets in .env file
python -m src.cli.main workflow.yaml --env-file .env.production
```

### ❌ Pitfall 3: No Default Values

**Bad:**
```yaml
params:
  - name: max_results
    type: number
    required: true  # ❌ Forces users to always specify
```

**Problem:** Annoying for users who want defaults.

**Solution:** Provide sensible defaults.

```yaml
params:
  - name: max_results
    type: number
    default: 10     # ✅ Works out of the box
    min: 1
    max: 100
```

---

## Security Best Practices

### 1. Never Commit Secrets

**Setup `.gitignore`:**
```bash
# .gitignore
.env
.env.*
secrets/
*.key
*.pem
credentials.json
```

**Use environment files:**
```bash
# .env.production (NOT in Git)
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxx
DATABASE_URL=postgresql://user:pass@host/db
```

### 2. Use Different `.env` Files Per Environment

```
.env.development    # Local development
.env.staging        # Staging environment
.env.production     # Production environment
```

```bash
# Development
python -m src.cli.main workflow.yaml --env-file .env.development

# Production
python -m src.cli.main workflow.yaml --env-file .env.production
```

### 3. Validate Sensitive Parameters

**Mark parameters as sensitive:**
```yaml
params:
  - name: api_token
    type: string
    required: true
    sensitive: true  # ← Won't be logged
```

**Use module-level security settings:**
```yaml
steps:
  - id: api_call
    module: api.http.post
    security:
      credentials_required: true
      allowed_domains: ["api.example.com"]  # ← Restrict domains
    params:
      headers:
        Authorization: "Bearer ${env.API_TOKEN}"
```

### 4. CI/CD Secret Management

**GitHub Actions:**
```yaml
- name: Run workflow
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  # ← From GitHub Secrets
    SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
  run: |
    python -m src.cli.main workflow.yaml
```

**Never:**
```yaml
# ❌ DON'T DO THIS
run: |
  python -m src.cli.main workflow.yaml --param api_key=sk_live_xxxxx
```

---

## Summary

| Scenario | Use | Example |
|----------|-----|---------|
| Technical config | Hardcode | `headless: true` |
| User input | `${params.*}` | `keyword: "${params.keyword}"` |
| Secrets | `${env.*}` | `token: "${env.GITHUB_TOKEN}"` |
| Defaults | `${params.*}` with `default:` | `max_results: 10` |
| Fixed selectors | Hardcode | `selector: "#search"` |
| Environment-specific | `${env.*}` | `database: "${env.DATABASE_URL}"` |

**Key Principle:** Parameterize what varies, hardcode what doesn't.

---

## Next Steps

- Read [CLI Guide](CLI.md) for parameter passing methods
- See [DSL Specification](DSL.md) for complete syntax
- Check [Example Workflows](../workflows/) for real implementations
