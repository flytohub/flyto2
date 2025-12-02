#!/bin/bash
# 啟動完美流程 Telegram Bot

echo "🤖 啟動 Flyto2 完美流程機器人"
echo ""

# 檢查環境變量
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ 錯誤: 請設置 TELEGRAM_BOT_TOKEN 環境變量"
    echo ""
    echo "設置方法:"
    echo "  export TELEGRAM_BOT_TOKEN=your_telegram_bot_token"
    echo ""
    echo "取得 token:"
    echo "  1. 在 Telegram 搜尋 @BotFather"
    echo "  2. 發送 /newbot 創建新機器人"
    echo "  3. 複製 token"
    exit 1
fi

# 檢查 Python 依賴
echo "📦 檢查依賴..."
python3 -c "import telegram" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 缺少 python-telegram-bot"
    echo "安裝: pip install python-telegram-bot"
    exit 1
fi

echo "✅ 依賴檢查完成"
echo ""

# 啟動機器人
echo "🚀 啟動機器人..."
echo "按 Ctrl+C 停止"
echo ""

cd "$(dirname "$0")"
python3 scripts/telegram_bot_perfect.py
