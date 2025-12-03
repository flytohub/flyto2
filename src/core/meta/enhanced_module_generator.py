"""
Enhanced Module Generator with Strict Quality Control and GitHub PR Integration
支援連續 3 次成功驗證 + 自動 GitHub PR 創建
"""
import os
import json
import subprocess
from typing import Dict, Any, Optional
from pathlib import Path
from openai import OpenAI

from src.core.meta.strict_pr_reviewer import StrictPRReviewer


class EnhancedModuleGenerator:
    """
    增強版模組生成器

    特點：
    1. 使用升級後的 GPT-4o prompt（包含所有安全性要求）
    2. 連續 3 次生成成功才通過
    3. 嚴格 PR 評分（9.8+/10）
    4. 自動創建 GitHub PR
    """

    def __init__(self):
        self.success_count = {}  # {module_name: success_count}
        self.reviewer = StrictPRReviewer()
        self.REQUIRED_SUCCESS_COUNT = 3
        self.MIN_PR_SCORE = 9.8

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

        # 生成檔案
        module_path = self._generate_module_file(spec)

        # 嚴格 PR 審查
        pr_result = self.reviewer.review_module(module_path)

        # 檢查是否通過
        if pr_result["score"] >= self.MIN_PR_SCORE:
            self.success_count[module_name] += 1
            print(f"✅ 成功 #{self.success_count[module_name]}/3 - PR 評分: {pr_result['score']}")
        else:
            print(f"❌ PR 評分不足: {pr_result['score']}/10.0 (目標: {self.MIN_PR_SCORE})")
            self.success_count[module_name] = 0  # 重置計數
            return {
                "success": False,
                "module_path": module_path,
                "pr_score": pr_result["score"],
                "pr_result": pr_result,
                "consecutive_success": 0,
                "ready_for_pr": False
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
        # 升級後的 prompt（包含所有安全性要求）
        prompt = f"""You are a SENIOR Python developer creating a PRODUCTION-READY Flyto2 atomic module.

Module to create: {module_name}
Purpose: {problem}

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

📋 EXAMPLE - WRONG vs CORRECT:

❌ WRONG (has issues):
```python
async def execute(self) -> Any:
    import httpx  # ← Duplicate import!
    from pathlib import Path  # ← Duplicate import!

    response = await client.get(self.url)  # ← No Content-Type check!
    path.write_bytes(response.content)  # ← No streaming!

    return {{"status": "success"}}
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
                    "message": f"Invalid content type: {{content_type}} (expected image/*)"
                }}

            content_length = int(head_response.headers.get("content-length", 0))
            max_size = 50 * 1024 * 1024  # 50 MB
            if content_length > max_size:
                return {{
                    "status": "error",
                    "message": f"File too large: {{content_length}} bytes (max: {{max_size}})"
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
            "message": f"HTTP error: {{e.response.status_code}}"
        }}
    except httpx.RequestError as e:
        return {{
            "status": "error",
            "message": f"Request failed: {{str(e)}}"
        }}
    except IOError as e:
        return {{
            "status": "error",
            "message": f"File I/O error: {{str(e)}}"
        }}
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {{str(e)}}")
```

📤 RETURN JSON:
{{
  "module_id": "{module_name}",
  "category": "image",  // MUST BE ONE OF: image, file, string, array, utility, data, browser, api, ai
  "description": "One clear sentence",
  "params": {{
    "param_name": "type - description"
  }},
  "returns": "Dict structure description",
  "suggested_imports": ["import httpx", "from pathlib import Path"],
  "implementation_code": "COMPLETE EXECUTABLE CODE (method body only, no 'async def execute')"
}}

⚠️  VALIDATION RULES:
- implementation_code must have: actual library calls, error handling, return statement
- implementation_code must NOT have: nested functions, imports, TODO, placeholder
- Code quality target: 9.8/10 (production-ready)

Generate PRODUCTION-READY code NOW for: {module_name}"""

        try:
            client = OpenAI(api_key=openai_api_key)

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior Python developer creating PRODUCTION-READY code for Flyto2. Your code MUST pass strict PR review (9.8/10). CRITICAL: (1) ALWAYS use self.variable_name, NEVER bare variable names. (2) For URL parameters, MUST include URL format validation using self.url.startswith(). (3) Include ALL security checks, proper error handling, and follow best practices exactly as shown in examples."
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

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"""

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

🤖 Generated with [Claude Code](https://claude.com/claude-code)
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
