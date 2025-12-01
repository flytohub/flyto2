# Testing with API Tokens

## Overview

The Flyto2 testing system now supports **optional API token collection** for comprehensive module testing.

## Current Test Coverage

Without API tokens:
- **21 modules tested** (18.9% coverage)
- Basic operations: string, array, math, object, file, datetime

With API tokens:
- **Up to 60+ modules** can be tested
- API integrations, notifications, databases, cloud storage

## How to Use (Telegram Bot)

### 1. Start Testing

Send `/test` command to the bot.

### 2. Choose Testing Mode

You'll see two options:

**Option A: 🔑 Provide API tokens**
- Test more modules (API integrations)
- Requires you to provide tokens

**Option B: ⏩ Skip tokens**
- Basic tests only (21 modules)
- No tokens needed

### 3. If You Choose "Provide API tokens"

The bot will ask you to send tokens one by one.

**Format:**
```
TOKEN_NAME=value
```

**Examples:**
```
OPENAI_API_KEY=sk-proj-xxx
SLACK_WEBHOOK_URL=https://hooks.slack.com/xxx
ANTHROPIC_API_KEY=sk-ant-xxx
TELEGRAM_BOT_TOKEN=123456:ABC-xxx
```

### 4. Finish Token Collection

When done, send:
- `/done` - Start tests with provided tokens
- `/skip` - Skip remaining tokens and start tests

## Supported API Tokens

### AI Providers
- `OPENAI_API_KEY` - OpenAI (GPT-4, DALL-E)
- `ANTHROPIC_API_KEY` - Claude
- `GOOGLE_GEMINI_API_KEY` - Gemini

### Notifications
- `SLACK_WEBHOOK_URL` - Slack
- `DISCORD_WEBHOOK_URL` - Discord
- `TELEGRAM_BOT_TOKEN` - Telegram bot
- `TELEGRAM_CHAT_ID` - Telegram chat
- `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS` - Email

### Cloud Storage
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` - AWS S3
- `GCS_CREDENTIALS_JSON` - Google Cloud Storage
- `AZURE_STORAGE_CONNECTION_STRING` - Azure

### Databases (if running locally)
- `MONGODB_URI` - MongoDB
- `POSTGRESQL_URI` - PostgreSQL
- `MYSQL_URI` - MySQL
- `REDIS_URL` - Redis

### Developer Tools
- `GITHUB_TOKEN` - GitHub API
- `NOTION_API_KEY` - Notion
- `AIRTABLE_API_KEY` - Airtable

## Example Session

```
User: /test

Bot: 🧪 Module Testing Options

Current coverage: ~21/111 modules (18.9%)

Would you like to provide API tokens to test more modules?

[Button] 🔑 Provide API tokens (test more modules)
[Button] ⏩ Skip tokens (basic tests only)

User: [Clicks "Provide API tokens"]

Bot: 🔑 Provide API Tokens

Please provide tokens one by one.
Send in format: TOKEN_NAME=value

Example:
OPENAI_API_KEY=sk-xxx

Send /done when finished, or /skip to skip remaining.

User: OPENAI_API_KEY=sk-proj-abc123

Bot: ✅ Added OPENAI_API_KEY

Send more tokens or /done to continue.

User: SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx

Bot: ✅ Added SLACK_WEBHOOK_URL

Send more tokens or /done to continue.

User: /done

Bot: ✅ Collected 2 token(s). Starting tests with API integrations...

🧪 Running quality tests...

This may take a few minutes.

📊 Test Coverage Report

Registered Modules: 111
Modules Tested: 35 (31.5%)
Modules Untested: 76

Test Results:
• Tests run: 25
• Passed: 24 ✅
• Failed: 1 ❌
• Pass rate: 96.0%
```

## Security Notes

⚠️ **Important:**
1. Tokens are **only stored in memory** during the test session
2. Tokens are **cleared** after tests complete
3. Tokens are **not logged** or saved to disk
4. Use **test/sandbox accounts** when possible
5. **Read-only tokens** are safer (avoid write permissions)

## Skipping Token Collection

If you don't want to provide tokens, just click **"Skip tokens"** button, and only basic tests will run (21 modules, no API calls).

## Adding New API Tests

To add tests for new API modules:

1. Create test workflow in `workflows/_test/`
2. Use environment variables for tokens
3. Add module ID to test YAML

Example: `workflows/_test/test_openai_chat.yaml`

```yaml
name: "Test OpenAI Chat"
description: "Verify OpenAI integration works"

steps:
  - id: test_chat
    module: api.openai.chat
    params:
      api_key: "${OPENAI_API_KEY}"  # From environment
      messages:
        - role: "user"
          content: "Say 'test passed' if you receive this"
      model: "gpt-3.5-turbo"

  - id: verify_response
    module: test.assert_contains
    params:
      value: "${test_chat.response}"
      substring: "test"
```

## FAQ

**Q: Are my tokens safe?**
A: Tokens are only in memory during tests, never saved to disk.

**Q: Can I test without tokens?**
A: Yes! Click "Skip tokens" for basic tests (21 modules).

**Q: Which tokens should I provide?**
A: Only provide tokens for services you want to test. Start with OpenAI if you have it.

**Q: What if a test fails?**
A: The bot will show which module failed and suggest fixes.

**Q: Can I reuse tokens for multiple test runs?**
A: No, you need to provide them each time (for security).

## Roadmap

Future enhancements:
- [ ] Token validation before testing
- [ ] Encrypted token storage (optional)
- [ ] Mock testing for API modules (no tokens needed)
- [ ] Token usage cost estimation
- [ ] Sandbox mode for destructive operations
