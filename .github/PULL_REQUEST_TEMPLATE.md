# Pull Request

## Description

Brief description of what this PR does.

Fixes # (issue number, if applicable)

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Module contribution
- [ ] Workflow example

## Changes Made

- List the key changes
- Be specific about what was added/modified/removed

## Testing

### How Has This Been Tested?

- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing
- [ ] Tested with example workflows

### Test Configuration

- **Python Version**: [e.g., 3.10]
- **OS**: [e.g., macOS, Ubuntu]
- **Playwright Version**: [e.g., 1.40.0]

### Test Evidence

```bash
# Paste test output here
$ pytest
...
```

## Module Checklist (if contributing a module)

- [ ] Follows naming convention (`namespace.category.action`)
- [ ] Includes `@register_module` decorator with metadata
- [ ] Has `validate_params()` method
- [ ] Has `async execute()` method returning dict
- [ ] Includes comprehensive error handling
- [ ] Added to `NAMESPACES.yaml`
- [ ] Includes i18n keys and translations
- [ ] Has usage examples in docstring
- [ ] Unit tests added (>80% coverage)
- [ ] Tests pass locally (`pytest`)

## Documentation Checklist

- [ ] Updated README (if needed)
- [ ] Updated relevant docs (if needed)
- [ ] Added/updated code comments
- [ ] Added usage examples (for new features)

## Code Quality

- [ ] Code follows the project's style guidelines
- [ ] Self-review completed
- [ ] No console.log or debug prints left
- [ ] No hardcoded secrets or credentials
- [ ] Type hints added for Python code

## Breaking Changes

Does this PR introduce breaking changes?

- [ ] No breaking changes
- [ ] Yes, breaking changes (describe below)

**If yes, describe the breaking changes:**

## Additional Notes

Any additional information, context, or screenshots.

## Checklist

- [ ] I have read [CONTRIBUTING.md](../CONTRIBUTING.md)
- [ ] My code follows the project's code style
- [ ] I have performed a self-review
- [ ] I have commented my code where needed
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing tests pass locally
- [ ] No merge conflicts
