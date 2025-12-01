# Precise English Prompts for Telegram Bot

Short, precise prompts for maximum efficiency and minimal cost.

## Quick Reference

### Ask Questions (Ollama - Free)

```
summarize today's commits
show quality status
list failing modules
what changed in last 24h
```

### Provide Guidance (When Bot Unsure - Free)

```
use approach B, keep compatibility
apply minimal fix, no full rewrite
focus on async error handling
avoid modifying atomic modules
```

### Force OpenAI (Paid ~$0.10)

```
/gpt refactor with dependency injection
/gpt analyze architecture risks
/gpt review this PR with detailed feedback
```

## Command Categories

### 1. Status Queries (Ollama)

**One-line answers:**
```
current pass rate?
any regressions?
modules below 98%?
last deployment?
```

**Detailed reports:**
```
summarize module quality in 3 bullets
list all modules with pass rates
show deployment history for string.split
```

### 2. Code Analysis (Ollama → Guidance → OpenAI)

**Initial ask (Ollama tries):**
```
review this code for issues
suggest refactoring approach
identify performance bottlenecks
```

**If Ollama unsure, provide guidance:**
```
Direction: focus on async patterns, ignore style
Constraint: maintain backward compatibility
Priority: fix error handling first
```

**If still needs help:**
```
/retry
```

### 3. Decision Making (Usually needs OpenAI)

**Complex decisions:**
```
/gpt should I enable auto-rollback now?
/gpt evaluate these 3 architecture options
/gpt risk analysis for this deployment
```

### 4. Code Generation (Ollama first, OpenAI if needed)

**Simple generation (Ollama):**
```
write test for string.split
add error handling to this function
create workflow for quality check
```

**Complex generation (OpenAI):**
```
/gpt refactor deployment_manager with clean architecture
/gpt design rollback system with safety checks
/gpt implement async queue with retry logic
```

## Guidance Templates

When bot asks for guidance, use these patterns:

### Direction
```
Use approach: <A|B|C>
Focus on: <specific aspect>
Avoid: <what not to do>
```

**Examples:**
```
Use approach: B with async
Focus on: error handling
Avoid: breaking changes

Direction: minimal change
Constraint: no new dependencies
```

### Correction
```
Your <assumption> is wrong
The correct <constraint> is <X>
Re-evaluate based on <fact>
```

**Examples:**
```
Your reasoning about atomicity is wrong
The correct rule is: no external API calls
Re-evaluate with this constraint

Incorrect. Module is third-party, not atomic
Correct approach: require human review
```

### Refinement
```
Expand on <topic>
Be more specific about <X>
Provide code for <Y>
```

**Examples:**
```
Expand on the async implementation
Be more specific about error cases
Provide code for the rollback function
```

## Cost-Saving Patterns

### Pattern 1: Progressive Detail

**Start simple (free):**
```
You: outline refactoring plan
Bot: [Ollama] 3-step plan...

You: expand step 2 with code
Bot: [Ollama] Here's the code...
```

**Only if needed:**
```
You: /gpt review this plan for issues
Bot: [OpenAI] Issues: ...
```

### Pattern 2: Filter First

**Filter with Ollama (free):**
```
You: which modules need attention?
Bot: [Ollama] string.replace, array.filter

You: /gpt analyze string.replace deeply
Bot: [OpenAI] Deep analysis...
```

### Pattern 3: Human Checkpoint

**Let bot attempt (free):**
```
You: refactor this function
Bot: [Ollama low confidence] Here's my attempt...
     Need guidance?

You: keep original logic, just clean syntax
Bot: [Ollama] Done, here's the cleaned version
```

**Skip OpenAI entirely with good guidance!**

## Flyto2-Specific Prompts

### Quality Monitoring

```
/status
show regressions
modules below threshold
last test results
```

### Workflow Triggers

```
test string.split
improve array.filter with guidance: <your guidance>
check deployment history
rollback to previous version
```

### Module Analysis

```
analyze string.replace quality trend
compare array.map vs array.filter stability
suggest improvements for math.round
```

## Prompt Anti-Patterns (Avoid)

### ❌ Too Verbose

```
Bad:  Can you please help me understand what might be
      the best approach to refactor this code while
      maintaining backward compatibility and...

Good: refactor this, keep compatibility
```

### ❌ Vague

```
Bad:  make it better
Good: improve error handling, add async
```

### ❌ Multiple Questions

```
Bad:  what's the status and also can you check if
      there are regressions and also...

Good: /status
      (then) any regressions?
```

### ❌ Unnecessary Context

```
Bad:  yesterday I was working on this and I think
      maybe we should consider...

Good: should we refactor X?
      constraint: no breaking changes
```

## OpenAI-Worthy Questions

Only use `/gpt` for:

✅ **Architecture decisions**
```
/gpt evaluate microservices vs monolith for this
/gpt design event-driven rollback system
```

✅ **Complex refactoring**
```
/gpt refactor with dependency injection + tests
/gpt migrate from sync to async architecture
```

✅ **Risk analysis**
```
/gpt analyze security risks in this approach
/gpt what could go wrong with auto-merge?
```

✅ **Code review (deep)**
```
/gpt review for concurrency issues
/gpt find edge cases in this logic
```

## Quick Reference Card

| Task | Command | Cost |
|------|---------|------|
| Simple question | `what changed?` | Free |
| Status check | `/status` | Free |
| Guidance | `use async, keep compat` | Free |
| Retry with OpenAI | `/retry` | $0.10 |
| Force OpenAI | `/gpt <question>` | $0.10 |
| Usage stats | `/stats` | Free |

## Examples: Free vs Paid

### Scenario 1: Daily Check (100% Free)

```
You: what changed today?
Bot: [Ollama] 3 commits: ...

You: any quality issues?
Bot: [Ollama] All modules 100%

You: show deployment history
Bot: [Ollama] Last 5 deployments: ...

Cost: $0
```

### Scenario 2: Code Review (Mostly Free)

```
You: review this function
Bot: [Ollama 60% confident] Some issues: ...
     Need guidance?

You: focus on error handling only
Bot: [Ollama] Error handling review: ...

Cost: $0
```

### Scenario 3: Architecture Decision (Paid)

```
You: /gpt should I enable auto-rollback?
     analyze all risks, give recommendation

Bot: [OpenAI] Based on your metrics...
     [detailed analysis]

Cost: $0.15
```

## Monthly Cost Examples

### Light Usage (20 questions/day)
```
18 Ollama + 2 guidance = Free
0 OpenAI

Cost: $0 (NT$0)
```

### Medium Usage (50 questions/day)
```
40 Ollama + 8 guidance = Free
2 OpenAI per day

Cost: $2/month (NT$60)
```

### Heavy Usage (100 questions/day)
```
85 Ollama + 12 guidance = Free
3 OpenAI per day

Cost: $3/month (NT$90)
```

---

**Key Principle:**
Be concise. Let Ollama try. Guide when needed. Use OpenAI sparingly.

**Your cost: ~NT$30-90/month (vs NT$2,430 with OpenAI-only)**
