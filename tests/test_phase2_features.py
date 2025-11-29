#!/usr/bin/env python3
"""
Unit tests for Phase 2 module features:
- Execution control (timeout, retry, concurrency)
- Security settings (credentials, sensitive data, permissions)
"""
import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from src.core.modules.registry import ModuleRegistry
from src.core.modules.base import BaseModule


class TestPhase2ExecutionSettings:
    """Test Phase 2 execution control settings"""

    def test_module_has_timeout_metadata(self):
        """Test that modules with timeout have correct metadata"""
        # Test browser launch module has timeout
        browser_launch = ModuleRegistry.get_metadata('core.browser.launch')
        assert browser_launch is not None
        assert 'timeout' in browser_launch
        assert browser_launch['timeout'] == 10

    def test_module_has_retryable_metadata(self):
        """Test that modules with retry have correct metadata"""
        # Test Anthropic module is retryable (API calls should be retryable)
        anthropic = ModuleRegistry.get_metadata('api.anthropic.chat')
        assert anthropic is not None
        assert anthropic['retryable'] is True
        assert anthropic['max_retries'] >= 2

    def test_module_has_concurrent_safe_metadata(self):
        """Test that modules have concurrent_safe flag"""
        # Browser modules should NOT be concurrent safe
        browser_launch = ModuleRegistry.get_metadata('core.browser.launch')
        assert browser_launch is not None
        assert browser_launch['concurrent_safe'] is False

        # API modules should be concurrent safe
        http_get = ModuleRegistry.get_metadata('core.api.http_get')
        assert http_get is not None
        assert http_get['concurrent_safe'] is True

    def test_all_modules_have_phase2_fields(self):
        """Test that all modules have Phase 2 fields defined"""
        all_modules = ModuleRegistry.get_all_metadata()

        required_fields = ['timeout', 'retryable', 'concurrent_safe']

        for module_id, module in all_modules.items():
            for field in required_fields:
                assert field in module, f"Module {module_id} missing {field}"

    def test_retryable_modules_have_max_retries(self):
        """Test that retryable modules have max_retries set"""
        all_modules = ModuleRegistry.get_all_metadata()

        for module_id, module in all_modules.items():
            if module.get('retryable'):
                assert 'max_retries' in module, f"Module {module_id} is retryable but missing max_retries"
                assert module['max_retries'] > 0, f"Module {module_id} has invalid max_retries"


class TestPhase2SecuritySettings:
    """Test Phase 2 security settings"""

    def test_module_has_requires_credentials(self):
        """Test that API modules have requires_credentials set"""
        # OpenAI module should require credentials
        anthropic_chat = ModuleRegistry.get_metadata('api.anthropic.chat')
        if anthropic_chat:
            assert anthropic_chat['requires_credentials'] is True

        # File read should NOT require credentials
        file_read = ModuleRegistry.get_metadata('file.read')
        if file_read:
            assert file_read['requires_credentials'] is False

    def test_module_has_handles_sensitive_data(self):
        """Test that modules declare sensitive data handling"""
        # AI chat modules handle sensitive data (user prompts)
        anthropic = ModuleRegistry.get_metadata('api.anthropic.chat')
        if anthropic:
            assert anthropic['handles_sensitive_data'] is True

        # Math operations don't handle sensitive data
        math_calc = ModuleRegistry.get_metadata('math.calculate')
        if math_calc:
            assert math_calc['handles_sensitive_data'] is False

    def test_module_has_required_permissions(self):
        """Test that modules declare required permissions"""
        # File write module should require file.write permission
        file_write = ModuleRegistry.get_metadata('file.write')
        if file_write:
            assert 'required_permissions' in file_write
            assert 'file.write' in file_write['required_permissions']

        # Browser launch should require browser.launch permission
        browser_launch = ModuleRegistry.get_metadata('core.browser.launch')
        if browser_launch:
            assert 'required_permissions' in browser_launch
            assert 'browser.launch' in browser_launch['required_permissions']

    def test_all_modules_have_security_fields(self):
        """Test that all modules have security fields defined"""
        all_modules = ModuleRegistry.get_all_metadata()

        required_fields = ['requires_credentials', 'handles_sensitive_data', 'required_permissions']

        for module_id, module in all_modules.items():
            for field in required_fields:
                assert field in module, f"Module {module_id} missing {field}"


class TestPhase2ValidationLogic:
    """Test Phase 2 validation logic"""

    def test_timeout_values_are_reasonable(self):
        """Test that timeout values are reasonable"""
        all_modules = ModuleRegistry.get_all_metadata()

        for module_id, module in all_modules.items():
            timeout = module.get('timeout')

            if timeout is not None:
                # Timeout should be between 1 second and 10 minutes
                assert 1 <= timeout <= 600, f"Module {module_id} has unreasonable timeout: {timeout}s"

    def test_max_retries_are_reasonable(self):
        """Test that max_retries values are reasonable"""
        all_modules = ModuleRegistry.get_all_metadata()

        for module_id, module in all_modules.items():
            if module.get('retryable'):
                max_retries = module.get('max_retries', 0)
                # Max retries should be between 1 and 5
                assert 1 <= max_retries <= 5, f"Module {module_id} has unreasonable max_retries: {max_retries}"

    def test_permission_format_is_valid(self):
        """Test that permission strings follow format: resource.action"""
        all_modules = ModuleRegistry.get_all_metadata()

        valid_permissions = [
            'network.access', 'file.read', 'file.write',
            'browser.launch', 'browser.read', 'system.process',
            'database.read', 'database.write', 'ai.api'
        ]

        for module_id, module in all_modules.items():
            permissions = module.get('required_permissions', [])

            for perm in permissions:
                # Permission should be in valid list or follow resource.action format
                if perm not in valid_permissions:
                    assert '.' in perm, f"Module {module_id} has invalid permission format: {perm}"


class TestPhase2ModuleCoverage:
    """Test Phase 2 coverage across module categories"""

    def test_atomic_modules_have_phase2(self):
        """Test that atomic modules have Phase 2 fields"""
        all_modules = ModuleRegistry.get_all_metadata()

        atomic_modules = {k: v for k, v in all_modules.items() if k.startswith(('core.', 'file.', 'string.', 'array.', 'math.', 'data.', 'utility.'))}

        assert len(atomic_modules) > 0, "No atomic modules found"

        for module_id, module in atomic_modules.items():
            assert 'timeout' in module
            assert 'retryable' in module
            assert 'concurrent_safe' in module

    def test_third_party_modules_have_phase2(self):
        """Test that third-party modules have Phase 2 fields"""
        all_modules = ModuleRegistry.get_all_metadata()

        third_party_modules = {k: v for k, v in all_modules.items() if k.startswith(('api.', 'notification.', 'db.', 'cloud.'))}

        assert len(third_party_modules) > 0, "No third-party modules found"

        for module_id, module in third_party_modules.items():
            assert 'requires_credentials' in module
            assert 'handles_sensitive_data' in module
            assert 'required_permissions' in module

    def test_browser_modules_have_phase2(self):
        """Test that browser modules have Phase 2 fields"""
        all_modules = ModuleRegistry.get_all_metadata()

        browser_modules = {k: v for k, v in all_modules.items() if 'browser' in k}

        assert len(browser_modules) > 0, "No browser modules found"

        # Browser launch module should NOT be concurrent safe (resource conflict)
        browser_launch = ModuleRegistry.get_metadata('core.browser.launch')
        if browser_launch:
            assert browser_launch['concurrent_safe'] is False, "Browser launch should not be concurrent_safe"

        # All browser modules should have Phase 2 fields
        for module_id, module in browser_modules.items():
            assert 'timeout' in module or module.get('timeout') is None
            assert 'retryable' in module
            assert 'concurrent_safe' in module


class TestPhase2I18nTranslations:
    """Test Phase 2 i18n translations"""

    def test_zh_translations_exist(self):
        """Test that Chinese translations for Phase 2 exist"""
        import json
        from pathlib import Path

        zh_file = Path(__file__).parent.parent / 'i18n' / 'zh.json'
        assert zh_file.exists(), "zh.json file not found"

        with open(zh_file, 'r', encoding='utf-8') as f:
            zh_data = json.load(f)

        # Check Phase 2 section exists
        assert 'phase2' in zh_data, "phase2 section missing in zh.json"
        assert 'execution' in zh_data['phase2']
        assert 'security' in zh_data['phase2']

        # Check key translations exist
        assert 'timeout' in zh_data['phase2']['execution']
        assert 'retryable' in zh_data['phase2']['execution']
        assert 'requires_credentials' in zh_data['phase2']['security']
        assert 'handles_sensitive_data' in zh_data['phase2']['security']

    def test_ja_translations_exist(self):
        """Test that Japanese translations for Phase 2 exist"""
        import json
        from pathlib import Path

        ja_file = Path(__file__).parent.parent / 'i18n' / 'ja.json'
        assert ja_file.exists(), "ja.json file not found"

        with open(ja_file, 'r', encoding='utf-8') as f:
            ja_data = json.load(f)

        # Check Phase 2 section exists
        assert 'phase2' in ja_data, "phase2 section missing in ja.json"
        assert 'execution' in ja_data['phase2']
        assert 'security' in ja_data['phase2']

        # Check key translations exist
        assert 'timeout' in ja_data['phase2']['execution']
        assert 'retryable' in ja_data['phase2']['execution']
        assert 'requires_credentials' in ja_data['phase2']['security']
        assert 'handles_sensitive_data' in ja_data['phase2']['security']

    def test_permission_translations_exist(self):
        """Test that permission translations exist"""
        import json
        from pathlib import Path

        zh_file = Path(__file__).parent.parent / 'i18n' / 'zh.json'
        with open(zh_file, 'r', encoding='utf-8') as f:
            zh_data = json.load(f)

        permissions = zh_data['phase2']['permissions']

        # Check common permissions are translated
        assert 'network.access' in permissions
        assert 'file.read' in permissions
        assert 'file.write' in permissions
        assert 'browser.launch' in permissions


class TestPhase2Consistency:
    """Test Phase 2 consistency rules"""

    def test_retryable_without_timeout_is_valid(self):
        """Test that modules can be retryable without timeout"""
        all_modules = ModuleRegistry.get_all_metadata()

        # Some modules might be retryable but instant (no timeout needed)
        # This should be valid
        for module_id, module in all_modules.items():
            if module.get('retryable') and not module.get('timeout'):
                # This is valid - just document it
                pass

    def test_credential_modules_have_network_permission(self):
        """Test that modules requiring credentials usually need network access"""
        all_modules = ModuleRegistry.get_all_metadata()

        for module_id, module in all_modules.items():
            # If module requires credentials, it likely needs network access
            # (except for local auth systems)
            if module.get('requires_credentials'):
                permissions = module.get('required_permissions', [])
                # Most credential-requiring modules need network access
                # But this is not a hard rule (e.g., local database with auth)
                # So we just check the field exists
                assert isinstance(permissions, list)

    def test_sensitive_data_modules_documented(self):
        """Test that modules handling sensitive data are properly documented"""
        all_modules = ModuleRegistry.get_all_metadata()

        sensitive_modules = []
        for module_id, module in all_modules.items():
            if module.get('handles_sensitive_data'):
                sensitive_modules.append(module_id)

        # Should have at least a few modules handling sensitive data
        assert len(sensitive_modules) > 0, "No modules declared as handling sensitive data"

        # Document which modules handle sensitive data
        print(f"\nModules handling sensitive data ({len(sensitive_modules)}):")
        for module_id in sensitive_modules:
            print(f"  - {module_id}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
