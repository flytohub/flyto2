#!/usr/bin/env python3
"""
完整自動進化流程測試 - SVG 轉換任務
模擬 Telegram 用戶輸入，展示：
1. 任務理解
2. 檢測缺失模組 (image.svg_convert)
3. 自動生成模組 (@register_module)
4. 測試模組
5. 創建 Git branch + commit
6. 創建 PR (如果 gh 已認證)
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

async def test_full_auto_evolution():
    """測試完整的自動進化流程"""
    from src.core.executor.smart_executor import SmartExecutor

    # 模擬 Telegram 用戶輸入
    user_message = "下載一張狗的圖片並轉換成 SVG 格式"

    print("=" * 80)
    print("🤖 FLYTO2 AUTO-EVOLUTION TEST")
    print("=" * 80)
    print(f"\n👤 User Input (Telegram): {user_message}\n")
    print("Expected Flow:")
    print("  1. ✅ Understand task")
    print("  2. 🔍 Detect missing module: image.svg_convert")
    print("  3. 🤖 AI generates module code (with @register_module)")
    print("  4. ✅ Quality validation (10/10 checks)")
    print("  5. 📝 Write module file")
    print("  6. 🌿 Git: create branch + commit + push")
    print("  7. 🔗 Create GitHub PR")
    print("\n" + "=" * 80)
    print("⏳ Starting execution...\n")

    executor = SmartExecutor()
    executor.max_retries = 3

    try:
        result = await executor.execute_task(
            task_description=user_message
        )

        print("\n" + "=" * 80)
        print("📊 EXECUTION RESULTS")
        print("=" * 80)
        print(f"Status: {result.get('status')}")
        print(f"Attempts: {len(result.get('attempts', []))}")

        if result.get('generated_modules'):
            print(f"\n🎉 NEW MODULES GENERATED:")
            for module in result['generated_modules']:
                print(f"  - {module.get('name')}")
                print(f"    Status: {module.get('status')}")
                if module.get('module_path'):
                    print(f"    Path: {module.get('module_path')}")
                if module.get('pr_url'):
                    print(f"    PR: {module.get('pr_url')}")
        else:
            print("\n⚠️  No modules were generated")

        if result.get('error'):
            print(f"\n❌ Error: {result['error']}")

        return result.get('status') == 'success'

    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ TEST FAILED")
        print("=" * 80)
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_full_auto_evolution())
    sys.exit(0 if success else 1)
