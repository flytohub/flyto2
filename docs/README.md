# 📚 Flyto2 Documentation

Complete documentation for the Flyto2 workflow automation engine.

---

## 📖 Quick Navigation

### 🚀 Getting Started
- [**Quick Start Guide**](../QUICKSTART.md) - Choose your path: Developer, Bot, or Monitoring
- [**CLI Usage**](getting-started/CLI.md) - Command-line interface reference
- [**DSL Specification**](getting-started/DSL.md) - Complete YAML workflow syntax
- [**Parameter Best Practices**](getting-started/PARAMETER_BEST_PRACTICES.md) - Design flexible workflows

### 🏗️ Architecture
- [**Project Structure**](architecture/PROJECT_STRUCTURE.md) - Directory organization
- [**Level 4 Architecture**](architecture/LEVEL_4_ARCHITECTURE.md) - Advanced monitoring system
- [**Bot Architecture**](architecture/TELEGRAM_BOT_ARCHITECTURE.md) - Telegram bot design

### 🧩 Modules
- [**Module Registry**](modules/MODULES.md) - All 100+ available modules
- [**Module Specification**](modules/MODULE_SPECIFICATION.md) - Complete module spec
- [**Module Quick Reference**](modules/MODULE_QUICK_REFERENCE.md) - Fast lookup
- [**Writing Modules**](modules/WRITING_MODULES.md) - Create custom modules
- [**Module Categories**](modules/MODULE_CATEGORIES.md) - Category organization
- [**Module Quality System**](modules/MODULE_QUALITY_SYSTEM.md) - Quality tracking
- [**Phase 2 Features**](modules/MODULE_PHASE2_FEATURES.md) - Advanced features
- [**Dynamic Module Registry**](modules/DYNAMIC_MODULE_REGISTRY.md) - Runtime registration

### 🚢 Deployment
- [**Windows Setup**](deployment/WINDOWS_SETUP.md) - Windows installation guide
- [**Telegram Bot Setup**](deployment/TELEGRAM_BOT_SETUP.md) - Bot deployment

### 📘 Advanced Guides
- [**Meta Workflows**](guides/META_WORKFLOWS.md) - Self-modifying workflows
- [**Meta Workflow Safety**](guides/META_WORKFLOW_SAFETY.md) - Safe meta-programming
- [**UI Module Integration**](guides/UI_MODULE_INTEGRATION.md) - Module UI components
- [**Phase 2 UI Integration**](guides/PHASE2_UI_INTEGRATION.md) - Advanced UI features

**Note:** AI Agent documentation is in [Module Registry](modules/MODULES.md#ai-agents)

### 🔧 References
- [**Contributing Guide**](../CONTRIBUTING.md) - How to contribute and maintain repository
- [**Documentation Index**](../DOCUMENTATION_INDEX.md) - Complete file organization guide

---

## 📂 Documentation Structure

```
docs/
├── README.md                      # This file
├── getting-started/               # New user guides
│   ├── CLI.md                    # Command-line reference
│   ├── DSL.md                    # Workflow syntax
│   ├── PARAMETER_BEST_PRACTICES.md
│   └── PROMPT_GUIDE.md
├── architecture/                  # System design
│   ├── ARCHITECTURE.md           # Core architecture
│   ├── PROJECT_STRUCTURE.md      # File organization
│   ├── LEVEL_4_ARCHITECTURE.md   # Monitoring system
│   └── TELEGRAM_BOT_ARCHITECTURE.md
├── modules/                       # Module documentation
│   ├── MODULES.md                # Complete registry
│   ├── MODULE_SPECIFICATION.md   # Spec reference
│   ├── MODULE_QUICK_REFERENCE.md # Quick lookup
│   ├── WRITING_MODULES.md        # Development guide
│   ├── MODULE_CATEGORIES.md
│   ├── MODULE_QUALITY_SYSTEM.md
│   ├── MODULE_PHASE2_FEATURES.md
│   └── DYNAMIC_MODULE_REGISTRY.md
├── deployment/                    # Deployment guides
│   ├── WINDOWS_SETUP.md
│   └── TELEGRAM_BOT_SETUP.md
├── guides/                        # Advanced topics
│   ├── META_WORKFLOWS.md
│   ├── META_WORKFLOW_SAFETY.md
│   ├── CASE_STUDY_META_WORKFLOW.md
│   ├── UI_BUILDER_INTEGRATION.md
│   ├── UI_MODULE_INTEGRATION.md
│   ├── PHASE2_UI_INTEGRATION.md
│   └── LOCAL_AI_AGENT.md
└── README.md                      # This file
```

---

## 🎯 Common Tasks

### Run Your First Workflow

```bash
# 1. Install
git clone https://github.com/flytohub/flyto2.git
cd flyto2
pip install -r requirements.txt
playwright install chromium

# 2. Run example
python -m src.cli.main workflows/api_pipeline.yaml

# 3. See all examples
ls workflows/
```

**Next:** Read [CLI Usage](getting-started/CLI.md)

### Create a Custom Workflow

```yaml
name: "My Workflow"
steps:
  - id: fetch_data
    module: api.http.get
    params:
      url: "https://api.example.com/data"

  - id: notify
    module: notification.slack.send_message
    params:
      text: "Data fetched: ${fetch_data.data}"
```

**Next:** Read [DSL Specification](getting-started/DSL.md)

### Find Available Modules

Browse by category in [Module Registry](modules/MODULES.md):
- Browser automation (9 modules)
- API integrations (25+ modules)
- Data processing (20+ modules)
- Notifications (5 modules)
- Utilities (30+ modules)

**Next:** See [Module Categories](modules/MODULE_CATEGORIES.md)

### Add a New Integration

1. Read [Writing Modules](modules/WRITING_MODULES.md)
2. Create module file in `src/core/modules/`
3. Use `@register_module` decorator
4. Add tests
5. Submit PR

**Next:** See [Contributing Guide](../CONTRIBUTING.md)

### Deploy to Production

Choose your deployment method:
- **Docker:** See [CLI Usage - Docker](getting-started/CLI.md#docker-usage)
- **Windows:** See [Windows Setup](deployment/WINDOWS_SETUP.md)
- **Telegram Bot:** See [Bot Setup](deployment/TELEGRAM_BOT_SETUP.md)
- **Cron:** See [CLI Usage - Scheduling](getting-started/CLI.md#scheduling-workflows)

### Debug a Workflow

```bash
# Enable debug logging
python -m src.cli.main workflow.yaml --log-level=DEBUG

# Validate without running
python -m src.cli.main workflow.yaml --dry-run
```

**Next:** See [CLI Usage - Debugging](getting-started/CLI.md#debugging)

---

## 🧩 Module Overview

### Atomic Modules (Core)
No external dependencies, composable building blocks:
- **Browser Operations**: launch, goto, click, type, extract, screenshot
- **Data Transformation**: CSV, JSON, templates
- **Utilities**: delay, random, datetime, hash

See [modules/MODULES.md - Atomic Modules](modules/MODULES.md#atomic-modules)

### Third-party Integrations
External services and platforms:
- **AI**: OpenAI, Anthropic Claude, Google Gemini
- **Communication**: Slack, Discord, Telegram, Email
- **Databases**: PostgreSQL, MySQL, MongoDB
- **Cloud Storage**: AWS S3
- **Productivity**: Notion, Google Sheets

See [modules/MODULES.md - Integrations](modules/MODULES.md#third-party-integrations)

---

## 🛠️ Quick Module Reference

### Browser Operations
```yaml
core.browser.launch        # Launch browser
core.browser.goto          # Navigate to URL
core.browser.click         # Click element
core.browser.type          # Type text
core.browser.extract       # Extract data
core.browser.screenshot    # Take screenshot
```

### AI Services
```yaml
ai.openai.chat            # OpenAI GPT chat
api.anthropic.chat        # Anthropic Claude
api.google_gemini.chat    # Google Gemini
```

### Communication
```yaml
notification.slack.send_message      # Slack
notification.discord.send_message    # Discord
notification.telegram.send_message   # Telegram
notification.email.send              # Email
```

### Data Processing
```yaml
data.csv.read             # Read CSV
data.csv.write            # Write CSV
data.json.parse           # Parse JSON
data.json.stringify       # To JSON
string.split              # Split string
array.filter              # Filter array
```

See [Module Quick Reference](modules/MODULE_QUICK_REFERENCE.md) for complete list.

---

## 🌍 Environment Variables

Common environment variables used across modules:

```bash
# Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CHAT_ID=@your_channel

# AI Services
OPENAI_API_KEY=sk-xxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
GOOGLE_AI_API_KEY=AIzaxxxxxxxxxxxx

# GitHub
GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# Databases
POSTGRESQL_URL=postgresql://user:password@host:port/db
MONGODB_URL=mongodb://user:password@host:port/db

# Cloud Storage
AWS_ACCESS_KEY_ID=AKIAxxxxxxxxxxxx
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxx
```

**Next:** See [CLI Usage - Environment](getting-started/CLI.md#environment-setup)

---

## 📦 Example Workflows

All examples available in `workflows/` directory:

1. **google_search.yaml** - Browser automation and web scraping
2. **api_pipeline.yaml** - Pure API workflow
3. **ai_content_summarizer.yaml** - Browser + AI
4. **github_to_slack.yaml** - GitHub API alerts
5. **data_scraping_to_csv.yaml** - Web scraping to CSV
6. **daily_report_email.yaml** - API to email report
7. **multi_channel_alert.yaml** - Multi-platform broadcast

**Next:** Browse [workflows/](../workflows/) directory

---

## 💬 Support and Community

- 🐛 **GitHub Issues**: [Report bugs, request features](https://github.com/flytohub/flyto2/issues)
- 💬 **Discussions**: [Ask questions, share workflows](https://github.com/flytohub/flyto2/discussions)
- 🤝 **Contributing**: [How to contribute](../CONTRIBUTING.md)

---

## 📄 License

MIT License - see [LICENSE](../LICENSE) file for details.

---

**Back to:** [Main README](../README.md) | [Quick Start](../QUICKSTART.md)
