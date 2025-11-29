# Workflow DSL Specification

This document defines the complete YAML DSL (Domain-Specific Language) for Flyto2.

**Version:** 1.0.0
**Status:** Alpha
**Last Updated:** 2025-01-29

---

## Table of Contents

- [Overview](#overview)
- [Workflow Structure](#workflow-structure)
- [Variable Resolution](#variable-resolution)
- [Step Definition](#step-definition)
- [Flow Control](#flow-control)
- [Error Handling](#error-handling)
- [Output Mapping](#output-mapping)
- [Complete Examples](#complete-examples)

---

## Overview

Workflows are defined in YAML files with a standardized structure. The engine:

1. **Parses** the YAML file
2. **Validates** structure and required fields
3. **Resolves** variables and expressions
4. **Executes** steps sequentially (unless parallel execution specified)
5. **Collects** outputs and returns results

### Design Principles

- **Declarative**: Describe what to do, not how
- **Composable**: Build complex workflows from atomic modules
- **Portable**: YAML files run anywhere without modification
- **Version-controllable**: Git-friendly format

---

## Workflow Structure

### Top-Level Fields

```yaml
# Metadata (optional but recommended)
id: "unique-workflow-id"
name: "Human Readable Name"
version: "1.0.0"
description: "What this workflow does"
author: "Your Name"
tags: ["tag1", "tag2"]

# Input parameters
params:
  - name: keyword
    type: string
    label: "Search Keyword"
    description: "The keyword to search for"
    required: true
    default: null
    placeholder: "example text"
    min: 1
    max: 100

# Execution steps
steps:
  - id: step1
    module: core.browser.launch
    params:
      headless: true
    on_error: continue
    timeout_ms: 30000

  - id: step2
    module: core.browser.goto
    params:
      browser: "${step1.browser}"
      url: "https://example.com"

# Output definition
output:
  status: "success"
  data: "${step2.data}"
  metadata:
    timestamp: "${timestamp}"
    workflow_id: "${workflow.id}"

# Error handling (optional)
on_error:
  action: rollback
  notify: "${env.ERROR_WEBHOOK_URL}"

# Execution options (optional)
options:
  timeout_ms: 600000
  retry_count: 3
  parallel: false
```

---

## Variable Resolution

The engine supports multiple variable types with a consistent `${...}` syntax.

### Variable Types

#### 1. Step Outputs

Access output from previous steps:

```yaml
steps:
  - id: launch_browser
    module: core.browser.launch
    # Output: { browser: <browser_instance>, status: "success" }

  - id: navigate
    module: core.browser.goto
    params:
      browser: "${launch_browser.browser}"  # Access step output
```

**Pattern:** `${<step_id>.<field>}`

**Internal mapping:** `steps.<step_id>.output.<field>`

#### 2. Workflow Parameters

Access user-provided parameters:

```yaml
params:
  - name: search_query
    type: string
    required: true

steps:
  - id: search
    module: core.api.google_search
    params:
      keyword: "${params.search_query}"
```

**Pattern:** `${params.<param_name>}`

#### 3. Environment Variables

Access environment variables:

```yaml
steps:
  - id: api_call
    module: ai.openai.chat
    params:
      api_key: "${env.OPENAI_API_KEY}"
      prompt: "Analyze this data"
```

**Pattern:** `${env.VAR_NAME}`

**Security:** Sensitive values should always use environment variables, never hardcoded.

#### 4. Built-in Variables

The engine provides several built-in variables:

```yaml
output:
  timestamp: "${timestamp}"           # ISO 8601 timestamp
  workflow_id: "${workflow.id}"       # Current workflow ID
  workflow_name: "${workflow.name}"   # Current workflow name
  execution_id: "${execution.id}"     # Unique execution ID
  user: "${user.id}"                  # User ID (if authenticated)
```

#### 5. Complex Expressions

Access nested fields and array elements:

```yaml
steps:
  - id: extract_data
    module: core.browser.extract
    # Output: { data: [{ title: "Title 1", url: "..." }, { title: "Title 2", url: "..." }] }

  - id: process_first
    module: core.data.transform
    params:
      input: "${extract_data.data[0].title}"  # Array access

  - id: process_all
    module: core.flow.loop
    params:
      items: "${extract_data.data}"           # Full array
      item_var: "item"
      steps:
        - module: core.data.log
          params:
            message: "${item.title}"          # Loop variable
```

### Variable Resolution Order

1. **Built-in variables** (timestamp, workflow.id, etc.)
2. **Environment variables** (env.*)
3. **Workflow parameters** (params.*)
4. **Step outputs** (step_id.field)
5. **Loop variables** (item, index) - only within loop context

### Escaping

To use literal `${...}` text without variable resolution:

```yaml
params:
  message: "$${this is not a variable}"  # Outputs: ${this is not a variable}
```

---

## Step Definition

Each step executes a single module with specified parameters.

### Step Fields

```yaml
steps:
  - id: unique_step_id           # Required: unique identifier
    module: core.browser.launch  # Required: module to execute

    description: "Launch browser"  # Optional: human-readable description

    params:                      # Optional: module-specific parameters
      headless: true
      viewport:
        width: 1920
        height: 1080

    when: "${params.enabled}"    # Optional: conditional execution

    timeout_ms: 30000            # Optional: step timeout (default: 120000)

    retry:                       # Optional: retry configuration
      count: 3
      delay_ms: 1000
      backoff: exponential

    on_error: continue           # Optional: error handling (continue, fail, rollback)

    always: false                # Optional: run even if previous steps failed
```

### Step Execution Order

By default, steps execute **sequentially** in the order defined:

```yaml
steps:
  - id: step1
    module: module.a
  - id: step2
    module: module.b    # Waits for step1 to complete
  - id: step3
    module: module.c    # Waits for step2 to complete
```

### Parallel Execution

Mark steps for parallel execution:

```yaml
steps:
  - id: task1
    module: core.api.fetch
    params:
      url: "https://api1.example.com"
    parallel: true

  - id: task2
    module: core.api.fetch
    params:
      url: "https://api2.example.com"
    parallel: true

  - id: task3
    module: core.api.fetch
    params:
      url: "https://api3.example.com"
    parallel: true

  - id: combine
    module: core.data.merge
    params:
      data:
        - "${task1.data}"
        - "${task2.data}"
        - "${task3.data}"
    # This step waits for all parallel steps above to complete
```

**Rules:**
- Steps marked `parallel: true` execute concurrently
- The first non-parallel step waits for all preceding parallel steps
- Parallel steps cannot reference each other's outputs

---

## Flow Control

### Conditional Execution

Execute steps based on conditions:

```yaml
steps:
  - id: check_login
    module: core.browser.element_exists
    params:
      browser: "${launch_browser.browser}"
      selector: "#login-button"

  - id: perform_login
    module: core.browser.click
    params:
      browser: "${launch_browser.browser}"
      selector: "#login-button"
    when: "${check_login.exists == true}"  # Only run if condition is true
```

**Supported operators:**
- `==` Equal
- `!=` Not equal
- `>` Greater than
- `<` Less than
- `>=` Greater than or equal
- `<=` Less than or equal
- `contains` String/array contains
- `!contains` String/array does not contain

### Loops

Iterate over arrays:

```yaml
steps:
  - id: extract_links
    module: core.browser.extract
    params:
      browser: "${launch_browser.browser}"
      selector: "a.product"
      # Returns: { data: [{ url: "..." }, { url: "..." }] }

  - id: visit_each
    module: core.flow.loop
    params:
      items: "${extract_links.data}"
      item_var: "product"           # Variable name for current item
      index_var: "idx"              # Variable name for current index
      output_mode: collect          # collect, last, none

      steps:
        - id: visit_product
          module: core.browser.goto
          params:
            browser: "${launch_browser.browser}"
            url: "${product.url}"

        - id: extract_price
          module: core.browser.extract
          params:
            browser: "${launch_browser.browser}"
            selector: ".price"
```

**Output modes:**
- `collect`: Collect all step results into an array
- `last`: Only return the last iteration's result
- `none`: Don't collect results

### Conditional Branches

If/else logic:

```yaml
steps:
  - id: check_status
    module: core.api.http_get
    params:
      url: "https://api.example.com/status"

  - id: handle_success
    module: core.data.log
    params:
      message: "Service is up"
    when: "${check_status.status_code == 200}"

  - id: handle_failure
    module: core.data.log
    params:
      message: "Service is down"
    when: "${check_status.status_code != 200}"
```

### Early Exit

Stop workflow execution based on condition:

```yaml
steps:
  - id: check_required_element
    module: core.browser.element_exists
    params:
      browser: "${launch_browser.browser}"
      selector: "#critical-element"

  - id: exit_if_missing
    module: core.flow.exit
    params:
      status: "failed"
      message: "Critical element not found"
    when: "${check_required_element.exists == false}"

  - id: continue_workflow
    module: core.browser.click
    params:
      browser: "${launch_browser.browser}"
      selector: "#critical-element"
```

---

## Error Handling

### Step-Level Error Handling

```yaml
steps:
  - id: risky_operation
    module: core.api.http_get
    params:
      url: "https://unreliable-api.example.com"

    on_error: continue        # continue, fail, rollback, retry

    retry:
      count: 3               # Retry up to 3 times
      delay_ms: 1000         # Wait 1 second between retries
      backoff: exponential   # exponential or linear
      on_retry:
        - module: core.data.log
          params:
            message: "Retrying after failure..."
```

**Error handling options:**
- `continue`: Log error and continue to next step
- `fail`: Stop workflow execution immediately
- `rollback`: Execute rollback steps (if defined)
- `retry`: Retry the step according to retry configuration

### Workflow-Level Error Handling

```yaml
on_error:
  action: rollback

  rollback_steps:
    - id: cleanup_browser
      module: core.browser.close
      params:
        browser: "${launch_browser.browser}"

    - id: notify_failure
      module: api.http.post
      params:
        url: "${env.ERROR_WEBHOOK_URL}"
        body:
          message: "Workflow failed"
          error: "${error.message}"
          step: "${error.step_id}"

  notify:
    webhook: "${env.ERROR_WEBHOOK_URL}"
    email: "${env.ADMIN_EMAIL}"
```

### Always Execute Steps

Steps that run regardless of previous failures:

```yaml
steps:
  - id: launch_browser
    module: core.browser.launch

  - id: risky_step
    module: core.browser.goto
    params:
      url: "https://might-fail.com"

  - id: cleanup
    module: core.browser.close
    params:
      browser: "${launch_browser.browser}"
    always: true              # Runs even if risky_step fails
```

### Error Context Variables

Access error information in error handlers:

```yaml
on_error:
  rollback_steps:
    - id: log_error
      module: core.data.log
      params:
        message: |
          Error occurred:
          Step: ${error.step_id}
          Module: ${error.module_id}
          Message: ${error.message}
          Stack: ${error.stack}
          Timestamp: ${error.timestamp}
```

---

## Output Mapping

Define workflow output using variable references:

### Simple Output

```yaml
steps:
  - id: extract_data
    module: core.browser.extract
    # Returns: { data: [...], count: 10 }

output:
  results: "${extract_data.data}"
  total: "${extract_data.count}"
```

### Computed Output

```yaml
output:
  status: "success"
  timestamp: "${timestamp}"
  results:
    raw_data: "${extract_data.data}"
    filtered_data: "${filtered.results}"
    summary:
      total_items: "${extract_data.count}"
      processed_items: "${filtered.count}"
      workflow_name: "${workflow.name}"
```

### Conditional Output

```yaml
output:
  status: "${steps.final_check.success ? 'completed' : 'partial'}"
  data:
    when: "${steps.extract_data.count > 0}"
    value: "${extract_data.data}"
  message:
    when: "${steps.extract_data.count == 0}"
    value: "No data found"
```

---

## Complete Examples

### Example 1: Minimal Workflow

```yaml
name: "Simple Page Title Extractor"
description: "Extract title from any webpage"

params:
  - name: url
    type: string
    required: true

steps:
  - id: launch_browser
    module: core.browser.launch

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
  url: "${params.url}"
  title: "${extract_title.data[0].text}"
```

### Example 2: Error Handling & Retry

```yaml
name: "Resilient API Call"
description: "Call API with retry and fallback"

params:
  - name: api_url
    type: string
    required: true

steps:
  - id: primary_api
    module: core.api.http_get
    params:
      url: "${params.api_url}"
    retry:
      count: 3
      delay_ms: 2000
      backoff: exponential
    on_error: continue

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
  source: "${primary_api.status == 'success' ? 'primary' : 'fallback'}"
  data: "${process_data.result}"
```

### Example 3: Conditional Flow

```yaml
name: "Conditional Login Flow"
description: "Login only if not already logged in"

steps:
  - id: launch_browser
    module: core.browser.launch

  - id: goto_homepage
    module: core.browser.goto
    params:
      browser: "${launch_browser.browser}"
      url: "https://app.example.com"

  - id: check_logged_in
    module: core.browser.element_exists
    params:
      browser: "${launch_browser.browser}"
      selector: ".user-profile"

  - id: goto_login
    module: core.browser.goto
    params:
      browser: "${launch_browser.browser}"
      url: "https://app.example.com/login"
    when: "${check_logged_in.exists == false}"

  - id: perform_login
    module: core.browser.type
    params:
      browser: "${launch_browser.browser}"
      selector: "#email"
      text: "${env.USER_EMAIL}"
    when: "${check_logged_in.exists == false}"

  - id: submit_login
    module: core.browser.click
    params:
      browser: "${launch_browser.browser}"
      selector: "#login-button"
    when: "${check_logged_in.exists == false}"

  - id: proceed_to_dashboard
    module: core.browser.goto
    params:
      browser: "${launch_browser.browser}"
      url: "https://app.example.com/dashboard"

output:
  logged_in: true
  already_logged_in: "${check_logged_in.exists}"
```

### Example 4: Loop with Collection

```yaml
name: "Multi-Page Scraper"
description: "Scrape data from multiple pages"

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
      index_var: "page_index"
      output_mode: collect

      steps:
        - id: navigate_to_page
          module: core.browser.goto
          params:
            browser: "${launch_browser.browser}"
            url: "${page_url}"

        - id: extract_content
          module: core.browser.extract
          params:
            browser: "${launch_browser.browser}"
            selector: ".content"
            fields:
              title: { selector: "h1", type: "text" }
              body: { selector: ".article-body", type: "text" }

  - id: cleanup
    module: core.browser.close
    params:
      browser: "${launch_browser.browser}"
    always: true

output:
  pages_scraped: "${scrape_pages.count}"
  data: "${scrape_pages.results}"
```

### Example 5: Parallel Execution

```yaml
name: "Parallel API Fetcher"
description: "Fetch from multiple APIs simultaneously"

steps:
  - id: fetch_weather
    module: core.api.http_get
    params:
      url: "https://api.weather.com/current"
    parallel: true

  - id: fetch_news
    module: core.api.http_get
    params:
      url: "https://api.news.com/headlines"
    parallel: true

  - id: fetch_stocks
    module: core.api.http_get
    params:
      url: "https://api.stocks.com/prices"
    parallel: true

  - id: combine_data
    module: core.data.merge
    params:
      sources:
        weather: "${fetch_weather.data}"
        news: "${fetch_news.data}"
        stocks: "${fetch_stocks.data}"

  - id: ai_summarize
    module: ai.openai.chat
    params:
      api_key: "${env.OPENAI_API_KEY}"
      prompt: |
        Summarize this data:
        Weather: ${fetch_weather.data}
        News: ${fetch_news.data}
        Stocks: ${fetch_stocks.data}

output:
  raw_data: "${combine_data.result}"
  summary: "${ai_summarize.message}"
  fetch_time_ms: "${execution.duration_ms}"
```

---

## Type System

### Parameter Types

```yaml
params:
  - name: string_param
    type: string
    min: 1              # Min length
    max: 100            # Max length
    pattern: "^[a-z]+$" # Regex pattern

  - name: number_param
    type: number
    min: 0              # Min value
    max: 100            # Max value

  - name: boolean_param
    type: boolean
    default: false

  - name: array_param
    type: array
    items:
      type: string
    min: 1              # Min array length
    max: 10             # Max array length

  - name: object_param
    type: object
    properties:
      field1:
        type: string
        required: true
      field2:
        type: number
        required: false

  - name: enum_param
    type: string
    enum: ["option1", "option2", "option3"]
```

---

## Best Practices

### 1. Always Use Descriptive IDs

```yaml
# Good
- id: launch_browser
- id: extract_product_prices
- id: notify_slack

# Bad
- id: step1
- id: step2
- id: step3
```

### 2. Use Environment Variables for Secrets

```yaml
# Good
params:
  api_key: "${env.OPENAI_API_KEY}"

# Bad
params:
  api_key: "sk-1234567890abcdef"  # Never hardcode secrets!
```

### 3. Add Descriptions for Complex Workflows

```yaml
steps:
  - id: complex_transformation
    description: "Transform raw data by filtering nulls, normalizing dates, and deduplicating"
    module: core.data.transform
    params:
      # ...
```

### 4. Handle Errors Explicitly

```yaml
steps:
  - id: api_call
    module: core.api.http_get
    params:
      url: "https://api.example.com"
    retry:
      count: 3
      delay_ms: 1000
    on_error: continue  # Explicit error handling
```

### 5. Use Cleanup Steps with `always: true`

```yaml
steps:
  - id: launch_browser
    module: core.browser.launch

  # ... other steps

  - id: cleanup_browser
    module: core.browser.close
    params:
      browser: "${launch_browser.browser}"
    always: true  # Always close browser, even on error
```

---

## Schema Validation

The engine validates workflows against this schema before execution. Invalid workflows will fail with detailed error messages.

### Common Validation Errors

**Missing required field:**
```
Error: Step "navigate" is missing required parameter "url"
```

**Invalid variable reference:**
```
Error: Variable "${nonexistent_step.data}" references undefined step "nonexistent_step"
```

**Type mismatch:**
```
Error: Parameter "headless" expects boolean, got string "true"
```

**Circular dependency:**
```
Error: Step "step2" creates circular dependency: step1 -> step2 -> step1
```

---

## Future Additions (Planned)

These features are planned for future versions:

- **Subroutines**: Reusable step sequences
- **Events & Triggers**: Webhook/scheduled triggers
- **Secrets Management**: First-class secret handling with vault integration
- **Dynamic Imports**: Import workflows from URLs
- **Template Syntax**: Jinja2-style templates in YAML values

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

**Last Updated:** 2025-01-29
**Version:** 1.0.0-alpha
