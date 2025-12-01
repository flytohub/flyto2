# Test Coverage Report

**Generated:** generate_test_coverage_report.py

## Summary

- **Total Modules:** 111
- **Tested:** 21 (18.9%)
- **Untested:** 90

## Untested Modules

### AGENT

- ✅ Can test `agent.autonomous`
- ✅ Can test `agent.chain`

### AI

- ✅ Can test `ai.local_ollama.chat`

### API

- 🔑 Needs API `api.anthropic.chat`
- 🔑 Needs API `api.github.create_issue`
- 🔑 Needs API `api.github.get_repo`
- 🔑 Needs API `api.github.list_issues`
- 🔑 Needs API `api.google_gemini.chat`
- 🔑 Needs API `api.google_sheets.read`
- 🔑 Needs API `api.google_sheets.write`
- 🔑 Needs API `api.notion.create_page`
- 🔑 Needs API `api.notion.query_database`
- 🔑 Needs API `api.openai.chat`
- 🔑 Needs API `api.openai.image`

### ARRAY

- ✅ Can test `array.chunk`
- ✅ Can test `array.difference`
- ✅ Can test `array.flatten`
- ✅ Can test `array.intersection`
- ✅ Can test `array.reduce`

### CLOUD

- 🔑 Needs API `cloud.aws_s3.download`
- 🔑 Needs API `cloud.aws_s3.upload`
- 🔑 Needs API `cloud.azure.download`
- 🔑 Needs API `cloud.azure.upload`
- 🔑 Needs API `cloud.gcs.download`
- 🔑 Needs API `cloud.gcs.upload`

### COMMUNICATION

- 🔑 Needs API `communication.twilio.make_call`
- 🔑 Needs API `communication.twilio.send_sms`

### CORE

- 🔑 Needs API `core.api.google_search`
- 🔑 Needs API `core.api.http_get`
- 🔑 Needs API `core.api.http_post`
- 🔑 Needs API `core.api.serpapi_search`
- ✅ Can test `core.browser.click`
- ✅ Can test `core.browser.extract`
- ✅ Can test `core.browser.find`
- ✅ Can test `core.browser.goto`
- ✅ Can test `core.browser.launch`
- ✅ Can test `core.browser.press`
- ✅ Can test `core.browser.screenshot`
- ✅ Can test `core.browser.type`
- ✅ Can test `core.browser.wait`
- ✅ Can test `core.element.attribute`
- ✅ Can test `core.element.query`
- ✅ Can test `core.element.text`
- ✅ Can test `core.flow.loop`

### DATA

- ✅ Can test `data.csv.read`
- ✅ Can test `data.csv.write`
- ✅ Can test `data.text.template`

### DATETIME

- ✅ Can test `datetime.add`
- ✅ Can test `datetime.format`
- ✅ Can test `datetime.parse`
- ✅ Can test `datetime.subtract`

### DB

- 🔑 Needs API `db.mongodb.find`
- 🔑 Needs API `db.mongodb.insert`
- 🔑 Needs API `db.mysql.query`
- 🔑 Needs API `db.postgresql.query`
- 🔑 Needs API `db.redis.get`
- 🔑 Needs API `db.redis.set`

### FILE

- ✅ Can test `file.copy`
- ✅ Can test `file.delete`
- ✅ Can test `file.exists`
- ✅ Can test `file.move`
- ✅ Can test `file.read`
- ✅ Can test `file.write`

### MATH

- ✅ Can test `math.calculate`
- ✅ Can test `math.ceil`
- ✅ Can test `math.floor`
- ✅ Can test `math.power`

### META

- ✅ Can test `meta.modules.list`
- ✅ Can test `meta.modules.update_docs`

### NOTIFICATION

- 🔑 Needs API `notification.discord.send_message`
- 🔑 Needs API `notification.email.send`
- 🔑 Needs API `notification.slack.send_message`
- 🔑 Needs API `notification.telegram.send_message`

### OBJECT

- ✅ Can test `object.omit`
- ✅ Can test `object.pick`
- ✅ Can test `object.values`

### PAYMENT

- 🔑 Needs API `payment.stripe.create_payment`
- 🔑 Needs API `payment.stripe.get_customer`
- 🔑 Needs API `payment.stripe.list_charges`

### PRODUCTIVITY

- 🔑 Needs API `productivity.airtable.create`
- 🔑 Needs API `productivity.airtable.read`
- 🔑 Needs API `productivity.airtable.update`

### STRING

- ✅ Can test `string.regex_match`
- ✅ Can test `string.titlecase`

### TEST

- ✅ Can test `test.assert_greater_than`

### UTILITY

- ✅ Can test `utility.datetime.now`
- ✅ Can test `utility.delay`
- ✅ Can test `utility.hash.md5`
- ✅ Can test `utility.random.number`
- ✅ Can test `utility.random.string`

