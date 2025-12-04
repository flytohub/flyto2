#!/usr/bin/env python3
"""
Module Generator - AI-powered automatic module generation

Capabilities:
- Generate module skeleton from specification
- Generate corresponding tests
- Validate generated code
- Integrate into system
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List


class ModuleGenerator:
    """Generate new modules automatically from specifications."""

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize module generator.

        Args:
            project_root: Project root path (auto-detected if not provided)
        """
        if project_root is None:
            current = Path(__file__).resolve()
            # src/core/meta/ → project root
            project_root = current.parent.parent.parent.parent

        self.project_root = project_root
        self.modules_dir = project_root / "src" / "core" / "modules" / "atomic"
        self.tests_dir = project_root / "workflows" / "_test"
        self.generated_log = project_root / "metrics" / "generated_modules.json"

    def generate_module(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complete module from specification.

        Args:
            spec: Module specification with:
                - module_id: e.g., "string.reverse"
                - description: What the module does
                - category: e.g., "string", "array", "math"
                - params: Dict of parameter names and type+description
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
            validation = self._validate_spec(spec)
            if not validation["valid"]:
                return {
                    "success": False,
                    "errors": validation["errors"],
                }

            module_code = self._generate_module_code(spec)
            test_code = self._generate_test_code(spec)

            module_path = self._get_module_path(spec)
            test_path = self._get_test_path(spec)

            self._write_module_file(module_path, module_code)
            self._update_init_file(module_path)
            self._write_test_file(test_path, test_code)

            self._log_generation(spec, module_path, test_path)

            return {
                "success": True,
                "module_path": str(module_path),
                "test_path": str(test_path),
                "code": module_code,
                "test_code": test_code,
                "errors": [],
            }

        except Exception as e:
            return {
                "success": False,
                "errors": [f"Generation failed: {str(e)}"],
            }

    def _validate_spec(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Validate module specification."""
        errors: List[str] = []

        required = ["module_id", "description", "category", "params", "returns"]
        for field in required:
            if field not in spec:
                errors.append(f"Missing required field: {field}")

        if "module_id" in spec:
            if not re.match(r"^[a-z_]+\.[a-z_]+$", spec["module_id"]):
                errors.append(f"Invalid module_id format: {spec['module_id']}")

        if "category" in spec:
            valid_categories = [
                "string",
                "array",
                "math",
                "object",
                "file",
                "datetime",
                "data",
                "utility",
                "test",
                "image",
                "video",
                "audio",
                "browser",
                "api",
                "ai",
            ]
            if spec["category"] not in valid_categories:
                errors.append(f"Invalid category: {spec['category']}")

        return {"valid": len(errors) == 0, "errors": errors}

    def _detect_imports_from_impl(self, implementation_code: str) -> List[str]:
        """
        Detect required imports by scanning implementation_code.
        This reduces reliance on GPT providing suggested_imports.
        """
        imports: List[str] = []

        impl = implementation_code

        def add_import(line: str) -> None:
            if line not in imports:
                imports.append(line)

        # httpx async client usage
        if "httpx." in impl or "httpx.AsyncClient" in impl:
            add_import("import httpx")

        # Path usage
        if "Path(" in impl or "pathlib.Path" in impl:
            add_import("from pathlib import Path")

        # regex usage
        if "re." in impl and "import re" not in impl:
            add_import("import re")

        return imports

    def _generate_module_code(self, spec: Dict[str, Any]) -> str:
        """Generate Python code for the module."""
        module_id = spec["module_id"]
        category, name = module_id.split(".")
        class_name = self._to_class_name(name)
        description = spec["description"]
        params = spec["params"]
        returns = spec["returns"]

        implementation_code = spec.get("implementation_code", "") or ""
        auto_imports = self._detect_imports_from_impl(implementation_code)

        # Parameter validation block
        param_validations: List[str] = []
        for param_name in params.keys():
            param_validations.append(
                f'        if "{param_name}" not in self.params:\n'
                f'            raise ValueError("Missing required parameter: {param_name}")\n'
                f'        self.{param_name} = self.params["{param_name}"]'
            )
        param_validation_code = "\n".join(param_validations)

        # Implementation body (properly indented as method body: 8 spaces)
        implementation = self._generate_implementation_template(spec)

        # Merge imports (base + auto-detected + suggested_imports)
        additional_imports = ""
        all_imports: List[str] = []

        # Backward compatibility: keep suggested_imports if present
        if "suggested_imports" in spec and spec["suggested_imports"]:
            if isinstance(spec["suggested_imports"], list):
                all_imports.extend(spec["suggested_imports"])
            elif isinstance(spec["suggested_imports"], str):
                all_imports.append(spec["suggested_imports"])

        for auto_imp in auto_imports:
            if auto_imp not in all_imports:
                all_imports.append(auto_imp)

        if all_imports:
            additional_imports = "\n" + "\n".join(sorted(all_imports))

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
        """Validate and extract parameters."""
{param_validation_code}

    async def execute(self) -> Any:
        """
        Execute the module logic.

        Returns:
            {returns}
        """
{implementation}
'''

        return code

    def _generate_implementation_template(self, spec: Dict[str, Any]) -> str:
        """
        Generate implementation template.

        Preferred path:
        - Use GPT-provided implementation_code (body only), properly indented.

        Fallback (CLI or manual spec):
        - Minimal unified-return implementation that always succeeds.
        """
        if "implementation_code" in spec and spec["implementation_code"]:
            impl_code = spec["implementation_code"].strip()
            lines = impl_code.split("\n")
            # 8 spaces indent for method body
            indented_lines = ["        " + line if line.strip() else "" for line in lines]
            return "\n".join(indented_lines)

        # Fallback (rare): keep it valid and aligned with unified return format.
        return (
            "        # Default fallback implementation.\n"
            "        # NOTE: This path should rarely be used in production.\n"
            "        result = None\n\n"
            "        return {\n"
            "            \"ok\": True,\n"
            "            \"output\": {\"result\": result},\n"
            "            \"error\": None,\n"
            "            \"meta\": {}\n"
            "        }\n"
        )

    def _generate_test_code(self, spec: Dict[str, Any]) -> str:
        """Generate YAML test for the module."""
        module_id = spec["module_id"]
        category, name = module_id.split(".")
        description = spec["description"]
        examples = spec.get("examples", [])

        test_steps: List[Dict[str, Any]] = []

        if examples:
            for i, example in enumerate(examples):
                step_id = f"test_{name}_{i+1}"
                test_steps.append(
                    {
                        "id": step_id,
                        "module": module_id,
                        "params": example.get("params", {}),
                        "description": example.get(
                            "description", f"Test case {i+1}"
                        ),
                    }
                )
        else:
            default_params = self._generate_default_params(spec["params"])
            test_steps.append(
                {
                    "id": f"test_{name}_basic",
                    "module": module_id,
                    "params": default_params,
                    "description": "Basic functionality test",
                }
            )

        # Verification step: check that result field is not null.
        test_steps.append(
            {
                "id": "verify_result",
                "module": "test.assert_not_null",
                "params": {
                    "value": f"${{{test_steps[0]['id']}}}",
                    "message": f"{module_id} should return a result",
                },
            }
        )

        yaml_content = (
            f'name: "Test {module_id}"\n'
            f'description: "{description} - Auto-generated test"\n\n'
            "steps:\n"
        )

        for step in test_steps:
            yaml_content += (
                f"  - id: {step['id']}\n"
                f"    module: {step['module']}\n"
                f"    params:\n"
            )
            for key, value in step["params"].items():
                if isinstance(value, str):
                    yaml_content += f'      {key}: "{value}"\n'
                else:
                    yaml_content += f"      {key}: {value}\n"

            if "description" in step:
                yaml_content += f'    description: "{step["description"]}"\n'
            yaml_content += "\n"

        return yaml_content

    def _generate_default_params(self, params: Dict[str, str]) -> Dict[str, Any]:
        """Generate realistic parameter values for testing."""
        defaults: Dict[str, Any] = {}

        for param_name, param_type in params.items():
            param_type_lower = param_type.lower()
            param_name_lower = param_name.lower()

            if "string" in param_type_lower or "str" in param_type_lower:
                if "url" in param_name_lower or "link" in param_name_lower:
                    defaults[param_name] = "https://httpbin.org/image/jpeg"
                elif "path" in param_name_lower or "file" in param_name_lower:
                    defaults[param_name] = f"/tmp/test_{param_name}.dat"
                elif "email" in param_name_lower:
                    defaults[param_name] = "test@example.com"
                elif "name" in param_name_lower:
                    defaults[param_name] = "TestName"
                elif "query" in param_name_lower or "search" in param_name_lower:
                    defaults[param_name] = "test search query"
                elif "text" in param_name_lower or "content" in param_name_lower:
                    defaults[param_name] = "Test content"
                else:
                    defaults[param_name] = "test_value"
            elif "int" in param_type_lower:
                defaults[param_name] = 42
            elif "float" in param_type_lower:
                defaults[param_name] = 3.14
            elif "bool" in param_type_lower:
                defaults[param_name] = True
            elif "array" in param_type_lower or "list" in param_type_lower:
                defaults[param_name] = [1, 2, 3]
            elif "object" in param_type_lower or "dict" in param_type_lower:
                defaults[param_name] = {"key": "value"}
            else:
                defaults[param_name] = "test"

        return defaults

    def _get_module_path(self, spec: Dict[str, Any]) -> Path:
        """Determine where to save the module file."""
        category = spec["category"]
        module_id = spec["module_id"]
        _, name = module_id.split(".")

        category_dir = self.modules_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)

        init_file = category_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text(f'"""\n{category.capitalize()} modules\n"""\n')

        return category_dir / f"{name}.py"

    def _get_test_path(self, spec: Dict[str, Any]) -> Path:
        """Determine where to save the test file."""
        module_id = spec["module_id"]
        test_name = f"test_{module_id.replace('.', '_')}.yaml"
        return self.tests_dir / test_name

    def _write_module_file(self, path: Path, code: str) -> None:
        """Write module code to file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(code, encoding="utf-8")
        print(f"✅ Module written to: {path}")

    def _write_test_file(self, path: Path, code: str) -> None:
        """Write test code to file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(code, encoding="utf-8")
        print(f"✅ Test written to: {path}")

    def _update_init_file(self, module_path: Path) -> None:
        """Update __init__.py to import the newly generated module."""
        try:
            module_file = Path(module_path)
            module_dir = module_file.parent
            init_file = module_dir / "__init__.py"

            module_name = module_file.stem

            if init_file.exists():
                existing_content = init_file.read_text()
            else:
                existing_content = (
                    f'"""\n{module_dir.name.capitalize()} modules\n"""\n\n__all__ = []\n'
                )

            import_statement = f"from .{module_name} import"
            if import_statement in existing_content:
                print(f"ℹ️  Import already exists in {init_file}")
                return

            new_import = (
                "\ntry:\n"
                f"    from .{module_name} import *\n"
                "except ImportError:\n"
                "    pass\n"
            )

            if "__all__" in existing_content:
                lines = existing_content.split("\n")
                insert_idx = None
                for i, line in enumerate(lines):
                    if line.strip().startswith("__all__"):
                        insert_idx = i
                        break

                if insert_idx is not None:
                    lines.insert(insert_idx, new_import.rstrip())
                    updated_content = "\n".join(lines)
                else:
                    updated_content = existing_content.rstrip() + new_import
            else:
                updated_content = existing_content.rstrip() + new_import

            init_file.write_text(updated_content)
            print(f"✅ Updated {init_file} to import {module_name}")

        except Exception as e:
            print(f"⚠️  Warning: Failed to update __init__.py: {e}")

    def _log_generation(
        self, spec: Dict[str, Any], module_path: Path, test_path: Path
    ) -> None:
        """Log module generation to metrics."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "module_id": spec["module_id"],
            "category": spec["category"],
            "description": spec["description"],
            "module_path": str(module_path),
            "test_path": str(test_path),
            "auto_generated": True,
        }

        if self.generated_log.exists():
            data = json.loads(self.generated_log.read_text())
        else:
            data = {"generations": []}

        data["generations"].append(log_entry)

        self.generated_log.parent.mkdir(parents=True, exist_ok=True)
        self.generated_log.write_text(json.dumps(data, indent=2))

    def _to_class_name(self, name: str) -> str:
        """Convert module name to class name (e.g., 'reverse' -> 'Reverse')."""
        return "".join(word.capitalize() for word in name.split("_"))

    def _format_params_doc(self, params: Dict[str, str]) -> str:
        """
        Format parameters for docstring.

        Expects param_type string like:
            "str - The URL of the image to download"
        """
        lines: List[str] = []
        for param_name, param_type in params.items():
            type_part = param_type
            desc_part = "Parameter value"
            if " - " in param_type:
                type_part, desc_part = [
                    p.strip() for p in param_type.split(" - ", 1)
                ]
            lines.append(f"        {param_name} ({type_part}): {desc_part}")
        return "\n".join(lines)


def main() -> None:
    """CLI for module generation."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate new modules automatically")
    parser.add_argument("--module-id", required=True, help="Module ID (e.g., string.reverse)")
    parser.add_argument("--description", required=True, help="Module description")
    parser.add_argument("--category", required=True, help="Module category")
    parser.add_argument("--params", required=True, help="Parameters as JSON")
    parser.add_argument("--returns", required=True, help="Return type description")

    args = parser.parse_args()

    params = json.loads(args.params)

    spec = {
        "module_id": args.module_id,
        "description": args.description,
        "category": args.category,
        "params": params,
        "returns": args.returns,
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
