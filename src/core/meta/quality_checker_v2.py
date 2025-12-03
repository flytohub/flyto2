"""
Quality Checker V2 - Enterprise-grade code quality assessment
Implements MODULE_QUALITY_STANDARDS.md with atomic, zero-coupling design
"""
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re


class QualityCheck:
    """Base class for atomic quality checks"""

    def __init__(self, weight: float, name: str):
        self.weight = weight
        self.name = name
        self.score = 0.0
        self.issues = []
        self.strengths = []

    def check(self, content: str, file_path: str) -> float:
        """Execute the quality check. Returns score (0 to weight)"""
        raise NotImplementedError

    def add_issue(self, message: str, deduction: float):
        """Add an issue and reduce score"""
        self.issues.append({"message": message, "deduction": deduction})
        self.score -= deduction

    def add_strength(self, message: str):
        """Add a strength"""
        self.strengths.append(message)


class UnifiedReturnFormatCheck(QualityCheck):
    """
    Check 1: Unified Return Format (2.0 points)
    All modules MUST return: {"ok": bool, "output": {}, "error": None/Dict, "meta": {}}
    """

    def __init__(self):
        super().__init__(weight=2.0, name="Unified Return Format")

    def check(self, content: str, file_path: str) -> float:
        self.score = self.weight

        # Find all return statements with dict (handle multi-line and nested dicts)
        # This pattern handles one level of nested braces
        returns = re.findall(r'return\s+\{(?:[^{}]|\{[^{}]*\})*\}', content, re.DOTALL)

        if not returns:
            return self.score

        # Check for required keys
        has_ok_key = False
        has_output_key = False
        has_error_key = False
        has_meta_key = False

        for ret in returns:
            if '"ok":' in ret or "'ok':" in ret:
                has_ok_key = True
            if '"output":' in ret or "'output':" in ret:
                has_output_key = True
            if '"error":' in ret or "'error':" in ret:
                has_error_key = True
            if '"meta":' in ret or "'meta':" in ret:
                has_meta_key = True

        # Check for wrong format (old style)
        has_status_key = any('"status":' in ret or "'status':" in ret for ret in returns)

        if has_status_key:
            self.add_issue("Uses 'status' instead of 'ok' (wrong format)", 1.5)

        if not has_ok_key:
            self.add_issue("Missing 'ok' key in return", 0.4)
        else:
            self.add_strength("Has 'ok' key")

        if not has_output_key:
            self.add_issue("Missing 'output' key in return", 0.4)
        else:
            self.add_strength("Has 'output' key")

        if not has_error_key:
            self.add_issue("Missing 'error' key in return", 0.4)
        else:
            self.add_strength("Has 'error' key")

        if not has_meta_key:
            self.add_issue("Missing 'meta' key in return", 0.3)
        else:
            self.add_strength("Has 'meta' key")

        # Check consistency across all returns
        if len(returns) > 1:
            formats = []
            for ret in returns:
                format_keys = []
                if '"ok":' in ret or "'ok':" in ret:
                    format_keys.append("ok")
                if '"status":' in ret or "'status':" in ret:
                    format_keys.append("status")
                formats.append(tuple(sorted(format_keys)))

            if len(set(formats)) > 1:
                self.add_issue("Inconsistent return format across returns", 0.5)

        return max(0.0, self.score)


class NoDuplicateImportsCheck(QualityCheck):
    """
    Check 2: No Duplicate Imports (1.0 point)
    All imports MUST be at file top, NEVER inside functions
    """

    def __init__(self):
        super().__init__(weight=1.0, name="No Duplicate Imports")

    def check(self, content: str, file_path: str) -> float:
        self.score = self.weight

        # Find imports inside functions (4+ spaces indent)
        function_imports = re.findall(r'^\s{4,}(?:from|import)\s+[\w.]+', content, re.MULTILINE)

        if function_imports:
            self.add_issue(f"Found {len(function_imports)} import(s) inside function", 1.0)
        else:
            self.add_strength("All imports at file top")

        return max(0.0, self.score)


class ProperVariableReferencesCheck(QualityCheck):
    """
    Check 3: Proper Variable References (1.0 point)
    All class properties MUST use self. prefix
    """

    def __init__(self):
        super().__init__(weight=1.0, name="Proper Variable References")

    def check(self, content: str, file_path: str) -> float:
        self.score = self.weight

        # Extract params assigned in validate_params
        params_pattern = r'self\.(\w+)\s*='
        params = re.findall(params_pattern, content)

        if not params:
            return self.score

        # Look for usage without self. in execute method
        execute_match = re.search(r'async def execute\(self\)[^:]*:(.*?)(?=\n    def |\n\nclass |\Z)', content, re.DOTALL)

        if not execute_match:
            return self.score

        execute_body = execute_match.group(1)

        issues_count = 0
        for param in params:
            # Look for bare usage (not self.param)
            # Match: param.method() or param[  but NOT self.param
            pattern = rf'(?<!self\.)\b{param}\b'
            matches = re.findall(pattern, execute_body)

            # Filter out false positives (like in strings or comments)
            real_matches = []
            for match_str in matches:
                # Check if it's in a context where it should have self.
                context_pattern = rf'(?<!self\.)\b{param}\.(startswith|get|read|write|close|append)'
                if re.search(context_pattern, execute_body):
                    real_matches.append(match_str)

            if real_matches:
                issues_count += len(real_matches)

        if issues_count > 0:
            deduction = min(1.0, issues_count * 0.2)
            self.add_issue(f"Found {issues_count} variable(s) without self. prefix", deduction)
        else:
            self.add_strength("All variables use self. prefix")

        return max(0.0, self.score)


class NoNestedFunctionsCheck(QualityCheck):
    """
    Check 4: No Nested Functions (0.5 points)
    NEVER define functions inside execute() or validate_params()
    """

    def __init__(self):
        super().__init__(weight=0.5, name="No Nested Functions")

    def check(self, content: str, file_path: str) -> float:
        self.score = self.weight

        # Find nested function definitions (8+ spaces indent)
        nested_def_pattern = r'^\s{8,}(?:async\s+)?def\s+\w+'
        nested_defs = re.findall(nested_def_pattern, content, re.MULTILINE)

        if nested_defs:
            self.add_issue(f"Found {len(nested_defs)} nested function(s)", 0.5)
        else:
            self.add_strength("No nested functions")

        return max(0.0, self.score)


class CleanSeparationCheck(QualityCheck):
    """
    Check 5: Clean Separation (1.0 point)
    validate_params() should ONLY validate, NO business logic
    """

    def __init__(self):
        super().__init__(weight=1.0, name="Clean Separation")

    def check(self, content: str, file_path: str) -> float:
        self.score = self.weight

        # Extract validate_params method
        validate_match = re.search(
            r'def validate_params\(self\)[^:]*:(.*?)(?=\n    def |\n    async def |\Z)',
            content,
            re.DOTALL
        )

        if not validate_match:
            return self.score

        validate_body = validate_match.group(1)

        # Check for business logic indicators
        has_await = 'await ' in validate_body
        has_http = 'httpx.' in validate_body or 'aiohttp.' in validate_body
        has_file_ops = '.read_text(' in validate_body or '.write_' in validate_body

        if has_await:
            self.add_issue("validate_params contains async operations", 0.5)

        if has_http:
            self.add_issue("validate_params contains HTTP calls", 0.5)

        if has_file_ops:
            self.add_issue("validate_params contains file operations", 0.5)

        if not (has_await or has_http or has_file_ops):
            self.add_strength("validate_params only validates")

        return max(0.0, self.score)


class AsyncIOCheck(QualityCheck):
    """
    Check 6: Async I/O (1.0 point)
    Network operations MUST use async libraries (httpx, aiohttp)
    """

    def __init__(self):
        super().__init__(weight=1.0, name="Async I/O")

    def check(self, content: str, file_path: str) -> float:
        self.score = self.weight

        # Check for blocking I/O libraries
        uses_requests = 'import requests' in content or 'from requests' in content
        uses_urllib = 'import urllib' in content or 'from urllib' in content

        # Check for async libraries
        uses_httpx = 'import httpx' in content or 'from httpx' in content
        uses_aiohttp = 'import aiohttp' in content or 'from aiohttp' in content

        if uses_requests:
            self.add_issue("Uses blocking 'requests' library", 1.0)
        elif uses_urllib and 'urllib.parse' not in content:
            self.add_issue("Uses blocking 'urllib' library", 1.0)
        elif uses_httpx or uses_aiohttp:
            self.add_strength("Uses async I/O library")

        return max(0.0, self.score)


class ComprehensiveErrorHandlingCheck(QualityCheck):
    """
    Check 7: Comprehensive Error Handling (1.0 point)
    Must catch at least 3 specific exception types
    """

    def __init__(self):
        super().__init__(weight=1.0, name="Comprehensive Error Handling")

    def check(self, content: str, file_path: str) -> float:
        self.score = self.weight

        # Check if has try/except
        if 'try:' not in content or 'except' not in content:
            self.add_issue("No error handling found", 1.0)
            return max(0.0, self.score)

        # Count specific exception types
        specific_exceptions = re.findall(r'except\s+(\w+(?:\.\w+)?)\s+as', content)

        # Filter out generic Exception
        specific_exceptions = [e for e in specific_exceptions if e != 'Exception']

        num_specific = len(set(specific_exceptions))

        if num_specific == 0:
            self.add_issue("Only generic Exception handler", 0.5)
        elif num_specific == 1:
            self.add_strength("Has 1 specific exception type")
            self.add_issue("Need at least 3 specific exception types", 0.6)
        elif num_specific == 2:
            self.add_strength("Has 2 specific exception types")
            self.add_issue("Need at least 3 specific exception types", 0.3)
        else:
            self.add_strength(f"Has {num_specific} specific exception types")

        # Check error return format
        error_returns = re.findall(r'return\s+\{[^}]*"ok":\s*False[^}]*\}', content, re.DOTALL)

        if error_returns:
            # Check if error returns have proper format
            has_error_field = any('"error":' in ret or "'error':" in ret for ret in error_returns)
            if has_error_field:
                self.add_strength("Error returns use unified format")
            else:
                self.add_issue("Error returns missing 'error' field", 0.3)

        return max(0.0, self.score)


class SecurityValidationsCheck(QualityCheck):
    """
    Check 8: Security Validations (1.5 points)
    URL validation (0.5), Content-Type (0.5), File size (0.5)
    """

    def __init__(self):
        super().__init__(weight=1.5, name="Security Validations")

    def check(self, content: str, file_path: str) -> float:
        self.score = self.weight

        # Check URL validation
        has_url_param = 'self.url' in content
        if has_url_param:
            has_url_validation = 'startswith("http' in content or 'startswith(\'http' in content
            if not has_url_validation:
                self.add_issue("Missing URL format validation", 0.5)
            else:
                self.add_strength("URL format validation present")

        # Check Content-Type validation (for download/fetch modules)
        is_download = 'download' in file_path.lower() or 'fetch' in file_path.lower()
        if is_download or 'response.content' in content:
            has_content_type = 'content-type' in content.lower() or 'content_type' in content
            if not has_content_type:
                self.add_issue("Missing Content-Type validation", 0.5)
            else:
                self.add_strength("Content-Type validation present")

        # Check file size limit
        if is_download or 'response.content' in content:
            has_size_limit = 'content-length' in content.lower() or 'max_size' in content.lower()
            if not has_size_limit:
                self.add_issue("Missing file size limit check", 0.5)
            else:
                self.add_strength("File size limit present")

        return max(0.0, self.score)


class NoPlaceholderCodeCheck(QualityCheck):
    """
    Check 9: No Placeholder Code (0.5 points)
    NO TODO, placeholder, pass, NotImplementedError
    """

    def __init__(self):
        super().__init__(weight=0.5, name="No Placeholder Code")

    def check(self, content: str, file_path: str) -> float:
        self.score = self.weight

        # Check for placeholder patterns
        placeholders = [
            ('TODO', 'TODO comment found'),
            ('placeholder', 'Placeholder code found'),
            ('implement here', 'Implementation placeholder found'),
            ('NotImplementedError', 'NotImplementedError found'),
        ]

        found_placeholders = []
        for pattern, message in placeholders:
            if pattern in content:
                found_placeholders.append(message)

        if found_placeholders:
            self.add_issue(f"Placeholder code: {', '.join(found_placeholders)}", 0.5)
        else:
            self.add_strength("No placeholder code")

        return max(0.0, self.score)


class CompleteDocumentationCheck(QualityCheck):
    """
    Check 10: Complete Documentation (0.5 points)
    Class docstring (0.3), Parameter docs (0.2)
    """

    def __init__(self):
        super().__init__(weight=0.5, name="Complete Documentation")

    def check(self, content: str, file_path: str) -> float:
        self.score = self.weight

        # Check for class docstring
        has_class_docstring = '"""' in content or "'''" in content

        if not has_class_docstring:
            self.add_issue("Missing class docstring", 0.3)
        else:
            # Check if docstring has parameter documentation
            docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if docstring_match:
                docstring = docstring_match.group(1)
                has_params = 'Parameters:' in docstring or 'Args:' in docstring or 'param' in docstring.lower()
                has_returns = 'Returns:' in docstring or 'return' in docstring.lower()

                if has_params:
                    self.add_strength("Has parameter documentation")
                else:
                    self.add_issue("Missing parameter documentation", 0.2)

                if has_returns:
                    self.add_strength("Has return documentation")
            else:
                self.add_strength("Has class docstring")

        return max(0.0, self.score)


class QualityCheckerV2:
    """
    Enterprise-grade quality checker with atomic, zero-coupling design
    Implements all 10 checks from MODULE_QUALITY_STANDARDS.md
    """

    def __init__(self):
        self.checks: List[QualityCheck] = [
            UnifiedReturnFormatCheck(),          # 2.0 points
            NoDuplicateImportsCheck(),            # 1.0 point
            ProperVariableReferencesCheck(),      # 1.0 point
            NoNestedFunctionsCheck(),             # 0.5 points
            CleanSeparationCheck(),               # 1.0 point
            AsyncIOCheck(),                       # 1.0 point
            ComprehensiveErrorHandlingCheck(),    # 1.0 point
            SecurityValidationsCheck(),           # 1.5 points
            NoPlaceholderCodeCheck(),             # 0.5 points
            CompleteDocumentationCheck(),         # 0.5 points
        ]

    def review_module(self, file_path: str) -> Dict:
        """
        Review a module file and return quality assessment

        Returns:
            {
                "score": float,  # 0-10
                "grade": str,    # A+, A, B, etc.
                "pass": bool,    # True if score >= 9.8
                "checks": List[Dict],  # Individual check results
                "issues": List[Dict],
                "strengths": List[str]
            }
        """
        # Read file
        content = Path(file_path).read_text()

        # Run all checks
        total_score = 0.0
        all_issues = []
        all_strengths = []
        check_results = []

        for check in self.checks:
            score = check.check(content, file_path)
            total_score += score

            check_results.append({
                "name": check.name,
                "weight": check.weight,
                "score": round(score, 2),
                "percentage": round((score / check.weight) * 100, 1) if check.weight > 0 else 100
            })

            all_issues.extend(check.issues)
            all_strengths.extend(check.strengths)

        # Calculate grade
        grade = self._calculate_grade(total_score)

        return {
            "score": round(total_score, 2),
            "grade": grade,
            "pass": total_score >= 9.8,
            "checks": check_results,
            "issues": all_issues,
            "strengths": all_strengths
        }

    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from score"""
        if score >= 9.8:
            return "A+"
        elif score >= 9.5:
            return "A"
        elif score >= 9.0:
            return "B+"
        elif score >= 8.0:
            return "B"
        elif score >= 7.0:
            return "C"
        else:
            return "F"


def review_module_file(file_path: str) -> Dict:
    """Convenience function to review a single module file"""
    checker = QualityCheckerV2()
    return checker.review_module(file_path)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "src/core/modules/atomic/image/download.py"

    result = review_module_file(file_path)

    print("=" * 80)
    print("Quality Assessment Report")
    print("=" * 80)
    print(f"Score: {result['score']}/10.0 ({result['grade']})")
    print(f"Pass: {'YES' if result['pass'] else 'NO'}")
    print()

    print("Individual Checks:")
    for check in result['checks']:
        status = "PASS" if check['percentage'] >= 80 else "FAIL"
        print(f"  [{status}] {check['name']}: {check['score']}/{check['weight']} ({check['percentage']}%)")
    print()

    if result['strengths']:
        print("Strengths:")
        for s in result['strengths']:
            print(f"  + {s}")
        print()

    if result['issues']:
        print("Issues:")
        for i in result['issues']:
            print(f"  - {i['message']} (-{i['deduction']})")
        print()
