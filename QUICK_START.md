# Quick Start - One-Click Bot Launch

## Windows: Super Easy Start 🚀

### Method 1: Double-Click (Easiest!)

1. **雙擊這個檔案：**
   ```
   START_BOT.bat
   ```

2. **跟著螢幕提示：**
   - 如果沒有 Ollama → 會問你要不要安裝
   - 如果沒有 .env → 會互動式問你：
     - Telegram Bot Token (從 @BotFather 拿)
     - Your User ID (從 @userinfobot 拿)
     - OpenAI Key (可選，按 Enter 跳過)

3. **完成！Bot 自動啟動**

### Method 2: PowerShell (Advanced)

```powershell
.\scripts\start_bot_windows.ps1
```

## 第一次使用？需要準備這些

### 1. Telegram Bot Token

**步驟：**
1. 打開 Telegram
2. 搜尋 `@BotFather`
3. 發送 `/newbot`
4. 跟著指示建立 bot
5. 複製 token (例：`7995397831:AAEVEF...`)

### 2. Your Telegram User ID

**步驟：**
1. 搜尋 `@userinfobot`
2. 發送 `/start`
3. 複製你的 ID (例：`123456789`)

### 3. OpenAI Key (選擇性)

**如果你想用 `/gpt` 指令：**
1. 去 https://platform.openai.com/api-keys
2. 建立新 key
3. 複製 (例：`sk-proj-...`)

**不想花錢？**
- 按 Enter 跳過
- 只用免費的 Ollama！

## 啟動後會發生什麼？

### 自動完成的事：

```
✓ 檢查 Python
✓ 檢查/啟動 Ollama
✓ 下載 llama3.2 模型（如果需要）
✓ 安裝 Python 套件
✓ 啟動 Bot
```

### 你會看到：

```
╔════════════════════════════════════════╗
║         Bot Starting...                ║
╚════════════════════════════════════════╝

Starting telegram_bot_v2.py...

✅ Bot V2 started!
Strategy: Ollama → Human Guidance → OpenAI
Expected cost: ~NT$30-60/month

Running... Press Ctrl+C to stop.
```

## 開始使用

### 在 Telegram 找到你的 Bot

1. 搜尋你的 bot 名稱（建立時設定的）
2. 或用這個連結格式：`t.me/YourBotName`

### 第一個對話

```
You: /start

Bot: 🤖 Flyto2 AI Assistant V2
     Ultra-Low-Cost Three-Tier Strategy

     Commands:
     • Just chat - I'll use Ollama
     • /gpt <q> - Force OpenAI ($)
     • /status - Quality status
     • /stats - Usage statistics

You: what's the current quality?

Bot: [Ollama ✓ 85%]
     All 21 modules at 100% pass rate ✅
```

## 常見問題

### Q: "Ollama not found"

**解法：**
1. 腳本會問你要不要安裝
2. 選 1 → 打開瀏覽器下載
3. 安裝完後重新執行 `START_BOT.bat`

### Q: "PowerShell execution policy error"

**解法：**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Q: Bot 不回應

**檢查：**
1. Bot 視窗有顯示 "Bot started" 嗎？
2. 你的 User ID 有在 .env 裡嗎？
3. 跟正確的 bot 說話了嗎？

### Q: 想更改設定

**方法 1：重新執行腳本**
```
START_BOT.bat
```
選 "y" 重新設定

**方法 2：手動編輯 .env**
```
notepad .env
```

## 成本說明

### 只用 Ollama（不設 OpenAI Key）

```
成本: NT$0/月 🎉
功能: 90% 的日常對話都能處理
```

### 混合模式（設定 OpenAI Key）

```
日常用 Ollama: 免費
特殊用 /gpt: ~NT$3/次
平均成本: NT$30-90/月

vs. 全 OpenAI: NT$2,430/月
省下: 96%！
```

## 關閉 Bot

按 `Ctrl+C` 在 Bot 視窗中

## 下次啟動

直接雙擊：
```
START_BOT.bat
```

所有設定都保存在 `.env`，不用重新輸入！

## 更多功能

查看完整文檔：
- **Bot 架構：** `docs/TELEGRAM_BOT_ARCHITECTURE.md`
- **使用指南：** `docs/TELEGRAM_BOT_SETUP.md`
- **Prompt 技巧：** `docs/PROMPT_GUIDE.md`

---

**超簡單版：**
1. 雙擊 `START_BOT.bat`
2. 輸入 Bot Token 和 User ID
3. 開始聊天！

**成本：免費（只用 Ollama）或 ~NT$50/月（偶爾用 OpenAI）**

🚀 Enjoy your AI assistant!
