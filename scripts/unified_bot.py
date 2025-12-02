#!/usr/bin/env python3
"""
Unified Bot - Combines Autonomous Training + Chat Features

Features:
- Auto-training loop (background task)
- Full chat bot functionality (/lang, /gpt, /memory, etc.)
- All TG commands available while training runs
"""
import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_ALLOWED_USERS = os.getenv('TELEGRAM_ALLOWED_USERS', '').split(',')

from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Import all command handlers from telegram_bot_v2
import importlib.util
spec = importlib.util.spec_from_file_location("telegram_bot_v2", PROJECT_ROOT / "scripts" / "telegram_bot_v2.py")
bot_v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bot_v2)


async def auto_training_loop(bot: Bot):
    """Background task for autonomous training"""
    iteration = 0
    interval_minutes = int(os.getenv('TRAINING_INTERVAL_MINUTES', '60'))

    # Send startup message
    for user_id in TELEGRAM_ALLOWED_USERS:
        try:
            await bot.send_message(
                chat_id=int(user_id),
                text=(
                    "🤖 **Unified Bot Started!**\n\n"
                    "✅ Chat features active - try /start\n"
                    "✅ Auto-training in background\n\n"
                    f"Training interval: {interval_minutes} minutes\n"
                    "(Set TRAINING_INTERVAL_MINUTES in .env to change)"
                )
            )
        except Exception as e:
            print(f"Failed to send startup message: {e}")

    while True:
        iteration += 1

        for user_id in TELEGRAM_ALLOWED_USERS:
            try:
                await bot.send_message(
                    chat_id=int(user_id),
                    text=f"🔄 **Training Iteration #{iteration}**\n\n🤖 Initializing self-healing AI engine...\n⏳ This may take a few minutes..."
                )
            except:
                pass

        # 1. Run crawler practice with SELF-HEALING
        try:
            from src.core.training.self_healing_practice import SelfHealingPracticeEngine

            engine = SelfHealingPracticeEngine()

            test_sites = [
                "https://example.com",
                "https://books.toscrape.com",
                "https://httpbin.org/html"
            ]

            success_count = 0
            error_count = 0

            # Create notification callback
            async def notify_telegram(message: str):
                for user_id in TELEGRAM_ALLOWED_USERS:
                    try:
                        await bot.send_message(chat_id=int(user_id), text=message)
                    except:
                        pass

            for site in test_sites:
                await notify_telegram(f"🎯 **Analyzing**: {site}")

                # Use self-healing engine (will auto-fix errors!)
                result = await engine.analyze_website(site, notify_callback=notify_telegram)

                if result['errors']:
                    error_count += 1
                    msg = f"📊 **Final Status**: {site}\n⚠️ Still has errors after healing attempts\n"
                    for err in result['errors'][:2]:
                        msg += f"  • {err[:100]}...\n"
                else:
                    success_count += 1
                    msg = f"📊 **Final Status**: {site}\n✅ Success!\n"
                    if result.get('structure', {}).get('title'):
                        msg += f"  Title: {result['structure']['title'][:50]}\n"

                await notify_telegram(msg)

            # Summary
            summary_msg = f"\n📈 **Crawler Summary**\n✅ Success: {success_count}\n⚠️ Errors: {error_count}"
            if success_count > 0:
                summary_msg += f"\n\n🧠 **AI Agent Status**: Learning and evolving!"
            await notify_telegram(summary_msg)

        except Exception as e:
            for user_id in TELEGRAM_ALLOWED_USERS:
                try:
                    await bot.send_message(
                        chat_id=int(user_id),
                        text=f"❌ Training error: {str(e)}"
                    )
                except:
                    pass

        # 2. Run auto-evolution
        try:
            from src.core.evolution.auto_evolution_engine import AutoEvolutionEngine

            evolution = AutoEvolutionEngine()
            result = await evolution.run_evolution_cycle()

            msg = f"🧬 **Evolution Cycle #{result['cycle_id']}**\n\n"
            msg += f"Status: {result['status']}\n"

            if 'test_crawler' in result['steps']:
                test = result['steps']['test_crawler']
                msg += f"Tests: {test['passed']}/{test['total']}\n"

            for user_id in TELEGRAM_ALLOWED_USERS:
                try:
                    await bot.send_message(chat_id=int(user_id), text=msg)
                except:
                    pass

        except Exception as e:
            for user_id in TELEGRAM_ALLOWED_USERS:
                try:
                    await bot.send_message(
                        chat_id=int(user_id),
                        text=f"❌ Evolution error: {str(e)}"
                    )
                except:
                    pass

        # 3. Aggregate knowledge to vector DB
        try:
            import subprocess
            result = subprocess.run(
                ["python", "scripts/aggregate_project_knowledge.py"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                msg = "📚 **Knowledge Base Updated**\n\nAll learnings archived!"
                for user_id in TELEGRAM_ALLOWED_USERS:
                    try:
                        await bot.send_message(chat_id=int(user_id), text=msg)
                    except:
                        pass
        except Exception as e:
            print(f"Knowledge aggregation error: {e}")

        # Report completion
        interval_seconds = interval_minutes * 60
        for user_id in TELEGRAM_ALLOWED_USERS:
            try:
                await bot.send_message(
                    chat_id=int(user_id),
                    text=(
                        f"✅ **Iteration #{iteration} Complete!**\n\n"
                        f"Next training in {interval_minutes} minutes...\n"
                        f"Chat features still active!\n"
                        f"(Try /lang, /gpt, /memory, /status)"
                    )
                )
            except:
                pass

        # Wait for configured interval
        await asyncio.sleep(interval_seconds)


async def main():
    """Start unified bot with training + chat"""
    print("=" * 60)
    print("  UNIFIED BOT - Training + Chat")
    print("  All features in one bot!")
    print("=" * 60)
    print()

    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not set in .env")
        return

    # Create application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Import crawl command
    from pathlib import Path
    sys.path.insert(0, str(PROJECT_ROOT))

    async def crawl_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Execute crawling task with self-healing"""
        if str(update.effective_user.id) not in TELEGRAM_ALLOWED_USERS:
            return

        if not context.args:
            await update.message.reply_text(
                "Usage: /crawl <url>\n\n"
                "Example: /crawl https://www.amazon.com"
            )
            return

        url = context.args[0]

        from src.core.executor.smart_executor import SmartExecutor

        executor = SmartExecutor()

        # Callback for progress updates
        async def notify(message: str):
            try:
                await update.message.reply_text(message)
            except:
                pass

        # Execute task
        result = await executor.execute_task(f"crawl {url}", notify_callback=notify)

        # Send final summary
        if result["status"] == "success":
            summary = f"✅ **Task Completed**\n\n"
            if result["generated_modules"]:
                summary += f"🆕 Generated {len(result['generated_modules'])} new modules\n"
            summary += f"Attempts: {len(result['attempts'])}"
        else:
            summary = f"❌ **Task Failed**\n\nAttempts: {len(result['attempts'])}"

        await update.message.reply_text(summary)

    async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show leaderboard rankings"""
        if str(update.effective_user.id) not in TELEGRAM_ALLOWED_USERS:
            return

        from src.core.leaderboard import MetricsTracker

        tracker = MetricsTracker()

        # Determine which leaderboard to show
        board_type = context.args[0] if context.args else "accuracy"

        if board_type == "accuracy":
            leaderboard = tracker.get_accuracy_leaderboard(10)
            msg = "🎯 **Accuracy Leaderboard**\n\n"
            for i, metric in enumerate(leaderboard, 1):
                msg += f"{i}. `{metric.module_id}`\n"
                msg += f"   Overall: {metric.overall_accuracy:.1f}%\n"
                msg += f"   Completeness: {metric.data_completeness:.1f}% | "
                msg += f"Correctness: {metric.format_correctness:.1f}%\n"
                msg += f"   Runs: {metric.total_runs}\n\n"

        elif board_type == "stability":
            leaderboard = tracker.get_stability_leaderboard(10)
            msg = "⚡ **Stability Leaderboard**\n\n"
            for i, metric in enumerate(leaderboard, 1):
                msg += f"{i}. `{metric.module_id}`\n"
                msg += f"   Score: {metric.stability_score:.1f}\n"
                msg += f"   Max Streak: {metric.max_consecutive_successes}\n"
                msg += f"   Recovery: {metric.error_recovery_rate:.1f}%\n\n"

        elif board_type == "evolution":
            leaderboard = tracker.get_evolution_leaderboard(10)
            msg = "🧬 **Evolution Leaderboard**\n\n"
            for i, metric in enumerate(leaderboard, 1):
                msg += f"{i}. `{metric.module_id}`\n"
                msg += f"   Index: {metric.evolution_index:.1f}\n"
                msg += f"   Modules: +{metric.modules_added} | "
                msg += f"Bugs: {metric.bugs_fixed}\n"
                msg += f"   Coverage: +{metric.test_coverage_growth:.1f}%\n\n"

        else:
            msg = (
                "Usage: /leaderboard [type]\n\n"
                "Types:\n"
                "• `accuracy` - Top accuracy scores (default)\n"
                "• `stability` - Most stable modules\n"
                "• `evolution` - Fastest evolving modules\n\n"
                "Example: /leaderboard stability"
            )

        await update.message.reply_text(msg, parse_mode='Markdown')

    # Register all command handlers from telegram_bot_v2
    app.add_handler(CommandHandler("start", bot_v2.start))
    app.add_handler(CommandHandler("crawl", crawl_command))
    app.add_handler(CommandHandler("leaderboard", leaderboard_command))
    app.add_handler(CommandHandler("lang", bot_v2.lang_command))
    app.add_handler(CommandHandler("retry", bot_v2.retry_command))
    app.add_handler(CommandHandler("gpt", bot_v2.gpt_command))
    app.add_handler(CommandHandler("stats", bot_v2.stats_command))
    app.add_handler(CommandHandler("status", bot_v2.status_command))
    app.add_handler(CommandHandler("stress", bot_v2.stress_command))
    app.add_handler(CommandHandler("memory", bot_v2.memory_command))
    app.add_handler(CommandHandler("evolve", bot_v2.evolve_command))
    async def smart_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Smart handler that detects intent and routes to task or conversation"""
        if str(update.effective_user.id) not in TELEGRAM_ALLOWED_USERS:
            return

        message = update.message.text

        # Step 1: Detect intent
        from src.core.agent.intent_detector import IntentDetector
        detector = IntentDetector()
        intent = detector.detect(message)

        # Step 2: If task, execute with SmartExecutor
        if intent["type"] == "task" and intent["confidence"] >= 0.4:
            await update.message.reply_text(
                f"🎯 Detected task: {intent['task_type']}\n"
                f"Confidence: {intent['confidence']:.0%}\n\n"
                f"Executing..."
            )

            from src.core.executor.smart_executor import SmartExecutor
            executor = SmartExecutor()

            # Callback for progress updates
            async def notify(msg: str):
                try:
                    await update.message.reply_text(msg)
                except:
                    pass

            # Build task description
            if intent["params"].get("urls"):
                task_desc = f"{intent['task_type']} {intent['params']['urls'][0]}"
                if intent["params"].get("query"):
                    task_desc += f" search for {intent['params']['query']}"
            else:
                task_desc = message

            # Execute task with RAG and self-healing
            result = await executor.execute_task(task_desc, notify_callback=notify)

            # Store task result in session for context
            user_id = update.effective_user.id
            session = bot_v2.state.get_session(user_id)

            # Format result for context
            if result.get("final_result"):
                result_summary = f"Task: {task_desc}\n"
                result_summary += f"Status: {result['status']}\n"
                if result.get("final_result", {}).get("outputs"):
                    result_summary += f"Results: {str(result['final_result']['outputs'])[:500]}"
                session["last_task_result"] = result_summary

            # Add task execution to conversation history
            bot_v2.state.add_to_history(user_id, "user", message)
            bot_v2.state.add_to_history(user_id, "assistant", f"Executed task: {task_desc}\nResult: {result['status']}")

            # Send final summary
            if result["status"] == "success":
                summary = f"✅ **Task Completed**\n\n"
                if result["generated_modules"]:
                    summary += f"🆕 Generated {len(result['generated_modules'])} new modules\n"
                summary += f"Attempts: {len(result['attempts'])}"
            else:
                summary = f"❌ **Task Failed**\n\nAttempts: {len(result['attempts'])}"

            await update.message.reply_text(summary)

        else:
            # Step 3: If conversation, use Ollama chat (existing handler)
            await bot_v2.handle_message(update, context)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, smart_message_handler))

    # Start auto-training loop in background
    asyncio.create_task(auto_training_loop(app.bot))

    print("✅ Unified Bot started!")
    print("- Auto-training: Running in background")
    print("- Chat features: All active")
    print("- Commands: /start, /lang, /gpt, /memory, /status, etc.")
    print()
    print("Running... Press Ctrl+C to stop")
    print()

    # Run bot
    await app.initialize()
    await app.start()
    await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping unified bot...")
        for user_id in TELEGRAM_ALLOWED_USERS:
            try:
                await app.bot.send_message(
                    chat_id=int(user_id),
                    text="⏸️ **Bot stopped**\n\nRun START_BOT.bat to restart"
                )
            except:
                pass

    await app.updater.stop()
    await app.stop()
    await app.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
