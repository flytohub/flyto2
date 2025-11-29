#!/usr/bin/env python3
"""
Simple module validator - validates all registered modules

Usage:
    python scripts/validate_all_modules.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Import modules to register them
from core.modules import atomic, third_party
from core.modules.registry import ModuleRegistry
from core.modules.validator import ModuleValidator


def main():
    """Validate all registered modules"""
    registry = ModuleRegistry()
    all_metadata = registry.get_all_metadata()

    print(f"\n{'='*60}")
    print(f"Validating {len(all_metadata)} registered modules")
    print(f"{'='*60}\n")

    validator = ModuleValidator(strict_mode=False)
    passed = 0
    failed = 0

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
            else:
                print(f"✓ {module_id}")
                passed += 1

            # Reset for next module
            validator.errors = []
            validator.warnings = []

        except Exception as e:
            print(f"✗ {module_id}")
            print(f"  ERROR: {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Total: {len(all_metadata)} modules")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"{'='*60}\n")

    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
