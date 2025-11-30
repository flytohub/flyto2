# Flyto2 Module Registry

Complete reference of all available modules organized by architecture pattern.

**Last Updated:** 2025-11-29

---

## Module Architecture

Flyto2 modules are organized into three architectural layers:

### Atomic Modules
Core building blocks that provide fundamental operations:
- Browser control and automation
- Data transformation and parsing
- Utility functions

**Characteristics:**
- No external dependencies
- Single responsibility
- Composable
- Synchronous or async

### Third-party Integrations
Modules that connect to external services and APIs:
- AI platforms
- Communication services
- Databases
- Cloud storage
- Productivity tools
- Developer platforms

**Characteristics:**
- Require API keys or credentials
- Network dependent
- Service-specific schemas
- Rate limits apply

### Composite Modules
High-level workflows combining multiple atomic or third-party modules:
- Multi-step automation patterns
- Common workflow templates
- Domain-specific solutions

**Status:** Coming in v1.1

---

## Table of Contents

### Atomic Modules
- [Browser Operations](#atomic-browser-operations)
- [Data Transformation](#atomic-data-transformation)
- [Utilities](#atomic-utilities)

### Third-party Integrations
- [AI Services](#integration-ai-services)
  - [OpenAI](#openai)
  - [Anthropic Claude](#anthropic-claude)
  - [Google Gemini](#google-gemini)
  - [Local Ollama](#local-ollama)
  - [AI Agents](#ai-agents)
- [Communication](#integration-communication)
  - [Slack](#slack)
  - [Discord](#discord)
  - [Telegram](#telegram)
  - [Email SMTP](#email-smtp)
- [Databases](#integration-databases)
  - [PostgreSQL](#postgresql)
  - [MySQL](#mysql)
  - [MongoDB](#mongodb)
- [Cloud Storage](#integration-cloud-storage)
  - [AWS S3](#aws-s3)
- [Productivity Tools](#integration-productivity-tools)
  - [Notion](#notion)
  - [Google Sheets](#google-sheets)
- [Developer Tools](#integration-developer-tools)
  - [GitHub](#github)
  - [HTTP REST](#http-rest)

---

# Atomic Modules

Fundamental building blocks with no external service dependencies.

---

## Atomic: Browser Operations

### core.browser.launch

**Description:** Launch a new browser instance with Playwright

**Category:** Atomic

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `headless` | boolean | No | `false` | Run browser in headless mode |
| `viewport` | object | No | `{width: 1280, height: 720}` | Browser viewport size |
| `browser_type` | select | No | `"chromium"` | Browser engine: chromium, firefox, webkit |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `browser` | object | Browser instance handle |
| `status` | string | Operation status |
| `message` | string | Status message |

**Example:**

```yaml
- id: launch
  module: core.browser.launch
  params:
    headless: true
    viewport:
      width: 1920
      height: 1080
```

---

### core.browser.goto

**Description:** Navigate browser to a URL

**Category:** Atomic

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `browser` | object | Yes | - | Browser instance from launch |
| `url` | string | Yes | - | Target URL |
| `wait_until` | select | No | `"load"` | Wait condition: load, domcontentloaded, networkidle |
| `timeout_ms` | number | No | `30000` | Navigation timeout in milliseconds |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Navigation status |
| `url` | string | Final URL after redirects |

**Example:**

```yaml
- id: navigate
  module: core.browser.goto
  params:
    browser: "${launch.browser}"
    url: "https://example.com"
    wait_until: "networkidle"
```

---

### core.browser.click

**Description:** Click an element on the page

**Category:** Atomic

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `browser` | object | Yes | - | Browser instance |
| `selector` | string | Yes | - | CSS selector for element |
| `wait_before_ms` | number | No | `0` | Wait before clicking |
| `timeout_ms` | number | No | `30000` | Click timeout |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Click status |
| `clicked` | boolean | Whether click succeeded |

**Example:**

```yaml
- id: click_button
  module: core.browser.click
  params:
    browser: "${launch.browser}"
    selector: "button#submit"
```

---

### core.browser.type

**Description:** Type text into an input field

**Category:** Atomic

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `browser` | object | Yes | - | Browser instance |
| `selector` | string | Yes | - | CSS selector for input |
| `text` | string | Yes | - | Text to type |
| `delay_ms` | number | No | `0` | Delay between keystrokes |
| `clear_first` | boolean | No | `true` | Clear existing text first |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Type status |
| `typed` | boolean | Whether typing succeeded |

**Example:**

```yaml
- id: search
  module: core.browser.type
  params:
    browser: "${launch.browser}"
    selector: "input[name='q']"
    text: "Flyto2 workflow automation"
```

---

### core.browser.extract

**Description:** Extract data from page elements

**Category:** Atomic

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `browser` | object | Yes | - | Browser instance |
| `selector` | string | Yes | - | CSS selector for elements |
| `limit` | number | No | `null` | Maximum elements to extract |
| `fields` | object | Yes | - | Field extraction definitions |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `data` | array | Array of extracted objects |
| `count` | number | Number of items extracted |

**Example:**

```yaml
- id: extract
  module: core.browser.extract
  params:
    browser: "${launch.browser}"
    selector: ".product"
    fields:
      name:
        selector: "h2"
        type: "text"
      price:
        selector: ".price"
        type: "text"
```

---

### core.browser.screenshot

**Description:** Take a screenshot of the page

**Category:** Atomic

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `browser` | object | Yes | - | Browser instance |
| `path` | string | Yes | - | File path to save screenshot |
| `full_page` | boolean | No | `false` | Capture full scrollable page |
| `selector` | string | No | - | CSS selector for specific element |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `path` | string | Screenshot file path |
| `status` | string | Screenshot status |

**Example:**

```yaml
- id: screenshot
  module: core.browser.screenshot
  params:
    browser: "${launch.browser}"
    path: "screenshot.png"
    full_page: true
```

---

### core.browser.close

**Description:** Close browser instance

**Category:** Atomic

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `browser` | object | Yes | - | Browser instance to close |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Close status |

**Example:**

```yaml
- id: cleanup
  module: core.browser.close
  params:
    browser: "${launch.browser}"
  on_error: "continue"
```

---

## Atomic: Data Transformation

### data.csv.read

**Description:** Read and parse CSV file

**Category:** Atomic

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | string | Yes | - | Path to CSV file |
| `has_header` | boolean | No | `true` | First row is header |
| `delimiter` | string | No | `","` | Field delimiter |
| `encoding` | string | No | `"utf-8"` | File encoding |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `data` | array | Array of row objects |
| `row_count` | number | Number of rows |
| `columns` | array | Column names |

**Example:**

```yaml
- id: read_csv
  module: data.csv.read
  params:
    file_path: "data.csv"
    has_header: true
```

---

### data.csv.write

**Description:** Write data to CSV file

**Category:** Atomic

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | string | Yes | - | Output file path |
| `data` | array | Yes | - | Array of objects to write |
| `headers` | array | No | - | Custom column headers |
| `delimiter` | string | No | `","` | Field delimiter |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `file_path` | string | Written file path |
| `row_count` | number | Rows written |

**Example:**

```yaml
- id: export_csv
  module: data.csv.write
  params:
    file_path: "output.csv"
    data: "${extract.data}"
```

---

### data.json.parse

**Description:** Parse JSON string to object

**Category:** Atomic

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `json_string` | string | Yes | - | JSON string to parse |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `data` | any | Parsed JSON object |

**Example:**

```yaml
- id: parse
  module: data.json.parse
  params:
    json_string: "${api_response.body}"
```

---

### data.json.stringify

**Description:** Convert object to JSON string

**Category:** Atomic

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `data` | any | Yes | - | Data to stringify |
| `pretty` | boolean | No | `false` | Pretty print with indentation |
| `indent` | number | No | `2` | Indentation spaces |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `json_string` | string | JSON string |

**Example:**

```yaml
- id: stringify
  module: data.json.stringify
  params:
    data: "${extract.data}"
    pretty: true
```

---

### data.text.template

**Description:** Fill text template with variables

**Category:** Atomic

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `template` | string | Yes | - | Template with placeholders |
| `variables` | object | Yes | - | Variable values |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `result` | string | Filled template |

**Example:**

```yaml
- id: format
  module: data.text.template
  params:
    template: "Hello {name}, you have {count} messages"
    variables:
      name: "Alice"
      count: 5
```

---

## Atomic: Utilities

### utility.delay

**Description:** Pause workflow execution

**Category:** Atomic

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `duration_ms` | number | No | `1000` | Duration in milliseconds |
| `duration_seconds` | number | No | - | Duration in seconds |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `waited_ms` | number | Actual wait time |

**Example:**

```yaml
- id: wait
  module: utility.delay
  params:
    duration_seconds: 2
```

---

### utility.random.number

**Description:** Generate random number

**Category:** Atomic

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `min` | number | No | `0` | Minimum value |
| `max` | number | No | `100` | Maximum value |
| `integer` | boolean | No | `true` | Return integer vs float |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `value` | number | Random number |

**Example:**

```yaml
- id: random
  module: utility.random.number
  params:
    min: 1
    max: 10
```

---

### utility.random.string

**Description:** Generate random string

**Category:** Atomic

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `length` | number | No | `16` | String length |
| `charset` | string | No | `"alphanumeric"` | Character set: alphanumeric, alpha, numeric, hex, uuid |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `value` | string | Random string |

**Example:**

```yaml
- id: generate_id
  module: utility.random.string
  params:
    charset: "uuid"
```

---

### utility.datetime.now

**Description:** Get current timestamp

**Category:** Atomic

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `format` | string | No | `"iso"` | Format: iso, unix, timestamp |
| `timezone` | string | No | `"UTC"` | Timezone name |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `datetime` | string | Formatted timestamp |
| `unix` | number | Unix timestamp |

**Example:**

```yaml
- id: timestamp
  module: utility.datetime.now
  params:
    format: "iso"
```

---

### utility.hash.md5

**Description:** Calculate MD5 hash

**Category:** Atomic

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `text` | string | Yes | - | Text to hash |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `hash` | string | MD5 hash hexadecimal |

**Example:**

```yaml
- id: hash
  module: utility.hash.md5
  params:
    text: "${params.input}"
```

---

# Third-party Integrations

Modules that connect to external services and platforms.

---

## Integration: AI Services

### OpenAI

#### ai.openai.chat

**Description:** OpenAI Chat Completion API

**Category:** Third-party Integration

**Requires:** `pip install openai`

**Authentication:** API Key

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_key` | string | No | `${env.OPENAI_API_KEY}` | OpenAI API key |
| `model` | string | No | `"gpt-4"` | Model name |
| `messages` | array | Yes | - | Chat messages |
| `temperature` | number | No | `1.0` | Sampling temperature 0-2 |
| `max_tokens` | number | No | - | Maximum tokens in response |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | AI response text |
| `usage` | object | Token usage statistics |

**Example:**

```yaml
- id: ask_gpt
  module: ai.openai.chat
  params:
    messages:
      - role: user
        content: "Explain workflow automation"
    max_tokens: 500
```

**Documentation:** https://platform.openai.com/docs/api-reference/chat

---

### Anthropic Claude

#### api.anthropic.chat

**Description:** Anthropic Claude AI chat completion

**Category:** Third-party Integration

**Requires:** `pip install aiohttp`

**Authentication:** API Key

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_key` | string | No | `${env.ANTHROPIC_API_KEY}` | Anthropic API key |
| `model` | string | No | `"claude-3-5-sonnet-20241022"` | Claude model |
| `messages` | array | Yes | - | Message objects with role and content |
| `max_tokens` | number | No | `1024` | Maximum response tokens 1-4096 |
| `temperature` | number | No | `1.0` | Sampling temperature 0-1 |
| `system` | string | No | - | System prompt |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `content` | string | Claude response text |
| `model` | string | Model used |
| `stop_reason` | string | Why model stopped |
| `usage` | object | Token usage |

**Example:**

```yaml
- id: ask_claude
  module: api.anthropic.chat
  params:
    messages:
      - role: user
        content: "Summarize this: ${article}"
    max_tokens: 500
    system: "You are a concise summarizer"
```

**Documentation:** https://docs.anthropic.com/claude/reference/messages_post

---

### Google Gemini

#### api.google_gemini.chat

**Description:** Google Gemini AI text generation

**Category:** Third-party Integration

**Requires:** `pip install aiohttp`

**Authentication:** API Key

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_key` | string | No | `${env.GOOGLE_AI_API_KEY}` | Google AI API key |
| `model` | string | No | `"gemini-1.5-pro"` | Gemini model |
| `prompt` | string | Yes | - | Text prompt |
| `temperature` | number | No | `1.0` | Randomness control 0-2 |
| `max_output_tokens` | number | No | `2048` | Max tokens 1-8192 |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `text` | string | Generated response |
| `model` | string | Model used |
| `candidates` | array | All response candidates |

**Example:**

```yaml
- id: ask_gemini
  module: api.google_gemini.chat
  params:
    prompt: "Explain quantum computing simply"
    max_output_tokens: 500
```

**Documentation:** https://ai.google.dev/api/rest/v1/models/generateContent

---

### Local Ollama

#### ai.local_ollama.chat

**Description:** Local LLM chat via Ollama (completely offline, no API key needed)

**Category:** Third-party Integration

**Requires:** Ollama installed and running (`ollama serve`)

**Authentication:** None (local only)

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | - | The message to send to local LLM |
| `model` | string | No | `"llama2"` | Ollama model (llama2, mistral, codellama, etc.) |
| `temperature` | number | No | `0.7` | Sampling temperature 0-2 |
| `system_message` | string | No | - | System role message |
| `ollama_url` | string | No | `"http://localhost:11434"` | Ollama server URL |
| `max_tokens` | number | No | - | Maximum tokens in response |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `response` | string | LLM response text |
| `model` | string | Model used |
| `context` | array | Context vector for conversation continuity |
| `total_duration` | number | Total processing time (nanoseconds) |
| `eval_count` | number | Number of tokens generated |

**Example:**

```yaml
- id: local_chat
  module: ai.local_ollama.chat
  params:
    prompt: "Explain workflow automation in 3 sentences"
    model: "llama2"
    temperature: 0.7
```

**Setup:**

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2

# Start server
ollama serve
```

**Documentation:** https://ollama.ai/

---

### AI Agents

#### agent.autonomous

**Description:** Self-directed AI agent with memory and goal-oriented behavior

**Category:** Third-party Integration

**Requires:** OpenAI library (`pip install openai`) OR Ollama (local)

**Authentication:** API Key (for OpenAI) or None (for Ollama)

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `goal` | string | Yes | - | The goal for the agent to achieve |
| `context` | string | No | - | Additional context or constraints |
| `max_iterations` | number | No | `5` | Maximum reasoning steps (1-20) |
| `llm_provider` | string | No | `"openai"` | LLM provider: "openai" or "ollama" |
| `model` | string | No | `"gpt-4-turbo-preview"` | Model name (gpt-4, llama2, mistral, etc.) |
| `ollama_url` | string | No | `"http://localhost:11434"` | Ollama URL (for ollama provider) |
| `temperature` | number | No | `0.7` | Creativity level 0-2 |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `result` | string | Final result/answer |
| `thoughts` | array | Array of reasoning steps |
| `iterations` | number | Number of iterations used |
| `goal_achieved` | boolean | Whether goal was achieved |

**Example (Cloud):**

```yaml
- id: research_agent
  module: agent.autonomous
  params:
    llm_provider: "openai"
    model: "gpt-4"
    goal: "Research the top 3 trends in AI for 2025"
    max_iterations: 5
```

**Example (Local):**

```yaml
- id: local_agent
  module: agent.autonomous
  params:
    llm_provider: "ollama"
    model: "mistral"
    ollama_url: "http://localhost:11434"
    goal: "Analyze pros and cons of microservices architecture"
    max_iterations: 5
```

**Documentation:** [Local AI Agent Guide](LOCAL_AI_AGENT.md)

---

#### agent.chain

**Description:** Sequential AI processing chain with multiple steps

**Category:** Third-party Integration

**Requires:** OpenAI library (`pip install openai`) OR Ollama (local)

**Authentication:** API Key (for OpenAI) or None (for Ollama)

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `input` | string | Yes | - | Initial input for the chain |
| `chain_steps` | array | Yes | - | Array of prompt templates (use {input}, {previous}) |
| `llm_provider` | string | No | `"openai"` | LLM provider: "openai" or "ollama" |
| `model` | string | No | `"gpt-3.5-turbo"` | Model name |
| `ollama_url` | string | No | `"http://localhost:11434"` | Ollama URL (for ollama provider) |
| `temperature` | number | No | `0.7` | Creativity level 0-2 |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `result` | string | Final output from last step |
| `intermediate_results` | array | Outputs from each step |
| `steps_completed` | number | Number of steps executed |

**Example (Cloud):**

```yaml
- id: content_pipeline
  module: agent.chain
  params:
    llm_provider: "openai"
    model: "gpt-4"
    input: "AI in healthcare"
    chain_steps:
      - "Generate 5 blog post ideas about: {input}"
      - "Write outline for first idea: {previous}"
      - "Write introduction paragraph: {previous}"
```

**Example (Local):**

```yaml
- id: local_pipeline
  module: agent.chain
  params:
    llm_provider: "ollama"
    model: "llama2"
    input: "Docker best practices"
    chain_steps:
      - "List 5 best practices for: {input}"
      - "Explain the first practice in detail: {previous}"
      - "Provide a code example: {previous}"
```

**Documentation:** [Local AI Agent Guide](LOCAL_AI_AGENT.md)

---

## Integration: Communication

### Slack

#### notification.slack.send_message

**Description:** Send message to Slack channel via webhook

**Category:** Third-party Integration

**Requires:** `pip install aiohttp`

**Authentication:** Webhook URL

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `webhook_url` | string | No | `${env.SLACK_WEBHOOK_URL}` | Slack webhook URL |
| `text` | string | Yes | - | Message text |
| `channel` | string | No | - | Override default channel |
| `username` | string | No | - | Bot display name |
| `icon_emoji` | string | No | - | Bot icon emoji |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Send status |
| `sent` | boolean | Whether message sent |
| `message` | string | Status message |

**Example:**

```yaml
- id: notify
  module: notification.slack.send_message
  params:
    text: "Workflow completed successfully"
    channel: "#alerts"
```

**Documentation:** https://api.slack.com/messaging/webhooks

---

### Discord

#### notification.discord.send_message

**Description:** Send message to Discord channel via webhook

**Category:** Third-party Integration

**Requires:** `pip install aiohttp`

**Authentication:** Webhook URL

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `webhook_url` | string | No | `${env.DISCORD_WEBHOOK_URL}` | Discord webhook URL |
| `content` | string | Yes | - | Message content |
| `username` | string | No | - | Bot username |
| `avatar_url` | string | No | - | Bot avatar URL |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Send status |
| `sent` | boolean | Whether message sent |

**Example:**

```yaml
- id: notify_discord
  module: notification.discord.send_message
  params:
    content: "Alert: High CPU usage detected"
```

**Documentation:** https://discord.com/developers/docs/resources/webhook

---

### Telegram

#### notification.telegram.send_message

**Description:** Send message via Telegram bot

**Category:** Third-party Integration

**Requires:** `pip install aiohttp`

**Authentication:** Bot Token

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `bot_token` | string | No | `${env.TELEGRAM_BOT_TOKEN}` | Telegram bot token |
| `chat_id` | string | No | `${env.TELEGRAM_CHAT_ID}` | Chat or channel ID |
| `text` | string | Yes | - | Message text |
| `parse_mode` | string | No | - | Formatting: Markdown, HTML |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Send status |
| `sent` | boolean | Whether message sent |
| `message_id` | number | Telegram message ID |

**Example:**

```yaml
- id: notify_telegram
  module: notification.telegram.send_message
  params:
    text: "Daily report ready"
    parse_mode: "Markdown"
```

**Documentation:** https://core.telegram.org/bots/api

---

### Email SMTP

#### notification.email.send

**Description:** Send email via SMTP server

**Category:** Third-party Integration

**Requires:** Built-in

**Authentication:** SMTP Credentials

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `smtp_server` | string | No | `${env.SMTP_SERVER}` | SMTP server hostname |
| `smtp_port` | number | No | `587` | SMTP port |
| `username` | string | No | `${env.SMTP_USERNAME}` | SMTP username |
| `password` | string | No | `${env.SMTP_PASSWORD}` | SMTP password |
| `from_email` | string | Yes | - | Sender email |
| `to_email` | string | Yes | - | Recipient email |
| `subject` | string | Yes | - | Email subject |
| `body` | string | Yes | - | Email body |
| `html` | boolean | No | `false` | Send as HTML |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Send status |
| `sent` | boolean | Whether email sent |

**Example:**

```yaml
- id: send_email
  module: notification.email.send
  params:
    from_email: "alerts@company.com"
    to_email: "team@company.com"
    subject: "Daily Report"
    body: "${report_content}"
```

---

## Integration: Databases

### PostgreSQL

#### db.postgresql.query

**Description:** Execute SQL query on PostgreSQL database

**Category:** Third-party Integration

**Requires:** `pip install asyncpg`

**Authentication:** Connection String

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `connection_string` | string | No | `${env.POSTGRESQL_URL}` | PostgreSQL URL |
| `query` | string | Yes | - | SQL query |
| `params` | array | No | - | Query parameters use dollar1 dollar2 |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `rows` | array | Result rows as objects |
| `row_count` | number | Rows returned |
| `columns` | array | Column names |

**Example:**

```yaml
- id: fetch_users
  module: db.postgresql.query
  params:
    query: "SELECT * FROM users WHERE active = true LIMIT 10"
```

**Documentation:** https://www.postgresql.org/docs/

---

### MySQL

#### db.mysql.query

**Description:** Execute SQL query on MySQL database

**Category:** Third-party Integration

**Requires:** `pip install aiomysql`

**Authentication:** Host Credentials

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `host` | string | No | `${env.MYSQL_HOST}` | MySQL host |
| `port` | number | No | `3306` | MySQL port |
| `user` | string | No | `${env.MYSQL_USER}` | MySQL user |
| `password` | string | No | `${env.MYSQL_PASSWORD}` | MySQL password |
| `database` | string | No | `${env.MYSQL_DATABASE}` | Database name |
| `query` | string | Yes | - | SQL query |
| `params` | array | No | - | Query parameters |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `rows` | array | Result rows |
| `row_count` | number | Rows returned |
| `columns` | array | Column names |

**Example:**

```yaml
- id: fetch_products
  module: db.mysql.query
  params:
    query: "SELECT id, name, price FROM products WHERE stock > 0"
```

**Documentation:** https://dev.mysql.com/doc/

---

### MongoDB

#### db.mongodb.find

**Description:** Query documents from MongoDB collection

**Category:** Third-party Integration

**Requires:** `pip install motor`

**Authentication:** Connection String

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `connection_string` | string | No | `${env.MONGODB_URL}` | MongoDB URL |
| `database` | string | Yes | - | Database name |
| `collection` | string | Yes | - | Collection name |
| `filter` | object | No | `{}` | Query filter |
| `projection` | object | No | - | Fields to return |
| `limit` | number | No | `100` | Max documents 1-10000 |
| `sort` | object | No | - | Sort order |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `documents` | array | Matching documents |
| `count` | number | Documents returned |

**Example:**

```yaml
- id: fetch_orders
  module: db.mongodb.find
  params:
    database: "myapp"
    collection: "orders"
    filter: {status: "completed"}
    limit: 50
```

**Documentation:** https://www.mongodb.com/docs/

---

#### db.mongodb.insert

**Description:** Insert documents into MongoDB collection

**Category:** Third-party Integration

**Requires:** `pip install motor`

**Authentication:** Connection String

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `connection_string` | string | No | `${env.MONGODB_URL}` | MongoDB URL |
| `database` | string | Yes | - | Database name |
| `collection` | string | Yes | - | Collection name |
| `document` | object | No | - | Single document |
| `documents` | array | No | - | Multiple documents |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `inserted_count` | number | Documents inserted |
| `inserted_ids` | array | Document IDs |

**Example:**

```yaml
- id: insert_log
  module: db.mongodb.insert
  params:
    database: "logs"
    collection: "events"
    document:
      event: "workflow_completed"
      timestamp: "${timestamp}"
```

**Documentation:** https://www.mongodb.com/docs/

---

## Integration: Cloud Storage

### AWS S3

#### cloud.aws_s3.upload

**Description:** Upload file to AWS S3 bucket

**Category:** Third-party Integration

**Requires:** `pip install aioboto3`

**Authentication:** AWS Credentials

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `aws_access_key_id` | string | No | `${env.AWS_ACCESS_KEY_ID}` | AWS access key |
| `aws_secret_access_key` | string | No | `${env.AWS_SECRET_ACCESS_KEY}` | AWS secret key |
| `region` | string | No | `${env.AWS_REGION}` | AWS region |
| `bucket` | string | Yes | - | S3 bucket name |
| `key` | string | Yes | - | Object key path |
| `file_path` | string | No | - | Local file path |
| `content` | string | No | - | File content |
| `content_type` | string | No | - | MIME type |
| `acl` | string | No | `"private"` | Access control |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | S3 object URL |
| `bucket` | string | Bucket name |
| `key` | string | Object key |
| `etag` | string | Object ETag |

**Example:**

```yaml
- id: upload
  module: cloud.aws_s3.upload
  params:
    bucket: "backups"
    key: "daily-${timestamp}.csv"
    content: "${csv_data}"
```

**Documentation:** https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html

---

#### cloud.aws_s3.download

**Description:** Download file from AWS S3 bucket

**Category:** Third-party Integration

**Requires:** `pip install aioboto3`

**Authentication:** AWS Credentials

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `aws_access_key_id` | string | No | `${env.AWS_ACCESS_KEY_ID}` | AWS access key |
| `aws_secret_access_key` | string | No | `${env.AWS_SECRET_ACCESS_KEY}` | AWS secret key |
| `region` | string | No | `${env.AWS_REGION}` | AWS region |
| `bucket` | string | Yes | - | S3 bucket name |
| `key` | string | Yes | - | Object key path |
| `file_path` | string | No | - | Save to file path |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `content` | string | File content |
| `file_path` | string | Saved file path |
| `size` | number | File size bytes |
| `content_type` | string | MIME type |

**Example:**

```yaml
- id: download
  module: cloud.aws_s3.download
  params:
    bucket: "configs"
    key: "app-config.json"
```

**Documentation:** https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html

---

## Integration: Productivity Tools

### Notion

#### api.notion.create_page

**Description:** Create page in Notion database

**Category:** Third-party Integration

**Requires:** `pip install aiohttp`

**Authentication:** Integration Token

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_key` | string | No | `${env.NOTION_API_KEY}` | Notion token |
| `database_id` | string | Yes | - | Database ID |
| `properties` | object | Yes | - | Page properties |
| `content` | array | No | - | Page content blocks |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `page_id` | string | Created page ID |
| `url` | string | Page URL |
| `created_time` | string | Creation timestamp |

**Example:**

```yaml
- id: create_task
  module: api.notion.create_page
  params:
    database_id: "abc123"
    properties:
      Name:
        title:
          - text:
              content: "New Task"
```

**Documentation:** https://developers.notion.com/reference/post-page

---

#### api.notion.query_database

**Description:** Query Notion database with filters

**Category:** Third-party Integration

**Requires:** `pip install aiohttp`

**Authentication:** Integration Token

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_key` | string | No | `${env.NOTION_API_KEY}` | Notion token |
| `database_id` | string | Yes | - | Database ID |
| `filter` | object | No | - | Query filter |
| `sorts` | array | No | - | Sort order |
| `page_size` | number | No | `100` | Results limit 1-100 |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `results` | array | Page objects |
| `count` | number | Results returned |
| `has_more` | boolean | More results available |

**Example:**

```yaml
- id: query_tasks
  module: api.notion.query_database
  params:
    database_id: "abc123"
    filter:
      property: "Status"
      select:
        equals: "Active"
```

**Documentation:** https://developers.notion.com/reference/post-database-query

---

### Google Sheets

#### api.google_sheets.read

**Description:** Read data from Google Sheets

**Category:** Third-party Integration

**Requires:** `pip install google-api-python-client google-auth`

**Authentication:** Service Account

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `credentials` | object | No | `${env.GOOGLE_CREDENTIALS_JSON}` | Service account JSON |
| `spreadsheet_id` | string | Yes | - | Spreadsheet ID from URL |
| `range` | string | Yes | - | A1 notation range |
| `include_header` | boolean | No | `true` | Parse first row as headers |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `values` | array | Raw row values |
| `data` | array | Row objects with headers |
| `row_count` | number | Rows read |

**Example:**

```yaml
- id: read_sheet
  module: api.google_sheets.read
  params:
    spreadsheet_id: "1BxiMVs0XRA5..."
    range: "Sheet1!A1:D100"
```

**Documentation:** https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/get

---

#### api.google_sheets.write

**Description:** Write data to Google Sheets

**Category:** Third-party Integration

**Requires:** `pip install google-api-python-client google-auth`

**Authentication:** Service Account

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `credentials` | object | No | `${env.GOOGLE_CREDENTIALS_JSON}` | Service account JSON |
| `spreadsheet_id` | string | Yes | - | Spreadsheet ID |
| `range` | string | Yes | - | A1 notation range |
| `values` | array | Yes | - | Array of rows |
| `value_input_option` | string | No | `"USER_ENTERED"` | Input mode |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `updated_range` | string | Range updated |
| `updated_rows` | number | Rows updated |
| `updated_columns` | number | Columns updated |
| `updated_cells` | number | Cells updated |

**Example:**

```yaml
- id: write_data
  module: api.google_sheets.write
  params:
    spreadsheet_id: "1BxiMVs0XRA5..."
    range: "Sheet1!A1"
    values:
      - ["Name", "Email"]
      - ["John", "john@example.com"]
```

**Documentation:** https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/update

---

## Integration: Developer Tools

### GitHub

#### api.github.get_repo

**Description:** Get GitHub repository information

**Category:** Third-party Integration

**Requires:** `pip install aiohttp`

**Authentication:** Token

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `owner` | string | Yes | - | Repository owner |
| `repo` | string | Yes | - | Repository name |
| `token` | string | No | `${env.GITHUB_TOKEN}` | GitHub token |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Repository name |
| `description` | string | Repository description |
| `stars` | number | Star count |
| `forks` | number | Fork count |
| `url` | string | Repository URL |

**Example:**

```yaml
- id: get_repo
  module: api.github.get_repo
  params:
    owner: "facebook"
    repo: "react"
```

**Documentation:** https://docs.github.com/rest/repos/repos

---

#### api.github.list_issues

**Description:** List GitHub repository issues

**Category:** Third-party Integration

**Requires:** `pip install aiohttp`

**Authentication:** Token

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `owner` | string | Yes | - | Repository owner |
| `repo` | string | Yes | - | Repository name |
| `token` | string | No | `${env.GITHUB_TOKEN}` | GitHub token |
| `state` | string | No | `"open"` | Issue state: open, closed, all |
| `labels` | string | No | - | Comma separated labels |
| `per_page` | number | No | `30` | Results per page 1-100 |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `issues` | array | Issue objects |
| `count` | number | Issues returned |

**Example:**

```yaml
- id: list_bugs
  module: api.github.list_issues
  params:
    owner: "facebook"
    repo: "react"
    state: "open"
    labels: "bug"
```

**Documentation:** https://docs.github.com/rest/issues/issues

---

#### api.github.create_issue

**Description:** Create GitHub issue

**Category:** Third-party Integration

**Requires:** `pip install aiohttp`

**Authentication:** Token

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `owner` | string | Yes | - | Repository owner |
| `repo` | string | Yes | - | Repository name |
| `token` | string | No | `${env.GITHUB_TOKEN}` | GitHub token |
| `title` | string | Yes | - | Issue title |
| `body` | string | No | - | Issue body |
| `labels` | array | No | - | Issue labels |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `issue_number` | number | Created issue number |
| `url` | string | Issue URL |
| `created_at` | string | Creation timestamp |

**Example:**

```yaml
- id: create_bug
  module: api.github.create_issue
  params:
    owner: "myorg"
    repo: "myrepo"
    title: "Bug found in workflow"
    body: "Details here"
    labels: ["bug", "high-priority"]
```

**Documentation:** https://docs.github.com/rest/issues/issues

---

### HTTP REST

#### api.http.get

**Description:** Make HTTP GET request

**Category:** Third-party Integration

**Requires:** `pip install aiohttp`

**Authentication:** Flexible

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | Yes | - | Request URL |
| `headers` | object | No | - | HTTP headers |
| `params` | object | No | - | Query parameters |
| `timeout_ms` | number | No | `30000` | Request timeout |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | number | HTTP status code |
| `body` | string | Response body |
| `json` | object | Parsed JSON if applicable |
| `headers` | object | Response headers |

**Example:**

```yaml
- id: fetch_api
  module: api.http.get
  params:
    url: "https://api.example.com/data"
    headers:
      Authorization: "Bearer ${env.API_TOKEN}"
```

---

#### api.http.post

**Description:** Make HTTP POST request

**Category:** Third-party Integration

**Requires:** `pip install aiohttp`

**Authentication:** Flexible

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | Yes | - | Request URL |
| `headers` | object | No | - | HTTP headers |
| `body` | string/object | No | - | Request body |
| `json` | object | No | - | JSON body auto serialized |
| `timeout_ms` | number | No | `30000` | Request timeout |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | number | HTTP status code |
| `body` | string | Response body |
| `json` | object | Parsed JSON if applicable |
| `headers` | object | Response headers |

**Example:**

```yaml
- id: post_data
  module: api.http.post
  params:
    url: "https://api.example.com/submit"
    json:
      name: "John"
      email: "john@example.com"
```

---

# Composite Modules

Coming in v1.1

High-level workflow templates combining multiple modules:
- Web scraping to database pipeline
- Multi-channel notification broadcast
- API data transformation and export
- Scheduled report generation

---

## Module Development

Want to create your own module? See [WRITING_MODULES.md](WRITING_MODULES.md) for a complete guide.

---

## Questions

- [Open an issue](https://github.com/flytohub/flyto2/issues)
- [View DSL specification](DSL.md)
- [See example workflows](../workflows/)
