# Flyto2 Documentation

Complete documentation for the Flyto2 workflow automation engine.

---

## Quick Navigation

### Getting Started
- [Quick Start Guide](../README.md#quick-start) - 3-step installation and first workflow
- [CLI Usage](CLI.md) - Command-line interface reference
- [DSL Specification](DSL.md) - Complete YAML workflow syntax

### Core References
- [Module Registry](MODULES.md) - All available modules with parameters
- [Architecture](ARCHITECTURE.md) - System design and engine internals
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute

### Development
- [Writing Modules](WRITING_MODULES.md) - Create custom modules
- [UI Builder Integration](UI_BUILDER_INTEGRATION.md) - For UI developers

---

## Documentation Structure

### 1. DSL Specification (DSL.md)

Complete reference for YAML workflow syntax including:
- Top-level fields (id, name, version, params, config, steps, output)
- Parameter types (string, number, boolean, select, array, object)
- Variable interpolation syntax
- Step configuration (module, params, timeout, retry, error handling)
- Control flow (if/when conditions)
- Examples and best practices

**Use when:** Writing or modifying workflows

### 2. Module Registry (MODULES.md)

Comprehensive list of all available modules organized by category:
- Browser Automation (launch, goto, click, type, extract, screenshot, close)
- HTTP and APIs (GET, POST, GitHub, Slack, Discord, Telegram, Email)
- AI Services (OpenAI, Anthropic Claude, Google Gemini)
- Databases (PostgreSQL, MySQL, MongoDB)
- Cloud Storage (AWS S3)
- Productivity (Notion, Google Sheets)
- Data Processing (CSV, JSON, templates)
- Utilities (delay, random, datetime, hash)

Each module includes:
- Parameter tables with types and descriptions
- Output schema
- Complete examples
- Links to official API documentation

**Use when:** Looking up module capabilities and parameters

### 3. CLI Usage (CLI.md)

Command-line interface guide covering:
- Installation and setup
- Running workflows
- Passing parameters (CLI args, env vars, .env file)
- Environment variable configuration
- Scheduling (cron, systemd, Windows Task Scheduler)
- Docker deployment
- CI/CD integration (GitHub Actions, GitLab CI)
- Debugging and troubleshooting

**Use when:** Running workflows or setting up automation

### 4. Architecture (ARCHITECTURE.md)

System design documentation including:
- Engine architecture overview
- Module system design
- Execution flow
- Variable resolution
- Error handling strategies
- Extension points

**Use when:** Understanding internals or extending the engine

### 5. Writing Modules (WRITING_MODULES.md)

Guide for creating custom modules:
- Module structure and registration
- Parameter schema definition
- Output schema specification
- Error handling
- Async/await patterns
- Testing modules
- Publishing to registry

**Use when:** Creating new integrations

### 6. Contributing Guide (../CONTRIBUTING.md)

How to contribute to the project:
- Code style guidelines
- Pull request process
- Issue reporting
- Good first issues
- Development setup

**Use when:** Contributing code or documentation

### 7. UI Builder Integration (UI_BUILDER_INTEGRATION.md)

For developers building visual workflow editors:
- YAML schema for UI generation
- Module metadata usage
- Validation rules
- UI component mapping
- Workflow export format

**Use when:** Building UI tools on top of Flyto2

---

## Common Tasks

### Run Your First Workflow

```bash
# 1. Install
git clone https://github.com/flytohub/flyto2.git
cd flyto2
pip install -r requirements.txt
playwright install chromium

# 2. Run example
python -m cli.main workflows/google_search.yaml

# 3. See all examples
ls workflows/
```

**Next:** Read [CLI Usage](CLI.md) for parameter passing and scheduling

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

**Next:** Read [DSL Specification](DSL.md) for complete syntax

### Find Available Modules

Browse by category in [Module Registry](MODULES.md):
- Browser automation
- API integrations
- Notifications
- Data processing
- Utilities

**Next:** See [Module Registry](MODULES.md) for all available modules

### Add a New Integration

1. Read [Writing Modules](WRITING_MODULES.md)
2. Create module file in `src/core/modules/`
3. Use `@register_module` decorator
4. Add tests
5. Submit PR

**Next:** See [Contributing Guide](../CONTRIBUTING.md)

### Deploy to Production

Choose your deployment method:
- **Docker:** See [CLI Usage - Docker](CLI.md#docker-usage)
- **Kubernetes:** See [README - Kubernetes CronJob](../README.md#kubernetes-cronjob)
- **GitHub Actions:** See [README - GitHub Actions](../README.md#github-actions)
- **Cron:** See [CLI Usage - Scheduling](CLI.md#scheduling-workflows)

**Next:** Read [CLI Usage](CLI.md) for production deployment

### Debug a Workflow

```bash
# Enable debug logging
python -m cli.main workflow.yaml --log-level=DEBUG

# Validate without running
python -m cli.main workflow.yaml --dry-run
```

**Next:** See [CLI Usage - Debugging](CLI.md#debugging)

---

## Module Categories

### Browser Automation
Launch browsers, navigate pages, extract data, take screenshots
- See [MODULES.md - Browser Automation](MODULES.md#browser-automation)

### HTTP and APIs
REST APIs, webhooks, GitHub, OpenAI integrations
- See [MODULES.md - HTTP and APIs](MODULES.md#http-and-apis)

### Notifications
Send alerts via Slack, Discord, Telegram, Email
- See [MODULES.md - Notifications](MODULES.md#notifications)

### AI Services
Integrate with OpenAI GPT, Anthropic Claude, Google Gemini
- See [MODULES.md - AI Services](MODULES.md#ai-services)

### Databases
Query and insert data in PostgreSQL, MySQL, MongoDB
- See [MODULES.md - Databases](MODULES.md#databases)

### Cloud Storage
Upload and download files from AWS S3
- See [MODULES.md - Cloud Storage](MODULES.md#cloud-storage)

### Productivity Tools
Create pages in Notion, read/write Google Sheets
- See [MODULES.md - Productivity](MODULES.md#productivity)

### Data Processing
Parse CSV/JSON, fill templates, transform data
- See [MODULES.md - Data Processing](MODULES.md#data-processing)

### Utilities
Delays, random values, timestamps, hashing
- See [MODULES.md - Utilities](MODULES.md#utilities)

---

## Example Workflows

All examples available in `workflows/` directory:

1. **google_search.yaml** - Browser automation and web scraping
2. **api_pipeline.yaml** - Pure API workflow
3. **ai_content_summarizer.yaml** - Browser scraping + OpenAI
4. **github_to_slack.yaml** - GitHub API to Slack alerts
5. **data_scraping_to_csv.yaml** - Web scraping to CSV export
6. **daily_report_email.yaml** - API data to email report
7. **multi_channel_alert.yaml** - Broadcast to Slack/Discord/Telegram/Email
8. **openai_chat.yaml** - OpenAI GPT integration
9. **browser_screenshot.yaml** - Automated screenshot capture

**Next:** Browse [workflows/](../workflows/) directory

---

## Environment Variables

Common environment variables used across modules:

### Notifications
```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CHAT_ID=@your_channel
```

### Email
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### APIs
```bash
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
GOOGLE_AI_API_KEY=AIzaxxxxxxxxxxxx
NOTION_API_KEY=secret_xxxxxxxxxxxx
```

### Databases
```bash
POSTGRESQL_URL=postgresql://user:password@host:port/database
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=mydb
MONGODB_URL=mongodb://user:password@host:port/database
```

### Cloud Storage
```bash
AWS_ACCESS_KEY_ID=AKIAxxxxxxxxxxxx
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxx
AWS_REGION=us-east-1
```

### Google Services
```bash
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
```

**Next:** See [CLI Usage - Environment Setup](CLI.md#environment-setup)

---

## API Reference

### Module Registration

```python
from core.module_registry import register_module

@register_module(
    module_id='category.service.action',
    version='1.0.0',
    category='category',
    tags=['tag1', 'tag2'],
    label='Human Readable Label',
    label_key='i18n.key.label',
    description='What this module does',
    description_key='i18n.key.description',
    icon='IconName',
    color='#HexColor',
    params_schema={...},
    output_schema={...},
    examples=[...],
    author='Your Name',
    license='MIT'
)
async def my_module(context):
    params = context['params']
    # Implementation
    return {...}
```

**Next:** See [Writing Modules](WRITING_MODULES.md)

---

## Support and Community

- **GitHub Issues:** [Report bugs, request features](https://github.com/flytohub/flyto2/issues)
- **Discussions:** [Ask questions, share workflows](https://github.com/flytohub/flyto2/discussions)
- **Contributing:** [How to contribute](../CONTRIBUTING.md)

---

## License

MIT License - see [LICENSE](../LICENSE) file for details.

---

**Back to:** [Main README](../README.md) | [Quick Start](../README.md#quick-start)
