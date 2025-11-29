# Workflow DSL Specification

This document defines the YAML-based Domain-Specific Language (DSL) for Flyto2 workflow automation engine.

**Version:** 1.0.0
**Status:** Alpha
**Last Updated:** 2025-11-29

---

## Table of Contents

- [Design Goals](#design-goals)
- [Workflow File Structure](#workflow-file-structure)
- [Parameter Definition (params)](#parameter-definition-params)
- [Steps](#steps)
- [Global Error Handling](#global-error-handling)
- [Workflow Output](#workflow-output)
- [Expression Syntax](#expression-syntax)
- [Subflows](#subflows)
- [Naming Conventions](#naming-conventions)
- [Examples](#examples)
- [Future Enhancements](#future-enhancements)

---

## Design Goals

- **Human Readable**: Workflows expressed in YAML, not hidden in databases or UIs
- **Git Friendly**: Suitable for git diff, PR reviews, and rollbacks
- **Composable**: Each step is an atomic module; workflows can be arbitrarily combined
- **Portable**: Same YAML file runs on local, Docker, Kubernetes, CI/CD, or servers
- **Developer Friendly**: Variables, error handling, conditions, and loops clearly defined in DSL

---

## Workflow File Structure

A workflow is a `.yaml` file with the following basic structure:

```yaml
id: google-search-top10
name: "Google Search Top 10"
version: "1.1.0"

description:
  en: "Extract top 10 Google search results for a keyword"
  zh: "提取 Google 搜尋結果的前 10 筆"

author: "Workflow Engine Team"
tags: ["google", "search", "scraping"]

engine: "browser-flow"

config:
  browser:
    headless: false
  timeout_ms: 60000

params:
  # User-provided parameters
steps:
  # Execution steps
error:
  # Error handling
output:
  # Workflow output
```

### Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | Globally unique workflow identifier (used in CLI/UI/API) |
| `name` | string | ✅ | Display name |
| `version` | string | ✅ | Semantic version (e.g., 1.0.0) |
| `description` | string / map | ❌ | Can be a simple string or i18n object `{en, zh, ...}` |
| `author` | string | ❌ | Author/maintainer information |
| `tags` | string[] | ❌ | Tags for UI categorization and search |
| `engine` | string | ✅ | Execution engine type: `browser-flow`, `http-flow`, `subflow` |
| `config` | object | ❌ | Workflow-local config (overrides global config) |
| `params` | Param[] | ❌ | User-provided parameters |
| `steps` | Step[] | ✅ | Workflow steps list |
| `error` | ErrorConfig | ❌ | Global error handling strategy |
| `output` | OutputSpec | ❌ | Workflow output definition |

---

## Parameter Definition (params)

`params` is an array where each param describes an input parameter (usable via CLI, UI, or API).

```yaml
params:
  - name: keyword
    type: string
    label:
      en: "Search Keyword"
      zh: "搜尋關鍵字"
    description:
      en: "The keyword to search on Google"
    placeholder: "python tutorial"
    required: true
    default: "python tutorial"
    validation:
      min_length: 1
      max_length: 100

  - name: max_results
    type: number
    label: "Maximum Results"
    description: "Number of results (1–100)"
    default: 10
    min: 1
    max: 100
    required: false
    advanced: true

  - name: output_format
    type: string
    label: "Output Format"
    default: "json"
    enum: ["json", "csv", "markdown"]
```

### Param Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ | Parameter name, accessed via `params.<name>` in DSL |
| `type` | "string" \| "number" \| "boolean" \| "array" \| "object" | ✅ | Parameter type |
| `label` | string / map | ❌ | UI display text, can support i18n |
| `description` | string / map | ❌ | UI/documentation description |
| `placeholder` | string | ❌ | UI placeholder |
| `required` | boolean | ❌ | Whether required (default: false) |
| `default` | any | ❌ | Default value (used when not provided) |
| `enum` | any[] | ❌ | Restrict to specific values |
| `min` / `max` | number | ❌ | Range validation for number types |
| `validation` | object | ❌ | Custom validation (e.g., min_length, max_length) |
| `advanced` | boolean | ❌ | Hide in UI "Advanced Settings" |
| `show_if` | object | ❌ | Control parameter visibility based on other params |

### show_if Structure

```yaml
show_if:
  field: "save_to_file"
  equals: true
```

In UI/tools, this parameter only shows when `params.save_to_file === true`.

---

## Steps

`steps` is a list executed **sequentially from top to bottom**. Each step performs one atomic action.

```yaml
steps:
  - id: launch_browser
    module: core.browser.launch
    description: "Launch web browser"
    params:
      headless: "${config.browser.headless}"
    output:
      browser: "${result.browser}"
      page: "${result.page}"
    on_error:
      retry: 1
      backoff_ms: 1000
      fatal: true

  - id: goto_google
    module: core.browser.goto
    description: "Navigate to Google"
    params:
      browser: "${launch_browser.browser}"
      url: "https://www.google.com"
      wait_until: "networkidle"

  - id: wait_search_box
    module: core.browser.wait
    description: "Wait for search input"
    params:
      browser: "${launch_browser.browser}"
      selector: 'input[name="q"], textarea[name="q"]'
      timeout_ms: 10000
```

### Step Common Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | Unique step ID for referencing (`<id>.<field>`) |
| `module` | string | ✅ | Module ID to invoke (e.g., `core.browser.launch`) |
| `description` | string | ❌ | Text description for UI or logs |
| `params` | object | ❌ | Parameters to pass to module (can contain expressions) |
| `output` | object | ❌ | Define which data to expose for subsequent steps |
| `when` | string | ❌ | Conditional expression; skips step if evaluates to false |
| `always` | boolean | ❌ | If true, executes even if previous steps failed (like finally) |
| `on_error` | object | ❌ | Step-level error handling config |

### Context Variables in params

In `params` (and `when`, `output`), you can use `${ ... }` expressions.
Available variables:

| Name | Description |
|------|-------------|
| `params` | User input parameters, e.g., `params.keyword` |
| `config` | Workflow config object |
| `env` | Environment variables, e.g., `env.OPENAI_API_KEY` |
| `steps` | All executed step outputs, e.g., `steps.launch_browser.output.browser` |
| `<stepId>` | Shorthand alias equivalent to `steps.<stepId>.output`, e.g., `launch_browser.browser` |
| `utils` | System-provided utility functions, e.g., `utils.slug()`, `utils.clean_url()` |
| `timestamp` | Current execution timestamp (ISO string) |
| `error` | Error object available in error handlers |
| `result` | Current module's raw result (only during output mapping) |

### output Field

`output` extracts parts of the module execution result, naming them for use in subsequent steps.

```yaml
- id: extract_results
  module: core.browser.extract
  params:
    browser: "${launch_browser.browser}"
    selector: "#search .g"
    limit: "${params.max_results || 10}"
    fields:
      title: { selector: "h3", type: "text" }
      url:   { selector: "a", type: "attribute", attribute: "href" }
  output:
    items: "${result.items}"
    count: "${result.items.length}"
```

Subsequent steps can reference:

```yaml
params:
  input: "${extract_results.items}"
  limit: "${extract_results.count}"
```

Equivalent to:

```yaml
params:
  input: "${steps.extract_results.output.items}"
```

### when - Conditional Execution

If `when` exists, it's evaluated first; if result is falsy (false / 0 / '' / null / undefined), the step is **skipped**.

```yaml
- id: save_to_file_step
  module: core.fs.write
  description: "Save results to file if enabled"
  when: "${params.save_to_file === true}"
  params:
    dir: "${params.output_dir || './results'}"
    filename: "google_search_${utils.slug(params.keyword)}_${timestamp}.txt"
    content: "${format_results.payload}"
```

### always (like finally)

If `always: true`, this step executes even if previous steps failed or workflow threw an error (typically used for cleanup like closing browsers).

```yaml
- id: close_browser
  module: core.browser.close
  description: "Close browser"
  params:
    browser: "${launch_browser.browser}"
  always: true
```

### Step-Level Error Handling (on_error)

Each step can configure retry/backoff/fatal behavior.

```yaml
- id: launch_browser
  module: core.browser.launch
  params:
    headless: "${config.browser.headless}"
  output:
    browser: "${result.browser}"
  on_error:
    retry: 1           # Number of retries on failure
    backoff_ms: 1000   # Wait time before each retry
    fatal: true        # If true, failure after retries terminates workflow
```

Field descriptions:

| Field | Type | Description |
|-------|------|-------------|
| `retry` | number | Maximum retry attempts |
| `backoff_ms` | number | Milliseconds to wait between retries |
| `fatal` | boolean | If true, step failure after retries terminates workflow |

---

## Global Error Handling

Besides step-level `on_error`, workflows can set global error handling strategies.

```yaml
error:
  on_error:
    - module: core.log.error
      params:
        message: "Google Search Top 10 workflow failed"
        error: "${error}"
    - module: core.browser.safe_close
      params:
        browser: "${launch_browser.browser}"

  strategy:
    stop_on_error: true
```

### Structure

| Field | Type | Description |
|-------|------|-------------|
| `on_error` | StepLike[] | When any step throws an unhandled error, execute these error handlers sequentially |
| `strategy` | object | Control whether to continue after errors, etc. |

`on_error` items are similar to regular steps (but typically don't need id/output):

```yaml
error:
  on_error:
    - module: core.log.error
      params:
        message: "Workflow failed"
        error: "${error}"
```

`strategy` can include:

```yaml
strategy:
  stop_on_error: true   # Default true; stops workflow on error
  # Future extensions: continue_on_non_fatal, max_error_steps, etc.
```

---

## Workflow Output

`output` defines the payload structure returned when workflow executes successfully.
The engine evaluates all expressions to compose the final returned JSON.

```yaml
output:
  fields:
    keyword:       "${params.keyword}"
    results:       "${normalize_results.items}"
    count:         "${normalize_results.count}"
    format:        "${params.output_format || 'json'}"
    saved_to_file: "${params.save_to_file === true}"
    file_path:     "${save_to_file_step.file_path || null}"
    timestamp:     "${timestamp}"
```

Final returned JSON:

```json
{
  "keyword": "...",
  "results": [ ... ],
  "count": 10,
  "format": "json",
  "saved_to_file": true,
  "file_path": "./results/xxx.txt",
  "timestamp": "2025-11-29T..."
}
```

**Convention:**
- `output` can use the same expression syntax and variable sources as step params
- Engine may choose to wrap as `{ ok: true, data: <output.fields> }` (but DSL level defines fields only)

---

## Expression Syntax (`${ ... }`)

### Basic Rules

Any string that is `${...}` (both prefix and suffix) is treated as an "expression" and evaluated via safe executor.

Other types (number / boolean / array / object) remain unchanged.

```yaml
params:
  url: "https://google.com"                        # Plain string
  query: "${params.keyword}"                       # Variable access
  limit: "${params.max_results || 10}"             # Logical operation
  filename: "google_${utils.slug(params.keyword)}_${timestamp}.json" # ❌ Currently treated as plain string (template strings need engine support)
```

**DSL v1 Recommendation:** Only support entire field as `${...}`.
Mixed string + expression templates should be handled by modules or future extensions.

### Available Variables

| Variable | Description |
|----------|-------------|
| `params` | Workflow parameters object |
| `config` | Workflow config |
| `env` | Environment variables |
| `steps` | All executed step outputs, `steps.<id>.output.<field>` |
| `<stepId>` | Shorthand: `<stepId>.<field>` = `steps.<stepId>.output.<field>` |
| `result` | Current step module return value (only during output mapping) |
| `utils` | Utility functions (slug, clean_url, ...) |
| `timestamp` | Current execution timestamp |
| `error` | Error object in error handlers |

### Expression Engine

Implementation can be:

```javascript
new Function("scope", "with (scope) { return (EXPRESSION); }")
scope = { params, config, env, steps, utils, timestamp, error, result, <stepId aliases> }
```

DSL spec only defines "what's available", not implementation details.

---

## Subflows

### Subflow Definition

For reusable sub-workflows:

```yaml
id: common-normalize-search-results
name: "Normalize Search Results"
engine: "subflow"

params:
  - name: items
    type: array
    required: true

steps:
  - id: normalize
    module: core.data.transform
    params:
      input: "${params.items}"
      operations:
        - type: "add_index"
          field: "position"
          start_from: 1
    output:
      items: "${result.items}"

output:
  fields:
    items: "${normalize.items}"
```

### Calling Subflows in Workflows

Via a module like `core.flow.call`:

```yaml
- id: normalize_results
  module: core.flow.call
  params:
    flow_id: "common-normalize-search-results"
    inputs:
      items: "${extract_results.items}"
  output:
    items: "${result.items}"
```

**Convention:** Subflow's `output.fields` are treated as top-level `result`.

---

## Naming Conventions

### Workflow / Subflow ID

- Use `kebab-case`: `google-search-top10`, `daily-admin-report`, `seo-rank-tracker`
- Must be globally unique

### Module ID

- Use namespace + function: `core.browser.launch`, `core.fs.write`, `ai.openai.chat`
- Keep atomic: one module does one thing

### Step ID

- `snake_case` or `kebab-case` both acceptable, but recommend `snake_case`:
  - `launch_browser`, `extract_results`, `normalize_results`, `save_to_file_step`

---

## Examples

### Example 1: Minimal Workflow

```yaml
id: extract-page-title
name: "Extract Page Title"
version: "1.0.0"

description: "Extract the title from any webpage"

params:
  - name: url
    type: string
    required: true
    label: "Target URL"
    placeholder: "https://example.com"

steps:
  - id: launch_browser
    module: core.browser.launch
    params:
      headless: true

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
    output:
      title: "${result.data[0].text}"

  - id: close_browser
    module: core.browser.close
    params:
      browser: "${launch_browser.browser}"
    always: true

output:
  fields:
    url: "${params.url}"
    title: "${extract_title.title}"
    timestamp: "${timestamp}"
```

### Example 2: Conditional Execution & Error Handling

```yaml
id: resilient-api-call
name: "Resilient API Call"
version: "1.0.0"

description: "Call API with automatic retry and fallback"

params:
  - name: api_url
    type: string
    required: true

steps:
  - id: primary_api
    module: core.api.http_get
    params:
      url: "${params.api_url}"
    on_error:
      retry: 3
      backoff_ms: 2000
      fatal: false

  - id: fallback_api
    module: core.api.http_get
    params:
      url: "${env.FALLBACK_API_URL}"
    when: "${primary_api.status != 'success'}"

  - id: process_data
    module: core.data.transform
    params:
      input: "${primary_api.status == 'success' ? primary_api.data : fallback_api.data}"

output:
  fields:
    source: "${primary_api.status == 'success' ? 'primary' : 'fallback'}"
    data: "${process_data.result}"
```

### Example 3: Loop & Parallel

```yaml
id: multi-page-scraper
name: "Multi-Page Scraper"
version: "1.0.0"

params:
  - name: page_urls
    type: array
    required: true

steps:
  - id: launch_browser
    module: core.browser.launch

  - id: scrape_pages
    module: core.flow.loop
    params:
      items: "${params.page_urls}"
      item_var: "page_url"
      output_mode: collect
      steps:
        - id: navigate
          module: core.browser.goto
          params:
            browser: "${launch_browser.browser}"
            url: "${page_url}"

        - id: extract
          module: core.browser.extract
          params:
            browser: "${launch_browser.browser}"
            selector: ".content"

  - id: cleanup
    module: core.browser.close
    params:
      browser: "${launch_browser.browser}"
    always: true

output:
  fields:
    pages_scraped: "${scrape_pages.count}"
    data: "${scrape_pages.results}"
```

---

## Future Enhancements

These are not part of v1 spec but planned for future versions:

- **flow.loop**: DSL-level loop step support (iterate over arrays)
- **flow.switch**: Multi-branch conditionals
- **parallel**: Parallel step group execution
- **triggers**: Define schedule/webhook/queue triggers in DSL (currently in JSON/README)
- **Template strings**: Support `"hello ${params.name}"` mixed-string templates

---

## TL;DR (Quick Summary)

1. **Workflow is a YAML file** containing `id`, `engine`, `params`, `steps`, `error`, `output`
2. **Each step points to a module**, uses `params` to pass data, `output` to extract results
3. **Expressions use `${ ... }`**, scope includes: `params`, `config`, `env`, `steps`, `utils`, `timestamp`
4. **`when` controls conditional execution**, `always` for cleanup, `on_error` for retry/fatal control
5. **`output.fields` determines workflow return result**
6. **Subflows defined with `engine: subflow`**, called via `core.flow.call`

---

## Contributing

This DSL specification is versioned alongside the engine. To propose changes:

1. Open an issue describing the use case
2. Discuss syntax and semantics
3. Update this document with proposed changes
4. Implement in the engine
5. Add tests and examples

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed contribution guidelines.

---

**Last Updated:** 2025-11-29
**Version:** 1.0.0-alpha
