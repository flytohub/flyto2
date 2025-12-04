# Flyto2 技術資產清單

> 最後更新：2025-12-04
> 用途：方便未來任意組合各種技術模組

---

## 概覽

| 分類 | 數量 | 說明 |
|------|------|------|
| 大系統 | 18 | 核心引擎級別 |
| 中系統 | 45+ | 功能模組級別 |
| 小元件 | 180+ | 原子操作級別 |

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
- **子模組**:
  - `auto_evolution_engine.py` - 自動進化引擎
  - `orchestrator.py` - 進化協調器
  - `reporter.py` - 進化報告
  - `ticket.py` - 進化票據

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
- **子模組**:
  - `enterprise_kb_manager.py` - 企業知識庫管理
  - `doc_ingestion.py` - 文件攝取
  - `knowledge_store.py` - 知識儲存
  - `vector_schema.py` - 向量結構定義

### 7. 記憶系統 (Memory System)
- **位置**: `src/core/memory/`
- **用途**: 執行歷史與上下文管理
- **核心能力**:
  - Job 記憶追蹤
  - 知識萃取
  - 對話記憶
  - 斷點續傳
  - 隱私保護
- **子模組**:
  - `job_memory.py` - 工作記憶
  - `conversation_memory.py` - 對話記憶
  - `knowledge_extractor.py` - 知識萃取
  - `resume.py` - 斷點續傳
  - `privacy.py` - 隱私遮蔽

### 8. AI 協調器 (LLM Orchestrator)
- **位置**: `src/core/ai/`
- **用途**: LLM 呼叫管理
- **核心能力**:
  - 任務協調
  - 輸出驗證
  - 多模型支援
- **子模組**:
  - `llm_orchestrator.py` - LLM 協調
  - `llm_task.py` - LLM 任務
  - `validators.py` - 輸出驗證

### 9. 自我修復系統 (Healing System)
- **位置**: `src/core/healing/`
- **用途**: 自動修復執行錯誤
- **核心能力**:
  - AI 錯誤解決
  - 工作流自動修復
  - 解決方案歸檔
- **子模組**:
  - `ai_error_solver.py` - AI 錯誤解決
  - `auto_heal.py` - 自動修復
- **原子元件**:
  - `vector_query.py` - 向量查詢
  - `solution_executor.py` - 解決方案執行
  - `similarity_trainer.py` - 相似度訓練
  - `solution_archiver.py` - 解決方案歸檔
  - `prompt_builder.py` - 提示建構
  - `ai_consulter.py` - AI 諮詢

### 10. 訓練系統 (Training System)
- **位置**: `src/core/training/`
- **用途**: 持續改進訓練
- **核心能力**:
  - 每日練習
  - 壓力測試
  - 自我修復練習
- **子模組**:
  - `daily_practice.py` - 每日練習
  - `stress_test.py` - 壓力測試
  - `self_healing_practice.py` - 自我修復練習
- **原子元件**:
  - `robots_parser.py` - Robots.txt 解析
  - `html_pattern_detector.py` - HTML 模式偵測
  - `schema_inferrer.py` - 結構推斷
  - `recommendation_generator.py` - 推薦生成

### 11. 競賽系統 (Competition System)
- **位置**: `src/core/competition/`
- **用途**: 模組效能比較
- **核心能力**:
  - 速度競賽 (SpeedRace)
  - 準確度競賽 (AccuracyRace)
  - 策略競賽 (StrategyRace)
  - 對抗競賽 (BattleRace)
  - 壓力競賽 (StressRace)
- **子模組**:
  - `speed_race.py` - 速度競賽
  - `race_types.py` - 競賽類型定義

### 12. 指標系統 (Metrics System)
- **位置**: `src/core/metrics/`
- **用途**: 執行指標追蹤
- **核心能力**:
  - PostgreSQL (Neon) 儲存
  - 模組生成指標
  - 精煉迭代指標
  - 測試執行指標
- **子模組**:
  - `db_manager.py` - 資料庫管理
  - `db_schema.sql` - 資料結構

### 13. 排行榜系統 (Leaderboard System) ⭐ 新增
- **位置**: `src/core/leaderboard/`
- **用途**: 模組效能排名與歷史比較
- **核心能力**:
  - 準確度排行榜 (Accuracy Leaderboard)
  - 穩定度排行榜 (Stability Leaderboard)
  - 進化排行榜 (Evolution Leaderboard)
  - 週對週/月對月比較
  - 趨勢分析
- **子模組**:
  - `metrics_tracker.py` - 指標追蹤（準確度/穩定度/進化）
  - `historical_comparison.py` - 歷史比較

### 14. 性能優化系統 (Performance System) ⭐ 新增
- **位置**: `src/core/performance/`
- **用途**: 模組性能分析與優化建議
- **核心能力**:
  - 慢模組偵測
  - 性能評級 (Optimal/Slow/Very Slow)
  - 自動優化建議
  - 綜合優化報告
- **子模組**:
  - `optimizer.py` - 性能優化器

### 15. 增強檢索系統 (Enhanced Retrieval) ⭐ 新增
- **位置**: `src/core/retrieval/`
- **用途**: 進階向量檢索
- **核心能力**:
  - 查詢改寫 (Query Rewrite)
  - MMR 多樣性選擇
  - 混合搜索 (Hybrid Search)
  - 結果重排序 (Reranking)
- **子模組**:
  - `enhanced_retrieval.py` - 增強檢索

### 16. 智能系統 (Intelligence System) ⭐ 新增
- **位置**: `src/core/intelligence/`
- **用途**: 自然語言理解
- **核心能力**:
  - 意圖偵測
  - 上下文理解
- **子模組**:
  - `intent_detector.py` - 意圖偵測

### 17. 審計系統 (Audit System) ⭐ 新增
- **位置**: `src/core/audit/`
- **用途**: AI 決策追蹤與日誌
- **核心能力**:
  - AI 決策日誌
  - 推理過程記錄
  - 信心度追蹤
- **子模組**:
  - `ai_logger.py` - AI 審計日誌

### 18. 測試系統 (Testing System) ⭐ 新增
- **位置**: `src/core/testing/`
- **用途**: 測試與錯誤報告
- **核心能力**:
  - Telegram 錯誤報告
  - 測試結果通知
- **子模組**:
  - `error_reporter.py` - 錯誤報告器

---

## 🟡 中系統（Feature Modules）

### Meta 子系統 (18 個)

| 名稱 | 位置 | 用途 |
|------|------|------|
| AutoRefiner V3 | `meta/auto_refiner_v3.py` | 同步原子式多輪精煉 |
| AutoRefiner V2 | `meta/auto_refiner_v2.py` | 進階精煉 + 問題優先排序 |
| AutoRefiner V1 | `meta/auto_refiner.py` | 基礎精煉 |
| Code Differ | `meta/code_differ.py` | 程式碼版本比較 |
| Convergence Detector | `meta/convergence_detector.py` | 精煉收斂偵測 |
| Issue Analyzer | `meta/issue_analyzer.py` | 問題分類與優先排序 |
| Quality Checker V2 | `meta/quality_checker_v2.py` | 10 項原子品質檢查 |
| Enhanced Module Generator | `meta/enhanced_module_generator.py` | 嚴格品質模組生成 |
| Module Generator | `meta/module_generator.py` | 基礎模組生成 |
| Test Generator | `meta/test_generator.py` | YAML 測試生成 |
| Test Executor | `meta/test_executor.py` | 測試執行 |
| Strict PR Reviewer | `meta/strict_pr_reviewer.py` | GitHub PR 審查 |
| Code Analyzer | `meta/code_analyzer.py` | 程式碼結構分析 |
| Enhanced Prompt Builder | `meta/enhanced_prompt_builder.py` | LLM 精煉提示建構 |
| Metrics Tracker | `meta/metrics_tracker.py` | 品質指標追蹤 |
| V3Evolution | `meta/v3_evolution.py` | 完整進化循環 |
| Prompt Loader | `meta/prompt_loader.py` | 提示載入 |

### 工具子系統 (7 個)

| 名稱 | 位置 | 用途 |
|------|------|------|
| HTTP Client | `utils/http_client.py` | 進階 HTTP 請求 + 重試 |
| RAG Retriever | `utils/rag_retriever.py` | 檢索增強生成 |
| Language Bridge | `utils/language_bridge.py` | 多語言支援 |
| Translator | `utils/translator.py` | 文字翻譯 |
| Notifier | `utils/notifier.py` | 通知系統 (Telegram) |
| Vector DB Manager | `utils/vector_db_manager.py` | 向量資料庫管理 |

### 排行榜子系統 (3 個) ⭐ 新增

| 名稱 | 位置 | 用途 |
|------|------|------|
| AccuracyMetric | `leaderboard/metrics_tracker.py` | 準確度指標 |
| StabilityMetric | `leaderboard/metrics_tracker.py` | 穩定度指標 |
| EvolutionMetric | `leaderboard/metrics_tracker.py` | 進化指標 |

### 檢索子系統 (3 個) ⭐ 新增

| 名稱 | 位置 | 用途 |
|------|------|------|
| QueryRewriter | `retrieval/enhanced_retrieval.py` | 查詢改寫 |
| MMRSelector | `retrieval/enhanced_retrieval.py` | MMR 多樣性選擇 |
| HybridSearcher | `retrieval/enhanced_retrieval.py` | 混合搜索 |

### 記憶子系統 (5 個)

| 名稱 | 位置 | 用途 |
|------|------|------|
| JobMemory | `memory/job_memory.py` | 工作記憶 |
| ConversationMemory | `memory/conversation_memory.py` | 對話記憶 |
| KnowledgeExtractor | `memory/knowledge_extractor.py` | 知識萃取 |
| Resume | `memory/resume.py` | 斷點續傳 |
| PrivacyRedactor | `memory/privacy.py` | 隱私遮蔽 |

### 其他中系統

| 名稱 | 位置 | 用途 |
|------|------|------|
| Intent Detector | `intelligence/intent_detector.py` | 自然語言意圖偵測 |
| AI Audit Logger | `audit/ai_logger.py` | AI 決策審計日誌 |
| Telegram Error Reporter | `testing/error_reporter.py` | Telegram 錯誤報告 |
| Smart Executor | `executor/smart_executor.py` | 智能執行 + 錯誤恢復 |
| Evolution Orchestrator | `evolution/orchestrator.py` | 進化管道協調 |
| Evolution Reporter | `evolution/reporter.py` | 進化結果報告 |
| AI Error Solver | `healing/ai_error_solver.py` | AI 錯誤解決 |
| Auto Heal | `healing/auto_heal.py` | 自動修復 |
| Performance Optimizer | `performance/optimizer.py` | 性能優化 |
| Historical Comparison | `leaderboard/historical_comparison.py` | 歷史比較 |
| HTML Analyzer | `analysis/html_analyzer.py` | HTML 結構分析 |

---

## 🟢 小元件（Atomic Modules）

> 共 180+ 個原子模組，35+ 個分類

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
| `utility.datetime_now` | 當前時間 |
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

### API 操作 (api.*) ⭐ 新增

| 模組 | 用途 |
|------|------|
| `api.rate_limiter` | 速率限制處理 |
| `api.connection_pool` | 連接池管理 |
| `api.proxy_manager` | 代理管理 |
| `api.anti_bot` | 反爬蟲偵測 |

### 訓練操作 (training.*) ⭐ 新增

| 模組 | 用途 |
|------|------|
| `training.analyze` | 訓練分析 |
| `training.execute` | 訓練執行 |
| `training.infer_schema` | 結構推斷 |
| `training.stats` | 訓練統計 |

### 訓練原子元件 ⭐ 新增

| 模組 | 用途 |
|------|------|
| `robots_parser` | Robots.txt 解析 |
| `html_pattern_detector` | HTML 模式偵測 |
| `schema_inferrer` | 結構推斷 |
| `recommendation_generator` | 推薦生成 |

### 修復原子元件 ⭐ 新增

| 模組 | 用途 |
|------|------|
| `vector_query` | 向量查詢 |
| `solution_executor` | 解決方案執行 |
| `similarity_trainer` | 相似度訓練 |
| `solution_archiver` | 解決方案歸檔 |
| `prompt_builder` | 提示建構 |
| `ai_consulter` | AI 諮詢 |

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

> 共 42+ 個整合模組

### AI 整合

| 模組 | 用途 |
|------|------|
| `openai.chat` | OpenAI 對話 |
| `openai.completion` | 文字補全 |
| `openai.embeddings` | 向量嵌入 |
| `ollama.local` | 本地 Ollama 模型 |
| `ai.services` | AI 服務協調 |
| `ai.agents` | AI Agent 協調 |

### 雲端儲存

| 模組 | 用途 |
|------|------|
| `gcs.*` | Google Cloud Storage |
| `azure.*` | Azure Storage |
| `storage.*` | 通用雲端儲存 |

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
| `messaging.*` | 通用訊息 |

### 生產力

| 模組 | 用途 |
|------|------|
| `airtable.*` | Airtable 整合 |
| `tools.*` | 生產力工具 |

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
| `auto_tool_creator.py` | 自動工具創建 |

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
| `clear_qdrant_cloud.py` | 清除資料 |
| `setup_qdrant_indexes.py` | 設置索引 |

### 系統管理

| 腳本 | 用途 |
|------|------|
| `start_api_server.py` | 啟動 API 服務 |
| `monitor_system.py` | 系統監控 |
| `run_scheduled_tasks.py` | 排程任務 |
| `update_metrics.py` | 更新指標 |
| `deployment_manager.py` | 部署管理 |
| `safety_manager.py` | 安全管理 |
| `generate_test_coverage_report.py` | 測試覆蓋率報告 |

---

## 🏆 評分與排行系統 ⭐ 新增

### 品質評分 (Quality Scoring)

| 評分維度 | 權重 | 說明 |
|----------|------|------|
| 資料完整度 | 40% | 數據擷取完整性 |
| 格式正確度 | 40% | 輸出格式符合規範 |
| 錯誤率 | 20% | 執行錯誤頻率 |

### 穩定度評分 (Stability Scoring)

| 評分維度 | 說明 |
|----------|------|
| 連續成功次數 | 連續成功執行次數 |
| 最大連續成功 | 歷史最高連續成功 |
| 錯誤恢復率 | 錯誤後恢復成功率 |
| 運行時間 | 累計運行小時數 |

### 進化評分 (Evolution Scoring)

| 評分維度 | 說明 |
|----------|------|
| 新增模組數 | 自動生成的模組數量 |
| 測試覆蓋增長 | 測試覆蓋率提升 |
| Bug 修復數 | 自動修復的 Bug 數量 |
| 平均修復時間 | 從發現到修復的時間 |

### 競賽類型 (Race Types)

| 競賽 | 用途 |
|------|------|
| SpeedRace | 執行速度比較 |
| AccuracyRace | 擷取準確度比較 |
| StrategyRace | 策略效能比較 |
| BattleRace | 對抗式比較 |
| StressRace | 壓力測試比較 |

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
QueryRewriter → vector.embeddings → MMRSelector → openai.chat
```

### 範例 5：自我修復工作流
```
Evolution System → AI Error Solver → Auto Heal → Telegram 通知
```

### 範例 6：性能優化管道
```
Performance Optimizer → 慢模組偵測 → 優化建議 → 排行榜更新
```

### 範例 7：反爬蟲處理
```
api.anti_bot → api.rate_limiter → api.proxy_manager → browser.goto
```

---

## 📊 統計總覽

| 指標 | 數值 |
|------|------|
| Python 檔案總數 | 236+ |
| 程式碼總行數 | ~50,000+ |
| 大系統數量 | 18 |
| 中系統數量 | 45+ |
| 原子模組數量 | 180+ |
| 第三方整合數量 | 42+ |
| 腳本工具數量 | 23 |
| 測試套件數量 | 5+ |

---

## 🛠️ 技術棧

| 類別 | 技術 |
|------|------|
| 語言 | Python 3.x |
| Web 框架 | FastAPI + Uvicorn |
| 瀏覽器自動化 | Playwright |
| 關聯式資料庫 | PostgreSQL (Neon) |
| 向量資料庫 | Qdrant |
| LLM | OpenAI GPT / Ollama |
| 通知 | Telegram API |
| 版本控制 | Git + GitHub |
| CI/CD | GitHub Actions |

---

## 🧠 特殊技術（Advanced Techniques）

### 設計模式 (Design Patterns)

| 模式 | 位置 | 用途 |
|------|------|------|
| **Singleton** | `evolution/auto_evolution_engine.py` | 全局單例：SpecGenerator, CodeGenerator, QualityGates |
| **Singleton** | `modules/registry.py` | ModuleCatalogManager 單例 |
| **Singleton** | `evolution/orchestrator.py` | Orchestrator 單例 |
| **Abstract Factory** | `modules/base.py` | BaseModule 抽象工廠 |
| **Protocol (DI)** | `meta/auto_refiner_v3.py` | QualityChecker Protocol 依賴注入 |
| **Decorator** | `modules/registry.py` | `@register_module` 裝飾器自動註冊 |
| **Strategy** | `meta/enhanced_prompt_builder.py` | RefineStrategy 策略模式 |
| **Strategy** | `modules/atomic/api/proxy_manager.py` | 代理輪換策略 (round_robin/random/least_used) |
| **State Machine** | `memory/job_memory.py` | JobStatus 9 狀態機 |
| **Event Sourcing** | `memory/job_memory.py` | JobEventType 事件溯源 |
| **Observer** | 多處 | 事件通知系統 |

### 算法技術 (Algorithms)

| 算法 | 位置 | 用途 |
|------|------|------|
| **MMR** | `retrieval/enhanced_retrieval.py` | Maximal Marginal Relevance 多樣性選擇 |
| **Cosine Similarity** | `retrieval/enhanced_retrieval.py` | 向量相似度計算 |
| **Exponential Backoff** | `modules/base.py`, `utils/http_client.py` | 重試延遲 `2^attempt` |
| **Query Rewriting** | `retrieval/enhanced_retrieval.py` | 查詢改寫 + 關鍵詞擴展 |
| **Code Diffing** | `meta/code_differ.py` | difflib 統一差異比較 |
| **Convergence Detection** | `meta/convergence_detector.py` | 5 種收斂偵測策略 |
| **Language Detection** | `memory/job_memory.py` | Unicode 範圍字元檢測 |
| **Similarity Ratio** | `meta/code_differ.py` | SequenceMatcher 相似度 |
| **Error Pattern Matching** | `evolution/auto_evolution_engine.py` | 錯誤模式匹配 |

### 架構技術 (Architecture)

| 技術 | 位置 | 說明 |
|------|------|------|
| **Zero Coupling** | `meta/*.py` | 純函數設計，零耦合 |
| **Dependency Injection** | `meta/auto_refiner_v3.py` | Protocol + Constructor 注入 |
| **Async/Await** | 全專案 | 全異步架構 |
| **Connection Pooling** | `modules/atomic/api/connection_pool.py` | aiohttp TCPConnector 連接池 |
| **Proxy Rotation** | `modules/atomic/api/proxy_manager.py` | 多策略代理輪換 |
| **Checkpoint/Resume** | `memory/resume.py` | 斷點續傳 |
| **Context Manager** | 多處 | `async with` 資源管理 |

### 可靠性技術 (Reliability)

| 技術 | 位置 | 說明 |
|------|------|------|
| **Retry + Backoff** | `modules/base.py` | 自動重試 + 指數退避 |
| **Timeout Handling** | `modules/base.py` | asyncio.wait_for 超時 |
| **Rate Limiting** | `modules/atomic/api/rate_limiter.py` | 速率限制 + 自動重試 |
| **Anti-Bot Detection** | `modules/atomic/api/anti_bot.py` | 反爬蟲檢測 (Cloudflare/Captcha) |
| **Graceful Degradation** | `utils/http_client.py` | Ollama 可用性檢測降級 |
| **Health Check** | 多處 | 服務健康檢查 |

### AI/ML 技術 (AI/ML)

| 技術 | 位置 | 說明 |
|------|------|------|
| **RAG** | `utils/rag_retriever.py` | 檢索增強生成 |
| **Vector Embeddings** | `modules/atomic/vector/embeddings.py` | OpenAI/Ollama 嵌入 |
| **Semantic Search** | `knowledge/enterprise_kb_manager.py` | 語義搜索 |
| **Multi-pass Refinement** | `meta/auto_refiner_v3.py` | 多輪精煉 (4 輪策略) |
| **Quality Scoring** | `meta/quality_checker_v2.py` | 10 分制品質評分 |
| **Hybrid Search** | `retrieval/enhanced_retrieval.py` | 混合搜索 (向量 + 關鍵詞) |
| **Reranking** | `retrieval/enhanced_retrieval.py` | 結果重排序 |
| **Issue Priority** | `meta/issue_analyzer.py` | 問題優先級排序 |

### 安全技術 (Security)

| 技術 | 位置 | 說明 |
|------|------|------|
| **Privacy Redaction** | `memory/privacy.py` | 敏感資訊遮蔽 (Email/Phone/URL) |
| **Permission System** | `memory/job_memory.py` | JobEventType.PERMISSION_CHECK |
| **Audit Logging** | `audit/ai_logger.py` | AI 決策審計日誌 |
| **Security Events** | `memory/job_memory.py` | SECURITY_VIOLATION 事件 |

### 資料結構 (Data Structures)

| 結構 | 位置 | 說明 |
|------|------|------|
| **@dataclass** | 多處 | 不可變資料類 |
| **Enum** | `meta/issue_analyzer.py` | 類型安全枚舉 |
| **Protocol** | `meta/auto_refiner_v3.py` | 結構性子類型 |
| **TypedDict** | 多處 | 類型化字典 |
| **Union/Optional** | 多處 | 類型聯合 |

### 收斂偵測策略 (Convergence Detection)

| 策略 | 說明 |
|------|------|
| `SCORE_PLATEAU` | 分數停滯不前 |
| `MINIMAL_CHANGES` | 代碼變更極小 |
| `INFINITE_LOOP` | 偵測到循環 |
| `NO_IMPROVEMENT` | 無改進 |
| `TARGET_REACHED` | 目標達成 |

### 精煉策略 (Refinement Strategies)

| 策略 | 說明 |
|------|------|
| `TARGETED_FIX` | 針對性修復特定問題 |
| `FULL_REWRITE` | 完整重寫 |
| `INCREMENTAL_IMPROVEMENT` | 漸進式改進 |

### Job 生命週期狀態 (Job Lifecycle)

```
QUEUED → PLANNING → EXECUTING → COMPLETED
                  ↓           ↓
               PAUSED     FAILED/TIMEOUT
                  ↓
        WAITING_USER_INPUT → CANCELLED
```

9 種狀態：queued, planning, executing, paused, waiting_user_input, completed, failed, cancelled, timeout

### 錯誤自動修復模式匹配

| 錯誤模式 | 自動修復策略 |
|----------|--------------|
| `timeout` | 增加超時 + 指數退避重試 |
| `element not found` | 智能等待 + fallback 選擇器 |
| `rate limit` | 速率限制處理 + 退避 |
| `captcha` | 反爬蟲偵測 + 代理輪換 |

---

## 📱 Telegram Bot 功能

### AI 對話 Bot (`scripts/telegram_bot.py`)

| 指令 | 功能 |
|------|------|
| `/start` | 啟動 Bot |
| `/help` | 顯示幫助 |
| `/mode local` | 只用本地 Ollama (免費) |
| `/mode openai` | 只用 OpenAI (付費) |
| `/mode auto` | 混合模式 (推薦) |
| `/ask <問題>` | 用當前模式問問題 |
| `/gpt <問題>` | 強制用 OpenAI GPT-4 |
| `/status` | 查看品質指標 |
| `/quality` | 詳細品質報告 |

**特色：**
- 混合 LLM：預設 Ollama (免費)，複雜任務用 GPT-4
- 對話記憶：保留最近 20 條訊息
- 成本追蹤：顯示省了多少錢
- 用戶白名單：只有授權用戶可用

### 錯誤報告系統 (`src/core/testing/error_reporter.py`)

| 函數 | 用途 |
|------|------|
| `report_test_failure()` | ❌ 測試失敗通知 |
| `report_module_error()` | ⚠️ 模組錯誤通知 |
| `report_system_error()` | 🚨 系統嚴重錯誤通知 |

### 通知系統 (`src/core/utils/notifier.py`)

| 方法 | 用途 |
|------|------|
| `notify()` | 統一通知 |
| `info()` | 資訊通知 |
| `warning()` | 警告通知 |
| `error()` | 錯誤通知 |
| `success()` | 成功通知 |

**支援後端：** console, callback (未來: telegram, slack)

### 配置

```bash
# .env
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_ALLOWED_USERS=123456789,987654321
OLLAMA_URL=http://localhost:11434
OPENAI_API_KEY=sk-xxx
```

### 待實現功能

- [ ] 進化系統通知 (PR 創建、模組生成)
- [ ] 排行榜更新通知
- [ ] 每日品質報告
- [ ] 互動式工作流執行

---

## ⚙️ 配置系統 (Configuration)

### 向量資料庫配置 (`config/vector_config.yaml`)

| 配置項 | 值 | 說明 |
|--------|-----|------|
| `vector_db.type` | qdrant | 向量資料庫類型 |
| `vector.model` | nomic-embed-text | Ollama 嵌入模型 |
| `vector.dimension` | 768 | 向量維度 |
| `vector.distance` | cosine | 距離計算方式 |
| `chunk.size` | 600 tokens | 切塊大小 |
| `chunk.overlap` | 100 tokens | 重疊大小 |
| `chunk.strategy` | semantic | 切分策略 |
| `retrieval.method` | hybrid | 檢索方法 |
| `retrieval.top_k` | 5 | 初始檢索數量 |
| `retrieval.score_threshold` | 0.5 | 相似度門檻 |
| `mmr.diversity` | 0.3 | MMR 多樣性參數 |
| `mmr.final_k` | 3 | MMR 後保留數量 |

### 記憶系統配置 (`config/memory_config.yaml`)

**雙層記憶架構：**

| 層級 | 名稱 | 儲存 | 用途 |
|------|------|------|------|
| Layer 1 | JobMemory | PostgreSQL | 短期任務記憶 |
| Layer 2 | Knowledge | Qdrant | 長期知識庫 |

**JobMemory 保留策略：**

| 項目 | 保留時間 |
|------|----------|
| 已完成任務 | 7 天 |
| 失敗任務 | 30 天 |
| 進行中超時 | 3 天視為失敗 |
| 對話訊息上限 | 500 條/任務 |

**知識類型：**

| 類型 | 說明 | 永久保存 |
|------|------|----------|
| `spec` | 模組規格 | ✅ |
| `module` | 模組實現 | ✅ |
| `lesson` | 經驗教訓 | ✅ |
| `error_log` | 錯誤日誌 | ❌ (90天) |

**知識提取規則：**
- 成功任務 → 提取模組組合、最佳實踐
- PR 審查 → 提取代碼品質經驗
- 失敗案例 → 提取常見錯誤、能力缺口

### 安全配置 (`config/safety.yaml`)

**Kill Switch：**

| 開關 | 說明 |
|------|------|
| `ai_automation_enabled` | AI 自動化總開關 |
| `auto_merge_enabled` | 自動合併開關 |
| `auto_rollback_enabled` | 自動回滾開關 |

**模組存取控制：**

| 策略 | 說明 |
|------|------|
| `blacklist` | 預設允許，黑名單禁止 |
| `whitelist` | 預設禁止，白名單允許 |

**黑名單 (禁止自動合併)：**
- `file.delete` - 檔案刪除
- `file.move` - 檔案移動
- `database.drop` - 資料庫刪除
- `bash.execute` - Shell 執行
- `system.*` - 系統操作

**速率限制：**

| 限制 | 值 |
|------|-----|
| 每小時自動合併 | 3 次 |
| 每日自動合併 | 10 次 |
| 每週自動合併 | 30 次 |
| 回滾後冷卻 | 30 分鐘 |

**品質門檻：**

| 門檻 | 值 |
|------|-----|
| 自動合併通過率 | ≥ 98% |
| 最小測試次數 | 10 次 |
| 最大性能退化 | 10% |
| 回滾觸發 - 通過率下降 | > 5% |
| 回滾觸發 - 絕對通過率 | < 95% |
| 回滾觸發 - 連續失敗 | 3 次 |

---

## 🗄️ 資料庫結構 (Database Schema)

### PostgreSQL 表結構 (`src/core/metrics/db_schema.sql`)

**module_metrics** - 模組生成指標

| 欄位 | 類型 | 說明 |
|------|------|------|
| module_name | VARCHAR(255) | 模組名稱 |
| initial_score | FLOAT | 初始分數 |
| final_score | FLOAT | 最終分數 |
| attempts | INTEGER | 嘗試次數 |
| success | BOOLEAN | 是否成功 |
| model_used | VARCHAR(50) | 使用模型 |
| total_time_seconds | FLOAT | 總耗時 |
| metadata | JSONB | 額外資料 |

**refine_iterations** - 精煉迭代記錄

| 欄位 | 類型 | 說明 |
|------|------|------|
| iteration_number | INTEGER | 迭代次數 |
| score_before | FLOAT | 迭代前分數 |
| score_after | FLOAT | 迭代後分數 |
| issues_before | JSONB | 迭代前問題 |
| issues_after | JSONB | 迭代後問題 |
| strategy_used | VARCHAR(50) | 使用策略 |
| code_similarity | FLOAT | 代碼相似度 |

**issue_stats** - 問題統計

| 欄位 | 類型 | 說明 |
|------|------|------|
| issue_type | VARCHAR(100) | 問題類型 |
| severity | VARCHAR(20) | 嚴重程度 |
| occurrence_count | INTEGER | 出現次數 |
| total_deduction | FLOAT | 總扣分 |

**convergence_events** - 收斂事件

| 欄位 | 類型 | 說明 |
|------|------|------|
| convergence_reason | VARCHAR(50) | 收斂原因 |
| confidence | FLOAT | 信心度 |
| score_at_convergence | FLOAT | 收斂時分數 |

---

## 🏷️ 向量元數據結構 (Vector Schema)

### VectorType (內容類型)

| 類型 | 說明 |
|------|------|
| `error` | 錯誤記錄 |
| `fix` | 修復方案 |
| `module` | 模組文件 |
| `practice` | 練習記錄 |
| `architecture` | 架構文件 |
| `pain_point` | 痛點記錄 |

### VectorCategory (領域分類)

| 分類 | 說明 |
|------|------|
| `browser` | 瀏覽器相關 |
| `crawler` | 爬蟲相關 |
| `ollama` | Ollama 相關 |
| `vector_db` | 向量資料庫 |
| `evolution` | 進化系統 |
| `dependency` | 依賴管理 |
| `general` | 通用 |

### VectorImportance (重要性)

| 等級 | 說明 |
|------|------|
| `critical` | 關鍵 |
| `high` | 高 |
| `medium` | 中 |
| `low` | 低 |

### VectorStatus (狀態)

| 狀態 | 說明 |
|------|------|
| `active` | 啟用中 |
| `deprecated` | 已棄用 |
| `archived` | 已歸檔 |

### VectorSource (來源)

| 來源 | 說明 |
|------|------|
| `manual` | 手動創建 |
| `error_solver` | 錯誤解決器 |
| `evolution_pipeline` | 進化管道 |
| `training` | 訓練系統 |
| `documentation` | 文件系統 |

---

## 🔑 環境變數 (Environment Variables)

### 必要配置

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_ALLOWED_USERS=123456789

# PostgreSQL (Neon 推薦)
POSTGRES_HOST=xxx.neon.tech
POSTGRES_PORT=5432
POSTGRES_DB=flyto2_jobs
POSTGRES_USER=xxx
POSTGRES_PASSWORD=xxx

# Qdrant Cloud
QDRANT_URL=https://xxx.cloud.qdrant.io:6333
QDRANT_API_KEY=xxx

# LLM
OPENAI_API_KEY=sk-xxx
OLLAMA_URL=http://localhost:11434
```

### 可選配置

```bash
# MySQL (備選)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=flyto2_jobs
MYSQL_USER=root
MYSQL_PASSWORD=password
```

---

## 🖥️ CLI 系統 (Command Line Interface)

### 執行方式

```bash
# 互動模式 (選擇工作流)
python -m flyto2.src.cli.main

# 直接執行工作流
python -m flyto2.src.cli.main workflows/example.yaml

# 帶參數執行 (4 種方式)
--params '{"key":"value"}'
--params-file params.json
--env-file .env.production
--param key=value
```

### i18n 多語言支援

| 語言 | 檔案 |
|------|------|
| English | `i18n/en.json` |
| 中文 | `i18n/zh.json` |
| 日本語 | `i18n/ja.json` |

### CLI 翻譯鍵值

| 鍵值 | 說明 |
|------|------|
| `cli.welcome` | 歡迎訊息 |
| `cli.available_workflows` | 可用工作流 |
| `cli.workflow_completed` | 執行成功 |
| `status.success/failed/running` | 狀態文字 |
| `phase2.execution.*` | 執行相關 |
| `phase2.security.*` | 安全相關 |
| `phase2.permissions.*` | 權限名稱 |

---

## 🌐 Web API 端點

### 模組 API (`/api/modules`)

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/modules/list` | GET | 列出所有模組 |
| `/api/modules/detail/{id}` | GET | 模組詳情 |
| `/api/modules/categories` | GET | 模組分類 |
| `/api/modules/schema/{id}` | GET | 參數結構 |
| `/api/modules/validate` | POST | 驗證參數 |
| `/api/modules/search` | GET | 搜尋模組 |

**查詢參數：** `category`, `tags`, `lang` (en/zh/ja)

---

## 📝 E2E 測試工作流結構

```yaml
id: image_dog_to_svg
version: 1
name: "Download dog image and convert to SVG"
tags: [image, e2e, autonomous]

entry:
  engine: smart_executor
  mode: autonomous
  max_attempts: 3
  timeout_seconds: 300

expectations:
  success_mode: "all"
  checks:
    - type: file_exists
    - type: file_size
    - type: file_content_startswith
    - type: module_usage
```

### E2E 檢查類型

| 類型 | 說明 |
|------|------|
| `file_exists` | 檔案存在 |
| `file_glob_any` | 符合 pattern |
| `file_size` | 檔案大小 |
| `file_content_startswith` | 內容開頭 |
| `module_usage` | 模組使用 |

---

## 🔐 權限系統 (Permissions)

| 權限 | 說明 |
|------|------|
| `network.access` | 網路存取 |
| `file.read` | 檔案讀取 |
| `file.write` | 檔案寫入 |
| `browser.launch` | 瀏覽器啟動 |
| `browser.read` | 瀏覽器讀取 |
| `system.process` | 系統處理 |
| `database.read` | 資料庫讀取 |
| `database.write` | 資料庫寫入 |
| `ai.api` | AI API |

### Phase 2 模組元數據

| 屬性 | 說明 |
|------|------|
| `timeout` | 超時時間 (秒) |
| `retryable` | 可重試 |
| `max_retries` | 最大重試次數 |
| `concurrent_safe` | 並發安全 |
| `requires_credentials` | 需要憑證 |
| `handles_sensitive_data` | 敏感資料 |
| `required_permissions` | 必要權限 |

---

## 📁 目錄結構

```
flyto2/
├── src/
│   ├── core/
│   │   ├── engine/          # 工作流引擎
│   │   ├── browser/         # 瀏覽器自動化
│   │   ├── modules/         # 模組系統
│   │   │   ├── atomic/      # 原子模組 (180+)
│   │   │   ├── third_party/ # 第三方整合
│   │   │   └── composite/   # 複合模組
│   │   ├── meta/            # 品質系統
│   │   ├── evolution/       # 進化系統
│   │   ├── knowledge/       # 知識系統
│   │   ├── memory/          # 記憶系統
│   │   ├── healing/         # 修復系統
│   │   ├── training/        # 訓練系統
│   │   ├── competition/     # 競賽系統
│   │   ├── leaderboard/     # 排行榜系統
│   │   ├── performance/     # 性能系統
│   │   ├── retrieval/       # 檢索系統
│   │   ├── intelligence/    # 智能系統
│   │   ├── audit/           # 審計系統
│   │   ├── testing/         # 測試系統
│   │   ├── metrics/         # 指標系統
│   │   ├── ai/              # AI 協調
│   │   ├── agent/           # Agent 系統
│   │   ├── analysis/        # 分析系統
│   │   ├── executor/        # 執行系統
│   │   └── utils/           # 工具集
│   ├── cli/                 # CLI 介面
│   └── ui/web/backend/      # Web API
├── scripts/                 # 腳本工具
├── workflows/               # 工作流範例
├── tests/                   # 測試套件
├── metrics/                 # 指標資料
└── docs/                    # 文件
```
