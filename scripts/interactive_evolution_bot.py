#!/usr/bin/env python3
"""
Interactive Self-Evolving AI Agent for Flyto2

Combines:
- Continuous improvement (autonomous evolution)
- Interactive dialogue (you guide via Telegram)
- Three-tier escalation (Ollama → Human → OpenAI)

Features:
- Tests all atomic/composed modules continuously
- Reads documentation to discover gaps
- Proposes new modules via Telegram
- Asks for your guidance when stuck
- Escalates to OpenAI when both agree
- Zero coupling enforcement
- Full audit trail
"""
import os
import sys
import json
import asyncio
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

load_dotenv()

# Add project root to sys.path BEFORE any imports from src
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_ALLOWED_USERS = os.getenv('TELEGRAM_ALLOWED_USERS', '').split(',')
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


class EvolutionState:
    """Tracks AI evolution state and conversation history"""

    def __init__(self):
        self.sessions: Dict[int, Dict] = {}
        self.autonomous_mode = False  # Auto-run continuous improvement
        self.last_test_run = None
        self.module_quality_data = {}
        self.pending_proposals = []  # AI proposals waiting for your review
        self.api_tokens: Dict[str, str] = {}  # User-provided API tokens for testing
        self.pending_test_token_collection = False  # Flag for token collection flow
        self.pending_practice_url_input = False  # Flag for practice URL input

        # Configurable escalation thresholds
        self.config = {
            'auto_escalate_threshold': 0.3,  # Auto jump to OpenAI if confidence < 0.3
            'human_guidance_threshold': 0.5,  # Ask user if confidence < 0.5
            'auto_approve_threshold': 0.8,   # Auto approve if confidence >= 0.8
        }

        # Leaderboard ranking tracking
        self.previous_rankings: Dict[str, int] = {}  # task_name -> rank

    def get_session(self, user_id: int) -> Dict:
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                "conversation": [],
                "context": "general",  # general, module_design, testing, documentation
                "pending_question": None,
                "ollama_confidence": 0.0,
                "stats": {
                    "ollama_queries": 0,
                    "human_guided": 0,
                    "openai_queries": 0,
                    "modules_proposed": 0,
                    "modules_implemented": 0
                }
            }
        return self.sessions[user_id]


state = EvolutionState()


def is_authorized(update: Update) -> bool:
    user_id = str(update.effective_user.id)
    return user_id in TELEGRAM_ALLOWED_USERS


# ============================================
# AI Layer - Ollama
# ============================================

async def ask_ollama(prompt: str, system_prompt: str = None) -> Tuple[str, float]:
    """
    Ask local Ollama model
    Returns: (response, confidence_score)
    """
    try:
        import requests

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": "llama3.2",
                "messages": messages,
                "stream": False
            },
            timeout=120
        )

        if response.status_code != 200:
            return f"Ollama error: {response.status_code}", 0.0

        data = response.json()
        content = data.get('message', {}).get('content', '')

        # Estimate confidence based on response characteristics
        confidence = estimate_confidence(content)

        return content, confidence

    except Exception as e:
        return f"Ollama unavailable: {str(e)}", 0.0


def estimate_confidence(response: str) -> float:
    """Estimate Ollama's confidence in its answer"""
    # Simple heuristics
    uncertainty_words = ["maybe", "perhaps", "might", "unsure", "not sure", "unclear"]
    certainty_words = ["definitely", "certainly", "clearly", "obviously", "sure"]

    response_lower = response.lower()

    uncertainty_count = sum(1 for word in uncertainty_words if word in response_lower)
    certainty_count = sum(1 for word in certainty_words if word in response_lower)

    # Base confidence
    confidence = 0.7

    # Adjust based on signals
    confidence -= uncertainty_count * 0.15
    confidence += certainty_count * 0.1

    # Length matters (too short might be uncertain)
    if len(response) < 50:
        confidence -= 0.2

    return max(0.0, min(1.0, confidence))


# ============================================
# AI Layer - OpenAI (escalation tier)
# ============================================

async def ask_openai(prompt: str, system_prompt: str = None) -> str:
    """Ask OpenAI (only when escalated)"""
    if not OPENAI_API_KEY:
        return "OpenAI API key not configured"

    try:
        import openai
        openai.api_key = OPENAI_API_KEY

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"OpenAI error: {str(e)}"


# ============================================
# Module Testing
# ============================================

async def run_module_quality_tests(provided_tokens: Optional[Dict[str, str]] = None) -> Dict:
    """Run REAL quality tests by executing test workflows

    Args:
        provided_tokens: Optional dict of API tokens for testing integrations
                        e.g., {'OPENAI_API_KEY': 'sk-...', 'SLACK_WEBHOOK_URL': '...'}
    """
    try:
        # Find all test workflows
        test_dir = PROJECT_ROOT / "workflows" / "_test"

        if not test_dir.exists():
            return {"error": "No test directory found"}

        test_files = list(test_dir.glob("test_*.yaml"))

        if not test_files:
            return {"error": "No test files found"}

        # Get total registered modules for coverage calculation
        from src.core.modules.registry import ModuleRegistry
        registry = ModuleRegistry()
        all_modules = registry.get_all_metadata()
        total_registered = len(all_modules)

        # Prepare environment with provided tokens
        test_env = os.environ.copy()
        if provided_tokens:
            test_env.update(provided_tokens)

        # Ensure PYTHONPATH includes project root
        pythonpath = str(PROJECT_ROOT)
        if 'PYTHONPATH' in test_env:
            test_env['PYTHONPATH'] = f"{pythonpath}:{test_env['PYTHONPATH']}"
        else:
            test_env['PYTHONPATH'] = pythonpath

        # Run each test workflow
        results = {}
        passed = 0
        failed = 0
        tested_modules = set()

        for test_file in test_files:
            module_name = test_file.stem.replace("test_", "")

            try:
                # Execute the test workflow with environment variables
                # Note: Use absolute path to avoid module import issues
                cli_script = PROJECT_ROOT / "src" / "cli" / "main.py"

                # Debug: Print command for first test
                if module_name == test_files[0].stem.replace("test_", ""):
                    print(f"[DEBUG] CLI script: {cli_script}")
                    print(f"[DEBUG] Test file: {test_file}")
                    print(f"[DEBUG] CWD: {PROJECT_ROOT}")
                    print(f"[DEBUG] Python: {sys.executable}")
                    print(f"[DEBUG] PYTHONPATH: {test_env.get('PYTHONPATH', 'Not set')}")

                # Execute CLI script directly with PYTHONPATH set
                # PYTHONPATH is the most reliable way across platforms
                result = subprocess.run(
                    [sys.executable, str(cli_script), str(test_file)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(PROJECT_ROOT),
                    env=test_env  # test_env already has PYTHONPATH set
                )

                # Extract which modules were tested from the workflow
                # Parse the YAML to see what modules were used
                import yaml
                with open(test_file, 'r') as f:
                    workflow = yaml.safe_load(f)
                    for step in workflow.get('steps', []):
                        # Check both 'module' and 'module_id' fields
                        module_id = step.get('module_id') or step.get('module')
                        if module_id:
                            tested_modules.add(module_id)

                if result.returncode == 0:
                    results[module_name] = {
                        "status": "pass",
                        "pass_rate": 1.0
                    }
                    passed += 1
                else:
                    # Keep full stderr for debugging
                    full_stderr = result.stderr if result.stderr else "Unknown error"

                    # Try to extract just the error message for display
                    display_error = full_stderr
                    if "Error occurred:" in full_stderr:
                        error_lines = full_stderr.split('\n')
                        for line in error_lines:
                            if "Error occurred:" in line:
                                display_error = line.split("Error occurred:", 1)[1].strip()
                                break

                    results[module_name] = {
                        "status": "fail",
                        "pass_rate": 0.0,
                        "error": display_error[:300],
                        "full_stderr": full_stderr  # Keep full output for debug
                    }
                    failed += 1

            except subprocess.TimeoutExpired:
                results[module_name] = {
                    "status": "fail",
                    "pass_rate": 0.0,
                    "error": "Test timeout (>30s)"
                }
                failed += 1
            except Exception as e:
                results[module_name] = {
                    "status": "fail",
                    "pass_rate": 0.0,
                    "error": f"Exception: {str(e)[:200]}"
                }
                failed += 1

        total_tests = passed + failed
        modules_tested = len(tested_modules)
        coverage_rate = modules_tested / total_registered if total_registered > 0 else 0

        # Add debug info if any tests failed
        debug_info = {}
        if failed > 0:
            cli_script = PROJECT_ROOT / "src" / "cli" / "main.py"
            first_result = results[list(results.keys())[0]] if results else {}
            debug_info = {
                "cli_script": str(cli_script),
                "cli_exists": cli_script.exists(),
                "project_root": str(PROJECT_ROOT),
                "python_executable": sys.executable,
                "pythonpath": test_env.get('PYTHONPATH', 'Not set'),
                "first_error": first_result.get("error", "N/A"),
                "os_pathsep": os.pathsep,
                "sample_full_stderr": first_result.get("full_stderr", first_result.get("error", "N/A"))[:800]
            }

        return {
            "total_tests": total_tests,
            "total_registered_modules": total_registered,
            "modules_tested": modules_tested,
            "modules_untested": total_registered - modules_tested,
            "coverage_rate": coverage_rate,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / total_tests if total_tests > 0 else 0,
            "tested_module_ids": sorted(list(tested_modules)),
            "modules": results,
            "source": "real_execution",
            "debug_info": debug_info if debug_info else None
        }

    except Exception as e:
        import traceback
        full_traceback = traceback.format_exc()

        # Get more context
        error_context = {
            "error": f"Test execution failed: {str(e)}",
            "error_type": type(e).__name__,
            "traceback": full_traceback,
            "project_root": str(PROJECT_ROOT),
            "python": sys.executable,
            "test_dir_exists": (PROJECT_ROOT / "workflows" / "_test").exists(),
            "cli_exists": (PROJECT_ROOT / "src" / "cli" / "main.py").exists(),
            "src_exists": (PROJECT_ROOT / "src").exists(),
            "pythonpath_set": str(PROJECT_ROOT) if 'PYTHONPATH' in os.environ else "Not in env"
        }

        return error_context


async def analyze_test_results(results: Dict) -> Dict:
    """Use Ollama to analyze test results and suggest improvements"""

    # Simple analysis without AI if results are straightforward
    total_tests = results.get("total_tests", 0)
    modules_tested = results.get("modules_tested", 0)
    modules_untested = results.get("modules_untested", 0)
    coverage_rate = results.get("coverage_rate", 0)
    passed = results.get("passed", 0)
    failed = results.get("failed", 0)
    pass_rate = results.get("pass_rate", 0)

    if total_tests == 0:
        return {
            "summary": "No tests executed",
            "issues": []
        }

    # Create detailed summary
    summary = f"**Coverage:** {coverage_rate:.1%} ({modules_tested}/{modules_tested + modules_untested} modules)\n"
    summary += f"**Test Success:** {pass_rate:.1%} ({passed}/{total_tests} tests passed)"

    if modules_untested > 0:
        summary += f"\n\n⚠️ **{modules_untested} modules have no tests** (need API keys or mocks)"

    # Identify failing modules
    issues = []
    modules = results.get("modules", {})
    for module_id, data in modules.items():
        if isinstance(data, dict) and data.get("status") == "fail":
            error_msg = data.get("error", "Unknown error")
            issues.append({
                "module_id": module_id,
                "current_pass_rate": data.get("pass_rate", 0.0),
                "issue": error_msg[:100],
                "suggestion": "Check module implementation and tests",
                "priority": "high"
            })

    # If Ollama available, try to get AI insights
    if (failed > 0 or coverage_rate < 0.5) and OLLAMA_URL:
        try:
            system_prompt = """Briefly analyze these test results and suggest improvements.
Keep response under 200 words, plain text format."""

            prompt = f"Test coverage: {coverage_rate:.1%} ({modules_tested}/{modules_tested + modules_untested})\n"
            prompt += f"Test results: {passed}/{total_tests} passed, {failed} failed.\n"
            if issues:
                prompt += f"Failing tests: {[m['module_id'] for m in issues[:3]]}\n"
            prompt += "\nSuggest improvements:"

            response, confidence = await ask_ollama(prompt, system_prompt)

            if response and "error" not in response.lower():
                summary += f"\n\n💡 AI Insight: {response[:300]}"
        except:
            pass  # Fallback to simple analysis

    return {
        "summary": summary,
        "issues": issues
    }


# ============================================
# Documentation Analysis
# ============================================

async def analyze_documentation() -> List[str]:
    """Read docs and identify missing modules/features"""
    docs_dir = PROJECT_ROOT / "docs"

    # Read relevant docs
    docs_content = ""
    for md_file in docs_dir.rglob("*.md"):
        try:
            with open(md_file) as f:
                docs_content += f"\n\n# {md_file.name}\n{f.read()}"
        except:
            continue

    system_prompt = """You are analyzing Flyto2 documentation to find gaps and missing features.

Look for:
1. Mentioned features not yet implemented
2. Common use cases that need atomic modules
3. Integration opportunities
4. Documentation TODO items

Return JSON list of suggestions:
[
  {
    "type": "missing_module",
    "module_id": "array.flatten",
    "description": "Flatten nested arrays",
    "priority": "medium",
    "found_in": "docs/MODULES.md"
  }
]
"""

    prompt = f"Analyze documentation and identify missing features:\n\n{docs_content[:10000]}"  # Limit size

    response, confidence = await ask_ollama(prompt, system_prompt)

    try:
        import re
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
    except:
        pass

    return []


# ============================================
# Telegram Bot Commands
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    if not is_authorized(update):
        await update.message.reply_text("Unauthorized")
        return

    keyboard = [
        ["🧪 Run Tests", "🏋️ Practice", "🏁 Competition"],
        ["📊 Show Status", "📚 Analyze Docs"],
        ["🤖 Toggle Auto Mode", "🔄 Evolve Now"],
        ["📋 View Proposals", "⚙️ Settings"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "🚀 **Flyto2 Interactive Evolution Bot**\n\n"
        "I'm your AI assistant for continuous module improvement.\n\n"
        "**What I can do:**\n"
        "• Test all modules and report quality\n"
        "• Practice on real websites daily\n"
        "• Suggest improvements based on failures\n"
        "• Analyze docs to find missing features\n"
        "• Discuss new module ideas with you\n"
        "• Auto-improve modules (when approved)\n"
        "• Manual evolution control (/evolve, /propose)\n"
        "• Escalate to OpenAI when needed\n\n"
        "**Three-tier strategy:**\n"
        "1️⃣ Ollama (local, free) - first attempt\n"
        "2️⃣ You (human guidance) - if Ollama unsure\n"
        "3️⃣ OpenAI (paid) - only when both agree\n\n"
        "**Available commands:**\n"
        "/test - Run all module tests\n"
        "/docs - Analyze documentation\n"
        "/practice - Daily practice challenges\n"
        "/competition - Speed race competitions\n"
        "/auto - Toggle autonomous evolution\n"
        "/evolve - Manually trigger evolution\n"
        "/propose - View AI proposals\n"
        "/approve <id> - Approve proposal\n"
        "/reject <id> - Reject proposal\n"
        "/status - Show system status\n\n"
        "Choose an action below:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def run_tests_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Run quality tests on all modules"""
    if not is_authorized(update):
        return

    # Ask if user wants to provide API tokens for more comprehensive testing
    keyboard = [
        [InlineKeyboardButton("🔑 Provide API tokens (test more modules)", callback_data="test_with_tokens")],
        [InlineKeyboardButton("⏩ Skip tokens (basic tests only)", callback_data="test_without_tokens")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🧪 **Module Testing Options**\n\n"
        "**Current coverage:** ~21/111 modules (18.9%)\n\n"
        "Would you like to provide API tokens to test more modules?\n\n"
        "**With tokens**, we can test:\n"
        "• OpenAI/Anthropic/Gemini integrations\n"
        "• Slack/Telegram/Email notifications\n"
        "• Database connectors (if running locally)\n"
        "• Cloud storage (AWS, GCS, Azure)\n\n"
        "**Without tokens**, we test:\n"
        "• String, array, math, object operations\n"
        "• File operations, datetime, utilities\n"
        "• Basic data transformations",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def execute_tests_and_show_results(query_or_message, provided_tokens: Optional[Dict[str, str]] = None):
    """Execute tests and show results (called from callback or directly)"""

    # Send initial message
    if hasattr(query_or_message, 'message'):
        # CallbackQuery
        await query_or_message.message.reply_text("🧪 Running quality tests...\n\nThis may take a few minutes.")
        message_obj = query_or_message.message
    else:
        # Direct message
        await query_or_message.reply_text("🧪 Running quality tests...\n\nThis may take a few minutes.")
        message_obj = query_or_message

    results = await run_module_quality_tests(provided_tokens)
    state.last_test_run = datetime.now(timezone.utc)
    state.module_quality_data = results

    if "error" in results:
        error_msg = f"❌ Test failed:\n{results['error']}"

        # Add debug info if available
        if "traceback" in results:
            error_msg += f"\n\n**Debug Info:**\n"
            error_msg += f"Error Type: {results.get('error_type', 'N/A')}\n"
            error_msg += f"Project Root: `{results.get('project_root', 'N/A')}`\n"
            error_msg += f"Python: `{results.get('python', 'N/A')}`\n"
            error_msg += f"Test Dir Exists: {results.get('test_dir_exists', 'N/A')}\n"
            error_msg += f"CLI Exists: {results.get('cli_exists', 'N/A')}\n"
            error_msg += f"Src Dir Exists: {results.get('src_exists', 'N/A')}\n"
            error_msg += f"PYTHONPATH: {results.get('pythonpath_set', 'N/A')}\n\n"

            # Show traceback (first 500 chars)
            tb = results.get('traceback', '')
            if tb:
                error_msg += f"**Traceback:**\n```\n{tb[:500]}\n```"

        await message_obj.reply_text(error_msg, parse_mode="Markdown")
        return

    # Show test coverage first
    total_tests = results.get("total_tests", 0)
    total_registered = results.get("total_registered_modules", 0)
    modules_tested = results.get("modules_tested", 0)
    modules_untested = results.get("modules_untested", 0)
    coverage_rate = results.get("coverage_rate", 0)
    passed = results.get("passed", 0)
    failed = results.get("failed", 0)
    pass_rate = results.get("pass_rate", 0)

    coverage_msg = (
        f"📊 **Test Coverage Report**\n\n"
        f"**Registered Modules:** {total_registered}\n"
        f"**Modules Tested:** {modules_tested} ({coverage_rate:.1%})\n"
        f"**Modules Untested:** {modules_untested}\n\n"
        f"**Test Results:**\n"
        f"• Tests run: {total_tests}\n"
        f"• Passed: {passed} ✅\n"
        f"• Failed: {failed} ❌\n"
        f"• Pass rate: {pass_rate:.1%}\n"
    )

    await message_obj.reply_text(coverage_msg, parse_mode="Markdown")

    # Show debug info if tests failed
    debug_info = results.get("debug_info")
    if debug_info and failed > 0:
        debug_msg = (
            f"🐛 **Debug Info** (for failed tests):\n\n"
            f"CLI Script: `{debug_info.get('cli_script', 'N/A')}`\n"
            f"CLI Exists: {debug_info.get('cli_exists', 'N/A')}\n"
            f"Project Root: `{debug_info.get('project_root', 'N/A')}`\n"
            f"Python: `{debug_info.get('python_executable', 'N/A')}`\n"
            f"PYTHONPATH: `{debug_info.get('pythonpath', 'N/A')}`\n"
            f"OS Path Sep: `{debug_info.get('os_pathsep', 'N/A')}`\n\n"
            f"**Full stderr from first test:**\n"
            f"```\n{debug_info.get('sample_full_stderr', 'N/A')}\n```"
        )
        await message_obj.reply_text(debug_msg, parse_mode="Markdown")

    # Analyze results
    await message_obj.reply_text("🤔 Analyzing results...")
    analysis = await analyze_test_results(results)

    if "error" in analysis:
        await message_obj.reply_text(f"⚠️ Analysis failed:\n{analysis['error']}")
        return

    # Format response
    summary = analysis.get("summary", "No summary")
    issues = analysis.get("issues", [])

    message = f"📋 **Analysis**\n\n{summary}\n\n"

    if issues:
        message += f"**Found {len(issues)} issues:**\n\n"
        for issue in issues[:5]:  # Show top 5
            message += f"• `{issue['module_id']}` ({issue['current_pass_rate']:.1%})\n"
            message += f"  Issue: {issue['issue']}\n"
            message += f"  💡 {issue['suggestion']}\n\n"

        if len(issues) > 5:
            message += f"...and {len(issues) - 5} more\n"
    else:
        message += "✅ All tested modules passed!"

    await message_obj.reply_text(message, parse_mode="Markdown")

    # Ask if user wants to auto-fix
    if issues:
        keyboard = [
            [InlineKeyboardButton("🔧 Auto-fix high priority", callback_data="autofix_high")],
            [InlineKeyboardButton("📋 Show all issues", callback_data="show_all_issues")],
            [InlineKeyboardButton("❌ Not now", callback_data="dismiss")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message_obj.reply_text(
            "Would you like me to attempt automatic fixes?",
            reply_markup=reply_markup
        )


async def analyze_docs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Analyze documentation for gaps"""
    if not is_authorized(update):
        return

    await update.message.reply_text("📚 Analyzing documentation...\n\nLooking for missing features and gaps.")

    suggestions = await analyze_documentation()

    if not suggestions:
        await update.message.reply_text("✅ Documentation looks complete! No obvious gaps found.")
        return

    message = f"📝 **Found {len(suggestions)} suggestions:**\n\n"

    for sug in suggestions[:5]:
        message += f"• **{sug.get('module_id', 'Unknown')}**\n"
        message += f"  {sug.get('description', '')}\n"
        message += f"  Priority: {sug.get('priority', 'unknown')}\n"
        message += f"  Source: {sug.get('found_in', 'docs')}\n\n"

    if len(suggestions) > 5:
        message += f"...and {len(suggestions) - 5} more\n"

    await update.message.reply_text(message, parse_mode="Markdown")

    # Store suggestions for later
    state.pending_proposals.extend(suggestions)


async def toggle_auto_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle autonomous evolution mode"""
    if not is_authorized(update):
        return

    state.autonomous_mode = not state.autonomous_mode

    if state.autonomous_mode:
        await update.message.reply_text(
            "🤖 **Autonomous Mode ENABLED**\n\n"
            "I will now:\n"
            "• Run tests every hour\n"
            "• Auto-propose improvements\n"
            "• Ask for your approval before merging\n"
            "• Notify you of all actions\n\n"
            "You can still chat with me anytime!"
        )
        # Start background task
        asyncio.create_task(autonomous_evolution_loop(context))
    else:
        await update.message.reply_text(
            "⏸️ **Autonomous Mode DISABLED**\n\n"
            "I'll wait for your commands."
        )


async def autonomous_evolution_loop(context):
    """Background task for autonomous evolution"""
    while state.autonomous_mode:
        # Run continuous improvement workflow
        try:
            result = subprocess.run(
                [
                    "python", "-m", "src.cli.main",
                    "workflows/meta/continuous_improvement_agent.yaml",
                    "--param", "max_improvements=3",
                    "--param", "dry_run=false"
                ],
                capture_output=True,
                text=True,
                timeout=3600,
                cwd=PROJECT_ROOT
            )

            # Parse output and notify user
            # (implementation depends on workflow output format)

        except Exception as e:
            # Notify user of error
            for user_id in TELEGRAM_ALLOWED_USERS:
                try:
                    await context.bot.send_message(
                        chat_id=int(user_id),
                        text=f"⚠️ Autonomous evolution error:\n{str(e)}"
                    )
                except:
                    pass

        # Wait 1 hour before next run
        await asyncio.sleep(3600)


async def competition_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start a competition"""
    if not is_authorized(update):
        return

    keyboard = [
        [InlineKeyboardButton("🏁 Speed Race", callback_data="comp_speed_race")],
        [InlineKeyboardButton("🏆 View Leaderboard", callback_data="comp_leaderboard")],
        [InlineKeyboardButton("📊 Race History", callback_data="comp_history")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🏁 **Competition Mode**\n\n"
        "Compete to improve performance:\n\n"
        "• **Speed Race** - Execute same task multiple times, track best time\n"
        "• **Leaderboard** - See your personal bests\n"
        "• **History** - View past race results\n\n"
        "What would you like to do?",
        reply_markup=reply_markup
    )


async def practice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start a daily practice session"""
    if not is_authorized(update):
        return

    keyboard = [
        [InlineKeyboardButton("🎯 Practice on a website", callback_data="practice_start")],
        [InlineKeyboardButton("📊 View practice stats", callback_data="practice_stats")],
        [InlineKeyboardButton("📜 View practice history", callback_data="practice_history")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🏋️ **Daily Practice Engine**\n\n"
        "Practice makes perfect! Let me train on real websites:\n\n"
        "• Analyze website structure\n"
        "• Infer data schemas automatically\n"
        "• Execute small-scale scraping (10-20 items)\n"
        "• Learn from errors\n"
        "• Track improvement over time\n\n"
        "What would you like to do?",
        reply_markup=reply_markup
    )


async def execute_practice_session(message, url: str, max_items: int = 10):
    """Execute a practice session and show results"""
    from src.core.training.daily_practice import DailyPracticeEngine

    await message.reply_text(f"🎯 Starting practice session on:\n`{url}`\n\nThis may take 30-60 seconds...", parse_mode="Markdown")

    try:
        engine = DailyPracticeEngine()

        # Execute practice
        result = await engine.execute_practice(url, max_items)

        # Format results
        status_emoji = "✅" if result.get("status") == "completed" else "❌"
        success_rate = result.get("success_rate", 0.0)
        success_emoji = "🎉" if success_rate >= 0.8 else ("👍" if success_rate >= 0.5 else "😓")

        response = f"{status_emoji} **Practice Session Complete**\n\n"
        response += f"**URL:** `{url}`\n"
        response += f"**Success Rate:** {success_rate:.1%} {success_emoji}\n"
        response += f"**Items Scraped:** {len(result.get('scraped_data', []))}/{max_items}\n"
        response += f"**Errors:** {len(result.get('errors', []))}\n\n"

        # Show learnings
        learnings = result.get("learnings", [])
        if learnings:
            response += "**🎓 Learnings:**\n"
            for learning in learnings[:5]:
                response += f"• {learning}\n"
            response += "\n"

        # Show recommendations
        recommendations = result.get("analysis", {}).get("recommendations", [])
        if recommendations:
            response += "**💡 Recommendations:**\n"
            for rec in recommendations[:3]:
                response += f"• {rec}\n"
            response += "\n"

        # Show sample data
        scraped_data = result.get("scraped_data", [])
        if scraped_data:
            response += f"**📦 Sample Data (first item):**\n```json\n{json.dumps(scraped_data[0], indent=2, ensure_ascii=False)[:500]}```\n"

        # Show errors if any
        errors = result.get("errors", [])
        if errors:
            response += f"\n**⚠️ Errors ({len(errors)}):**\n"
            for error in errors[:3]:
                response += f"• {error[:100]}\n"

        await message.reply_text(response, parse_mode="Markdown")

    except Exception as e:
        await message.reply_text(f"❌ Practice session failed:\n`{str(e)}`", parse_mode="Markdown")


async def show_practice_stats(message):
    """Show overall practice statistics"""
    from src.core.training.daily_practice import DailyPracticeEngine

    try:
        engine = DailyPracticeEngine()
        stats = engine.get_practice_stats()

        response = "📊 **Practice Statistics**\n\n"
        response += f"**Total Sessions:** {stats.get('total_sessions', 0)}\n"
        response += f"**Avg Success Rate:** {stats.get('avg_success_rate', 0.0):.1%}\n"
        response += f"**Total Items Scraped:** {stats.get('total_items_scraped', 0)}\n"
        response += f"**Total Errors:** {stats.get('total_errors', 0)}\n"

        last_session = stats.get('last_session')
        if last_session:
            response += f"**Last Session:** {last_session}\n"

        await message.reply_text(response, parse_mode="Markdown")

    except Exception as e:
        await message.reply_text(f"❌ Failed to get stats:\n`{str(e)}`", parse_mode="Markdown")


async def show_practice_history(message, limit: int = 5):
    """Show recent practice history"""
    from src.core.training.daily_practice import DailyPracticeEngine

    try:
        engine = DailyPracticeEngine()
        history = engine.get_practice_history(limit)

        if not history:
            await message.reply_text("📜 No practice history yet. Start your first session with `/practice`!")
            return

        response = f"📜 **Recent Practice History (last {len(history)}):**\n\n"

        for idx, session in enumerate(history, 1):
            url = session.get('url', 'Unknown')
            success_rate = session.get('success_rate', 0.0)
            status = session.get('status', 'unknown')
            timestamp = session.get('timestamp', 'Unknown')

            status_emoji = "✅" if status == "completed" else "❌"

            response += f"**{idx}. {status_emoji} {url[:50]}**\n"
            response += f"   Success: {success_rate:.1%} | {timestamp[:10]}\n\n"

        await message.reply_text(response, parse_mode="Markdown")

    except Exception as e:
        await message.reply_text(f"❌ Failed to get history:\n`{str(e)}`", parse_mode="Markdown")


async def show_competition_leaderboard(message, check_changes=True):
    """Show competition leaderboard with ranking change notifications"""
    from src.core.competition.speed_race import SpeedRace

    try:
        engine = SpeedRace()
        leaderboard = engine.get_leaderboard()

        if not leaderboard:
            await message.reply_text("🏆 No races yet. Run your first speed race!")
            return

        # Check for ranking changes
        ranking_changes = []
        current_rankings = {}

        for idx, entry in enumerate(leaderboard[:10], 1):
            task_name = entry.get('task_name', 'Unknown')
            current_rankings[task_name] = idx

            # Compare with previous ranking
            if check_changes and task_name in state.previous_rankings:
                prev_rank = state.previous_rankings[task_name]
                if prev_rank != idx:
                    change = prev_rank - idx  # Positive = improved
                    ranking_changes.append({
                        'task_name': task_name,
                        'prev_rank': prev_rank,
                        'current_rank': idx,
                        'change': change
                    })

        # Send ranking change notifications
        if ranking_changes:
            changes_msg = "📊 **Ranking Changes Detected!**\n\n"
            for change in ranking_changes:
                task = change['task_name']
                prev = change['prev_rank']
                curr = change['current_rank']
                diff = change['change']

                if diff > 0:
                    changes_msg += f"🎉 **{task}** improved!\n"
                    changes_msg += f"   {prev} → {curr} (↑{diff})\n\n"
                else:
                    changes_msg += f"📉 **{task}** dropped\n"
                    changes_msg += f"   {prev} → {curr} (↓{abs(diff)})\n\n"

            await message.reply_text(changes_msg, parse_mode="Markdown")

        # Show leaderboard
        response = "🏆 **Speed Race Leaderboard**\n\n"

        for idx, entry in enumerate(leaderboard[:10], 1):
            task_name = entry.get('task_name', 'Unknown')
            best_time = entry.get('best_time', 0.0)
            avg_time = entry.get('avg_time', 0.0)
            timestamp = entry.get('timestamp', 'Unknown')

            medal = "🥇" if idx == 1 else ("🥈" if idx == 2 else ("🥉" if idx == 3 else f"{idx}."))

            # Add change indicator based on detected changes
            change_indicator = ""
            for change in ranking_changes:
                if change['task_name'] == task_name:
                    if change['change'] > 0:
                        change_indicator = " ↑"
                    else:
                        change_indicator = " ↓"
                    break

            response += f"{medal} **{task_name}**{change_indicator}\n"
            response += f"   Best: {best_time:.2f}s | Avg: {avg_time:.2f}s\n"
            response += f"   Date: {timestamp[:10]}\n\n"

        # Update previous rankings after displaying
        state.previous_rankings = current_rankings

        await message.reply_text(response, parse_mode="Markdown")

    except Exception as e:
        await message.reply_text(f"❌ Failed to get leaderboard:\n`{str(e)}`", parse_mode="Markdown")


async def show_competition_history(message, limit: int = 5):
    """Show recent competition history"""
    from src.core.competition.speed_race import SpeedRace

    try:
        engine = SpeedRace()
        history = engine.get_race_history(limit=limit)

        if not history:
            await message.reply_text("📊 No race history yet. Start your first competition!")
            return

        response = f"📊 **Recent Race History (last {len(history)}):**\n\n"

        for idx, race in enumerate(history, 1):
            task_name = race.get('task_name', 'Unknown')
            status = race.get('status', 'unknown')
            timestamp = race.get('timestamp', 'Unknown')

            status_emoji = "✅" if status == "completed" else "❌"

            stats = race.get('stats', {})
            best_time = stats.get('best_time', 0.0)
            avg_time = stats.get('avg_time', 0.0)

            response += f"**{idx}. {status_emoji} {task_name}**\n"
            if status == "completed":
                response += f"   Best: {best_time:.2f}s | Avg: {avg_time:.2f}s\n"
            response += f"   {timestamp[:10]}\n\n"

        await message.reply_text(response, parse_mode="Markdown")

    except Exception as e:
        await message.reply_text(f"❌ Failed to get history:\n`{str(e)}`", parse_mode="Markdown")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle free-form conversation"""
    if not is_authorized(update):
        return

    user_id = update.effective_user.id
    session = state.get_session(user_id)
    message_text = update.message.text

    # Handle practice URL input flow
    if state.pending_practice_url_input:
        if message_text == "/cancel":
            state.pending_practice_url_input = False
            await update.message.reply_text("❌ Practice session cancelled.")
            return

        # Validate URL
        if message_text.startswith("http://") or message_text.startswith("https://"):
            state.pending_practice_url_input = False
            await execute_practice_session(update.message, message_text, max_items=10)
        else:
            await update.message.reply_text("❌ Invalid URL. Please provide a valid URL starting with http:// or https://\n\nOr send `/cancel` to abort.", parse_mode="Markdown")
        return

    # Handle token collection flow
    if state.pending_test_token_collection:
        if message_text == "/done":
            state.pending_test_token_collection = False
            if state.api_tokens:
                await update.message.reply_text(f"✅ Collected {len(state.api_tokens)} token(s). Starting tests with API integrations...")
                await execute_tests_and_show_results(update.message, provided_tokens=state.api_tokens)
            else:
                await update.message.reply_text("No tokens provided. Running basic tests...")
                await execute_tests_and_show_results(update.message, provided_tokens=None)
            return

        if message_text == "/skip":
            state.pending_test_token_collection = False
            await update.message.reply_text("Skipped token collection. Running basic tests...")
            await execute_tests_and_show_results(update.message, provided_tokens=None)
            return

        # Parse token input
        if "=" in message_text:
            parts = message_text.split("=", 1)
            if len(parts) == 2:
                token_name = parts[0].strip()
                token_value = parts[1].strip()
                state.api_tokens[token_name] = token_value
                await update.message.reply_text(f"✅ Added `{token_name}`\n\nSend more tokens or `/done` to continue.", parse_mode="Markdown")
                return

        await update.message.reply_text("❌ Invalid format. Use: `TOKEN_NAME=value`\nOr send `/done` to finish.", parse_mode="Markdown")
        return

    # Quick replies
    if message_text == "🧪 Run Tests":
        await run_tests_command(update, context)
        return
    elif message_text == "🏋️ Practice":
        await practice_command(update, context)
        return
    elif message_text == "🏁 Competition":
        await competition_command(update, context)
        return
    elif message_text == "📚 Analyze Docs":
        await analyze_docs_command(update, context)
        return
    elif message_text == "🤖 Toggle Auto Mode":
        await toggle_auto_mode(update, context)
        return
    elif message_text == "📊 Show Status":
        await show_status(update, context)
        return
    elif message_text == "🔄 Evolve Now":
        await evolve_command(update, context)
        return
    elif message_text == "📋 View Proposals":
        await propose_command(update, context)
        return

    # General conversation with Ollama
    await update.message.reply_text("🤔 Thinking...")

    system_prompt = """You are an AI assistant for the Flyto2 workflow automation project.

You help with:
- Designing new atomic modules (zero coupling)
- Analyzing test failures
- Suggesting improvements
- Understanding documentation

Key principles:
- Atomic modules must have NO external dependencies (no requests, no playwright, no DB)
- Each module does ONE thing well
- Pure functions preferred
- Always maintain backward compatibility

Current context: {context}
""".format(context=session['context'])

    response, confidence = await ask_ollama(message_text, system_prompt)
    session['stats']['ollama_queries'] += 1

    # Auto-escalation: very low confidence -> jump directly to OpenAI
    auto_escalate_threshold = state.config['auto_escalate_threshold']
    if confidence < auto_escalate_threshold:
        await update.message.reply_text(
            f"💭 Ollama says (confidence: {confidence:.0%}):\n\n{response}\n\n"
            f"⚠️ Very low confidence (< {auto_escalate_threshold:.0%})! Auto-escalating to OpenAI..."
        )

        openai_response = await ask_openai(message_text, system_prompt)
        session['stats']['openai_queries'] += 1

        await update.message.reply_text(
            f"🚀 **OpenAI says:**\n\n{openai_response}"
        )
        return

    # If confidence is low but not critical, ask user for guidance
    human_guidance_threshold = state.config['human_guidance_threshold']
    if confidence < human_guidance_threshold:
        session['pending_question'] = message_text
        session['ollama_confidence'] = confidence

        keyboard = [
            [InlineKeyboardButton("✅ Sounds good", callback_data="approve_ollama")],
            [InlineKeyboardButton("🤔 I'll guide you", callback_data="human_guide")],
            [InlineKeyboardButton("🚀 Ask OpenAI", callback_data="escalate_openai")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"💭 Ollama says (confidence: {confidence:.0%}):\n\n{response}\n\n"
            "I'm not very confident. What should I do?",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(response)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    session = state.get_session(user_id)

    # Competition callbacks
    if query.data == "comp_speed_race":
        await query.edit_message_text("🏁 **Speed Race**\n\nSpeed races are not yet implemented via Telegram UI.\n\nYou can run them via workflow:\n```yaml\n- module: competition.speed_race.run\n  params:\n    task_name: \"my_task\"\n    workflow_path: \"path/to/workflow.yaml\"\n    rounds: 5\n```", parse_mode="Markdown")
        return

    if query.data == "comp_leaderboard":
        await query.message.delete()
        await show_competition_leaderboard(query.message)
        return

    if query.data == "comp_history":
        await query.message.delete()
        await show_competition_history(query.message, limit=5)
        return

    # Practice callbacks
    if query.data == "practice_start":
        await query.edit_message_text("🎯 **Start Practice Session**\n\nPlease send me the URL of a website to practice on.\n\nExample:\n`https://example.com`\n\nSend `/cancel` to abort.", parse_mode="Markdown")
        state.pending_practice_url_input = True
        return

    if query.data == "practice_stats":
        await query.message.delete()
        await show_practice_stats(query.message)
        return

    if query.data == "practice_history":
        await query.message.delete()
        await show_practice_history(query.message, limit=5)
        return

    # Test with tokens flow
    if query.data == "test_with_tokens":
        await query.edit_message_text("🔑 **Provide API Tokens**\n\nPlease provide tokens one by one.\nSend in format: `TOKEN_NAME=value`\n\nExample:\n`OPENAI_API_KEY=sk-xxx`\n\nSend `/done` when finished, or `/skip` to skip remaining.", parse_mode="Markdown")
        state.pending_test_token_collection = True
        state.api_tokens = {}
        return

    # Test without tokens flow
    if query.data == "test_without_tokens":
        await query.edit_message_text("⏩ Running basic tests (no API tokens)...")
        await execute_tests_and_show_results(query, provided_tokens=None)
        return

    if query.data == "escalate_openai":
        await query.edit_message_text("🚀 Escalating to OpenAI...")
        session['stats']['openai_queries'] += 1

        question = session.get('pending_question', query.message.text)
        response = await ask_openai(question, "You are helping with Flyto2 module design.")

        await context.bot.send_message(
            chat_id=user_id,
            text=f"💎 OpenAI says:\n\n{response}"
        )

    elif query.data == "human_guide":
        session['stats']['human_guided'] += 1
        await query.edit_message_text("👤 Waiting for your guidance...\n\nPlease tell me what you think:")

    elif query.data == "approve_ollama":
        await query.edit_message_text("✅ Proceeding with Ollama's suggestion")

    elif query.data == "autofix_high":
        await query.edit_message_text("🔧 Starting auto-fix for high priority issues...")
        # Trigger continuous improvement workflow
        # (implementation)

    elif query.data == "dismiss":
        await query.edit_message_text("👍 Dismissed")


async def show_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show system status"""
    if not is_authorized(update):
        return

    user_id = update.effective_user.id
    session = state.get_session(user_id)

    # Load safety config
    from scripts.safety_manager import SafetyManager
    safety = SafetyManager()

    status_msg = "📊 **System Status**\n\n"
    status_msg += f"**Autonomous Mode**: {'🟢 ON' if state.autonomous_mode else '🔴 OFF'}\n"
    status_msg += f"**Auto-merge**: {'✅ Enabled' if safety.is_auto_merge_enabled() else '❌ Disabled'}\n"
    status_msg += f"**Auto-rollback**: {'✅ Enabled' if safety.is_auto_rollback_enabled() else '❌ Disabled'}\n"
    status_msg += f"**Dry-run**: {'🔍 ON' if safety.is_dry_run_enabled() else 'OFF'}\n\n"

    status_msg += "**Your Session Stats:**\n"
    status_msg += f"• Ollama queries: {session['stats']['ollama_queries']}\n"
    status_msg += f"• Human guided: {session['stats']['human_guided']}\n"
    status_msg += f"• OpenAI queries: {session['stats']['openai_queries']}\n"
    status_msg += f"• Modules proposed: {session['stats']['modules_proposed']}\n"
    status_msg += f"• Modules implemented: {session['stats']['modules_implemented']}\n\n"

    if state.last_test_run:
        status_msg += f"**Last test run**: {state.last_test_run.strftime('%Y-%m-%d %H:%M')}\n"

    status_msg += f"**Pending proposals**: {len(state.pending_proposals)}\n"

    await update.message.reply_text(status_msg, parse_mode="Markdown")


async def evolve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manually trigger evolution cycle"""
    if not is_authorized(update):
        return

    await update.message.reply_text("🔄 Triggering manual evolution cycle...")

    try:
        result = subprocess.run(
            [
                "python", "-m", "src.cli.main",
                "workflows/meta/continuous_improvement_agent.yaml",
                "--param", "max_improvements=3",
                "--param", "dry_run=false"
            ],
            capture_output=True,
            text=True,
            timeout=3600,
            cwd=PROJECT_ROOT
        )

        if result.returncode == 0:
            await update.message.reply_text(
                "✅ **Evolution cycle completed**\n\n"
                f"Output:\n```\n{result.stdout[-500:] if len(result.stdout) > 500 else result.stdout}\n```",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                f"❌ **Evolution cycle failed**\n\n```\n{result.stderr[-500:]}\n```",
                parse_mode="Markdown"
            )
    except subprocess.TimeoutExpired:
        await update.message.reply_text("⏱️ Evolution cycle timed out (1 hour limit)")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def propose_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View pending AI proposals"""
    if not is_authorized(update):
        return

    if not state.pending_proposals:
        await update.message.reply_text(
            "📭 **No pending proposals**\n\n"
            "Run /evolve or /docs to generate new improvement suggestions."
        )
        return

    message = f"📋 **Pending Proposals** ({len(state.pending_proposals)})\n\n"

    for idx, proposal in enumerate(state.pending_proposals):
        status_icon = "⏳" if proposal.get('status') == 'pending' else "✅"
        message += f"{status_icon} **[{idx}]** {proposal.get('module_id', 'Unknown')}\n"
        message += f"   {proposal.get('description', 'No description')}\n"
        message += f"   Priority: {proposal.get('priority', 'unknown')}\n"
        message += f"   Source: {proposal.get('found_in', 'unknown')}\n\n"

    message += "\nUse `/approve <id>` or `/reject <id>` to respond."

    await update.message.reply_text(message, parse_mode="Markdown")


async def approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Approve a specific proposal"""
    if not is_authorized(update):
        return

    if not context.args:
        await update.message.reply_text(
            "❌ **Usage**: /approve <id>\n\n"
            "Use /propose to see proposal IDs."
        )
        return

    try:
        proposal_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid proposal ID. Must be a number.")
        return

    if proposal_id < 0 or proposal_id >= len(state.pending_proposals):
        await update.message.reply_text(
            f"❌ Proposal ID {proposal_id} not found.\n\n"
            f"Valid range: 0-{len(state.pending_proposals) - 1}"
        )
        return

    proposal = state.pending_proposals[proposal_id]
    proposal['status'] = 'approved'
    proposal['approved_at'] = datetime.now(timezone.utc).isoformat()

    # Log to evolution reporter
    try:
        from src.core.evolution import get_reporter
        reporter = get_reporter()
        reporter.log_evolution_event(
            event_type="proposal_accepted",
            description=f"Approved proposal for {proposal.get('module_id')}",
            details={
                "proposal_id": proposal_id,
                "module_id": proposal.get('module_id'),
                "priority": proposal.get('priority')
            },
            impact="high"
        )
    except Exception as e:
        print(f"Warning: Could not log to evolution reporter: {e}")

    await update.message.reply_text(
        f"✅ **Proposal [{proposal_id}] APPROVED**\n\n"
        f"Module: {proposal.get('module_id')}\n"
        f"Description: {proposal.get('description')}\n\n"
        f"This proposal is now ready for implementation."
    )


async def reject_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reject a specific proposal"""
    if not is_authorized(update):
        return

    if not context.args:
        await update.message.reply_text(
            "❌ **Usage**: /reject <id>\n\n"
            "Use /propose to see proposal IDs."
        )
        return

    try:
        proposal_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid proposal ID. Must be a number.")
        return

    if proposal_id < 0 or proposal_id >= len(state.pending_proposals):
        await update.message.reply_text(
            f"❌ Proposal ID {proposal_id} not found.\n\n"
            f"Valid range: 0-{len(state.pending_proposals) - 1}"
        )
        return

    proposal = state.pending_proposals[proposal_id]
    proposal['status'] = 'rejected'
    proposal['rejected_at'] = datetime.now(timezone.utc).isoformat()

    # Log to evolution reporter
    try:
        from src.core.evolution import get_reporter
        reporter = get_reporter()
        reporter.log_evolution_event(
            event_type="proposal_rejected",
            description=f"Rejected proposal for {proposal.get('module_id')}",
            details={
                "proposal_id": proposal_id,
                "module_id": proposal.get('module_id'),
                "priority": proposal.get('priority')
            },
            impact="low"
        )
    except Exception as e:
        print(f"Warning: Could not log to evolution reporter: {e}")

    await update.message.reply_text(
        f"❌ **Proposal [{proposal_id}] REJECTED**\n\n"
        f"Module: {proposal.get('module_id')}\n"
        f"Description: {proposal.get('description')}\n\n"
        f"This proposal will not be implemented."
    )


async def config_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View or update escalation configuration"""
    if not is_authorized(update):
        return

    if not context.args:
        # Show current config
        config = state.config
        await update.message.reply_text(
            "⚙️ **Escalation Configuration**\n\n"
            f"**Auto-escalate threshold**: {config['auto_escalate_threshold']:.0%}\n"
            f"  • Confidence < {config['auto_escalate_threshold']:.0%} → Auto jump to OpenAI\n\n"
            f"**Human guidance threshold**: {config['human_guidance_threshold']:.0%}\n"
            f"  • Confidence < {config['human_guidance_threshold']:.0%} → Ask for guidance\n\n"
            f"**Auto-approve threshold**: {config['auto_approve_threshold']:.0%}\n"
            f"  • Confidence >= {config['auto_approve_threshold']:.0%} → Auto approve\n\n"
            "**Usage**: /config <key> <value>\n"
            "Example: /config auto_escalate_threshold 0.25",
            parse_mode="Markdown"
        )
        return

    # Update config
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ **Usage**: /config <key> <value>\n\n"
            "Available keys:\n"
            "• auto_escalate_threshold\n"
            "• human_guidance_threshold\n"
            "• auto_approve_threshold"
        )
        return

    key = context.args[0]
    try:
        value = float(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Value must be a number between 0 and 1")
        return

    if key not in state.config:
        await update.message.reply_text(
            f"❌ Unknown config key: {key}\n\n"
            "Available keys:\n"
            "• auto_escalate_threshold\n"
            "• human_guidance_threshold\n"
            "• auto_approve_threshold"
        )
        return

    if not 0 <= value <= 1:
        await update.message.reply_text("❌ Value must be between 0 and 1")
        return

    old_value = state.config[key]
    state.config[key] = value

    await update.message.reply_text(
        f"✅ **Config updated**\n\n"
        f"{key}: {old_value:.0%} → {value:.0%}"
    )


# ============================================
# Main
# ============================================

def main():
    """Start the bot"""
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set")
        return 1

    print("Starting Flyto2 Interactive Evolution Bot...")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Ollama URL: {OLLAMA_URL}")
    print(f"OpenAI configured: {bool(OPENAI_API_KEY)}")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", run_tests_command))
    app.add_handler(CommandHandler("docs", analyze_docs_command))
    app.add_handler(CommandHandler("practice", practice_command))
    app.add_handler(CommandHandler("competition", competition_command))
    app.add_handler(CommandHandler("auto", toggle_auto_mode))
    app.add_handler(CommandHandler("status", show_status))
    app.add_handler(CommandHandler("evolve", evolve_command))
    app.add_handler(CommandHandler("propose", propose_command))
    app.add_handler(CommandHandler("approve", approve_command))
    app.add_handler(CommandHandler("reject", reject_command))
    app.add_handler(CommandHandler("config", config_command))

    # Message handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Callback handlers
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("Bot ready! Send /start to begin.")
    app.run_polling()


if __name__ == "__main__":
    exit(main())
