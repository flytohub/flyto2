# Meta-Workflows

AI-powered workflows that analyze, generate, and improve other workflows.

## Quick Start

### Generate New Workflow

```bash
python -m src.cli.main workflows/meta/generate_workflow.yaml \
  --param description="Daily backup of database to S3" \
  --param output_path=workflows/_generated/db_backup.yaml \
  --param model=gpt-4
```

### Analyze Existing Workflow

```bash
python -m src.cli.main workflows/meta/analyze_workflow.yaml \
  --param target_workflow=workflows/google_search.yaml \
  --param llm_provider=ollama \
  --param model=mistral
```

### Refactor for Improvement

```bash
python -m src.cli.main workflows/meta/refactor_workflow.yaml \
  --param target_workflow=workflows/api_pipeline.yaml \
  --param output_path=workflows/_refactored/api_pipeline_v2.yaml \
  --param improvements=error-handling
```

### Autonomous Improvement

```bash
python -m src.cli.main workflows/meta/autonomous_improve.yaml \
  --param target_workflow=workflows/daily_report.yaml \
  --param output_path=workflows/_improved/daily_report_v2.yaml \
  --param llm_provider=ollama \
  --param model=mistral
```

### Full Pipeline

```bash
python -m src.cli.main workflows/meta/full_improvement_pipeline.yaml \
  --param target_workflow=workflows/multi_channel_alert.yaml \
  --param model=gpt-4
```

## Available Meta-Workflows

| Workflow | Purpose | Output |
|----------|---------|--------|
| `analyze_workflow.yaml` | Analyze and suggest improvements | Analysis report |
| `generate_workflow.yaml` | Generate from description | New workflow YAML |
| `refactor_workflow.yaml` | Refactor existing workflow | Improved version |
| `validate_workflow.yaml` | Validate YAML structure | Validation report |
| `autonomous_improve.yaml` | Agent-driven improvement | Improved workflow |
| `create_github_pr.yaml` | Create PR for changes | GitHub PR |
| `full_improvement_pipeline.yaml` | Complete pipeline | All outputs |
| `continuous_learning.yaml` | Learn from execution logs | Learning report |

## Safety

Meta-workflows follow strict safety protocols:

1. Never modify production workflows directly
2. Always write to isolated directories
3. Require validation before use
4. Human review required for production
5. Complete audit trail maintained

See [Meta-Workflow Safety Guide](../../docs/META_WORKFLOW_SAFETY.md)

## Architecture

Meta-workflows use existing atomic modules:

```
data.file.read          -> Read specs and workflows
ai.openai.chat          -> Cloud LLM analysis
ai.local_ollama.chat    -> Local LLM analysis
agent.autonomous        -> Self-directed improvement
agent.chain             -> Multi-step processing
data.file.write         -> Save results
api.github.*            -> Create PRs
```

Low coupling, high cohesion, atomic composition.

## Quick Validation

Use the validation helper script:

```bash
# Linux/Mac
./scripts/validate.sh workflows/_generated/my_workflow.yaml

# Windows
scripts\validate.bat workflows\_generated\my_workflow.yaml

# Strict mode
./scripts/validate.sh workflows/_generated/my_workflow.yaml --strict
```

Or use the meta-workflow directly:

```bash
python -m src.cli.main workflows/meta/validate_workflow.yaml \
  --param target=workflows/_generated/my_workflow.yaml
```

## Documentation

- [Meta-Workflow Guide](../../docs/META_WORKFLOWS.md)
- [Safety Guide](../../docs/META_WORKFLOW_SAFETY.md)
- [Case Study](../../docs/CASE_STUDY_META_WORKFLOW.md)
- [DSL Specification](../../docs/DSL.md)
- [Module Registry](../../docs/MODULES.md)

## Examples

### Example 1: Generate Blog Post Scraper

```bash
python -m src.cli.main workflows/meta/generate_workflow.yaml \
  --param description="Scrape Medium top stories, extract titles and authors, save to CSV" \
  --param output_path=workflows/_generated/medium_scraper.yaml
```

### Example 2: Improve Error Handling

```bash
python -m src.cli.main workflows/meta/refactor_workflow.yaml \
  --param target_workflow=workflows/google_search.yaml \
  --param improvements=error-handling \
  --param output_path=workflows/_refactored/google_search_v2.yaml
```

### Example 3: Learn from Failures

```bash
python -m src.cli.main workflows/meta/continuous_learning.yaml \
  --param log_directory=logs/executions \
  --param analysis_period_days=7
```

## Best Practices

1. Start with analysis before modification
2. Use local LLM (Ollama) for cost efficiency
3. Always validate generated workflows
4. Test in sandbox before production
5. Review AI output carefully
6. Maintain audit trail
7. Use version control for all changes

## Contributing

To add new meta-workflows:

1. Follow atomic composition pattern
2. Keep coupling low between steps
3. Add safety checks and validation
4. Write to isolated directories only
5. Include comprehensive documentation
6. Test with various workflows

## Questions

See [main documentation](../../docs/META_WORKFLOWS.md) or open an issue.
