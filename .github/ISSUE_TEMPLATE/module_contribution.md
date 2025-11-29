---
name: Module Contribution
about: Propose or contribute a new module
title: '[MODULE] '
labels: module, enhancement
assignees: ''
---

## Module Proposal

**Module ID**: `namespace.category.action` (e.g., `api.slack.send_message`)

**Category**: [Browser / API / AI / Database / Cloud / Notification / Flow / Data]

**Description**: Brief description of what this module does

## Use Case

What problem does this module solve? When would someone use it?

## Module Specification

### Parameters

```yaml
params_schema:
  param_name:
    type: string  # string | number | boolean | object | array
    label: "Parameter Label"
    description: "What this parameter does"
    required: true
    default: null
```

### Output

```yaml
output_schema:
  result:
    type: object
    description: "What this module returns"
```

### Example Usage

```yaml
steps:
  - id: example
    module: your.module.id
    params:
      param1: value1
      param2: value2

output:
  result: "${example.result}"
```

## Dependencies

Does this module require additional Python packages?

```bash
pip install package-name
```

## Implementation Status

- [ ] I have a working implementation ready to submit
- [ ] I need help implementing this module
- [ ] This is just a proposal, looking for feedback

## Checklist

- [ ] Follows atomic design (single responsibility)
- [ ] Includes comprehensive parameter validation
- [ ] Has clear input/output schema
- [ ] Includes usage examples
- [ ] Follows naming convention (`namespace.category.action`)
- [ ] Will include tests (>80% coverage)
- [ ] Will include i18n support

## Additional Context

Add any other context, code samples, or examples about the module here.

---

**Next Steps:**
1. Get feedback on this proposal
2. Implement the module following [docs/WRITING_MODULES.md](../../docs/WRITING_MODULES.md)
3. Submit a Pull Request
