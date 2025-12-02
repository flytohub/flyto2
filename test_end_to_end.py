#!/usr/bin/env python3
"""
端到端測試 - 測試整個系統是否真的能工作

測試場景: "爬蟲 google.com"
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_simple_crawl():
    """測試簡單的爬蟲任務"""
    print("=" * 60)
    print("端到端測試: 爬蟲 google.com")
    print("=" * 60)

    from src.core.executor.smart_executor import SmartExecutor

    executor = SmartExecutor()

    async def notify(msg):
        print(f"  {msg}")

    # 執行任務
    result = await executor.execute_task(
        task_description="爬蟲 google.com",
        notify_callback=notify
    )

    print("\n" + "=" * 60)
    print("結果:")
    print("=" * 60)
    print(f"Status: {result['status']}")
    print(f"Attempts: {len(result['attempts'])}")

    if result['status'] == 'success':
        print("✅ 成功！系統可以執行任務")
        return True
    else:
        print("❌ 失敗")
        print(f"Final result: {result['final_result']}")
        for i, attempt in enumerate(result['attempts'], 1):
            print(f"\nAttempt {i}:")
            print(f"  Error: {attempt.get('error', 'N/A')}")
        return False

async def test_intent_detection():
    """測試意圖檢測"""
    print("\n" + "=" * 60)
    print("測試意圖檢測")
    print("=" * 60)

    from src.core.agent.intent_detector import IntentDetector

    detector = IntentDetector()

    test_cases = [
        "爬蟲 google.com",
        "幫我爬蟲google 搜尋蝦皮 給我第二筆網站",
        "搜尋 amazon.com",
        "你好"
    ]

    for task in test_cases:
        result = detector.detect(task)
        print(f"\n輸入: {task}")
        print(f"  類型: {result['type']}")
        print(f"  信心: {result['confidence']:.0%}")
        if result.get('task_type'):
            print(f"  任務類型: {result['task_type']}")

async def test_workflow_engine():
    """測試 workflow 引擎"""
    print("\n" + "=" * 60)
    print("測試 Workflow 引擎")
    print("=" * 60)

    from src.core.engine.workflow_engine import WorkflowEngine

    # 簡單的字串處理 workflow
    workflow = {
        "workflow_name": "test_string",
        "steps": [
            {
                "step_id": "uppercase",
                "module": "string.uppercase",
                "params": {"text": "hello world"}
            }
        ]
    }

    engine = WorkflowEngine(workflow)
    result = await engine.execute()

    print(f"Status: {result['status']}")
    print(f"Result: {result['steps']['uppercase']['result']}")

    if result['status'] == 'completed':
        print("✅ Workflow 引擎工作正常")
        return True
    else:
        print("❌ Workflow 引擎失敗")
        return False

async def main():
    """執行所有測試"""
    print("\n🧪 Flyto2 端到端測試\n")

    results = {}

    # Test 1: Intent Detection
    try:
        await test_intent_detection()
        results['intent'] = True
    except Exception as e:
        print(f"❌ Intent detection failed: {e}")
        results['intent'] = False

    # Test 2: Workflow Engine
    try:
        results['workflow'] = await test_workflow_engine()
    except Exception as e:
        print(f"❌ Workflow engine failed: {e}")
        results['workflow'] = False

    # Test 3: Full crawl (may fail if Playwright not installed)
    try:
        results['crawl'] = await test_simple_crawl()
    except Exception as e:
        print(f"❌ Crawl test failed: {e}")
        import traceback
        traceback.print_exc()
        results['crawl'] = False

    # Summary
    print("\n" + "=" * 60)
    print("測試總結")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {test_name}")

    total = len(results)
    passed = sum(results.values())
    print(f"\n通過: {passed}/{total}")

    return all(results.values())

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
