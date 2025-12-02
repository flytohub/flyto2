# Flyto2 Project Knowledge Base (English Only)

**Version**: V4.0
**Date**: 2025-12-02
**Status**: Production Ready

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Creating YAML Workflows](#creating-yaml-workflows)
4. [Adding Atomic Modules](#adding-atomic-modules)
5. [Module Catalog](#module-catalog)
6. [Common Patterns](#common-patterns)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

---

## 1. Project Overview

### What is Flyto2?

Flyto2 is an autonomous self-evolving AI bot system that can:
- Execute tasks via YAML workflows
- Learn from errors automatically
- Generate new features and bug fixes
- Create pull requests for human review
- Update its own knowledge base

### Core Components

1. **Workflow Engine**: Executes YAML-based workflows
2. **Atomic Modules**: 120+ reusable building blocks
3. **Error Center**: Collects and analyzes errors
4. **Debug Engine**: Diagnoses problems automatically
5. **Evolution Pipeline**: Generates fixes and features
6. **Vector Database (Qdrant)**: Stores knowledge
7. **Telegram Bot**: User interface

---

## 2. Architecture

### System Layers

```
┌─────────────────────────────────────────────┐
│     Control Layer (Telegram Bot + CLI)     │
│  Commands: /start /test /evolve /debug     │
└─────────────────────────────────────────────┘
                    │
┌───────────────────┼─────────────────────────┐
│              Evolution Layer                │
│  ErrorCenter → DebugEngine → Orchestrator  │
│  Planner → Designer → Implementation        │
└───────────────────┼─────────────────────────┘
                    │
┌───────────────────┼─────────────────────────┐
│                AI Layer                     │
│  LLM: Ollama → GPT → Claude                │
│  RAG Retriever (Qdrant Vector DB)          │
└───────────────────┼─────────────────────────┘
                    │
┌───────────────────┼─────────────────────────┐
│             Memory Layer                    │
│  VectorDB + Module Catalog + Metrics       │
└───────────────────┼─────────────────────────┘
                    │
┌───────────────────┼─────────────────────────┐
│            Execution Layer                  │
│  Workflow Engine + Atomic Modules           │
└─────────────────────────────────────────────┘
```

### Data Flow

```
[User Request via Telegram]
    ↓
[Generate YAML Workflow]
    ↓
[Execute Workflow]
    ↓
[Error Occurs] → [ErrorCenter]
    ↓
[DebugEngine Analysis]
    ↓
[Evolution Ticket Created]
    ↓
[Generate Fix (YAML + Code)]
    ↓
[Create Pull Request]
    ↓
[Human Review & Merge]
    ↓
[Update Vector Database]
```

---

## 3. Creating YAML Workflows

### Basic Structure

```yaml
id: workflow_name
name: Descriptive Workflow Name
version: "1.0.0"

params:
  - name: url
    type: string
    required: true
    description: Target URL

steps:
  - id: step1
    module: browser.launch
    params:
      headless: true
      browser_type: chromium

  - id: step2
    module: browser.goto
    params:
      url: ${params.url}

  - id: step3
    module: browser.extract
    params:
      selector: "body"
      fields:
        title:
          selector: "h1"
          type: "text"
        content:
          selector: "p"
          type: "text"

output:
  status: success
  data: ${step3.result}
```

### Variable Resolution

Use `${variable_name}` to reference:
- **Parameters**: `${params.url}`
- **Step Results**: `${step1.result}`
- **Context**: `${context.browser_instance}`
- **Workflow Metadata**: `${workflow.id}`

### Conditional Execution

```yaml
steps:
  - id: check_status
    module: api.http_get
    params:
      url: https://example.com/api/status

  - id: handle_error
    module: notification.send
    when: ${check_status.result.status == 'error'}
    params:
      message: "API is down!"
```

### Retry Logic

```yaml
steps:
  - id: fetch_data
    module: api.http_get
    params:
      url: https://api.example.com/data
    retry:
      count: 3
      delay_ms: 1000
      backoff: exponential
```

### Parallel Execution

```yaml
steps:
  - id: task1
    module: api.http_get
    parallel: true
    params:
      url: https://api1.example.com

  - id: task2
    module: api.http_get
    parallel: true
    params:
      url: https://api2.example.com

  - id: combine
    module: data.merge
    params:
      sources:
        - ${task1.result}
        - ${task2.result}
```

---

## 4. Adding Atomic Modules

### Module Structure

All atomic modules are located in: `src/core/modules/atomic/`

### Basic Module Template

```python
"""
Module: category.action_name
Description: What this module does
"""
from src.core.modules.base import BaseModule
from src.core.modules.registry import register_module
from typing import Any, Dict


@register_module('category.action_name')
class ActionNameModule(BaseModule):
    """
    Module documentation

    Params:
        param1 (str): Description of param1
        param2 (int): Description of param2

    Returns:
        dict: {
            'status': 'success',
            'data': result_data
        }
    """

    module_name = "Action Name"
    module_description = "Brief description"

    def validate_params(self):
        """Validate and extract parameters"""
        # Required parameters
        if 'param1' not in self.params:
            raise ValueError("Missing required parameter: param1")

        self.param1 = self.params['param1']

        # Optional parameters with defaults
        self.param2 = self.params.get('param2', 10)

    async def execute(self) -> Dict[str, Any]:
        """Execute module logic"""
        try:
            # Your implementation here
            result = await self._do_something(self.param1, self.param2)

            return {
                'status': 'success',
                'data': result
            }

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    async def _do_something(self, param1: str, param2: int):
        """Helper method"""
        # Implementation
        return {"result": f"Processed {param1} with {param2}"}
```

### Module Categories

1. **browser.*** - Browser automation (Playwright)
2. **api.*** - HTTP/API operations
3. **data.*** - Data transformation
4. **file.*** - File operations
5. **string.*** - String manipulation
6. **array.*** - Array operations
7. **object.*** - Object manipulation
8. **datetime.*** - Date/time operations
9. **loop.*** - Iteration
10. **condition.*** - Conditional logic

### Registration

Modules are automatically registered when decorated with `@register_module('module_id')`.

The registry maintains metadata for:
- Module discovery
- UI builders
- Documentation generation
- Validation

---

## 5. Module Catalog

### Browser Modules

#### browser.launch
Launch a browser instance.

```yaml
- id: launch
  module: browser.launch
  params:
    headless: true
    browser_type: chromium  # chromium, firefox, webkit
```

#### browser.goto
Navigate to a URL.

```yaml
- id: navigate
  module: browser.goto
  params:
    url: https://example.com
    wait_until: networkidle  # load, domcontentloaded, networkidle
```

#### browser.click
Click an element.

```yaml
- id: click_button
  module: browser.click
  params:
    selector: "button#submit"
    wait_for_selector: true
    timeout: 5000
```

#### browser.type
Type text into an input field.

```yaml
- id: fill_form
  module: browser.type
  params:
    selector: "input[name='email']"
    text: "user@example.com"
    clear_first: true
```

#### browser.extract
Extract data from the page.

```yaml
- id: scrape
  module: browser.extract
  params:
    selector: "div.product"
    limit: 10
    fields:
      name:
        selector: "h2.title"
        type: text
      price:
        selector: "span.price"
        type: text
      link:
        selector: "a"
        type: attribute
        attribute: href
```

#### browser.screenshot
Take a screenshot.

```yaml
- id: capture
  module: browser.screenshot
  params:
    path: screenshots/page.png
    full_page: true
```

#### browser.wait
Wait for conditions.

```yaml
- id: wait_for_load
  module: browser.wait
  params:
    type: selector  # selector, timeout, networkidle
    selector: "div.loaded"
    timeout: 10000
```

### API Modules

#### api.http_get
HTTP GET request.

```yaml
- id: fetch
  module: api.http_get
  params:
    url: https://api.example.com/data
    headers:
      Authorization: Bearer ${params.token}
```

#### api.http_post
HTTP POST request.

```yaml
- id: create
  module: api.http_post
  params:
    url: https://api.example.com/items
    json:
      name: New Item
      value: 123
```

### Data Modules

#### data.transform
Transform data structure.

```yaml
- id: reshape
  module: data.transform
  params:
    data: ${step1.result}
    mapping:
      output_field: input_field
      new_name: old_name
```

#### data.filter
Filter data by conditions.

```yaml
- id: filter_results
  module: data.filter
  params:
    data: ${step1.result}
    condition:
      field: price
      operator: ">"
      value: 100
```

#### data.merge
Merge multiple data sources.

```yaml
- id: combine
  module: data.merge
  params:
    sources:
      - ${step1.result}
      - ${step2.result}
    strategy: deep  # shallow, deep
```

### String Modules

#### string.uppercase
Convert to uppercase.

```yaml
- id: upper
  module: string.uppercase
  params:
    text: ${params.input}
```

#### string.replace
Find and replace text.

```yaml
- id: clean
  module: string.replace
  params:
    text: ${params.input}
    pattern: "old"
    replacement: "new"
    regex: false
```

### Array Modules

#### array.map
Transform array elements.

```yaml
- id: transform_items
  module: array.map
  params:
    array: ${step1.result}
    transform:
      field: name
      operation: uppercase
```

#### array.filter
Filter array elements.

```yaml
- id: filter_items
  module: array.filter
  params:
    array: ${step1.result}
    condition:
      field: active
      value: true
```

### Loop Modules

#### loop.foreach
Iterate over array.

```yaml
- id: process_items
  module: loop.foreach
  params:
    array: ${step1.result}
    steps:
      - id: process
        module: data.transform
        params:
          data: ${item}
```

---

## 6. Common Patterns

### Pattern 1: Web Scraping

```yaml
id: scrape_website
name: Scrape Website Content

params:
  - name: url
    type: string
    required: true

steps:
  - id: launch
    module: browser.launch
    params:
      headless: true

  - id: goto
    module: browser.goto
    params:
      url: ${params.url}

  - id: extract
    module: browser.extract
    params:
      selector: "body"
      fields:
        title:
          selector: "h1"
          type: text
        links:
          selector: "a"
          type: attribute
          attribute: href

output:
  data: ${extract.result}
```

### Pattern 2: API Integration

```yaml
id: api_workflow
name: API Data Processing

steps:
  - id: fetch
    module: api.http_get
    params:
      url: https://api.example.com/data
    retry:
      count: 3
      delay_ms: 1000

  - id: filter
    module: data.filter
    params:
      data: ${fetch.result}
      condition:
        field: status
        operator: "=="
        value: "active"

  - id: transform
    module: data.transform
    params:
      data: ${filter.result}
```

### Pattern 3: Error Handling

```yaml
steps:
  - id: risky_operation
    module: api.http_get
    params:
      url: https://unstable-api.com
    on_error: continue

  - id: check_status
    module: condition.if
    when: ${risky_operation.status == 'error'}
    params:
      then:
        - module: notification.send
          params:
            message: "Operation failed"
```

---

## 7. Testing

### Running Tests

```bash
# Test workflow engine
python3 test_end_to_end.py

# Test specific module
python3 -m pytest tests/test_browser.py

# Run all tests
python3 -m pytest
```

### Test Workflow

```yaml
id: test_workflow
name: Test Basic Functionality

steps:
  - id: test_string
    module: string.uppercase
    params:
      text: "hello world"

  - id: assert
    module: test.assert_equals
    params:
      actual: ${test_string.result}
      expected: "HELLO WORLD"
```

---

## 8. Troubleshooting

### Common Issues

#### 1. Module Not Found
**Error**: `Module not found: browser.launch`

**Solution**:
- Check module is registered: `@register_module('browser.launch')`
- Verify import path in `registry.py`
- Ensure module file exists in correct directory

#### 2. Browser Not Launching
**Error**: `Browser executable not found`

**Solution**:
```bash
# Install Playwright browsers
playwright install chromium
```

#### 3. Variable Resolution Failed
**Error**: `Cannot resolve variable: ${step1.result}`

**Solution**:
- Verify step ID matches: `step1` not `step_1`
- Ensure step completed before reference
- Check result structure matches access pattern

#### 4. Connection Timeout
**Error**: `Connection timeout after 30s`

**Solution**:
- Increase timeout in params
- Check network connectivity
- Verify URL is correct

### Debug Commands

```bash
# Check module catalog
python3 scripts/check_module_catalog.py

# Debug workflow execution
python3 -m flyto2.src.cli.main workflow.yaml --debug

# View error logs
python3 scripts/view_errors.py

# Test Qdrant connection
python3 scripts/test_qdrant.py
```

---

## Summary

This knowledge base covers:
1. ✅ Project architecture and components
2. ✅ How to create YAML workflows
3. ✅ How to add atomic modules
4. ✅ Complete module catalog
5. ✅ Common patterns for tasks
6. ✅ Testing strategies
7. ✅ Troubleshooting guide

**Key Principles**:
- Atomic modules are single-purpose, reusable
- Workflows combine modules via YAML
- Variables flow through `${variable}` syntax
- Errors are captured and used for evolution
- Knowledge is stored in Vector DB for RAG
