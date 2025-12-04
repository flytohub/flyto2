"""
Unit Tests for E2E Runner Check Validators

Tests all 5 check validator types:
- file_exists
- file_glob_any
- file_size
- file_content_startswith
- module_usage
"""
import pytest
from pathlib import Path
import tempfile
import sys

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.e2e_runner import (
    FileExistsCheck,
    FileGlobAnyCheck,
    FileSizeCheck,
    FileContentStartswithCheck,
    ModuleUsageCheck,
    CheckValidatorFactory
)


class TestFileExistsCheck:
    """Test file_exists validator"""

    def test_file_exists_success(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        validator = FileExistsCheck()
        spec = {"id": "test_check", "path": "test.txt"}
        result = validator.validate(spec, tmp_path)

        assert result.passed is True
        assert result.check_id == "test_check"
        assert result.check_type == "file_exists"

    def test_file_exists_failure(self, tmp_path):
        validator = FileExistsCheck()
        spec = {"id": "test_check", "path": "nonexistent.txt"}
        result = validator.validate(spec, tmp_path)

        assert result.passed is False
        assert "not found" in result.error_message.lower()


class TestFileGlobAnyCheck:
    """Test file_glob_any validator"""

    def test_glob_match_success(self, tmp_path):
        (tmp_path / "output").mkdir()
        (tmp_path / "output" / "file1.txt").write_text("content")
        (tmp_path / "output" / "file2.txt").write_text("content")

        validator = FileGlobAnyCheck()
        spec = {"id": "test_check", "pattern": "output/*.txt"}
        result = validator.validate(spec, tmp_path)

        assert result.passed is True
        assert result.actual_value == 2

    def test_glob_no_match(self, tmp_path):
        validator = FileGlobAnyCheck()
        spec = {"id": "test_check", "pattern": "output/*.txt"}
        result = validator.validate(spec, tmp_path)

        assert result.passed is False
        assert result.actual_value == 0


class TestFileSizeCheck:
    """Test file_size validator"""

    def test_file_size_sufficient(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("a" * 1000)

        validator = FileSizeCheck()
        spec = {"id": "test_check", "path": "test.txt", "min_bytes": 500}
        result = validator.validate(spec, tmp_path)

        assert result.passed is True
        assert result.actual_value >= 500

    def test_file_size_insufficient(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("small")

        validator = FileSizeCheck()
        spec = {"id": "test_check", "path": "test.txt", "min_bytes": 1000}
        result = validator.validate(spec, tmp_path)

        assert result.passed is False
        assert "too small" in result.error_message.lower()


class TestFileContentStartswithCheck:
    """Test file_content_startswith validator"""

    def test_content_starts_with_success(self, tmp_path):
        test_file = tmp_path / "test.svg"
        test_file.write_text("<svg width='100' height='100'></svg>")

        validator = FileContentStartswithCheck()
        spec = {"id": "test_check", "path": "test.svg", "prefix": "<svg"}
        result = validator.validate(spec, tmp_path)

        assert result.passed is True

    def test_content_starts_with_failure(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("wrong content")

        validator = FileContentStartswithCheck()
        spec = {"id": "test_check", "path": "test.txt", "prefix": "<svg"}
        result = validator.validate(spec, tmp_path)

        assert result.passed is False
        assert "does not start with" in result.error_message.lower()


class TestModuleUsageCheck:
    """Test module_usage validator"""

    def test_module_usage_success(self, tmp_path):
        execution_result = {
            "generated_modules": [
                {"module_name": "image.download"},
                {"module_name": "image.svg_convert"}
            ]
        }

        validator = ModuleUsageCheck()
        spec = {
            "id": "test_check",
            "includes": ["image.download", "image.svg_convert"]
        }
        result = validator.validate(spec, tmp_path, execution_result)

        assert result.passed is True

    def test_module_usage_missing_modules(self, tmp_path):
        execution_result = {
            "generated_modules": [
                {"module_name": "image.download"}
            ]
        }

        validator = ModuleUsageCheck()
        spec = {
            "id": "test_check",
            "includes": ["image.download", "image.svg_convert", "file.save"]
        }
        result = validator.validate(spec, tmp_path, execution_result)

        assert result.passed is False
        assert "missing modules" in result.error_message.lower()


class TestCheckValidatorFactory:
    """Test CheckValidatorFactory"""

    def test_factory_creates_all_validators(self):
        validators = [
            ("file_exists", FileExistsCheck),
            ("file_glob_any", FileGlobAnyCheck),
            ("file_size", FileSizeCheck),
            ("file_content_startswith", FileContentStartswithCheck),
            ("module_usage", ModuleUsageCheck),
        ]

        for check_type, expected_class in validators:
            validator = CheckValidatorFactory.create(check_type)
            assert validator is not None
            assert isinstance(validator, expected_class)

    def test_factory_returns_none_for_unknown(self):
        validator = CheckValidatorFactory.create("unknown_type")
        assert validator is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
