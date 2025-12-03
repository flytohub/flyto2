"""
Privacy & Redaction Module
Ensures sensitive information is not stored in long-term knowledge base
"""
import re
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class PrivacyRedactor:
    """
    Privacy Redactor

    Purpose: Remove sensitive information before promoting JobMemory content to Knowledge
    """

    # Sensitive pattern definitions
    PATTERNS = {
        # Email
        'email': (
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            '[EMAIL]'
        ),

        # URL with specific IDs (Google Sheets, Docs, etc.)
        'google_sheet_url': (
            r'https?://docs\.google\.com/spreadsheets/d/[A-Za-z0-9_-]+[^\s]*',
            '[GOOGLE_SHEET_URL]'
        ),
        'google_doc_url': (
            r'https?://docs\.google\.com/document/d/[A-Za-z0-9_-]+[^\s]*',
            '[GOOGLE_DOC_URL]'
        ),
        'google_form_url': (
            r'https?://docs\.google\.com/forms/d/[A-Za-z0-9_-]+[^\s]*',
            '[GOOGLE_FORM_URL]'
        ),

        # Generic URL with long IDs
        'url_with_id': (
            r'https?://[^\s]+/[A-Za-z0-9_-]{20,}[^\s]*',
            '[URL_WITH_ID]'
        ),

        # Phone numbers (10+ digits)
        'phone': (
            r'\b\d{10,}\b',
            '[PHONE]'
        ),

        # API keys/tokens (long strings)
        'api_key': (
            r'\b[A-Za-z0-9_-]{32,}\b',
            '[API_KEY]'
        ),

        # IP addresses
        'ip_address': (
            r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            '[IP_ADDRESS]'
        ),

        # Credit card (simplified)
        'credit_card': (
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            '[CREDIT_CARD]'
        ),

        # JWT tokens
        'jwt_token': (
            r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',
            '[JWT_TOKEN]'
        ),

        # Taiwan ID number
        'taiwan_id': (
            r'\b[A-Z][12]\d{8}\b',
            '[ID_NUMBER]'
        ),
    }

    # Sensitive keywords (require manual confirmation)
    SENSITIVE_KEYWORDS = [
        'password', 'passwd', 'pwd',
        'secret', 'private key', 'api key',
        'account', 'username',
        'cookie', 'session',
        'credit card',
        'id card', 'identification',
    ]

    def __init__(self):
        """Initialize Redactor"""
        self.redaction_count = {}  # Statistics for each redaction type

    def redact(self, text: str, aggressive: bool = False) -> Tuple[str, Dict[str, int]]:
        """
        Redact sensitive information

        Args:
            text: Original text
            aggressive: Whether to use aggressive mode (more filtering rules)

        Returns:
            (redacted_text, statistics)
        """
        redacted_text = text
        stats = {}

        # Apply all filtering patterns
        for pattern_name, (pattern, replacement) in self.PATTERNS.items():
            matches = re.findall(pattern, redacted_text, re.IGNORECASE)
            count = len(matches)

            if count > 0:
                redacted_text = re.sub(pattern, replacement, redacted_text, flags=re.IGNORECASE)
                stats[pattern_name] = count
                logger.debug(f"Redacted {count} instances of {pattern_name}")

        # Aggressive mode: filter content around sensitive keywords
        if aggressive:
            redacted_text, keyword_stats = self._redact_around_keywords(redacted_text)
            stats.update(keyword_stats)

        return redacted_text, stats

    def _redact_around_keywords(self, text: str) -> Tuple[str, Dict[str, int]]:
        """
        Redact content around sensitive keywords

        Example: "password is abc123" -> "password: [REDACTED]"
        """
        redacted_text = text
        stats = {}

        for keyword in self.SENSITIVE_KEYWORDS:
            # Find content after keyword
            pattern = rf'{keyword}\s*[:：=]\s*([^\s\n]+)'
            matches = re.findall(pattern, redacted_text, re.IGNORECASE)

            if matches:
                redacted_text = re.sub(
                    pattern,
                    f'{keyword}: [REDACTED]',
                    redacted_text,
                    flags=re.IGNORECASE
                )
                stats[f'keyword_{keyword}'] = len(matches)

        return redacted_text, stats

    def check_sensitive(self, text: str) -> List[str]:
        """
        Check if text contains sensitive information

        Args:
            text: Text to check

        Returns:
            List of sensitive pattern names (if any)
        """
        sensitive_patterns = []

        for pattern_name, (pattern, _) in self.PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                sensitive_patterns.append(pattern_name)

        # Check sensitive keywords
        for keyword in self.SENSITIVE_KEYWORDS:
            if keyword.lower() in text.lower():
                sensitive_patterns.append(f'keyword_{keyword}')

        return sensitive_patterns

    def is_safe_for_knowledge(self, text: str) -> bool:
        """
        Determine if text is safe to store in knowledge base

        Args:
            text: Text to check

        Returns:
            True if safe, False if contains sensitive info
        """
        sensitive = self.check_sensitive(text)
        return len(sensitive) == 0


# Global instance
_redactor = None


def get_redactor() -> PrivacyRedactor:
    """Get global Redactor instance"""
    global _redactor
    if _redactor is None:
        _redactor = PrivacyRedactor()
    return _redactor


def redact_for_knowledge(text: str, aggressive: bool = False) -> str:
    """
    Convenience function: Redact text for knowledge base

    Args:
        text: Original text
        aggressive: Aggressive mode

    Returns:
        Redacted text
    """
    redactor = get_redactor()
    redacted_text, stats = redactor.redact(text, aggressive=aggressive)

    if stats:
        logger.info(f"Redaction applied: {stats}")

    return redacted_text


def validate_before_knowledge_store(content: str, metadata: Dict) -> Tuple[bool, List[str]]:
    """
    Validate content before storing in knowledge base

    Args:
        content: Content text
        metadata: Metadata dict

    Returns:
        (is_valid, warnings)
    """
    redactor = get_redactor()
    warnings = []

    # Check content
    sensitive_in_content = redactor.check_sensitive(content)
    if sensitive_in_content:
        warnings.append(f"Content contains sensitive info: {', '.join(sensitive_in_content)}")

    # Check metadata for sensitive information
    for key, value in metadata.items():
        if isinstance(value, str):
            sensitive_in_meta = redactor.check_sensitive(value)
            if sensitive_in_meta:
                warnings.append(f"Metadata[{key}] contains sensitive info: {', '.join(sensitive_in_meta)}")

    is_valid = len(warnings) == 0
    return is_valid, warnings


# ============================================================
# Usage Example
# ============================================================

if __name__ == "__main__":
    # Test redaction
    test_cases = [
        "My email is user@example.com",
        "Password is super_secret_123",
        "This is my Google Sheet: https://docs.google.com/spreadsheets/d/1AbCdEfGhIjKlMnOpQrStUvWxYz/edit",
        "API Key: sk_live_AbCdEfGhIjKlMnOpQrStUvWxYz123456",
        "Phone: 0912345678",
        "ID: A123456789",
    ]

    redactor = get_redactor()

    print("=" * 80)
    print("Redaction Test")
    print("=" * 80)

    for i, text in enumerate(test_cases, 1):
        print(f"\n[Test {i}]")
        print(f"Original: {text}")

        redacted, stats = redactor.redact(text)
        print(f"Redacted: {redacted}")
        print(f"Stats: {stats}")

        is_safe = redactor.is_safe_for_knowledge(redacted)
        print(f"Safe: {'✅' if is_safe else '❌'}")
