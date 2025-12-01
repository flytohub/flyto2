#!/usr/bin/env python
"""
Simple module validator - validates all registered modules.

Usage:
    python scripts/validate_all_modules.py

This script:
- Validates metadata for all registered modules
- Exits with code 1 if ANY module fails validation
- Exits with code 0 only when all modules pass
"""

import sys
from pathlib import Path
from typing import Tuple


def setup_sys_path() -> Path:
    """
    Configure PROJECT_ROOT and sys.path so this script can be executed
    from any working directory.

    :return: The project root path
    """
    project_root = Path(__file__).resolve().parent.parent
    src_path = project_root / "src"

    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    return project_root


def import_core_modules() -> Tuple[object, object, object]:
    """
    Import core modules and validator classes.

    :return: (ModuleRegistry, ModuleValidator, imported_modules)
    """
    try:
        # Importing this triggers auto-registration of atomic and third-party modules
        from core.modules import atomic, third_party  # noqa: F401

        from core.modules.registry import ModuleRegistry
        from core.modules.validator import ModuleValidator

        return ModuleRegistry, ModuleValidator, (atomic, third_party)

    except Exception as e:  # noqa: BLE001
        print("\n" + "=" * 60)
        print("✗ Failed to import core modules")
        print("=" * 60)
        print(f"  ERROR: {type(e).__name__}: {e}")
        print("  HINTS:")
        print("    - Make sure src/core/modules/ exists")
        print("    - Ensure you are running from the correct project root")
        print("    - When running inside Telegram/CI, ensure cwd is the project root")
        print("=" * 60 + "\n")
        sys.exit(1)


def main() -> int:
    """Validate all registered modules."""
    project_root = setup_sys_path()

    ModuleRegistry, ModuleValidator, _ = import_core_modules()

    registry = ModuleRegistry()
    all_metadata = registry.get_all_metadata()

    total = len(all_metadata)

    print(f"\n{'=' * 60}")
    print(f"Validating {total} registered modules")
    print(f"{'=' * 60}\n")

    if total == 0:
        print("⚠ No modules registered. Nothing to validate.\n")
        return 0  # No modules = success

    validator = ModuleValidator(strict_mode=False)
    passed = 0
    failed = 0
    warned = 0

    for module_id, metadata in all_metadata.items():
        try:
            validator.validate(metadata)

            if validator.errors:
                print(f"✗ {module_id}")
                for error in validator.errors:
                    print(f"  ERROR: {error}")
                failed += 1

            elif validator.warnings:
                print(f"⚠ {module_id}")
                for warning in validator.warnings:
                    print(f"  WARNING: {warning}")
                passed += 1
                warned += 1

            else:
                print(f"✓ {module_id}")
                passed += 1

        except Exception as e:  # noqa: BLE001
            # Treat unexpected exceptions as validation failures
            print(f"✗ {module_id}")
            print(f"  ERROR: {type(e).__name__}: {e}")
            failed += 1

        finally:
            # Reset between modules
            validator.errors = []
            validator.warnings = []

    print(f"\n{'=' * 60}")
    print(f"Total modules : {total}")
    print(f"Passed        : {passed}")
    print(f"With warnings : {warned}")
    print(f"Failed        : {failed}")
    print(f"{'=' * 60}\n")

    # Exit 1 if ANY module failed — used by CI / Telegram bot
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
