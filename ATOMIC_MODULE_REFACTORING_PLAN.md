# Atomic Module Refactoring Plan

**日期**: 2025-12-03
**目標**: 將所有模組拆分為真正的原子級別（One Module = One File）

---

## 🚨 當前問題

### 違反原子設計原則

**原子設計理念**: 每個模組應該：
- ✅ 只做一件事
- ✅ 獨立檔案
- ✅ < 150 行程式碼
- ✅ 可獨立測試

**當前狀態**: ❌ 嚴重違反

| 檔案 | 模組數 | 行數 | 應拆分成 |
|------|--------|------|----------|
| `array/advanced_operations.py` | 7 | 704 | 7 個獨立檔案 |
| `browser_ops/operations.py` | 8 | 626 | 8 個獨立檔案 |
| `data/transformation.py` | 5 | 553 | 5 個獨立檔案 |
| `utility/helpers.py` | 5 | 540 | 5 個獨立檔案 |
| `datetime/operations.py` | 4 | 479 | 4 個獨立檔案 |
| `math/advanced_operations.py` | 5 | 417 | 5 個獨立檔案 |
| `object/operations.py` | 5 | 386 | 5 個獨立檔案 |
| `string/operations.py` | 3 | 330 | 3 個獨立檔案 |
| `file/advanced_operations.py` | 3 | 325 | 3 個獨立檔案 |
| `array/operations.py` | 3 | 312 | 3 個獨立檔案 |
| `analysis/html.py` | 6 | 269 | 6 個獨立檔案 |
| `training/practice.py` | 5 | 200 | 5 個獨立檔案 |
| `competition/speed_race.py` | 4 | 186 | 4 個獨立檔案 |

**總計**: 60+ 模組需要拆分成獨立檔案

---

## 📊 Three-Tier Escalation 實際狀態

### ✅ 已實作部分

1. **Ollama 整合** ✅
   - 檔案: `scripts/interactive_evolution_bot.py:95-130`
   - 函數: `ask_ollama(prompt, system_prompt) -> (response, confidence)`
   - Confidence estimation 機制

2. **OpenAI Fallback** ✅
   - 檔案: `scripts/interactive_evolution_bot.py:162-189`
   - 函數: `ask_openai(prompt, system_prompt) -> response`

3. **Human Approval Flow** ✅
   - 檔案: `scripts/interactive_evolution_bot.py:1090-1111`
   - 低信心度時 (< 0.5) 自動詢問使用者
   - 提供 3 個選項: ✅ Approve / 🤔 Guide / 🚀 Escalate to OpenAI

### ❌ 缺少部分

1. **自動 Escalation** ❌
   - 目前: 需要使用者點選 "🚀 Ask OpenAI" 按鈕
   - 應該: confidence < 0.3 時自動 escalate 到 OpenAI
   - 應該: OpenAI 也失敗時自動請求 Human

2. **Escalation 策略配置** ❌
   - 缺少可配置的 threshold
   - 缺少 retry 機制
   - 缺少 fallback chain

### 🔧 修正建議

建立 `src/core/ai/escalation.py`:
```python
class ThreeTierEscalation:
    async def ask(self, prompt, confidence_threshold=0.5):
        # Tier 1: Ollama
        response, confidence = await ask_ollama(prompt)
        if confidence >= confidence_threshold:
            return response

        # Tier 2: Human (via Telegram)
        human_response = await ask_human_approval(prompt, response)
        if human_response.approved:
            return human_response.final_answer

        # Tier 3: OpenAI
        return await ask_openai(prompt)
```

---

## 📋 原子模組拆分方案

### Phase 1: Array Modules（優先）

**當前**: `array/advanced_operations.py` (7 modules, 704 lines)

**拆分為**:
```
src/core/modules/atomic/array/
├── map.py           # array.map
├── reduce.py        # array.reduce
├── join.py          # array.join
├── flatten.py       # array.flatten
├── chunk.py         # array.chunk
├── intersection.py  # array.intersection
└── difference.py    # array.difference
```

**效益**:
- ✅ 每個檔案 80-100 行
- ✅ 職責單一
- ✅ 易於測試
- ✅ 易於維護

### Phase 2: Browser Modules

**當前**: `browser_ops/operations.py` (8 modules, 626 lines)

**拆分為**:
```
src/core/modules/atomic/browser/
├── launch.py        # core.browser.launch
├── goto.py          # core.browser.goto
├── click.py         # core.browser.click
├── type.py          # core.browser.type
├── screenshot.py    # core.browser.screenshot
├── wait.py          # core.browser.wait
├── extract.py       # core.browser.extract
└── press.py         # core.browser.press
```

### Phase 3: Data Transformation Modules

**當前**: `data/transformation.py` (5 modules, 553 lines)

**拆分為**:
```
src/core/modules/atomic/data/
├── json_parse.py       # data.json.parse
├── json_stringify.py   # data.json.stringify
├── csv_read.py         # data.csv.read
├── csv_write.py        # data.csv.write
└── text_template.py    # data.text.template
```

### Phase 4: Utility Helpers

**當前**: `utility/helpers.py` (5 modules, 540 lines)

**拆分為**:
```
src/core/modules/atomic/utility/
├── delay.py            # utility.delay
├── random_number.py    # utility.random.number
├── random_string.py    # utility.random.string
├── datetime_now.py     # utility.datetime.now
└── hash_md5.py         # utility.hash.md5
```

### Phase 5: HTML Analysis

**當前**: `analysis/html.py` (6 modules, 269 lines)

**拆分為**:
```
src/core/modules/atomic/analysis/html/
├── structure.py          # analysis.html.structure
├── find_patterns.py      # analysis.html.find_patterns
├── extract_tables.py     # analysis.html.extract_tables
├── extract_forms.py      # analysis.html.extract_forms
├── extract_metadata.py   # analysis.html.extract_metadata
└── analyze_readability.py # analysis.html.analyze_readability
```

### Phase 6: Training Practice

**當前**: `training/practice.py` (5 modules, 200 lines)

**拆分為**:
```
src/core/modules/atomic/training/
├── practice_analyze.py      # training.practice.analyze
├── practice_infer_schema.py # training.practice.infer_schema
├── practice_execute.py      # training.practice.execute
├── practice_stats.py        # training.practice.stats
└── practice_history.py      # training.practice.history
```

### Phase 7: Speed Race

**當前**: `competition/speed_race.py` (4 modules, 186 lines)

**拆分為**:
```
src/core/modules/atomic/competition/
├── speed_race_run.py        # competition.speed_race.run
├── speed_race_leaderboard.py # competition.speed_race.leaderboard
├── speed_race_history.py    # competition.speed_race.history
└── speed_race_compare.py    # competition.speed_race.compare
```

---

## ⚠️ 功能驗證問題

### 已測試 vs 聲稱完成

**測試檔案數**: 21 個
**聲稱完成模組**: 87 個原子 + 42 個第三方 = 129 個
**測試覆蓋率**: 21/129 = **16.3%**（不是 22.9%）

### 測試覆蓋缺口

**已測試** (21):
```
✅ array: filter, join, map, sort, unique
✅ string: lowercase, replace, reverse, split, trim, uppercase
✅ object: keys, merge
✅ math: abs, round
✅ data: json_parse, json_stringify
✅ training: daily_practice
✅ analysis: html_analysis
✅ meta: module_generator
✅ test: assert
```

**未測試但聲稱完成** (66+):
```
❌ browser: launch, goto, click, type, screenshot, wait, extract, press (8個)
❌ file: read, write, exists, delete, move, copy (6個)
❌ array: reduce, flatten, chunk, intersection, difference (5個)
❌ datetime: format, parse, add, subtract (4個)
❌ utility: delay, random.*, datetime.now, hash.md5 (5個)
❌ 42 個第三方整合模組（全部未測試）
```

---

## 🎯 立即行動項目

### 1. 修正文檔誤導

**COMPLETE_FEATURE_CHECKLIST.md** 需更新:

```markdown
### ❌ 1.1 Three-Tier Escalation
- [x] Ollama 本地 LLM 整合
- [x] Telegram 人工回饋
- [x] OpenAI 作為 fallback
- [ ] 自動選擇適合的 tier  ❌ 手動選擇

狀態: ⏳ PARTIAL (75% - 缺自動 escalation)
```

```markdown
### ⏳ 1.2 Continuous Automated Testing
測試覆蓋率: 22.9% → 16.3% (21/129)
已測試模組: 27 → 21

狀態: ⏳ PARTIAL (16% - 大量模組未測試)
```

### 2. 拆分最大的檔案（Week 1）

優先順序:
1. ✅ `array/advanced_operations.py` → 7 files
2. ✅ `browser_ops/operations.py` → 8 files
3. ✅ `data/transformation.py` → 5 files

### 3. 為未測試模組建立測試（Week 2）

優先級 P0（核心功能）:
1. Browser 模組 (8個)
2. File 模組 (6個)
3. Datetime 模組 (4個)

### 4. 實作自動 Escalation（Week 1）

建立:
- `src/core/ai/escalation.py`
- `src/core/ai/confidence_estimator.py`
- 測試: `workflows/_test/test_three_tier_escalation.yaml`

---

## 📐 拆分原則

### ✅ 良好範例

```python
# src/core/modules/atomic/array/map.py
@register_module(module_id='array.map', ...)
class ArrayMapModule(BaseModule):
    def validate_params(self):
        self.array = self.params.get('array', [])
        self.operation = self.params.get('operation')

    async def execute(self):
        # 單一職責: 映射轉換
        result = [self.transform(item) for item in self.array]
        return {"result": result}
```

**特徵**:
- ✅ 單一檔案
- ✅ < 100 行
- ✅ 單一職責
- ✅ 獨立測試

### ❌ 違反原則範例

```python
# array/advanced_operations.py (704 lines)
class ArrayMapModule: ...      # Line 96-132
class ArrayReduceModule: ...   # Line 219-256
class ArrayJoinModule: ...     # Line 325-342
class ArrayFlattenModule: ...  # Line 412-445
class ArrayChunkModule: ...    # Line 515-539
class ArrayIntersectionModule: ... # Line 592-616
class ArrayDifferenceModule: ... # Line 678-704
```

**問題**:
- ❌ 7 個模組在一個檔案
- ❌ 704 行太長
- ❌ 職責混雜
- ❌ 難以維護

---

## 🛠️ 實施計畫

### Week 1: Critical Refactoring
- [ ] 拆分 Array modules (7 files)
- [ ] 拆分 Browser modules (8 files)
- [ ] 拆分 Data modules (5 files)
- [ ] 實作自動 Escalation
- [ ] 更新 COMPLETE_FEATURE_CHECKLIST.md

### Week 2: Testing & Documentation
- [ ] 為 Browser modules 建立測試 (8)
- [ ] 為 File modules 建立測試 (6)
- [ ] 為 Datetime modules 建立測試 (4)
- [ ] 更新 TEST_COVERAGE_REPORT.md

### Week 3: Remaining Modules
- [ ] 拆分 Utility modules (5 files)
- [ ] 拆分 HTML Analysis (6 files)
- [ ] 拆分 Training modules (5 files)
- [ ] 拆分 Competition modules (4 files)

### Week 4: Quality & Integration
- [ ] 所有模組測試覆蓋率 > 80%
- [ ] 自動化測試 CI/CD
- [ ] 效能基準測試
- [ ] 文檔完整性檢查

---

## 📈 預期成果

**Before**:
- 16 個大型檔案（200-700行）
- 60+ 個模組混在一起
- 測試覆蓋率 16.3%
- 維護困難

**After**:
- 129 個獨立檔案
- 1 Module = 1 File
- 測試覆蓋率 > 80%
- 真正的原子設計

**效益**:
- ✅ 易於理解
- ✅ 易於測試
- ✅ 易於維護
- ✅ 易於擴展
- ✅ 符合專案理念

---

**Created**: 2025-12-03
**Status**: Draft - Pending User Approval
