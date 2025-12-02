# Flyto2 快速設置指南

## 步驟 1: 安裝依賴

```bash
# Windows
START_BOT.bat

# Mac/Linux
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 步驟 2: 配置環境變數

1. **複製範例配置文件**
   ```bash
   cp .env.example .env
   ```

2. **編輯 `.env` 文件，填入你的 Token**

### 必填項目

#### Telegram Bot Token
1. 打開 Telegram，搜尋 `@BotFather`
2. 發送 `/newbot` 創建新 bot
3. 按照指示設定 bot 名稱和 username
4. 複製你的 bot token，貼到 `.env` 文件：
   ```
   TELEGRAM_BOT_TOKEN=110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw
   ```

#### Telegram User ID
1. 打開 Telegram，搜尋 `@userinfobot`
2. 發送任何訊息，bot 會回覆你的 ID
3. 把 ID 貼到 `.env` 文件：
   ```
   TELEGRAM_ALLOWED_USERS=123456789
   ```
   多個用戶用逗號分隔：`123456789,987654321`

### 選填項目

#### OpenAI API Key（如果要使用 /gpt 指令）
1. 前往 https://platform.openai.com/api-keys
2. 登入並創建新 API key
3. 複製 key 貼到 `.env` 文件：
   ```
   OPENAI_API_KEY=sk-proj-abc123...
   ```

**注意**：沒有 OpenAI key 也能用！系統會用 Ollama（免費）處理 90% 的查詢

#### Ollama（免費 AI，建議安裝）
1. 下載 Ollama：https://ollama.ai/download
2. 安裝後執行：
   ```bash
   ollama pull llama3.2
   ```
3. 預設會在 `http://localhost:11434` 運行

## 步驟 3: 啟動系統

### 方式 1: 完全自動模式（推薦）
```bash
START_BOT.bat
```

**自動功能**：
- ✅ 每小時自動訓練（爬網站、測試元件）
- ✅ 自動進化循環（發現問題 → 生成解決方案）
- ✅ 自動更新知識庫（向量資料庫）
- ✅ 所有進度報告到 Telegram

### 方式 2: 只啟動 Telegram 聊天機器人
```bash
python scripts/telegram_bot_v2.py
```

**功能**：
- 💬 對話（Ollama → 人工引導 → OpenAI 三層策略）
- 🌐 語言選擇（`/lang`）
- 📊 查看狀態（`/status`）
- 🧠 向量資料庫管理（`/memory`）
- 🔥 壓力測試（`/stress`）

## Telegram Bot 指令

```
/start   - 查看說明
/lang    - 選擇回覆語言（繁中/簡中/英/日/韓）
/gpt     - 使用 OpenAI GPT-4（付費）
/retry   - 對不滿意的回答重試 OpenAI
/stats   - 查看使用統計和省下的費用
/status  - 查看系統品質狀態
/memory  - 向量資料庫管理
/stress  - 運行壓力測試
/evolve  - 手動觸發進化循環
```

## 費用說明

- **Ollama（免費）**：處理 90% 的查詢
- **人工引導（免費）**：當 Ollama 不確定時，你提供方向
- **OpenAI（付費）**：只在你批准時使用
  - 每次查詢約 NT$3-4.5（$0.10）
  - 預估月費：NT$30-60

## 故障排除

### Telegram bot 收不到訊息
1. 確認 `TELEGRAM_BOT_TOKEN` 正確
2. 確認 `TELEGRAM_ALLOWED_USERS` 是你的 user ID
3. 在 Telegram 發送 `/start` 給你的 bot

### Ollama 連不上
```bash
# 確認 Ollama 是否運行
curl http://localhost:11434/api/tags

# 如果沒反應，重新啟動 Ollama
ollama serve
```

### OpenAI 錯誤
1. 確認 `OPENAI_API_KEY` 正確
2. 確認帳號有餘額
3. 沒有 OpenAI key 也能用！系統會用免費的 Ollama

## 進階配置

### 向量資料庫（Qdrant）

預設使用本機 Qdrant：
```bash
# Docker 方式
docker run -p 6333:6333 qdrant/qdrant

# 或使用 Qdrant Cloud（免費 1GB）
# 設定 .env:
# QDRANT_URL=https://your-cluster.qdrant.io
# QDRANT_API_KEY=your-api-key
```

### 自訂訓練網站

編輯 `scripts/autonomous_bot.py`：
```python
test_sites = [
    "https://example.com",
    "https://your-website.com",  # 加入你的網站
]
```

## 目錄結構

```
flyto2/
├── .env                    # 你的配置（不會提交到 git）
├── .env.example            # 配置範例
├── START_BOT.bat           # 唯一啟動入口
├── requirements.txt        # Python 依賴
├── scripts/
│   ├── autonomous_bot.py       # 自動訓練循環
│   └── telegram_bot_v2.py      # Telegram 聊天機器人
├── src/core/
│   ├── modules/            # 149 個原子模組
│   ├── engine/             # Workflow 引擎
│   └── evolution/          # 自動進化引擎
└── workflows/              # YAML 工作流程
```

## 下一步

1. ✅ 設定好 `.env` 文件
2. ✅ 執行 `START_BOT.bat`
3. ✅ 在 Telegram 發送 `/start` 給你的 bot
4. ✅ 試試看用 `/lang zh-TW` 設定語言
5. ✅ 開始聊天！系統會自動學習和進化

有問題？在 Telegram 發送 `/help` 或查看文檔！
