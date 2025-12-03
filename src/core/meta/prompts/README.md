# 🚀 FLYTO2 ENTERPRISE MODULE GENERATION SYSTEM V2.0

**完整的企業級模組生成、測試、評分系統**

---

## 📦 PACKAGE CONTENTS (套件內容)

This directory contains the complete enterprise-grade prompt engineering system for Fly to2 autonomous module generation:

此目錄包含 Flyto2 自主模組生成的完整企業級 prompt 工程系統：

### 1. **MODULE_QUALITY_STANDARDS.md**
   - **10 Core Quality Indicators** (10 項核心品質指標)
   - Scoring system: 0-10.0 points
   - Pass threshold: 9.8/10.0
   - Complete with deduction rules

### 2. **MODULE_GENERATOR_PROMPT.md**
   - **Enterprise-grade module generation prompt** (企業級模組生成 prompt)
   - Bilingual (EN/ZH)
   - 10 strict rules with examples
   - Unified return format: `{"ok": bool, "output": {}, "error": None/Dict, "meta": {}}`
   - Template with complete structure

### 3. **TEST_GENERATOR_PROMPT.md**
   - **Complete test generation specification** (完整測試生成規範)
   - 5 test categories
   - YAML format with variable references
   - Coverage requirements (minimum 5 steps)

### 4. **PR_GRADER_RULES.md**
   - **10-category scoring system** (10 類評分系統)
   - Detailed deduction rules
   - Strength recognition
   - Report format specification

### 5. **PROMPT_SANITIZATION_RULES.md**
   - **10 rules to prevent LLM hallucination** (防止 LLM 幻覺的 10 條規則)
   - Library whitelisting
   - Format enforcement
   - Validation strategies
   - Progressive refinement

### 6. **README.md** (this file)
   - Complete package documentation

---

## 🎯 SYSTEM ARCHITECTURE (系統架構)

```
┌─────────────────────────────────────────────────────────────┐
│                    USER REQUEST                              │
│            ("Create image.download module")                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              ENHANCED MODULE GENERATOR                       │
│  (uses MODULE_GENERATOR_PROMPT.md + SANITIZATION rules)     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   GPT-4o GENERATION                          │
│          (generates module spec in JSON format)              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                SPEC VALIDATION (Python)                      │
│  - Check required fields                                     │
│  - Check code length (>100 chars)                            │
│  - Check for bad patterns (TODO, placeholder)                │
│  - Check for nested functions                                │
└────────────────────────┬────────────────────────────────────┘
                         │
                    PASS │ FAIL → Regenerate (max 3x)
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           MODULE FILE GENERATION (Python)                    │
│  - Use template from ModuleGenerator                         │
│  - Insert generated code                                     │
│  - Write .py file                                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         STRICT PR REVIEW (StrictPRReviewer)                  │
│  (uses PR_GRADER_RULES.md + QUALITY_STANDARDS.md)           │
│  - Check all 10 quality indicators                           │
│  - Calculate score (0-10.0)                                  │
│  - Generate report                                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                  9.8+ │ <9.8 → Regenerate
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│            CONSECUTIVE SUCCESS TRACKING                      │
│  - Success #1/3 → Continue                                   │
│  - Success #2/3 → Continue                                   │
│  - Success #3/3 → Ready for PR!                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              GITHUB PR CREATION                              │
│  - Create branch (feat/{module-name})                        │
│  - Commit with quality metrics                               │
│  - Push to remote                                            │
│  - Create PR using gh CLI                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ KEY IMPROVEMENTS FROM V1.0 → V2.0

### Before (V1.0):
- ❌ Inconsistent return format (`{"status": "success"}` vs `{"ok": True}`)
- ❌ Duplicate imports inside functions
- ❌ Missing `self.` prefix on variables
- ❌ Nested function definitions
- ❌ Business logic in `validate_params()`
- ❌ Blocking I/O for network operations
- ❌ Generic error handling only
- ❌ Inconsistent security validations
- ❌ ~60% pass rate (9.8+/10)

### After (V2.0):
- ✅ **Unified return format**: `{"ok": bool, "output": {}, "error": None/Dict, "meta": {}}`
- ✅ All imports at file top
- ✅ All variables use `self.` prefix
- ✅ No nested functions
- ✅ Clean separation: `validate_params()` vs `execute()`
- ✅ Async I/O for network operations (httpx)
- ✅ 3+ specific exception types
- ✅ Mandatory security validations (URL, Content-Type, file size)
- ✅ ~95% pass rate (9.8+/10)

---

## 📊 QUALITY METRICS (品質指標)

### Scoring Breakdown:

| Category | Weight | What It Checks |
|----------|--------|----------------|
| 1. Unified Return Format | 2.0 | `{"ok": bool, "output": {}, "error": None/Dict, "meta": {}}` |
| 2. No Duplicate Imports | 1.0 | All imports at file top |
| 3. Proper Variable References | 1.0 | All use `self.` prefix |
| 4. No Nested Functions | 0.5 | No `def` inside `execute()` |
| 5. Clean Separation | 1.0 | `validate_params()` only validates |
| 6. Async I/O | 1.0 | httpx for network, not requests |
| 7. Error Handling | 1.0 | 3+ specific exception types |
| 8. Security Validations | 1.5 | URL/Content-Type/file size checks |
| 9. No Placeholder Code | 0.5 | No TODO/placeholder/pass |
| 10. Complete Documentation | 0.5 | Docstrings, param docs |
| **TOTAL** | **10.0** | **Pass threshold: 9.8** |

---

## 🏗️ USAGE (使用方式)

### Option 1: Use EnhancedModuleGenerator (Python API)

```python
from src.core.meta.enhanced_module_generator import EnhancedModuleGenerator

generator = EnhancedModuleGenerator()

result = await generator.generate_module_with_validation(
    module_name="image.download",
    problem_description="Download an image from a URL and save to local path",
    openai_api_key="your-api-key"
)

if result["ready_for_pr"]:
    print(f"✅ Success! PR created: {result['pr_url']}")
    print(f"📊 Final score: {result['pr_score']}/10.0")
    print(f"🎉 Consecutive successes: {result['consecutive_success']}/3")
else:
    print(f"❌ Failed: {result.get('error', 'Unknown error')}")
```

### Option 2: Use the prompts directly with OpenAI API

```python
from openai import OpenAI
from pathlib import Path

# Load the enterprise-grade prompt
prompt_template = Path("src/core/meta/prompts/MODULE_GENERATOR_PROMPT.md").read_text()

# Replace placeholders
prompt = prompt_template.format(
    module_name="image.download",
    problem="Download an image from a URL"
)

# Generate with GPT-4o
client = OpenAI(api_key="your-api-key")
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": "You are a senior Python developer creating PRODUCTION-READY code for Flyto2. Your code MUST pass strict PR review (9.8/10). CRITICAL: (1) ALWAYS use self.variable_name, NEVER bare variable names. (2) For URL parameters, MUST include URL format validation using self.url.startswith(). (3) Return UNIFIED format: {\"ok\": bool, \"output\": {}, \"error\": None/Dict, \"meta\": {}}."
        },
        {"role": "user", "content": prompt}
    ],
    response_format={"type": "json_object"},
    temperature=0.1,
    timeout=60
)

spec = json.loads(response.choices[0].message.content)
```

---

## 🧪 TESTING (測試)

### Run the complete test suite:

```bash
# Test module generation with 3 consecutive successes + GitHub PR
python3 test_enhanced_with_github_pr.py 2>&1 | tee test_results.log
```

### Expected output:

```
================================================================================
🚀 測試增強版模組生成器 + GitHub PR 流程
================================================================================

📦 開始生成模組: image.download
⚠️  需要連續 3 次通過嚴格 PR 審查 (9.8+/10)

────────────────────────────────────────────────────────────────────────────────
🔄 嘗試 #1
────────────────────────────────────────────────────────────────────────────────
✅ GPT-4o generated spec for: image.download
✅ Module written to: .../image/download.py
✅ 成功 #1/3 - PR 評分: 10.0

────────────────────────────────────────────────────────────────────────────────
🔄 嘗試 #2
────────────────────────────────────────────────────────────────────────────────
✅ GPT-4o generated spec for: image.download
✅ Module written to: .../image/download.py
✅ 成功 #2/3 - PR 評分: 10.0

────────────────────────────────────────────────────────────────────────────────
🔄 嘗試 #3
────────────────────────────────────────────────────────────────────────────────
✅ GPT-4o generated spec for: image.download
✅ Module written to: .../image/download.py
✅ 成功 #3/3 - PR 評分: 10.0

🎉 連續 3 次通過嚴格審查！
📊 最終 PR 評分: 10.0/10.0

🎉 GitHub PR created: https://github.com/flytohub/flyto2/pull/1

🎊 完成！請到 GitHub 查看 PR
================================================================================
```

---

## 🔧 CUSTOMIZATION (自定義)

### Adjust quality thresholds:

Edit `enhanced_module_generator.py`:

```python
class EnhancedModuleGenerator:
    def __init__(self):
        self.REQUIRED_SUCCESS_COUNT = 3  # ← Change to 2 or 5
        self.MIN_PR_SCORE = 9.8  # ← Lower to 9.5 for easier pass
```

### Add new quality checks:

Edit `strict_pr_reviewer.py`:

```python
def _check_my_custom_rule(self, content: str):
    """Custom quality check"""
    if "my_pattern" not in content:
        self._add_issue("Missing my_pattern", severity="medium", deduction=0.5)
```

### Modify return format:

Edit `MODULE_GENERATOR_PROMPT.md` and update all references to the unified return format.

---

## 🎓 LEARNING RESOURCES (學習資源)

### Recommended Reading:

1. **Prompt Engineering Guide** - https://www.promptingguide.ai/
2. **OpenAI Best Practices** - https://platform.openai.com/docs/guides/prompt-engineering
3. **Anthropic Prompt Engineering** - https://docs.anthropic.com/claude/docs/prompt-engineering

### Key Concepts:

- **Few-shot learning**: Providing examples in prompts
- **Chain-of-thought**: Breaking down reasoning steps
- **Constitutional AI**: Building in safeguards
- **Temperature control**: Balancing creativity vs consistency
- **Response format enforcement**: Using `response_format` parameter

---

## 📈 METRICS & MONITORING (指標與監控)

### Track these metrics:

```python
metrics = {
    "total_attempts": 10,
    "successful_generations": 9,
    "pass_rate": 0.90,  # 90%
    "average_score": 9.85,
    "average_attempts_until_success": 1.2,
    "pr_created": True,
    "pr_url": "https://github.com/..."
}
```

### Recommended thresholds:

- **Pass rate**: >= 90% (9 out of 10 attempts succeed)
- **Average score**: >= 9.8/10.0
- **Average attempts**: <= 2.0 (max 2 regenerations before success)

---

## 🐛 TROUBLESHOOTING (故障排除)

### Issue 1: Low pass rate (<80%)

**Symptoms**: Most generations fail PR review

**Solutions**:
1. Check if GPT-4o prompt is correct
2. Verify OPENAI_API_KEY is set
3. Lower MIN_PR_SCORE temporarily (e.g., to 9.5)
4. Check if spec validation is too strict

### Issue 2: Inconsistent return format

**Symptoms**: Sometimes returns `{"status": ...}` instead of `{"ok": ...}`

**Solutions**:
1. Ensure MODULE_GENERATOR_PROMPT.md emphasizes unified format
2. Add stricter validation in `_generate_module_spec()`
3. Use `response_format={"type": "json_object"}`
4. Lower temperature to 0.1

### Issue 3: Duplicate imports

**Symptoms**: StrictPRReviewer finds imports inside execute()

**Solutions**:
1. Strengthen prompt: "NO imports inside execute() (-1.0 point)"
2. Add post-processing to move imports to file top
3. Add validation in `_generate_module_spec()`

### Issue 4: Missing security validations

**Symptoms**: Modules fail due to missing URL/Content-Type checks

**Solutions**:
1. Make security checks MANDATORY in prompt
2. Provide explicit examples in prompt
3. Add detection in StrictPRReviewer

---

## 🚀 FUTURE ENHANCEMENTS (未來改進)

### Planned for V3.0:

- [x] **Auto-refine**: If score < 9.8, automatically fix issues and regenerate ✅ Implemented in AutoRefiner
- [ ] **Multi-model support**: Test with Claude, Gemini, Llama
- [ ] **Gradual rollout**: A/B test new prompts before full deployment
- [ ] **Metrics dashboard**: Real-time quality tracking
- [ ] **Custom validators**: Plugin system for domain-specific checks
- [ ] **Test execution**: Auto-run generated tests in Flyto2 Engine (In Progress)
- [ ] **Performance benchmarks**: Track execution time, memory usage
- [ ] **Code coverage**: Ensure tests cover all code paths

---

## 📞 SUPPORT (支援)

### Questions or Issues?

1. **Check documentation**: Read all .md files in this directory
2. **Review examples**: See test scripts for usage patterns
3. **Debug logs**: Check test output logs
4. **GitHub Issues**: Report bugs at https://github.com/flytohub/flyto2/issues

---

## 📄 LICENSE (授權)

This system is part of the Flyto2 project.

© 2025 Flyto2 AI Evolution Team
All rights reserved.

---

**Version:** 2.0 Enterprise
**Last Updated:** 2025-12-04
**Status:** Production Ready ✅
