#!/usr/bin/env python3
"""
Automatic Tool Creator for Telegram Bot

Detects when user describes a new task and automatically:
1. Generates module code with Ollama
2. Validates code quality
3. Creates git branch and PR
4. Notifies user
"""
import sys
import re
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.evolution.auto_evolution_engine import ImplementationAgent


class AutoToolCreator:
    """Automatically creates new modules based on user requests"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.agent = ImplementationAgent(use_ollama=True)

        # Patterns to detect tool creation requests
        # More flexible patterns to catch various phrasings
        self.patterns = [
            # English patterns - more flexible
            (r'create (?:a|an) (.+?)(?:module|tool|feature)', 'create_tool'),
            (r'create (?:a|an) (.+)', 'create_tool'),  # Fallback without module/tool
            (r'I need (?:a|an) (.+?)(?:module|tool|feature)', 'need_tool'),
            (r'I need (?:a|an )?(?:tool to |module to |feature to )?(.+)', 'need_tool'),
            (r'make (?:a|an) (.+?)(?:module|tool|feature)', 'create_tool'),
            (r'build (?:a|an) (.+?)(?:module|tool|feature)', 'create_tool'),
            (r'try (?:to )?(.+)', 'try_tool'),
            (r'can you (?:create|make|build) (?:a|an )?(.+)', 'can_create'),
        ]

    def detect_tool_request(self, message: str) -> Optional[Dict[str, Any]]:
        """Detect if user is requesting a new tool"""

        for pattern, request_type in self.patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                # Extract the description
                if match.groups():
                    description = match.group(1) if len(match.groups()) >= 1 else match.group(0)
                else:
                    description = message

                return {
                    'type': request_type,
                    'description': description.strip(),
                    'original_message': message
                }

        return None

    async def create_tool_from_description(self, description: str) -> Dict[str, Any]:
        """
        Automatically create a new tool/module from description

        Returns:
            dict with keys: success, module_id, code, branch, pr_url, error
        """

        result = {
            'success': False,
            'module_id': None,
            'code': None,
            'code_quality': 'unknown',
            'branch': None,
            'pr_url': None,
            'error': None
        }

        try:
            # Step 1: Analyze description and suggest module structure
            print(f"🤖 Analyzing: {description}")

            # Use Ollama to design the module
            design_prompt = f"""Given this user request: "{description}"

Design an atomic module for it.

Output ONLY a JSON with:
{{
  "module_id": "category.name",
  "module_name": "Name",
  "description": "What it does",
  "params": ["param1", "param2"]
}}

Keep it atomic - one specific task only."""

            import requests
            design_response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": design_prompt,
                    "stream": False
                }
            )

            if design_response.status_code != 200:
                result['error'] = f"Ollama error: {design_response.status_code}"
                return result

            design_text = design_response.json()['response']

            # Extract JSON from response
            import json
            json_match = re.search(r'\{[^}]+\}', design_text, re.DOTALL)
            if not json_match:
                result['error'] = "Could not parse module design"
                return result

            design = json.loads(json_match.group(0))
            module_id = design['module_id']
            result['module_id'] = module_id

            print(f"✅ Designed module: {module_id}")

            # Step 2: Generate code with ImplementationAgent
            print(f"💻 Generating code...")

            path_parts = module_id.split('.')
            if len(path_parts) == 2:
                category, name = path_parts
                module_path = f"src/core/modules/atomic/{category}/{name}.py"
            else:
                module_path = f"src/core/modules/atomic/{module_id.replace('.', '/')}.py"

            change = {
                'path': module_path,
                'reason': design.get('description', description),
                'template': 'atomic_module'
            }

            code = await self.agent._generate_with_ollama(change)

            if not code:
                result['error'] = "Code generation failed"
                return result

            result['code'] = code
            print(f"✅ Code generated ({len(code)} chars)")

            # Step 3: Validate quality
            print(f"🔍 Validating quality...")

            quality_checks = {
                "BaseModule import": "from src.core.modules.base import BaseModule" in code,
                "@register_module": "@register_module" in code,
                "validate_params()": "def validate_params" in code,
                "execute()": "def execute" in code,
                "self.params": "self.params" in code,
                "No hardcoded": all(x not in code for x in ["test@example.com", "'12345'", '"password"']),
                "Error handling": "try:" in code and "except" in code,
                "Return dict": "return {" in code,
                "No markdown": "```" not in code,
                "No redefinition": "class BaseModule" not in code
            }

            passed = sum(1 for v in quality_checks.values() if v)
            result['code_quality'] = f"{'✅' if passed == 10 else '❌'} {passed}/10 checks"

            if passed < 8:
                result['error'] = f"Quality too low: {passed}/10 checks"
                return result

            print(f"✅ Quality: {passed}/10")

            # Step 4: Write file
            print(f"📝 Writing file...")

            file_path = self.project_root / module_path
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w') as f:
                f.write(code)

            print(f"✅ File written: {module_path}")

            # Step 5: Git operations
            print(f"📦 Creating git branch...")

            import subprocess

            branch_name = f"feat/auto-{module_id.replace('.', '-')}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

            # Create branch
            subprocess.run(
                ['git', 'checkout', '-b', branch_name],
                check=True,
                cwd=self.project_root,
                capture_output=True
            )
            result['branch'] = branch_name
            print(f"✅ Branch: {branch_name}")

            # Commit
            subprocess.run(['git', 'add', module_path], check=True, cwd=self.project_root)

            commit_msg = f"""feat: Auto-create {module_id} module

{design.get('description', description)}

Auto-generated from user request via Telegram bot
Code Quality: {result['code_quality']}
Generated with Ollama (llama3.2:3b)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"""

            subprocess.run(
                ['git', 'commit', '-m', commit_msg],
                check=True,
                cwd=self.project_root,
                capture_output=True
            )
            print(f"✅ Commit created")

            # Step 6: Push and create PR
            print(f"🚀 Pushing and creating PR...")

            # Push
            push_result = subprocess.run(
                ['git', 'push', '-u', 'origin', branch_name],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            if push_result.returncode != 0:
                result['error'] = f"Push failed: {push_result.stderr}"
                print(f"⚠️ Push failed")
            else:
                print(f"✅ Pushed")

                # Create PR
                pr_title = f"feat: Auto-create {module_id} module"
                pr_body = f"""## Auto-Generated Module

**User Request**: {description}

**Module**: `{module_id}`
**Code Quality**: {result['code_quality']}

## Details
This module was automatically created by the Telegram bot using:
- Ollama (llama3.2:3b) for code generation
- Automated quality validation
- Zero-coupling architecture

## Test Plan
- [ ] Verify module imports correctly
- [ ] Test with valid parameters
- [ ] Verify error handling
- [ ] Check code quality

🤖 Auto-generated with [Claude Code](https://claude.com/claude-code)"""

                pr_result = subprocess.run(
                    ['gh', 'pr', 'create', '--title', pr_title, '--body', pr_body],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root
                )

                if pr_result.returncode == 0:
                    result['pr_url'] = pr_result.stdout.strip()
                    print(f"✅ PR created: {result['pr_url']}")
                else:
                    print(f"⚠️ PR creation failed (may need gh auth)")

            # Switch back to main
            subprocess.run(['git', 'checkout', 'main'], check=True, cwd=self.project_root, capture_output=True)

            result['success'] = True
            return result

        except Exception as e:
            result['error'] = str(e)
            print(f"❌ Error: {e}")

            # Try to switch back to main
            try:
                import subprocess
                subprocess.run(['git', 'checkout', 'main'], cwd=self.project_root, capture_output=True)
            except:
                pass

            return result


# Test
async def test():
    """Test auto tool creation"""
    creator = AutoToolCreator(Path.cwd())

    # Test detection
    test_messages = [
        "try downloading images",
        "create a CSV parser module",
        "I need a tool to compress images",
        "can you make a JSON validator"
    ]

    print("Testing detection:")
    for msg in test_messages:
        detection = creator.detect_tool_request(msg)
        print(f"  '{msg}' -> {detection}")

    print("\n" + "="*80)

    # Test creation
    print("\nTesting creation:")
    result = await creator.create_tool_from_description("Add two numbers together")
    print(f"\nResult: {result}")


if __name__ == "__main__":
    asyncio.run(test())
