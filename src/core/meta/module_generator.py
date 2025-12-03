#!/usr/bin/env python3
"""
Module Generator - AI-powered automatic module generation

Capabilities:
- Generate module skeleton from specification
- Generate corresponding tests
- Validate generated code
- Integrate into system
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import re


class ModuleGenerator:
    """Generate new modules automatically from specifications"""

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize module generator

        Args:
            project_root: Project root path (auto-detected if not provided)
        """
        if project_root is None:
            # Auto-detect project root
            current = Path(__file__).resolve()
            # Go up from src/core/meta/ to project root
            project_root = current.parent.parent.parent.parent

        self.project_root = project_root
        self.modules_dir = project_root / "src" / "core" / "modules" / "atomic"
        self.tests_dir = project_root / "workflows" / "_test"
        self.generated_log = project_root / "metrics" / "generated_modules.json"

    def generate_module(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complete module from specification

        Args:
            spec: Module specification with:
                - module_id: e.g., "string.reverse"
                - description: What the module does
                - category: e.g., "string", "array", "math"
                - params: Dict of parameter names and types
                - returns: Return type description
                - examples: List of example usages (optional)

        Returns:
            Dict with:
                - success: bool
                - module_path: Path to generated module
                - test_path: Path to generated test
                - code: Generated module code
                - test_code: Generated test code
                - errors: List of errors if any
        """
        try:
            # Validate spec
            validation = self._validate_spec(spec)
            if not validation["valid"]:
                return {
                    "success": False,
                    "errors": validation["errors"]
                }

            # Generate module code
            module_code = self._generate_module_code(spec)

            # Generate test code
            test_code = self._generate_test_code(spec)

            # Determine file paths
            module_path = self._get_module_path(spec)
            test_path = self._get_test_path(spec)

            # Write files
            self._write_module_file(module_path, module_code)
            self._write_test_file(test_path, test_code)

            # Log generation
            self._log_generation(spec, module_path, test_path)

            return {
                "success": True,
                "module_path": str(module_path),
                "test_path": str(test_path),
                "code": module_code,
                "test_code": test_code,
                "errors": []
            }

        except Exception as e:
            return {
                "success": False,
                "errors": [f"Generation failed: {str(e)}"]
            }

    def _validate_spec(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Validate module specification"""
        errors = []

        # Required fields
        required = ["module_id", "description", "category", "params", "returns"]
        for field in required:
            if field not in spec:
                errors.append(f"Missing required field: {field}")

        # Validate module_id format
        if "module_id" in spec:
            if not re.match(r'^[a-z_]+\.[a-z_]+$', spec["module_id"]):
                errors.append(f"Invalid module_id format: {spec['module_id']}")

        # Validate category
        if "category" in spec:
            valid_categories = ["string", "array", "math", "object", "file",
                              "datetime", "data", "utility", "test", "image",
                              "video", "audio", "browser", "api", "ai"]
            if spec["category"] not in valid_categories:
                errors.append(f"Invalid category: {spec['category']}")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    def _generate_module_code(self, spec: Dict[str, Any]) -> str:
        """Generate Python code for the module"""
        module_id = spec["module_id"]
        category, name = module_id.split(".")
        class_name = self._to_class_name(name)
        description = spec["description"]
        params = spec["params"]
        returns = spec["returns"]

        # Generate parameter validation
        param_validations = []
        for param_name, param_type in params.items():
            param_validations.append(
                f'        if "{param_name}" not in self.params:\n'
                f'            raise ValueError("Missing required parameter: {param_name}")\n'
                f'        self.{param_name} = self.params["{param_name}"]'
            )

        param_validation_code = "\n".join(param_validations)

        # Generate example implementation based on category
        implementation = self._generate_implementation_template(spec)

        # Get suggested imports from GPT-4o (if provided)
        additional_imports = ""
        if "suggested_imports" in spec and spec["suggested_imports"]:
            imports_list = spec["suggested_imports"]
            if isinstance(imports_list, list):
                additional_imports = "\n" + "\n".join(imports_list)
            elif isinstance(imports_list, str):
                additional_imports = "\n" + imports_list

        code = f'''"""
{class_name} Module - {description}

Auto-generated by ModuleGenerator
Generated at: {datetime.now().isoformat()}
"""

from src.core.modules.base import BaseModule
from src.core.modules.registry import register_module
from typing import Any, Dict{additional_imports}


@register_module('{module_id}')
class {class_name}(BaseModule):
    """
    {description}

    Parameters:
{self._format_params_doc(params)}

    Returns:
        {returns}
    """

    module_name = "{class_name}"
    module_description = "{description}"

    def validate_params(self):
        """Validate and extract parameters"""
{param_validation_code}

    async def execute(self) -> Any:
        """
        Execute the module logic

        Returns:
            {returns}
        """
        try:
{implementation}

        except Exception as e:
            raise RuntimeError(f"{{self.module_name}} execution failed: {{str(e)}}")
'''

        return code

    def _generate_implementation_template(self, spec: Dict[str, Any]) -> str:
        """Generate implementation template - use GPT-4o code if available"""

        # First, check if GPT-4o provided actual implementation code
        if "implementation_code" in spec and spec["implementation_code"]:
            impl_code = spec["implementation_code"].strip()
            # Ensure proper indentation (12 spaces for execute method body)
            lines = impl_code.split('\n')
            indented_lines = ['            ' + line if line.strip() else '' for line in lines]
            return '\n'.join(indented_lines)

        # Fallback: generic placeholder (should rarely happen with GPT-4o)
        return '''            # Implementation not provided by AI
            # TODO: Implement actual logic here
            result = None

            return {
                "result": result,
                "status": "success"
            }'''

    def _generate_test_code(self, spec: Dict[str, Any]) -> str:
        """Generate YAML test for the module"""
        module_id = spec["module_id"]
        category, name = module_id.split(".")
        description = spec["description"]
        examples = spec.get("examples", [])

        # Generate test steps from examples
        test_steps = []

        if examples:
            for i, example in enumerate(examples):
                step_id = f"test_{name}_{i+1}"
                test_steps.append({
                    "id": step_id,
                    "module": module_id,
                    "params": example.get("params", {}),
                    "description": example.get("description", f"Test case {i+1}")
                })
        else:
            # Generate default test
            default_params = self._generate_default_params(spec["params"])
            test_steps.append({
                "id": f"test_{name}_basic",
                "module": module_id,
                "params": default_params,
                "description": "Basic functionality test"
            })

        # Generate verification step
        test_steps.append({
            "id": "verify_result",
            "module": "test.assert_not_null",
            "params": {
                "value": f"${{{test_steps[0]['id']}.result}}",
                "message": f"{module_id} should return a result"
            }
        })

        # Format as YAML
        yaml_content = f'''name: "Test {module_id}"
description: "{description} - Auto-generated test"

steps:
'''

        for step in test_steps:
            yaml_content += f'''  - id: {step['id']}
    module: {step['module']}
    params:
'''
            for key, value in step['params'].items():
                if isinstance(value, str) and value.startswith("${"):
                    yaml_content += f'      {key}: "{value}"\n'
                elif isinstance(value, str):
                    yaml_content += f'      {key}: "{value}"\n'
                else:
                    yaml_content += f'      {key}: {value}\n'

            if 'description' in step:
                yaml_content += f'    description: "{step["description"]}"\n'
            yaml_content += '\n'

        return yaml_content

    def _generate_default_params(self, params: Dict[str, str]) -> Dict[str, Any]:
        """Generate realistic parameter values for testing"""
        defaults = {}

        for param_name, param_type in params.items():
            if "string" in param_type.lower() or "str" in param_type.lower():
                # Generate realistic values based on parameter name
                param_lower = param_name.lower()
                if "url" in param_lower or "link" in param_lower:
                    # Use a reliable test image URL
                    defaults[param_name] = "https://httpbin.org/image/jpeg"
                elif "path" in param_lower or "file" in param_lower:
                    # Use /tmp for test files
                    defaults[param_name] = f"/tmp/test_{param_name}.dat"
                elif "email" in param_lower:
                    defaults[param_name] = "test@example.com"
                elif "name" in param_lower:
                    defaults[param_name] = "TestName"
                elif "query" in param_lower or "search" in param_lower:
                    defaults[param_name] = "test search query"
                elif "text" in param_lower or "content" in param_lower:
                    defaults[param_name] = "Test content"
                else:
                    defaults[param_name] = "test_value"
            elif "int" in param_type.lower():
                defaults[param_name] = 42
            elif "float" in param_type.lower():
                defaults[param_name] = 3.14
            elif "bool" in param_type.lower():
                defaults[param_name] = True
            elif "array" in param_type.lower() or "list" in param_type.lower():
                defaults[param_name] = [1, 2, 3]
            elif "object" in param_type.lower() or "dict" in param_type.lower():
                defaults[param_name] = {"key": "value"}
            else:
                defaults[param_name] = "test"

        return defaults

    def _get_module_path(self, spec: Dict[str, Any]) -> Path:
        """Determine where to save the module file"""
        category = spec["category"]
        module_id = spec["module_id"]
        _, name = module_id.split(".")

        # Create category directory if needed
        category_dir = self.modules_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)

        # Create __init__.py if it doesn't exist (makes directory a Python package)
        init_file = category_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text(f'"""\n{category.capitalize()} modules\n"""\n')

        return category_dir / f"{name}.py"

    def _get_test_path(self, spec: Dict[str, Any]) -> Path:
        """Determine where to save the test file"""
        module_id = spec["module_id"]
        test_name = f"test_{module_id.replace('.', '_')}.yaml"

        return self.tests_dir / test_name

    def _write_module_file(self, path: Path, code: str):
        """Write module code to file"""
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(code)

        print(f"✅ Module written to: {path}")

    def _write_test_file(self, path: Path, code: str):
        """Write test code to file"""
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(code)

        print(f"✅ Test written to: {path}")

    def _log_generation(self, spec: Dict[str, Any], module_path: Path, test_path: Path):
        """Log module generation to metrics"""
        import json

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "module_id": spec["module_id"],
            "category": spec["category"],
            "description": spec["description"],
            "module_path": str(module_path),
            "test_path": str(test_path),
            "auto_generated": True
        }

        # Load existing log
        if self.generated_log.exists():
            with open(self.generated_log, 'r') as f:
                log_data = json.load(f)
        else:
            log_data = {"generations": []}

        # Append new entry
        log_data["generations"].append(log_entry)

        # Save log
        self.generated_log.parent.mkdir(parents=True, exist_ok=True)
        with open(self.generated_log, 'w') as f:
            json.dump(log_data, f, indent=2)

    def _to_class_name(self, name: str) -> str:
        """Convert module name to class name (e.g., 'reverse' -> 'Reverse')"""
        return ''.join(word.capitalize() for word in name.split('_'))

    def _format_params_doc(self, params: Dict[str, str]) -> str:
        """Format parameters for docstring"""
        lines = []
        for param_name, param_type in params.items():
            lines.append(f"        {param_name} ({param_type}): Parameter description")
        return "\n".join(lines)


def main():
    """CLI for module generation"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate new modules automatically")
    parser.add_argument("--module-id", required=True, help="Module ID (e.g., string.reverse)")
    parser.add_argument("--description", required=True, help="Module description")
    parser.add_argument("--category", required=True, help="Module category")
    parser.add_argument("--params", required=True, help="Parameters as JSON")
    parser.add_argument("--returns", required=True, help="Return type description")

    args = parser.parse_args()

    import json
    params = json.loads(args.params)

    spec = {
        "module_id": args.module_id,
        "description": args.description,
        "category": args.category,
        "params": params,
        "returns": args.returns
    }

    generator = ModuleGenerator()
    result = generator.generate_module(spec)

    if result["success"]:
        print("\n✅ Module generation successful!")
        print(f"Module: {result['module_path']}")
        print(f"Test: {result['test_path']}")
    else:
        print("\n❌ Module generation failed!")
        for error in result["errors"]:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
