# Meta-Workflow System

## Overview

Flyto2 can improve itself using AI-powered meta-workflows. These workflows analyze, generate, refactor, and validate other workflows, creating a self-improving automation engine.

## Architecture

Meta-workflows follow the same atomic/composite/third-party pattern:

```
workflows/meta/
├── analyze_workflow.yaml       - Analyze existing workflows
├── generate_workflow.yaml      - Generate new workflows from descriptions
├── refactor_workflow.yaml      - Refactor and improve workflows
├── validate_workflow.yaml      - Validate YAML structure
├── autonomous_improve.yaml     - Autonomous improvement agent
├── create_github_pr.yaml       - Auto-create PRs for changes
├── full_improvement_pipeline.yaml - Complete pipeline
└── continuous_learning.yaml    - Learn from execution logs
```

## Key Principles

### 1. Low Coupling

Each meta-workflow is independent and composable:
- Analysis does not modify
- Generation does not validate
- Validation does not commit
- Commit does not merge

### 2. Safety First

No meta-workflow directly modifies production workflows:
- Always write to `_generated/` or `_refactored/`
- Require validation before PR
- Human review before merge
- Sandbox testing required

### 3. Atomic Composition

Meta-workflows use existing modules:
- `data.file.read` - Read specs and workflows
- `ai.openai.chat` / `ai.local_ollama.chat` - AI analysis
- `agent.autonomous` - Self-directed improvement
- `agent.chain` - Multi-step processing
- `data.file.write` - Save results
- `api.github.*` - Create PRs

## Usage Examples

### Analyze Existing Workflow

```bash
python -m src.cli.main workflows/meta/analyze_workflow.yaml \
  --param target_workflow=workflows/google_search.yaml \
  --param llm_provider=ollama \
  --param model=mistral
```

Output: `workflows/_analysis/<timestamp>_analysis.md`

### Generate New Workflow

```bash
python -m src.cli.main workflows/meta/generate_workflow.yaml \
  --param description="Scrape Hacker News front page and post to Slack" \
  --param output_path=workflows/_generated/hn_scraper.yaml \
  --param model=gpt-4
```

### Refactor Workflow

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
  --param error_log_path=logs/daily_report_errors.log \
  --param output_path=workflows/_improved/daily_report_v2.yaml \
  --param llm_provider=ollama \
  --param model=mistral
```

### Full Pipeline

```bash
python -m src.cli.main workflows/meta/full_improvement_pipeline.yaml \
  --param target_workflow=workflows/multi_channel_alert.yaml \
  --param auto_create_pr=true \
  --param model=gpt-4
```

### Continuous Learning

```bash
python -m src.cli.main workflows/meta/continuous_learning.yaml \
  --param log_directory=logs/executions \
  --param analysis_period_days=7 \
  --param llm_provider=ollama
```

## Workflow Descriptions

### analyze_workflow.yaml

Analyzes existing workflow and provides suggestions.

**Inputs:**
- `target_workflow` - Path to workflow
- `llm_provider` - openai or ollama
- `model` - Model to use

**Outputs:**
- Analysis report in `workflows/_analysis/`

**Use Case:** Before refactoring, understand issues

### generate_workflow.yaml

Generates new workflow from natural language description.

**Inputs:**
- `description` - What the workflow should do
- `output_path` - Where to save
- `llm_provider` - openai or ollama
- `model` - Model to use

**Outputs:**
- Generated YAML workflow
- Generation report

**Use Case:** Rapid prototyping, idea to YAML

### refactor_workflow.yaml

Refactors existing workflow with improvements.

**Inputs:**
- `target_workflow` - Workflow to refactor
- `output_path` - Where to save refactored version
- `improvements` - Focus area
- `llm_provider` - openai or ollama
- `model` - Model to use

**Outputs:**
- Refactored YAML
- Diff report

**Use Case:** Improve existing workflows systematically

### validate_workflow.yaml

Validates YAML structure and module usage.

**Inputs:**
- `target` - Workflow to validate
- `strict` - Enable strict mode

**Outputs:**
- Validation report JSON

**Use Case:** Pre-commit validation

### autonomous_improve.yaml

Agent autonomously improves workflow based on logs.

**Inputs:**
- `target_workflow` - Workflow to improve
- `error_log_path` - Execution error logs
- `output_path` - Where to save
- `llm_provider` - openai or ollama
- `model` - Model for agent

**Outputs:**
- Improved workflow
- Reasoning trace
- Improvement report

**Use Case:** Fix production issues automatically

### create_github_pr.yaml

Creates GitHub PR for workflow changes.

**Inputs:**
- `workflow_path` - Changed workflow
- `branch_name` - PR branch name
- `pr_title` - PR title
- `pr_description` - PR description

**Outputs:**
- GitHub PR
- Slack notification

**Use Case:** Automate PR creation

### full_improvement_pipeline.yaml

Complete pipeline: analyze, improve, validate, PR.

**Inputs:**
- `target_workflow` - Workflow to improve
- `auto_create_pr` - Auto-create PR
- `llm_provider` - openai or ollama
- `model` - Model to use

**Outputs:**
- Analysis report
- Improved workflow
- Validation results
- GitHub PR (optional)
- Pipeline report

**Use Case:** End-to-end improvement automation

### continuous_learning.yaml

Monitors executions and suggests improvements.

**Inputs:**
- `log_directory` - Execution logs location
- `analysis_period_days` - Days to analyze
- `min_failure_rate` - Threshold for improvement
- `llm_provider` - openai or ollama

**Outputs:**
- Learning report
- Prioritized improvement list
- Slack notification

**Use Case:** Proactive quality improvement

## Best Practices

### 1. Start with Analysis

Always analyze before modifying:
```bash
# First analyze
python -m src.cli.main workflows/meta/analyze_workflow.yaml \
  --param target_workflow=<path>

# Then improve based on analysis
```

### 2. Use Local LLM for Cost

Use Ollama for frequent operations:
```bash
--param llm_provider=ollama \
--param model=mistral
```

Use OpenAI for complex tasks:
```bash
--param llm_provider=openai \
--param model=gpt-4
```

### 3. Always Validate

After generation or refactoring:
```bash
python -m src.cli.main workflows/meta/validate_workflow.yaml \
  --param target=<generated_workflow>
```

### 4. Test Before Merge

Test generated workflows in sandbox:
```bash
# Test with dry-run or test parameters
python -m src.cli.main <generated_workflow> \
  --param environment=test
```

### 5. Review AI Output

Never blindly trust AI-generated code:
- Review YAML structure
- Verify module IDs
- Check error handling
- Test thoroughly

## Safety Mechanisms

### Output Isolation

Meta-workflows never write directly to production:
```
workflows/              - Production workflows (protected)
workflows/_generated/   - AI-generated workflows
workflows/_refactored/  - Refactored workflows
workflows/_improved/    - Autonomous improvements
workflows/_analysis/    - Analysis reports
workflows/_validation/  - Validation results
workflows/_reports/     - Pipeline reports
workflows/_learning/    - Learning reports
```

### Validation Gates

Before any workflow is used:
1. YAML syntax validation
2. Module ID verification
3. Parameter type checking
4. Sandbox testing
5. Human review

### Version Control

All changes go through Git:
1. AI generates workflow
2. Commit to feature branch
3. Create PR with details
4. Human review required
5. Merge only after approval

### Audit Trail

Every meta-workflow execution creates:
- Timestamp in filename
- Full report with reasoning
- Original and modified versions
- Validation results

## Advanced Patterns

### Chain Multiple Meta-Workflows

```yaml
steps:
  # Step 1: Analyze
  - id: analyze
    module: workflow.execute
    params:
      workflow_path: workflows/meta/analyze_workflow.yaml
      params:
        target_workflow: workflows/example.yaml

  # Step 2: Improve based on analysis
  - id: improve
    module: workflow.execute
    params:
      workflow_path: workflows/meta/refactor_workflow.yaml
      params:
        target_workflow: workflows/example.yaml
        improvements: "${analyze.suggestions}"

  # Step 3: Validate
  - id: validate
    module: workflow.execute
    params:
      workflow_path: workflows/meta/validate_workflow.yaml
      params:
        target: "${improve.output_path}"
```

### Scheduled Continuous Learning

```yaml
# Run weekly via cron
0 0 * * 0 python -m src.cli.main workflows/meta/continuous_learning.yaml
```

### Conditional Auto-PR

```yaml
steps:
  - id: improve
    module: workflow.execute
    params:
      workflow_path: workflows/meta/autonomous_improve.yaml

  - id: validate
    module: workflow.execute
    params:
      workflow_path: workflows/meta/validate_workflow.yaml

  - id: create_pr
    module: workflow.execute
    if: "${validate.quality_score > 80}"
    params:
      workflow_path: workflows/meta/create_github_pr.yaml
```

## Monitoring and Metrics

Track meta-workflow effectiveness:

### Metrics to Monitor

- Success rate of AI-generated workflows
- Quality scores from validation
- Number of improvements applied
- Failure rate reduction after improvements
- Time saved vs manual workflow creation

### Example Monitoring Workflow

```yaml
steps:
  - id: collect_metrics
    module: data.file.read
    params:
      file_path: workflows/_reports/*_pipeline_report.md

  - id: analyze_effectiveness
    module: agent.autonomous
    params:
      goal: "Analyze meta-workflow effectiveness metrics"
      context: "${collect_metrics.content}"

  - id: report
    module: notification.slack.send_message
    params:
      text: "${analyze_effectiveness.result}"
```

## Troubleshooting

### AI Generates Invalid YAML

**Problem:** Generated YAML does not parse

**Solution:**
1. Use more specific prompts
2. Increase temperature to 0.1-0.2
3. Provide more examples in prompt
4. Use GPT-4 instead of GPT-3.5

### Module IDs Not Found

**Problem:** AI invents non-existent modules

**Solution:**
1. Include full MODULES.md in prompt
2. Add explicit instruction: "Use only modules from registry"
3. Validate before saving
4. Use chain agent with verification step

### Generated Workflow Too Complex

**Problem:** AI creates overly complex workflows

**Solution:**
1. Specify "keep it simple" in prompt
2. Use examples of simple workflows
3. Break task into smaller workflows
4. Review and simplify manually

### High Cost from OpenAI

**Problem:** Meta-workflows consume too many tokens

**Solution:**
1. Switch to Ollama for frequent operations
2. Use GPT-3.5 instead of GPT-4 where appropriate
3. Reduce context size in prompts
4. Cache common analyses

## Future Enhancements

Planned improvements to meta-workflow system:

### 1. Workflow Templates

Generate workflows from templates:
```yaml
template: "web_scraping"
target_url: "https://example.com"
data_fields: ["title", "price"]
```

### 2. A/B Testing

Compare original vs improved workflows:
```yaml
- id: ab_test
  module: meta.compare_workflows
  params:
    workflow_a: original.yaml
    workflow_b: improved.yaml
    test_iterations: 100
```

### 3. Auto-Rollback

Automatically rollback if improvements fail:
```yaml
- id: monitor
  module: meta.monitor_deployment
  params:
    workflow: improved.yaml
    rollback_on_failure: true
```

### 4. Learning Repository

Build knowledge base of improvements:
```yaml
- id: learn
  module: meta.update_knowledge_base
  params:
    improvement: "${improvement_report}"
    category: "error_handling"
```

## Resources

- [DSL Specification](DSL.md)
- [Module Registry](MODULES.md)
- [Local AI Agent Guide](LOCAL_AI_AGENT.md)
- [Example Workflows](../workflows/)

## Contributing

To add new meta-workflows:

1. Follow atomic composition pattern
2. Keep coupling low
3. Add safety checks
4. Write to isolated directories
5. Include validation
6. Document thoroughly
7. Test with various workflows

## Questions

Open an issue on [GitHub](https://github.com/flytohub/flyto2/issues)
