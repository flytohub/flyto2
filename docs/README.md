# Flyto2 Documentation

Complete documentation for the Flyto2 workflow automation engine.

---

## Quick Navigation

### Getting Started
- [Quick Start Guide](../README.md#quick-start) - 3-step installation and first workflow
- [Contributor Quickstart](../QUICKSTART.md) - 5-minute guide for new contributors
- [CLI Usage](CLI.md) - Command-line interface reference
- [DSL Specification](DSL.md) - Complete YAML workflow syntax
- [Parameter Best Practices](PARAMETER_BEST_PRACTICES.md) - Design flexible, reusable workflows

### Core References
- [Module Registry](MODULES.md) - All 102 available modules with parameters
- [Architecture](ARCHITECTURE.md) - System design and engine internals
- [Project Structure](PROJECT_STRUCTURE.md) - Directory organization
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute

### Module Development
- [Module Specification](MODULE_SPECIFICATION.md) - Complete module specification
- [Module Quick Reference](MODULE_QUICK_REFERENCE.md) - Fast lookup guide
- [Writing Modules](WRITING_MODULES.md) - Create custom modules
- [Phase 2 Features](MODULE_PHASE2_FEATURES.md) - Execution control & security

### UI Integration
- [UI Builder Integration](UI_BUILDER_INTEGRATION.md) - For UI developers
- [UI Module Integration](UI_MODULE_INTEGRATION.md) - Module UI components
- [Phase 2 UI Integration](PHASE2_UI_INTEGRATION.md) - Phase 2 features in UI

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

Comprehensive list of all 56 available modules organized by category:
- Browser Automation (launch, goto, click, type, extract, screenshot, press, find, wait)
- HTTP and APIs (GET, POST, GitHub, Slack, Discord, Telegram, Email, Google Search)
- AI Services (Anthropic Claude, Google Gemini)
- Databases (PostgreSQL, MySQL, MongoDB)
- Cloud Storage (AWS S3)
- Productivity (Notion pages/databases, Google Sheets)
- Data Processing (CSV read/write, JSON parse/stringify, text templates)
- Utilities (delay, random numbers/strings, datetime, hash, arrays, strings, math)

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
python -m src.cli.main workflows/google_search.yaml

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
python -m src.cli.main workflow.yaml --log-level=DEBUG

# Validate without running
python -m src.cli.main workflow.yaml --dry-run
```

**Next:** See [CLI Usage - Debugging](CLI.md#debugging)

---

## Module Architecture

Flyto2 modules are organized into three architectural layers:

### Atomic Modules
Core building blocks with no external dependencies:
- **Browser Operations** - Launch, navigate, click, type, extract, screenshot
- **Data Transformation** - CSV read/write, JSON parse/stringify, templates
- **Utilities** - Delay, random, datetime, hash

**Characteristics:** Single responsibility, composable, no API keys required

See [MODULES.md - Atomic Modules](MODULES.md#atomic-modules)

### Third-party Integrations
Connect to external services and platforms:
- **AI Services** - OpenAI, Anthropic Claude, Google Gemini
- **Communication** - Slack, Discord, Telegram, Email SMTP
- **Databases** - PostgreSQL, MySQL, MongoDB
- **Cloud Storage** - AWS S3
- **Productivity Tools** - Notion, Google Sheets
- **Developer Tools** - GitHub, HTTP REST

**Characteristics:** Require API keys, network dependent, rate limits apply

See [MODULES.md - Third-party Integrations](MODULES.md#third-party-integrations)

### Composite Modules
High-level workflow templates combining multiple modules:
- Web scraping to database pipeline
- Multi-channel notification broadcast
- API data transformation and export
- Scheduled report generation

**Status:** Coming in v1.1

---

## Quick Module Reference

### Atomic: Browser Operations
```yaml
core.browser.launch        # Launch browser instance
core.browser.goto          # Navigate to URL
core.browser.click         # Click element
core.browser.type          # Type text in input
core.browser.extract       # Extract data from page
core.browser.screenshot    # Take screenshot
core.browser.close         # Close browser
```

### Atomic: Data Transformation
```yaml
data.csv.read             # Read CSV file
data.csv.write            # Write CSV file
data.json.parse           # Parse JSON string
data.json.stringify       # Convert to JSON
data.text.template        # Fill text template
```

### Atomic: Utilities
```yaml
utility.delay             # Pause execution
utility.random.number     # Generate random number
utility.random.string     # Generate random string
utility.datetime.now      # Get current timestamp
utility.hash.md5          # Calculate MD5 hash
```

### Integration: AI Services
```yaml
ai.openai.chat            # OpenAI GPT chat
api.anthropic.chat        # Anthropic Claude chat
api.google_gemini.chat    # Google Gemini chat
```

### Integration: Communication
```yaml
notification.slack.send_message      # Slack message
notification.discord.send_message    # Discord message
notification.telegram.send_message   # Telegram message
notification.email.send              # Email via SMTP
```

### Integration: Databases
```yaml
db.postgresql.query       # PostgreSQL SQL query
db.mysql.query            # MySQL SQL query
db.mongodb.find           # MongoDB find documents
db.mongodb.insert         # MongoDB insert documents
```

### Integration: Cloud Storage
```yaml
cloud.aws_s3.upload       # Upload to S3
cloud.aws_s3.download     # Download from S3
```

### Integration: Productivity Tools
```yaml
api.notion.create_page    # Create Notion page
api.notion.query_database # Query Notion database
api.google_sheets.read    # Read Google Sheets
api.google_sheets.write   # Write Google Sheets
```

### Integration: Developer Tools
```yaml
api.github.get_repo       # Get GitHub repo info
api.github.list_issues    # List GitHub issues
api.github.create_issue   # Create GitHub issue
api.http.get              # HTTP GET request
api.http.post             # HTTP POST request
```

---

## Example Workflows

All examples available in `workflows/` directory:

1. **google_search.yaml** - Browser automation and web scraping
2. **api_pipeline.yaml** - Pure API workflow
3. **ai_content_summarizer.yaml** - Browser scraping + AI
4. **github_to_slack.yaml** - GitHub API to Slack alerts
5. **data_scraping_to_csv.yaml** - Web scraping to CSV export
6. **daily_report_email.yaml** - API data to email report
7. **multi_channel_alert.yaml** - Broadcast to Slack/Discord/Telegram/Email
8. **openai_chat.yaml** - AI chat interaction (Anthropic Claude)
9. **browser_screenshot.yaml** - Automated screenshot capture
10. **authenticated_scraping.yaml** - Web scraping with authentication
11. **pagination_scraper.yaml** - Multi-page scraping with pagination
12. **test_simple.yaml** - Simple workflow for testing

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
