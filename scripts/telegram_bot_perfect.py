#!/usr/bin/env python3
"""
Telegram Bot - 完美流程實現

用戶流程:
1. TG 輸入任務 → 機器人接收
2. 機器人思考 → 決定組成什麼 YAML
3. 生成 YAML → 測試執行
4. 如果失敗 → 想辦法解決
5. 提問用戶 → TG 顯示選項:
   - 讓我（用戶）解決
   - 讓機器人自己解決
   - 問 OpenAI
6. 繼續測試 → 直到成功
7. 發 PR → 用戶驗證
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
ALLOWED_USERS = os.getenv("TELEGRAM_ALLOWED_USERS", "").split(",")

# Import our modules
from src.core.agent.intent_detector import IntentDetector
from src.core.utils.http_client import HTTPClient
from src.core.engine.workflow_engine import WorkflowEngine


class PerfectBot:
    """完美流程機器人"""

    def __init__(self):
        self.intent_detector = IntentDetector()
        self.active_tasks = {}  # user_id -> task_state

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """啟動命令"""
        await update.message.reply_text(
            "🤖 Flyto2 完美流程機器人\n\n"
            "直接輸入任務，例如:\n"
            "- 爬蟲 google.com\n"
            "- 幫我爬蟲google 搜尋蝦皮 給我第二筆網站\n\n"
            "我會:\n"
            "1. 理解你的任務\n"
            "2. 生成 YAML workflow\n"
            "3. 測試執行\n"
            "4. 如果失敗，問你要怎麼解決\n"
            "5. 繼續測試直到成功\n"
            "6. 發 PR 給你驗證"
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """處理用戶訊息"""
        user_id = update.effective_user.id
        message = update.message.text

        # 檢查權限
        if str(user_id) not in ALLOWED_USERS and ALLOWED_USERS[0] != "":
            await update.message.reply_text("❌ 你沒有權限使用此機器人")
            return

        await update.message.reply_text("🤔 收到任務，正在思考...")

        # Step 1: 意圖檢測
        intent = self.intent_detector.detect(message)

        if intent['type'] == 'conversation':
            await update.message.reply_text("💬 這看起來是對話，不是任務。請描述具體的任務。")
            return

        await update.message.reply_text(
            f"✅ 理解任務\n"
            f"類型: {intent['task_type']}\n"
            f"信心: {intent['confidence']:.0%}"
        )

        # Step 2: 生成 YAML workflow
        await update.message.reply_text("📝 正在生成 YAML workflow...")

        workflow = await self.generate_workflow(message, update)

        if not workflow:
            await update.message.reply_text("❌ 無法生成 workflow")
            return

        # 保存任務狀態
        task_state = {
            "original_message": message,
            "intent": intent,
            "workflow": workflow,
            "attempt": 1,
            "max_attempts": 3
        }
        self.active_tasks[user_id] = task_state

        # Step 3: 測試執行
        await self.test_workflow(update, context, task_state)

    async def generate_workflow(self, task_description: str, update: Update) -> Optional[Dict[str, Any]]:
        """生成 YAML workflow"""

        system_prompt = """你是 Flyto2 workflow 生成器。根據用戶任務生成 YAML 格式的 workflow。

可用模組:
- browser.launch: 啟動瀏覽器
- browser.goto: 訪問網址 (params: url)
- browser.extract: 提取數據 (params: fields)
- browser.close: 關閉瀏覽器
- string.uppercase/lowercase: 字串轉換

返回 JSON 格式:
{
  "workflow_name": "任務名稱",
  "steps": [
    {"step_id": "唯一ID", "module": "模組名", "params": {...}}
  ]
}

例如 "爬蟲 google.com":
{
  "workflow_name": "crawl_google",
  "steps": [
    {"step_id": "launch", "module": "browser.launch", "params": {"headless": true}},
    {"step_id": "goto", "module": "browser.goto", "params": {"url": "https://google.com"}},
    {"step_id": "extract", "module": "browser.extract", "params": {"fields": [{"name": "title", "selector": "title"}]}},
    {"step_id": "close", "module": "browser.close", "params": {}}
  ]
}"""

        try:
            response = await HTTPClient.ask_ollama(
                prompt=f"任務: {task_description}\n\n生成 workflow JSON:",
                system_prompt=system_prompt,
                timeout=60,
                extract_json=True
            )

            if response["success"] and response.get("structured"):
                workflow = response["structured"]

                # 顯示生成的 workflow
                yaml_preview = self.workflow_to_yaml(workflow)
                await update.message.reply_text(
                    f"✅ 生成 workflow:\n\n```yaml\n{yaml_preview[:500]}\n```",
                    parse_mode="Markdown"
                )

                return workflow
            else:
                await update.message.reply_text(f"❌ AI 生成失敗: {response.get('error')}")
                return None

        except Exception as e:
            await update.message.reply_text(f"❌ 生成錯誤: {e}")
            return None

    async def test_workflow(self, update: Update, context: ContextTypes.DEFAULT_TYPE, task_state: Dict):
        """測試執行 workflow"""
        user_id = update.effective_user.id
        workflow = task_state["workflow"]
        attempt = task_state["attempt"]

        await update.message.reply_text(f"🧪 測試執行 (嘗試 {attempt}/{task_state['max_attempts']})...")

        try:
            engine = WorkflowEngine(workflow)
            result = await engine.execute()

            if result['status'] == 'completed':
                # 成功！
                await update.message.reply_text(
                    f"✅ 測試成功！\n\n"
                    f"結果:\n{json.dumps(result.get('output', {}), indent=2, ensure_ascii=False)[:500]}"
                )

                # 詢問是否發 PR
                keyboard = [
                    [InlineKeyboardButton("發 PR 給我驗證", callback_data=f"pr_{user_id}")],
                    [InlineKeyboardButton("直接使用", callback_data=f"use_{user_id}")]
                ]
                await update.message.reply_text(
                    "🎉 Workflow 測試成功！接下來要做什麼？",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )

                return
            else:
                # 失敗，詢問如何處理
                error_msg = result.get('error', '未知錯誤')
                await self.handle_failure(update, context, task_state, error_msg)

        except Exception as e:
            await self.handle_failure(update, context, task_state, str(e))

    async def handle_failure(self, update: Update, context: ContextTypes.DEFAULT_TYPE, task_state: Dict, error: str):
        """處理執行失敗"""
        user_id = update.effective_user.id

        await update.message.reply_text(f"❌ 執行失敗:\n{error[:300]}")

        # 如果還有重試次數
        if task_state["attempt"] < task_state["max_attempts"]:
            # 顯示選項
            keyboard = [
                [InlineKeyboardButton("🙋 讓我來解決", callback_data=f"manual_{user_id}")],
                [InlineKeyboardButton("🤖 讓機器人解決", callback_data=f"auto_{user_id}")],
                [InlineKeyboardButton("💰 問 OpenAI ($)", callback_data=f"openai_{user_id}")]
            ]

            await update.message.reply_text(
                "🤔 要怎麼解決這個問題？",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text(
                f"❌ 已達最大嘗試次數 ({task_state['max_attempts']})，任務失敗"
            )
            if user_id in self.active_tasks:
                del self.active_tasks[user_id]

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """處理按鈕回調"""
        query = update.callback_query
        await query.answer()

        data = query.data
        user_id = update.effective_user.id

        if data.startswith("manual_"):
            await query.edit_message_text("📝 請告訴我怎麼修復，或輸入新的 workflow")

        elif data.startswith("auto_"):
            await query.edit_message_text("🤖 讓機器人自己想辦法...")

            # 使用 AI Error Solver
            task_state = self.active_tasks.get(user_id)
            if task_state:
                await self.auto_solve(update, context, task_state)

        elif data.startswith("openai_"):
            await query.edit_message_text("💰 詢問 OpenAI...")

            task_state = self.active_tasks.get(user_id)
            if task_state:
                await self.solve_with_openai(update, context, task_state)

        elif data.startswith("pr_"):
            await query.edit_message_text("📋 發送 PR 請求...")
            await self.create_pr(update, context)

        elif data.startswith("use_"):
            await query.edit_message_text("✅ Workflow 已保存，可以直接使用")

    async def auto_solve(self, update: Update, context: ContextTypes.DEFAULT_TYPE, task_state: Dict):
        """自動解決問題（使用 AI Error Solver）"""
        try:
            from src.core.healing.ai_error_solver import AIErrorSolver

            solver = AIErrorSolver()

            # 模擬錯誤
            error = Exception("Workflow execution failed")
            error_context = {
                "task": task_state["original_message"],
                "workflow": task_state["workflow"],
                "attempt": task_state["attempt"]
            }

            # 通知回調
            async def notify(msg):
                try:
                    await update.callback_query.message.reply_text(msg)
                except:
                    pass

            result = await solver.solve_error(error, error_context, notify)

            if result.get("success"):
                # 重試
                task_state["attempt"] += 1
                await self.test_workflow(update, context, task_state)
            else:
                await update.callback_query.message.reply_text("❌ 自動解決失敗")

        except Exception as e:
            await update.callback_query.message.reply_text(f"❌ 自動解決錯誤: {e}")

    async def solve_with_openai(self, update: Update, context: ContextTypes.DEFAULT_TYPE, task_state: Dict):
        """使用 OpenAI 解決"""
        # TODO: 實現 OpenAI 解決方案
        await update.callback_query.message.reply_text("🚧 OpenAI 整合開發中...")

    async def create_pr(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """創建 Pull Request"""
        # TODO: 實現 PR 創建
        await update.callback_query.message.reply_text(
            "🚧 PR 功能開發中...\n\n"
            "將來會:\n"
            "1. 創建新分支\n"
            "2. 提交 workflow\n"
            "3. 推送到 GitHub\n"
            "4. 創建 PR 給你審核"
        )

    def workflow_to_yaml(self, workflow: Dict) -> str:
        """轉換 workflow 為 YAML 預覽"""
        yaml = f"workflow_name: {workflow.get('workflow_name', 'untitled')}\n"
        yaml += "steps:\n"
        for step in workflow.get('steps', []):
            yaml += f"  - step_id: {step.get('step_id')}\n"
            yaml += f"    module: {step.get('module')}\n"
            yaml += f"    params: {step.get('params', {})}\n"
        return yaml


async def main():
    """啟動機器人"""
    if not TELEGRAM_TOKEN:
        print("❌ 請設置 TELEGRAM_BOT_TOKEN 環境變量")
        return

    bot = PerfectBot()
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # 註冊處理器
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    app.add_handler(CallbackQueryHandler(bot.handle_callback))

    print("✅ Flyto2 完美流程機器人啟動")
    print(f"📊 允許用戶: {ALLOWED_USERS if ALLOWED_USERS[0] else '所有用戶'}")

    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
