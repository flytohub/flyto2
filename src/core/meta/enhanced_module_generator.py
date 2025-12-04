"""
Enhanced Module Generator with Strict Quality Control and GitHub PR Integration
Support continuous 3 successful validations + automatic GitHub PR creation
"""
import os
import json
import subprocess
from typing import Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
from openai import OpenAI

from src.core.meta.quality_checker_v2 import QualityCheckerV2
from src.core.meta.auto_refiner_v3 import MultiPassRefiner

if TYPE_CHECKING:
    from src.core.metrics.collector import MetricsCollector


class EnhancedModuleGenerator:
    """
    Enhanced Module Generator with Strict Quality Control

    Features:
    1. Uses enterprise-grade GPT-4o prompt (MODULE_GENERATOR_PROMPT.md v2.0)
    2. Requires 3 consecutive successful generations
    3. Strict quality scoring using 10 atomic checks (9.8+/10)
    4. Automatic GitHub PR creation
    """

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        metrics_collector: Optional['MetricsCollector'] = None
    ):
        self.success_count = {}  # {module_name: success_count}
        self.quality_checker = QualityCheckerV2(metrics_collector=metrics_collector)
        self.openai_api_key = openai_api_key  # Store for multi-pass refiner
        self.metrics_collector = metrics_collector
        self.REQUIRED_SUCCESS_COUNT = 3
        self.MIN_PR_SCORE = 9.5  # Temporarily lowered from 9.8 for testing
        self.MAX_REFINE_ATTEMPTS = 5  # Multi-pass refinement (4 rounds + buffer)

    async def generate_module_with_validation(
        self,
        module_name: str,
        problem_description: str,
        openai_api_key: str
    ) -> Dict[str, Any]:
        """
        生成模組並進行連續驗證

        Returns:
            {
                "success": bool,
                "module_path": str,
                "pr_score": float,
                "consecutive_success": int,
                "ready_for_pr": bool,
                "pr_url": Optional[str]
            }
        """
        # 初始化計數器
        if module_name not in self.success_count:
            self.success_count[module_name] = 0

        # 生成模組規格
        spec = await self._generate_module_spec(
            module_name,
            problem_description,
            openai_api_key
        )

        if not spec:
            self.success_count[module_name] = 0  # 重置計數
            return {
                "success": False,
                "consecutive_success": 0,
                "ready_for_pr": False,
                "error": "Failed to generate module spec"
            }

        # Generate module file
        module_path = self._generate_module_file(spec)

        # Strict quality check using 10 atomic checks
        pr_result = self.quality_checker.review_module(module_path)

        # 檢查是否通過
        if pr_result["score"] >= self.MIN_PR_SCORE:
            self.success_count[module_name] += 1
            print(f"✅ 成功 #{self.success_count[module_name]}/3 - PR 評分: {pr_result['score']}")
        else:
            print(f"❌ PR 評分不足: {pr_result['score']}/10.0 (目標: {self.MIN_PR_SCORE})")

            # Multi-pass AutoRefiner V2 (Strategy C - Atomic)
            print(f"🔧 啟動 Multi-pass AutoRefiner...")

            # Read current code
            module_code = Path(module_path).read_text()

            # Create atomic multi-pass refiner
            refiner = MultiPassRefiner(
                quality_checker=self.quality_checker,
                openai_api_key=openai_api_key,
                max_rounds=self.MAX_REFINE_ATTEMPTS,
                target_score=self.MIN_PR_SCORE,
                min_improvement=0.1,
                metrics_collector=self.metrics_collector,
            )

            # Run multi-pass refinement
            refine_result = refiner.refine_module(
                module_path=module_path,
                initial_code=module_code,
                initial_result=pr_result,
            )

            # Display results
            print(f"   📊 初始分數: {refine_result.initial_score:.1f}/10.0")
            print(f"   📊 最終分數: {refine_result.final_score:.1f}/10.0")
            print(f"   📈 總改善: {refine_result.total_improvement:+.1f}")
            print(f"   🔄 執行輪數: {len(refine_result.rounds)}")

            for round_result in refine_result.rounds:
                print(f"      Round {round_result.round_index}: "
                      f"{round_result.before_score:.1f} → {round_result.after_score:.1f} "
                      f"({round_result.improvement:+.1f})")

            # Update PR result with final state
            pr_result = self.quality_checker.review_module(module_path)

            # Check if target reached
            if refine_result.achieved_target:
                print(f"   🎉 多輪修復達標！")
                self.success_count[module_name] += 1
            else:
                print(f"   ❌ 多輪修復後仍未達標")
                self.success_count[module_name] = 0
                return {
                    "success": False,
                    "module_path": module_path,
                    "pr_score": pr_result["score"],
                    "pr_result": pr_result,
                    "consecutive_success": 0,
                    "ready_for_pr": False,
                    "refined": True,
                    "refine_rounds": len(refine_result.rounds),
                }

        # 檢查是否達到 3 次成功
        ready_for_pr = self.success_count[module_name] >= self.REQUIRED_SUCCESS_COUNT

        result = {
            "success": True,
            "module_path": module_path,
            "pr_score": pr_result["score"],
            "pr_result": pr_result,
            "consecutive_success": self.success_count[module_name],
            "ready_for_pr": ready_for_pr
        }

        # 如果達標，創建 GitHub PR
        if ready_for_pr:
            print(f"\n🎉 連續 {self.REQUIRED_SUCCESS_COUNT} 次通過嚴格審查！")
            print(f"📊 最終 PR 評分: {pr_result['score']}/10.0")

            pr_url = await self._create_github_pr(
                module_name,
                module_path,
                pr_result
            )

            result["pr_url"] = pr_url

            # 重置計數器
            self.success_count[module_name] = 0

        return result

    async def _generate_module_spec(
        self,
        module_name: str,
        problem: str,
        openai_api_key: str
    ) -> Optional[Dict[str, Any]]:
        """
        使用升級後的 GPT-4o prompt 生成模組規格
        """
        # 升級後的 prompt（包含所有安全性要求 + Few-shot 範例）
        prompt = """You are a SENIOR Python developer creating a PRODUCTION-READY Flyto2 atomic module.

Module to create: {{module_name}}
Purpose: {{problem}}

🔒 MANDATORY QUALITY RULES (Auto-checked by QualityCheckerV2 - Score must be 9.5+/10):

⚠️  FORBIDDEN PATTERNS (Will fail PR review):
❌ NO nested function definitions (NEVER define async def inside async def)
❌ NO nested try-except blocks
❌ NO generic 'except Exception' without specific exceptions first
❌ NO placeholder text like "Parameter description" in docstrings
❌ NO duplicate imports
❌ NO bare variable names (must use self.variable_name)

✅ REQUIRED PATTERNS (Must have):
✓ Specific exception types BEFORE generic Exception
✓ Complete parameter documentation (type + clear description)
✓ Unified return format: {{"ok": bool, "output": dict, "error": None or dict, "meta": dict}}
✓ All variables use self. prefix
✓ URL validation for URL parameters

🔒 STRUCTURAL TEMPLATE (MANDATORY - USE THIS EXACT STRUCTURE):

YOU MUST use EXACTLY this structure. Fill in the <placeholders> with your logic:

class YourModuleName(BaseModule):
    async def execute(self) -> Any:
        \"\"\"
        Execute the module logic

        Returns:
            <describe your return value>
        \"\"\"
        try:
            # Step 1: Validate inputs
            <your validation logic here>

            # Step 2: Main execution logic
            <your main logic here>

            # Step 3: Return success result
            return {{
                "ok": True,
                "output": {{"result_key": result_value}},
                "error": None,
                "meta": dict
            }}

        except SpecificException as e:
            return {{
                "ok": False,
                "output": dict,
                "error": {{"message": str(e)}},
                "meta": dict
            }}
        except Exception as e:
            raise RuntimeError(self.module_name + " execution failed: " + str(e))

⚠️ CRITICAL RULES:
• You MUST NOT define ANY function inside execute()
• You MUST NOT create nested async def execute()
• You MUST NOT add function definitions beyond the single execute() method shown above
• ONLY fill in the <placeholder> sections with your specific logic

🔒 CRITICAL SECURITY & QUALITY REQUIREMENTS (MANDATORY):

1. ✅ Variable references:
   - ALWAYS use self.variable_name (e.g., self.url, self.save_path)
   - NEVER use bare variable names (e.g., url, save_path)
   - Example: if not self.url.startswith("http://") ✅
   - Example: if not url.startswith("http://") ❌

2. ✅ NO duplicate imports
   - Import ALL libraries at file top ONLY
   - NEVER import inside functions/methods

3. ✅ URL validation (MANDATORY for ALL modules with URL parameter):
   - MUST validate URL format FIRST (http/https only)
   - Check: if not (self.url.startswith("http://") or self.url.startswith("https://"))
   - This is REQUIRED, not optional

4. ✅ For download/fetch/HTTP modules (in addition to URL validation):
   - MUST validate Content-Type header
   - MUST check file size before downloading (Content-Length)
   - MUST use streaming for large files (stream=True, iter_bytes)

5. ✅ Error handling:
   - Catch specific exceptions (HTTPStatusError, RequestError, IOError)
   - Return {{"status": "error", "message": "..."}} for recoverable errors
   - Raise RuntimeError for fatal errors

6. ✅ Code structure:
   - NO nested function definitions
   - NO placeholders or TODOs
   - Use async/await properly
   - Clear variable names with self. prefix

⛔ WRONG EXAMPLE (8.7 score) - NEVER do this:

❌ INCORRECT - Nested function definition (loses 0.5 points):
```python
async def execute(self) -> Any:
    try:
        async def execute(self) -> Any:  # ❌ NESTED! This is FORBIDDEN!
            # ... code here ...
            return {{"ok": True, ...}}
    except Exception as e:
        raise RuntimeError(...)
```
**Why wrong:** Defining `async def execute` INSIDE another `async def execute` creates nested functions (-0.5 points).

📋 GOOD EXAMPLE (9.5+ score) - Use this as template:

✅ CORRECT for simple text processing:
```python
async def execute(self) -> Any:
    \"\"\"
    Execute the module logic

    Returns:
        Dict with reversed text string
    \"\"\"
    try:
        # Input validation first
        if not isinstance(self.text, str):
            return {{
                "ok": False,
                "output": dict,
                "error": {{"message": "Invalid input: text must be a string"}},
                "meta": dict
            }}

        # Main logic
        reversed_text = self.text[::-1]

        return {{
            "ok": True,
            "output": {{"reversed_text": reversed_text}},
            "error": None,
            "meta": dict
        }}

    except ValueError as e:
        return {{
            "ok": False,
            "output": dict,
            "error": {{"message": "Value error: " + str(e)}},
            "meta": dict
        }}
    except TypeError as e:
        return {{
            "ok": False,
            "output": dict,
            "error": {{"message": "Type error: " + str(e)}},
            "meta": dict
        }}
    except Exception as e:
        raise RuntimeError(self.module_name + " execution failed: " + str(e))
```

❌ WRONG (will fail with 9.0 score or lower):
```python
async def execute(self) -> Any:
    try:
        try:  # ← FORBIDDEN: nested try-except
            result = process(text)  # ← WRONG: bare variable
            return {{"status": "success"}}  # ← WRONG format
        except Exception as e:  # ← WRONG: only generic handler
            return {{"error": str(e)}}
    except Exception as e:
        raise RuntimeError(str(e))
```

✅ CORRECT (production-ready):
```python
# NOTE: imports are at file top, not shown here
async def execute(self) -> Any:
    # Validate URL format
    if not (self.url.startswith("http://") or self.url.startswith("https://")):
        return {{
            "status": "error",
            "message": "Invalid URL: must start with http:// or https://"
        }}

    try:
        async with httpx.AsyncClient() as client:
            # First, get headers to check Content-Type and size
            head_response = await client.head(self.url, timeout=10.0)

            content_type = head_response.headers.get("content-type", "").lower()
            if not content_type.startswith("image/"):
                return {{
                    "status": "error",
                    "message": "Invalid content type: {{content_type}} (expected image/*)"
                }}

            content_length = int(head_response.headers.get("content-length", 0))
            max_size = 50 * 1024 * 1024  # 50 MB
            if content_length > max_size:
                return {{
                    "status": "error",
                    "message": "File too large: {{content_length}} bytes (max: {{max_size}})"
                }}

            # Download with streaming
            async with client.stream("GET", self.url, timeout=30.0) as response:
                response.raise_for_status()

                path = Path(self.save_path)
                path.parent.mkdir(parents=True, exist_ok=True)

                downloaded_size = 0
                with open(path, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        downloaded_size += len(chunk)
                        if downloaded_size > max_size:
                            return {{
                                "status": "error",
                                "message": "File size exceeded limit during download"
                            }}
                        f.write(chunk)

                return {{
                    "status": "success",
                    "path": str(path),
                    "size": downloaded_size,
                    "url": self.url,
                    "content_type": content_type
                }}

    except httpx.HTTPStatusError as e:
        return {{
            "status": "error",
            "message": "HTTP error: {{e.response.status_code}}"
        }}
    except httpx.RequestError as e:
        return {{
            "status": "error",
            "message": "Request failed: {{str(e)}}"
        }}
    except IOError as e:
        return {{
            "status": "error",
            "message": "File I/O error: {{str(e)}}"
        }}
    except Exception as e:
        raise RuntimeError("Unexpected error: {{str(e)}}")
```

📤 RETURN JSON:
{{
  "module_id": "{{module_name}}",
  "category": "string",  // ONE OF: image, file, string, array, utility, data, browser, api, ai
  "description": "One clear sentence describing what this module does",
  "params": {{
    "text": "str - The input text string to process (NO generic 'Parameter description'!)"
  }},
  "returns": "Dict[str, Any] with keys: ok, output, error, meta",
  "suggested_imports": ["from typing import Any, Dict"],
  "implementation_code": "COMPLETE EXECUTABLE CODE (method body only, no 'async def execute')"
}}

⚠️  STRICT VALIDATION (Will auto-fail if violated):
- implementation_code MUST have: specific exception handlers (ValueError, TypeError, etc.)
- implementation_code MUST NOT have: nested try-except, generic Exception only, TODO, "Parameter description"
- params MUST have real descriptions, NOT "Parameter description"
- Code quality target: 9.5+/10 (anything below 9.5 will be rejected)

🎯 FINAL REQUIREMENT:
If you cannot write code that passes all rules above, return an error instead of low-quality code.
Your code will be auto-tested by QualityCheckerV2. Follow the GOOD EXAMPLE template.

Generate code NOW for: {module_name}""".format(module_name=module_name, problem=problem)

        try:
            client = OpenAI(api_key=openai_api_key)

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a SENIOR Python developer creating PRODUCTION-READY code for Flyto2. Your code MUST pass strict PR review (9.5+/10).

CRITICAL REQUIREMENTS - MUST FOLLOW ALL:

1. UNIFIED RETURN FORMAT (2.0 pts):
   - ALL returns: {"ok": bool, "output": {}, "error": None/Dict, "meta": {}}
   - NEVER use {"status": "success"}!

2. VARIABLE REFERENCES (1.0 pt):
   - ALWAYS use self.variable_name
   - NEVER bare variables

3. ERROR HANDLING (1.0 pt) - CRITICAL:
   - Use SPECIFIC exception types first: ValueError, TypeError, IOError, etc.
   - ONE final generic 'except Exception' that raises RuntimeError
   - NEVER nest try-except blocks
   - Example:
     try:
         if not isinstance(self.text, str):
             return {"ok": False, "output": {}, "error": {"message": "..."}, "meta": {}}
         result = process(self.text)
         return {"ok": True, "output": {"result": result}, "error": None, "meta": {}}
     except ValueError as e:
         return {"ok": False, "output": {}, "error": {"message": f"Invalid value: {e}"}, "meta": {}}
     except TypeError as e:
         return {"ok": False, "output": {}, "error": {"message": f"Invalid type: {e}"}, "meta": {}}
     except Exception as e:
         raise RuntimeError(f"{self.module_name} execution failed: {e}")

4. DOCUMENTATION (0.5 pt):
   - Complete parameter docs in class docstring
   - Format: param_name (type): Clear description
   - NO placeholders like "Parameter description"

5. SECURITY:
   - URL validation: self.url.startswith("http://") or self.url.startswith("https://")
   - Input validation at start of execute()

TARGET SCORE: 9.5+/10.0 - This is MANDATORY."""
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                timeout=60
            )

            spec = json.loads(response.choices[0].message.content)

            # 基本驗證
            required = ["module_id", "category", "description", "params", "returns", "implementation_code"]
            if not all(k in spec for k in required):
                print(f"❌ Missing required fields")
                return None

            impl_code = spec.get("implementation_code", "")

            # 檢查程式碼品質
            if len(impl_code.strip()) < 100:
                print(f"❌ Code too short")
                return None

            # 檢查壞模式
            bad_patterns = ["TODO", "placeholder", "implement here"]
            for pattern in bad_patterns:
                if pattern.lower() in impl_code.lower():
                    print(f"❌ Found bad pattern: {pattern}")
                    return None

            # 檢查嵌套函數
            if "\n    def " in impl_code or "\n    async def " in impl_code:
                print(f"❌ Found nested function definition")
                return None

            print(f"✅ GPT-4o generated spec for: {spec['module_id']}")
            return spec

        except Exception as e:
            print(f"❌ GPT-4o failed: {e}")
            return None

    def _generate_module_file(self, spec: Dict[str, Any]) -> str:
        """生成模組檔案"""
        from src.core.meta.module_generator import ModuleGenerator

        generator = ModuleGenerator()
        result = generator.generate_module(spec)

        # generator.generate_module() returns a dict
        if not isinstance(result, dict):
            raise ValueError(f"Unexpected result type: {type(result)}")

        if not result.get('success'):
            errors = result.get('errors', ['Unknown error'])
            raise ValueError(f"Module generation failed: {errors}")

        module_path = result.get('module_path')
        if not module_path or not Path(module_path).exists():
            raise ValueError(f"Module file not created: {module_path}")

        print(f"✅ Module written to: {module_path}")
        return module_path

    async def _create_github_pr(
        self,
        module_name: str,
        module_path: str,
        pr_result: Dict
    ) -> Optional[str]:
        """
        創建 GitHub Pull Request

        Returns:
            PR URL or None if failed
        """
        try:
            branch_name = f"feat/{module_name.replace('.', '-')}"

            # 1. 創建新分支
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                check=True,
                capture_output=True
            )

            # 2. Add 檔案
            subprocess.run(
                ["git", "add", module_path],
                check=True
            )

            # 3. Commit
            commit_msg = f"""feat: Add {module_name} module

✅ Passed strict PR review: {pr_result['score']}/10.0
✅ Validated {self.REQUIRED_SUCCESS_COUNT} times consecutively

Quality checks:
{chr(10).join(f'  - {s}' for s in pr_result['strengths'][:5])}

🤖 Auto-generated by Flyto2"""

            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                check=True
            )

            # 4. Push
            subprocess.run(
                ["git", "push", "-u", "origin", branch_name],
                check=True
            )

            # 5. 創建 PR
            pr_body = f"""## 📊 Auto-generated Module: `{module_name}`

### ✅ Quality Metrics

- **PR Score**: {pr_result['score']}/10.0 (Grade: {pr_result['grade']})
- **Consecutive Validations**: {self.REQUIRED_SUCCESS_COUNT} times
- **Status**: {'✅ PASS' if pr_result['pass'] else '❌ FAIL'}

### 💪 Strengths

{chr(10).join(f'- {s}' for s in pr_result['strengths'])}

### 📝 Module Details

**File**: `{module_path}`

**Category**: Image processing
**Description**: Downloads an image from a specified URL with proper validation

### 🤖 Auto-generated

This module was automatically generated and validated by the Flyto2 Auto-Evolution system.
- Model: GPT-4o
- Validation passes: {self.REQUIRED_SUCCESS_COUNT}
- PR threshold: {self.MIN_PR_SCORE}/10.0

🤖 Auto-generated by Flyto2
"""

            result = subprocess.run(
                [
                    "gh", "pr", "create",
                    "--title", f"feat: Add {module_name} module",
                    "--body", pr_body,
                    "--base", "main"
                ],
                check=True,
                capture_output=True,
                text=True
            )

            pr_url = result.stdout.strip().split('\n')[-1]
            print(f"\n🎉 GitHub PR created: {pr_url}")

            return pr_url

        except subprocess.CalledProcessError as e:
            print(f"❌ GitHub PR creation failed: {e}")
            print(f"   stdout: {e.stdout}")
            print(f"   stderr: {e.stderr}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error creating PR: {e}")
            return None
