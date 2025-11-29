# Flyto2 Workflow DSL Documentation

Flyto2 workflows are defined as **YAML files**.
This document describes the **structure, field rules, and variable syntax** for Workflow YAML files, enabling you to:

- Write workflows by hand
- Understand UI-generated workflows
- Review workflow changes via Git diff/PR in CI/CD

> **Quick Summary:**
> **One YAML = One Workflow**
> `steps[*].module` = The atomic module to execute
> `${...}` = Variable interpolation

---

## 1. Minimal Example

```yaml
name: "Extract Page Title"
description: "Get the title from any website"

params:
  - name: url
    type: string
    label: "Website URL"
    required: true

steps:
  - id: launch_browser
    module: core.browser.launch
    params:
      headless: false

  - id: navigate
    module: core.browser.goto
    params:
      browser: "${launch_browser.browser}"
      url: "${params.url}"

  - id: extract_title
    module: core.browser.extract
    params:
      browser: "${launch_browser.browser}"
      selector: "title"
      fields:
        title:
          selector: "title"
          type: "text"

output:
  url: "${params.url}"
  title: "${extract_title.data[0].title}"
```

---

## 2. File Structure

A Flyto2 workflow YAML has the following top-level structure:

```yaml
name: "My Workflow"          # [Required] Workflow name
description: "What it does"  # [Recommended] Human-readable description
version: "1.0.0"             # [Optional] Workflow version

tags:                         # [Optional] For categorization/search
  - "browser"
  - "ai"

params:                       # [Optional] User-provided parameter definitions
  - ...

config:                       # [Optional] Workflow-level configuration
  ...

steps:                        # [Required] Workflow steps (executed sequentially)
  - id: ...
    module: ...
    params: ...
    ...

output:                       # [Optional] Workflow output (any YAML structure + interpolation)
  ...
```

### 2.1 name (Required)

**Type:** `string`

**Purpose:** Workflow name, used in CLI logs and UI display

```yaml
name: "Google Search Top 10"
```

### 2.2 description (Recommended)

**Type:** `string` or `object` (for i18n)

**Simple usage:**
```yaml
description: "Extract the title from any website"
```

**Multi-language:**
```yaml
description:
  en: "Extract the title from any website"
  zh: "取得任意網站的標題"
  ja: "任意サイトのタイトルを取得"
```

### 2.3 version (Optional)

**Type:** `string`

Does not affect execution logic, just metadata (useful for workflow schema versioning and UI display).

```yaml
version: "1.0.0"
```

### 2.4 tags (Optional)

**Type:** `string[]`

Used for UI/search/documentation, does not affect execution.

```yaml
tags: ["browser", "ai", "internal-tooling"]
```

### 2.5 config (Optional)

Workflow-level configuration that overrides engine defaults:

```yaml
config:
  browser:
    headless: true
    viewport:
      width: 1280
      height: 720

  retries:
    default_max_attempts: 2
    default_delay_ms: 500

  timeout_ms: 300000   # Workflow timeout: 300 seconds
```

**Implementation Note (Backend):**
- Merge `config` into engine's `EngineConfig` when loading YAML
- Use config defaults for steps that don't specify their own timeout/retry

---

## 3. params: External Parameter Definitions

Each workflow can define a set of parameters used in:

- CLI invocation (`--param.url=...`)
- Future HTTP API calls (POST body → params)
- UI auto-generated forms

### 3.1 Structure

```yaml
params:
  - name: keyword
    type: string            # string | number | boolean | object | array
    label: "Search Keyword" # UI label
    description: "Keyword to search on Google"
    required: true
    default: "python tutorial"
    enum:                   # [Optional] Restrict to specific options
      - "python tutorial"
      - "golang tutorial"
    min: 1                  # For type=number
    max: 100
    pattern: "^[a-zA-Z0-9 ]+$"  # For type=string (basic regex)
```

### 3.2 Accessing Values

Use `${params.<name>}` in YAML:

```yaml
params:
  - name: url
    type: string
    required: true

steps:
  - id: navigate
    module: core.browser.goto
    params:
      url: "${params.url}"
```

---

## 4. steps: Step Definitions

`steps` is an array executed **sequentially** (future: parallel/condition/loop control flow).

### 4.1 Basic Fields

```yaml
steps:
  - id: launch_browser            # [Recommended] Unique ID for referencing output
    module: core.browser.launch   # [Required] Module path
    description: "Launch browser" # [Optional] Human-readable description

    params:                       # [Optional] Parameters passed to module
      headless: false

    # Advanced: Control flow / Error handling (optional)
    if: "${params.run_browser}"   # [Optional] Conditional execution (skip if false)
    timeout_ms: 10000             # [Optional] Step timeout
    retry:
      max_attempts: 2
      delay_ms: 500
      backoff: "exponential"      # fixed | exponential | none
      retry_on:                   # [Optional] Retry based on error type/code
        - "TimeoutError"

    on_error: "fail"              # fail | skip | continue | goto
    on_error_goto: "cleanup"      # When on_error=goto, jump to this step id
```

**Minimal syntax:**

```yaml
steps:
  - module: core.browser.launch
  - module: core.browser.goto
    params:
      url: "https://example.com"
```

If `id` is omitted, engine can auto-generate (e.g., `_step_1`), but documentation recommends user-defined IDs for easier referencing.

---

## 5. Variable Interpolation / Expressions (`${ ... }`)

### 5.1 Available Namespaces

Currently defined in Flyto2:

- **params**: Workflow parameters
- **env**: Environment variables (`os.environ`)
- **Step outputs**: Shorthand as `${<stepId>}` or `${<stepId>.<field>}`
- **timestamp**: Current execution ISO timestamp (string)

#### 5.1.1 Parameters

```yaml
url: "${params.url}"
keyword: "${params.keyword}"
```

#### 5.1.2 Environment Variables

```yaml
openai_key: "${env.OPENAI_API_KEY}"
slack_webhook: "${env.SLACK_WEBHOOK_URL}"
```

#### 5.1.3 Step Outputs

If a step returns:

```python
step_output = {
  "browser": <BrowserHandle>,
  "data": [...],
  "count": 10,
}
```

In YAML:

```yaml
browser: "${launch_browser.browser}"
results: "${extract_results.data}"
count: "${extract_results.count}"
```

**Shorthand (from README):**
- `${<id>}` → equals `steps.<id>.output`
- `${<id>.<field>}` → equals `steps.<id>.output.<field>`

Engine internally maps to `steps["launch_browser"].output["browser"]`.

#### 5.1.4 System Variables

- `${timestamp}`: ISO8601 timestamp (e.g., `2025-11-29T12:34:56Z`)

---

## 6. Output Structure

`output` defines the data returned after workflow execution.
Can be any YAML structure with free interpolation:

```yaml
output:
  keyword: "${params.keyword}"
  total_results: "${extract_results.count}"
  first_result:
    title: "${extract_results.data[0].title}"
    url: "${extract_results.data[0].url}"
  generated_at: "${timestamp}"
```

Engine converts this to a dict for return (CLI prints JSON, API returns JSON body).

---

## 7. Control Flow Design (Planned/In Progress)

Some features are on the roadmap or being implemented. DSL documentation defines the syntax, modules/engine implement accordingly.

### 7.1 Conditional Execution: `if`

Every step can have an `if` clause:

```yaml
steps:
  - id: maybe_notify
    module: api.http.post
    if: "${extract_results.count > 0}"
    params:
      url: "${env.SLACK_WEBHOOK_URL}"
      body:
        text: "We have ${extract_results.count} results"
```

**Implementation Note (Backend):**
- Evaluate `if` expression before executing step
- If falsy (false/0/empty string/empty array), skip execution with `status=SKIPPED` (for logging)
- Expression engine can start simple:
  - Support `${...}` + basic operations (`==`, `>`, `<`, `contains`)
  - Or allow only "boolean string result" where upstream pre-calculates pass/fail

### 7.2 Loop: DSL Design Suggestion

While `core.flow.loop` module works, DSL can provide more readable syntax:

**Current (module version):**
```yaml
steps:
  - id: loop_results
    module: core.flow.loop
    params:
      items: "${extract_results.data}"
      as: item
      steps:
        - module: core.data.filter
          params:
            input: "${item}"
            condition: "${item.url contains 'mysite.com'}"
```

**Future (DSL syntax sugar):**
```yaml
steps:
  - id: process_each
    loop:
      items: "${extract_results.data}"
      as: item
      steps:
        - module: core.data.filter
          params:
            input: "${item}"
            condition: "${item.url contains 'mysite.com'}"
```

Use module version for now; mark DSL version as roadmap.

### 7.3 Parallel Execution

Similar concept, implementable via module:

```yaml
steps:
  - id: fetch_in_parallel
    module: core.flow.parallel
    params:
      branches:
        - steps:
            - module: api.http.get
              params:
                url: "https://api.service1.com"
        - steps:
            - module: api.http.get
              params:
                url: "https://api.service2.com"
```

---

## 8. Error Handling / Retry

Each step can have error handling configuration:

```yaml
steps:
  - id: call_api
    module: api.http.get
    params:
      url: "https://example.com"
    timeout_ms: 5000
    retry:
      max_attempts: 3
      delay_ms: 500
      backoff: "exponential"  # fixed | exponential | none
      retry_on:
        - "TimeoutError"
        - "ConnectionError"
    on_error: "fail"           # fail | skip | continue | goto
    on_error_goto: "cleanup"   # Used when on_error=goto
```

**Implementation Suggestion:**

Wrap single-step execution with retry logic:
1. Attempt to execute module
2. Catch exception → check if in `retry_on` → sleep → retry
3. After exceeding `max_attempts`, enter `on_error` branch:
   - **fail**: Terminate entire workflow, mark as failed
   - **skip**: Skip this step, mark as `SKIPPED`, continue to next step
   - **continue**: Same as skip, but preserve error info in context (`steps.call_api.error`)
   - **goto**: Jump to specified `on_error_goto` step id and continue

---

## 9. Module ID Naming Convention

Modules (`module` field) should use namespace paths:

- `core.browser.launch`
- `core.browser.goto`
- `core.browser.type`
- `core.browser.extract`
- `core.ai.openai.chat`
- `api.http.get`
- `api.http.post`

Benefits:
- Auto-generate module lists (NAMESPACES)
- UI categorization
- Documentation organization

---

## 10. Complete Example: Google Search Top 10

```yaml
name: "Google Search Top 10"
description: "Extract top 10 Google search results for a keyword"
version: "1.0.0"
tags: ["google", "search", "scraping"]

params:
  - name: keyword
    type: string
    label: "Search Keyword"
    description: "The keyword to search on Google"
    required: true
    default: "python tutorial"

  - name: max_results
    type: number
    label: "Maximum Results"
    description: "Number of results to extract (1-100)"
    required: false
    default: 10
    min: 1
    max: 100

steps:
  - id: launch_browser
    module: core.browser.launch
    params:
      headless: true

  - id: goto_google
    module: core.browser.goto
    params:
      browser: "${launch_browser.browser}"
      url: "https://www.google.com"

  - id: type_keyword
    module: core.browser.type
    params:
      browser: "${launch_browser.browser}"
      selector: 'input[name="q"]'
      text: "${params.keyword}"

  - id: submit_search
    module: core.browser.press
    params:
      browser: "${launch_browser.browser}"
      key: "Enter"

  - id: wait_results
    module: core.browser.wait
    params:
      browser: "${launch_browser.browser}"
      selector: "#search"
      timeout_ms: 10000

  - id: extract_results
    module: core.browser.extract
    params:
      browser: "${launch_browser.browser}"
      selector: "#search .g"
      limit: "${params.max_results}"
      fields:
        title:
          selector: "h3"
          type: "text"
        url:
          selector: "a"
          type: "attribute"
          attribute: "href"
        description:
          selector: ".VwiC3b"
          type: "text"

output:
  keyword: "${params.keyword}"
  count: "${extract_results.count}"
  results: "${extract_results.data}"
  generated_at: "${timestamp}"
```

---

## 11. Backward Compatibility & Reserved Fields

To allow future expansion, the following keys are reserved and should not be used as parameter/step field names:

- `name`
- `description`
- `version`
- `tags`
- `params`
- `config`
- `steps`
- `output`
- `env` (if future per-workflow env override)
- `schedule` (if future built-in scheduling)

---

## 12. Contributor Guidelines (Module Authors)

If you're writing your own module, please follow:

1. **module_id** = `namespace.subnamespace.action` (e.g., `core.browser.click`)

2. **Register with metadata:**
   ```python
   @register_module(
       module_id="core.browser.click",
       label="Click Element",
       description="Click an element on the page"
   )
   class BrowserClickModule(BaseModule):
       async def execute(self) -> Dict[str, Any]:
           # ...
           return {"clicked": True}
   ```

3. **Return a dict** from `execute()`, which goes directly into `steps.<id>.output`

---

## 13. Documentation Split Suggestion

If you want to split this DSL documentation:

- **docs/WORKFLOW_BASICS.md**: Minimal examples + basic structure
- **docs/DSL_REFERENCE.md**: Advanced features (if/loop/retry, etc.)

This DSL spec aligns with current implementation and reserves space for future features without over-promising.

---

**Last Updated:** 2025-11-29
**Version:** 1.0.0-alpha
