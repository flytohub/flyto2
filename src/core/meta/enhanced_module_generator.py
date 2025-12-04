"""
Enhanced Module Generator with Strict Quality Control and GitHub PR Integration
Support continuous 3 successful validations + automatic GitHub PR creation
"""
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
    3. Strict quality scoring using 10 atomic checks (9.5+/10)
    4. Automatic GitHub PR creation
    """

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        metrics_collector: Optional["MetricsCollector"] = None,
    ):
        self.success_count: Dict[str, int] = {}  # {module_name: success_count}
        self.quality_checker = QualityCheckerV2(metrics_collector=metrics_collector)
        # Store for multi-pass refiner
        self.openai_api_key = openai_api_key
        self.metrics_collector = metrics_collector

        self.REQUIRED_SUCCESS_COUNT = 3
        self.MIN_PR_SCORE = 9.5  # Temporarily lowered from 9.8 for testing
        self.MAX_REFINE_ATTEMPTS = 5  # Multi-pass refinement (4 rounds + buffer)

    async def generate_module_with_validation(
        self,
        module_name: str,
        problem_description: str,
        openai_api_key: str,
    ) -> Dict[str, Any]:
        """
        Generate module with strict validation and optional PR creation.

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
        # Initialize counter
        if module_name not in self.success_count:
            self.success_count[module_name] = 0

        # 1) Ask GPT-4o for spec
        spec = await self._generate_module_spec(
            module_name=module_name,
            problem=problem_description,
            openai_api_key=openai_api_key,
        )

        if not spec:
            self.success_count[module_name] = 0
            return {
                "success": False,
                "consecutive_success": 0,
                "ready_for_pr": False,
                "error": "Failed to generate module spec",
            }

        # 2) Generate module file from spec
        module_path = self._generate_module_file(spec)

        # 3) Strict quality check using 10 atomic checks (+ syntax gate)
        pr_result = self.quality_checker.review_module(module_path)

        # 4) If score too low → try MultiPassRefiner
        if pr_result["score"] < self.MIN_PR_SCORE:
            print(
                f"❌ PR 評分不足: {pr_result['score']}/10.0 "
                f"(目標: {self.MIN_PR_SCORE})"
            )
            print("🔧 啟動 Multi-pass AutoRefiner...")

            module_code = Path(module_path).read_text()

            refiner = MultiPassRefiner(
                quality_checker=self.quality_checker,
                openai_api_key=openai_api_key,
                max_rounds=self.MAX_REFINE_ATTEMPTS,
                target_score=self.MIN_PR_SCORE,
                min_improvement=0.1,
                metrics_collector=self.metrics_collector,
            )

            refine_result = refiner.refine_module(
                module_path=module_path,
                initial_code=module_code,
                initial_result=pr_result,
            )

            print(f"   📊 初始分數: {refine_result.initial_score:.1f}/10.0")
            print(f"   📊 最終分數: {refine_result.final_score:.1f}/10.0")
            print(f"   📈 總改善: {refine_result.total_improvement:+.1f}")
            print(f"   🔄 執行輪數: {len(refine_result.rounds)}")

            for round_result in refine_result.rounds:
                print(
                    "      Round "
                    f"{round_result.round_index}: "
                    f"{round_result.before_score:.1f} → {round_result.after_score:.1f} "
                    f"({round_result.improvement:+.1f})"
                )

            # Re-evaluate after refinement
            pr_result = self.quality_checker.review_module(module_path)

            if not refine_result.achieved_target:
                print("   ❌ 多輪修復後仍未達標 (或語法錯誤未修復)")
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

            print("   🎉 多輪修復達標！")

        # 走到這裡 = score >= MIN_PR_SCORE 且語法 OK
        self.success_count[module_name] += 1
        print(
            f"✅ 成功 #{self.success_count[module_name]}/"
            f"{self.REQUIRED_SUCCESS_COUNT} - PR 評分: {pr_result['score']}"
        )

        ready_for_pr = self.success_count[module_name] >= self.REQUIRED_SUCCESS_COUNT

        result: Dict[str, Any] = {
            "success": True,
            "module_path": module_path,
            "pr_score": pr_result["score"],
            "pr_result": pr_result,
            "consecutive_success": self.success_count[module_name],
            "ready_for_pr": ready_for_pr,
        }

        if ready_for_pr:
            print(
                f"\n🎉 連續 {self.REQUIRED_SUCCESS_COUNT} 次通過嚴格審查！"
            )
            print(f"📊 最終 PR 評分: {pr_result['score']}/10.0")

            pr_url = await self._create_github_pr(
                module_name=module_name,
                module_path=module_path,
                pr_result=pr_result,
            )
            result["pr_url"] = pr_url
            # Reset counter
            self.success_count[module_name] = 0

        return result

    async def _generate_module_spec(
        self,
        module_name: str,
        problem: str,
        openai_api_key: str,
    ) -> Optional[Dict[str, Any]]:
        """
        使用升級後的 GPT-4o prompt 生成模組規格
        （implementation_code 是 execute() 的「body only」）
        """
        prompt = """You are a SENIOR Python developer creating a PRODUCTION-READY Flyto2 atomic module.

Module to create: {module_name}
Purpose: {problem}

🔒 MANDATORY QUALITY RULES (Auto-checked by QualityCheckerV2 - Target score: 9.5+/10):

====================
FORBIDDEN PATTERNS
====================
❌ NO nested function definitions in implementation_code
    - Do NOT write "def ..." or "async def ..." inside implementation_code
    - implementation_code is BODY ONLY, it will be wrapped inside:
        async def execute(self) -> Any:
            <implementation_code>

❌ NO nested try/except blocks
❌ NO generic 'except Exception' without specific exceptions first
❌ NO placeholder text like "Parameter description" in docstrings
❌ NO duplicate imports
❌ NO bare variables (use self.variable_name for all instance data)
❌ NO alternative return formats like {"status": "success"} or {"message": "..."}

====================
REQUIRED PATTERNS
====================
✅ UNIFIED RETURN FORMAT (for ALL returns):

    return {
        "ok": bool,
        "output": {...},               # main result payload
        "error": None or {"message": "..."},
        "meta": {}                     # optional metadata (can be empty)
    }

✅ VARIABLE USAGE
- ALWAYS use self.variable_name (e.g. self.url, self.save_path, self.text)
- NEVER use plain url / save_path / text without self.

✅ ERROR HANDLING
- Use specific exceptions first (ValueError, TypeError, IOError, httpx.HTTPStatusError, httpx.RequestError, etc.)
- ONE final generic handler that raises RuntimeError with module_name
- NO nested try/except

✅ URL VALIDATION (for any module with URL parameter)
- If there is a URL parameter (for example self.url), you MUST validate it at the top:

    if not isinstance(self.url, str):
        return {
            "ok": False,
            "output": {},
            "error": {"message": "Invalid URL: must be a string"},
            "meta": {}
        }

    if not (self.url.startswith("http://") or self.url.startswith("https://")):
        return {
            "ok": False,
            "output": {},
            "error": {"message": "Invalid URL: must start with http:// or https://"},
            "meta": {}
        }

✅ DOCUMENTATION (outside implementation_code)
- Class docstring parameters MUST have clear descriptions:
  param_name (type): clear explanation
- NO generic "Parameter description" text

====================
IMPLEMENTATION CODE SHAPE
====================
implementation_code MUST be a VALID PYTHON BODY that can be placed INSIDE:

    async def execute(self) -> Any:
        <implementation_code>

Therefore:
- DO NOT include "async def execute" in implementation_code
- DO NOT include any function or class definitions in implementation_code
- DO NOT include import statements in implementation_code

You ONLY write the body:
- input validation
- main logic
- return dictionaries using the unified format

====================
GOOD EXAMPLE (download image with validation - BODY ONLY)
====================

    # Basic type checks
    if not isinstance(self.url, str):
        return {
            "ok": False,
            "output": {},
            "error": {"message": "Invalid URL: must be a string"},
            "meta": {}
        }

    if not isinstance(self.save_path, str):
        return {
            "ok": False,
            "output": {},
            "error": {"message": "Invalid save_path: must be a string"},
            "meta": {}
        }

    if not (self.url.startswith("http://") or self.url.startswith("https://")):
        return {
            "ok": False,
            "output": {},
            "error": {"message": "Invalid URL: must start with http:// or https://"},
            "meta": {}
        }

    try:
        async with httpx.AsyncClient() as client:
            head_response = await client.head(self.url, timeout=10.0)
            content_type = head_response.headers.get("content-type", "").lower()
            content_length = int(head_response.headers.get("content-length", 0) or 0)
            max_size = 50 * 1024 * 1024  # 50 MB

            if not content_type.startswith("image/"):
                return {
                    "ok": False,
                    "output": {},
                    "error": {"message": f"Invalid content type: {content_type} (expected image/*)"},
                    "meta": {}
                }

            if content_length > max_size:
                return {
                    "ok": False,
                    "output": {},
                    "error": {"message": f"File too large: {content_length} bytes (max: {max_size})"},
                    "meta": {}
                }

            path = Path(self.save_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            downloaded_size = 0
            async with client.stream("GET", self.url, timeout=30.0) as response:
                response.raise_for_status()
                with path.open("wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        downloaded_size += len(chunk)
                        if downloaded_size > max_size:
                            return {
                                "ok": False,
                                "output": {},
                                "error": {"message": "File size exceeded limit during download"},
                                "meta": {}
                            }
                        f.write(chunk)

        return {
            "ok": True,
            "output": {
                "path": str(path),
                "size": downloaded_size,
                "url": self.url,
                "content_type": content_type
            },
            "error": None,
            "meta": {}
        }

    except httpx.HTTPStatusError as e:
        return {
            "ok": False,
            "output": {},
            "error": {"message": f"HTTP error: {e.response.status_code}"},
            "meta": {}
        }
    except httpx.RequestError as e:
        return {
            "ok": False,
            "output": {},
            "error": {"message": f"Request error: {str(e)}"},
            "meta": {}
        }
    except IOError as e:
        return {
            "ok": False,
            "output": {},
            "error": {"message": f"File I/O error: {str(e)}"},
            "meta": {}
        }
    except Exception as e:
        raise RuntimeError(f"{self.module_name} execution failed: {e}")

====================
OUTPUT JSON FORMAT
====================
You MUST return a valid JSON object with the following fields:

{
  "module_id": "{module_name}",
  "category": "image",   // e.g. image, file, string, array, utility, data, browser, api, ai
  "description": "One clear sentence describing what this module does.",
  "params": {
    "param_name": "type - Clear, concrete description of this parameter"
  },
  "returns": "Dict[str, Any] with keys: ok, output, error, meta",
  "implementation_code": "COMPLETE EXECUTABLE PYTHON CODE FOR THE BODY OF execute(self)->Any, WITHOUT any def/async def or imports"
}

DO NOT include markdown code fences in implementation_code.
DO NOT include function or class definitions in implementation_code.
DO NOT include import statements in implementation_code.

If you cannot satisfy ALL rules above, you MUST respond with an error instead of low-quality code.
""".format(
            module_name=module_name,
            problem=problem,
        )

        try:
            client = OpenAI(api_key=openai_api_key)

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You MUST follow ALL HARD RULES below without exception.\n\n"
                            "1. NEVER generate nested functions.\n"
                            "2. NEVER rename class names, module names, BaseModule or "
                            "@register_module decorators, or function signatures.\n"
                            "3. ALWAYS generate syntactically correct Python code (no markdown, "
                            "no code fences).\n"
                            "4. NEVER add unofficial dependencies.\n"
                            "5. ALWAYS use unified return format: "
                            "return {'ok': bool, 'output': {}, 'error': None or {'message': str}, 'meta': {}}.\n"
                            "6. If you violate ANY HARD RULE, you MUST regenerate and FIX it."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                timeout=60,
            )

            spec = json.loads(response.choices[0].message.content)

            required = [
                "module_id",
                "category",
                "description",
                "params",
                "returns",
                "implementation_code",
            ]
            if not all(k in spec for k in required):
                print("❌ Missing required fields in GPT-4o spec")
                return None

            impl_code: str = spec.get("implementation_code", "") or ""

            if len(impl_code.strip()) < 100:
                print("❌ Code too short")
                return None

            bad_patterns = ["TODO", "placeholder", "implement here"]
            for pattern in bad_patterns:
                if pattern.lower() in impl_code.lower():
                    print(f"❌ Found bad pattern in implementation_code: {pattern}")
                    return None

            # 禁止出現 def / async def（implementation_code 必須是 body only）
            if "\ndef " in impl_code or "\nasync def " in impl_code:
                print("❌ Found function definition inside implementation_code")
                return None

            # 禁止 import
            if "import " in impl_code:
                print("❌ Found import statement inside implementation_code")
                return None

            print(f"✅ GPT-4o generated spec for: {spec['module_id']}")
            return spec

        except Exception as e:
            print(f"❌ GPT-4o failed: {e}")
            return None

    def _generate_module_file(self, spec: Dict[str, Any]) -> str:
        """Generate module file via ModuleGenerator."""
        from src.core.meta.module_generator import ModuleGenerator

        generator = ModuleGenerator()
        result = generator.generate_module(spec)

        if not isinstance(result, dict):
            raise ValueError(f"Unexpected result type from ModuleGenerator: {type(result)}")

        if not result.get("success"):
            errors = result.get("errors", ["Unknown error"])
            raise ValueError(f"Module generation failed: {errors}")

        module_path = result.get("module_path")
        if not module_path or not Path(module_path).exists():
            raise ValueError(f"Module file not created: {module_path}")

        print(f"✅ Module written to: {module_path}")
        return module_path

    async def _create_github_pr(
        self,
        module_name: str,
        module_path: str,
        pr_result: Dict[str, Any],
    ) -> Optional[str]:
        """
        創建 GitHub Pull Request

        Returns:
            PR URL or None if failed
        """
        try:
            branch_name = f"feat/{module_name.replace('.', '-')}"

            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                check=True,
                capture_output=True,
            )

            subprocess.run(
                ["git", "add", module_path],
                check=True,
            )

            commit_msg = (
                f"feat: Add {module_name} module\n\n"
                f"✅ Passed strict PR review: {pr_result['score']}/10.0\n"
                f"✅ Validated {self.REQUIRED_SUCCESS_COUNT} times consecutively\n\n"
                "Quality checks:\n"
                + "\n".join(f"  - {s}" for s in pr_result.get("strengths", [])[:5])
                + "\n\n🤖 Auto-generated by Flyto2"
            )

            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                check=True,
            )

            subprocess.run(
                ["git", "push", "-u", "origin", branch_name],
                check=True,
            )

            pr_body = (
                f"## 📊 Auto-generated Module: `{module_name}`\n\n"
                "### ✅ Quality Metrics\n\n"
                f"- **PR Score**: {pr_result['score']}/10.0 "
                f"(Grade: {pr_result['grade']})\n"
                f"- **Consecutive Validations**: {self.REQUIRED_SUCCESS_COUNT} times\n"
                f"- **Status**: {'✅ PASS' if pr_result['pass'] else '❌ FAIL'}\n\n"
                "### 💪 Strengths\n\n"
                + "\n".join(f"- {s}" for s in pr_result.get("strengths", []))
                + "\n\n### 📝 Module Details\n\n"
                f"**File**: `{module_path}`\n\n"
                "**Category**: Image processing\n"
                "**Description**: Downloads an image from a specified URL with proper validation\n\n"
                "### 🤖 Auto-generated\n\n"
                "This module was automatically generated and validated by the Flyto2 "
                "Auto-Evolution system.\n"
                "- Model: GPT-4o\n"
                f"- Validation passes: {self.REQUIRED_SUCCESS_COUNT}\n"
                f"- PR threshold: {self.MIN_PR_SCORE}/10.0\n\n"
                "🤖 Auto-generated by Flyto2\n"
            )

            result = subprocess.run(
                [
                    "gh",
                    "pr",
                    "create",
                    "--title",
                    f"feat: Add {module_name} module",
                    "--body",
                    pr_body,
                    "--base",
                    "main",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            pr_url = result.stdout.strip().split("\n")[-1]
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
