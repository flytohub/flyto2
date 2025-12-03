# AutoRefiner V2 - 原子化多輪修復架構

## 🎯 設計原則

1. **單一職責** - 每個組件只做一件事
2. **純函數優先** - 無副作用的函數容易測試
3. **清晰資料流** - 輸入輸出明確
4. **可獨立測試** - 每個組件可單獨驗證
5. **可替換組件** - Protocol-based dependency injection

---

## 📦 原子化組件架構

```
┌─────────────────────────────────────────────────────────────┐
│                    MultiPassRefiner                         │
│                  (協調整體多輪流程)                          │
└────────────┬────────────────────────────────────────────────┘
             │
             ├──> IssueConverter
             │    (PR result → Issue list)
             │
             ├──> RoundPlanner
             │    (決定每輪修什麼)
             │
             ├──> For each round:
             │    │
             │    ├──> IssueFilter
             │    │    (過濾 focus issues)
             │    │
             │    ├──> PromptBuilder
             │    │    (構建 system/user prompt)
             │    │
             │    ├──> RoundExecutor
             │    │    (調用 GPT-4o 修復)
             │    │
             │    ├──> CodeValidator
             │    │    (驗證生成的程式碼)
             │    │
             │    └──> QualityChecker
             │         (重新評分)
             │
             └──> RefineResult
                  (返回完整歷史記錄)
```

---

## 🧩 組件說明

### 1. Data Structures (純數據)

```python
Issue          # 單一質量問題
QualityReport  # 質量評估結果
RoundResult    # 單輪修復結果
RefineResult   # 多輪最終結果
```

### 2. IssueFilter (問題過濾器)

```python
# 職責：過濾特定類型的問題
IssueFilter.filter_by_types(issues, ["generic_exception", "nested_try_except"])
# → 返回匹配的 Issue 列表
```

**原子化好處**：可獨立測試過濾邏輯

### 3. IssueConverter (格式轉換器)

```python
# 職責：將 PR result 轉換為標準 Issue 格式
IssueConverter.from_pr_result(pr_result)
# → 返回 List[Issue]
```

**原子化好處**：與 QualityChecker 的格式解耦

### 4. PromptBuilder (Prompt 構建器)

```python
# 職責：構建 system 和 user prompt
PromptBuilder.SYSTEM_PROMPT  # 固定的 system prompt
PromptBuilder.build_user_prompt(round_index, ..., focus_issues)
# → 返回 user prompt string
```

**原子化好處**：可獨立調整 prompt 不影響其他組件

### 5. CodeValidator (程式碼驗證器)

```python
# 職責：驗證生成的程式碼品質
CodeValidator.is_valid_python(code)           # 語法檢查
CodeValidator.strip_markdown(code)            # 清除 markdown
CodeValidator.has_significant_change(old, new)  # 是否真的有改
CodeValidator.check_length_reasonable(old, new) # 防止截斷
```

**原子化好處**：可輕易添加新的驗證規則

### 6. RoundPlanner (輪次規劃器)

```python
# 職責：決定每輪重點修復哪些類型的問題
RoundPlanner.DEFAULT_PLAN = [
    ["generic_exception", "nested_try_except"],     # Round 1
    ["placeholder_docstring", "missing_param_docs"], # Round 2
    ["return_format_inconsistent", "duplicate_imports"], # Round 3
]

RoundPlanner.get_focus_issues_for_round(round_index, all_issues)
# → 返回該輪應該修復的 Issue list
```

**原子化好處**：可輕易自訂修復策略

### 7. RoundExecutor (輪次執行器)

```python
# 職責：執行單一輪的修復
executor = RoundExecutor(openai_api_key)
refined_code = await executor.execute_round(
    round_index=1,
    focus_issues=[...],
    ...
)
# → 返回修復後的程式碼
```

**原子化好處**：可替換成不同的 LLM (Claude, GPT-4, etc.)

### 8. MultiPassRefiner (多輪協調器)

```python
# 職責：協調整個多輪修復流程
refiner = MultiPassRefiner(
    quality_checker=checker,
    openai_api_key=key,
    max_rounds=2,
    target_score=9.5,
)

result = refiner.refine_module(module_path, initial_code, initial_pr_result)
# → 返回 RefineResult (包含完整歷史)
```

**原子化好處**：組合所有原子組件，單一進入點

---

## 🔬 可測試性示例

### 單元測試 IssueFilter

```python
def test_issue_filter():
    issues = [
        Issue("generic_exception", "Generic Exception"),
        Issue("nested_try_except", "Nested try/except"),
        Issue("placeholder_docstring", "Placeholder docs"),
    ]

    filtered = IssueFilter.filter_by_types(
        issues,
        ["generic_exception", "nested_try_except"]
    )

    assert len(filtered) == 2
    assert all(i.type in ["generic_exception", "nested_try_except"] for i in filtered)
```

### 單元測試 CodeValidator

```python
def test_code_validator():
    assert CodeValidator.is_valid_python("print('hello')")
    assert not CodeValidator.is_valid_python("print('hello'")

    code_with_fence = "```python\nprint('hello')\n```"
    assert CodeValidator.strip_markdown(code_with_fence) == "print('hello')"

    old = "def foo(): pass"
    new = "def bar(): return 1"
    assert CodeValidator.has_significant_change(old, new)
```

---

## 🔄 資料流

```
1. Input: module_path, initial_code, initial_pr_result
   ↓
2. IssueConverter: pr_result → List[Issue]
   ↓
3. For each round (1..max_rounds):
   ↓
4. RoundPlanner: all_issues + round_index → focus_issues
   ↓
5. PromptBuilder: focus_issues → (system_prompt, user_prompt)
   ↓
6. RoundExecutor: prompts → refined_code (via GPT-4o)
   ↓
7. CodeValidator: refined_code → validated (syntax, length, changes)
   ↓
8. Write to file & QualityChecker: → new_score, new_issues
   ↓
9. RoundResult: record (before_score, after_score, improvement)
   ↓
10. Check: target reached? improvement significant? → continue or stop
    ↓
11. Output: RefineResult (final_code, final_score, rounds history)
```

---

## 🎯 實際使用

### 在 EnhancedModuleGenerator 中

```python
from src.core.meta.auto_refiner_v2 import MultiPassRefiner

# 當初始生成分數 < 9.5 時
refiner = MultiPassRefiner(
    quality_checker=self.quality_checker,
    openai_api_key=openai_api_key,
    max_rounds=2,
    target_score=9.5,
    min_improvement=0.1,
)

result = refiner.refine_module(
    module_path=module_path,
    initial_code=module_code,
    initial_pr_result=pr_result,
)

# 檢查結果
if result.achieved_target:
    print(f"✅ 達標！{result.initial_score} → {result.final_score}")
else:
    print(f"❌ 未達標：{result.final_score}/10.0")

# 查看每輪歷史
for round_result in result.rounds:
    print(f"Round {round_result.round_index}: "
          f"{round_result.before_score} → {round_result.after_score} "
          f"({round_result.improvement:+.1f})")
```

---

## 🔧 自訂組件

### 自訂修復策略

```python
# 創建自訂的修復計劃
CUSTOM_PLAN = [
    ["generic_exception"],           # Round 1: 只修 exceptions
    ["nested_try_except"],           # Round 2: 只修嵌套
    ["placeholder_docstring"],       # Round 3: 只修文檔
]

# 使用自訂計劃
focus_issues = RoundPlanner.get_focus_issues_for_round(
    round_index,
    all_issues,
    plan=CUSTOM_PLAN  # 傳入自訂計劃
)
```

### 自訂驗證規則

```python
class StrictCodeValidator(CodeValidator):
    @staticmethod
    def check_no_print_statements(code: str) -> bool:
        """額外檢查：不允許 print"""
        return "print(" not in code
```

---

## 📊 優勢總結

| 方面 | 舊版 AutoRefiner | V2 原子化版本 |
|------|-----------------|---------------|
| **可測試性** | 難以單元測試 | 每個組件獨立可測 |
| **可替換性** | 整體替換 | 單一組件替換 |
| **可讀性** | 長函數邏輯複雜 | 清晰的組件職責 |
| **可擴展性** | 修改影響大 | 新增組件不影響舊的 |
| **調試** | 難以定位問題 | 明確的組件邊界 |
| **重用性** | 難以重用部分邏輯 | 任何組件可獨立重用 |

---

## 🚀 未來擴展方向

1. **添加 DiffAnalyzer** - 分析前後程式碼差異
2. **添加 IssueClassifier** - 智能分類問題嚴重程度
3. **添加 HistoryTracker** - 追蹤跨多次生成的修復模式
4. **添加 CostCalculator** - 計算 API 成本
5. **支援多種 LLM** - Claude, GPT-4, 開源模型

---

## 📝 結論

原子化設計讓 AutoRefiner V2：

- ✅ **更可靠** - 每個組件單獨驗證
- ✅ **更靈活** - 可輕易替換或擴展組件
- ✅ **更清晰** - 資料流和職責明確
- ✅ **更易維護** - 修改影響範圍小
- ✅ **更易測試** - 單元測試覆蓋每個組件

這就是**功能能拆就拆，原子化**的實踐！
