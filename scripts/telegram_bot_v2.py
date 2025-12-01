#!/usr/bin/env python3
"""
Flyto2 Telegram Bot V2 - Ultra-Low-Cost Three-Tier Strategy

Tier 1: Ollama (free) - handles 90% of queries
Tier 2: Human guidance (free) - you provide direction when Ollama unsure
Tier 3: OpenAI (paid) - only when you explicitly approve

Cost: ~NT$30-60/month (vs NT$2,430 with OpenAI-only)
"""
import os
import json
import subprocess
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_ALLOWED_USERS = os.getenv('TELEGRAM_ALLOWED_USERS', '').split(',')
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PROJECT_ROOT = Path(__file__).parent.parent


class BotState:
    """Session state with pending questions"""

    def __init__(self):
        self.sessions: Dict[int, Dict] = {}

    def get_session(self, user_id: int) -> Dict:
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                "conversation": [],
                "pending_question": None,  # Question waiting for guidance
                "ollama_attempt": None,     # Last Ollama response
                "stats": {
                    "ollama_queries": 0,
                    "human_guided": 0,
                    "openai_queries": 0,
                    "cost_today": 0.0
                }
            }
        return self.sessions[user_id]

    def set_pending(self, user_id: int, question: str, ollama_response: str):
        """Store question that needs human guidance"""
        session = self.get_session(user_id)
        session["pending_question"] = question
        session["ollama_attempt"] = ollama_response

    def clear_pending(self, user_id: int):
        """Clear pending question after resolved"""
        session = self.get_session(user_id)
        session["pending_question"] = None
        session["ollama_attempt"] = None


state = BotState()


def is_authorized(update: Update) -> bool:
    user_id = str(update.effective_user.id)
    return user_id in TELEGRAM_ALLOWED_USERS


async def ask_ollama(prompt: str, system_prompt: str = None) -> tuple[str, float]:
    """
    Ask Ollama and return (response, confidence)
    Confidence: 0.0-1.0 estimate based on response analysis
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
            timeout=60
        )

        if response.status_code != 200:
            return f"Ollama error: {response.status_code}", 0.0

        answer = response.json()['message']['content']

        # Estimate confidence based on response patterns
        confidence = estimate_confidence(answer)

        return answer, confidence

    except Exception as e:
        return f"Ollama unavailable: {e}", 0.0


def estimate_confidence(answer: str) -> float:
    """
    Estimate LLM confidence based on response patterns
    Returns 0.0-1.0
    """
    low_confidence_phrases = [
        "not sure", "uncertain", "might", "maybe", "could be",
        "not confident", "i think", "probably", "perhaps",
        "unclear", "don't know"
    ]

    answer_lower = answer.lower()

    # Check for uncertainty phrases
    uncertainty_count = sum(1 for phrase in low_confidence_phrases if phrase in answer_lower)

    if uncertainty_count >= 2:
        return 0.3  # Low confidence
    elif uncertainty_count == 1:
        return 0.6  # Medium confidence
    elif len(answer) < 50:
        return 0.5  # Too short, unclear
    else:
        return 0.8  # Likely confident


async def ask_openai(prompt: str, system_prompt: str = None) -> str:
    """Ask OpenAI GPT-4 (costs money)"""
    try:
        import openai

        if not OPENAI_API_KEY:
            return "OpenAI API key not configured"

        client = openai.OpenAI(api_key=OPENAI_API_KEY)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.3  # Lower for more focused answers
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"OpenAI error: {e}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    if not is_authorized(update):
        await update.message.reply_text("Unauthorized")
        return

    welcome = """
🤖 *Flyto2 AI Assistant V2*
Ultra-Low-Cost Three-Tier Strategy

*How it works:*
1️⃣ I try with Ollama (free)
2️⃣ If unsure, I ask your guidance (free)
3️⃣ You can force OpenAI if needed (paid)

*Cost: ~NT$30-60/month* 💰

*Commands:*
• Just chat - I'll use Ollama
• `/gpt <q>` - Force OpenAI ($)
• `/retry` - Retry with OpenAI after my attempt
• `/status` - Flyto2 quality status
• `/stats` - Usage statistics

*Example flow:*
```
You: How to refactor this?
Bot: [Ollama] I'm not confident...
     Need your guidance?

You: Use async, keep compatibility
Bot: [Ollama] Got it! Here's the plan...
```

Start chatting! 🚀
    """

    await update.message.reply_text(welcome, parse_mode='Markdown')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages with three-tier logic"""
    if not is_authorized(update):
        return

    user_id = update.effective_user.id
    session = state.get_session(user_id)
    message = update.message.text

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    # Check if this is guidance for a pending question
    if session["pending_question"]:
        # User is providing guidance
        await handle_guidance(update, context, message)
        return

    # Tier 1: Try Ollama first
    answer, confidence = await ask_ollama(message)
    session['stats']['ollama_queries'] += 1

    # If confident enough, return directly
    if confidence >= 0.7:
        await update.message.reply_text(
            f"*[Ollama ✓ {confidence:.0%}]*\n\n{answer}",
            parse_mode='Markdown'
        )
        return

    # Tier 2: Not confident - ask for human guidance
    state.set_pending(user_id, message, answer)

    guidance_keyboard = [
        ["💡 Give guidance", "🤖 Retry OpenAI ($)"],
        ["✅ Accept anyway"]
    ]

    await update.message.reply_text(
        f"*[Ollama ⚠️ Low confidence: {confidence:.0%}]*\n\n{answer}\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"*Options:*\n"
        f"• Give me direction (free)\n"
        f"• `/retry` - Use OpenAI (costs $0.05-0.15)\n"
        f"• Accept this answer anyway",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup(
            guidance_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )


async def handle_guidance(update: Update, context: ContextTypes.DEFAULT_TYPE, guidance: str):
    """Handle human guidance for pending question"""
    user_id = update.effective_user.id
    session = state.get_session(user_id)

    original_question = session["pending_question"]

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    # Re-ask Ollama with guidance
    enhanced_prompt = f"""
Original question: {original_question}

Human guidance: {guidance}

Based on the guidance above, provide a focused answer.
Be concise. Follow the direction given.
"""

    answer, confidence = await ask_ollama(enhanced_prompt)
    session['stats']['human_guided'] += 1

    state.clear_pending(user_id)

    await update.message.reply_text(
        f"*[Ollama + Your Guidance ✓]*\n\n{answer}",
        parse_mode='Markdown'
    )


async def retry_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Retry with OpenAI (Tier 3)"""
    if not is_authorized(update):
        return

    user_id = update.effective_user.id
    session = state.get_session(user_id)

    if not session["pending_question"]:
        await update.message.reply_text(
            "No pending question to retry.\n"
            "Use `/gpt <question>` to ask OpenAI directly."
        )
        return

    question = session["pending_question"]

    await update.message.reply_text(
        "💰 Using OpenAI (~$0.05-0.15)...",
        parse_mode='Markdown'
    )

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    # Tier 3: OpenAI
    system_prompt = "You are an expert engineer. Provide the best solution. Be concise. Full code, minimal prose."
    answer = await ask_openai(question, system_prompt)

    session['stats']['openai_queries'] += 1
    session['stats']['cost_today'] += 0.10  # Rough estimate

    state.clear_pending(user_id)

    await update.message.reply_text(
        f"*[OpenAI GPT-4 ✓ $0.10]*\n\n{answer}",
        parse_mode='Markdown'
    )


async def gpt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Direct OpenAI query (skip Ollama)"""
    if not is_authorized(update):
        return

    if not context.args:
        await update.message.reply_text("Usage: `/gpt <question>`", parse_mode='Markdown')
        return

    user_id = update.effective_user.id
    session = state.get_session(user_id)
    question = " ".join(context.args)

    await update.message.reply_text("💰 Using OpenAI...", parse_mode='Markdown')

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    system_prompt = "You are an expert engineer. Provide the best solution. Be concise. Full code, minimal prose."
    answer = await ask_openai(question, system_prompt)

    session['stats']['openai_queries'] += 1
    session['stats']['cost_today'] += 0.10

    await update.message.reply_text(
        f"*[OpenAI GPT-4 ✓ $0.10]*\n\n{answer}",
        parse_mode='Markdown'
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show usage statistics"""
    if not is_authorized(update):
        return

    user_id = update.effective_user.id
    session = state.get_session(user_id)
    stats = session['stats']

    total_queries = stats['ollama_queries'] + stats['human_guided'] + stats['openai_queries']

    if total_queries == 0:
        savings = 0
    else:
        # If all were OpenAI: total * $0.10
        # Actual: openai_queries * $0.10
        could_have_spent = total_queries * 0.10
        actual_spent = stats['openai_queries'] * 0.10
        savings = could_have_spent - actual_spent

    stats_msg = f"""
📊 *Usage Statistics*

*Today's Queries:*
• Ollama (free): {stats['ollama_queries']}
• Human guided (free): {stats['human_guided']}
• OpenAI (paid): {stats['openai_queries']}

*Cost Analysis:*
• Spent today: ${stats['cost_today']:.2f} (NT${stats['cost_today']*30:.0f})
• Saved: ${savings:.2f} (NT${savings*30:.0f}) ✅

*Efficiency:*
• Free queries: {stats['ollama_queries'] + stats['human_guided']} ({((stats['ollama_queries'] + stats['human_guided'])/total_queries*100 if total_queries > 0 else 0):.0f}%)
• Paid queries: {stats['openai_queries']} ({(stats['openai_queries']/total_queries*100 if total_queries > 0 else 0):.0f}%)
    """

    await update.message.reply_text(stats_msg, parse_mode='Markdown')


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Flyto2 status"""
    if not is_authorized(update):
        return

    await update.message.reply_text("📊 Loading quality status...")

    try:
        metrics_file = PROJECT_ROOT / "metrics" / "module_quality.json"
        with open(metrics_file) as f:
            metrics = json.load(f)

        summary = metrics.get('summary', {})

        status_msg = f"""
📊 *Flyto2 Quality Status*

*Modules:* {summary.get('total_modules', 0)}
• ≥98%: {summary.get('modules_above_98', 0)} ✅
• 95-98%: {summary.get('modules_95_to_98', 0)} ⚠️
• <95%: {summary.get('modules_below_95', 0)} 🚨

*Auto-merge approved:* {summary.get('auto_merge_approved_count', 0)}

*Updated:* {metrics.get('_last_updated', 'Unknown')}
        """

        await update.message.reply_text(status_msg, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


def main():
    """Start bot"""
    print("Starting Flyto2 Telegram Bot V2 (Ultra-Low-Cost)...")

    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not set")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("retry", retry_command))
    app.add_handler(CommandHandler("gpt", gpt_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot V2 started!")
    print(f"Strategy: Ollama → Human Guidance → OpenAI")
    print(f"Expected cost: ~NT$30-60/month")
    print("\nRunning... Press Ctrl+C to stop.")

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
