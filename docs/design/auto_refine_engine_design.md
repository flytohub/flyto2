# Auto-Refine Engine 設計文檔

## 概述

Auto-Refine Engine 是 Flyto2 的自動修復系統，負責將未達標的模組自動優化至目標分數。

## 系統架構

```
Input: Generated Module (score < 9.5)
  ↓
┌─────────────────────────────────────┐
│  1. Issue Analyzer                  │
│     - Parse quality report          │
│     - Categorize issues             │
│     - Prioritize fixes              │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│  2. Refine Strategy Selector        │
│     - Choose refine approach        │
│     - Multi-round vs single-shot    │
│     - Determine max iterations      │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│  3. Prompt Builder                  │
│     - Build context-aware prompt    │
│     - Include examples              │
│     - Add constraints               │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│  4. Refine Executor                 │
│     - Call LLM with prompt          │
│     - Extract refined code          │
│     - Validate syntax               │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│  5. Quality Re-Validator            │
│     - Run QualityCheckerV2          │
│     - Compare scores                │
│     - Detect convergence            │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│  6. Convergence Decision            │
│     - Score >= target? → PASS       │
│     - No improvement? → FAIL        │
│     - Max iterations? → FAIL        │
│     - Otherwise → Loop back to #1   │
└─────────────────────────────────────┘
  ↓
Output: Refined Module (score >= 9.5) or FAIL
```

## 核心類設計

### 1. AutoRefineEngine (Main Orchestrator)

```python
class AutoRefineEngine:
    """
    主要的自動修復引擎

    負責：
    - 協調整個修復流程
    - 管理修復歷史
    - 收集統計數據
    """

    def __init__(
        self,
        quality_checker: QualityCheckerV2,
        llm_client: LLMClient,
        max_iterations: int = 5,
        target_score: float = 9.5,
        min_improvement: float = 0.1,
        convergence_patience: int = 2
    ):
        pass

    def refine_module(
        self,
        module_path: str,
        initial_code: str,
        initial_report: QualityReport
    ) -> RefineResult:
        """
        主要修復流程

        Returns:
            RefineResult with:
            - success: bool
            - final_code: str
            - final_score: float
            - iterations: List[IterationResult]
            - metrics: RefineMetrics
        """
        pass
```

### 2. IssueAnalyzer

```python
class IssueAnalyzer:
    """
    分析品質報告中的問題

    負責：
    - 解析 QualityReport
    - 分類問題類型
    - 評估修復優先級
    - 生成修復建議
    """

    @dataclass
    class AnalyzedIssue:
        type: str              # 問題類型
        severity: float        # 嚴重程度 (扣分)
        location: str          # 位置
        message: str           # 描述
        fix_suggestion: str    # 修復建議
        priority: int          # 優先級 (1-5)

    def analyze(self, report: QualityReport) -> List[AnalyzedIssue]:
        """
        分析品質報告

        Returns:
            按優先級排序的問題列表
        """
        pass

    def prioritize(self, issues: List[Issue]) -> List[AnalyzedIssue]:
        """
        優先級規則：
        1. 語法錯誤 > 邏輯錯誤 > 風格問題
        2. 高扣分 > 低扣分
        3. 容易修復 > 複雜修復
        """
        pass
```

### 3. RefineStrategySelector

```python
class RefineStrategySelector:
    """
    選擇修復策略

    策略類型：
    - SINGLE_SHOT: 一次修復所有問題
    - MULTI_ROUND: 分輪修復（V3 當前使用）
    - INCREMENTAL: 增量修復（一個一個修）
    - ADAPTIVE: 自適應（根據問題類型動態選擇）
    """

    def select_strategy(
        self,
        issues: List[AnalyzedIssue],
        current_score: float,
        history: List[IterationResult]
    ) -> RefineStrategy:
        """
        根據問題特徵和歷史選擇最佳策略
        """
        pass
```

### 4. PromptBuilder (Enhanced)

```python
class RefinePromptBuilder:
    """
    構建修復 prompt

    特點：
    - 上下文感知
    - 包含具體範例
    - 漸進式提示（根據迭代次數調整）
    """

    SYSTEM_PROMPT = """You are an expert Python code refiner.
Your task: fix ONLY the specific issues listed below.

CRITICAL RULES:
1. Do NOT change working code
2. Do NOT add new features
3. Do NOT refactor unnecessarily
4. Output ONLY the FULL corrected Python file
5. NO markdown, NO explanations
"""

    def build_refine_prompt(
        self,
        current_code: str,
        issues: List[AnalyzedIssue],
        iteration: int,
        previous_attempts: List[str]
    ) -> str:
        """
        構建修復 prompt

        Prompt 結構：
        1. 系統角色
        2. 當前代碼
        3. 問題列表（按優先級）
        4. 修復範例（如果有類似問題）
        5. 約束條件
        6. 預期輸出格式
        """
        pass

    def _get_fix_examples(self, issue_type: str) -> str:
        """
        獲取該問題類型的修復範例

        例如：
        - nested_function → 展開範例
        - missing_self → self.x 範例
        - placeholder_docstring → 完整文檔範例
        """
        pass

    def _adjust_for_iteration(self, iteration: int) -> str:
        """
        根據迭代次數調整提示強度

        Iteration 1: 正常提示
        Iteration 2: 加強警告
        Iteration 3+: 超強警告 + 負面範例
        """
        pass
```

### 5. CodeDiffer

```python
class CodeDiffer:
    """
    比較代碼差異

    用途：
    - 檢測是否有實質變化
    - 記錄修改歷史
    - 防止無效循環
    """

    def get_diff(self, old_code: str, new_code: str) -> CodeDiff:
        """
        獲取代碼差異

        Returns:
            CodeDiff with:
            - has_changes: bool
            - added_lines: int
            - removed_lines: int
            - modified_lines: int
            - diff_text: str
        """
        pass

    def is_meaningful_change(self, diff: CodeDiff) -> bool:
        """
        判斷是否為有意義的修改

        排除：
        - 僅空白符變化
        - 僅註釋變化
        - 格式調整
        """
        pass
```

### 6. ConvergenceDetector

```python
class ConvergenceDetector:
    """
    檢測收斂狀態

    防止：
    - 無限循環
    - 分數震盪
    - 無效修改
    """

    def check_convergence(
        self,
        history: List[IterationResult]
    ) -> ConvergenceState:
        """
        檢查收斂狀態

        收斂條件：
        1. 達到目標分數 → SUCCESS
        2. N 輪無改進 → STAGNANT
        3. 分數下降 → REGRESSING
        4. 代碼來回變化 → OSCILLATING
        5. 達到最大迭代 → MAX_ITER_REACHED
        """
        pass

    def detect_oscillation(
        self,
        history: List[IterationResult]
    ) -> bool:
        """
        檢測震盪

        如果：
        - 分數 9.0 → 9.2 → 9.0 → 9.2 (震盪)
        - 或代碼 A → B → A → B (循環)

        則判定為震盪，應停止
        """
        pass
```

### 7. RefineMetricsTracker

```python
class RefineMetricsTracker:
    """
    追蹤修復過程指標

    收集：
    - 每輪耗時
    - LLM token 使用
    - 分數變化軌跡
    - 問題類型分佈
    - 修復成功率
    """

    @dataclass
    class RefineMetrics:
        total_iterations: int
        total_time: float
        total_tokens: int
        initial_score: float
        final_score: float
        improvement: float
        success: bool

        # 詳細統計
        iterations_detail: List[IterationMetrics]
        issue_type_counts: Dict[str, int]
        fix_success_by_type: Dict[str, float]

    def track_iteration(
        self,
        iteration: int,
        issues: List[AnalyzedIssue],
        result: IterationResult
    ):
        """記錄單次迭代"""
        pass

    def export_metrics(self) -> RefineMetrics:
        """導出完整指標"""
        pass
```

## 數據結構

### IterationResult

```python
@dataclass
class IterationResult:
    """單次修復迭代結果"""
    iteration: int
    strategy: str

    # 輸入
    issues_before: List[AnalyzedIssue]
    score_before: float
    code_before: str

    # 輸出
    code_after: str
    score_after: float
    issues_after: List[AnalyzedIssue]

    # 過程
    diff: CodeDiff
    improvement: float
    llm_tokens: int
    time_seconds: float

    # 狀態
    success: bool
    convergence_state: str
```

### RefineResult

```python
@dataclass
class RefineResult:
    """完整修復結果"""
    success: bool
    final_code: str
    final_score: float

    initial_score: float
    total_improvement: float

    iterations: List[IterationResult]
    metrics: RefineMetrics

    # 失敗原因（如果失敗）
    failure_reason: Optional[str] = None
    remaining_issues: Optional[List[AnalyzedIssue]] = None
```

## 修復流程詳細設計

### 主流程

```python
def refine_module(self, module_path, initial_code, initial_report):
    """
    完整修復流程
    """
    # 初始化
    history = []
    current_code = initial_code
    current_score = initial_report.score

    # 開始迭代
    for iteration in range(1, self.max_iterations + 1):
        # 1. 分析問題
        issues = self.issue_analyzer.analyze(current_report)

        if not issues:
            # 沒問題但分數不夠 → 可能是閾值問題
            break

        # 2. 選擇策略
        strategy = self.strategy_selector.select(
            issues, current_score, history
        )

        # 3. 構建 prompt
        prompt = self.prompt_builder.build(
            current_code,
            issues,
            iteration,
            [h.code_after for h in history]
        )

        # 4. 執行修復
        refined_code = self.refine_executor.refine(
            prompt,
            strategy
        )

        # 5. 驗證語法
        if not self.validator.is_valid_python(refined_code):
            # 語法錯誤 → 記錄並重試
            continue

        # 6. 檢查差異
        diff = self.differ.get_diff(current_code, refined_code)
        if not diff.has_meaningful_changes:
            # 沒有實質修改 → 可能收斂或卡住
            break

        # 7. 寫入文件並重新評分
        Path(module_path).write_text(refined_code)
        new_report = self.quality_checker.review_module(module_path)

        # 8. 記錄結果
        iter_result = IterationResult(
            iteration=iteration,
            score_before=current_score,
            score_after=new_report.score,
            code_before=current_code,
            code_after=refined_code,
            diff=diff,
            improvement=new_report.score - current_score,
            # ...
        )
        history.append(iter_result)

        # 9. 檢查收斂
        convergence = self.convergence_detector.check(history)

        if convergence == ConvergenceState.SUCCESS:
            # 達標！
            return RefineResult(success=True, ...)
        elif convergence in [STAGNANT, OSCILLATING]:
            # 卡住了
            break

        # 10. 更新狀態
        current_code = refined_code
        current_score = new_report.score
        current_report = new_report

    # 迭代結束但未達標
    return RefineResult(
        success=False,
        failure_reason="Max iterations reached",
        ...
    )
```

## Prompt 範例

### 基礎修復 Prompt

```
You are a Python code refiner. Fix ONLY the listed issues.

CURRENT CODE:
```python
{current_code}
```

ISSUES TO FIX (Priority Order):
1. [CRITICAL] Nested function definition at line 45
   - Current: async def execute inside another async def execute
   - Fix: Remove nested definition, flatten structure

2. [HIGH] Missing self. prefix for variable 'url' at line 23
   - Current: if url.startswith(...)
   - Fix: if self.url.startswith(...)

3. [MEDIUM] Placeholder docstring "Parameter description"
   - Current: url (str): Parameter description
   - Fix: url (str): The URL to download the image from

CONSTRAINTS:
- Output ONLY the full corrected Python file
- NO markdown code blocks
- NO explanations
- DO NOT change working logic
- DO NOT add new features

CORRECT CODE:
```

### 漸進式提示（第 3+ 輪）

```
⚠️ WARNING: This is iteration #{iteration}.
Previous attempts failed to fix these issues.

CRITICAL: You MUST fix ALL issues listed below.

{...rest of prompt...}

REMINDER:
- Double-check EVERY line
- Nested functions are ABSOLUTELY FORBIDDEN
- Use self.variable for ALL instance variables
```

## 與現有系統集成

### 集成到 EnhancedModuleGenerator

```python
class EnhancedModuleGenerator:

    def __init__(self, ...):
        # 添加 AutoRefineEngine
        self.auto_refine_engine = AutoRefineEngine(
            quality_checker=self.quality_checker,
            llm_client=self.llm_client,
            max_iterations=5,
            target_score=9.5
        )

    async def generate_module_with_validation(self, ...):
        # ... 生成初始代碼 ...

        # 品質檢查
        pr_result = self.quality_checker.review_module(module_path)

        if pr_result["score"] < self.MIN_PR_SCORE:
            print(f"🔧 Score {pr_result['score']} < {self.MIN_PR_SCORE}, starting Auto-Refine...")

            # 啟動 Auto-Refine
            refine_result = self.auto_refine_engine.refine_module(
                module_path=module_path,
                initial_code=module_code,
                initial_report=pr_result
            )

            if refine_result.success:
                print(f"✅ Auto-Refine succeeded: {refine_result.final_score}/10.0")
                print(f"   Iterations: {len(refine_result.iterations)}")
                print(f"   Improvement: +{refine_result.total_improvement:.1f}")

                # 使用修復後的代碼
                module_code = refine_result.final_code
                pr_result["score"] = refine_result.final_score
            else:
                print(f"❌ Auto-Refine failed: {refine_result.failure_reason}")
                # 繼續原流程（重新生成）

        # ... 後續流程 ...
```

## 統計數據收集

### 數據存儲結構

```json
{
  "refine_session_id": "uuid",
  "module_name": "image.download",
  "timestamp": "2025-12-04T03:00:00Z",

  "initial": {
    "score": 8.5,
    "issues": [...]
  },

  "final": {
    "score": 9.6,
    "issues": []
  },

  "iterations": [
    {
      "iteration": 1,
      "strategy": "multi_round",
      "score_before": 8.5,
      "score_after": 9.0,
      "improvement": 0.5,
      "issues_fixed": ["nested_function"],
      "time_seconds": 12.3,
      "tokens_used": 2847
    },
    {
      "iteration": 2,
      "score_before": 9.0,
      "score_after": 9.6,
      "improvement": 0.6,
      "issues_fixed": ["placeholder_docstring", "missing_self"],
      "time_seconds": 10.1,
      "tokens_used": 2234
    }
  ],

  "metrics": {
    "total_iterations": 2,
    "total_time": 22.4,
    "total_tokens": 5081,
    "total_improvement": 1.1,
    "success": true
  }
}
```

### 存儲到文件

```python
# data/refine_history/2025-12-04/image_download_uuid.json
```

## 配置選項

```yaml
# config/auto_refine.yaml

auto_refine:
  enabled: true

  limits:
    max_iterations: 5
    max_time_seconds: 300
    max_tokens_per_iteration: 5000

  targets:
    min_score: 9.5
    min_improvement: 0.1

  convergence:
    patience: 2              # N 輪無改進則停止
    oscillation_threshold: 3 # N 次震盪則停止

  strategies:
    default: "multi_round"
    fallback: "single_shot"

  prompt:
    temperature: 0.1
    include_examples: true
    progressive_warning: true
```

## 測試策略

### 單元測試

```python
def test_issue_analyzer():
    """測試問題分析器"""
    report = QualityReport(score=8.5, issues=[...])
    analyzer = IssueAnalyzer()
    issues = analyzer.analyze(report)

    assert len(issues) > 0
    assert issues[0].priority >= issues[-1].priority

def test_convergence_detector():
    """測試收斂檢測"""
    history = [
        IterationResult(score_after=9.0),
        IterationResult(score_after=9.0),
        IterationResult(score_after=9.0),
    ]
    detector = ConvergenceDetector(patience=2)
    state = detector.check_convergence(history)

    assert state == ConvergenceState.STAGNANT
```

### 集成測試

```python
@pytest.mark.asyncio
async def test_full_refine_flow():
    """測試完整修復流程"""
    engine = AutoRefineEngine(...)

    # 使用已知有問題的代碼
    bad_code = """
    async def execute(self):
        async def execute(self):  # 嵌套！
            return {"ok": True}
    """

    result = engine.refine_module(
        module_path="test.py",
        initial_code=bad_code,
        initial_report=QualityReport(score=8.5, ...)
    )

    assert result.success
    assert result.final_score >= 9.5
    assert "async def execute" not in result.final_code.replace("async def execute(self)", "", 1)
```

## 實作優先級

### Phase 1: 核心功能（1-2 天）
- [x] AutoRefiner V3（已完成）
- [x] IssueAnalyzer (已完成 - 22 tests passed)
- [x] Enhanced PromptBuilder (已完成 - 18 tests passed)
- [ ] 基礎集成到 EnhancedModuleGenerator

### Phase 2: 增強功能（2-3 天）
- [x] RefineStrategySelector (已整合到 PromptBuilder)
- [x] ConvergenceDetector (已完成 - 22 tests passed)
- [x] CodeDiffer (已完成 - 23 tests passed)
- [ ] RefineMetricsTracker

### Phase 3: 優化與監控（1-2 天）
- [ ] 統計數據收集
- [ ] 配置文件支持
- [ ] 詳細日誌
- [ ] 性能優化

## 預期效果

### Before Auto-Refine
```
Generate → Score 8.5 → ❌ FAIL → Retry → Score 8.7 → ❌ FAIL → ...
Success Rate: ~10-20%
```

### After Auto-Refine
```
Generate → Score 8.5 → Auto-Refine → Score 9.6 → ✅ PASS
Success Rate: ~85-95%
Average Iterations: 1.8
```

## 監控指標

跟蹤以下指標以評估 Auto-Refine 效能：

1. **成功率**：達到目標分數的比例
2. **平均迭代次數**：成功案例的平均迭代
3. **平均改進幅度**：分數提升量
4. **問題類型修復率**：各類問題的修復成功率
5. **Token 使用效率**：每提升 1 分需要的 token 數
6. **時間效率**：每次修復的平均耗時

---

## Implementation Status

### ✅ Completed Components (2025-12-04)

All core components have been implemented in `src/core/meta/`:

- [x] **AutoRefiner V3** (`auto_refiner_v3.py`) - 92 tests passed
  - Synchronous multi-pass refinement system
  - Integrated with QualityCheckerV2
  - Metrics collection support

- [x] **IssueAnalyzer** (`issue_analyzer.py`) - 22 tests passed
  - Parse and categorize quality issues
  - Priority-based issue filtering

- [x] **Enhanced PromptBuilder** (`enhanced_prompt_builder.py`) - 18 tests passed
  - Context-aware prompt generation
  - Strategy-based prompt selection
  - Iteration-aware prompt escalation

- [x] **CodeDiffer** (`code_differ.py`) - 23 tests passed
  - Detect meaningful code changes
  - Prevent no-op loops

- [x] **ConvergenceDetector** (`convergence_detector.py`) - 22 tests passed
  - Detect stagnation and oscillation
  - Prevent infinite refinement loops

### Integration Status

- [x] Integrated into EnhancedModuleGenerator with metrics support
- [x] End-to-end testing completed (49 tests passed)
- [ ] Performance evaluation (target: 85%+ success rate at 9.5+ score)

### Next Steps

1. ~~Implement IssueAnalyzer and Enhanced PromptBuilder~~ ✅ DONE
2. ~~Integrate into EnhancedModuleGenerator~~ ✅ DONE
3. ~~Run tests to verify functionality~~ ✅ DONE (92 tests passed)
4. **Evaluate performance metrics** (in progress)
5. **Optimize prompts based on data** (pending metrics analysis)
