# 🛡️ PROMPT SANITIZATION RULES (Prompt 消毒規範)

**Version:** 1.0
**Language:** Bilingual (EN/ZH)
**Purpose:** Prevent LLM hallucination and ensure consistent output quality
**Target:** ModuleGenerator, TestGenerator, Any AI-powered generation

---

## 🎯 GOAL (目標)

Prevent common LLM failure modes:
- Hallucinating non-existent libraries
- Generating placeholder code
- Producing inconsistent formats
- Ignoring critical requirements
- Creating syntax errors

防止常見的 LLM 失敗模式：
- 虛構不存在的庫
- 生成佔位符代碼
- 產生不一致的格式
- 忽略關鍵要求
- 創建語法錯誤

---

## 🚫 RULE 1: EXPLICIT LIBRARY WHITELIST (明確的庫白名單)

### Problem (問題)

LLMs often hallucinate libraries that don't exist or use wrong import names.

LLM 經常虛構不存在的庫或使用錯誤的 import 名稱。

### Solution (解決方案)

**ALWAYS provide an explicit whitelist of allowed libraries in the prompt.**

**始終在 prompt 中提供明確的允許庫白名單。**

✅ **CORRECT Prompt:**
```
ALLOWED LIBRARIES (explicitly):
- httpx (NOT requests)
- Pillow (import as: from PIL import Image, NOT import pillow)
- pathlib.Path
- aiofiles
- cairosvg

NEVER use:
- requests (blocking, not allowed)
- urllib (not async)
- PIL directly (use: from PIL import Image)
```

❌ **WRONG Prompt:**
```
Use appropriate HTTP library
Use standard image processing libraries
```

### Why This Works (為什麼有效)

- Explicit list → LLM follows exactly
- Shows correct import syntax → prevents import errors
- Lists forbidden alternatives → prevents wrong choices

---

## 🚫 RULE 2: FORMAT SPECIFICATION WITH EXAMPLES (格式規範附示例)

### Problem (問題)

LLMs generate inconsistent output formats when given abstract descriptions.

當給予抽象描述時，LLM 生成不一致的輸出格式。

### Solution (解決方案)

**ALWAYS show the EXACT format with a complete example.**

**始終顯示完整示例的確切格式。**

✅ **CORRECT Prompt:**
```python
Return format (MANDATORY):
{
    "ok": True,          # ← EXACTLY this key, not "status" or "success"
    "output": {...},     # ← EXACTLY this key, not "data" or "result"
    "error": None,       # ← EXACTLY this key, not "errors" or "exception"
    "meta": {...}        # ← EXACTLY this key, not "metadata"
}

EXAMPLE (copy this structure):
return {
    "ok": True,
    "output": {"path": "/tmp/file.jpg", "size": 12345},
    "error": None,
    "meta": {"module": self.module_name, "execution_time": 0.123}
}
```

❌ **WRONG Prompt:**
```
Return a dictionary with success status, output data, error info, and metadata.
```

### Why This Works (為什麼有效)

- Exact key names → no variation
- Inline comments → emphasizes requirements
- Complete example → LLM copies the pattern

---

## 🚫 RULE 3: NEGATIVE EXAMPLES (反面示例)

### Problem (問題)

LLMs often make the same mistakes even when told what NOT to do.

即使被告知不要做什麼，LLM 仍經常犯同樣的錯誤。

### Solution (解決方案)

**Show WRONG examples with clear ❌ markers, followed by CORRECT examples with ✅ markers.**

**顯示帶有明確 ❌ 標記的錯誤示例，然後是帶有 ✅ 標記的正確示例。**

✅ **CORRECT Prompt:**
```python
❌ WRONG - Do NOT do this:
async def execute(self):
    import httpx  # ← NEVER import inside execute()!
    if url.startswith("http://"):  # ← Missing self.!

✅ CORRECT - Do this instead:
# imports at file top
import httpx

async def execute(self):
    # No imports here
    if self.url.startswith("http://"):  # ← Use self.!
```

❌ **WRONG Prompt:**
```
Don't import inside functions. Always use self. prefix.
```

### Why This Works (為什麼有效)

- Visual contrast (❌ vs ✅) → clear distinction
- Shows exact mistakes → LLM learns what to avoid
- Provides immediate correction → LLM sees the fix

---

## 🚫 RULE 4: MANDATORY vs OPTIONAL (必需 vs 可選)

### Problem (問題)

LLMs treat all requirements as optional suggestions unless explicitly marked as MANDATORY.

除非明確標記為 MANDATORY，否則 LLM 將所有要求視為可選建議。

### Solution (解決方案)

**Use MANDATORY, REQUIRED, MUST keywords for critical requirements.**

**對關鍵要求使用 MANDATORY、REQUIRED、MUST 關鍵詞。**

✅ **CORRECT Prompt:**
```
🔒 MANDATORY REQUIREMENTS (non-negotiable):

1. ✅ MUST return unified format ({"ok": bool, "output": {}, ...})
2. ✅ MUST include URL validation for URL parameters
3. ✅ MUST use async I/O for network operations
4. ✅ MUST have 3+ specific exception types

⚠️  OPTIONAL ENHANCEMENTS (nice to have):

- Performance optimizations
- Additional logging
- Extra validation layers
```

❌ **WRONG Prompt:**
```
It's good practice to return a consistent format.
Consider adding URL validation.
Async I/O is recommended for network operations.
```

### Why This Works (為什麼有效)

- MUST → LLM prioritizes
- Clear separation → LLM knows what's required
- Visual markers (🔒, ✅, ⚠️) → enhances importance

---

## 🚫 RULE 5: PROHIBITION WITH CONSEQUENCES (禁止附後果)

### Problem (問題)

LLMs ignore "don't do X" unless there's a clear consequence.

LLM 忽略「不要做 X」，除非有明確的後果。

### Solution (解決方案)

**State the prohibition AND the deduction/failure consequence.**

**聲明禁止事項及扣分/失敗後果。**

✅ **CORRECT Prompt:**
```
❌ RULE: NO Placeholder Code

Forbidden patterns:
- # TODO → -0.5 points (instant fail)
- # placeholder → -0.5 points (instant fail)
- pass without logic → -0.5 points (instant fail)
- raise NotImplementedError → -0.5 points (instant fail)

⚠️  Any module with placeholder code will score < 9.8 and FAIL PR review.
```

❌ **WRONG Prompt:**
```
Avoid using placeholder code like TODO or pass.
```

### Why This Works (為什麼有效)

- Explicit consequence → LLM takes seriously
- Point deduction → quantifies impact
- "instant fail" → creates urgency

---

## 🚫 RULE 6: CONTEXT REPETITION (上下文重複)

### Problem (問題)

LLMs forget context from earlier in the prompt by the time they generate code.

當生成代碼時，LLM 忘記 prompt 早期的上下文。

### Solution (解決方案)

**Repeat critical requirements at the START, MIDDLE, and END of the prompt.**

**在 prompt 的開始、中間和結尾重複關鍵要求。**

✅ **CORRECT Prompt Structure:**
```
[START]
🎯 MISSION: Generate PRODUCTION-READY module with 9.8+/10 quality.
Key requirement: Unified return format {"ok": bool, ...}

[MIDDLE - Before examples]
⚠️  REMINDER: ALL returns MUST use {"ok": bool, "output": {}, "error": None/Dict, "meta": {}}

[END - Before output]
📤 FINAL CHECKLIST before submitting:
- ✅ ALL returns use {"ok": bool, "output": {}, "error": None/Dict, "meta": {}}
- ✅ NO imports inside execute()
- ✅ ALL variables use self. prefix
```

❌ **WRONG Prompt:**
```
[START]
Use unified return format.

[20 paragraphs of other content...]

[END]
Generate the code now.
```

### Why This Works (為什麼有效)

- Recency bias → LLM remembers recent content
- Multiple exposures → reinforces requirement
- Final checklist → LLM self-verifies

---

## 🚫 RULE 7: SINGLE RESPONSIBILITY PER INSTRUCTION (每條指令單一職責)

### Problem (問題)

Complex multi-part instructions get partially ignored.

複雜的多部分指令會被部分忽略。

### Solution (解決方案)

**Break down complex rules into separate, numbered instructions.**

**將複雜規則分解為單獨的編號指令。**

✅ **CORRECT Prompt:**
```
Error Handling Requirements:

1. ✅ MUST catch httpx.HTTPStatusError
   - Return {"ok": False, "error": {"type": "HTTPStatusError", ...}, ...}

2. ✅ MUST catch httpx.RequestError
   - Return {"ok": False, "error": {"type": "RequestError", ...}, ...}

3. ✅ MUST catch IOError
   - Return {"ok": False, "error": {"type": "IOError", ...}, ...}

4. ✅ MUST catch generic Exception as last resort
   - Return {"ok": False, "error": {"type": "UnexpectedError", ...}, ...}
```

❌ **WRONG Prompt:**
```
Catch specific exceptions like HTTPStatusError, RequestError, IOError, and have a generic Exception handler, and make sure each returns the right error format with ok=False and error dict with type and message.
```

### Why This Works (為什麼有效)

- One rule per line → easy to follow
- Numbered → LLM checks off each item
- Consistent structure → pattern recognition

---

## 🚫 RULE 8: OUTPUT FORMAT ENFORCEMENT (輸出格式強制)

### Problem (問題)

LLMs add extra commentary, explanations, or markdown when you just want code.

當你只想要代碼時，LLM 添加額外的註釋、解釋或 markdown。

### Solution (解決方案)

**Use `response_format={"type": "json_object"}` with OpenAI API and specify exact JSON schema.**

**使用 OpenAI API 的 `response_format={"type": "json_object"}` 並指定確切的 JSON schema。**

✅ **CORRECT Prompt:**
```python
# In code
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    response_format={"type": "json_object"},  # ← Forces JSON output
    temperature=0.1  # ← Lower = more deterministic
)

# In prompt
📤 OUTPUT FORMAT (return ONLY valid JSON, no markdown, no explanations):
{
  "module_id": "string",
  "category": "string",
  "description": "string",
  "implementation_code": "string"
}
```

❌ **WRONG Prompt:**
```python
# No response_format specified
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    temperature=0.7  # ← Higher = more creative/unpredictable
)

# Vague instruction
Return the module details in JSON format.
```

### Why This Works (為什麼有效)

- `response_format` → API enforces JSON
- Low temperature → reduces creativity/variance
- "ONLY valid JSON" → no extra text

---

## 🚫 RULE 9: VALIDATION AFTER GENERATION (生成後驗證)

### Problem (問題)

Even with perfect prompts, LLMs occasionally produce invalid output.

即使有完美的 prompt，LLM 偶爾也會產生無效的輸出。

### Solution (解決方案)

**ALWAYS validate LLM output before using it.**

**使用前始終驗證 LLM 輸出。**

✅ **CORRECT Implementation:**
```python
def _generate_module_spec(self, module_name: str, problem: str) -> Optional[Dict]:
    response = client.chat.completions.create(...)
    spec = json.loads(response.choices[0].message.content)

    # VALIDATION (critical!)
    required_fields = ["module_id", "category", "description", "implementation_code"]
    if not all(k in spec for k in required_fields):
        print(f"❌ Missing required fields")
        return None

    impl_code = spec.get("implementation_code", "")

    # Check code length
    if len(impl_code.strip()) < 100:
        print(f"❌ Code too short")
        return None

    # Check for bad patterns
    bad_patterns = ["TODO", "placeholder", "implement here"]
    for pattern in bad_patterns:
        if pattern.lower() in impl_code.lower():
            print(f"❌ Found bad pattern: {pattern}")
            return None

    # Check for nested functions
    if "\n    def " in impl_code or "\n    async def " in impl_code:
        print(f"❌ Found nested function definition")
        return None

    return spec
```

❌ **WRONG Implementation:**
```python
def _generate_module_spec(self, module_name: str, problem: str) -> Dict:
    response = client.chat.completions.create(...)
    spec = json.loads(response.choices[0].message.content)
    return spec  # ← No validation!
```

### Why This Works (為什麼有效)

- Catches LLM errors → prevents bad code from being used
- Provides feedback → can retry generation
- Multiple checks → catches different failure modes

---

## 🚫 RULE 10: PROGRESSIVE REFINEMENT (漸進式改進)

### Problem (問題)

Trying to get perfect output in one shot often fails.

試圖一次獲得完美輸出通常會失敗。

### Solution (解決方案)

**Use a multi-stage process: Generate → Validate → Refine → Re-validate.**

**使用多階段流程：生成 → 驗證 → 改進 → 重新驗證。**

✅ **CORRECT Flow:**
```
Stage 1: Generate module spec (GPT-4o)
  ↓
Stage 2: Validate spec (Python validator)
  ├─ Pass → Continue
  └─ Fail → Regenerate (max 3 attempts)
  ↓
Stage 3: Generate Python file (ModuleGenerator)
  ↓
Stage 4: Strict PR Review (StrictPRReviewer)
  ├─ Score >= 9.8 → Accept
  └─ Score < 9.8 → Regenerate from Stage 1
  ↓
Stage 5: Test execution (Flyto2 Engine)
  ├─ Pass → Success!
  └─ Fail → Regenerate from Stage 1
```

❌ **WRONG Flow:**
```
Stage 1: Generate complete module (GPT-4o)
  ↓
Done (no validation, no refinement)
```

### Why This Works (為什麼有效)

- Early validation → catches errors before they propagate
- Multiple checkpoints → ensures quality at each stage
- Regeneration logic → recovers from failures

---

## 📊 SUMMARY CHECKLIST (總結檢查清單)

When creating prompts for LLMs:

- [ ] ✅ Provide explicit library whitelist
- [ ] ✅ Show exact format with complete examples
- [ ] ✅ Include negative examples (❌ WRONG vs ✅ CORRECT)
- [ ] ✅ Use MANDATORY/MUST keywords for critical requirements
- [ ] ✅ State prohibitions with consequences (deduction points)
- [ ] ✅ Repeat critical requirements at START, MIDDLE, END
- [ ] ✅ Break complex rules into numbered single-responsibility instructions
- [ ] ✅ Use `response_format={"type": "json_object"}` and low temperature
- [ ] ✅ Validate output after generation
- [ ] ✅ Implement progressive refinement (generate → validate → refine)

---

## 🎯 EXPECTED OUTCOME (預期結果)

With proper prompt sanitization:

**Before:**
- 50-60% of generations pass quality review
- Inconsistent output formats
- Frequent hallucinated libraries
- Placeholder code common

**After:**
- 90-95% of generations pass quality review
- Consistent output formats
- No hallucinated libraries
- Production-ready code

---

**Version:** 1.0
**Last Updated:** 2025-12-04
**Maintained by:** Flyto2 AI Evolution Team
