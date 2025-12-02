"""
Unified Notification System - Atomic module for notifications

Purpose: Single source of truth for all notification logic
- Eliminates duplicate _notify() methods across 5+ files
- Supports multiple backends (console, callback, future: telegram, slack)
- Consistent notification formatting
"""

from typing import Optional, Callable, List
import sys


class Notifier:
    """
    Unified notification system

    Replaces scattered _notify() implementations across:
    - ai_error_solver.py
    - smart_executor.py
    - daily_practice.py
    - self_healing_practice.py
    - Bot scripts
    """

    def __init__(
        self,
        callback: Optional[Callable] = None,
        backends: List[str] = None
    ):
        """
        Initialize notifier

        Args:
            callback: Optional async callback function
            backends: List of backends ['console', 'callback']
        """
        self.callback = callback
        self.backends = backends or ['console']

    async def notify(self, message: str, level: str = 'info'):
        """
        Send notification to all configured backends

        Args:
            message: Notification message
            level: Notification level (info, warning, error, success)
        """
        # Format message with level
        formatted = self._format_message(message, level)

        # Send to all backends
        if 'console' in self.backends:
            await self._notify_console(formatted)

        if 'callback' in self.backends and self.callback:
            await self._notify_callback(formatted)

    def _format_message(self, message: str, level: str) -> str:
        """Format message based on level (already has emojis usually)"""
        # Most messages already have emojis, just return as-is
        return message

    async def _notify_console(self, message: str):
        """Print to console"""
        print(message, flush=True)

    async def _notify_callback(self, message: str):
        """Call async callback if provided"""
        if self.callback:
            try:
                await self.callback(message)
            except Exception as e:
                # Don't fail on notification errors
                print(f"⚠️ Notification callback error: {e}", file=sys.stderr)

    # Convenience methods for different levels
    async def info(self, message: str):
        """Send info notification"""
        await self.notify(message, level='info')

    async def warning(self, message: str):
        """Send warning notification"""
        await self.notify(message, level='warning')

    async def error(self, message: str):
        """Send error notification"""
        await self.notify(message, level='error')

    async def success(self, message: str):
        """Send success notification"""
        await self.notify(message, level='success')


# Singleton instance for global use
_notifier = None

def get_notifier(callback: Optional[Callable] = None) -> Notifier:
    """
    Get or create global notifier instance

    Args:
        callback: Optional callback to set

    Returns:
        Notifier instance
    """
    global _notifier
    if _notifier is None:
        _notifier = Notifier(callback=callback)
    elif callback:
        _notifier.callback = callback
    return _notifier


async def notify(message: str, callback: Optional[Callable] = None):
    """
    Convenience function for quick notifications

    Args:
        message: Message to send
        callback: Optional callback
    """
    notifier = get_notifier(callback)
    await notifier.notify(message)
