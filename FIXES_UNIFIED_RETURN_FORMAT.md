# Unified Return Format Fixes - Summary

## Problem
GPT-4o was generating modules with inconsistent return format: `{"status": "success", ...}` instead of the unified format: `{"ok": bool, "output": dict, "error": None/dict, "meta": dict}`.

This caused all auto-generated modules to fail tests because:
1. Test generator expects unified format with `.ok`, `.output`, `.error`, `.meta` keys
2. Variable resolver tries to access `${step_id.output.key}` which doesn't exist when using old format
3. All zero-assistance bot tests failed repeatedly

## Root Cause
The GPT-4o module generation prompt in `src/core/executor/smart_executor.py` was teaching the AI to use the wrong return format through:
1. Incorrect requirement description (line 816)
2. Wrong example code snippets (lines 838-896)

## Solution Applied

### User Actions
1. Cleared Qdrant vector database to remove "polluted" learning examples:
   ```bash
   python3 scripts/clear_qdrant_cloud.py
   ```
   - Deleted 4 collections: flyto2_project_knowledge, flyto2_ollama, flyto2_knowledge, flyto2_memory

2. Deleted incorrectly generated modules:
   ```bash
   rm -f src/core/modules/atomic/image/download.py
   rm -f src/core/modules/atomic/image/svg_convert.py
   ```

### Code Fixes in `src/core/executor/smart_executor.py`

#### 1. Line 816 - Updated Requirement #7
**Before:**
```
7. Return structured dict with status and data
```

**After:**
```
7. MUST return UNIFIED format: {"ok": bool, "output": dict, "error": None/dict, "meta": dict}
```

#### 2. Lines 838-847 - Fixed First Example
**Before:**
```python
return {
    "status": "success",
    "path": str(path),
    "size": len(response.content),
    "url": self.url
}
```

**After:**
```python
return {
    "ok": True,
    "output": {
        "path": str(path),
        "size": len(response.content),
        "url": self.url
    },
    "error": None,
    "meta": {}
}
```

#### 3. Lines 866-875 - Fixed image.download Example
Same transformation as above - moved data fields into `output` dict, added required `ok`, `error`, `meta` keys.

#### 4. Lines 888-896 - Fixed file.read Example
**Before:**
```python
return {
    "status": "success",
    "content": content,
    "size": len(content)
}
```

**After:**
```python
return {
    "ok": True,
    "output": {
        "content": content,
        "size": len(content)
    },
    "error": None,
    "meta": {}
}
```

## Expected Impact

With these fixes:
1. GPT-4o will now generate modules using the correct unified return format
2. Test generator will correctly validate module outputs
3. Variable resolution `${step_id.output.key}` will work properly
4. Zero-assistance bot should pass tests end-to-end
5. All auto-generated modules will be compatible with the rest of the system

## Files Modified
- `src/core/executor/smart_executor.py` - Lines 816, 838-847, 866-875, 888-896

## Test Status
Currently running: `test_bot_zero_assistance.py` to verify complete fix

## Next Steps
1. Monitor test execution to verify GPT-4o generates correct format
2. If successful, run additional e2e tests (scoring system, etc.)
3. Document any remaining issues
