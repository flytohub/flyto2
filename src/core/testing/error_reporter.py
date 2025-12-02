"""
Error Reporter - Automatic error reporting to Telegram
Sends test failures and system errors to Telegram automatically
"""
import os
import json
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path


class TelegramErrorReporter:
    """
    Automatically report errors to Telegram
    """

    def __init__(self):
        """Initialize error reporter"""
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_ids = os.getenv('TELEGRAM_ALLOWED_USERS', '').split(',')
        self.enabled = bool(self.bot_token and self.chat_ids[0])

        if not self.enabled:
            print("Warning: Telegram error reporting disabled (no credentials)")

    def report_test_failure(
        self,
        test_name: str,
        error_message: str,
        traceback: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Report test failure to Telegram

        Args:
            test_name: Name of failed test
            error_message: Error message
            traceback: Optional traceback string
            context: Optional additional context

        Returns:
            True if sent successfully
        """
        if not self.enabled:
            return False

        # Build message
        message = self._format_test_failure(
            test_name, error_message, traceback, context
        )

        return self._send_to_telegram(message)

    def report_module_error(
        self,
        module_id: str,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Report module execution error to Telegram

        Args:
            module_id: Module identifier
            error_type: Error type/class name
            error_message: Error message
            context: Optional context

        Returns:
            True if sent successfully
        """
        if not self.enabled:
            return False

        message = self._format_module_error(
            module_id, error_type, error_message, context
        )

        return self._send_to_telegram(message)

    def report_system_error(
        self,
        component: str,
        error: Exception,
        severity: str = "ERROR"
    ) -> bool:
        """
        Report system-level error to Telegram

        Args:
            component: Component name
            error: Exception instance
            severity: ERROR, WARNING, CRITICAL

        Returns:
            True if sent successfully
        """
        if not self.enabled:
            return False

        emoji = {
            "CRITICAL": "🚨",
            "ERROR": "❌",
            "WARNING": "⚠️"
        }.get(severity, "❌")

        message = f"""
{emoji} *System {severity}*

*Component:* {component}
*Error:* {type(error).__name__}
*Message:* {str(error)}

*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()

        return self._send_to_telegram(message)

    def _format_test_failure(
        self,
        test_name: str,
        error_message: str,
        traceback: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Format test failure message"""
        message = f"""
❌ *Test Failed*

*Test:* {test_name}
*Error:* {error_message}
        """.strip()

        if traceback:
            # Truncate long tracebacks
            tb_lines = traceback.split('\n')
            if len(tb_lines) > 10:
                tb_short = '\n'.join(tb_lines[-10:])
                message += f"\n\n*Traceback (last 10 lines):*\n```\n{tb_short}\n```"
            else:
                message += f"\n\n*Traceback:*\n```\n{traceback}\n```"

        if context:
            message += f"\n\n*Context:* {json.dumps(context, indent=2)[:200]}"

        message += f"\n\n*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        return message

    def _format_module_error(
        self,
        module_id: str,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Format module error message"""
        message = f"""
⚠️ *Module Error*

*Module:* {module_id}
*Type:* {error_type}
*Message:* {error_message}
        """.strip()

        if context:
            ctx_str = json.dumps(context, indent=2)
            if len(ctx_str) > 200:
                ctx_str = ctx_str[:200] + "..."
            message += f"\n\n*Context:*\n```json\n{ctx_str}\n```"

        message += f"\n\n*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        return message

    def _send_to_telegram(self, message: str) -> bool:
        """
        Send message to Telegram

        Args:
            message: Message text (Markdown format)

        Returns:
            True if sent successfully
        """
        if not self.enabled:
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

        # Send to all allowed users
        success = True
        for chat_id in self.chat_ids:
            if not chat_id.strip():
                continue

            try:
                response = requests.post(
                    url,
                    json={
                        "chat_id": chat_id.strip(),
                        "text": message,
                        "parse_mode": "Markdown"
                    },
                    timeout=10
                )

                if response.status_code != 200:
                    print(f"Failed to send error report to {chat_id}: {response.status_code}")
                    success = False

            except Exception as e:
                print(f"Error sending to Telegram: {e}")
                success = False

        return success


# Global instance
_reporter = None


def get_error_reporter() -> TelegramErrorReporter:
    """Get global error reporter instance"""
    global _reporter
    if _reporter is None:
        _reporter = TelegramErrorReporter()
    return _reporter


def report_test_failure(test_name: str, error_message: str, **kwargs) -> bool:
    """Convenience function to report test failure"""
    return get_error_reporter().report_test_failure(test_name, error_message, **kwargs)


def report_module_error(module_id: str, error_type: str, error_message: str, **kwargs) -> bool:
    """Convenience function to report module error"""
    return get_error_reporter().report_module_error(module_id, error_type, error_message, **kwargs)


def report_system_error(component: str, error: Exception, severity: str = "ERROR") -> bool:
    """Convenience function to report system error"""
    return get_error_reporter().report_system_error(component, error, severity)
