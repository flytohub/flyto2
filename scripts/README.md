# Flyto2 Helper Scripts

Utility scripts for common workflow operations.

## validate.sh / validate.bat

Workflow validation helper script.

### Usage

**Linux/Mac:**
```bash
./scripts/validate.sh <workflow_path> [options]
```

**Windows:**
```cmd
scripts\validate.bat <workflow_path> [options]
```

### Options

- `--strict` - Enable strict validation mode
- `--help` - Show help message

### Examples

```bash
# Validate a workflow
./scripts/validate.sh workflows/google_search.yaml

# Strict validation
./scripts/validate.sh workflows/_generated/new_workflow.yaml --strict

# Validate all generated workflows
./scripts/validate.sh workflows/_generated/*.yaml
```

### What It Validates

- YAML syntax
- Required fields (name, steps)
- Module existence in registry
- Parameter schemas
- Variable references
- Security issues (hardcoded secrets)
- Conditional logic
- Step ID uniqueness

### Exit Codes

- `0` - Validation passed
- `1` - Validation failed
- `2` - Invalid usage

### How It Works

The script is a simple wrapper around the `validate_workflow.yaml` meta-workflow:

```bash
python -m src.cli.main workflows/meta/validate_workflow.yaml \
    --param target="$WORKFLOW_PATH" \
    --param strict="$STRICT"
```

### Integration with CI/CD

Add to your CI pipeline:

**GitHub Actions:**
```yaml
- name: Validate workflows
  run: |
    ./scripts/validate.sh workflows/*.yaml
```

**GitLab CI:**
```yaml
validate:
  script:
    - ./scripts/validate.sh workflows/*.yaml
```

**Pre-commit Hook:**
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Validate all staged YAML files
for file in $(git diff --cached --name-only | grep '\.yaml$'); do
    if [[ $file == workflows/* ]]; then
        ./scripts/validate.sh "$file" || exit 1
    fi
done
```

## Documentation

- [Meta-Workflow Guide](../docs/META_WORKFLOWS.md)
- [Safety Guide](../docs/META_WORKFLOW_SAFETY.md)
- [Validation Rules](../docs/META_WORKFLOW_SAFETY.md#validation-requirements)
