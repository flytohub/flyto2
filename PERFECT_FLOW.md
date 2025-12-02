# 🎯 Flyto2 完美流程 - 用戶手冊

## 概述

這是實現你描述的完美流程的 Telegram 機器人：

```
TG 輸入 → 思考 → 生成 YAML → 測試 → 失敗？→ 選擇解決方式 → 重試 → 成功 → 發 PR
```

## 完整流程

### 1. 用戶輸入任務
```
你: 爬蟲 google 搜尋蝦皮 給我第二筆網站
```

### 2. 機器人思考
```
🤔 收到任務，正在思考...
✅ 理解任務
   類型: crawl
   信心: 80%
```

### 3. 生成 YAML Workflow
```
📝 正在生成 YAML workflow...
✅ 生成 workflow:

workflow_name: google_search_shopee
steps:
  - step_id: launch
    module: browser.launch
    params: {headless: true}
  - step_id: goto
    module: browser.goto
    params: {url: "https://google.com"}
  ...
```

### 4. 測試執行
```
🧪 測試執行 (嘗試 1/3)...
```

### 5a. 如果成功
```
✅ 測試成功！

結果:
{
  "title": "蝦皮購物 - 台灣最大購物平台",
  "url": "https://shopee.tw"
}

🎉 Workflow 測試成功！接下來要做什麼？

[發 PR 給我驗證] [直接使用]
```

### 5b. 如果失敗 - 顯示選項
```
❌ 執行失敗:
ModuleNotFoundError: No module named 'playwright'

🤔 要怎麼解決這個問題？

[🙋 讓我來解決] [🤖 讓機器人解決] [💰 問 OpenAI ($)]
```

#### 選項 1: 讓我來解決
```
點擊 [🙋 讓我來解決]

機器人: 📝 請告訴我怎麼修復，或輸入新的 workflow

你: 先安裝 playwright: pip install playwright
    然後 playwright install chromium
```

#### 選項 2: 讓機器人解決
```
點擊 [🤖 讓機器人解決]

機器人:
  🤖 讓機器人自己想辦法...
  🔍 Searching vector DB for similar solutions...
  💡 AI provided solution: Install playwright
  ⚙️ Executing 2 commands...
    $ pip install playwright
    ✅ Success
    $ playwright install chromium
    ✅ Success
  ✅ AI solution worked!
  🧪 測試執行 (嘗試 2/3)...
  ✅ 測試成功！
```

#### 選項 3: 問 OpenAI
```
點擊 [💰 問 OpenAI ($)]

機器人:
  💰 詢問 OpenAI...
  (使用 GPT-4 分析問題)
  ✅ OpenAI 建議: [詳細解決方案]
  執行中...
```

### 6. 繼續測試直到成功

每次失敗後自動重試，最多 3 次。

### 7. 發 PR 給你驗證

```
點擊 [發 PR 給我驗證]

機器人:
  📋 發送 PR 請求...
  🌿 Creating branch: flyto2-workflow-20250102-1234
  💾 Committing workflow...
  ⬆️ Pushing to GitHub...
  🔗 Creating PR: https://github.com/you/repo/pull/123

  ✅ PR 已創建，請前往 GitHub 審核
```

## 啟動機器人

### 快速啟動
```bash
export TELEGRAM_BOT_TOKEN=your_token
./START_PERFECT_BOT.sh
```

### 手動啟動
```bash
export TELEGRAM_BOT_TOKEN=your_token
export TELEGRAM_ALLOWED_USERS=123456789,987654321  # 可選
python3 scripts/telegram_bot_perfect.py
```

## 環境變量

| 變量 | 必需 | 說明 |
|------|------|------|
| `TELEGRAM_BOT_TOKEN` | ✅ | Telegram bot token |
| `TELEGRAM_ALLOWED_USERS` | ❌ | 允許的用戶 ID（逗號分隔，留空=所有用戶）|
| `OLLAMA_URL` | ❌ | Ollama API 地址（默認: http://localhost:11434）|
| `OPENAI_API_KEY` | ❌ | OpenAI API key（用於選項 3）|

## 取得 Telegram Bot Token

1. 在 Telegram 搜尋 `@BotFather`
2. 發送 `/newbot`
3. 按照提示設置機器人名稱
4. 複製 API token
5. 設置環境變量: `export TELEGRAM_BOT_TOKEN=your_token`

## 取得你的 User ID

1. 在 Telegram 搜尋 `@userinfobot`
2. 點擊 Start
3. 複製你的 ID
4. 設置: `export TELEGRAM_ALLOWED_USERS=your_id`

## 依賴安裝

```bash
# Python 依賴
pip install -r requirements.txt

# Playwright（用於瀏覽器自動化）
pip install playwright
playwright install chromium

# Telegram bot
pip install python-telegram-bot
```

## 功能狀態

| 功能 | 狀態 | 說明 |
|------|------|------|
| 意圖檢測 | ✅ 完成 | 理解中文/英文任務 |
| YAML 生成 | ✅ 完成 | 用 Ollama 生成 workflow |
| 測試執行 | ✅ 完成 | 真正執行 workflow |
| 失敗選項 | ✅ 完成 | 三種解決方式 |
| 自動解決 | ✅ 完成 | AI Error Solver |
| 手動解決 | ✅ 完成 | 用戶提供指導 |
| OpenAI 解決 | 🚧 開發中 | 需要 API key |
| PR 創建 | 🚧 開發中 | 需要 GitHub token |

## 範例對話

```
你: /start

機器人:
  🤖 Flyto2 完美流程機器人

  直接輸入任務，例如:
  - 爬蟲 google.com
  - 幫我爬蟲google 搜尋蝦皮 給我第二筆網站

  我會:
  1. 理解你的任務
  2. 生成 YAML workflow
  3. 測試執行
  4. 如果失敗，問你要怎麼解決
  5. 繼續測試直到成功
  6. 發 PR 給你驗證

---

你: 爬蟲 example.com

機器人:
  🤔 收到任務，正在思考...
  ✅ 理解任務
     類型: crawl
     信心: 90%
  📝 正在生成 YAML workflow...
  ✅ 生成 workflow: [顯示 YAML]
  🧪 測試執行 (嘗試 1/3)...
  ✅ 測試成功！

  結果:
  {
    "title": "Example Domain",
    "content": "This domain is for use in..."
  }

  🎉 Workflow 測試成功！接下來要做什麼？

  [發 PR 給我驗證] [直接使用]
```

## 架構

```
telegram_bot_perfect.py
│
├─ PerfectBot
│  ├─ handle_message() ─────── 接收用戶輸入
│  ├─ generate_workflow() ───── 用 Ollama 生成 YAML
│  ├─ test_workflow() ────────── 用 WorkflowEngine 執行
│  ├─ handle_failure() ────────── 顯示三個選項
│  ├─ auto_solve() ───────────── 調用 AI Error Solver
│  ├─ solve_with_openai() ───── 使用 OpenAI (付費)
│  └─ create_pr() ────────────── 創建 GitHub PR
│
├─ IntentDetector ─────────────── 理解用戶意圖
├─ HTTPClient ──────────────────── Ollama API
├─ WorkflowEngine ──────────────── 執行 YAML
└─ AIErrorSolver ───────────────── 自動修復錯誤
```

## 這是 A + C 的完美搭配

### A: 修復端到端流程
- ✅ TG → Intent → Workflow → Execute → Result
- ✅ 真正能執行任務
- ✅ 錯誤處理完整

### C: 簡化複雜度
- ✅ 一個文件，清晰的流程
- ✅ 用戶友好的選項
- ✅ 不過度工程化

## 下一步

1. **測試基本流程**: `./START_PERFECT_BOT.sh`
2. **實現 OpenAI 整合**: 付費但更準確
3. **實現 PR 創建**: 自動化 GitHub 工作流
4. **添加更多模組**: 根據需求擴展

## 問題排查

### 機器人無回應
- 檢查 token 是否正確
- 檢查用戶 ID 是否在允許列表

### Workflow 生成失敗
- 確認 Ollama 正在運行: `curl http://localhost:11434`
- 檢查模型是否下載: `ollama list`

### 測試執行失敗
- 檢查依賴是否安裝: `pip list | grep playwright`
- 檢查瀏覽器是否安裝: `playwright install --help`

## 支援

遇到問題？
1. 查看日誌輸出
2. 檢查 `test_end_to_end.py` 測試結果
3. 查閱 GitHub Issues
