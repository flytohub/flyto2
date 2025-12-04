#!/usr/bin/env python3
"""
BOT Test with Automatic Module Fixing
測試每個生成的模組並自動修復問題
"""

import asyncio
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import openai

# 添加項目根目錄到路徑
sys.path.insert(0, str(Path(__file__).parent))


async def test_module(module_name: str) -> Dict[str, Any]:
    """
    測試指定的模組

    Returns:
        {
            "passed": bool,
            "error": str or None,
            "output": str
        }
    """
    test_file = Path(f"workflows/_test/test_{module_name.replace('.', '_')}.yaml")

    if not test_file.exists():
        return {
            "passed": False,
            "error": f"Test file not found: {test_file}",
            "output": ""
        }

    # 運行測試
    cmd = ["python3", "-m", "src.cli.main", str(test_file)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    passed = result.returncode == 0

    return {
        "passed": passed,
        "error": None if passed else result.stderr or result.stdout,
        "output": result.stdout
    }


async def fix_module_with_ai(module_name: str, module_path: Path, error: str, openai_api_key: str) -> bool:
    """
    用 AI 分析錯誤並修復模組

    Returns:
        True if fixed successfully, False otherwise
    """
    print(f"🔧 使用 AI 修復模組: {module_name}")

    # 讀取當前代碼
    if not module_path.exists():
        print(f"❌ 模組文件不存在: {module_path}")
        return False

    current_code = module_path.read_text()

    # 構建 AI prompt
    prompt = f"""你是一個 Python 代碼修復專家。以下模組測試失敗了，請修復它。

模組名稱: {module_name}
錯誤信息:
{error}

當前代碼:
```python
{current_code}
```

CRITICAL RULES:
1. 必須使用統一返回格式: {{"ok": bool, "output": {{}}, "error": None/Dict, "meta": {{}}}}
2. 絕對不能使用 {{"status": "..."}} 格式
3. 成功時: {{"ok": True, "output": {{...}}, "error": None, "meta": {{}}}}
4. 失敗時: {{"ok": False, "output": {{}}, "error": {{"message": "..."}}, "meta": {{}}}}
5. 確保所有 import 語句都在文件頂部
6. 檢查縮進是否正確
7. 檢查是否有語法錯誤

請輸出修復後的完整代碼（不要包含 markdown 標記）:
"""

    client = openai.OpenAI(api_key=openai_api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a Python code fixing expert. Output only valid Python code without markdown code blocks."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        fixed_code = response.choices[0].message.content.strip()

        # 移除可能的 markdown 標記
        if fixed_code.startswith("```python"):
            fixed_code = fixed_code.split("```python", 1)[1]
        if fixed_code.startswith("```"):
            fixed_code = fixed_code.split("```", 1)[1]
        if fixed_code.endswith("```"):
            fixed_code = fixed_code.rsplit("```", 1)[0]

        fixed_code = fixed_code.strip()

        # 寫回文件
        module_path.write_text(fixed_code)
        print(f"✅ 已更新模組代碼")

        return True

    except Exception as e:
        print(f"❌ AI 修復失敗: {e}")
        return False


async def test_and_fix_module(module_name: str, module_path: Path, openai_api_key: str, max_retries: int = 3) -> Dict[str, Any]:
    """
    測試模組，如果失敗則修復，最多重試 max_retries 次

    Returns:
        {
            "module_name": str,
            "passed": bool,
            "attempts": int,
            "final_error": str or None
        }
    """
    print()
    print(f"{'='*80}")
    print(f"🧪 測試模組: {module_name}")
    print(f"{'='*80}")

    for attempt in range(1, max_retries + 1):
        print(f"\n嘗試 #{attempt}/{max_retries}")

        # 測試模組
        test_result = await test_module(module_name)

        if test_result["passed"]:
            print(f"✅ 測試通過!")
            return {
                "module_name": module_name,
                "passed": True,
                "attempts": attempt,
                "final_error": None
            }

        print(f"❌ 測試失敗")
        print(f"錯誤: {test_result['error'][:200]}...")  # 只顯示前200字符

        if attempt < max_retries:
            # 嘗試修復
            fixed = await fix_module_with_ai(
                module_name=module_name,
                module_path=module_path,
                error=test_result["error"],
                openai_api_key=openai_api_key
            )

            if not fixed:
                print(f"⚠️  AI 修復失敗，繼續下一次嘗試...")
        else:
            print(f"❌ 達到最大重試次數 ({max_retries})")

    return {
        "module_name": module_name,
        "passed": False,
        "attempts": max_retries,
        "final_error": test_result["error"]
    }


async def main():
    """主測試流程"""

    print("="*80)
    print("🤖 BOT 測試：逐個模組測試並自動修復")
    print("="*80)
    print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print()

    # 檢查 API Key
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ 錯誤: 未設置 OPENAI_API_KEY 環境變量")
        return False

    # 要測試的模組列表（從 src/core/modules/atomic/image/ 目錄找到）
    modules_to_test = [
        {
            "name": "image.download",
            "path": Path("src/core/modules/atomic/image/download.py")
        },
        {
            "name": "image.svg_convert",
            "path": Path("src/core/modules/atomic/image/svg_convert.py")
        }
    ]

    # 過濾掉不存在的模組
    existing_modules = []
    for mod in modules_to_test:
        if mod["path"].exists():
            existing_modules.append(mod)
        else:
            print(f"⚠️  跳過不存在的模組: {mod['name']} (path: {mod['path']})")

    if not existing_modules:
        print("❌ 沒有找到任何模組可以測試")
        return False

    print(f"📦 找到 {len(existing_modules)} 個模組需要測試")
    for mod in existing_modules:
        print(f"  - {mod['name']}")
    print()

    # 測試每個模組
    results = []
    for mod in existing_modules:
        result = await test_and_fix_module(
            module_name=mod["name"],
            module_path=mod["path"],
            openai_api_key=openai_key,
            max_retries=3
        )
        results.append(result)

    # 總結
    print()
    print("="*80)
    print("📊 測試總結")
    print("="*80)

    passed_count = sum(1 for r in results if r["passed"])
    failed_count = len(results) - passed_count

    print(f"總模組數: {len(results)}")
    print(f"✅ 通過: {passed_count}")
    print(f"❌ 失敗: {failed_count}")
    print()

    for result in results:
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"{status} {result['module_name']} (嘗試次數: {result['attempts']})")
        if result["final_error"]:
            print(f"     錯誤: {result['final_error'][:100]}...")

    print()
    print("="*80)

    return failed_count == 0


if __name__ == "__main__":
    start_time = datetime.now()

    success = asyncio.run(main())

    elapsed = (datetime.now() - start_time).total_seconds()

    print()
    print(f"⏱️  總耗時: {elapsed:.1f} 秒")
    print()

    sys.exit(0 if success else 1)
