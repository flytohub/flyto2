"""
Auto-Heal Decorator - Add AI error handling to any function

Usage:
    @auto_heal(max_retries=3)
    async def my_function():
        # Your code that might fail
        ...

If error occurs:
1. Catch error
2. Ask AI for solution
3. Execute solution
4. Retry function
5. If success → store solution to vector DB
"""

import functools
import traceback
from typing import Any, Callable, Optional
from .ai_error_solver import AIErrorSolver


def auto_heal(max_retries: int = 3, notify_callback: Optional[Callable] = None):
    """
    Decorator to add AI-powered error handling to any function

    Args:
        max_retries: Maximum retry attempts
        notify_callback: Optional callback for progress notifications

    Example:
        @auto_heal(max_retries=3)
        async def crawl_website(url):
            browser = await playwright.chromium.launch()
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            solver = AIErrorSolver()

            for attempt in range(1, max_retries + 1):
                try:
                    # Try to execute the function
                    result = await func(*args, **kwargs)
                    return result

                except Exception as e:
                    # Build error context
                    context = {
                        "function": func.__name__,
                        "module": func.__module__,
                        "attempt": attempt,
                        "max_retries": max_retries,
                        "args": str(args)[:500],
                        "kwargs": str(kwargs)[:500],
                        "traceback": traceback.format_exc()[:2000]
                    }

                    if attempt < max_retries:
                        # Ask AI to solve the error
                        solution_result = await solver.solve_error(
                            e,
                            context,
                            notify_callback
                        )

                        if solution_result["success"]:
                            # Solution applied, retry
                            if notify_callback:
                                await notify_callback(f"🔄 Retrying {func.__name__} (attempt {attempt + 1}/{max_retries})...")
                            continue
                        else:
                            # Solution failed, still retry
                            if notify_callback:
                                await notify_callback(f"⚠️ Solution failed, retrying anyway...")
                            continue
                    else:
                        # Max retries reached
                        if notify_callback:
                            await notify_callback(f"❌ Max retries reached for {func.__name__}")
                        raise

        return wrapper

    return decorator
