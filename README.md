# Flyto2

> **The Git-Native Workflow Automation Engine**
>
> Browser automation + AI + API integration in portable YAML workflows

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## Why Flyto2?

**Your workflows shouldn't be trapped in a database.**

Flyto2 treats workflows as **version-controlled YAML files** - not proprietary JSON locked in a database. Perfect for teams who need:

✅ **Git-Native Workflows** - Diff, PR review, version control
✅ **Browser + AI + APIs** - Playwright, OpenAI, Slack, GitHub in one engine
✅ **Deploy Anywhere** - Local, Docker, Kubernetes, Lambda
✅ **No Vendor Lock-in** - YAML files run anywhere

**Best for:** DevOps automation, web scraping + AI, internal tools, data pipelines

---

## Quick Start

```bash
# 1. Install
git clone https://github.com/flytohub/flyto2.git
cd flyto2
pip install -r requirements.txt
playwright install chromium

# 2. Run example
python -m cli.main workflows/google_search.yaml

# 3. Create your own
cat > my_workflow.yaml <<EOF
name: "Hello Automation"
steps:
  - id: greet
    module: notification.slack.send_message
    params:
      text: "Workflow engine is running!"
EOF

export SLACK_WEBHOOK_URL=https://hooks.slack.com/...
python -m cli.main my_workflow.yaml
```

**That's it!** You're automating with YAML workflows.

---

## What Makes This Different

| Feature | Flyto2 | n8n | Zapier | Airflow |
|---------|--------|-----|--------|---------|
| **Workflow Format** | ✅ YAML files | JSON in database | Proprietary | Python code |
| **Git Version Control** | ✅ Native | Manual export | ❌ No | ✅ Native |
| **Browser Automation** | ✅ Playwright | Limited | ❌ No | ❌ No |
| **Portable** | ✅ Run anywhere | Needs n8n instance | ❌ Cloud only | Needs Airflow |
| **Open Source Engine** | ✅ MIT | Fair-code license | ❌ Closed | ✅ Apache |

**Use n8n if:** You want a database-backed UI for API integrations
**Use Flyto2 if:** You need Git workflows, browser automation, or YAML portability

---

## Built-in Integrations

Flyto2 comes with **production-ready modules** out of the box:

### 🔔 Notifications
**Slack** • **Discord** • **Telegram** • **Email/SMTP**

### 🔗 APIs
**GitHub** (repos, issues, PRs) • **HTTP/REST** • **OpenAI**

### 🌐 Browser Automation
**Launch** • **Navigate** • **Click** • **Type** • **Extract** • **Screenshot**

### 📊 Data Processing
**CSV** (read/write) • **JSON** (parse/stringify) • **Templates**

### 🛠️ Utilities
**Delay** • **Random** • **DateTime** • **Hash** • **UUIDs**

[→ See complete module list](docs/MODULES.md)

---

## Real-World Examples

### Example 1: GitHub Issues → Slack Alerts

```yaml
name: "Monitor GitHub Issues"

steps:
  - id: fetch_issues
    module: api.github.list_issues
    params:
      owner: "facebook"
      repo: "react"
      state: "open"
      labels: "bug"
      token: "${env.GITHUB_TOKEN}"

  - id: notify
    module: notification.slack.send_message
    if: "${fetch_issues.count > 10}"
    params:
      text: "⚠️ ${fetch_issues.count} open bugs!"
```

**Deploy:**
```bash
export GITHUB_TOKEN=ghp_xxxxx
export SLACK_WEBHOOK_URL=https://hooks.slack.com/...
python -m cli.main github_monitor.yaml
```

**Schedule (cron):**
```bash
*/15 * * * * cd /app && python -m cli.main github_monitor.yaml
```

### Example 2: Web Scraping → CSV Export

```yaml
name: "Scrape Product Prices"

steps:
  - id: browser
    module: core.browser.launch
    params:
      headless: true

  - id: navigate
    module: core.browser.goto
    params:
      browser: "${browser.browser}"
      url: "${params.shop_url}"

  - id: extract
    module: core.browser.extract
    params:
      browser: "${browser.browser}"
      selector: ".product"
      fields:
        name: { selector: "h2", type: "text" }
        price: { selector: ".price", type: "text" }

  - id: export
    module: data.csv.write
    params:
      file_path: "prices_${timestamp}.csv"
      data: "${extract.data}"
```

### More Examples

- [Google Search Automation](workflows/google_search.yaml) - Browser scraping
- [API Pipeline](workflows/api_pipeline.yaml) - Pure API workflows
- [AI Content Summarizer](workflows/ai_content_summarizer.yaml) - Browser + OpenAI
- [Multi-Channel Alerts](workflows/multi_channel_alert.yaml) - Slack + Discord + Telegram + Email
- [Daily Report Email](workflows/daily_report_email.yaml) - API + Email automation

[→ See all 9 example workflows](workflows/)

---

## Documentation

📘 **Essential Guides**
- [DSL Specification](docs/DSL.md) - Complete YAML syntax reference
- [Module Registry](docs/MODULES.md) - All available modules with parameters
- [CLI Usage](docs/CLI.md) - Command-line interface guide

🛠️ **Development**
- [Writing Modules](docs/WRITING_MODULES.md) - Create custom modules
- [Contributing Guide](CONTRIBUTING.md) - How to contribute

🏗️ **Architecture**
- [System Architecture](docs/ARCHITECTURE.md) - Engine design
- [UI Builder Integration](docs/UI_BUILDER_INTEGRATION.md) - For UI developers

---

## Production Deployment

### Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt && playwright install chromium chromium-deps
COPY . .
CMD ["python", "-m", "cli.main", "workflows/production.yaml"]
```

### Kubernetes CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: flyto2-daily-report
spec:
  schedule: "0 9 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: flyto2
            image: flyto2:latest
            args: ["python", "-m", "cli.main", "workflows/daily_report.yaml"]
            envFrom:
            - secretRef:
                name: flyto2-secrets
```

### GitHub Actions

```yaml
name: Run Workflow
on:
  schedule:
    - cron: '0 * * * *'
jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: |
          pip install -r requirements.txt
          playwright install chromium
      - run: python -m cli.main workflows/production.yaml
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

---

## Architecture: Open Engine + Optional UI

### 🔓 Workflow Engine (This Repository)

**Open Source • MIT License • Community-Driven**

The runtime that executes YAML workflows. Run anywhere, no database required.

```bash
pip install -r requirements.txt
python -m cli.main my_workflow.yaml
```

### 🎨 Visual Workflow Builder (Separate Product)

**Free to Use • Closed Source • Completely Optional**

A drag-and-drop editor for building workflows visually.

**Important:** The engine is fully usable without the UI. All workflows created in the UI are standard YAML files that use this open source engine.

---

## Roadmap

**Current (v1.0-alpha)**
- ✅ YAML workflow parser & execution engine
- ✅ Browser automation (Playwright)
- ✅ 20+ production-ready modules
- ✅ Flow control (if/when, retry, error handling)
- ✅ Integrations: Slack, Discord, Telegram, Email, GitHub, OpenAI

**Coming Soon (v1.1)**
- 🚧 Enhanced observability dashboard
- 🚧 More AI integrations (Claude, Gemini)
- 🚧 Database modules (PostgreSQL, MongoDB, Redis)
- 🚧 Cloud storage (S3, GCS, Azure)
- 🚧 Loop & parallel execution control flow

**Future (v2.0)**
- 🔮 Module marketplace
- 🔮 Workflow template library
- 🔮 Distributed execution engine
- 🔮 Kubernetes operator

---

## Contributing

We welcome contributions! **Ways to help:**

- ⚡ **Add modules** - New integrations, AI services, cloud APIs
- 📝 **Improve docs** - Better examples, tutorials
- 🐛 **Report bugs** - Help us improve stability
- 💡 **Share workflows** - Show the community what you build

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Good First Issues

Looking to contribute? Check out issues tagged [`good first issue`](https://github.com/flytohub/flyto2/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22):

- Add module: `api.http.delete`
- Add example: GitHub stars scraper
- Add module: `db.postgresql.query`

---

## Community

- **GitHub Discussions** - [Ask questions, share workflows](https://github.com/flytohub/flyto2/discussions)
- **Issues** - [Report bugs, request features](https://github.com/flytohub/flyto2/issues)
- **Contributing** - [How to contribute](CONTRIBUTING.md)

---

## License

MIT License - see [LICENSE](LICENSE) file.

**You can:**
✅ Use commercially
✅ Modify and distribute
✅ Use in proprietary software
✅ Sub-license

**You must:**
📋 Include license and copyright notice

---

## Acknowledgments

**Built with:**
- [Playwright](https://playwright.dev/) - Browser automation
- Python's async/await - Performance

**Inspired by:**
- Unix philosophy - Do one thing well
- YAML - Human-readable configuration
- Git workflows - Version-controlled automation

---

<div align="center">

**If this project helps you, give it a ⭐!**

[🌟 Star on GitHub](https://github.com/flytohub/flyto2) • [📖 Read Docs](docs/) • [💬 Discussions](https://github.com/flytohub/flyto2/discussions)

**Flyto2: Git-Native Workflow Automation**

</div>
