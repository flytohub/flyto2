# Flyto2 Module Registry

Complete reference of all available modules, their parameters, and return values.

**Last Updated:** 2025-11-29

---

## Table of Contents

- [Browser Automation](#browser-automation)
- [HTTP/API Operations](#httpapi-operations)
- [Notifications](#notifications)
- [AI Services](#ai-services)
- [Databases](#databases)
- [Cloud Storage](#cloud-storage)
- [Productivity](#productivity)
- [Data Processing](#data-processing)
- [Utility](#utility)

---

## Browser Automation

### core.browser.launch

**Description:** Launch a new browser instance with Playwright

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `headless` | boolean | No | `false` | Run browser in headless mode (no UI) |
| `viewport` | object | No | `{width: 1280, height: 720}` | Browser viewport size |
| `browser_type` | select | No | `"chromium"` | Browser type: chromium, firefox, webkit |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `browser` | object | Browser instance handle (for other modules) |
| `status` | string | "success" or "error" |
| `message` | string | Status message |

**Example:**

```yaml
- id: launch
  module: core.browser.launch
  params:
    headless: true
```

---

### core.browser.goto

**Description:** Navigate browser to a URL

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `browser` | object | Yes | - | Browser instance from launch step |
| `url` | string | Yes | - | Target URL |
| `wait_until` | select | No | `"load"` | Wait condition: load, domcontentloaded, networkidle |
| `timeout_ms` | number | No | `30000` | Navigation timeout |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | "success" or "error" |
| `url` | string | Final URL (after redirects) |

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

### core.browser.wait

**Description:** Wait for element or condition

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `browser` | object | Yes | - | Browser instance |
| `selector` | string | Yes | - | CSS selector to wait for |
| `state` | select | No | `"visible"` | Element state: visible, attached, hidden |
| `timeout_ms` | number | No | `30000` | Wait timeout |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | "success" or "error" |
| `found` | boolean | Whether element was found |

**Example:**

```yaml
- id: wait_for_results
  module: core.browser.wait
  params:
    browser: "${launch.browser}"
    selector: ".search-results"
    timeout_ms: 10000
```

---

### core.browser.type

**Description:** Type text into an input element

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `browser` | object | Yes | - | Browser instance |
| `selector` | string | Yes | - | CSS selector for input element |
| `text` | string | Yes | - | Text to type |
| `delay` | number | No | `0` | Delay between keystrokes (ms) |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | "success" or "error" |

**Example:**

```yaml
- id: enter_keyword
  module: core.browser.type
  params:
    browser: "${launch.browser}"
    selector: 'input[name="q"]'
    text: "${params.keyword}"
```

---

### core.browser.click

**Description:** Click an element

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `browser` | object | Yes | - | Browser instance |
| `selector` | string | Yes | - | CSS selector for element to click |
| `button` | select | No | `"left"` | Mouse button: left, right, middle |
| `click_count` | number | No | `1` | Number of clicks |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | "success" or "error" |

---

### core.browser.extract

**Description:** Extract data from page elements

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `browser` | object | Yes | - | Browser instance |
| `selector` | string | Yes | - | CSS selector for elements |
| `limit` | number | No | `null` | Maximum number of elements |
| `fields` | object | Yes | - | Field extraction definitions |

**Field Definition:**

```yaml
fields:
  field_name:
    selector: "css selector"
    type: "text"           # text, attribute, html
    attribute: "href"      # Required if type=attribute
```

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `data` | array | Array of extracted objects |
| `count` | number | Number of items extracted |
| `status` | string | "success" or "error" |

**Example:**

```yaml
- id: extract_results
  module: core.browser.extract
  params:
    browser: "${launch.browser}"
    selector: ".result"
    limit: 10
    fields:
      title:
        selector: "h2"
        type: "text"
      url:
        selector: "a"
        type: "attribute"
        attribute: "href"
```

---

### core.browser.screenshot

**Description:** Take a screenshot

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `browser` | object | Yes | - | Browser instance |
| `path` | string | Yes | - | Output file path |
| `full_page` | boolean | No | `false` | Capture full page |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `filepath` | string | Path to saved screenshot |
| `status` | string | "success" or "error" |

---

### core.browser.close

**Description:** Close browser instance

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `browser` | object | Yes | - | Browser instance to close |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | "success" or "error" |

---

## HTTP/API Operations

### api.http.get

**Description:** Send HTTP GET request

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | Yes | - | Target URL |
| `headers` | object | No | `{}` | HTTP headers |
| `params` | object | No | `{}` | Query parameters |
| `timeout` | number | No | `30` | Timeout in seconds |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `status_code` | number | HTTP status code |
| `headers` | object | Response headers |
| `body` | string | Response body text |
| `json` | object | Parsed JSON (if Content-Type is JSON) |

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

### api.http.post

**Description:** Send HTTP POST request

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | Yes | - | Target URL |
| `headers` | object | No | `{}` | HTTP headers |
| `body` | string | No | - | Request body (text) |
| `json` | object | No | - | Request body (JSON) |
| `timeout` | number | No | `30` | Timeout in seconds |

**Returns:**

Same as `api.http.get`

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

### api.github.get_repo

**Description:** Get GitHub repository information

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `owner` | string | Yes | - | Repository owner (username or org) |
| `repo` | string | Yes | - | Repository name |
| `token` | string | No | `${env.GITHUB_TOKEN}` | GitHub access token |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Repository name |
| `full_name` | string | Full name (owner/repo) |
| `description` | string | Repository description |
| `stars` | number | Star count |
| `forks` | number | Fork count |
| `url` | string | Repository URL |

---

### api.github.list_issues

**Description:** List GitHub repository issues

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `owner` | string | Yes | - | Repository owner |
| `repo` | string | Yes | - | Repository name |
| `state` | select | No | `"open"` | Filter: open, closed, all |
| `labels` | string | No | - | Filter by labels (comma-separated) |
| `limit` | number | No | `30` | Maximum issues to fetch |
| `token` | string | No | `${env.GITHUB_TOKEN}` | GitHub access token |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `issues` | array | Array of issue objects |
| `count` | number | Number of issues returned |

---

### api.github.create_issue

**Description:** Create a new GitHub issue

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `owner` | string | Yes | - | Repository owner |
| `repo` | string | Yes | - | Repository name |
| `title` | string | Yes | - | Issue title |
| `body` | string | No | `""` | Issue description (Markdown) |
| `labels` | array | No | `[]` | Issue labels |
| `assignees` | array | No | `[]` | GitHub usernames to assign |
| `token` | string | Yes | `${env.GITHUB_TOKEN}` | GitHub access token |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `number` | number | Issue number |
| `url` | string | Issue URL |

---

## Notifications

### notification.slack.send_message

**Description:** Send message to Slack via webhook

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `webhook_url` | string | No | `${env.SLACK_WEBHOOK_URL}` | Slack webhook URL |
| `text` | string | Yes | - | Message text |
| `channel` | string | No | - | Override default channel |
| `username` | string | No | - | Override bot username |
| `icon_emoji` | string | No | - | Bot icon emoji |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `sent` | boolean | Whether message was sent |
| `status` | string | "success" or "error" |
| `message` | string | Status message |

**Example:**

```yaml
- id: notify
  module: notification.slack.send_message
  params:
    text: "Workflow completed successfully!"
    channel: "#alerts"
    icon_emoji: ":white_check_mark:"
```

---

### notification.discord.send_message

**Description:** Send message to Discord via webhook

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `webhook_url` | string | No | `${env.DISCORD_WEBHOOK_URL}` | Discord webhook URL |
| `content` | string | Yes | - | Message content |
| `username` | string | No | - | Override bot username |
| `avatar_url` | string | No | - | Bot avatar URL |

**Returns:**

Same as Slack module

---

### notification.telegram.send_message

**Description:** Send message via Telegram Bot API

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `bot_token` | string | No | `${env.TELEGRAM_BOT_TOKEN}` | Bot token from @BotFather |
| `chat_id` | string | Yes | - | Chat ID or channel username |
| `text` | string | Yes | - | Message text |
| `parse_mode` | select | No | `"Markdown"` | Format: Markdown, HTML, None |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `sent` | boolean | Whether message was sent |
| `message_id` | number | Telegram message ID |

---

### notification.email.send

**Description:** Send email via SMTP

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `smtp_server` | string | Yes | - | SMTP server hostname |
| `smtp_port` | number | No | `587` | SMTP port |
| `username` | string | Yes | - | SMTP username |
| `password` | string | Yes | - | SMTP password |
| `from_email` | string | Yes | - | Sender email |
| `to_email` | string | Yes | - | Recipient email |
| `subject` | string | Yes | - | Email subject |
| `body` | string | Yes | - | Email body |
| `html` | boolean | No | `false` | Send as HTML |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `sent` | boolean | Whether email was sent |

---

## Data Processing

### data.csv.read

**Description:** Read and parse CSV file

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | string | Yes | - | Path to CSV file |
| `delimiter` | string | No | `","` | CSV delimiter |
| `encoding` | string | No | `"utf-8"` | File encoding |
| `skip_header` | boolean | No | `false` | Skip first row |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `data` | array | Array of row objects |
| `rows` | number | Number of rows |
| `columns` | array | Column names |

---

### data.csv.write

**Description:** Write array to CSV file

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | string | Yes | - | Output file path |
| `data` | array | Yes | - | Array of objects to write |
| `delimiter` | string | No | `","` | CSV delimiter |
| `encoding` | string | No | `"utf-8"` | File encoding |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `file_path` | string | Path to saved file |
| `rows_written` | number | Number of rows written |

---

### data.json.parse

**Description:** Parse JSON string to object

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `json_string` | string | Yes | - | JSON string to parse |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `data` | object/array | Parsed JSON data |

---

### data.json.stringify

**Description:** Convert object to JSON string

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `data` | object/array | Yes | - | Data to stringify |
| `pretty` | boolean | No | `false` | Format with indentation |
| `indent` | number | No | `2` | Indent size (if pretty=true) |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `json` | string | JSON string |

---

### data.text.template

**Description:** Fill text template with variables

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `template` | string | Yes | - | Template with `{variable}` placeholders |
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
  # Returns: { result: "Hello Alice, you have 5 messages" }
```

---

## Utility

### utility.delay

**Description:** Pause workflow execution

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `duration_ms` | number | No | `1000` | Duration in milliseconds |
| `duration_seconds` | number | No | - | Duration in seconds |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `waited_ms` | number | Actual wait time |

---

### utility.random.number

**Description:** Generate random number

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `min` | number | No | `0` | Minimum value (inclusive) |
| `max` | number | No | `100` | Maximum value (inclusive) |
| `decimals` | number | No | `0` | Decimal places (0=integer) |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `value` | number | Random number |

---

### utility.random.string

**Description:** Generate random string or UUID

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `length` | number | No | `16` | String length |
| `charset` | select | No | `"alphanumeric"` | Character set: alphanumeric, letters, lowercase, uppercase, numbers, hex, uuid |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `value` | string | Random string |

---

### utility.datetime.now

**Description:** Get current date/time

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `format` | select | No | `"iso"` | Format: iso, unix, unix_ms, date, time, custom |
| `custom_format` | string | No | - | Python strftime format (if format=custom) |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `datetime` | string | Formatted date/time |
| `timestamp` | number | Unix timestamp |
| `iso` | string | ISO 8601 format |

---

### utility.hash.md5

**Description:** Calculate MD5 hash

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `text` | string | Yes | - | Text to hash |
| `encoding` | string | No | `"utf-8"` | Text encoding |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `hash` | string | MD5 hash (hexadecimal) |

---

## AI Services

### ai.openai.chat

**Description:** OpenAI Chat Completion API

**Requires:** `pip install openai`

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_key` | string | No | `${env.OPENAI_API_KEY}` | OpenAI API key |
| `model` | string | No | `"gpt-4"` | Model name |
| `messages` | array | Yes | - | Chat messages |
| `temperature` | number | No | `1.0` | Sampling temperature |
| `max_tokens` | number | No | - | Maximum tokens |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | AI response |
| `usage` | object | Token usage stats |

---

### api.anthropic.chat

**Description:** Send a chat message to Anthropic Claude AI and get a response

**Requires:** `pip install aiohttp`

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_key` | string | No | `${env.ANTHROPIC_API_KEY}` | Anthropic API key |
| `model` | string | No | `"claude-3-5-sonnet-20241022"` | Model: claude-3-5-sonnet-20241022, claude-3-opus-20240229, claude-3-haiku-20240307 |
| `messages` | array | Yes | - | Array of message objects with role and content |
| `max_tokens` | number | No | `1024` | Maximum tokens in response (1-4096) |
| `temperature` | number | No | `1.0` | Sampling temperature 0-1 |
| `system` | string | No | - | System prompt to guide Claude behavior |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `content` | string | Claude response text |
| `model` | string | Model used for response |
| `stop_reason` | string | Why the model stopped (end_turn, max_tokens) |
| `usage` | object | Token usage (input_tokens, output_tokens) |

**Example:**

```yaml
- id: ask_claude
  module: api.anthropic.chat
  params:
    messages:
      - role: user
        content: "Summarize this article: ${article_text}"
    max_tokens: 500
    system: "You are a helpful assistant that summarizes text concisely."
```

---

### api.google_gemini.chat

**Description:** Send a chat message to Google Gemini AI and get a response

**Requires:** `pip install aiohttp`

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_key` | string | No | `${env.GOOGLE_AI_API_KEY}` | Google AI API key |
| `model` | string | No | `"gemini-1.5-pro"` | Model: gemini-1.5-pro, gemini-1.5-flash, gemini-pro |
| `prompt` | string | Yes | - | The text prompt to send to Gemini |
| `temperature` | number | No | `1.0` | Controls randomness 0-2 |
| `max_output_tokens` | number | No | `2048` | Maximum number of tokens in response (1-8192) |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `text` | string | Generated text response from Gemini |
| `model` | string | Model used for generation |
| `candidates` | array | All candidate responses |

**Example:**

```yaml
- id: ask_gemini
  module: api.google_gemini.chat
  params:
    prompt: "Explain quantum computing in simple terms"
    temperature: 0.7
    max_output_tokens: 500
```

---

## Databases

### db.postgresql.query

**Description:** Execute a SQL query on PostgreSQL database and return results

**Requires:** `pip install asyncpg`

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `connection_string` | string | No | `${env.POSTGRESQL_URL}` | PostgreSQL connection string (postgresql://user:password@host:port/database) |
| `query` | string | Yes | - | SQL query to execute |
| `params` | array | No | - | Parameters for parameterized queries (use $1, $2, etc) |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `rows` | array | Array of result rows as objects |
| `row_count` | number | Number of rows returned |
| `columns` | array | Column names in result set |

**Example:**

```yaml
- id: fetch_users
  module: db.postgresql.query
  params:
    query: "SELECT id, email, created_at FROM users WHERE active = true LIMIT 10"

- id: fetch_orders
  module: db.postgresql.query
  params:
    query: "SELECT * FROM orders WHERE user_id = $1 AND status = $2"
    params: ["${user_id}", "completed"]
```

---

### db.mysql.query

**Description:** Execute a SQL query on MySQL database and return results

**Requires:** `pip install aiomysql`

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `host` | string | No | `${env.MYSQL_HOST}` or `"localhost"` | MySQL server host |
| `port` | number | No | `3306` | MySQL server port |
| `user` | string | No | `${env.MYSQL_USER}` | MySQL username |
| `password` | string | No | `${env.MYSQL_PASSWORD}` | MySQL password |
| `database` | string | No | `${env.MYSQL_DATABASE}` | Database name |
| `query` | string | Yes | - | SQL query to execute |
| `params` | array | No | - | Parameters for parameterized queries (use %s) |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `rows` | array | Array of result rows as objects |
| `row_count` | number | Number of rows returned |
| `columns` | array | Column names in result set |

**Example:**

```yaml
- id: fetch_products
  module: db.mysql.query
  params:
    query: "SELECT id, name, price FROM products WHERE stock > 0 ORDER BY price DESC LIMIT 20"
```

---

### db.mongodb.find

**Description:** Query documents from MongoDB collection

**Requires:** `pip install motor`

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `connection_string` | string | No | `${env.MONGODB_URL}` | MongoDB connection string (mongodb://... or mongodb+srv://...) |
| `database` | string | Yes | - | Database name |
| `collection` | string | Yes | - | Collection name |
| `filter` | object | No | `{}` | MongoDB query filter (empty object returns all) |
| `projection` | object | No | - | Fields to include/exclude |
| `limit` | number | No | `100` | Maximum number of documents (1-10000) |
| `sort` | object | No | - | Sort order (1 for ascending, -1 for descending) |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `documents` | array | Array of matching documents |
| `count` | number | Number of documents returned |

**Example:**

```yaml
- id: fetch_users
  module: db.mongodb.find
  params:
    database: "myapp"
    collection: "users"
    filter: {status: "active"}
    projection: {_id: 0, name: 1, email: 1}
    limit: 50

- id: fetch_orders
  module: db.mongodb.find
  params:
    database: "myapp"
    collection: "orders"
    filter: {total: {$gt: 100}}
    sort: {created_at: -1}
    limit: 20
```

---

### db.mongodb.insert

**Description:** Insert one or more documents into MongoDB collection

**Requires:** `pip install motor`

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `connection_string` | string | No | `${env.MONGODB_URL}` | MongoDB connection string |
| `database` | string | Yes | - | Database name |
| `collection` | string | Yes | - | Collection name |
| `document` | object | No | - | Document to insert (for single insert) |
| `documents` | array | No | - | Array of documents (for bulk insert) |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `inserted_count` | number | Number of documents inserted |
| `inserted_ids` | array | Array of inserted document IDs |

**Example:**

```yaml
- id: insert_user
  module: db.mongodb.insert
  params:
    database: "myapp"
    collection: "users"
    document:
      name: "John Doe"
      email: "john@example.com"
      created_at: "${timestamp}"
```

---

## Cloud Storage

### cloud.aws_s3.upload

**Description:** Upload a file or data to AWS S3 bucket

**Requires:** `pip install aioboto3`

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `aws_access_key_id` | string | No | `${env.AWS_ACCESS_KEY_ID}` | AWS access key ID |
| `aws_secret_access_key` | string | No | `${env.AWS_SECRET_ACCESS_KEY}` | AWS secret access key |
| `region` | string | No | `${env.AWS_REGION}` or `"us-east-1"` | AWS region |
| `bucket` | string | Yes | - | S3 bucket name |
| `key` | string | Yes | - | S3 object key (file path in bucket) |
| `file_path` | string | No | - | Local file path to upload |
| `content` | string | No | - | File content to upload (as string or base64) |
| `content_type` | string | No | - | MIME type of the file (auto-detected if not provided) |
| `acl` | string | No | `"private"` | Access control: private, public-read, public-read-write |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | S3 URL of uploaded object |
| `bucket` | string | Bucket name |
| `key` | string | Object key |
| `etag` | string | ETag of uploaded object |

**Example:**

```yaml
- id: upload_report
  module: cloud.aws_s3.upload
  params:
    bucket: "my-bucket"
    key: "reports/daily-${timestamp}.txt"
    content: "${report_text}"
    content_type: "text/plain"

- id: upload_file
  module: cloud.aws_s3.upload
  params:
    bucket: "my-bucket"
    key: "backups/database.sql"
    file_path: "/tmp/backup.sql"
    acl: "private"
```

---

### cloud.aws_s3.download

**Description:** Download a file from AWS S3 bucket

**Requires:** `pip install aioboto3`

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `aws_access_key_id` | string | No | `${env.AWS_ACCESS_KEY_ID}` | AWS access key ID |
| `aws_secret_access_key` | string | No | `${env.AWS_SECRET_ACCESS_KEY}` | AWS secret access key |
| `region` | string | No | `${env.AWS_REGION}` or `"us-east-1"` | AWS region |
| `bucket` | string | Yes | - | S3 bucket name |
| `key` | string | Yes | - | S3 object key (file path in bucket) |
| `file_path` | string | No | - | Local file path to save downloaded content |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `content` | string | File content (if file_path not provided) |
| `file_path` | string | Path where file was saved (if file_path provided) |
| `size` | number | File size in bytes |
| `content_type` | string | MIME type of the file |

**Example:**

```yaml
- id: download_config
  module: cloud.aws_s3.download
  params:
    bucket: "my-bucket"
    key: "data/config.json"

- id: download_backup
  module: cloud.aws_s3.download
  params:
    bucket: "my-bucket"
    key: "backups/database.sql"
    file_path: "/tmp/downloaded.sql"
```

---

## Productivity

### api.notion.create_page

**Description:** Create a new page in Notion database

**Requires:** `pip install aiohttp`

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_key` | string | No | `${env.NOTION_API_KEY}` | Notion integration token (create at https://www.notion.so/my-integrations) |
| `database_id` | string | Yes | - | Notion database ID (32-char hex string) |
| `properties` | object | Yes | - | Page properties (must match your database schema) |
| `content` | array | No | - | Page content as Notion blocks |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `page_id` | string | Created page ID |
| `url` | string | URL to the created page |
| `created_time` | string | Page creation timestamp |

**Example:**

```yaml
- id: create_task
  module: api.notion.create_page
  params:
    database_id: "your_database_id"
    properties:
      Name:
        title:
          - text:
              content: "New Task"
      Status:
        select:
          name: "In Progress"
      Priority:
        select:
          name: "High"
```

---

### api.notion.query_database

**Description:** Query pages from Notion database with filters and sorting

**Requires:** `pip install aiohttp`

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_key` | string | No | `${env.NOTION_API_KEY}` | Notion integration token |
| `database_id` | string | Yes | - | Notion database ID |
| `filter` | object | No | - | Filter conditions for query |
| `sorts` | array | No | - | Sort order for results |
| `page_size` | number | No | `100` | Number of results to return (1-100) |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `results` | array | Array of page objects |
| `count` | number | Number of results returned |
| `has_more` | boolean | Whether there are more results |

**Example:**

```yaml
- id: query_tasks
  module: api.notion.query_database
  params:
    database_id: "your_database_id"
    filter:
      property: "Status"
      select:
        equals: "In Progress"
    sorts:
      - property: "Created"
        direction: "descending"
```

---

### api.google_sheets.read

**Description:** Read data from Google Sheets spreadsheet

**Requires:** `pip install google-api-python-client google-auth`

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `credentials` | object | No | `${env.GOOGLE_CREDENTIALS_JSON}` | Google service account JSON credentials (create at console.cloud.google.com) |
| `spreadsheet_id` | string | Yes | - | Google Sheets spreadsheet ID (from URL: /spreadsheets/d/{ID}/edit) |
| `range` | string | Yes | - | A1 notation range to read (e.g. Sheet1!A1:E100) |
| `include_header` | boolean | No | `true` | Parse first row as column headers |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `values` | array | Array of rows (each row is array of values) |
| `data` | array | Array of row objects (if include_header=true) |
| `row_count` | number | Number of rows read |

**Example:**

```yaml
- id: read_sheet
  module: api.google_sheets.read
  params:
    spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    range: "Sheet1!A1:D100"
    include_header: true
```

---

### api.google_sheets.write

**Description:** Write data to Google Sheets spreadsheet

**Requires:** `pip install google-api-python-client google-auth`

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `credentials` | object | No | `${env.GOOGLE_CREDENTIALS_JSON}` | Google service account JSON credentials |
| `spreadsheet_id` | string | Yes | - | Google Sheets spreadsheet ID |
| `range` | string | Yes | - | A1 notation range to write (e.g. Sheet1!A1) |
| `values` | array | Yes | - | Array of rows to write (each row is array of values) |
| `value_input_option` | string | No | `"USER_ENTERED"` | How to interpret input: USER_ENTERED (parse formulas), RAW (no parsing) |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `updated_range` | string | Range that was updated |
| `updated_rows` | number | Number of rows updated |
| `updated_columns` | number | Number of columns updated |
| `updated_cells` | number | Number of cells updated |

**Example:**

```yaml
- id: write_data
  module: api.google_sheets.write
  params:
    spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    range: "Sheet1!A1"
    values:
      - ["Name", "Email", "Status"]
      - ["John Doe", "john@example.com", "Active"]
      - ["Jane Smith", "jane@example.com", "Active"]
```

---

## Module Development

Want to create your own module? See [WRITING_MODULES.md](WRITING_MODULES.md) for a complete guide.

---

## Questions?

- [Open an issue](https://github.com/flytohub/flyto2/issues)
- [View DSL specification](DSL.md)
- [See example workflows](../workflows/)
