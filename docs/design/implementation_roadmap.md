# Flyto2 V3 Implementation Roadmap

## 總覽

將 Flyto2 升級到真正的自動演化系統，具備：
1. **Auto-Refine Engine**: 自動修復低分模組
2. **Metrics Dashboard**: 品質監控與分析

---

## 📋 當前狀態 (2025-12-04)

### ✅ 已完成
- [x] QualityCheckerV2 (10條品質規則)
- [x] AutoRefiner V3 (同步版本，4輪修復)
- [x] EnhancedModuleGenerator (GPT-4o 生成 + 驗證)
- [x] 模板約束 prompt (減少嵌套函數)
- [x] IssueConverter (支援更多問題類型)
- [x] RoundPlanner (4輪修復計劃)
- [x] IssueAnalyzer (22 tests passed)
- [x] EnhancedPromptBuilder with strategy selection (18 tests passed)
- [x] CodeDiffer (23 tests passed)
- [x] ConvergenceDetector (22 tests passed)
- [x] Auto-Refine Integration Tests (7 tests passed, total 92 tests)
- [x] Metrics Dashboard - PostgreSQL schema design
- [x] Metrics Dashboard - DatabaseManager with cloud PostgreSQL
- [x] Metrics Dashboard - MetricsCollector (16 tests passed)
- [x] Metrics Dashboard - API Server (19 tests passed)

### ⚠️ 進行中
- [ ] 測試 AutoRefiner V3 效果 (目標: 9.5+ 達成率 85%+)
- [ ] 優化 prompt 策略
- [ ] Metrics Dashboard - Data collection integration
- [ ] 集成 Auto-Refine Engine 到 EnhancedModuleGenerator

### ❌ 未開始
- [ ] Metrics Dashboard UI

---

## 🗓 實作計劃

### Week 1: Auto-Refine Engine (核心功能)

#### Day 1-2: 核心組件實作
**目標**: 實作 Auto-Refine 核心組件

**Tasks**:
1. ✅ 實作 IssueAnalyzer
   - 解析 QualityReport
   - 分類問題類型
   - 評估優先級
   ```python
   src/core/meta/issue_analyzer.py
   ```

2. ✅ 增強 PromptBuilder
   - 上下文感知 prompt
   - 問題類型範例庫
   - 漸進式警告（iteration 越多越嚴格）
   ```python
   src/core/meta/refine_prompt_builder.py
   ```

3. ✅ 實作 CodeDiffer
   - 檢測代碼變化
   - 防止無效循環
   ```python
   src/core/meta/code_differ.py
   ```

**驗證**:
```bash
pytest tests/test_issue_analyzer.py
pytest tests/test_prompt_builder.py
pytest tests/test_code_differ.py
```

#### Day 3-4: 策略與收斂

**Tasks**:
1. ✅ 實作 RefineStrategySelector
   - 多種修復策略
   - 自適應選擇
   ```python
   src/core/meta/strategy_selector.py
   ```

2. ✅ 實作 ConvergenceDetector
   - 檢測收斂狀態
   - 防止震盪
   ```python
   src/core/meta/convergence_detector.py
   ```

3. ✅ 集成到 EnhancedModuleGenerator
   ```python
   # 在 enhanced_module_generator.py 中使用新組件
   ```

**驗證**:
```bash
# 完整流程測試
python test_auto_refine_complete.py
```

#### Day 5: 測試與優化

**Tasks**:
1. 運行大規模測試 (50+ 模組)
2. 收集數據分析效果
3. 調整 prompt 和策略
4. 性能優化

**目標指標**:
- 成功率: > 85%
- 平均迭代: < 2.0
- 平均提升: > 1.0 分

---

### Week 2: Metrics Dashboard (監控系統)

#### Day 6-7: 數據層

**Tasks**:
1. ✅ 設計數據庫 schema
   ```sql
   data/metrics/schema.sql
   ```

2. ✅ 實作 MetricsCollector
   ```python
   src/core/metrics/collector.py
   ```

3. ✅ 在現有系統中埋點
   - QualityCheckerV2
   - AutoRefineEngine
   - E2E Runner (之後實作)

4. ✅ 數據庫初始化腳本
   ```python
   src/core/metrics/init_db.py
   ```

**驗證**:
```bash
# 初始化數據庫
python -m src.core.metrics.init_db

# 運行幾次生成，確認數據有寫入
python test_metrics_collection.py

# 檢查數據庫
sqlite3 data/metrics/metrics.db "SELECT COUNT(*) FROM module_quality"
```

#### Day 8-9: API 層

**Tasks**:
1. ✅ 實作 FastAPI endpoints
   ```python
   src/api/metrics_api.py
   ```
   - GET /api/metrics/modules
   - GET /api/metrics/modules/{id}/history
   - GET /api/metrics/refine/summary
   - GET /api/metrics/e2e/summary
   - GET /api/metrics/models

2. ✅ 添加數據聚合查詢
3. ✅ API 文檔（Swagger）

**驗證**:
```bash
# 啟動 API server
uvicorn src.api.metrics_api:app --reload --port 9002

# 測試 endpoints
curl http://localhost:9002/api/metrics/modules
curl http://localhost:9002/api/metrics/refine/summary

# 查看 API 文檔
open http://localhost:9002/docs
```

#### Day 10-12: UI 層

**Tasks**:
1. ✅ 設計 Dashboard layout (Figma/Sketch)
2. ✅ 實作核心組件
   ```vue
   src/ui/web/frontend/src/views/MetricsDashboard.vue
   src/ui/web/frontend/src/components/metrics/
     - OverviewCard.vue
     - QualityTrendChart.vue
     - RefinePerformanceTable.vue
     - E2ESuccessRates.vue
     - ModelComparison.vue
   ```

3. ✅ API 集成
   ```javascript
   src/ui/web/frontend/src/api/metrics.js
   ```

4. ✅ 路由集成
   ```javascript
   // router/index.js
   {
     path: '/metrics',
     name: 'Metrics',
     component: () => import('@/views/MetricsDashboard.vue')
   }
   ```

**驗證**:
```bash
# 啟動前端
cd src/ui/web/frontend
npm run dev

# 訪問 dashboard
open http://localhost:5173/metrics
```

---

### Week 3: E2E 驗證系統

#### Day 13-14: E2E 規格與 Runner

**Tasks**:
1. ✅ 設計 E2E 任務規格 (YAML)
   ```yaml
   workflows/e2e/image_dog_to_svg.yaml
   ```

2. ✅ 實作 E2E Runner
   ```python
   scripts/e2e_runner.py
   ```
   - 讀取 YAML 規格
   - 執行 SmartExecutor
   - 驗證 expectations
   - 記錄結果到 metrics

3. ✅ 實作 Check 驗證器
   - file_exists
   - file_glob_any
   - file_size
   - file_content_startswith
   - module_usage

**驗證**:
```bash
# 運行單個 E2E 任務
python scripts/e2e_runner.py --task workflows/e2e/image_dog_to_svg.yaml

# 運行所有 E2E 任務
python scripts/e2e_runner.py --dir workflows/e2e
```

#### Day 15: CI/CD 集成

**Tasks**:
1. ✅ GitHub Actions 配置
   ```yaml
   .github/workflows/ci.yml
   ```

2. ✅ GitLab CI 配置
   ```yaml
   .gitlab-ci.yml
   ```

3. ✅ 配置品質門檻
   - Unit tests 必過
   - Quality score >= 9.8
   - E2E success rate >= 80%

**驗證**:
```bash
# 本地運行 CI 流程
./run_ci_local.sh
```

---

## 📊 成功指標 (KPIs)

### Auto-Refine Engine
- ✅ **成功率**: ≥ 85% (達到目標分數)
- ✅ **平均迭代**: ≤ 2.0
- ✅ **平均提升**: ≥ 1.0 分
- ✅ **時間效率**: ≤ 30 秒/次

### Metrics Dashboard
- ✅ **數據完整性**: 100% 埋點覆蓋
- ✅ **實時性**: ≤ 5 秒延遲
- ✅ **可用性**: 99.9% uptime
- ✅ **性能**: API 響應 < 500ms

### E2E Validation
- ✅ **任務覆蓋**: ≥ 10 個關鍵任務
- ✅ **成功率**: ≥ 80%
- ✅ **執行時間**: ≤ 60 秒/任務

---

## 🛠 開發工具與依賴

### 新增依賴

```bash
# Auto-Refine Engine
pip install openai==1.3.0        # LLM client
pip install difflib              # Code diff (內建)

# Metrics Dashboard
pip install fastapi==0.104.1     # API server
pip install uvicorn==0.24.0      # ASGI server
pip install sqlite3              # Database (內建)

# E2E Runner
pip install pyyaml==6.0.1        # YAML parser
pip install pytest-asyncio       # Async testing

# Frontend (已有)
# Vue 3, Chart.js, Axios
```

### 開發環境

```bash
# 虛擬環境
python -m venv .venv
source .venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 前端
cd src/ui/web/frontend
npm install
```

---

## 📁 目錄結構變化

```
flyto2/
  src/
    core/
      meta/
        auto_refiner_v3.py               # ✅ 已實作
        issue_analyzer.py                # 🆕 待實作
        refine_prompt_builder.py         # 🆕 待實作
        strategy_selector.py             # 🆕 待實作
        convergence_detector.py          # 🆕 待實作
        code_differ.py                   # 🆕 待實作

      metrics/
        __init__.py                      # 🆕
        collector.py                     # 🆕 數據收集器
        init_db.py                       # 🆕 數據庫初始化

    api/
      metrics_api.py                     # 🆕 Metrics API

    ui/web/frontend/src/
      views/
        MetricsDashboard.vue             # 🆕
      components/metrics/
        OverviewCard.vue                 # 🆕
        QualityTrendChart.vue            # 🆕
        RefinePerformanceTable.vue       # 🆕
        E2ESuccessRates.vue              # 🆕
        ModelComparison.vue              # 🆕
      api/
        metrics.js                       # 🆕

  scripts/
    e2e_runner.py                        # 🆕 E2E 任務執行器
    run_ci_local.sh                      # 🆕 本地 CI 腳本

  workflows/e2e/
    image_dog_to_svg.yaml                # 🆕 E2E 任務規格
    text_summarize.yaml                  # 🆕
    scrape_and_analyze.yaml              # 🆕

  data/
    metrics/
      metrics.db                         # 🆕 SQLite 數據庫
      schema.sql                         # 🆕 數據庫 schema

  docs/design/
    auto_refine_engine_design.md         # ✅ 已完成
    metrics_dashboard_design.md          # ✅ 已完成
    e2e_validation_design.md             # 🆕 待補充

  .github/workflows/
    ci.yml                               # 🆕 GitHub Actions

  .gitlab-ci.yml                         # 🆕 GitLab CI
```

---

## 🧪 測試策略

### 單元測試
```bash
# Auto-Refine 組件
pytest tests/meta/test_issue_analyzer.py
pytest tests/meta/test_prompt_builder.py
pytest tests/meta/test_convergence_detector.py

# Metrics 收集
pytest tests/metrics/test_collector.py

# API
pytest tests/api/test_metrics_api.py
```

### 集成測試
```bash
# 完整 Auto-Refine 流程
pytest tests/integration/test_auto_refine_flow.py

# E2E 任務
pytest tests/integration/test_e2e_runner.py
```

### 性能測試
```bash
# 大規模模組生成
python tests/performance/test_batch_generation.py

# API 性能
locust -f tests/performance/locustfile.py
```

---

## 🚀 部署

### 本地開發
```bash
# Backend API
uvicorn src.api.metrics_api:app --reload --port 9002

# Frontend
cd src/ui/web/frontend && npm run dev

# Full app (Electron)
npm run dev
```

### 生產環境
```bash
# Build frontend
cd src/ui/web/frontend && npm run build

# Build Electron app
npm run build

# 或部署為 web app
docker-compose up -d
```

---

## 📈 監控與告警

### 關鍵指標監控

```yaml
# config/alerts.yaml
alerts:
  - name: module_quality_degradation
    condition: avg_score < 9.3
    action: slack_notification

  - name: refine_success_rate_low
    condition: refine_success_rate < 0.80
    action: email_alert

  - name: e2e_failure_spike
    condition: e2e_failure_rate > 0.30
    action: pager_duty

  - name: token_usage_high
    condition: daily_tokens > 1000000
    action: slack_notification
```

### 日誌收集

```python
# 結構化日誌
import structlog

logger = structlog.get_logger()

logger.info(
    "auto_refine_completed",
    module_id="image.download",
    initial_score=8.5,
    final_score=9.6,
    iterations=2,
    success=True
)
```

---

## 🎯 里程碑

### Milestone 1: Auto-Refine Engine (Week 1)
- [ ] 所有核心組件實作完成
- [ ] 測試達成率 ≥ 85%
- [ ] 集成到 EnhancedModuleGenerator

### Milestone 2: Metrics Dashboard (Week 2)
- [ ] 數據層完成
- [ ] API 完成
- [ ] UI 完成
- [ ] 可視化質量趨勢

### Milestone 3: E2E Validation (Week 3)
- [ ] E2E Runner 完成
- [ ] 10+ 任務規格
- [ ] CI/CD 集成
- [ ] 80%+ 任務成功率

### Milestone 4: Production Ready (Week 4)
- [ ] 性能優化
- [ ] 文檔完善
- [ ] 部署指南
- [ ] 用戶培訓

---

## 🤝 協作方式

### 分支策略
```
main           # 穩定版本
develop        # 開發分支
feature/*      # 功能分支
  - feature/auto-refine-engine
  - feature/metrics-dashboard
  - feature/e2e-validation
```

### Commit Message 格式
```
feat: Add IssueAnalyzer component
fix: Fix convergence detection bug
docs: Update Auto-Refine design doc
test: Add unit tests for PromptBuilder
refactor: Optimize MetricsCollector performance
```

### Code Review Checklist
- [ ] 代碼符合 PEP 8
- [ ] 單元測試覆蓋率 ≥ 80%
- [ ] 文檔字符串完整
- [ ] 無安全漏洞
- [ ] 性能符合要求

---

## 📚 參考資源

### 設計文檔
- [Auto-Refine Engine Design](./auto_refine_engine_design.md)
- [Metrics Dashboard Design](./metrics_dashboard_design.md)
- [E2E Validation Design](./e2e_validation_design.md)

### 外部文檔
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue 3 Guide](https://vuejs.org/guide/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

---

## ✅ 下一步行動

### 立即開始（優先級最高）
1. **完成當前測試**
   ```bash
   # 運行 dog photo SVG 測試，驗證 V3 效果
   python test_dog_photo_svg_zero_assistance.py
   ```

2. **實作 IssueAnalyzer**
   ```bash
   # 創建文件並實作
   touch src/core/meta/issue_analyzer.py
   ```

3. **初始化 Metrics 數據庫**
   ```bash
   # 創建數據庫結構
   python -m src.core.metrics.init_db
   ```

### 本週目標（Week 1）
- [ ] Auto-Refine V3 測試通過（9.5+ 達成率 ≥ 85%）
- [ ] 實作完整 Auto-Refine Engine
- [ ] 開始 Metrics 數據收集

### 本月目標
- [ ] Auto-Refine Engine 生產就緒
- [ ] Metrics Dashboard 上線
- [ ] E2E 驗證系統運行
- [ ] CI/CD 全自動化

---

**現在就開始！讓 Flyto2 成為真正的自動演化系統 🚀**
