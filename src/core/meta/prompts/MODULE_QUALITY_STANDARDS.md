# 📊 Flyto2 Module Quality Standards (企業級品質標準)

## 🎯 Quality Score: 10 Core Indicators

Every Flyto2 atomic module MUST meet these 10 quality standards to achieve 9.8+/10 score.

---

## ✅ 1. UNIFIED RETURN FORMAT (統一回傳格式)

**Score: 2.0 points**

All modules MUST return this exact structure:

```python
{
    "ok": True,           # Boolean: operation success
    "output": {...},      # Dict: actual results
    "error": None,        # Dict or None: error details
    "meta": {             # Dict: metadata
        "module": self.module_name,
        "timestamp": "...",
        "execution_time": 0.123
    }
}
```

❌ **Deductions:**
- Using `{"status": "success"}` instead of `{"ok": True}`: -2.0
- Missing `output` field: -1.0
- Missing `error` field: -0.5
- Missing `meta` field: -0.5

✅ **Why this matters:**
- Engine can chain modules seamlessly
- LLM can reason about outputs
- PR grader can validate structure
- Evolution system can track metrics

---

## ✅ 2. NO DUPLICATE IMPORTS (無重複 import)

**Score: 1.0 point**

All imports MUST be at the file top, NEVER inside functions.

❌ **Wrong:**
```python
async def execute(self):
    import httpx  # ← Duplicate!
    from pathlib import Path  # ← Duplicate!
```

✅ **Correct:**
```python
# At file top
import httpx
from pathlib import Path

async def execute(self):
    # No imports here
```

**Deduction:** -1.0 for ANY import inside execute()

---

## ✅ 3. PROPER VARIABLE REFERENCES (正確使用 self.)

**Score: 1.0 point**

All class properties MUST use `self.` prefix.

❌ **Wrong:**
```python
if not url.startswith("http://"):  # ← Missing self.
```

✅ **Correct:**
```python
if not self.url.startswith("http://"):  # ← Correct
```

**Deduction:** -0.2 per instance (max -1.0)

---

## ✅ 4. NO NESTED FUNCTIONS (無嵌套函數)

**Score: 0.5 points**

NEVER define functions inside execute().

❌ **Wrong:**
```python
async def execute(self):
    def helper():  # ← Nested function!
        pass
```

**Deduction:** -0.5 for ANY nested function

---

## ✅ 5. CLEAN SEPARATION: validate_params vs execute

**Score: 1.0 point**

- `validate_params()`: ONLY check params and assign to self
- `execute()`: ONLY business logic

❌ **Wrong:**
```python
def validate_params(self):
    self.url = self.params["url"]
    # ❌ NO business logic here!
    response = httpx.get(self.url)
```

✅ **Correct:**
```python
def validate_params(self):
    if "url" not in self.params:
        raise ValueError("Missing parameter: url")
    self.url = self.params["url"]
    # Only validation, no logic
```

**Deduction:** -1.0 if business logic in validate_params()

---

## ✅ 6. ASYNC I/O PROPERLY USED (正確使用異步)

**Score: 1.0 point**

Network operations MUST use async libraries.

❌ **Wrong:**
```python
import requests  # ← Blocking!
response = requests.get(url)
```

✅ **Correct:**
```python
import httpx
async with httpx.AsyncClient() as client:
    response = await client.get(self.url)
```

**Deduction:** -1.0 for blocking I/O on network

---

## ✅ 7. COMPREHENSIVE ERROR HANDLING (完整錯誤處理)

**Score: 1.0 point**

Must catch specific exceptions and return proper error format.

❌ **Wrong:**
```python
try:
    result = await client.get(url)
except:  # ← Too broad!
    pass
```

✅ **Correct:**
```python
try:
    result = await client.get(self.url)
except httpx.HTTPStatusError as e:
    return {
        "ok": False,
        "output": {},
        "error": {"type": "HTTPStatusError", "message": str(e)},
        "meta": {"module": self.module_name}
    }
except httpx.RequestError as e:
    return {
        "ok": False,
        "output": {},
        "error": {"type": "RequestError", "message": str(e)},
        "meta": {"module": self.module_name}
    }
```

**Deduction:**
- No error handling: -1.0
- Only generic `except Exception`: -0.5
- Less than 3 specific exception types: -0.3

---

## ✅ 8. SECURITY VALIDATIONS (安全性驗證)

**Score: 1.5 points**

For modules with URLs or file operations:

**URL modules MUST have:**
- URL format validation (http/https)
- Content-Type validation (if downloading)
- File size limit check (if downloading)

**File modules MUST have:**
- Path traversal prevention
- File extension whitelist
- Size limits

❌ **Wrong:**
```python
async def execute(self):
    response = await client.get(self.url)  # ← No validation!
```

✅ **Correct:**
```python
async def execute(self):
    # URL validation
    if not (self.url.startswith("http://") or self.url.startswith("https://")):
        return {
            "ok": False,
            "output": {},
            "error": {"message": "Invalid URL format"},
            "meta": {"module": self.module_name}
        }

    # Content-Type check
    head = await client.head(self.url)
    if not head.headers.get("content-type", "").startswith("image/"):
        return {
            "ok": False,
            "output": {},
            "error": {"message": "Invalid content type"},
            "meta": {"module": self.module_name}
        }
```

**Deduction:**
- Missing URL validation: -0.5
- Missing Content-Type check (download): -0.5
- Missing size limit (download): -0.5

---

## ✅ 9. NO PLACEHOLDER CODE (無佔位符)

**Score: 0.5 points**

Code must be production-ready. NO:
- `# TODO`
- `# placeholder`
- `pass` without logic
- `raise NotImplementedError`

**Deduction:** -0.5 for ANY placeholder

---

## ✅ 10. COMPLETE DOCSTRINGS (完整文檔)

**Score: 0.5 points**

Module MUST have:
- Class docstring
- Parameter descriptions
- Return value description
- Example (optional but recommended)

✅ **Correct:**
```python
@register_module("image.download")
class ImageDownload(BaseModule):
    """
    Download an image from a URL and save to local path.

    This module performs secure image downloading with validation:
    - URL format check (http/https only)
    - Content-Type validation (image/* only)
    - File size limits (50 MB max)
    - Streaming download for large files

    Parameters:
        url (str): Image URL to download
        save_path (str): Local file path to save

    Returns:
        {
            "ok": True,
            "output": {
                "path": "/path/to/file.jpg",
                "size": 123456,
                "content_type": "image/jpeg"
            },
            "error": None,
            "meta": {...}
        }
    """
```

**Deduction:**
- Missing class docstring: -0.3
- Missing parameter docs: -0.2

---

## 📊 GRADING SCALE

| Score | Grade | Status |
|-------|-------|--------|
| 9.8 - 10.0 | A+ | ✅ Ready for PR |
| 9.5 - 9.7 | A | ⚠️ Minor improvements needed |
| 9.0 - 9.4 | B+ | ⚠️ Significant improvements needed |
| < 9.0 | B or below | ❌ Reject - regenerate |

---

## 🎯 TARGET: 9.8+/10

For a module to pass Flyto2 strict quality control and trigger GitHub PR creation:
- Must score 9.8+/10
- Must pass 3 consecutive generations
- Must be production-ready
- Must follow ALL 10 standards

---

## 💡 QUICK CHECKLIST

Before submitting a module, verify:

- [ ] Returns `{"ok": bool, "output": {}, "error": None/Dict, "meta": {}}`
- [ ] All imports at file top
- [ ] All variables use `self.` prefix
- [ ] No nested functions
- [ ] validate_params() only validates
- [ ] execute() uses async I/O for network
- [ ] Catches specific exceptions
- [ ] Has security validations (URL/file)
- [ ] No TODO/placeholder/pass
- [ ] Has complete docstrings

---

**Last updated:** 2025-12-04
**Version:** 1.0
**Status:** Enterprise Production Standard
