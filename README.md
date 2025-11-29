# Flyto2

> **Browser Automation + AI + YAML Workflows**
> The workflow engine designed for developers who need version control, portability, and browser-level automation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## Why This Engine?

This engine is built for developers who need:

✅ **Workflows as plain YAML files** - Git diff, PR review, copy anywhere
✅ **Browser-level automation** - Playwright + APIs + AI in one unified engine
✅ **Composable atomic modules** - Build anything from small building blocks, not locked-in node types

**Perfect for:** Internal automation, web scraping + AI processing, DevOps workflows, data pipeline tasks

### Comparison with Existing Tools

| Tool | Workflow Storage | Portability | Best For |
|------|------------------|-------------|----------|
| **n8n** | JSON in database | ❌ Locked to n8n | API integrations, webhooks |
| **Zapier** | Proprietary cloud | ❌ No export | Non-technical users, SaaS apps |
| **Airflow** | Python DAGs | ⚠️ Code only | Data engineering, batch jobs |
| **This Engine** | **YAML files** | ✅ **Run anywhere** | **Browser automation + Git workflows** |

### Our Solution: Atomic Design + YAML

**One module = One action.** Combine them however you want. Workflows are **YAML files** you can version control.

```yaml
# Build complex workflows by combining atomic modules
steps:
  - module: core.browser.launch    # Launch browser
  - module: core.browser.goto      # Navigate
  - module: core.browser.type      # Type keyword
  - module: core.browser.press     # Press Enter
  - module: core.flow.loop         # Extract results
```

**Benefits:**
- 🧩 Build ANY workflow by combining atomic modules
- 🔓 Workflows are YAML files, not database records
- 📝 Version control with Git
- 🚀 Deploy anywhere (local, Docker, Kubernetes, Lambda)
- 🎯 No vendor lock-in

### Real-World Example

Daily competitor monitoring (browser + AI + notifications):

```yaml
# Monitor competitor pricing every day
steps:
  - id: launch_browser
    module: core.browser.launch

  - id: navigate
    module: core.browser.goto
    params:
      browser: "${launch_browser.browser}"
      url: "https://competitor.com/pricing"

  - id: extract_prices
    module: core.browser.extract
    params:
      browser: "${launch_browser.browser}"
      selector: ".price-table"
      fields:
        plan: { selector: "h3", type: "text" }
        price: { selector: ".amount", type: "text" }

  - id: ai_analysis
    module: ai.openai.chat
    params:
      prompt: "Analyze these prices and suggest if we need to adjust: ${extract_prices.data}"

  - id: notify_slack
    module: api.http.post
    params:
      url: "https://slack.com/api/chat.postMessage"
      body:
        text: "${ai_analysis.message}"
```

**Deploy as cron job:** `0 9 * * * python -m cli.main monitor.yaml`

**Version control:** `git diff monitor.yaml` to see strategy changes over time

---

## Why Not Just Use n8n?

n8n is excellent for API integrations and webhooks. This engine excels when you need:

| Scenario | n8n | This Engine |
|----------|-----|-------------|
| **Complex browser automation** | Limited browser support | ✅ Full Playwright power |
| **Git-based workflow management** | Manual JSON export | ✅ YAML files, native Git |
| **Run the same flow in multiple environments** | Requires n8n instance | ✅ Just copy YAML files |
| **Atomic module composition** | Large predefined nodes | ✅ Build from tiny modules |
| **CI/CD integration** | Need API calls to n8n | ✅ Direct CLI execution |

**Use n8n if:** You primarily connect APIs and need a database-backed UI

**Use this engine if:** You need browser automation, YAML portability, or Git-native workflows

---

## Architecture: Open Engine + Free UI

This project separates the workflow engine from the visual builder:

### 🔓 Workflow Engine (This Repository)
**Open Source • MIT License • Community-Driven**

The runtime that executes YAML workflows. Runs anywhere.

```bash
# Install and run anywhere
pip install -r requirements.txt
python -m cli.main my_workflow.yaml
```

**Why open source?**
- ✅ Complete transparency - audit the code
- ✅ Community contributions - anyone can add modules
- ✅ No vendor lock-in - YAML runs anywhere
- ✅ Self-hostable - own your infrastructure
- ✅ Extend with custom Python modules

### 🎨 Visual Workflow Builder
**Free to Use • Closed Source • Completely Optional**

A drag-and-drop editor for building workflows visually (separate product).

- Visual workflow designer with live preview
- Workflow debugging and testing tools
- Template library and sharing
- Team collaboration features

**Important:** The workflow engine is **fully usable without the visual UI**. You can run all workflows using only the open source CLI + YAML files. The UI is an optional tool for those who prefer visual editing.

**The critical design:** All workflows created in the UI are **standard YAML files** that use this open source engine.

You can:
- Build in UI → Export YAML → Run with open source engine
- Write YAML by hand → Import to UI for visualization
- Mix both approaches freely
- **Never touch the UI** and still have full functionality

```yaml
# Create workflow in UI → Export as YAML → Run anywhere

# On your laptop
python -m cli.main workflow.yaml

# In Docker
docker run -v $(pwd):/workflows workflow-engine workflow.yaml

# On Kubernetes
kubectl create configmap workflow --from-file=workflow.yaml
```

### 🔑 Why This Matters

**Your workflows are portable YAML files, not locked in a database!**

| Feature | This Engine | n8n | Zapier | Airflow |
|---------|-------------|-----|--------|---------|
| **Workflow Format** | YAML files | JSON in DB | Proprietary | Python code |
| **Portability** | ✅ Run anywhere | ❌ Locked to n8n | ❌ Cloud only | ⚠️ Requires Airflow |
| **Version Control** | ✅ Git native | ⚠️ Manual export | ❌ No | ✅ Git native |
| **UI** | ✅ Free | ✅ Free | ❌ Limited free | ❌ No official UI |
| **Engine** | ✅ Open source | ✅ Open source | ❌ Closed | ✅ Open source |
| **Atomic Modules** | ✅ Yes | ❌ Monolithic | ❌ Predefined | ⚠️ Task-based |

---

## Features

### Core Capabilities
- 🧩 **Atomic Modules** - Compose workflows like LEGO blocks
- 📦 **YAML Workflows** - Portable, version-controllable, runs anywhere
- 🌐 **Browser Automation** - Full Playwright power (Chrome, Firefox, WebKit)
- 🔌 **Third-party Integrations** - OpenAI, Anthropic, Gemini (install what you need)
- 🔧 **Extensible** - Write custom modules in Python

### Production Ready
- 🔐 **Secret Management** - Environment variables and `.env` file support (Vault integration planned)
- 🔁 **Error Handling** - Built-in retry, timeout, and error recovery modules
- 📊 **Observability** - Structured logs and execution metadata (dashboard in roadmap)
- ⚡ **Flow Control** - Loop, condition, parallel execution, error branching
- 📘 **Type Safety** - Full Python type hints for reliability

### Developer Experience
- 🎨 **Free Visual Builder** - Optional drag-and-drop UI (closed source, free to use)
- 🔌 **Metadata API** - REST API for UI builders to auto-generate forms (like Swagger)
- ☁️ **Deploy Anywhere** - Local, Docker, Kubernetes, Lambda, CI/CD
- 🌍 **i18n Support** - Multi-language module labels and descriptions
- 📝 **Git Native** - Diff workflows, PR reviews, version control

---

## Quick Start

### 5-Minute Setup

```bash
# 1. Clone and install
git clone https://github.com/flytohub/flyto2.git
cd flyto2
pip install -r requirements.txt
playwright install chromium

# 2. Run example workflow
python -m cli.main workflows/google_search.yaml

# 3. Edit the YAML and run again!
```

**That's it!** You just automated a Google search with YAML.

### Your First Custom Workflow

Create `my_workflow.yaml`:

```yaml
name: "Extract Page Title"
description: "Get the title from any website"

params:
  - name: url
    type: string
    label: "Website URL"
    required: true

steps:
  - id: launch_browser
    module: core.browser.launch
    params:
      headless: false

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
      fields:
        title:
          selector: "title"
          type: "text"

output:
  url: "${params.url}"
  title: "${extract_title.data[0].title}"
```

Run it: `python -m cli.main my_workflow.yaml`

**Version control it:** `git add my_workflow.yaml && git commit`

**Deploy it anywhere:** The same YAML runs on any platform!

---

## Variable Access Convention

All examples in this README follow a consistent variable access pattern:

- **Step outputs:** Each step with an `id` is accessible as `${<id>}`
- **Output fields:** Access step output fields as `${<id>.<field>}`
  - Example: `${extract_prices.data}`, `${ai_analysis.message}`
- **Environment variables:** Access via `${env.VAR_NAME}`
  - Example: `${env.OPENAI_API_KEY}`, `${env.SLACK_WEBHOOK_URL}`
- **Workflow parameters:** Access via `${params.param_name}`
  - Example: `${params.keyword}`, `${params.url}`

**Internally**, the engine maps these to `steps.<id>.output.<field>`, but YAML uses the simplified syntax for readability.

---

## Third-party Integrations

Flyto2 follows a modular architecture similar to n8n - the core engine is lightweight, and you install only the integrations you need.

### Available Integrations

| Integration | Install Command | Modules | Status |
|-------------|----------------|---------|--------|
| **OpenAI** | `pip install openai` | `core.ai.openai.chat`<br/>`core.ai.analyze_text`<br/>`core.ai.summarize` | ✅ Available |
| **Anthropic** | `pip install anthropic` | Coming soon | 🚧 Planned |
| **Google Gemini** | `pip install google-generativeai` | Coming soon | 🚧 Planned |
| **Slack** | `pip install slack-sdk` | Coming soon | 🚧 Planned |
| **Discord** | `pip install discord.py` | Coming soon | 🚧 Planned |

### How to Use Integrations

1. **Install the integration you need:**
   ```bash
   # Install OpenAI integration
   pip install openai

   # Or install from requirements-integrations.txt
   pip install -r requirements-integrations.txt
   ```

2. **Use in your workflow:**
   ```yaml
   steps:
     - id: ai_analysis
       module: core.ai.openai.chat
       params:
         messages:
           - role: user
             content: "Analyze this data: ${extract_data.results}"
         model: gpt-4
   ```

3. **Environment variables:**
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

**Why this approach?**
- ✅ Core engine stays lightweight (no forced AI dependencies)
- ✅ Install only what you need
- ✅ Community can contribute new integrations independently
- ✅ Similar to n8n's node architecture

---

## Atomic Module Philosophy

### Core Principle

**Each module does ONE thing and does it well.**

Complex workflows = Simple modules combined.

### Three Levels of Abstraction

Developers choose their level:

```python
Level 1: Atomic (Maximum Flexibility)
├─ core.browser.launch
├─ core.browser.goto
└─ core.element.click

Level 2: Composite (Balanced)
└─ workflows.google_search
    └─ Combines multiple atomic modules

Level 3: Specific (Domain-Focused)
└─ ecommerce.shopify.sync_inventory
    └─ Built for specific use cases
```

**You choose what to build:**
- Want full control? → Use atomic modules
- Want productivity? → Use composite workflows
- Have specific needs? → Create domain modules

### Available Modules

| Category | Modules | Purpose |
|----------|---------|---------|
| **Browser** | `launch`, `goto`, `click`, `type`, `wait`, `screenshot` | Browser automation |
| **Element** | `find`, `query`, `text`, `attribute` | DOM manipulation |
| **Flow** | `loop`, `condition`, `retry`, `parallel` | Control flow |
| **API** | `http.get`, `http.post`, `google_search` | External APIs |

See [NAMESPACES.yaml](NAMESPACES.yaml) for complete list.

### Example: Build Google Search

```yaml
steps:
  - id: launch_browser
    module: core.browser.launch

  - id: navigate
    module: core.browser.goto
    params:
      browser: "${launch_browser.browser}"
      url: "https://google.com"

  - id: type_query
    module: core.browser.type
    params:
      browser: "${launch_browser.browser}"
      selector: 'input[name="q"]'
      text: "workflow automation"

  - id: submit_search
    module: core.browser.press
    params:
      browser: "${launch_browser.browser}"
      key: "Enter"

  - id: extract_results
    module: core.browser.extract
    params:
      browser: "${launch_browser.browser}"
      selector: "#search .g"
      limit: 10
```

**Each step is atomic, reusable, and composable!**

---

## YAML Portability

### Write Once, Run Anywhere

Your workflows are YAML files - they run on any platform:

```bash
# Local development
python -m cli.main workflow.yaml

# Docker container
docker run -v $(pwd):/app workflow-engine python -m cli.main /app/workflow.yaml

# Kubernetes CronJob
apiVersion: batch/v1
kind: CronJob
spec:
  schedule: "0 * * * *"
  jobTemplate:
    spec:
      containers:
      - name: workflow
        image: workflow-engine
        args: ["python", "-m", "cli.main", "/workflows/workflow.yaml"]

# AWS Lambda
# Serverless function
# CI/CD pipeline
# Anywhere!
```

### Version Control Friendly

```bash
# Your workflows are just files
git add workflows/
git commit -m "Add customer onboarding workflow"
git push

# Review changes
git diff workflows/google_search.yaml

# Rollback if needed
git revert HEAD
```

### No Database Lock-in

Unlike n8n or Zapier, your workflows aren't trapped in a database:

```yaml
# n8n: Workflows stored in PostgreSQL/SQLite
# ❌ Hard to backup
# ❌ Hard to migrate
# ❌ Hard to version control

# This Engine: Workflows are YAML files
# ✅ Easy to backup (cp *.yaml backup/)
# ✅ Easy to migrate (just copy files)
# ✅ Native Git support
```

---

## Documentation

- **DSL Specification**: [docs/DSL.md](docs/DSL.md) - Complete YAML workflow syntax reference
- **UI Builder Integration**: [docs/UI_BUILDER_INTEGRATION.md](docs/UI_BUILDER_INTEGRATION.md) - Metadata API for dynamic form generation (like Swagger)
- **Metadata API**: [docs/METADATA_API.md](docs/METADATA_API.md) - REST API endpoints for module metadata
- **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Third-party integrations design
- **Contributing Guide**: [CONTRIBUTING.md](CONTRIBUTING.md) - How to add modules
- **Module Taxonomy**: [NAMESPACES.yaml](NAMESPACES.yaml) - All available modules
- **Example Workflows**: [workflows/](workflows/) - Ready-to-use examples

---

## Roadmap

### Current (v1.0)
- ✅ Core browser automation modules (Playwright)
- ✅ Flow control (loop, condition, retry)
- ✅ Atomic module architecture
- ✅ YAML workflow engine
- ✅ Environment variable support for secrets
- ✅ Basic error handling and logging
- ✅ Free visual UI (closed source, launching simultaneously)

### Coming Soon (v1.1)
- [ ] Enhanced observability (workflow execution dashboard)
- [ ] Vault integration for secret management
- [ ] More AI integrations (Claude, Gemini)
- [ ] Database modules (PostgreSQL, MongoDB, Redis)
- [ ] Cloud storage (S3, GCS, Azure Blob)
- [ ] Notification modules (Slack, Discord, Email)
- [ ] Advanced error recovery strategies

### Future (v2.0)
- [ ] Module marketplace and community modules
- [ ] Workflow template library
- [ ] Distributed execution engine
- [ ] Kubernetes operator for workflow scheduling
- [ ] Real-time collaboration in visual UI

**Want to help?** Check [CONTRIBUTING.md](CONTRIBUTING.md)!

---

## Contributing

We welcome contributions! This project thrives on community modules.

**Ways to contribute:**
- ⚡ Add new atomic modules (AI, cloud, databases)
- 📝 Improve documentation
- 🐛 Report bugs
- ✅ Write tests
- 💡 Share workflow examples

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guide.

### Module Development

Creating a module is simple:

```python
@register_module(
    module_id='core.browser.click',
    label='Click Element',
    label_key='modules.browser.click.label',
    description='Click an element on the page'
)
class BrowserClickModule(BaseModule):
    async def execute(self):
        # Your implementation here
        pass
```

Check existing modules in `src/core/modules/` for examples.

---

## Project Structure

```
flyto2/
├── cli/                  # CLI application
├── src/
│   └── core/
│       └── modules/      # All modules here
│           ├── browser_modules.py
│           ├── api_modules.py
│           └── atomic/
├── workflows/            # Example YAML workflows
├── i18n/                 # Translations
├── docs/                 # Documentation
│   └── DSL.md           # YAML syntax specification
├── NAMESPACES.yaml       # Module taxonomy
├── CONTRIBUTING.md       # How to contribute
└── README.md            # You are here
```

---

## Production Examples

### Example 1: Automated Competitor Monitoring

Monitor competitor prices and get AI-powered insights delivered to Slack daily:

```yaml
name: "Competitor Price Monitor"
description: "Daily competitor analysis with AI insights"

steps:
  - id: launch_browser
    module: core.browser.launch
    params:
      headless: true

  - id: navigate
    module: core.browser.goto
    params:
      browser: "${launch_browser.browser}"
      url: "${env.COMPETITOR_URL}"

  - id: extract_prices
    module: core.browser.extract
    params:
      browser: "${launch_browser.browser}"
      selector: ".pricing-table"
      fields:
        plan: { selector: ".plan-name", type: "text" }
        price: { selector: ".price-amount", type: "text" }

  - id: ai_analysis
    module: ai.openai.chat
    params:
      api_key: "${env.OPENAI_API_KEY}"
      prompt: |
        Analyze competitor pricing and suggest actions:
        ${extract_prices.data}

  - id: notify_team
    module: api.http.post
    params:
      url: "${env.SLACK_WEBHOOK_URL}"
      body:
        text: "Daily Competitor Analysis"
        blocks:
          - type: "section"
            text: "${ai_analysis.message}"
```

**Deploy:** `0 9 * * * python -m cli.main competitor_monitor.yaml`

### Example 2: Internal Admin Dashboard Automation

Log in to your internal admin panel, pull reports, and process with AI:

```yaml
name: "Daily Admin Report"
description: "Auto-login, extract data, summarize with AI"

steps:
  - id: launch_browser
    module: core.browser.launch

  - id: goto_login
    module: core.browser.goto
    params:
      browser: "${launch_browser.browser}"
      url: "https://admin.yourcompany.com/login"

  - id: type_email
    module: core.browser.type
    params:
      browser: "${launch_browser.browser}"
      selector: "#email"
      text: "${env.ADMIN_EMAIL}"

  - id: type_password
    module: core.browser.type
    params:
      browser: "${launch_browser.browser}"
      selector: "#password"
      text: "${env.ADMIN_PASSWORD}"

  - id: submit_login
    module: core.browser.click
    params:
      browser: "${launch_browser.browser}"
      selector: "button[type=submit]"

  - id: wait_dashboard
    module: core.browser.wait
    params:
      browser: "${launch_browser.browser}"
      selector: ".dashboard"
      timeout_ms: 5000

  - id: goto_reports
    module: core.browser.goto
    params:
      browser: "${launch_browser.browser}"
      url: "https://admin.yourcompany.com/reports/daily"

  - id: extract_metrics
    module: core.browser.extract
    params:
      browser: "${launch_browser.browser}"
      selector: ".report-row"
      limit: 100
      fields:
        metric: { selector: ".metric-name", type: "text" }
        value: { selector: ".metric-value", type: "text" }

  - id: ai_summary
    module: ai.openai.chat
    params:
      api_key: "${env.OPENAI_API_KEY}"
      prompt: "Summarize these metrics and highlight anomalies: ${extract_metrics.data}"

  - id: notify_slack
    module: api.http.post
    params:
      url: "${env.SLACK_WEBHOOK_URL}"
      body: { text: "${ai_summary.message}" }
```

**Version control:** Track strategy changes with `git diff daily_report.yaml`

### Example 3: SEO Rank Tracking

Track keyword rankings and save historical data:

```yaml
name: "SEO Rank Tracker"
steps:
  - id: launch_browser
    module: core.browser.launch

  - id: search_keyword
    module: core.browser.goto
    params:
      browser: "${launch_browser.browser}"
      url: "https://google.com/search?q=${params.keyword}"

  - id: extract_results
    module: core.browser.extract
    params:
      browser: "${launch_browser.browser}"
      selector: "#search .g"
      limit: 100
      fields:
        position: { type: "index" }
        title: { selector: "h3", type: "text" }
        url: { selector: "a", type: "attribute", attribute: "href" }

  - id: find_our_ranking
    module: core.flow.loop
    params:
      items: "${extract_results.data}"
      steps:
        - module: core.data.filter
          params:
            condition: "${item.url} contains 'mysite.com'"
            output: "our_ranking"

  - id: save_ranking
    module: api.http.post
    params:
      url: "${env.DATABASE_API}/rankings"
      body:
        keyword: "${params.keyword}"
        position: "${find_our_ranking.our_ranking.position}"
        date: "${timestamp}"
```

**Run in CI/CD:** Perfect for scheduled jobs in GitHub Actions or GitLab CI

---

**More production examples:** See [workflows/](workflows/) directory for complete, runnable workflow files.

---

## License

MIT License - see [LICENSE](LICENSE) file.

Feel free to use this in commercial projects!

---

## Acknowledgments

Built with:
- [Playwright](https://playwright.dev/) - Browser automation
- Python's async/await - Performance

Inspired by:
- Unix philosophy - Do one thing well
- LEGO blocks - Composable modules
- YAML - Human-readable configuration

---

## Community

- **GitHub Issues**: [Report bugs or request features](https://github.com/flytohub/flyto2/issues)
- **Discussions**: [Ask questions, share workflows](https://github.com/flytohub/flyto2/discussions)
- **Contributing**: [Join the development](CONTRIBUTING.md)

---

<div align="center">

**If you find this useful, give it a ⭐!**

**Flyto2: Open Engine • Free UI • Portable YAML**

[⭐ Star](https://github.com/flytohub/flyto2) | [🐛 Report Bug](https://github.com/flytohub/flyto2/issues) | [💡 Request Feature](https://github.com/flytohub/flyto2/issues)

</div>
