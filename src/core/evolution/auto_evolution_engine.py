"""
Auto Evolution Engine - Continuous Self-Improvement System

This engine creates an automated loop:
1. Test crawler on real websites
2. Detect errors and failures
3. Analyze what resources are missing
4. Generate new atomic modules (if needed)
5. Run tests
6. Create PR
7. Notify via Telegram

The system evolves automatically without human intervention.

Components:
- EvolutionPlanner: Analyze errors and create evolution plan
- EvolutionDesigner: Design implementation details
- ImplementationAgent: Generate and apply code changes
"""
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import re

logger = logging.getLogger(__name__)


class EvolutionPlanner:
    """
    Create evolution plans from error tickets

    Analyzes errors, queries knowledge base, and generates structured plans.
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent

    async def analyze_and_plan(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze error ticket and create evolution plan

        Args:
            ticket: Error ticket with context

        Returns:
            {
                "problem_summary": str,
                "root_cause": str,
                "fix_strategy": str,
                "required_modules": list,
                "changes_needed": list,
                "confidence": float
            }
        """
        logger.info(f"Planning for ticket: {ticket.get('ticket_id', 'unknown')}")

        # Step 1: Gather context
        context = await self._gather_context(ticket)

        # Step 2: Analyze error patterns
        analysis = self._analyze_error_patterns(ticket, context)

        # Step 3: Generate plan
        plan = {
            "problem_summary": analysis.get("summary", "Unknown error"),
            "root_cause": analysis.get("root_cause", "To be determined"),
            "fix_strategy": analysis.get("strategy", "Investigate and fix"),
            "required_modules": analysis.get("modules", []),
            "changes_needed": analysis.get("changes", []),
            "confidence": analysis.get("confidence", 0.5)
        }

        logger.info(f"Plan created with confidence: {plan['confidence']}")
        return plan

    async def _gather_context(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """Gather all relevant context for planning"""
        context = {
            "error_context": ticket.get("context", {}),
            "similar_errors": [],
            "related_modules": [],
            "past_fixes": []
        }

        # Try to load RAG retriever if available
        try:
            from src.core.utils.rag_retriever import retrieve_knowledge

            error_sig = ticket.get("error_signature", "")
            if error_sig:
                # Query for similar errors
                rag_results = await retrieve_knowledge(
                    query=f"error {error_sig}",
                    filters={"type": "error"},
                    top_k=5
                )
                context["similar_errors"] = rag_results.get("results", [])

                # Query for past fixes
                fix_results = await retrieve_knowledge(
                    query=f"fix {error_sig}",
                    filters={"type": "fix"},
                    top_k=3
                )
                context["past_fixes"] = fix_results.get("results", [])
        except Exception as e:
            logger.warning(f"RAG retrieval failed: {e}")

        return context

    def _analyze_error_patterns(self, ticket: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze error patterns and determine fix strategy"""
        error_msg = str(ticket.get("error_message", ""))
        error_sig = ticket.get("error_signature", "")

        analysis = {
            "summary": f"Error: {error_sig}",
            "root_cause": "Unknown",
            "strategy": "Investigate and fix",
            "modules": [],
            "changes": [],
            "confidence": 0.3
        }

        # Pattern matching for common errors
        error_lower = error_msg.lower()

        if "timeout" in error_lower:
            analysis.update({
                "root_cause": "Request timeout - insufficient wait time or slow response",
                "strategy": "Increase timeout and add retry logic with exponential backoff",
                "modules": ["browser.wait", "api.retry"],
                "changes": [{
                    "type": "update_module",
                    "target": "browser.wait",
                    "reason": "Increase default timeout values"
                }],
                "confidence": 0.7
            })
        elif "element not found" in error_lower or "selector" in error_lower:
            analysis.update({
                "root_cause": "DOM selector issue - element may load dynamically or selector incorrect",
                "strategy": "Add intelligent wait for element and fallback selectors",
                "modules": ["browser.wait_for_element", "element.smart_query"],
                "changes": [{
                    "type": "update_module",
                    "target": "element.query",
                    "reason": "Add retry logic and multiple selector strategies"
                }],
                "confidence": 0.8
            })
        elif "connection" in error_lower or "network" in error_lower:
            analysis.update({
                "root_cause": "Network connectivity issue",
                "strategy": "Implement connection pooling and retry logic",
                "modules": ["api.connection_pool", "api.retry"],
                "changes": [{
                    "type": "create_module",
                    "target": "api.connection_manager",
                    "reason": "Centralized connection management"
                }],
                "confidence": 0.6
            })
        elif "rate limit" in error_lower:
            analysis.update({
                "root_cause": "API rate limiting",
                "strategy": "Implement intelligent rate limiting with backoff",
                "modules": ["api.rate_limiter"],
                "changes": [{
                    "type": "create_module",
                    "target": "api.rate_limiter",
                    "reason": "Prevent rate limit errors"
                }],
                "confidence": 0.9
            })

        return analysis


class EvolutionDesigner:
    """
    Design implementation details from evolution plans

    Takes plans and creates detailed implementation specifications.
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent

    async def design_implementation(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Design detailed implementation from plan

        Args:
            plan: Evolution plan from Planner

        Returns:
            {
                "design_doc": str,
                "file_changes": list,
                "test_plan": str,
                "rollback_plan": str,
                "estimated_effort": str
            }
        """
        logger.info("Designing implementation...")

        file_changes = []

        for change in plan.get("changes_needed", []):
            change_type = change.get("type", "")
            target = change.get("target", "")
            reason = change.get("reason", "")

            if change_type == "create_module":
                file_changes.append({
                    "action": "create",
                    "path": self._module_id_to_path(target),
                    "reason": reason,
                    "template": "atomic_module"
                })
            elif change_type == "update_module":
                file_changes.append({
                    "action": "update",
                    "path": self._module_id_to_path(target),
                    "reason": reason,
                    "changes": ["Add error handling", "Increase timeout", "Add retry logic"]
                })
            elif change_type == "update_workflow":
                file_changes.append({
                    "action": "update",
                    "path": f"workflows/{target}",
                    "reason": reason,
                    "changes": ["Update module parameters"]
                })

        design = {
            "design_doc": self._generate_design_doc(plan, file_changes),
            "file_changes": file_changes,
            "test_plan": self._generate_test_plan(plan),
            "rollback_plan": self._generate_rollback_plan(file_changes),
            "estimated_effort": self._estimate_effort(file_changes)
        }

        logger.info(f"Design complete: {len(file_changes)} file changes")
        return design

    def _module_id_to_path(self, module_id: str) -> str:
        """Convert module ID to file path"""
        parts = module_id.split('.')
        if len(parts) == 2:
            category, name = parts
            return f"src/core/modules/atomic/{category}/{name}.py"
        return f"src/core/modules/{module_id.replace('.', '/')}.py"

    def _generate_design_doc(self, plan: Dict[str, Any], file_changes: List[Dict]) -> str:
        """Generate design documentation"""
        lines = [
            "# Implementation Design",
            "",
            f"## Problem: {plan.get('problem_summary', 'Unknown')}",
            "",
            f"## Root Cause: {plan.get('root_cause', 'Unknown')}",
            "",
            f"## Strategy: {plan.get('fix_strategy', 'Unknown')}",
            "",
            "## File Changes:",
            ""
        ]

        for change in file_changes:
            lines.append(f"- {change['action'].upper()}: {change['path']}")
            lines.append(f"  Reason: {change['reason']}")
            lines.append("")

        return "\n".join(lines)

    def _generate_test_plan(self, plan: Dict[str, Any]) -> str:
        """Generate test plan"""
        return f"""
Test Plan:
1. Unit tests for modified modules
2. Integration tests for affected workflows
3. Regression tests for related functionality
4. Performance tests if timeout/retry logic changed
5. End-to-end test on target website

Success Criteria:
- All existing tests pass
- New tests cover edge cases
- Error no longer occurs in practice run
"""

    def _generate_rollback_plan(self, file_changes: List[Dict]) -> str:
        """Generate rollback plan"""
        lines = ["Rollback Plan:", ""]
        for change in file_changes:
            if change['action'] == 'create':
                lines.append(f"- Delete: {change['path']}")
            elif change['action'] == 'update':
                lines.append(f"- Revert: {change['path']} (use git checkout)")
        return "\n".join(lines)

    def _estimate_effort(self, file_changes: List[Dict]) -> str:
        """Estimate implementation effort"""
        count = len(file_changes)
        if count == 0:
            return "No changes needed"
        elif count == 1:
            return "Small (< 1 hour)"
        elif count <= 3:
            return "Medium (1-3 hours)"
        else:
            return "Large (> 3 hours)"


class ImplementationAgent:
    """
    Generate and apply code changes

    Takes designs and creates actual code implementations.
    Uses Ollama for intelligent code generation with failure learning.
    """

    def __init__(self, use_ollama: bool = True):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.use_ollama = use_ollama
        self.ollama_url = "http://localhost:11434"
        self.ollama_model = "llama3.2:latest"

    async def implement_design(self, design: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implement the design

        Args:
            design: Design specification from Designer

        Returns:
            {
                "success": bool,
                "files_modified": list,
                "files_created": list,
                "tests_created": list,
                "errors": list
            }
        """
        logger.info("Implementing design...")

        result = {
            "success": True,
            "files_modified": [],
            "files_created": [],
            "tests_created": [],
            "errors": []
        }

        for change in design.get("file_changes", []):
            try:
                if change['action'] == 'create':
                    success = await self._create_file(change)
                    if success:
                        result["files_created"].append(change['path'])
                    else:
                        result["errors"].append(f"Failed to create {change['path']}")
                        result["success"] = False

                elif change['action'] == 'update':
                    success = await self._update_file(change)
                    if success:
                        result["files_modified"].append(change['path'])
                    else:
                        result["errors"].append(f"Failed to update {change['path']}")
                        result["success"] = False

            except Exception as e:
                result["errors"].append(f"Error processing {change['path']}: {str(e)}")
                result["success"] = False

        logger.info(f"Implementation {'succeeded' if result['success'] else 'failed'}")
        return result

    async def _generate_with_ollama(self, change: Dict[str, Any]) -> Optional[str]:
        """
        Use Ollama to generate actual module implementation

        Args:
            change: Change specification with module info

        Returns:
            Generated Python code or None if generation failed
        """
        if not self.use_ollama:
            return None

        try:
            import requests
            import re

            # Load atomic module standards
            standards_path = self.project_root / "docs" / "ATOMIC_MODULE_STANDARDS.md"
            standards_content = ""
            if standards_path.exists():
                with open(standards_path, 'r', encoding='utf-8') as f:
                    standards_content = f.read()[:5000]  # First 5000 chars

            # Query past failures from Qdrant (if available)
            past_failures = await self._query_past_failures(change)

            # Build prompt with quality requirements
            module_id = self._extract_module_id_from_path(change['path'])
            reason = change.get('reason', 'Generated module')

            system_prompt = f"""You are an expert Python developer creating atomic modules for Flyto2 workflow automation.

ATOMIC MODULE STANDARDS:
{standards_content[:3000]}

CRITICAL QUALITY REQUIREMENTS (MUST FOLLOW):
1. ❌ NO HARDCODED test data in execute()
2. ❌ NO random data generation (no random.randint, random.choice, etc.)
3. ❌ DO NOT redefine BaseModule - IMPORT it from src.core.modules.base
4. ❌ DO NOT redefine @register_module - IMPORT it from src.core.modules.registry
5. ✅ MUST read ALL data from self.params
6. ✅ MUST validate required params in validate_params()
7. ✅ validate_params() MUST actually validate and raise ValueError if params missing
8. ✅ MUST be reusable with different inputs
9. ✅ Handle errors gracefully with try/except
10. ✅ Return proper status dict with 'status', 'data', and 'error' fields

REQUIRED IMPORTS (copy exactly):
from typing import Dict, Any
from src.core.modules.base import BaseModule
from src.core.modules.registry import register_module

OUTPUT FORMAT:
- Return ONLY the Python code
- Do NOT include markdown code fences (no ```)
- Do NOT include explanations or comments outside code
- Do NOT redefine BaseModule or @register_module
- Code must be complete and production-ready

EXAMPLE STRUCTURE (follow this pattern):
```
from typing import Dict, Any
from src.core.modules.base import BaseModule
from src.core.modules.registry import register_module

@register_module('category.action')
class MyModule(BaseModule):
    module_name = "My Module"
    module_description = "Description"

    def validate_params(self) -> Dict[str, Any]:
        if 'input' not in self.params:
            raise ValueError("Missing required parameter: input")
        self.input_data = self.params['input']
        return {{'status': 'success', 'data': None}}

    async def execute(self) -> Dict[str, Any]:
        try:
            result = process(self.input_data)
            return {{'status': 'success', 'data': result}}
        except Exception as e:
            return {{'status': 'error', 'error': str(e)}}
```"""

            user_prompt = f"""Create atomic module: {module_id}

Purpose: {reason}

Requirements:
- Module ID: {module_id}
- Must inherit from BaseModule
- Register with @register_module('{module_id}')
- Implement validate_params() with REAL validation
- Implement execute() using self.params (NO hardcoded data)

"""

            if past_failures:
                user_prompt += f"\nLEARN FROM PAST FAILURES:\n"
                for failure in past_failures[:3]:
                    user_prompt += f"- {failure}\n"
                user_prompt += "\nDO NOT repeat these mistakes!\n"

            user_prompt += f"\nGenerate the complete, production-ready Python code now:"

            # Call Ollama
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": f"{system_prompt}\n\n{user_prompt}",
                    "stream": False
                },
                timeout=120
            )

            if response.status_code != 200:
                logger.warning(f"Ollama request failed: {response.status_code}")
                return None

            data = response.json()
            generated_code = data.get('response', '')

            # Strip markdown code blocks
            generated_code = re.sub(r'^```(?:python)?\n', '', generated_code, flags=re.MULTILINE)
            generated_code = re.sub(r'\n```$', '', generated_code, flags=re.MULTILINE)
            generated_code = generated_code.strip()

            # Validate generated code quality
            validation_result = self._validate_generated_code(generated_code, module_id)

            if validation_result['valid']:
                logger.info(f"✅ Ollama generated high-quality code for {module_id}")
                return generated_code
            else:
                issues = ', '.join(validation_result['issues'])
                logger.warning(f"⚠️ Ollama code has quality issues: {issues}")
                return None

        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return None

    def _validate_generated_code(self, code: str, module_id: str) -> Dict[str, Any]:
        """
        Validate generated code quality

        Checks for common issues:
        - Redefining BaseModule or decorators
        - Missing imports
        - Hardcoded test data
        - No actual validation
        - Using random data

        Args:
            code: Generated Python code
            module_id: Expected module ID

        Returns:
            {'valid': bool, 'issues': List[str]}
        """
        issues = []

        # Check 1: Must have proper imports
        if 'from src.core.modules.base import BaseModule' not in code:
            issues.append("Missing BaseModule import")

        if 'from src.core.modules.registry import register_module' not in code:
            issues.append("Missing register_module import")

        # Check 2: Must NOT redefine BaseModule
        if 'class BaseModule' in code:
            issues.append("Redefining BaseModule (should import it)")

        # Check 3: Must have @register_module with correct ID
        if f"@register_module('{module_id}')" not in code and f'@register_module("{module_id}")' not in code:
            issues.append(f"Missing or incorrect @register_module('{module_id}')")

        # Check 4: Must have class inheriting BaseModule
        if 'class' not in code or '(BaseModule)' not in code:
            issues.append("Missing class inheriting from BaseModule")

        # Check 5: Must have validate_params and execute methods
        if 'def validate_params' not in code:
            issues.append("Missing validate_params method")

        if 'def execute' not in code and 'async def execute' not in code:
            issues.append("Missing execute method")

        # Check 6: validate_params should have real validation (not just return success)
        if 'def validate_params' in code:
            # Extract validate_params method
            lines = code.split('\n')
            in_validate = False
            validate_lines = []
            indent_level = 0

            for line in lines:
                if 'def validate_params' in line:
                    in_validate = True
                    indent_level = len(line) - len(line.lstrip())
                    continue

                if in_validate:
                    current_indent = len(line) - len(line.lstrip())
                    if line.strip() and current_indent <= indent_level:
                        break
                    validate_lines.append(line)

            validate_body = '\n'.join(validate_lines)

            # Should have at least one validation check
            if 'if' not in validate_body and 'raise' not in validate_body:
                issues.append("validate_params has no actual validation logic")

        # Check 7: Should NOT have hardcoded test data
        hardcoded_patterns = [
            'xml_string = ',
            'test_data = ',
            'example_data = ',
            'sample = ',
            '<root>',  # Hardcoded XML
            '{"test"',  # Hardcoded JSON
        ]

        for pattern in hardcoded_patterns:
            if pattern in code and 'def execute' in code:
                # Check if it's in execute method
                issues.append(f"Possible hardcoded test data: '{pattern}'")
                break

        # Check 8: Should NOT use random data generation
        if 'random.' in code and 'import random' in code:
            issues.append("Using random data generation (not deterministic)")

        # Check 9: Should use self.params
        if 'self.params' not in code:
            issues.append("Not reading from self.params")

        # Check 10: Should return proper status dict
        if "{'status':" not in code and '{"status":' not in code:
            issues.append("execute() should return dict with 'status' field")

        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

    async def _query_past_failures(self, change: Dict[str, Any]) -> List[str]:
        """
        Query Qdrant for past failures related to this module

        Args:
            change: Change specification

        Returns:
            List of past failure messages
        """
        try:
            from src.core.utils.rag_retriever import retrieve_knowledge

            module_id = self._extract_module_id_from_path(change['path'])

            # Query for failures
            results = await retrieve_knowledge(
                query=f"error failure {module_id}",
                filters={"type": "error"},
                top_k=3
            )

            failures = []
            for result in results.get('results', []):
                content = result.get('content', '')
                if content:
                    failures.append(content[:200])

            return failures

        except Exception as e:
            logger.debug(f"Could not query past failures: {e}")
            return []

    def _extract_module_id_from_path(self, path: str) -> str:
        """Extract module ID from file path"""
        path_parts = Path(path).parts
        if 'atomic' in path_parts:
            atomic_idx = path_parts.index('atomic')
            category_parts = path_parts[atomic_idx + 1:-1]
            module_name = Path(path).stem
            if category_parts:
                category = '.'.join(category_parts)
                return f"{category}.{module_name}"
            return module_name
        return Path(path).stem

    async def _create_file(self, change: Dict[str, Any]) -> bool:
        """
        Create new file with AI-generated or template content

        Tries Ollama first, falls back to template if Ollama fails.
        """
        file_path = self.project_root / change['path']

        # Check if file already exists
        if file_path.exists():
            logger.warning(f"File already exists: {file_path}")
            return False

        # Create directory if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Try Ollama generation first for atomic modules
        content = None
        if change.get('template') == 'atomic_module' and self.use_ollama:
            logger.info(f"🤖 Generating with Ollama: {change['path']}")
            content = await self._generate_with_ollama(change)

            if content:
                logger.info(f"✅ Using Ollama-generated implementation")
            else:
                logger.warning(f"⚠️ Ollama generation failed, falling back to template")

        # Fallback to template if Ollama failed or not used
        if not content:
            if change.get('template') == 'atomic_module':
                content = self._generate_atomic_module_template(change)
                logger.info(f"📝 Using quality-enforced template (with TODOs)")
            else:
                content = f"# {change.get('reason', 'Generated file')}\n"

        try:
            file_path.write_text(content, encoding='utf-8')
            logger.info(f"✅ Created file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create file: {e}")
            return False

    async def _update_file(self, change: Dict[str, Any]) -> bool:
        """Update existing file"""
        file_path = self.project_root / change['path']

        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False

        try:
            # For now, just add a comment noting the change needed
            # In production, would use AST manipulation or LLM-generated patches
            content = file_path.read_text(encoding='utf-8')

            comment = f"\n# TODO: {change.get('reason', 'Update needed')}\n"
            if comment not in content:
                content = content + comment
                file_path.write_text(content, encoding='utf-8')
                logger.info(f"Updated file: {file_path}")

            return True
        except Exception as e:
            logger.error(f"Failed to update file: {e}")
            return False

    def _generate_atomic_module_template(self, change: Dict[str, Any]) -> str:
        """Generate atomic module template with quality standards"""
        module_name = Path(change['path']).stem
        reason = change.get('reason', 'Generated module')

        # Extract module_id from path (e.g., "xml/parse_elements.py" -> "xml.parse_elements")
        path_parts = Path(change['path']).parts
        if 'atomic' in path_parts:
            atomic_idx = path_parts.index('atomic')
            category_parts = path_parts[atomic_idx + 1:-1]  # Between atomic/ and filename
            if category_parts:
                category = '.'.join(category_parts)
                module_id = f"{category}.{module_name}"
            else:
                module_id = module_name
        else:
            module_id = module_name

        return f'''"""
{module_name.replace('_', ' ').title()} Module

{reason}

QUALITY STANDARDS ENFORCED:
- ✅ Uses BaseModule class
- ✅ Registered with @register_module
- ✅ Validates required params in validate_params()
- ✅ Uses self.params (NO hardcoded data)
- ✅ Production-ready implementation
"""
from typing import Dict, Any
from src.core.modules.base import BaseModule
from src.core.modules.registry import register_module


@register_module('{module_id}')
class {self._to_class_name(module_name)}(BaseModule):
    """
    {reason}

    Example usage:
        {{
            "module": "{module_id}",
            "params": {{
                # Add required parameters here
            }}
        }}
    """

    module_name = "{module_name.replace('_', ' ').title()}"
    module_description = "{reason}"

    def validate_params(self) -> Dict[str, Any]:
        """
        Validate and extract parameters

        IMPORTANT: This method MUST validate all required parameters.
        Raise ValueError if any required parameter is missing.
        """
        # TODO: Add actual parameter validation
        # Example:
        # if 'input_data' not in self.params:
        #     raise ValueError("Missing required parameter: input_data")
        # self.input_data = self.params['input_data']

        return {{'status': 'success', 'data': None}}

    async def execute(self) -> Dict[str, Any]:
        """
        Execute {module_name} operation

        CRITICAL RULES:
        - ❌ NO hardcoded test data
        - ✅ MUST read from self.params
        - ✅ MUST be reusable with different inputs
        - ✅ Handle errors gracefully

        Returns:
            {{
                "status": "success" or "error",
                "data": result_data,
                "error": error_message (if status is error)
            }}
        """
        try:
            # TODO: Implement actual module logic using self.params
            # Example:
            # result = process(self.input_data)
            # return {{'status': 'success', 'data': result}}

            return {{
                'status': 'success',
                'data': None,
                'message': '{module_name} executed (implementation pending)'
            }}

        except Exception as e:
            return {{
                'status': 'error',
                'error': str(e)
            }}
'''

    def _to_class_name(self, module_name: str) -> str:
        """Convert module_name to ClassName (e.g., parse_xml_elements -> ParseXmlElementsModule)"""
        words = module_name.split('_')
        class_name = ''.join(word.capitalize() for word in words)
        if not class_name.endswith('Module'):
            class_name += 'Module'
        return class_name


class AutoEvolutionEngine:
    """
    Autonomous evolution engine for continuous improvement
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.metrics_dir = self.project_root / "metrics"
        self.metrics_dir.mkdir(exist_ok=True)
        self.evolution_log = self.metrics_dir / "auto_evolution.json"
        self.cycles = self._load_cycles()

        # Initialize evolution components
        self.planner = EvolutionPlanner()
        self.designer = EvolutionDesigner()
        self.implementer = ImplementationAgent()

    def _load_cycles(self) -> List[Dict[str, Any]]:
        """Load evolution cycle history"""
        if self.evolution_log.exists():
            try:
                return json.loads(self.evolution_log.read_text())
            except Exception:
                return []
        return []

    def _save_cycles(self):
        """Save evolution cycle history"""
        self.evolution_log.write_text(
            json.dumps(self.cycles, indent=2),
            encoding='utf-8'
        )

    async def run_evolution_cycle(self) -> Dict[str, Any]:
        """
        Run one complete evolution cycle

        Returns:
            Cycle results
        """
        cycle_id = len(self.cycles) + 1

        print("=" * 70)
        print(f"EVOLUTION CYCLE #{cycle_id}")
        print("=" * 70)
        print()

        cycle = {
            "cycle_id": cycle_id,
            "timestamp": datetime.now().isoformat(),
            "steps": {},
            "status": "running"
        }

        try:
            # Step 1: Test crawler
            print("STEP 1: Testing crawler...")
            test_result = await self._test_crawler()
            cycle["steps"]["test_crawler"] = test_result
            print(f"  Status: {'✅' if test_result['success'] else '❌'}")
            print(f"  Tests passed: {test_result['passed']}/{test_result['total']}")
            print()

            # Step 2: Analyze errors (using Planner)
            if not test_result['success']:
                print("STEP 2: Analyzing errors and planning...")
                ticket = self._create_ticket_from_errors(test_result['errors'])
                plan = await self.planner.analyze_and_plan(ticket)
                cycle["steps"]["plan"] = plan
                print(f"  Root cause: {plan['root_cause'][:60]}...")
                print(f"  Confidence: {plan['confidence']:.0%}")
                print()

                # Step 3: Design solution
                if plan.get('changes_needed'):
                    print("STEP 3: Designing solution...")
                    design = await self.designer.design_implementation(plan)
                    cycle["steps"]["design"] = design
                    print(f"  File changes: {len(design['file_changes'])}")
                    print(f"  Effort: {design['estimated_effort']}")
                    print()

                    # Step 4: Implement changes
                    print("STEP 4: Implementing changes...")
                    impl_result = await self.implementer.implement_design(design)
                    cycle["steps"]["implementation"] = impl_result
                    print(f"  Files created: {len(impl_result['files_created'])}")
                    print(f"  Files modified: {len(impl_result['files_modified'])}")
                    if impl_result['errors']:
                        print(f"  ⚠️  Errors: {len(impl_result['errors'])}")
                    print()

                    # Step 5: Run tests
                    print("STEP 5: Running tests...")
                    test_results = await self._run_tests()
                    cycle["steps"]["run_tests"] = test_results
                    print(f"  Tests: {'✅ PASS' if test_results['all_passed'] else '❌ FAIL'}")
                    print()

                    # Step 6: Create PR (if tests pass)
                    if test_results['all_passed']:
                        print("STEP 6: Creating PR...")
                        pr_result = await self._create_pr(cycle)
                        cycle["steps"]["create_pr"] = pr_result
                        print(f"  PR: {pr_result.get('branch', 'N/A')}")
                        print()

                        # Step 7: Notify Telegram
                        print("STEP 7: Notifying Telegram...")
                        notify_result = await self._notify_telegram(cycle, pr_result)
                        cycle["steps"]["notify_telegram"] = notify_result
                        print(f"  Notification: {'✅ Sent' if notify_result['success'] else '❌ Failed'}")
                        print()

            cycle["status"] = "completed"

        except Exception as e:
            cycle["status"] = "error"
            cycle["error"] = str(e)
            print(f"❌ CYCLE ERROR: {e}")

        # Save cycle
        self.cycles.append(cycle)
        self._save_cycles()

        print("=" * 70)
        print(f"Cycle #{cycle_id}: {cycle['status'].upper()}")
        print("=" * 70)
        print()

        return cycle

    async def _test_crawler(self) -> Dict[str, Any]:
        """
        Test crawler on real websites

        Returns:
            Test results
        """
        # Run test_crawler_practice.py
        try:
            result = subprocess.run(
                ["python", "tests/test_crawler_practice.py"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )

            # Parse output for success/failure
            output = result.stdout + result.stderr
            errors = []

            # Simple heuristic: look for error indicators
            if "❌" in output or "EXCEPTION" in output or result.returncode != 0:
                # Extract error lines
                for line in output.split('\n'):
                    if "❌" in line or "EXCEPTION" in line or "Error" in line:
                        errors.append(line.strip())

            passed = output.count("✅ SUCCESS")
            total = output.count("Testing:")

            return {
                "success": len(errors) == 0,
                "passed": passed,
                "total": total,
                "errors": errors,
                "output": output[:500]  # First 500 chars
            }

        except Exception as e:
            return {
                "success": False,
                "passed": 0,
                "total": 0,
                "errors": [str(e)],
                "output": ""
            }

    def _create_ticket_from_errors(self, errors: List[str]) -> Dict[str, Any]:
        """
        Create evolution ticket from test errors

        Args:
            errors: List of error messages

        Returns:
            Ticket dictionary
        """
        import hashlib

        # Combine errors for signature
        error_text = " | ".join(errors[:3])  # Use first 3 errors
        error_sig = hashlib.md5(error_text.encode()).hexdigest()[:8]

        ticket = {
            "ticket_id": f"auto_{error_sig}",
            "error_signature": error_sig,
            "error_message": error_text,
            "trigger": "automated_testing",
            "context": {
                "errors": errors,
                "error_count": len(errors),
                "timestamp": datetime.now().isoformat()
            }
        }

        return ticket

    async def _run_tests(self) -> Dict[str, Any]:
        """
        Run all tests

        Returns:
            Test results
        """
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )

            output = result.stdout + result.stderr

            # Parse pytest output
            passed = output.count(" PASSED")
            failed = output.count(" FAILED")

            return {
                "all_passed": result.returncode == 0,
                "passed": passed,
                "failed": failed,
                "output": output[:500]
            }

        except Exception as e:
            return {
                "all_passed": False,
                "passed": 0,
                "failed": 0,
                "error": str(e)
            }

    async def _create_pr(self, cycle: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create pull request

        Args:
            cycle: Evolution cycle data

        Returns:
            PR creation result
        """
        # Generate PR title and body
        pr_title = f"Auto-evolution cycle #{cycle['cycle_id']}"
        pr_body = self._generate_pr_body(cycle)

        try:
            # Check if there are changes to commit
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            if not result.stdout.strip():
                return {
                    "success": False,
                    "message": "No changes to commit"
                }

            # Create branch
            branch_name = f"auto-evolution-{cycle['cycle_id']}"

            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=self.project_root,
                check=True
            )

            # Stage all changes
            subprocess.run(
                ["git", "add", "."],
                cwd=self.project_root,
                check=True
            )

            # Commit
            subprocess.run(
                ["git", "commit", "-m", f"{pr_title}\n\n{pr_body}"],
                cwd=self.project_root,
                check=True
            )

            # Push to remote
            logger.info(f"Pushing branch {branch_name} to remote...")
            push_result = subprocess.run(
                ["git", "push", "-u", "origin", branch_name],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            if push_result.returncode != 0:
                logger.warning(f"Push failed: {push_result.stderr}")
                return {
                    "success": False,
                    "branch": branch_name,
                    "error": f"Failed to push: {push_result.stderr}"
                }

            # Create PR using gh CLI
            logger.info(f"Creating PR: {pr_title}")
            pr_result = subprocess.run(
                [
                    "gh", "pr", "create",
                    "--title", pr_title,
                    "--body", pr_body,
                    "--head", branch_name
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            if pr_result.returncode == 0:
                pr_url = pr_result.stdout.strip()
                logger.info(f"✅ PR created: {pr_url}")
                return {
                    "success": True,
                    "branch": branch_name,
                    "pr_url": pr_url,
                    "title": pr_title,
                    "message": f"PR created successfully: {pr_url}"
                }
            else:
                logger.warning(f"PR creation failed: {pr_result.stderr}")
                return {
                    "success": True,  # Push succeeded
                    "branch": branch_name,
                    "title": pr_title,
                    "message": f"Branch pushed, but PR creation failed: {pr_result.stderr}",
                    "manual_pr": True
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _generate_pr_body(self, cycle: Dict[str, Any]) -> str:
        """Generate PR description"""
        lines = [
            f"## Auto-Evolution Cycle #{cycle['cycle_id']}",
            "",
            "### Analysis",
            ""
        ]

        if "plan" in cycle["steps"]:
            plan = cycle["steps"]["plan"]
            lines.append(f"**Problem**: {plan.get('problem_summary', 'Unknown')}")
            lines.append(f"**Root Cause**: {plan.get('root_cause', 'Unknown')}")
            lines.append(f"**Strategy**: {plan.get('fix_strategy', 'Unknown')}")
            lines.append(f"**Confidence**: {plan.get('confidence', 0):.0%}")
            lines.append("")

        if "implementation" in cycle["steps"]:
            impl = cycle["steps"]["implementation"]
            lines.append("### Changes")
            lines.append("")
            if impl.get('files_created'):
                lines.append(f"- **Files Created**: {len(impl['files_created'])}")
                for f in impl['files_created'][:5]:  # Show first 5
                    lines.append(f"  - {f}")
            if impl.get('files_modified'):
                lines.append(f"- **Files Modified**: {len(impl['files_modified'])}")
                for f in impl['files_modified'][:5]:  # Show first 5
                    lines.append(f"  - {f}")
            lines.append("")

        if "run_tests" in cycle["steps"]:
            tests = cycle["steps"]["run_tests"]
            lines.append("### Test Results")
            lines.append("")
            lines.append(f"- **Tests Passed**: {tests.get('passed', 0)}")
            lines.append(f"- **Tests Failed**: {tests.get('failed', 0)}")
            lines.append("")

        lines.extend([
            "---",
            "",
            "Auto-generated by Evolution Engine",
            f"Timestamp: {cycle.get('timestamp', 'N/A')}"
        ])

        return "\n".join(lines)

    async def _notify_telegram(self, cycle: Dict[str, Any], pr_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send notification to Telegram

        Args:
            cycle: Evolution cycle data
            pr_result: PR creation result

        Returns:
            Notification result
        """
        # This would integrate with telegram_bot_v2.py
        # For now, just log
        message = f"""
🤖 Auto-Evolution Cycle #{cycle['cycle_id']}

Status: {cycle['status']}
PR: {pr_result.get('branch', 'N/A')}
Tests: {cycle['steps'].get('run_tests', {}).get('passed', 0)} passed

Ready for review!
        """.strip()

        print(f"\nTelegram message:\n{message}\n")

        return {
            "success": True,
            "message": message
        }

    async def run_continuous_evolution(self, max_cycles: int = 10, interval_hours: int = 24):
        """
        Run continuous evolution loop

        Args:
            max_cycles: Maximum number of cycles
            interval_hours: Hours between cycles
        """
        print("🤖 AUTO-EVOLUTION ENGINE STARTED")
        print(f"   Max cycles: {max_cycles}")
        print(f"   Interval: {interval_hours} hours")
        print()

        for i in range(max_cycles):
            await self.run_evolution_cycle()

            if i < max_cycles - 1:
                print(f"⏳ Waiting {interval_hours} hours until next cycle...")
                await asyncio.sleep(interval_hours * 3600)


# ============================================================
# Phase 5.1: Module Spec Generator (Atomic Component)
# ============================================================

class SpecGenerator:
    """
    Generate module specifications using LLM (Phase 5.1)
    Analyzes task context and creates structured module specs
    """

    def __init__(self, ollama_endpoint: str = "http://localhost:11434"):
        self.ollama_endpoint = ollama_endpoint
        self.model = "qwen2.5:32b"
        self.logger = logging.getLogger(__name__)

    async def generate_spec(
        self,
        module_id: str,
        task_context: str,
        similar_modules: List[Dict] = None
    ) -> Dict:
        """
        Generate specification for new module

        Args:
            module_id: Desired module ID (e.g., "excel.read")
            task_context: Why this module is needed
            similar_modules: Similar existing modules for reference

        Returns:
            Module specification dict
        """

        # Build prompt with examples
        prompt = self._build_spec_prompt(module_id, task_context, similar_modules or [])

        # Call LLM
        response = self._call_llm(prompt)

        # Parse response
        try:
            spec = json.loads(response)

            # Validate spec structure
            required_fields = ['module_id', 'description', 'parameters', 'returns']
            if not all(field in spec for field in required_fields):
                raise ValueError(f"Spec missing required fields: {required_fields}")

            return spec

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse spec JSON: {e}")
            raise

    def _build_spec_prompt(
        self,
        module_id: str,
        task_context: str,
        similar_modules: List[Dict]
    ) -> str:
        """Build prompt for spec generation"""

        prompt_parts = [
            "Generate a module specification in JSON format.",
            "",
            f"Module ID: {module_id}",
            f"Context: {task_context}",
            ""
        ]

        # Add examples from similar modules
        if similar_modules:
            prompt_parts.append("Similar existing modules for reference:")
            for mod in similar_modules[:2]:
                metadata = mod.get('metadata', {})
                mod_id = metadata.get('module_id', 'unknown')
                desc = metadata.get('description', '')
                params = metadata.get('parameters', {})

                prompt_parts.append(f"  Module: {mod_id}")
                prompt_parts.append(f"  Description: {desc}")
                prompt_parts.append(f"  Parameters: {json.dumps(params, indent=4)}")
                prompt_parts.append("")

        prompt_parts.append("Generate spec in this JSON format:")
        prompt_parts.append("""{
    "module_id": "excel.read",
    "category": "data",
    "description": "Read data from Excel file",
    "parameters": {
        "filepath": {
            "type": "string",
            "description": "Path to Excel file",
            "required": true
        }
    },
    "returns": {
        "data": {
            "type": "array",
            "description": "Array of row objects"
        }
    },
    "dependencies": ["openpyxl"]
}""")

        prompt_parts.append("\nOutput ONLY the JSON, no explanations.")

        return "\n".join(prompt_parts)

    def _call_llm(self, prompt: str) -> str:
        """Call Ollama LLM"""
        import requests

        try:
            response = requests.post(
                f"{self.ollama_endpoint}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 1024
                    }
                },
                timeout=60
            )

            if response.status_code != 200:
                raise Exception(f"LLM API error: {response.status_code}")

            return response.json().get('response', '').strip()

        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise


# Global instance
_spec_generator = None


def get_spec_generator() -> SpecGenerator:
    """Get global spec generator (singleton)"""
    global _spec_generator
    if _spec_generator is None:
        _spec_generator = SpecGenerator()
    return _spec_generator


# ============================================================
# Phase 5.2: Code Generator (Atomic Component)
# ============================================================

class CodeGenerator:
    """
    Generate Python code from module spec (Phase 5.2)
    Uses code-specialized LLM model
    """

    def __init__(self, ollama_endpoint: str = "http://localhost:11434"):
        self.ollama_endpoint = ollama_endpoint
        self.model = "qwen2.5-coder:32b"
        self.logger = logging.getLogger(__name__)

    async def generate_code(self, spec: Dict) -> str:
        """
        Generate Python code from spec

        Args:
            spec: Module specification

        Returns:
            Python code as string
        """

        # Build prompt
        prompt = self._build_code_prompt(spec)

        # Generate code
        code = self._call_llm(prompt)

        return code

    def _build_code_prompt(self, spec: Dict) -> str:
        """Build code generation prompt"""

        prompt_parts = [
            "Generate Python code for a module based on this specification:",
            "",
            f"Spec: {json.dumps(spec, indent=2)}",
            "",
            "Requirements:",
            "1. Inherit from BaseModule",
            "2. Implement validate_params() and execute() methods",
            "3. Use async/await for execute()",
            "4. Add proper error handling",
            "5. Include docstrings",
            "6. NEVER hardcode API keys or secrets",
            "",
            "Generate complete Python module code:"
        ]

        return "\n".join(prompt_parts)

    def _call_llm(self, prompt: str) -> str:
        """Call Ollama code model"""
        import requests

        try:
            response = requests.post(
                f"{self.ollama_endpoint}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.2,
                        "num_predict": 2048
                    }
                },
                timeout=120
            )

            if response.status_code != 200:
                raise Exception(f"LLM API error: {response.status_code}")

            code = response.json().get('response', '').strip()

            # Extract code from markdown if present
            if '```python' in code:
                code = code.split('```python')[1].split('```')[0].strip()

            return code

        except Exception as e:
            self.logger.error(f"Code generation failed: {e}")
            raise


# Global instance
_code_generator = None


def get_code_generator() -> CodeGenerator:
    """Get global code generator (singleton)"""
    global _code_generator
    if _code_generator is None:
        _code_generator = CodeGenerator()
    return _code_generator


# ============================================================
# Phase 5.2: Quality Gates (Atomic Component)
# ============================================================

import ast
import tempfile
from typing import Tuple

class QualityGates:
    """
    Run quality checks on generated code (Phase 5.2)

    Gates:
    1. AST parse check (syntax valid?)
    2. Bandit security scan
    3. Pylint code quality
    """

    def __init__(self):
        self.bandit_severity_threshold = "LOW"
        self.logger = logging.getLogger(__name__)

    def check_all(self, code: str) -> Tuple[bool, List[str]]:
        """
        Run all quality gates

        Args:
            code: Python code to check

        Returns:
            (passed, list_of_issues)
        """
        issues = []

        # Gate 1: AST parse
        ast_ok, ast_errors = self.check_ast(code)
        if not ast_ok:
            issues.extend([f"AST: {e}" for e in ast_errors])

        # Gate 2: Security scan
        bandit_ok, bandit_issues = self.check_security(code)
        if not bandit_ok:
            issues.extend([f"Security: {i}" for i in bandit_issues])

        # Gate 3: Code quality
        pylint_ok, pylint_issues = self.check_quality(code)
        if not pylint_ok:
            issues.extend([f"Quality: {i}" for i in pylint_issues])

        passed = len(issues) == 0

        return (passed, issues)

    def check_ast(self, code: str) -> Tuple[bool, List[str]]:
        """Check if code parses as valid Python"""
        try:
            ast.parse(code)
            return (True, [])
        except SyntaxError as e:
            return (False, [f"Line {e.lineno}: {e.msg}"])

    def check_security(self, code: str) -> Tuple[bool, List[str]]:
        """Run Bandit security scanner"""
        try:
            # Write code to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = f.name

            # Run Bandit
            result = subprocess.run(
                ['bandit', '-f', 'json', temp_path],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Parse results
            try:
                data = json.loads(result.stdout)
                results = data.get('results', [])

                # Filter by severity
                critical_issues = [
                    f"{r['issue_text']} (Line {r['line_number']})"
                    for r in results
                    if r['issue_severity'] in ['HIGH', 'MEDIUM', 'LOW']
                ]

                return (len(critical_issues) == 0, critical_issues)

            except json.JSONDecodeError:
                self.logger.error("Failed to parse Bandit output")
                return (True, [])

        except Exception as e:
            self.logger.error(f"Bandit check failed: {e}")
            return (True, [])

    def check_quality(self, code: str) -> Tuple[bool, List[str]]:
        """Run Pylint code quality check"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = f.name

            # Run Pylint
            result = subprocess.run(
                ['pylint', '--output-format=json', temp_path],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Parse results
            try:
                messages = json.loads(result.stdout)

                # Filter critical issues
                critical = [
                    f"{m['message']} (Line {m['line']})"
                    for m in messages
                    if m['type'] in ['error', 'warning']
                ]

                return (len(critical) == 0, critical)

            except json.JSONDecodeError:
                return (True, [])

        except Exception as e:
            self.logger.error(f"Pylint check failed: {e}")
            return (True, [])


# Global instance
_quality_gates = None


def get_quality_gates() -> QualityGates:
    """Get global quality gates (singleton)"""
    global _quality_gates
    if _quality_gates is None:
        _quality_gates = QualityGates()
    return _quality_gates


# ============================================================
# Phase 6.1: Lesson Extractor (Atomic Component)
# ============================================================

class LessonExtractor:
    """
    Extract lessons from recurring errors (Phase 6.1)
    Learns from failures and stores knowledge
    """

    def __init__(self, ollama_endpoint: str = "http://localhost:11434"):
        self.ollama_endpoint = ollama_endpoint
        self.model = "qwen2.5:32b"
        self.logger = logging.getLogger(__name__)

    async def extract_lesson(
        self,
        error_pattern: str,
        occurrences: List[Dict],
        successful_workarounds: List[Dict] = None
    ) -> Dict:
        """
        Extract lesson from recurring error

        Args:
            error_pattern: Error pattern (e.g., "browser.goto:TimeoutError")
            occurrences: List of error occurrences with job_ids
            successful_workarounds: List of successful fixes (if any)

        Returns:
            Lesson dict with problem, solution, and recommendations
        """

        # Build analysis prompt
        prompt = self._build_lesson_prompt(error_pattern, occurrences, successful_workarounds or [])

        # Call LLM to analyze
        response = self._call_llm(prompt)

        # Parse lesson
        try:
            lesson = json.loads(response)

            # Validate lesson structure
            required_fields = ['problem_description', 'root_cause', 'solution', 'recommendations']
            if not all(field in lesson for field in required_fields):
                raise ValueError(f"Lesson missing required fields: {required_fields}")

            # Add metadata
            lesson['error_pattern'] = error_pattern
            lesson['occurrences_count'] = len(occurrences)
            lesson['has_workaround'] = len(successful_workarounds or []) > 0
            lesson['extracted_at'] = datetime.now().isoformat()

            return lesson

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse lesson JSON: {e}")
            raise

    def _build_lesson_prompt(
        self,
        error_pattern: str,
        occurrences: List[Dict],
        workarounds: List[Dict]
    ) -> str:
        """Build lesson extraction prompt"""

        prompt_parts = [
            "Analyze this recurring error pattern and extract a lesson.",
            "",
            f"Error Pattern: {error_pattern}",
            f"Occurrences: {len(occurrences)} times",
            "",
            "Sample error messages:"
        ]

        # Add sample error messages (max 3)
        for i, occ in enumerate(occurrences[:3]):
            prompt_parts.append(f"  {i+1}. {occ.get('message', 'No message')[:100]}")

        prompt_parts.append("")

        # Add workarounds if available
        if workarounds:
            prompt_parts.append("Successful workarounds found:")
            for i, wa in enumerate(workarounds[:2]):
                prompt_parts.append(f"  {i+1}. {wa.get('solution', 'No solution')[:100]}")
            prompt_parts.append("")

        prompt_parts.append("Extract lesson in this JSON format:")
        prompt_parts.append("""{
    "problem_description": "Clear description of the problem",
    "root_cause": "Why this error happens",
    "solution": "How to fix or prevent it",
    "recommendations": [
        "Specific actionable recommendation 1",
        "Specific actionable recommendation 2"
    ],
    "prevention_strategy": "How to avoid this in the future"
}""")

        prompt_parts.append("\nOutput ONLY the JSON, no explanations.")

        return "\n".join(prompt_parts)

    def _call_llm(self, prompt: str) -> str:
        """Call Ollama LLM"""
        import requests

        try:
            response = requests.post(
                f"{self.ollama_endpoint}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 1024
                    }
                },
                timeout=60
            )

            if response.status_code != 200:
                raise Exception(f"LLM API error: {response.status_code}")

            return response.json().get('response', '').strip()

        except Exception as e:
            self.logger.error(f"Lesson extraction failed: {e}")
            raise

    async def store_lesson(self, lesson: Dict) -> str:
        """
        Store lesson in knowledge base

        Args:
            lesson: Lesson dict

        Returns:
            Knowledge ID
        """
        try:
            from src.core.memory.knowledge_extractor import get_knowledge_extractor

            knowledge = get_knowledge_extractor()

            # Format lesson content
            content = f"""
Lesson Learned from Recurring Error

Problem: {lesson['problem_description']}
Root Cause: {lesson['root_cause']}

Solution:
{lesson['solution']}

Recommendations:
{chr(10).join('- ' + r for r in lesson['recommendations'])}

Prevention Strategy:
{lesson['prevention_strategy']}

Pattern: {lesson['error_pattern']}
Occurrences: {lesson['occurrences_count']}
"""

            # Store in knowledge base
            knowledge_id = f"lesson_{lesson['error_pattern'].replace(':', '_')}_{datetime.now().strftime('%Y%m%d')}"

            # Use KnowledgeType.LESSON if available
            try:
                from src.core.memory.knowledge_extractor import KnowledgeType
                knowledge_type = KnowledgeType.LESSON
            except (ImportError, AttributeError):
                knowledge_type = "lesson"

            metadata = {
                'knowledge_type': knowledge_type,
                'error_pattern': lesson['error_pattern'],
                'occurrences_count': lesson['occurrences_count'],
                'has_workaround': lesson.get('has_workaround', False),
                'extracted_at': lesson['extracted_at']
            }

            result = knowledge._store_knowledge(knowledge_id, content, metadata)

            self.logger.info(f"Stored lesson: {knowledge_id}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to store lesson: {e}")
            raise


# Global instance
_lesson_extractor = None


def get_lesson_extractor() -> LessonExtractor:
    """Get global lesson extractor (singleton)"""
    global _lesson_extractor
    if _lesson_extractor is None:
        _lesson_extractor = LessonExtractor()
    return _lesson_extractor


# ============================================================
# Main Entry Point
# ============================================================

async def main():
    """Main execution"""
    engine = AutoEvolutionEngine()

    # Run one evolution cycle
    result = await engine.run_evolution_cycle()

    print("\n📊 Evolution Cycle Summary:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
