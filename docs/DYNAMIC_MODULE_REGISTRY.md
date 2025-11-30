# Dynamic Module Registry

## Overview

The module registry is automatically maintained and always reflects your current modules. No manual documentation updates required.

## How It Works

### 1. Automatic Registration

When you create a module with the `@register_module` decorator, it automatically registers in the global registry:

```python
@register_module(
    module_id='my.new.module',
    version='1.0.0',
    description='Does something useful',
    params_schema={...},
    output_schema={...}
)
class MyNewModule(BaseModule):
    pass
```

The registry immediately knows about this module.

### 2. Live Query System

The `meta.modules.list` module queries the live registry:

```yaml
steps:
  - id: get_current_modules
    module: meta.modules.list
    params:
      format: "markdown"
      include_params: true
```

This always returns your **current** modules, not stale documentation.

### 3. AI Always Has Current Info

Meta-workflows use `meta.modules.list` instead of reading static files:

```yaml
# OLD WAY (static, gets stale)
- id: read_modules
  module: data.file.read
  params:
    file_path: "docs/MODULES.md"

# NEW WAY (dynamic, always current)
- id: get_modules
  module: meta.modules.list
  params:
    format: "markdown"
```

AI workflows now always know what modules exist.

## Using the Module Registry

### List All Modules

```bash
python -m src.cli.main workflows/meta/list_modules_example.yaml
```

This workflow demonstrates all the ways to query modules.

### Query by Category

```yaml
- id: list_browser_modules
  module: meta.modules.list
  params:
    category: "browser"
    format: "markdown"
```

### Query by Tags

```yaml
- id: list_ai_modules
  module: meta.modules.list
  params:
    tags: ["ai", "llm"]
    format: "compact"
```

### Format Options

**JSON (structured):**
```yaml
params:
  format: "json"
  include_params: true
  include_output: true
```

Returns detailed JSON with full schemas.

**Markdown (human-readable):**
```yaml
params:
  format: "markdown"
  include_params: true
```

Returns formatted documentation.

**Compact (AI-friendly):**
```yaml
params:
  format: "compact"
  include_params: true
```

Returns concise list optimized for AI prompts.

## Auto-Generate Documentation

Update MODULES.md from live registry:

```bash
python -m src.cli.main workflows/meta/update_module_docs.yaml
```

This workflow:
1. Backups existing MODULES.md
2. Queries live registry
3. Generates new documentation
4. Saves to docs/MODULES.md

Run this whenever you add/remove modules.

### Schedule Auto-Update

Add to your development workflow:

```bash
# Git pre-commit hook
#!/bin/bash
# Check if any module files changed
if git diff --cached --name-only | grep -q 'src/core/modules/'; then
    echo "Modules changed, updating documentation..."
    python -m src.cli.main workflows/meta/update_module_docs.yaml
    git add docs/MODULES.md
fi
```

Or schedule periodic updates:

```bash
# Update every day at 2am
0 2 * * * cd /path/to/flyto2 && python -m src.cli.main workflows/meta/update_module_docs.yaml
```

## Benefits

### 1. Always Accurate

AI never uses outdated module information because it queries the live registry.

### 2. Zero Maintenance

Add a module, it's immediately available. Remove a module, it's immediately gone. No manual doc updates.

### 3. Prevents Hallucinations

AI can't invent modules because it sees exactly what exists:

```yaml
- id: get_available_modules
  module: meta.modules.list
  params:
    format: "compact"

- id: ask_ai
  module: ai.openai.chat
  params:
    system: "Only use modules from this list. Do not invent modules."
    messages:
      - role: user
        content: |
          Available modules:
          ${get_available_modules.formatted}

          Generate workflow for: ${params.task}
```

AI sees the actual list, can't make up fake modules.

### 4. Fast Filtering

Get only relevant modules for AI context:

```yaml
# For browser automation task
- id: get_browser_modules
  module: meta.modules.list
  params:
    category: "browser"
    format: "compact"

# For AI task
- id: get_ai_modules
  module: meta.modules.list
  params:
    tags: ["ai", "llm"]
    format: "compact"
```

Reduces token usage by only including relevant modules.

## Integration with Meta-Workflows

All meta-workflows now use live module registry:

### generate_workflow.yaml

```yaml
steps:
  - id: get_modules
    module: meta.modules.list
    params:
      format: "markdown"

  - id: generate
    module: ai.openai.chat
    params:
      prompt: |
        Available modules:
        ${get_modules.formatted}

        Generate workflow for: ${params.description}
```

### refactor_workflow.yaml

```yaml
steps:
  - id: get_modules
    module: meta.modules.list
    params:
      format: "markdown"

  - id: refactor
    module: ai.openai.chat
    params:
      prompt: |
        Available modules:
        ${get_modules.formatted}

        Refactor this workflow: ${target_workflow}
```

### analyze_workflow.yaml

```yaml
steps:
  - id: get_modules
    module: meta.modules.list
    params:
      format: "compact"

  - id: analyze
    module: ai.openai.chat
    params:
      prompt: |
        Available modules:
        ${get_modules.formatted}

        Analyze: ${target_workflow}
```

## Performance Considerations

### Caching

Module registry is loaded once at startup. Querying is fast.

### Token Optimization

Use format options to control output size:

**Compact format** - Minimal, for AI context:
```
- browser.launch: Launch browser
  params: headless, timeout
- browser.goto: Navigate to URL
  params: url, browser
```

**Full format** - Complete, for documentation:
```markdown
### browser.launch
Launch a new browser instance
**Parameters:**
- headless (boolean, optional): Run in headless mode
- timeout (number, optional): Launch timeout in seconds
**Output:**
- browser (object): Browser instance
```

Choose based on needs.

## Troubleshooting

### Module Not Showing Up

If a module doesn't appear:

1. Check decorator is applied: `@register_module(...)`
2. Check module is imported in `__init__.py`
3. Restart if running in dev mode
4. Run list_modules to verify:

```bash
python -m src.cli.main workflows/meta/list_modules_example.yaml
```

### Documentation Out of Sync

Run the update workflow:

```bash
python -m src.cli.main workflows/meta/update_module_docs.yaml
```

This regenerates docs/MODULES.md from live registry.

### AI Using Wrong Modules

Make sure meta-workflows use `meta.modules.list`:

```yaml
# Correct
- module: meta.modules.list

# Wrong (static, outdated)
- module: data.file.read
  params:
    file_path: "docs/MODULES.md"
```

## Example: Complete Workflow

```yaml
name: "Generate Workflow with Current Modules"

steps:
  # Get current modules
  - id: modules
    module: meta.modules.list
    params:
      format: "compact"
      include_params: true

  # Generate workflow
  - id: generate
    module: ai.openai.chat
    params:
      model: "gpt-4"
      system: |
        You are a workflow engineer.
        Only use modules from the provided list.
        Module names must match exactly.
      messages:
        - role: user
          content: |
            Available modules (${modules.count} total):
            ${modules.formatted}

            Task: ${params.description}

            Generate a workflow using only these modules.

  # Save result
  - id: save
    module: data.file.write
    params:
      file_path: "workflows/_generated/${timestamp}_workflow.yaml"
      content: "${generate.response}"
```

Run:
```bash
python -m src.cli.main workflow.yaml \
  --param description="Scrape news and send to Slack"
```

Result: AI uses your **current** modules, not outdated list.

## Summary

**Before (static):**
- Manually maintain MODULES.md
- Gets out of sync quickly
- AI uses outdated information
- Manual updates required

**After (dynamic):**
- Registry queries live modules
- Always current
- AI has accurate information
- Zero maintenance

**Key modules:**
- `meta.modules.list` - Query registry
- `meta.modules.update_docs` - Generate docs

**Key workflows:**
- `workflows/meta/update_module_docs.yaml` - Update MODULES.md
- `workflows/meta/list_modules_example.yaml` - Query examples

The system maintains itself. You just add modules, everything else is automatic.
