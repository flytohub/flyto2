# Flyto2 技術資產清單

> 最後更新：2025-12-04
> 用途：方便未來任意組合各種技術模組

---

## 概覽

| 分類 | 數量 | 說明 |
|------|------|------|
| 大系統 | 12 | 核心引擎級別 |
| 中系統 | 28 | 功能模組級別 |
| 小元件 | 162+ | 原子操作級別 |

---

## 🔴 大系統（Core Systems）

### 1. 工作流引擎 (Workflow Engine)
- **位置**: `src/core/engine/`
- **用途**: YAML 工作流解析與執行
- **核心能力**:
  - YAML 工作流定義與執行
  - `${variable}` 變數解析
  - 條件執行 (when)
  - 重試機制 (retry)
  - 平行執行 (parallel)
  - 步驟級錯誤處理

### 2. 模組註冊系統 (Module Registry)
- **位置**: `src/core/modules/registry.py`
- **用途**: 所有模組的統一管理
- **核心能力**:
  - 裝飾器自動註冊 `@register_module`
  - 多語言支援 (i18n)
  - 版本管理
  - 模組元數據查詢
  - UI 動態表單生成

### 3. 瀏覽器自動化 (Browser Automation)
- **位置**: `src/core/browser/driver.py`
- **用途**: 網頁操作自動化
- **核心能力**:
  - Playwright 驅動 (Chrome/Firefox/WebKit)
  - Headless/可視模式
  - DOM 操作 (click/type/wait/extract)
  - 截圖與數據擷取
  - Cookie/Session 管理

### 4. 進化系統 (Evolution System)
- **位置**: `src/core/evolution/`
- **用途**: 自動偵測錯誤並生成修復
- **核心能力**:
  - 錯誤偵測 → 分析 → 生成模組 → 測試 → PR
  - RAG 錯誤分析
  - 錯誤模式匹配
  - GitHub PR 自動創建
  - Telegram 通知

### 5. Meta 品質系統 (Meta Quality System)
- **位置**: `src/core/meta/`
- **用途**: 程式碼品質控制與精煉
- **核心能力**:
  - 多輪自動精煉 (AutoRefiner V3)
  - 10 分制品質評分
  - 收斂偵測
  - 程式碼差異追蹤
  - 問題分類與優先排序

### 6. 知識系統 (Knowledge System)
- **位置**: `src/core/knowledge/`
- **用途**: 知識庫管理與檢索
- **核心能力**:
  - Qdrant 向量資料庫
  - RAG 檢索增強生成
  - 文件攝取管道
  - 知識儲存與查詢

### 7. 記憶系統 (Memory System)
- **位置**: `src/core/memory/`
- **用途**: 執行歷史與上下文管理
- **核心能力**:
  - Job 記憶追蹤
  - 知識萃取
  - 對話記憶
  - 斷點續傳
  - 隱私保護

### 8. AI 協調器 (LLM Orchestrator)
- **位置**: `src/core/ai/`
- **用途**: LLM 呼叫管理
- **核心能力**:
  - 任務協調
  - 輸出驗證
  - 多模型支援

### 9. 自我修復系統 (Healing System)
- **位置**: `src/core/healing/`
- **用途**: 自動修復執行錯誤
- **核心能力**:
  - AI 錯誤解決
  - 工作流自動修復

### 10. 訓練系統 (Training System)
- **位置**: `src/core/training/`
- **用途**: 持續改進訓練
- **核心能力**:
  - 每日練習
  - 壓力測試
  - 自我修復練習

### 11. 競賽系統 (Competition System)
- **位置**: `src/core/competition/`
- **用途**: 模組效能比較
- **核心能力**:
  - 速度競賽
  - 效能評比

### 12. 指標系統 (Metrics System)
- **位置**: `src/core/metrics/`
- **用途**: 執行指標追蹤
- **核心能力**:
  - PostgreSQL (Neon) 儲存
  - 模組生成指標
  - 精煉迭代指標
  - 測試執行指標

---

## 🟡 中系統（Feature Modules）

### Meta 子系統

| 名稱 | 位置 | 用途 |
|------|------|------|
| AutoRefiner V3 | `meta/auto_refiner_v3.py` | 同步原子式多輪精煉 |
| AutoRefiner V2 | `meta/auto_refiner_v2.py` | 進階精煉 + 問題優先排序 |
| Code Differ | `meta/code_differ.py` | 程式碼版本比較 |
| Convergence Detector | `meta/convergence_detector.py` | 精煉收斂偵測 |
| Issue Analyzer | `meta/issue_analyzer.py` | 問題分類與優先排序 |
| Quality Checker V2 | `meta/quality_checker_v2.py` | 10 項原子品質檢查 |
| Enhanced Module Generator | `meta/enhanced_module_generator.py` | 嚴格品質模組生成 |
| Module Generator | `meta/module_generator.py` | 基礎模組生成 |
| Test Executor | `meta/test_executor.py` | 測試生成與執行 |
| Strict PR Reviewer | `meta/strict_pr_reviewer.py` | GitHub PR 審查 |
| Code Analyzer | `meta/code_analyzer.py` | 程式碼結構分析 |
| Enhanced Prompt Builder | `meta/enhanced_prompt_builder.py` | LLM 精煉提示建構 |
| Metrics Tracker | `meta/metrics_tracker.py` | 品質指標追蹤 |
| V3Evolution | `meta/v3_evolution.py` | 完整進化循環 |

### 工具子系統

| 名稱 | 位置 | 用途 |
|------|------|------|
| HTTP Client | `utils/http_client.py` | 進階 HTTP 請求 + 重試 |
| RAG Retriever | `utils/rag_retriever.py` | 檢索增強生成 |
| Language Bridge | `utils/language_bridge.py` | 多語言支援 |
| Translator | `utils/translator.py` | 文字翻譯 |
| Notifier | `utils/notifier.py` | 通知系統 |
| Vector DB Manager | `utils/vector_db_manager.py` | 向量資料庫管理 |

### 其他中系統

| 名稱 | 位置 | 用途 |
|------|------|------|
| Intent Detector | `agent/intent_detector.py` | 自然語言意圖偵測 |
| AI Logger | `audit/ai_logger.py` | AI 操作日誌 |
| Error Reporter | `audit/error_reporter.py` | 錯誤回報 |
| Smart Executor | `executor/smart_executor.py` | 智能執行 + 錯誤恢復 |
| Evolution Orchestrator | `evolution/orchestrator.py` | 進化管道協調 |
| Reporter | `evolution/reporter.py` | 進化結果報告 |
| AI Error Solver | `healing/ai_error_solver.py` | AI 錯誤解決 |
| Auto Heal | `healing/auto_heal.py` | 自動修復 |

---

## 🟢 小元件（Atomic Modules）

> 共 162+ 個原子模組，32+ 個分類

### 瀏覽器操作 (browser.*)

| 模組 | 用途 |
|------|------|
| `browser.launch` | 啟動瀏覽器 |
| `browser.goto` | 導航到 URL |
| `browser.click` | 點擊元素 |
| `browser.type` | 輸入文字 |
| `browser.press` | 按鍵操作 |
| `browser.screenshot` | 截圖 |
| `browser.extract` | 結構化數據擷取 |
| `browser.wait` | 等待條件 |
| `browser.find` | 查找元素 |

### 陣列操作 (array.*)

| 模組 | 用途 |
|------|------|
| `array.chunk` | 分割陣列 |
| `array.difference` | 陣列差集 |
| `array.filter` | 過濾陣列 |
| `array.flatten` | 攤平巢狀陣列 |
| `array.intersection` | 陣列交集 |
| `array.join` | 合併陣列 |
| `array.map` | 映射操作 |
| `array.reduce` | 歸約操作 |
| `array.sort` | 排序 |
| `array.unique` | 去重 |

### 字串操作 (string.*)

| 模組 | 用途 |
|------|------|
| `string.lowercase` | 轉小寫 |
| `string.uppercase` | 轉大寫 |
| `string.titlecase` | 標題大小寫 |
| `string.trim` | 去除空白 |
| `string.split` | 分割字串 |
| `string.replace` | 替換字串 |
| `string.reverse` | 反轉字串 |

### 數學操作 (math.*)

| 模組 | 用途 |
|------|------|
| `math.calculate` | 數學計算 |
| `math.abs` | 絕對值 |
| `math.ceil` | 無條件進位 |
| `math.floor` | 無條件捨去 |
| `math.power` | 次方 |
| `math.round` | 四捨五入 |

### 資料操作 (data.*)

| 模組 | 用途 |
|------|------|
| `csv.read` | 讀取 CSV |
| `csv.write` | 寫入 CSV |
| `json.parse` | 解析 JSON |
| `json.stringify` | 轉換為 JSON |
| `text.template` | 模板渲染 |

### 檔案操作 (file.*)

| 模組 | 用途 |
|------|------|
| `file.read` | 讀取檔案 |
| `file.write` | 寫入檔案 |
| `file.copy` | 複製檔案 |
| `file.delete` | 刪除檔案 |
| `file.move` | 移動檔案 |
| `file.exists` | 檢查檔案存在 |

### 日期時間 (datetime.*)

| 模組 | 用途 |
|------|------|
| `datetime.parse` | 解析日期 |
| `datetime.format` | 格式化日期 |
| `datetime.add` | 增加時間 |
| `datetime.subtract` | 減少時間 |
| `datetime.now` | 當前時間 |

### 物件操作 (object.*)

| 模組 | 用途 |
|------|------|
| `object.keys` | 取得鍵值 |
| `object.values` | 取得值 |
| `object.merge` | 合併物件 |
| `object.pick` | 選取屬性 |
| `object.omit` | 排除屬性 |

### 工具操作 (utility.*)

| 模組 | 用途 |
|------|------|
| `utility.delay` | 延遲執行 |
| `utility.hash_md5` | MD5 雜湊 |
| `utility.random_number` | 隨機數字 |
| `utility.random_string` | 隨機字串 |
| `utility.not` | 邏輯非 |

### 向量操作 (vector.*)

| 模組 | 用途 |
|------|------|
| `vector.embeddings` | 生成向量嵌入 |
| `vector.connector` | 連接向量資料庫 |
| `vector.knowledge_manager` | 知識管理 |
| `vector.knowledge_store` | 知識儲存 |
| `vector.rag` | 檢索增強生成 |
| `vector.quality_filter` | 品質過濾 |
| `vector.auto_archive` | 自動歸檔 |

### 分析操作 (analysis.*)

| 模組 | 用途 |
|------|------|
| `analysis.readability` | 可讀性分析 |
| `analysis.forms` | 表單擷取 |
| `analysis.metadata` | 元數據擷取 |
| `analysis.tables` | 表格擷取 |
| `analysis.patterns` | 模式偵測 |
| `analysis.structure` | 結構分析 |

### 流程控制 (flow.*)

| 模組 | 用途 |
|------|------|
| `loop` | 迴圈執行 |
| `foreach` | 遍歷執行 |
| `condition` | 條件分支 |
| `parallel` | 平行執行 |

### 圖片操作 (image.*)

| 模組 | 用途 |
|------|------|
| `image.download` | 下載圖片 |
| `image.svg_convert` | SVG 轉換 |

---

## 🔵 第三方整合（Integrations）

> 共 42 個整合模組

### AI 整合

| 模組 | 用途 |
|------|------|
| `openai.chat` | OpenAI 對話 |
| `openai.completion` | 文字補全 |
| `openai.embeddings` | 向量嵌入 |
| `ollama.local` | 本地 Ollama 模型 |

### 雲端儲存

| 模組 | 用途 |
|------|------|
| `gcs.*` | Google Cloud Storage |
| `azure.*` | Azure Storage |

### 資料庫

| 模組 | 用途 |
|------|------|
| `db.connector` | 資料庫連接器 |
| `redis.*` | Redis 整合 |

### 開發工具

| 模組 | 用途 |
|------|------|
| `http.*` | HTTP 請求 |
| `github.*` | GitHub API |

### 通訊

| 模組 | 用途 |
|------|------|
| `twilio.*` | SMS/語音 |

### 支付

| 模組 | 用途 |
|------|------|
| `stripe.*` | Stripe 支付 |

---

## 📦 腳本工具（Scripts）

### 模組管理

| 腳本 | 用途 |
|------|------|
| `create_module.py` | 創建新模組 |
| `lint_modules.py` | 程式碼檢查 |
| `validate_all_modules.py` | 驗證所有模組 |
| `update_modules.py` | 更新模組註冊 |

### Bot 自動化

| 腳本 | 用途 |
|------|------|
| `autonomous_bot.py` | 自主進化 Bot |
| `interactive_evolution_bot.py` | 互動進化 Bot |
| `telegram_bot.py` | Telegram 通知 |

### 知識管理

| 腳本 | 用途 |
|------|------|
| `ingest_modules_to_knowledge.py` | 攝取模組到知識庫 |
| `ingest_with_ollama.py` | 本地 LLM 攝取 |
| `query_project_knowledge.py` | 查詢知識庫 |

### 向量資料庫

| 腳本 | 用途 |
|------|------|
| `setup_cloud_qdrant.py` | 設置 Qdrant 雲端 |
| `check_qdrant_status.py` | 健康檢查 |
| `reset_qdrant_collection.py` | 重置集合 |

---

## 🎯 組合範例

### 範例 1：網頁爬蟲 + AI 分析
```
browser.launch → browser.goto → browser.extract → openai.chat
```

### 範例 2：資料處理管道
```
csv.read → array.filter → array.map → json.stringify → file.write
```

### 範例 3：自動化測試 + 品質保證
```
AutoRefiner V3 → Test Executor → Quality Checker V2 → GitHub PR
```

### 範例 4：知識檢索 + RAG
```
vector.embeddings → vector.knowledge_store → vector.rag → openai.chat
```

### 範例 5：自我修復工作流
```
Evolution System → AI Error Solver → Auto Heal → Telegram 通知
```

---

## 📊 統計總覽

| 指標 | 數值 |
|------|------|
| Python 檔案總數 | 236 |
| 程式碼總行數 | ~46,758 |
| 原子模組數量 | 162+ |
| 第三方整合數量 | 42 |
| Meta 系統元件 | 16 |
| 測試套件數量 | 5 |

---

## 🛠️ 技術棧

- **語言**: Python 3.x
- **Web 框架**: FastAPI + Uvicorn
- **瀏覽器自動化**: Playwright
- **資料庫**: PostgreSQL (Neon)
- **向量資料庫**: Qdrant
- **LLM**: OpenAI GPT
- **通知**: Telegram API
