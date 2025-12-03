#!/usr/bin/env python3
"""
Complete flow test - simulates full Telegram bot workflow
Tests: Message → Intent Detection → Workflow Generation → Execution → Result
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

async def test_complete_flow():
    """Test the complete flow from user message to result"""
    from src.core.executor.smart_executor import SmartExecutor

    # Test case: User asks to find and download dog images
    test_message = "幫我去網路上找狗狗圖片下載下來"

    print("=" * 80)
    print("🧪 COMPLETE FLOW TEST")
    print("=" * 80)
    print(f"\n📝 User Message: {test_message}\n")

    try:
        # Step 1: Create executor
        print("Step 1: Initializing SmartExecutor...")
        executor = SmartExecutor()
        executor.max_retries = 3
        print("✅ SmartExecutor initialized\n")

        # Step 2: Generate workflow
        print("Step 2: Generating workflow from user intent...")
        workflow = await executor._generate_workflow(test_message)
        print("✅ Workflow generated:")
        print(json.dumps(workflow, indent=2, ensure_ascii=False))
        print()

        # Step 3: Execute task
        print("Step 3: Executing task...")
        print("-" * 80)
        result = await executor.execute_task(
            task_description=test_message
        )
        print("-" * 80)
        print()

        # Step 4: Display results
        print("=" * 80)
        print("📊 EXECUTION RESULTS")
        print("=" * 80)
        print(f"Status: {result.get('status')}")
        print(f"Attempts: {result.get('attempts', 'N/A')}")
        print(f"Error: {result.get('error', 'None')}")

        if result.get('result'):
            print(f"\nResult Data:")
            print(json.dumps(result.get('result'), indent=2, ensure_ascii=False))

        # Step 5: Check if modules were generated
        if result.get('generated_modules'):
            print(f"\n🎉 New Modules Generated:")
            for mod in result['generated_modules']:
                print(f"  - {mod}")

        # Step 6: Check if PR was created
        if result.get('pr_url'):
            print(f"\n🔗 PR Created: {result['pr_url']}")

        print("\n" + "=" * 80)
        if result.get('status') == 'completed':
            print("✅ FLOW TEST PASSED")
        else:
            print("⚠️  FLOW TEST COMPLETED WITH ISSUES")
        print("=" * 80)

    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ FLOW TEST FAILED")
        print("=" * 80)
        print(f"Error: {str(e)}")
        print("\nFull traceback:")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = asyncio.run(test_complete_flow())
    sys.exit(0 if success else 1)
