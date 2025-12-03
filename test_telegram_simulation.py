#!/usr/bin/env python3
"""
Direct test of Telegram bot message handling
Simulates what happens when user sends a message via Telegram
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

async def test_task_execution():
    """Test the exact flow that happens in Telegram bot"""
    from src.core.executor.smart_executor import SmartExecutor
    import json

    # This is the exact message user sent in Telegram
    message_text = "幫我去網路上找狗狗圖片下載下來 轉檔案svg"

    print(f"Testing message: {message_text}")
    print("=" * 60)

    try:
        # Create executor (same as in Telegram bot)
        executor = SmartExecutor()
        executor.max_retries = 2

        # First, let's see what workflow is generated
        print("\n🔍 Generating workflow...")
        workflow = await executor._generate_workflow(message_text)

        print("\n📋 Generated Workflow:")
        print("=" * 60)
        print(json.dumps(workflow, indent=2, ensure_ascii=False))
        print("=" * 60)

        # Execute task (same as in Telegram bot)
        result = await executor.execute_task(
            task_description=message_text
        )

        print("\n" + "=" * 60)
        print("✅ TASK EXECUTION SUCCESS!")
        print("=" * 60)
        print(f"Status: {result.get('status')}")
        print(f"Result: {result.get('result')}")
        print(f"Attempts: {result.get('attempts')}")

    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ TASK EXECUTION FAILED!")
        print("=" * 60)
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")

        # Print full traceback
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_task_execution())
