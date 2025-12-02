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
                "conversation_history": [],  # Full conversation history with context
                "last_task_result": None,    # Result of last executed task
                "pending_question": None,    # Question waiting for guidance
                "ollama_attempt": None,      # Last Ollama response
                "language": "zh-TW",         # Default: Traditional Chinese
                "stats": {
                    "ollama_queries": 0,
                    "human_guided": 0,
                    "openai_queries": 0,
                    "cost_today": 0.0
                }
            }
        return self.sessions[user_id]

    def add_to_history(self, user_id: int, role: str, content: str):
        """Add message to conversation history"""
        session = self.get_session(user_id)
        session["conversation_history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

        # Keep last 20 messages for context
        if len(session["conversation_history"]) > 20:
            session["conversation_history"] = session["conversation_history"][-20:]

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


async def translate_to_english(text: str) -> str:
    """Translate text to English using Ollama (free)"""
    try:
        import requests

        messages = [
            {"role": "system", "content": "Translate the following text to English. Only output the translation, no explanations."},
            {"role": "user", "content": text}
        ]

        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": "llama3.2",
                "messages": messages,
                "stream": False
            },
            timeout=30
        )

        if response.status_code == 200:
            return response.json()['message']['content']
        else:
            return text  # Fallback: return original

    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Fallback: return original


async def store_conversation_to_vector_db(question: str, answer: str, source: str = "telegram_chat"):
    """
    Store conversation to vector database
    Translates to English before storing for consistency
    """
    try:
        import sys
        sys.path.insert(0, str(PROJECT_ROOT))

        from src.core.modules.atomic.vector import VectorDBConnector, KnowledgeStore

        # Translate both Q&A to English
        question_en = await translate_to_english(question)
        answer_en = await translate_to_english(answer)

        # Combine as Q&A pair
        content = f"Q: {question_en}\n\nA: {answer_en}"

        # Store in vector DB
        connector = VectorDBConnector(mode="local")
        connector.connect()

        store = KnowledgeStore(
            connector=connector,
            collection_name="flyto2_project_knowledge",
            embedding_provider="local"
        )

        store.add_entry(
            content=content,
            metadata={
                "source": source,
                "timestamp": datetime.now().isoformat(),
                "category": "telegram_conversation",
                "question_original": question[:200],  # Keep original for reference
                "answer_original": answer[:200]
            }
        )

        connector.disconnect()
        print(f"✅ Stored to vector DB: {question_en[:50]}...")

    except Exception as e:
        print(f"❌ Failed to store to vector DB: {e}")
        import traceback
        traceback.print_exc()


async def ask_ollama(prompt: str, system_prompt: str = None, language: str = "zh-TW", conversation_history: list = None) -> tuple[str, float]:
    """
    Ask Ollama and return (response, confidence)
    Confidence: 0.0-1.0 estimate based on response analysis
    """
    try:
        import requests

        # Language instruction mapping
        lang_instructions = {
            "zh-TW": "請用繁體中文回答。Be concise and clear.",
            "zh-CN": "请用简体中文回答。Be concise and clear.",
            "en": "Please reply in English. Be concise and clear.",
            "ja": "日本語で答えてください。Be concise and clear.",
            "ko": "한국어로 답변해주세요. Be concise and clear.",
        }

        lang_instruction = lang_instructions.get(language, lang_instructions["zh-TW"])

        # Combine system prompt with language instruction
        full_system_prompt = f"{system_prompt}\n\n{lang_instruction}" if system_prompt else lang_instruction

        messages = []
        messages.append({"role": "system", "content": full_system_prompt})

        # Add conversation history for context
        if conversation_history:
            for msg in conversation_history[-10:]:  # Last 10 messages
                messages.append({"role": msg["role"], "content": msg["content"]})

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

    user_id = update.effective_user.id
    session = state.get_session(user_id)
    current_lang = session.get("language", "zh-TW")

    lang_names = {
        "zh-TW": "繁體中文",
        "zh-CN": "简体中文",
        "en": "English",
        "ja": "日本語",
        "ko": "한국어"
    }

    welcome = f"""
🤖 *Flyto2 AI Assistant V2*
Ultra-Low-Cost Three-Tier Strategy

*How it works:*
1️⃣ I try with Ollama (free)
2️⃣ If unsure, I ask your guidance (free)
3️⃣ You can force OpenAI if needed (paid)

*Cost: ~NT$30-60/month* 💰

*Commands:*
• Just chat - I'll use Ollama
• `/crawl <url>` - Crawl a website (self-healing) 🕷️
• `/leaderboard [type]` - Rankings (accuracy/stability/evolution) 🏆
• `/lang` - Change reply language (Current: {lang_names[current_lang]}) 🌐
• `/gpt <q>` - Force OpenAI ($)
• `/retry` - Retry with OpenAI after my attempt
• `/status` - Flyto2 quality status
• `/stats` - Usage statistics
• `/stress` - Run stress test (100 concurrent ops) 🔥
• `/memory` - Vector DB memory management 🧠

*Auto-Storage:* All conversations → Vector DB (English) ✅

*Self-Healing Crawl:*
```
You: /crawl https://www.amazon.com
Bot: 🎯 Task: crawl amazon.com
     📝 Generating workflow...
     ▶️ Executing workflow...
     ❌ Error: Module not found
     📦 Generating missing module...
     🔄 Retrying...
     ✅ Task completed!
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
    language = session.get("language", "zh-TW")

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    # Add user message to history
    state.add_to_history(user_id, "user", message)

    # Check if this is guidance for a pending question
    if session["pending_question"]:
        # User is providing guidance
        await handle_guidance(update, context, message)
        return

    # Prepare context for Ollama with project knowledge
    system_prompt = """You are Flyto2 AI Agent - an intelligent web scraping and automation assistant.

**Your Capabilities**:
- Execute web crawling tasks automatically
- Browser automation (Playwright)
- Data extraction from websites
- Self-healing when encountering errors
- Learning from past experiences

**Architecture**:
- Atomic module system
- YAML-based workflows
- Vector database for knowledge storage
- Categories: browser, string, array, math, object, file, datetime, data

**Important**:
- When user asks to crawl/scrape a website, tell them you'll execute it for them
- Don't give general advice - you can actually do the task!
- Be concise and action-oriented
- Use your Chinese language skills when appropriate

Example:
User: "爬 amazon.com"
You: "好的！我现在帮你爬取 amazon.com。正在启动浏览器..."
(Then the system will execute the task automatically)
"""

    if session.get("last_task_result"):
        # Add task result to context
        system_prompt += f"\n\n**Previous Task Result**:\n{session['last_task_result']}"

    # Tier 1: Try Ollama first (with conversation history)
    answer, confidence = await ask_ollama(
        message,
        system_prompt=system_prompt,
        language=language,
        conversation_history=session["conversation_history"]
    )
    session['stats']['ollama_queries'] += 1

    # Add bot response to history
    state.add_to_history(user_id, "assistant", answer)

    # Store to vector DB (async, don't wait)
    import asyncio
    asyncio.create_task(store_conversation_to_vector_db(message, answer, source="telegram_ollama"))

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
    language = session.get("language", "zh-TW")

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

    answer, confidence = await ask_ollama(enhanced_prompt, language=language)
    session['stats']['human_guided'] += 1

    # Store to vector DB
    import asyncio
    asyncio.create_task(store_conversation_to_vector_db(original_question, answer, source="telegram_guided"))

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

    # Store to vector DB
    import asyncio
    asyncio.create_task(store_conversation_to_vector_db(question, answer, source="telegram_openai"))

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

    # Store to vector DB
    import asyncio
    asyncio.create_task(store_conversation_to_vector_db(question, answer, source="telegram_openai"))

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


async def stress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Run stress tests on the system
    Tests 100 concurrent operations with >= 95% success rate target
    """
    if not is_authorized(update):
        return

    await update.message.reply_text("🔥 Starting stress test...\n100 concurrent operations")

    try:
        import sys
        sys.path.insert(0, str(PROJECT_ROOT))

        from src.core.training.stress_test import StressTestEngine
        from src.core.engine.workflow_engine import WorkflowEngine

        async def run_operation(op_id, module_name, params):
            """Run a single operation"""
            workflow = {
                'workflow_name': f'stress_test_{op_id}',
                'steps': [{'step_id': f'op_{op_id}', 'module': module_name, 'params': params}]
            }
            engine = WorkflowEngine(workflow)
            result = await engine.execute()
            return result

        # Define operation templates
        operation_templates = [
            ('string.uppercase', {'text': 'test'}),
            ('string.lowercase', {'text': 'TEST'}),
            ('string.reverse', {'text': 'reverse'}),
            ('string.trim', {'text': '  trim  '}),
            ('math.abs', {'number': -42.5}),
            ('math.round', {'number': 3.14159, 'decimals': 2}),
            ('array.sort', {'array': [3, 1, 4, 2], 'order': 'asc'}),
            ('array.unique', {'array': [1, 1, 2, 2, 3]}),
            ('array.join', {'array': ['a', 'b', 'c'], 'separator': ','}),
            ('object.keys', {'object': {'key1': 1, 'key2': 2}}),
        ]

        # Create 100 operation params
        operation_params = []
        for i in range(100):
            module_name, base_params = operation_templates[i % len(operation_templates)]

            # Customize params for each iteration
            params = base_params.copy()
            if 'text' in params:
                params['text'] = f"{params['text']}_{i}"
            elif 'number' in params and module_name == 'math.abs':
                params['number'] = -i * 1.5
            elif 'array' in params and module_name == 'array.sort':
                params['array'] = [i, i+1, i+2, i+3]

            operation_params.append({
                'op_id': i,
                'module_name': module_name,
                'params': params
            })

        # Run stress test using StressTestEngine
        engine = StressTestEngine(min_success_rate=95.0)

        # Wrap run_operation to match expected signature
        async def operation_wrapper(op_id, module_name, params):
            return await run_operation(op_id, module_name, params)

        result = await engine.run_burst_test(
            operation=operation_wrapper,
            operation_params=operation_params,
            concurrency=100
        )

        # Generate report
        report = engine.generate_report(result)

        # Format for Telegram (limit message length)
        if len(report) > 4000:
            report_lines = report.split('\n')
            telegram_report = '\n'.join(report_lines[:30])
            telegram_report += f"\n... (truncated, total {len(report_lines)} lines)"
        else:
            telegram_report = report

        await update.message.reply_text(f"```\n{telegram_report}\n```", parse_mode='Markdown')

        # Also send summary
        summary = f"""
🔥 *Stress Test Complete*

*Results:*
• Total operations: {result.total}
• Successful: {result.successful}
• Failed: {result.failed}
• Success rate: {result.success_rate:.1f}%
• Duration: {result.duration:.2f}s
• Throughput: {result.ops_per_second:.1f} ops/sec

*Status:* {'✅ PASS' if engine.validate_result(result) else '❌ FAIL'}
        """
        await update.message.reply_text(summary, parse_mode='Markdown')

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        await update.message.reply_text(f"❌ Stress test failed:\n{str(e)}")
        print(f"Stress test error:\n{error_details}")


async def memory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Vector Database Memory Management
    Commands:
    - /memory search <query> - Search knowledge base
    - /memory stats - Show statistics
    - /memory recent [limit] - Show recent entries
    - /memory clear <days> - Clear old entries
    - /memory export - Export knowledge base
    - /memory help - Show this help
    """
    if not is_authorized(update):
        return

    import sys
    sys.path.insert(0, str(PROJECT_ROOT))

    from src.core.modules.atomic.vector import (
        VectorDBConnector,
        KnowledgeStore,
        KnowledgeManager,
        KnowledgeSearch
    )

    args = context.args

    if not args or args[0] == "help":
        help_msg = """
🧠 *Vector Database Memory Management*

*Commands:*
• `/memory search <query>` - Search knowledge base
• `/memory stats` - Show statistics
• `/memory recent [limit]` - Recent entries (default 10)
• `/memory clear <days>` - Clear entries older than N days
• `/memory export` - Export to JSON
• `/memory help` - Show this help

*Examples:*
• `/memory search browser error`
• `/memory recent 20`
• `/memory clear 90`
        """
        await update.message.reply_text(help_msg, parse_mode='Markdown')
        return

    command = args[0]

    try:
        # Connect to vector database
        connector = VectorDBConnector(mode="local")
        connector.connect()

        store = KnowledgeStore(
            connector=connector,
            collection_name="flyto2_project_knowledge",
            embedding_provider="local"
        )

        if command == "search":
            if len(args) < 2:
                await update.message.reply_text("Usage: /memory search <query>")
                return

            query = " ".join(args[1:])
            await update.message.reply_text(f"🔍 Searching for: *{query}*", parse_mode='Markdown')

            results = store.search(query, top_k=5)

            if not results:
                await update.message.reply_text("No results found.")
                connector.disconnect()
                return

            response = "📚 *Search Results:*\n\n"
            for i, result in enumerate(results, 1):
                content = result.get('content', '')[:200]  # First 200 chars
                score = result.get('score', 0)
                metadata = result.get('metadata', {})
                source = metadata.get('source', 'unknown')

                response += f"*{i}. [{source}]* (score: {score:.2f})\n"
                response += f"{content}...\n\n"

            await update.message.reply_text(response, parse_mode='Markdown')

        elif command == "stats":
            await update.message.reply_text("📊 Loading statistics...")

            manager = KnowledgeManager(store)
            stats = manager.get_statistics()

            stats_msg = f"""
📊 *Knowledge Base Statistics*

*Total Entries:* {stats.get('total_entries', 0)}

*By Category:*
"""
            categories = stats.get('categories', {})
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                stats_msg += f"• {cat}: {count}\n"

            stats_msg += f"\n*By Source:*\n"
            sources = stats.get('sources', {})
            for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True)[:10]:
                stats_msg += f"• {source}: {count}\n"

            stats_msg += f"""
*Avg Content Length:* {stats.get('avg_content_length', 0):.0f} chars

*Embedding:* {stats.get('embedding_provider', 'unknown')}
*Dimension:* {stats.get('vector_dimension', 0)}
*Collection:* {stats.get('collection', 'unknown')}
            """

            await update.message.reply_text(stats_msg, parse_mode='Markdown')

        elif command == "recent":
            limit = 10
            if len(args) >= 2 and args[1].isdigit():
                limit = int(args[1])
                limit = min(limit, 50)  # Max 50

            await update.message.reply_text(f"📋 Loading {limit} recent entries...")

            manager = KnowledgeManager(store)
            entries = manager.list_all(limit=limit)

            if not entries:
                await update.message.reply_text("No entries found.")
                connector.disconnect()
                return

            response = f"📋 *Recent {len(entries)} Entries:*\n\n"
            for i, entry in enumerate(entries[:limit], 1):
                content = entry.get('content', '')[:150]
                metadata = entry.get('metadata', {})
                source = metadata.get('source', 'unknown')
                timestamp = metadata.get('timestamp', '')[:10]  # Date only

                response += f"*{i}. [{source}]* {timestamp}\n"
                response += f"{content}...\n\n"

            await update.message.reply_text(response, parse_mode='Markdown')

        elif command == "clear":
            if len(args) < 2:
                await update.message.reply_text("Usage: /memory clear <days>\nExample: /memory clear 90")
                return

            days = int(args[1])
            await update.message.reply_text(f"🗑️ Clearing entries older than {days} days...")

            manager = KnowledgeManager(store)
            deleted = manager.delete_old_entries(days_old=days, dry_run=False)

            await update.message.reply_text(f"✅ Deleted {deleted} old entries (>{days} days)")

        elif command == "export":
            await update.message.reply_text("📦 Exporting knowledge base...")

            export_file = PROJECT_ROOT / "exports" / f"knowledge_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            export_file.parent.mkdir(exist_ok=True)

            manager = KnowledgeManager(store)
            exported = manager.export_entries(str(export_file), format="json")

            file_size = export_file.stat().st_size / 1024  # KB
            await update.message.reply_text(
                f"✅ Exported {exported} entries\n"
                f"File: `{export_file.name}`\n"
                f"Size: {file_size:.1f} KB",
                parse_mode='Markdown'
            )

        else:
            await update.message.reply_text(f"Unknown command: {command}\nUse /memory help")

        connector.disconnect()

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Change reply language preference"""
    if not is_authorized(update):
        return

    user_id = update.effective_user.id
    session = state.get_session(user_id)

    if not context.args:
        current_lang = session.get("language", "zh-TW")
        lang_names = {
            "zh-TW": "繁體中文 (Traditional Chinese)",
            "zh-CN": "简体中文 (Simplified Chinese)",
            "en": "English",
            "ja": "日本語 (Japanese)",
            "ko": "한국어 (Korean)"
        }

        help_msg = f"""
🌐 *Language Settings*

*Current Language:* {lang_names.get(current_lang, current_lang)}

*Available Languages:*
• `/lang zh-TW` - 繁體中文 (Traditional Chinese)
• `/lang zh-CN` - 简体中文 (Simplified Chinese)
• `/lang en` - English
• `/lang ja` - 日本語 (Japanese)
• `/lang ko` - 한국어 (Korean)

*Note:* All conversations are automatically stored in vector database (translated to English for consistency).
        """
        await update.message.reply_text(help_msg, parse_mode='Markdown')
        return

    new_lang = context.args[0]
    valid_langs = ["zh-TW", "zh-CN", "en", "ja", "ko"]

    if new_lang not in valid_langs:
        await update.message.reply_text(
            f"❌ Invalid language: {new_lang}\n"
            f"Valid options: {', '.join(valid_langs)}\n"
            f"Use `/lang` to see all options."
        )
        return

    session["language"] = new_lang

    lang_names = {
        "zh-TW": "繁體中文",
        "zh-CN": "简体中文",
        "en": "English",
        "ja": "日本語",
        "ko": "한국어"
    }

    await update.message.reply_text(
        f"✅ Language set to: *{lang_names[new_lang]}*\n\n"
        f"All future replies will be in {lang_names[new_lang]}.\n"
        f"(Conversations are still stored in English in vector DB)",
        parse_mode='Markdown'
    )


async def evolve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Run one auto-evolution cycle
    Tests crawler → Analyzes errors → Generates solutions → Creates PR
    """
    if not is_authorized(update):
        return

    await update.message.reply_text("🤖 Starting auto-evolution cycle...\nThis may take a few minutes.")

    try:
        import sys
        sys.path.insert(0, str(PROJECT_ROOT))

        from src.core.evolution.auto_evolution_engine import AutoEvolutionEngine

        engine = AutoEvolutionEngine()
        result = await engine.run_evolution_cycle()

        # Format results
        status_emoji = "✅" if result['status'] == 'completed' else "❌"

        msg = f"{status_emoji} Evolution Cycle #{result['cycle_id']}\n\n"

        # Test results
        if 'test_crawler' in result['steps']:
            test = result['steps']['test_crawler']
            msg += f"🔍 Crawler Tests: {test['passed']}/{test['total']}\n"

        # Error analysis
        if 'analyze_errors' in result['steps']:
            analysis = result['steps']['analyze_errors']
            msg += f"🔬 Missing Resources: {len(analysis['missing_resources'])}\n"

        # Solutions
        if 'generate_solutions' in result['steps']:
            solutions = result['steps']['generate_solutions']
            msg += f"💡 Solutions Generated: {solutions['count']}\n"

        # PR
        if 'create_pr' in result['steps']:
            pr = result['steps']['create_pr']
            if pr['success']:
                msg += f"🎯 Branch: {pr['branch']}\n"

        msg += f"\nStatus: {result['status']}"

        await update.message.reply_text(msg)

    except Exception as e:
        await update.message.reply_text(f"❌ Evolution failed: {str(e)}")
        print(f"Error in evolve_command: {e}")


def main():
    """Start bot"""
    print("Starting Flyto2 Telegram Bot V2 (Ultra-Low-Cost)...")

    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not set")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("lang", lang_command))
    app.add_handler(CommandHandler("retry", retry_command))
    app.add_handler(CommandHandler("gpt", gpt_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("stress", stress_command))
    app.add_handler(CommandHandler("memory", memory_command))
    app.add_handler(CommandHandler("evolve", evolve_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot V2 started!")
    print(f"Strategy: Ollama → Human Guidance → OpenAI")
    print(f"Expected cost: ~NT$30-60/month")
    print("\nRunning... Press Ctrl+C to stop.")

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
