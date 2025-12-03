# 🧪 TEST GENERATOR PROMPT (測試生成規範)

**Version:** 2.0
**Language:** Bilingual (EN/ZH)
**Target:** Flyto2 Module Test Generation
**Quality Standard:** Complete & Executable

---

## 🎯 MISSION (任務)

Generate a **complete, executable YAML test** for every Flyto2 atomic module.

為每個 Flyto2 原子模組生成**完整、可執行的 YAML 測試**。

---

## 📋 TEST STRUCTURE TEMPLATE (測試結構模板)

```yaml
name: "Test {module.id}"
description: "Complete test suite for {module.id} module - Auto-generated"

steps:
  # ========================================
  # TEST 1: Basic functionality
  # ========================================
  - id: test_basic
    module: {module.id}
    params:
      param1: "value1"
      param2: "value2"
    description: "Test basic functionality with valid inputs"

  # ========================================
  # TEST 2: Verify return format
  # ========================================
  - id: verify_return_format
    module: test.assert_structure
    params:
      value: "${test_basic.result}"
      required_keys: ["ok", "output", "error", "meta"]
      message: "{module.id} must return unified format"

  # ========================================
  # TEST 3: Verify success case
  # ========================================
  - id: verify_success
    module: test.assert_equals
    params:
      actual: "${test_basic.result.ok}"
      expected: true
      message: "{module.id} should return ok=true for valid input"

  # ========================================
  # TEST 4: Test error handling
  # ========================================
  - id: test_error_case
    module: {module.id}
    params:
      param1: "invalid_value"  # Intentionally invalid
    description: "Test error handling with invalid input"

  # ========================================
  # TEST 5: Verify error format
  # ========================================
  - id: verify_error_format
    module: test.assert_structure
    params:
      value: "${test_error_case.result}"
      required_keys: ["ok", "output", "error", "meta"]
      message: "{module.id} error response must have unified format"

  # ========================================
  # TEST 6: Verify error details
  # ========================================
  - id: verify_error_details
    module: test.assert_equals
    params:
      actual: "${test_error_case.result.ok}"
      expected: false
      message: "{module.id} should return ok=false for invalid input"

  # ========================================
  # TEST 7: Performance test (if applicable)
  # ========================================
  - id: test_performance
    module: {module.id}
    params:
      param1: "value1"
      param2: "value2"
    description: "Performance test - should complete within reasonable time"

  # ========================================
  # TEST 8: Verify execution time
  # ========================================
  - id: verify_execution_time
    module: test.assert_less_than
    params:
      actual: "${test_performance.result.meta.execution_time}"
      expected: 10.0  # 10 seconds max
      message: "{module.id} should complete within 10 seconds"
```

---

## 🚫 STRICT RULES (嚴格規則)

### ❌ RULE 1: ALWAYS Test Return Format

**English:**
Every test MUST verify the module returns:
```python
{
    "ok": bool,
    "output": {...},
    "error": None or {...},
    "meta": {...}
}
```

**中文：**
每個測試必須驗證模組返回：
```python
{
    "ok": bool,
    "output": {...},
    "error": None or {...},
    "meta": {...}
}
```

---

### ❌ RULE 2: Test Both Success AND Error Cases

**English:**
- At least 1 test for **success case** (ok=true)
- At least 1 test for **error case** (ok=false)

**中文：**
- 至少 1 個**成功案例**測試（ok=true）
- 至少 1 個**錯誤案例**測試（ok=false）

---

### ❌ RULE 3: Use Variable References

**English:**
Use `${step_id.result}` to access previous step outputs

**中文：**
使用 `${step_id.result}` 訪問前一步驟輸出

```yaml
# ✅ CORRECT
- id: verify_result
  module: test.assert_not_null
  params:
    value: "${test_basic.result.output}"
```

---

### ❌ RULE 4: NO Hardcoded Assertions on Dynamic Data

**English:**
Don't assert exact values for timestamps, random IDs, etc.

**中文：**
不對時間戳、隨機 ID 等動態數據進行精確斷言

```yaml
# ❌ WRONG
- module: test.assert_equals
  params:
    actual: "${result.meta.timestamp}"
    expected: "2025-12-04T00:00:00"  # ← Will fail!

# ✅ CORRECT
- module: test.assert_not_null
  params:
    value: "${result.meta.timestamp}"
```

---

### ❌ RULE 5: Test Descriptions Must Be Clear

**English:**
Every step MUST have a clear `description` field

**中文：**
每個步驟必須有清晰的 `description` 欄位

```yaml
# ❌ WRONG
- id: test1
  module: image.download
  params: {...}
  # No description!

# ✅ CORRECT
- id: test_basic_download
  module: image.download
  params: {...}
  description: "Test basic image download with valid URL"
```

---

## 📦 TEST CATEGORIES (測試類別)

### 1. Basic Functionality Test (基本功能測試)

Test the module with **valid inputs** and verify it returns `ok=true`.

```yaml
- id: test_basic
  module: {module.id}
  params:
    param1: "valid_value"
  description: "Test basic functionality"
```

### 2. Return Format Test (返回格式測試)

Verify the response has required keys: `ok`, `output`, `error`, `meta`.

```yaml
- id: verify_format
  module: test.assert_structure
  params:
    value: "${test_basic.result}"
    required_keys: ["ok", "output", "error", "meta"]
```

### 3. Error Handling Test (錯誤處理測試)

Test the module with **invalid inputs** and verify it returns `ok=false`.

```yaml
- id: test_error
  module: {module.id}
  params:
    param1: "invalid_value"
  description: "Test error handling"

- id: verify_error
  module: test.assert_equals
  params:
    actual: "${test_error.result.ok}"
    expected: false
```

### 4. Security Test (安全性測試)

Test with **malicious inputs** to verify security validations work.

```yaml
# For URL modules
- id: test_security_url
  module: {module.id}
  params:
    url: "javascript:alert(1)"  # XSS attempt
  description: "Test URL validation rejects non-http(s) URLs"

- id: verify_security
  module: test.assert_equals
  params:
    actual: "${test_security_url.result.ok}"
    expected: false
```

### 5. Performance Test (性能測試)

Verify execution completes within reasonable time.

```yaml
- id: test_performance
  module: {module.id}
  params: {...}
  description: "Performance test"

- id: verify_time
  module: test.assert_less_than
  params:
    actual: "${test_performance.result.meta.execution_time}"
    expected: 5.0  # 5 seconds
```

---

## 🎯 COVERAGE REQUIREMENTS (覆蓋率要求)

Every test suite MUST include:

✅ **1. Basic functionality test** (valid input → ok=true)
✅ **2. Return format validation** (has ok, output, error, meta)
✅ **3. Error handling test** (invalid input → ok=false)
✅ **4. Output structure validation** (output has expected keys)
✅ **5. Metadata validation** (meta has module name, execution_time)

**Minimum:** 5 test steps
**Recommended:** 8+ test steps

---

## 📤 OUTPUT FORMAT (輸出格式)

Return the test as a **valid YAML string**:

```yaml
name: "Test {module.id}"
description: "{module description} - Auto-generated test"

steps:
  - id: test_basic
    module: {module.id}
    params:
      param1: "value1"
    description: "Basic functionality test"

  - id: verify_result
    module: test.assert_not_null
    params:
      value: "${test_basic.result}"
      message: "{module.id} should return a result"

  # ... more steps ...
```

---

## 🏆 QUALITY CHECKLIST (品質檢查清單)

Before submitting the test:

- [x] Has at least 5 test steps ✅ Implemented in TestGenerator
- [x] Tests both success (ok=true) and error (ok=false) cases ✅ Implemented in TestGenerator
- [x] Verifies return format (ok, output, error, meta) ✅ Implemented in TestGenerator
- [x] Uses variable references (${step.result}) ✅ Implemented in TestGenerator
- [x] Every step has a clear description ✅ Implemented in TestGenerator
- [x] No hardcoded assertions on dynamic data ✅ Uses variable references
- [x] Tests security validations (if applicable) ✅ Module-specific
- [x] Tests performance (if applicable) ✅ Module-specific
- [x] Valid YAML syntax ✅ Validated in TestGenerator.validate_test()
- [x] Can be executed by Flyto2 Engine ✅ YAML format compatible

---

**Version:** 2.0 Enterprise
**Last Updated:** 2025-12-04
**Maintained by:** Flyto2 AI Evolution Team
