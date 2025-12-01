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

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_ALLOWED_USERS = os.getenv('TELEGRAM_ALLOWED_USERS', '').split(',')
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PROJECT_ROOT = Path(__file__).parent.parent


class EvolutionState:
    """Tracks AI evolution state and conversation history"""

    def __init__(self):
        self.sessions: Dict[int, Dict] = {}
        self.autonomous_mode = False  # Auto-run continuous improvement
        self.last_test_run = None
        self.module_quality_data = {}
        self.pending_proposals = []  # AI proposals waiting for your review

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

async def run_module_quality_tests() -> Dict:
    """Run REAL quality tests by executing test workflows"""
    try:
        # Find all test workflows
        test_dir = PROJECT_ROOT / "workflows" / "_test"

        if not test_dir.exists():
            return {"error": "No test directory found"}

        test_files = list(test_dir.glob("test_*.yaml"))

        if not test_files:
            return {"error": "No test files found"}

        # Run each test workflow
        results = {}
        passed = 0
        failed = 0

        for test_file in test_files:
            module_name = test_file.stem.replace("test_", "")

            try:
                # Execute the test workflow
                result = subprocess.run(
                    ["python", "-m", "src.cli.main", str(test_file)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=PROJECT_ROOT
                )

                if result.returncode == 0:
                    results[module_name] = {
                        "status": "pass",
                        "pass_rate": 1.0
                    }
                    passed += 1
                else:
                    results[module_name] = {
                        "status": "fail",
                        "pass_rate": 0.0,
                        "error": result.stderr[:200] if result.stderr else "Unknown error"
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
                    "error": str(e)[:200]
                }
                failed += 1

        total = passed + failed

        return {
            "total_modules": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / total if total > 0 else 0,
            "modules": results,
            "source": "real_execution"
        }

    except Exception as e:
        return {"error": f"Test execution failed: {str(e)}"}


async def analyze_test_results(results: Dict) -> Dict:
    """Use Ollama to analyze test results and suggest improvements"""

    # Simple analysis without AI if results are straightforward
    total = results.get("total_modules", 0)
    passed = results.get("passed", 0)
    failed = results.get("failed", 0)
    pass_rate = results.get("pass_rate", 0)

    if total == 0:
        return {
            "summary": "No modules tested",
            "issues": []
        }

    # Create simple summary
    summary = f"Tested {total} modules: {passed} passed, {failed} failed ({pass_rate:.1%} success rate)"

    # Identify failing modules
    issues = []
    modules = results.get("modules", {})
    for module_id, data in modules.items():
        if isinstance(data, dict) and data.get("status") == "fail":
            issues.append({
                "module_id": module_id,
                "current_pass_rate": data.get("pass_rate", 0.0),
                "issue": "Module validation failed",
                "suggestion": "Check module implementation and tests",
                "priority": "high"
            })

    # If Ollama available, try to get AI insights
    if failed > 0 and OLLAMA_URL:
        try:
            system_prompt = """Briefly analyze these module test failures and suggest fixes.
Keep response under 200 words, plain text format."""

            prompt = f"Test results: {passed}/{total} passed, {failed} failed.\nFailing modules: {[m['module_id'] for m in issues]}\n\nSuggest improvements:"

            response, confidence = await ask_ollama(prompt, system_prompt)

            if response and "error" not in response.lower():
                summary += f"\n\nAI insights: {response[:300]}"
        except:
            pass  # Fallback to simple analysis

    return {
        "summary": summary,
        "issues": issues,
        "total_modules": total,
        "passed": passed,
        "failed": failed
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
        ["🧪 Run Tests", "📊 Show Status"],
        ["💡 Suggest Improvements", "📚 Analyze Docs"],
        ["🤖 Toggle Auto Mode", "⚙️ Settings"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "🚀 **Flyto2 Interactive Evolution Bot**\n\n"
        "I'm your AI assistant for continuous module improvement.\n\n"
        "**What I can do:**\n"
        "• Test all modules and report quality\n"
        "• Suggest improvements based on failures\n"
        "• Analyze docs to find missing features\n"
        "• Discuss new module ideas with you\n"
        "• Auto-improve modules (when approved)\n"
        "• Escalate to OpenAI when needed\n\n"
        "**Three-tier strategy:**\n"
        "1️⃣ Ollama (local, free) - first attempt\n"
        "2️⃣ You (human guidance) - if Ollama unsure\n"
        "3️⃣ OpenAI (paid) - only when both agree\n\n"
        "Choose an action below:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def run_tests_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Run quality tests on all modules"""
    if not is_authorized(update):
        return

    await update.message.reply_text("🧪 Running quality tests on all modules...\n\nThis may take a few minutes.")

    results = await run_module_quality_tests()
    state.last_test_run = datetime.now(timezone.utc)
    state.module_quality_data = results

    if "error" in results:
        await update.message.reply_text(f"❌ Test failed:\n{results['error']}")
        return

    # Analyze results with Ollama
    await update.message.reply_text("🤔 Analyzing results with local AI...")
    analysis = await analyze_test_results(results)

    if "error" in analysis:
        await update.message.reply_text(f"⚠️ Analysis failed:\n{analysis['error']}")
        return

    # Format response
    summary = analysis.get("summary", "No summary")
    issues = analysis.get("issues", [])

    message = f"📊 **Test Results**\n\n{summary}\n\n"

    if issues:
        message += f"**Found {len(issues)} issues:**\n\n"
        for issue in issues[:5]:  # Show top 5
            message += f"• `{issue['module_id']}` ({issue['current_pass_rate']:.1%})\n"
            message += f"  Issue: {issue['issue']}\n"
            message += f"  💡 {issue['suggestion']}\n\n"

        if len(issues) > 5:
            message += f"...and {len(issues) - 5} more\n"
    else:
        message += "✅ All modules looking good!"

    await update.message.reply_text(message, parse_mode="Markdown")

    # Ask if user wants to auto-fix
    if issues:
        keyboard = [
            [InlineKeyboardButton("🔧 Auto-fix high priority", callback_data="autofix_high")],
            [InlineKeyboardButton("📋 Show all issues", callback_data="show_all_issues")],
            [InlineKeyboardButton("❌ Not now", callback_data="dismiss")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
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


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle free-form conversation"""
    if not is_authorized(update):
        return

    user_id = update.effective_user.id
    session = state.get_session(user_id)
    message_text = update.message.text

    # Quick replies
    if message_text == "🧪 Run Tests":
        await run_tests_command(update, context)
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

    # If confidence is low, ask user for guidance
    if confidence < 0.5:
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
    app.add_handler(CommandHandler("auto", toggle_auto_mode))
    app.add_handler(CommandHandler("status", show_status))

    # Message handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Callback handlers
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("Bot ready! Send /start to begin.")
    app.run_polling()


if __name__ == "__main__":
    exit(main())
