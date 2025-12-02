#!/usr/bin/env python3
"""
Fully Autonomous Self-Evolving AI Bot
Starts automatically and never stops learning!

Features:
- Auto-starts training on startup
- Continuous evolution loop (every hour)
- Auto-explores vector database
- Auto-practices on websites
- Auto-generates missing modules
- Reports everything to Telegram
"""
import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_ALLOWED_USERS = os.getenv('TELEGRAM_ALLOWED_USERS', '').split(',')

from telegram import Bot
from telegram.ext import Application


async def send_startup_message(bot: Bot):
    """Send startup notification"""
    for user_id in TELEGRAM_ALLOWED_USERS:
        try:
            await bot.send_message(
                chat_id=int(user_id),
                text=(
                    "🤖 **Autonomous AI Started!**\n\n"
                    "I'm now running on autopilot:\n\n"
                    "✅ Auto-training every hour\n"
                    "✅ Auto-evolution loops\n"
                    "✅ Auto-exploring knowledge base\n"
                    "✅ Auto-generating missing modules\n\n"
                    "I'll notify you of all discoveries and improvements!\n\n"
                    "Starting first training session..."
                )
            )
        except Exception as e:
            print(f"Failed to send startup message: {e}")


async def auto_training_loop(bot: Bot):
    """Continuous training loop"""
    iteration = 0

    while True:
        iteration += 1

        for user_id in TELEGRAM_ALLOWED_USERS:
            try:
                await bot.send_message(
                    chat_id=int(user_id),
                    text=f"🔄 **Training Iteration #{iteration}**\n\nStarting..."
                )
            except:
                pass

        # 1. Run crawler practice
        try:
            from src.core.training.daily_practice import DailyPracticeEngine

            engine = DailyPracticeEngine()

            test_sites = [
                "https://example.com",
                "https://books.toscrape.com",
                "https://httpbin.org/html"
            ]

            success_count = 0
            error_count = 0

            for site in test_sites:
                result = await engine.analyze_website(site)

                if result['errors']:
                    error_count += 1
                    msg = f"📊 **Analyzed**: {site}\n⚠️ Errors:\n"
                    for err in result['errors'][:2]:  # Show first 2 errors
                        msg += f"  • {err}\n"
                else:
                    success_count += 1
                    msg = f"📊 **Analyzed**: {site}\n✅ Success!\n"
                    if result.get('structure', {}).get('title'):
                        msg += f"  Title: {result['structure']['title'][:50]}\n"

                for user_id in TELEGRAM_ALLOWED_USERS:
                    try:
                        await bot.send_message(chat_id=int(user_id), text=msg)
                    except:
                        pass

            # Summary
            summary_msg = f"\n📈 **Crawler Summary**\n✅ Success: {success_count}\n⚠️ Errors: {error_count}"
            for user_id in TELEGRAM_ALLOWED_USERS:
                try:
                    await bot.send_message(chat_id=int(user_id), text=summary_msg)
                except:
                    pass

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
        # Configurable interval (default: 1 hour)
        interval_minutes = int(os.getenv('TRAINING_INTERVAL_MINUTES', '60'))
        interval_seconds = interval_minutes * 60

        for user_id in TELEGRAM_ALLOWED_USERS:
            try:
                await bot.send_message(
                    chat_id=int(user_id),
                    text=(
                        f"✅ **Iteration #{iteration} Complete!**\n\n"
                        f"Next training in {interval_minutes} minutes...\n"
                        f"(Set TRAINING_INTERVAL_MINUTES in .env to change)\n"
                        f"(Send /stop to pause autonomous mode)"
                    )
                )
            except:
                pass

        # Wait for configured interval
        await asyncio.sleep(interval_seconds)


async def main():
    """Main autonomous bot"""
    print("=" * 60)
    print("  AUTONOMOUS SELF-EVOLVING AI")
    print("  Fully automated - never stops learning!")
    print("=" * 60)
    print()

    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not set in .env")
        return

    # Create bot
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    bot = app.bot

    # Send startup message
    await send_startup_message(bot)

    # Start autonomous loop
    print("🤖 Autonomous mode activated!")
    print("Bot will train, evolve, and learn continuously...")
    print("Press Ctrl+C to stop")
    print()

    try:
        await auto_training_loop(bot)
    except KeyboardInterrupt:
        print("\n\nStopping autonomous mode...")

        for user_id in TELEGRAM_ALLOWED_USERS:
            try:
                await bot.send_message(
                    chat_id=int(user_id),
                    text="⏸️ **Autonomous mode stopped**\n\nI'll wait for your commands."
                )
            except:
                pass


if __name__ == '__main__':
    asyncio.run(main())
