"""
Testing Module
Automated testing and error reporting
"""
from .error_reporter import (
    TelegramErrorReporter,
    get_error_reporter,
    report_test_failure,
    report_module_error,
    report_system_error
)

__all__ = [
    "TelegramErrorReporter",
    "get_error_reporter",
    "report_test_failure",
    "report_module_error",
    "report_system_error"
]
