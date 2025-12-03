# 🎯 PR GRADER RULES (PR 評分規則)

**Version:** 2.0 Enterprise
**Language:** Bilingual (EN/ZH)
**Target:** Flyto2 Module Quality Assessment
**Scoring Range:** 0-10.0

---

## 📊 SCORING SYSTEM (評分系統)

**Base Score:** 10.0 points

**Grading Scale:**
| Score | Grade | Status |
|-------|-------|--------|
| 9.8 - 10.0 | A+ | ✅ PASS - Ready for PR |
| 9.5 - 9.7 | A | ⚠️ Minor improvements needed |
| 9.0 - 9.4 | B+ | ⚠️ Significant improvements needed |
| 8.0 - 8.9 | B | ❌ FAIL - Regenerate |
| < 8.0 | C or below | ❌ FAIL - Regenerate |

**Pass Threshold:** 9.8/10.0

---

## ✅ CATEGORY 1: UNIFIED RETURN FORMAT (統一回傳格式)

**Weight:** 2.0 points (CRITICAL)

### Check 1.1: Unified Structure (1.5 points)

Module MUST return this EXACT structure:

```python
{
    "ok": bool,
    "output": {...},
    "error": None or {...},
    "meta": {...}
}
```

**Checks:**
- ✅ Has `"ok":` key → +0.4
- ✅ Has `"output":` key → +0.4
- ✅ Has `"error":` key → +0.4
- ✅ Has `"meta":` key → +0.3

**Deductions:**
- ❌ Uses `"status":` instead of `"ok":` → -1.5 (CRITICAL)
- ❌ Missing `"output"` key → -0.4
- ❌ Missing `"error"` key → -0.4
- ❌ Missing `"meta"` key → -0.3

### Check 1.2: Consistent Usage (0.5 points)

ALL return statements must use the same format.

**Pattern to find:**
```python
return {
    "ok":
    "output":
    "error":
    "meta":
}
```

**Deductions:**
- ❌ Inconsistent return format across different returns → -0.5

---

## ✅ CATEGORY 2: NO DUPLICATE IMPORTS (無重複 import)

**Weight:** 1.0 point

### Check 2.1: Top-Level Imports Only

ALL imports MUST be at file top.

**Pattern to detect:**
```python
# ❌ WRONG
async def execute(self):
    import httpx  # ← FAIL!
```

**Deductions:**
- ❌ ANY import inside `execute()` → -1.0
- ❌ ANY import inside `validate_params()` → -1.0

---

## ✅ CATEGORY 3: PROPER VARIABLE REFERENCES (正確變數引用)

**Weight:** 1.0 point

### Check 3.1: self. Prefix Required

ALL class properties MUST use `self.` prefix.

**Pattern to detect:**
```python
# ❌ WRONG
if not url.startswith("http://"):  # Missing self.!
    path = Path(save_path)  # Missing self.!

# ✅ CORRECT
if not self.url.startswith("http://"):
    path = Path(self.save_path)
```

**Detection method:**
1. Extract all params from `validate_params()` (e.g., `self.url = ...`)
2. Search for bare usage (e.g., `url.startswith` instead of `self.url.startswith`)

**Deductions:**
- ❌ -0.2 per instance of missing `self.` (max -1.0)

---

## ✅ CATEGORY 4: NO NESTED FUNCTIONS (無嵌套函數)

**Weight:** 0.5 points

### Check 4.1: No Function Definitions Inside execute()

NEVER define functions inside `execute()` or `validate_params()`.

**Pattern to detect:**
```python
# ❌ WRONG
async def execute(self):
    def helper():  # ← FAIL!
        pass

    async def async_helper():  # ← FAIL!
        pass
```

**Deductions:**
- ❌ ANY nested `def` → -0.5
- ❌ ANY nested `async def` → -0.5

---

## ✅ CATEGORY 5: CLEAN SEPARATION (職責分離)

**Weight:** 1.0 point

### Check 5.1: validate_params() = Validation Only

`validate_params()` should ONLY:
- Check if params exist
- Assign to `self.{param}`
- Raise `ValueError` if missing

Should NOT:
- Make API calls
- Perform business logic
- Access files
- Do computations

**Pattern to detect:**
```python
# ❌ WRONG
def validate_params(self):
    self.url = self.params["url"]
    response = httpx.get(self.url)  # ← Business logic! FAIL!
```

**Deductions:**
- ❌ Contains `await` → -0.5
- ❌ Contains `httpx.` or `aiohttp.` → -0.5
- ❌ Contains `Path().read` or file operations → -0.5
- ❌ Any business logic → -1.0 (max deduction)

---

## ✅ CATEGORY 6: ASYNC I/O PROPERLY USED (正確異步)

**Weight:** 1.0 point

### Check 6.1: Network Operations Use Async

Network operations MUST use async libraries.

**Allowed:**
- `httpx.AsyncClient`
- `aiohttp.ClientSession`

**NOT Allowed:**
- `requests.get/post`
- `urllib.request`

**Pattern to detect:**
```python
# ❌ WRONG
import requests
response = requests.get(url)

# ✅ CORRECT
import httpx
async with httpx.AsyncClient() as client:
    response = await client.get(self.url)
```

**Deductions:**
- ❌ Uses `requests` → -1.0
- ❌ Uses `urllib.request` → -1.0

---

## ✅ CATEGORY 7: COMPREHENSIVE ERROR HANDLING (完整錯誤處理)

**Weight:** 1.0 point

### Check 7.1: Multiple Specific Exception Types (0.7 points)

MUST catch at least 3 specific exception types.

**Scoring:**
- 1 specific exception → +0.2
- 2 specific exceptions → +0.4
- 3+ specific exceptions → +0.7

**Good patterns:**
```python
except httpx.HTTPStatusError as e:
except httpx.RequestError as e:
except IOError as e:
except ValueError as e:
except Exception as e:  # Generic catch-all is OK as last resort
```

**Deductions:**
- ❌ Only generic `except Exception` → -0.5
- ❌ No error handling → -1.0

### Check 7.2: Error Return Format (0.3 points)

Error responses MUST use unified format:

```python
return {
    "ok": False,
    "output": {},
    "error": {
        "type": "ExceptionName",
        "message": str(e)
    },
    "meta": {...}
}
```

**Deductions:**
- ❌ Error response doesn't use unified format → -0.3

---

## ✅ CATEGORY 8: SECURITY VALIDATIONS (安全性驗證)

**Weight:** 1.5 points

### Check 8.1: URL Validation (0.5 points)

For modules with URL parameters:

**MUST have:**
```python
if not (self.url.startswith("http://") or self.url.startswith("https://")):
    return {
        "ok": False,
        "error": {"message": "Invalid URL format"},
        ...
    }
```

**Detection:**
- Look for pattern: `startswith("http://")` or `startswith("https://")`

**Deductions:**
- ❌ Missing URL validation → -0.5

### Check 8.2: Content-Type Validation (0.5 points)

For download/fetch modules:

**MUST have:**
```python
content_type = response.headers.get("content-type", "").lower()
if not content_type.startswith("image/"):  # or appropriate type
    return {"ok": False, "error": {...}, ...}
```

**Deductions:**
- ❌ Missing Content-Type check → -0.5

### Check 8.3: File Size Limit (0.5 points)

For download/fetch modules:

**MUST have:**
```python
content_length = int(response.headers.get("content-length", 0))
max_size = 50 * 1024 * 1024  # Or similar limit
if content_length > max_size:
    return {"ok": False, "error": {...}, ...}
```

**Deductions:**
- ❌ Missing file size check → -0.5

---

## ✅ CATEGORY 9: NO PLACEHOLDER CODE (無佔位符)

**Weight:** 0.5 points

### Check 9.1: Production-Ready Code

Code must be complete and executable. NO:
- `# TODO`
- `# placeholder`
- `pass` without logic
- `raise NotImplementedError`
- Comments like `# implement here`

**Deductions:**
- ❌ ANY placeholder found → -0.5

---

## ✅ CATEGORY 10: COMPLETE DOCUMENTATION (完整文檔)

**Weight:** 0.5 points

### Check 10.1: Class Docstring (0.3 points)

Class MUST have detailed docstring with:
- Description
- Parameters with types
- Return format
- Example (optional)

**Deductions:**
- ❌ Missing class docstring → -0.3

### Check 10.2: Parameter Documentation (0.2 points)

Parameters MUST be documented in docstring.

**Deductions:**
- ❌ Missing parameter docs → -0.2

---

## 🏆 STRENGTH RECOGNITION (優點識別)

In addition to scoring, identify strengths:

**Basic Quality:**
- ✅ 包含完整 docstring
- ✅ 包含 type hints
- ✅ 包含錯誤處理
- ✅ 包含參數驗證

**Advanced Quality:**
- ✅ 無重複 import
- ✅ 通過安全性檢查
- ✅ 錯誤處理明確具體 (3+ exception types)
- ✅ 多層錯誤處理 (5+ except blocks)
- ✅ 統一的回傳格式 (包含 ok, output, error, meta)
- ✅ 無嵌套函數定義
- ✅ 程式碼長度適中 (80-150 lines)
- ✅ 使用 async I/O for network
- ✅ URL 格式驗證present
- ✅ Content-Type 驗證 present
- ✅ 檔案大小限制 present

---

## 📝 REPORT FORMAT (報告格式)

PR Grader MUST return:

```python
{
    "score": 9.8,  # float
    "grade": "A+",  # str
    "pass": True,  # bool
    "issues": [  # List[Dict]
        {
            "severity": "medium",
            "message": "缺少 URL 格式驗證",
            "deduction": 0.5
        }
    ],
    "strengths": [  # List[str]
        "✅ 包含完整 docstring",
        "✅ 統一的回傳格式",
        "✅ 無重複 import"
    ],
    "recommendations": [  # List[str]
        "建議添加 URL 格式驗證"
    ]
}
```

---

## 🎯 QUALITY GATES (品質門檻)

**To achieve 9.8+/10:**

**MUST have (required):**
- ✅ Unified return format: `{"ok": bool, "output": {}, "error": None/Dict, "meta": {}}`
- ✅ No duplicate imports
- ✅ Proper variable references (self.)
- ✅ No nested functions
- ✅ 3+ specific exception types

**For URL/Download modules (required):**
- ✅ URL format validation
- ✅ Content-Type validation (for downloads)
- ✅ File size limits (for downloads)

**MUST NOT have:**
- ❌ Any placeholder code
- ❌ Business logic in validate_params()
- ❌ Blocking I/O for network operations

---

## 🚀 IMPLEMENTATION CHECKLIST (實施檢查清單)

When implementing the PR Grader:

- [ ] Check unified return format (2.0 points)
- [ ] Check no duplicate imports (1.0 point)
- [ ] Check proper variable references (1.0 point)
- [ ] Check no nested functions (0.5 points)
- [ ] Check clean separation (1.0 point)
- [ ] Check async I/O usage (1.0 point)
- [ ] Check error handling (1.0 point)
- [ ] Check security validations (1.5 points)
- [ ] Check no placeholders (0.5 points)
- [ ] Check documentation (0.5 points)

**Total:** 10.0 points

---

**Version:** 2.0 Enterprise
**Last Updated:** 2025-12-04
**Maintained by:** Flyto2 AI Evolution Team
