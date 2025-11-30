# 🚀 Quickstart Guide for Contributors

Welcome to Flyto2! This guide will get you up and running in **5 minutes**.

---

## Prerequisites

- Python 3.8+ installed
- Git installed
- Basic Python knowledge
- (Optional) Playwright for browser automation

---

## 1. Clone & Setup (2 minutes)

```bash
# Clone the repository
git clone https://github.com/flytohub/flyto2.git
cd flyto2

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development

# Install Playwright browsers (optional, for browser modules)
playwright install chromium
```

---

## 2. Run Your First Workflow (1 minute)

```bash
# Run a simple example workflow
python -m src.cli.main workflows/api_pipeline.yaml
```

You should see output showing the workflow executing successfully! ✅

---

## 3. Explore the Codebase (2 minutes)

### Project Structure

```
flyto2/
├── src/
│   └── core/
│       ├── engine/          # Workflow execution engine
│       ├── modules/         # All 56 modules
│       │   ├── atomic/      # Core modules (no dependencies)
│       │   └── third_party/ # External integrations
│       └── browser/         # Playwright browser driver
│
├── workflows/               # Example YAML workflows
├── tests/                   # Unit tests
├── docs/                    # Documentation
└── i18n/                    # Translations (en, zh, ja)
```

### Key Files to Know

- **Module Registry**: `src/core/modules/registry.py`
- **Module Base Class**: `src/core/modules/base.py`
- **Workflow Engine**: `src/core/engine/workflow_engine.py`
- **Module Specification**: `docs/MODULE_SPECIFICATION.md`

---

## 4. Your First Contribution

### Option A: Add a Simple Module (Beginner)

Let's add an `api.openai.chat` module:

1. **Create the file**: `src/core/modules/third_party/ai/openai.py`

```python
from ...base import BaseModule
from ...registry import register_module

@register_module(
    module_id='api.openai.chat',
    version='1.0.0',
    category='ai',
    subcategory='ai',
    label='OpenAI Chat',
    description='Send a chat message to OpenAI GPT',
    icon='MessageCircle',
    color='#10A37F',

    # Phase 2: Execution settings
    timeout=60,
    retryable=True,
    max_retries=3,
    concurrent_safe=True,

    # Phase 2: Security settings
    requires_credentials=True,
    handles_sensitive_data=True,
    required_permissions=['network.access', 'ai.api'],

    params_schema={
        'prompt': {
            'type': 'string',
            'label': 'Prompt',
            'description': 'The message to send to GPT',
            'required': True
        },
        'model': {
            'type': 'string',
            'label': 'Model',
            'description': 'OpenAI model to use',
            'default': 'gpt-4',
            'required': False
        }
    },
    output_schema={
        'response': {'type': 'string'},
        'usage': {'type': 'object'}
    }
)
class OpenAIChatModule(BaseModule):
    """OpenAI Chat Module"""

    def validate_params(self):
        self.prompt = self.params.get('prompt')
        self.model = self.params.get('model', 'gpt-4')

        import os
        self.api_key = os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable required")

    async def execute(self):
        import openai
        openai.api_key = self.api_key

        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[{"role": "user", "content": self.prompt}]
        )

        return {
            "response": response.choices[0].message.content,
            "usage": response.usage
        }
```

2. **Import in** `src/core/modules/third_party/ai/__init__.py`:

```python
from . import services  # Existing
from . import openai    # Add this
```

3. **Test it**:

```bash
# Validate module
python scripts/validate_all_modules.py

# Run tests
python -m pytest tests/test_phase2_features.py -v
```

4. **Create a test workflow** `test_openai.yaml`:

```yaml
name: "Test OpenAI"
steps:
  - id: chat
    module: api.openai.chat
    params:
      prompt: "Say hello in 5 words"
      model: "gpt-4"
```

5. **Submit PR**:

```bash
git checkout -b feature/add-openai-module
git add .
git commit -m "Add OpenAI GPT chat module"
git push origin feature/add-openai-module
```

### Option B: Add an Example Workflow (Beginner)

Create `workflows/github_stars_scraper.yaml`:

```yaml
name: "GitHub Stars Scraper"
description: "Scrape GitHub repository stars and save to CSV"

steps:
  - id: fetch_repo
    module: api.github.get_repo
    params:
      owner: "facebook"
      repo: "react"
      token: "${env.GITHUB_TOKEN}"

  - id: fetch_stargazers
    module: api.http_get
    params:
      url: "https://api.github.com/repos/facebook/react/stargazers"
      headers:
        Authorization: "token ${env.GITHUB_TOKEN}"

  - id: save_csv
    module: data.csv.write
    params:
      file_path: "react_stars.csv"
      data: "${fetch_stargazers.data}"

  - id: notify
    module: notification.slack.send_message
    params:
      text: "✅ Scraped ${fetch_repo.data.stargazers_count} stars!"
```

### Option C: Improve Documentation (Beginner)

- Add examples to `docs/MODULES.md`
- Write tutorials in `docs/`
- Translate to other languages in `i18n/`

---

## 5. Development Best Practices

### Before Submitting a PR

```bash
# 1. Validate modules
python scripts/validate_all_modules.py

# 2. Run linter
python scripts/lint_modules.py --strict

# 3. Run tests
python -m pytest tests/ -v

# 4. Check Phase 2 compliance
python -m pytest tests/test_phase2_features.py -v
```

### PR Checklist

- [ ] Module follows atomic design (single responsibility)
- [ ] Uses i18n keys (no hardcoded Chinese text in code)
- [ ] Complete `params_schema` with descriptions
- [ ] At least 2 examples in module metadata
- [ ] Error handling implemented
- [ ] Phase 2 execution settings configured
- [ ] Phase 2 security settings declared
- [ ] Validation passes: `python scripts/validate_all_modules.py`

---

## 6. Getting Help

- 📖 **Documentation**: Check `docs/` folder
- 💬 **Discussions**: [GitHub Discussions](https://github.com/flytohub/flyto2/discussions)
- 🐛 **Issues**: [Report bugs](https://github.com/flytohub/flyto2/issues)
- 📝 **Contributing Guide**: See `CONTRIBUTING.md`

---

## 7. What to Build Next

### Easy Wins (Good First Issues)
- ✅ Add `api.openai.chat` module
- ✅ Add `api.http.delete` module
- ✅ Add `db.redis.get/set` modules
- ✅ Add more example workflows
- ✅ Write tutorials

### Medium Difficulty
- 🔧 Add parallel execution blocks to DSL
- 🔧 Create observability dashboard
- 🔧 Add GCS/Azure storage modules

### Advanced
- 🚀 Module marketplace
- 🚀 Distributed execution engine
- 🚀 Kubernetes operator

---

## 8. Community Guidelines

- **Be respectful** - We're all learning together
- **Ask questions** - No question is too small
- **Share knowledge** - Help others when you can
- **Start small** - Begin with simple contributions
- **Have fun!** - Enjoy building automation tools 🎉

---

## Quick Reference Commands

```bash
# Development
python -m src.cli.main <workflow.yaml>          # Run workflow
python scripts/validate_all_modules.py      # Validate modules
python scripts/lint_modules.py --strict     # Lint modules
python -m pytest tests/ -v                  # Run all tests

# Git
git checkout -b feature/your-feature        # New branch
git add .                                   # Stage changes
git commit -m "message"                     # Commit
git push origin feature/your-feature        # Push
```

---

**Ready to contribute?** Pick a task from [Good First Issues](https://github.com/flytohub/flyto2/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) and get started! 🚀

**Questions?** Open a [Discussion](https://github.com/flytohub/flyto2/discussions) - we're here to help!
