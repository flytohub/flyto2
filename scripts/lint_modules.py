#!/usr/bin/env python3
"""
Module Linter CLI Tool

Validates module files against the Module Specification.
Run before submitting PRs to ensure quality standards.

Usage:
    python scripts/lint_modules.py                    # Lint all modules
    python scripts/lint_modules.py path/to/module.py  # Lint specific file
    python scripts/lint_modules.py --strict           # Fail on warnings
"""

import sys
import os
import importlib.util
from pathlib import Path
from typing import List, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.modules.validator import ModuleValidator
from core.modules.registry import ModuleRegistry


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def find_module_files(root_dir: Path) -> List[Path]:
    """Find all Python files in modules directory"""
    modules_dir = root_dir / 'src' / 'core' / 'modules'
    module_files = []

    for path in modules_dir.rglob('*.py'):
        # Skip __pycache__ and __init__.py
        if '__pycache__' in str(path) or path.name == '__init__.py':
            continue
        # Skip base.py and registry.py
        if path.name in ['base.py', 'registry.py', 'validator.py']:
            continue
        module_files.append(path)

    return sorted(module_files)


def lint_file(file_path: Path, strict: bool = False) -> Tuple[bool, str, List[str], List[str]]:
    """
    Lint a single module file

    Returns:
        (success, module_name, errors, warnings)
    """
    # Import the module to trigger registration
    spec = importlib.util.spec_from_file_location("temp_module", file_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            return False, str(file_path), [f"Failed to import: {e}"], []

    # Get registered modules from this file
    registry = ModuleRegistry()
    all_modules = registry.get_all_metadata()

    # Validate each module
    errors = []
    warnings = []

    for module_id, metadata in all_modules.items():
        validator = ModuleValidator(strict_mode=False)
        try:
            validator.validate(metadata)
            errors.extend(validator.errors)
            warnings.extend(validator.warnings)
        except Exception as e:
            errors.append(str(e))

    success = len(errors) == 0 and (not strict or len(warnings) == 0)
    module_name = file_path.stem

    return success, module_name, errors, warnings


def print_results(results: List[Tuple[bool, str, List[str], List[str]]]):
    """Print linting results"""
    total = len(results)
    passed = sum(1 for r in results if r[0])
    failed = total - passed

    print(f"\n{Colors.BOLD}Module Linting Results{Colors.END}")
    print("=" * 60)

    for success, module_name, errors, warnings in results:
        if success:
            status = f"{Colors.GREEN}✓{Colors.END}"
        else:
            status = f"{Colors.RED}✗{Colors.END}"

        print(f"\n{status} {Colors.BOLD}{module_name}{Colors.END}")

        if errors:
            print(f"  {Colors.RED}Errors:{Colors.END}")
            for error in errors:
                print(f"    • {error}")

        if warnings:
            print(f"  {Colors.YELLOW}Warnings:{Colors.END}")
            for warning in warnings:
                print(f"    • {warning}")

        if not errors and not warnings:
            print(f"  {Colors.GREEN}All checks passed{Colors.END}")

    print("\n" + "=" * 60)
    print(f"Total: {total} modules")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
    if failed > 0:
        print(f"{Colors.RED}Failed: {failed}{Colors.END}")

    return failed == 0


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Lint Flyto2 modules for specification compliance'
    )
    parser.add_argument(
        'files',
        nargs='*',
        help='Specific module files to lint (default: all)'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Fail on warnings'
    )
    parser.add_argument(
        '--summary-only',
        action='store_true',
        help='Only show summary, not details'
    )

    args = parser.parse_args()

    # Determine files to lint
    root_dir = Path(__file__).parent.parent

    if args.files:
        files_to_lint = [Path(f) for f in args.files]
    else:
        files_to_lint = find_module_files(root_dir)

    if not files_to_lint:
        print(f"{Colors.YELLOW}No module files found to lint{Colors.END}")
        return 0

    print(f"{Colors.BLUE}Linting {len(files_to_lint)} module files...{Colors.END}\n")

    # Lint each file
    results = []
    for file_path in files_to_lint:
        success, module_name, errors, warnings = lint_file(file_path, args.strict)
        results.append((success, module_name, errors, warnings))

    # Print results
    if not args.summary_only:
        all_passed = print_results(results)
    else:
        passed = sum(1 for r in results if r[0])
        print(f"Passed: {passed}/{len(results)}")
        all_passed = passed == len(results)

    # Exit code
    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()
