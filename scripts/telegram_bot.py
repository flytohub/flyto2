#!/usr/bin/env python3
"""
Flyto2 Telegram Bot - AI Assistant with Hybrid LLM
Default: Local LLM (Ollama) - Free
On-demand: OpenAI GPT-4 - For complex tasks
"""
import os
import json
import subprocess
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_ALLOWED_USERS = os.getenv('TELEGRAM_ALLOWED_USERS', '').split(',')
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PROJECT_ROOT = Path(__file__).parent.parent


class ModelMode:
    """Model operation modes"""
    LOCAL = "local"      # Always use Ollama
    OPENAI = "openai"    # Always use OpenAI
    AUTO = "auto"        # Default Ollama, /gpt for OpenAI


class BotState:
    """In-memory conversation state"""

    def __init__(self):
        self.sessions: Dict[int, Dict] = {}

    def get_session(self, user_id: int) -> Dict:
        """Get or create user session"""
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                "model_mode": ModelMode.AUTO,
                "conversation_history": [],
                "stats": {
                    "local_queries": 0,
                    "openai_queries": 0,
                    "cost_saved": 0.0
                }
            }
        return self.sessions[user_id]

    def add_message(self, user_id: int, role: str, content: str):
        """Add message to conversation history"""
        session = self.get_session(user_id)
        session["conversation_history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Keep only last 20 messages
        if len(session["conversation_history"]) > 20:
            session["conversation_history"] = session["conversation_history"][-20:]


# Global state
state = BotState()


def is_authorized(update: Update) -> bool:
    """Check if user is authorized"""
    user_id = str(update.effective_user.id)
    return user_id in TELEGRAM_ALLOWED_USERS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    if not is_authorized(update):
        await update.message.reply_text("Unauthorized access.")
        return

    user_id = update.effective_user.id
    session = state.get_session(user_id)

    welcome = f"""
🤖 **Flyto2 AI Assistant**

Hi! I'm your hybrid AI assistant.

**Current mode:** {session['model_mode']}

**Available commands:**

**Model Control:**
• `/mode local` - Always use local LLM (free)
• `/mode openai` - Always use OpenAI (costs money)
• `/mode auto` - Smart hybrid (recommended)
• `/mode status` - Show current settings

**Ask Questions:**
• `/ask <question>` - Ask using current model
• `/gpt <question>` - Force OpenAI for this question

**Flyto2 Workflows:**
• `/status` - Current quality metrics
• `/quality` - Detailed quality report
• `/test <module>` - Run tests for module

**Help:**
• `/help` - Show this message

Just start chatting! I'll use {session['model_mode']} mode.
    """

    await update.message.reply_text(welcome, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    if not is_authorized(update):
        return

    help_text = """
**Flyto2 Bot Commands**

**Chat:**
• Just type your message - I'll respond using current model
• `/gpt <question>` - Use OpenAI for complex tasks

**Model Switching:**
• `/mode local` - Use Ollama only (free, fast)
• `/mode openai` - Use OpenAI only ($$)
• `/mode auto` - Hybrid (default Ollama, /gpt for OpenAI)

**Flyto2:**
• `/status` - Quality overview
• `/quality` - Detailed metrics
• `/test string.split` - Test specific module

**Examples:**
```
You: What changed yesterday?
Bot: [Ollama] Shows git log...

You: /gpt Refactor this code with best practices
Bot: [OpenAI] Detailed refactoring...

You: /status
Bot: 21 modules, 100% pass rate ✅
```
    """

    await update.message.reply_text(help_text, parse_mode='Markdown')


async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mode command"""
    if not is_authorized(update):
        return

    user_id = update.effective_user.id
    session = state.get_session(user_id)

    if not context.args:
        # Show current mode
        stats = session['stats']
        status_msg = f"""
**Current Mode:** {session['model_mode']}

**Today's Stats:**
• Ollama queries: {stats['local_queries']} (free)
• OpenAI queries: {stats['openai_queries']}
• Estimated savings: ${stats['cost_saved']:.2f}

**Change mode:**
• `/mode local` - Local only
• `/mode openai` - OpenAI only
• `/mode auto` - Hybrid (recommended)
        """
        await update.message.reply_text(status_msg, parse_mode='Markdown')
        return

    new_mode = context.args[0].lower()

    if new_mode not in [ModelMode.LOCAL, ModelMode.OPENAI, ModelMode.AUTO]:
        await update.message.reply_text(
            f"Invalid mode: {new_mode}\nUse: local, openai, or auto"
        )
        return

    session['model_mode'] = new_mode
    await update.message.reply_text(
        f"✅ Switched to **{new_mode}** mode",
        parse_mode='Markdown'
    )


async def ask_ollama(prompt: str, conversation_history: List = None) -> str:
    """Ask Ollama (local LLM)"""
    try:
        import requests

        messages = conversation_history or []
        messages.append({"role": "user", "content": prompt})

        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": "llama3.2",
                "messages": messages,
                "stream": False
            },
            timeout=60
        )

        if response.status_code == 200:
            return response.json()['message']['content']
        else:
            return f"Ollama error: {response.status_code}"

    except Exception as e:
        return f"Ollama unavailable: {e}\nTry `/mode openai` or install Ollama"


async def ask_openai(prompt: str, conversation_history: List = None) -> str:
    """Ask OpenAI GPT-4"""
    try:
        import openai

        if not OPENAI_API_KEY:
            return "OpenAI API key not configured. Add OPENAI_API_KEY to .env"

        client = openai.OpenAI(api_key=OPENAI_API_KEY)

        messages = conversation_history or []
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"OpenAI error: {e}"


async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ask command"""
    if not is_authorized(update):
        return

    if not context.args:
        await update.message.reply_text("Usage: /ask <your question>")
        return

    user_id = update.effective_user.id
    session = state.get_session(user_id)
    question = " ".join(context.args)

    # Add to history
    state.add_message(user_id, "user", question)

    # Determine which model to use
    mode = session['model_mode']

    # Send "typing" indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    if mode == ModelMode.OPENAI:
        response = await ask_openai(question, session['conversation_history'])
        session['stats']['openai_queries'] += 1
        model_used = "OpenAI GPT-4"
    else:  # LOCAL or AUTO
        response = await ask_ollama(question, session['conversation_history'])
        session['stats']['local_queries'] += 1
        session['stats']['cost_saved'] += 0.15  # Rough estimate
        model_used = "Ollama (Local)"

    # Add response to history
    state.add_message(user_id, "assistant", response)

    # Send response
    await update.message.reply_text(
        f"*[{model_used}]*\n\n{response}",
        parse_mode='Markdown'
    )


async def gpt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /gpt command - force OpenAI"""
    if not is_authorized(update):
        return

    if not context.args:
        await update.message.reply_text("Usage: /gpt <your question>")
        return

    user_id = update.effective_user.id
    session = state.get_session(user_id)
    question = " ".join(context.args)

    state.add_message(user_id, "user", question)

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    # Force OpenAI
    response = await ask_openai(question, session['conversation_history'])
    session['stats']['openai_queries'] += 1

    state.add_message(user_id, "assistant", response)

    await update.message.reply_text(
        f"*[OpenAI GPT-4]*\n\n{response}",
        parse_mode='Markdown'
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status - show Flyto2 quality status"""
    if not is_authorized(update):
        return

    await update.message.reply_text("📊 Checking quality status...")

    try:
        # Read metrics file
        metrics_file = PROJECT_ROOT / "metrics" / "module_quality.json"

        with open(metrics_file) as f:
            metrics = json.load(f)

        summary = metrics.get('summary', {})

        status_msg = f"""
**📊 Flyto2 Quality Status**

**Modules:** {summary.get('total_modules', 0)}
• Above 98%: {summary.get('modules_above_98', 0)} ✅
• 95-98%: {summary.get('modules_95_to_98', 0)} ⚠️
• Below 95%: {summary.get('modules_below_95', 0)} 🚨

**Auto-merge approved:** {summary.get('auto_merge_approved_count', 0)}

**Last updated:** {metrics.get('_last_updated', 'Unknown')}
        """

        await update.message.reply_text(status_msg, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"Error reading metrics: {e}")


async def quality_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /quality - detailed quality report"""
    if not is_authorized(update):
        return

    await update.message.reply_text("📈 Generating quality report...")

    try:
        metrics_file = PROJECT_ROOT / "metrics" / "module_quality.json"

        with open(metrics_file) as f:
            metrics = json.load(f)

        modules = metrics.get('modules', {})

        # Group by pass rate
        perfect = []
        good = []
        needs_attention = []

        for module_id, data in modules.items():
            rate = data.get('recent_pass_rate', 0)
            if rate >= 0.98:
                perfect.append(f"• {module_id}: {rate:.1%}")
            elif rate >= 0.95:
                good.append(f"• {module_id}: {rate:.1%}")
            else:
                needs_attention.append(f"• {module_id}: {rate:.1%} 🚨")

        report = f"""
**📈 Detailed Quality Report**

**Perfect (≥98%):** {len(perfect)}
{chr(10).join(perfect[:5])}  # Show first 5

**Good (95-98%):** {len(good)}
{chr(10).join(good) if good else '(none)'}

**Needs Attention (<95%):** {len(needs_attention)}
{chr(10).join(needs_attention) if needs_attention else '(none)'}
        """

        await update.message.reply_text(report, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages (chat mode)"""
    if not is_authorized(update):
        return

    user_id = update.effective_user.id
    session = state.get_session(user_id)
    message = update.message.text

    # Add to history
    state.add_message(user_id, "user", message)

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    # Use current mode
    mode = session['model_mode']

    if mode == ModelMode.OPENAI:
        response = await ask_openai(message, session['conversation_history'])
        session['stats']['openai_queries'] += 1
        model_used = "OpenAI"
    else:
        response = await ask_ollama(message, session['conversation_history'])
        session['stats']['local_queries'] += 1
        session['stats']['cost_saved'] += 0.15
        model_used = "Ollama"

    state.add_message(user_id, "assistant", response)

    await update.message.reply_text(response)


def main():
    """Start the bot"""
    print("Starting Flyto2 Telegram Bot...")

    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not set in .env")
        return

    if not TELEGRAM_ALLOWED_USERS or TELEGRAM_ALLOWED_USERS == ['']:
        print("WARNING: TELEGRAM_ALLOWED_USERS not set - bot will reject all users")
        print("Add your Telegram user ID to .env: TELEGRAM_ALLOWED_USERS=123456789")

    # Create application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("mode", mode_command))
    app.add_handler(CommandHandler("ask", ask_command))
    app.add_handler(CommandHandler("gpt", gpt_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("quality", quality_command))

    # Handle regular messages (chat mode)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot started successfully!")
    print(f"Allowed users: {TELEGRAM_ALLOWED_USERS}")
    print(f"Ollama URL: {OLLAMA_URL}")
    print(f"OpenAI configured: {bool(OPENAI_API_KEY)}")
    print("\nBot is running... Press Ctrl+C to stop.")

    # Start polling
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
