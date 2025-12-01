# Module Categories

## Overview

Flyto2 modules are classified into three categories based on coupling, dependencies, and scope. This classification determines which modules can be automatically modified by AI systems.

## Category Definitions

### Atomic Modules

Lowest-level modules with minimal coupling and no external dependencies.

**Characteristics:**
- Pure functions: input → output transformation
- No external API calls
- No database connections
- No browser automation
- No cloud service dependencies
- Minimal side effects (local file operations allowed)
- Standard library only (plus whitelisted utilities)

**Naming Patterns:**
- `string.*` - String manipulation
- `array.*` - Array operations
- `object.*` - Object transformations
- `math.*` - Mathematical operations
- `data.*` - Data format conversions
- `datetime.*` - Date/time operations
- `file.*` - Local file operations
- `crypto.*` - Cryptographic operations
- `validation.*` - Input validation

**Examples:**
```
string.split
string.join
array.map
array.filter
object.merge
math.sum
data.json.parse
datetime.format
file.read
```

**AI Modification Policy:**
- ✅ Allowed for automatic modification
- ✅ Can auto-merge if quality gate passed
- Must maintain ≥98% success rate

### Third-Party Modules

Modules that integrate with external services, APIs, or infrastructure.

**Characteristics:**
- HTTP/API calls to external services
- Cloud service integrations
- Database connections
- Browser automation
- Authentication required
- Network-dependent
- Rate limits apply
- External service errors possible

**Naming Patterns:**
- `ai.*` - AI service integrations
- `notification.*` - Notification services
- `cloud.*` - Cloud storage/compute
- `api.*` - External API integrations
- `db.*` - Database operations
- `browser.*` - Browser automation
- `auth.*` - Authentication services

**Examples:**
```
ai.openai.chat
ai.local_ollama.chat
notification.telegram.send_message
notification.slack.post
cloud.aws.s3.upload
api.github.create_pr
db.postgres.query
browser.launch
```

**AI Modification Policy:**
- ⚠️  Requires human review
- ⚠️  No automatic merge
- Can propose improvements via PR
- Must include integration tests

### Composed Modules

High-level modules that orchestrate multiple atomic/third-party modules.

**Characteristics:**
- Call multiple other modules
- Implement business logic
- Coordinate workflows
- Handle complex error cases
- May combine atomic + third-party operations

**Naming Patterns:**
- `workflow.*` - Multi-step workflows
- `pipeline.*` - Data pipelines
- `agent.*` - Autonomous agents
- Custom domain-specific prefixes

**Examples:**
```
agent.autonomous
agent.chain_of_thought
workflow.scrape_and_notify
pipeline.data_processing
```

**AI Modification Policy:**
- ⚠️  Requires human review
- ⚠️  No automatic merge
- High-level logic needs careful validation
- Must test all component interactions

## Classification Rules

### Rule 1: Import Restrictions

**Atomic modules MUST NOT import:**
```python
# Network/API
import requests
import httpx
import aiohttp
import urllib

# AI Services
import openai
import anthropic
from google.cloud import aiplatform

# Browser
from playwright import async_api
from selenium import webdriver

# Database
import psycopg2
import pymongo
import redis

# Cloud
import boto3
from google.cloud import storage
```

**Atomic modules CAN import:**
```python
# Standard library
import json
import re
import datetime
import hashlib
import base64
import math
import os
import pathlib

# Whitelisted utilities
import yaml
import pydantic
```

### Rule 2: Naming Convention

Module ID must match category:
- Atomic: Use standard prefixes (string, array, object, math, data, datetime, file)
- Third-party: Use service name prefix (ai, notification, cloud, api, db, browser)
- Composed: Use workflow/agent/pipeline prefix

### Rule 3: Side Effects

**Atomic modules:**
- Read-only operations: No restrictions
- Local file write: Allowed (data.file.write, etc.)
- Network calls: ❌ Not allowed
- Database writes: ❌ Not allowed
- External service calls: ❌ Not allowed

**Third-party/Composed:**
- All side effects allowed with proper error handling

### Rule 4: Dependency Graph

**Atomic:**
- May depend on: Other atomic modules only
- Dependency depth: ≤ 2 levels

**Third-party:**
- May depend on: Atomic modules
- Should not depend on: Other third-party modules (prefer composition)

**Composed:**
- May depend on: Any modules
- Should minimize coupling between components

## Validation Process

### Automated Checks

1. **Import Analysis**
   - Scan Python files for import statements
   - Check against whitelist/blacklist
   - Flag violations

2. **Naming Convention**
   - Verify module_id matches category
   - Check for inconsistencies

3. **Dependency Analysis**
   - Build module dependency graph
   - Verify atomic modules don't call third-party
   - Check for circular dependencies

4. **Side Effect Detection**
   - Scan for network calls
   - Scan for database operations
   - Scan for external service usage

### Manual Review Required

- Category boundary cases
- New module categories
- Unusual dependency patterns
- Complex composed workflows

## Quality Gates

### For Atomic Modules

Before AI modification is accepted:
1. ✅ Category verified as "atomic"
2. ✅ Import restrictions validated
3. ✅ All tests pass
4. ✅ Success rate ≥ 98% over last 50 runs
5. ✅ New version success rate ≥ old version
6. ✅ No regression in performance
7. ✅ Code review (optional for minor changes)

### For Third-Party Modules

Before modification is accepted:
1. ✅ Category verified as "third_party"
2. ✅ Integration tests pass
3. ✅ Success rate ≥ 95% (lower threshold due to external dependencies)
4. ⚠️  Manual code review required
5. ⚠️  Manual testing with real services
6. ⚠️  No automatic merge

### For Composed Modules

Before modification is accepted:
1. ✅ Category verified as "composed"
2. ✅ All component modules tested
3. ✅ End-to-end workflow tests pass
4. ⚠️  Manual code review required
5. ⚠️  Manual approval required
6. ⚠️  No automatic merge

## Module Lifecycle

### New Module

1. Developer creates module
2. Applies `@register_module` decorator
3. Declares category in metadata
4. Creates test workflow in `tests/modules/`
5. Initial validation run
6. Adds to module registry

### AI Improvement Proposal

1. AI analyzes module quality metrics
2. Generates improved version
3. Saves to `_generated/modules/`
4. Automated testing (30-50 runs)
5. Quality gate evaluation
6. If passed: Create PR
7. If failed: Log failure, discard

### Quality Degradation

1. Success rate drops below threshold
2. Telegram alert sent
3. Module marked for review
4. AI proposes fix
5. Testing & validation
6. Human review if critical

### Module Retirement

1. Module deprecated in registry
2. Dependencies identified
3. Migration plan created
4. Gradual phase-out
5. Remove from registry

## Best Practices

### For Atomic Modules

- Keep functions pure when possible
- One responsibility per module
- Comprehensive input validation
- Clear error messages
- Fast execution (< 100ms typical)
- No hidden state
- Deterministic output

### For Third-Party Modules

- Robust error handling
- Timeout configuration
- Retry logic with backoff
- Rate limit handling
- Clear service status errors
- Graceful degradation
- Connection pooling

### For Composed Modules

- Clear step boundaries
- Error propagation strategy
- Partial success handling
- Compensation logic for failures
- Clear rollback strategy
- Comprehensive logging
- Circuit breaker pattern

## Metrics Tracked

For each module category:

**Quality Metrics:**
- Success rate (last 50 runs)
- Average execution time
- Error frequency by type
- Retry success rate

**Usage Metrics:**
- Total executions
- Unique workflows using module
- Peak usage periods
- Deprecation impact

**Improvement Metrics:**
- AI proposal count
- Accepted improvement rate
- Quality improvement delta
- Regression count

## Examples

### Valid Atomic Module

```python
@register_module(
    module_id='string.split',
    version='1.0.0',
    category='atomic',
    description='Split string by separator',
    params_schema={
        'text': {'type': 'string', 'required': True},
        'separator': {'type': 'string', 'default': ','}
    },
    output_schema={
        'parts': {'type': 'array', 'items': {'type': 'string'}}
    }
)
class StringSplitModule(BaseModule):
    async def execute(self) -> Any:
        parts = self.text.split(self.separator)
        return {'parts': parts}
```

**Why valid:**
- No external imports
- Pure transformation
- Fast execution
- No side effects
- Clear input/output

### Invalid Atomic Module

```python
@register_module(
    module_id='string.translate',
    category='atomic',  # ❌ WRONG - calls external API
    ...
)
class StringTranslateModule(BaseModule):
    async def execute(self) -> Any:
        import openai  # ❌ VIOLATION
        response = await openai.chat.completions.create(...)  # ❌ VIOLATION
        return {'translated': response}
```

**Why invalid:**
- Imports external service (openai)
- Makes network calls
- Should be categorized as "third_party"
- Not deterministic
- Slow execution

### Valid Third-Party Module

```python
@register_module(
    module_id='ai.openai.chat',
    category='third_party',
    description='Chat with OpenAI',
    ...
)
class OpenAIChatModule(BaseModule):
    async def execute(self) -> Any:
        # External API call - appropriate for third_party
        response = await self.client.chat.completions.create(...)
        return {'response': response}
```

**Why valid:**
- Correctly categorized as third_party
- External API usage expected
- Proper error handling
- Clear service dependency

## Summary

**Key Principles:**
1. Atomic = Pure, fast, no external deps → AI can auto-modify
2. Third-party = External services → AI proposes, human reviews
3. Composed = Business logic → Human-controlled
4. Classification enforced by automated validation
5. Quality gates prevent degradation
6. Success rate ≥ 98% for atomic auto-merge
7. All changes tracked and reversible

This classification system ensures AI improvements enhance the codebase without introducing coupling, external dependencies, or quality regressions.
