# Flyto2 Module Registry

Complete reference of all available modules, their parameters, and return values.

**Last Updated:** 2025-11-29

---

## Table of Contents

- [Browser Automation](#browser-automation)
- [HTTP/API Operations](#httpapi-operations)
- [Notifications](#notifications)
- [Data Processing](#data-processing)
- [Utility](#utility)
- [AI/ML](#aiml)

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

## AI/ML

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

## Module Development

Want to create your own module? See [WRITING_MODULES.md](WRITING_MODULES.md) for a complete guide.

---

## Questions?

- [Open an issue](https://github.com/flytohub/flyto2/issues)
- [View DSL specification](DSL.md)
- [See example workflows](../workflows/)
