#!/usr/bin/env python3
"""
BOT Zero-Assistance Test
全程零輔助：任務 → 模組生成 → 自動優化 → GitHub PR

目標：證明 BOT 可以完全自主完成從任務到高質量代碼的全流程
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# 添加項目根目錄到路徑
sys.path.insert(0, str(Path(__file__).parent))

from src.core.executor.smart_executor import SmartExecutor


async def main():
    """BOT 零輔助完整流程"""

    print("="*80)
    print("🤖 BOT 零輔助測試：從任務到 GitHub PR")
    print("="*80)
    print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("目標品質: 9.0+/10.0")
    print("人工干預: 0 次")
    print("="*80)
    print()

    # 任務描述
    task = "從網路上找一張小狗圖片，下載到本地，然後轉換成 SVG 格式"

    print(f"📝 任務: {task}")
    print()

    # 檢查 API Key
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ 錯誤: 未設置 OPENAI_API_KEY 環境變量")
        print("請執行: export OPENAI_API_KEY='your-key-here'")
        return False

    try:
        # Step 1: SmartExecutor 自主執行
        print("🚀 Step 1: SmartExecutor 開始自主執行")
        print("-"*80)

        executor = SmartExecutor()

        result = await executor.execute_task(
            task_description=task
        )

        # 檢查結果
        status = result.get("status")
        print()
        print(f"📊 執行結果: {status}")

        if status != "success":
            print("❌ SmartExecutor 執行失敗")
            print(f"狀態: {status}")
            if result.get("attempts"):
                print(f"嘗試次數: {len(result['attempts'])}")
            return False

        # 顯示生成的模組
        generated_modules = result.get("generated_modules", [])
        print(f"✅ 成功生成 {len(generated_modules)} 個模組:")
        print()

        for i, mod in enumerate(generated_modules, 1):
            mod_name = mod.get("module_name", "Unknown")
            mod_path = mod.get("module_path", "")
            print(f"  {i}. {mod_name}")
            if mod_path:
                print(f"     路徑: {mod_path}")

            # 如果有品質分數，顯示
            if "quality_score" in mod:
                score = mod["quality_score"]
                print(f"     品質分數: {score:.2f}/10.0")

        print()
        print("="*80)
        print("✅ BOT 零輔助測試完成")
        print("="*80)

        # 統計
        elapsed = (datetime.now() - datetime.now()).total_seconds()
        print(f"生成模組數量: {len(generated_modules)}")
        print(f"執行狀態: {status}")
        print(f"結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        return True

    except Exception as e:
        print()
        print(f"❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    start_time = datetime.now()

    success = asyncio.run(main())

    elapsed = (datetime.now() - start_time).total_seconds()

    print()
    print(f"⏱️  總耗時: {elapsed:.1f} 秒")
    print()

    sys.exit(0 if success else 1)
