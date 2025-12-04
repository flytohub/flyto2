# Metrics Dashboard 設計文檔

## 概述

Metrics Dashboard 是 Flyto2 的品質監控中心，提供模組品質、自動演化效能、E2E 任務成功率等核心指標的可視化。

## 系統架構

```
┌────────────────────────────────────────────────────────────┐
│                    Metrics Dashboard                        │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │  Data        │    │  Aggregation │    │  API         │ │
│  │  Collectors  │───→│  Engine      │───→│  Server      │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│         │                    │                    │         │
│         ↓                    ↓                    ↓         │
│  ┌──────────────────────────────────────────────────────┐ │
│  │              Storage Layer (SQLite / JSON)           │ │
│  └──────────────────────────────────────────────────────┘ │
│                             ↑                               │
│  ┌──────────────────────────────────────────────────────┐ │
│  │         Web UI (Vue 3 / React Dashboard)             │ │
│  │  - Overview                                           │ │
│  │  - Module Quality Trends                             │ │
│  │  - Auto-Refine Performance                           │ │
│  │  - E2E Success Rates                                 │ │
│  │  - Model Comparison                                  │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

## 數據模型設計

### 1. Module Quality Metrics

追蹤每個模組的品質歷史。

#### Schema (SQLite)

```sql
CREATE TABLE module_quality (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id TEXT NOT NULL,
    module_name TEXT NOT NULL,
    version TEXT DEFAULT 'latest',

    -- Quality scores
    score REAL NOT NULL,
    passed BOOLEAN NOT NULL,

    -- Breakdown
    score_breakdown JSON,  -- {"syntax": 10, "style": 9.5, ...}

    -- Issues
    issues JSON,           -- [{"type": "...", "severity": ...}, ...]
    issues_count INTEGER DEFAULT 0,

    -- Metadata
    generated_by TEXT,     -- "manual" | "auto_refine" | "llm_direct"
    llm_model TEXT,        -- "gpt-4o" | "claude-3.7" | ...

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    INDEX idx_module_id (module_id),
    INDEX idx_score (score),
    INDEX idx_created_at (created_at)
);
```

#### JSON Example

```json
{
  "id": 12345,
  "module_id": "image.download",
  "module_name": "ImageDownload",
  "version": "v2.1",
  "score": 9.6,
  "passed": true,
  "score_breakdown": {
    "syntax": 10.0,
    "style": 9.5,
    "documentation": 9.8,
    "error_handling": 9.2,
    "security": 10.0
  },
  "issues": [
    {
      "type": "missing_type_hint",
      "severity": 0.2,
      "message": "Missing type hint for parameter 'timeout'"
    }
  ],
  "issues_count": 1,
  "generated_by": "auto_refine",
  "llm_model": "gpt-4o",
  "created_at": "2025-12-04T03:15:23Z"
}
```

---

### 2. Auto-Refine Performance Metrics

追蹤 Auto-Refine 引擎的表現。

#### Schema

```sql
CREATE TABLE refine_sessions (
    id TEXT PRIMARY KEY,          -- UUID
    module_id TEXT NOT NULL,

    -- Initial state
    initial_score REAL NOT NULL,
    initial_issues JSON,

    -- Final state
    final_score REAL NOT NULL,
    final_issues JSON,

    -- Process
    total_iterations INTEGER NOT NULL,
    strategy TEXT,                -- "multi_round" | "single_shot" | ...
    convergence_state TEXT,       -- "success" | "stagnant" | "max_iter" | ...

    -- Performance
    total_time_seconds REAL,
    total_tokens INTEGER,
    total_improvement REAL,

    -- Success
    success BOOLEAN NOT NULL,
    failure_reason TEXT,

    -- Detailed iterations
    iterations JSON,              -- List of IterationResult

    -- Metadata
    llm_model TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_module_id (module_id),
    INDEX idx_success (success),
    INDEX idx_created_at (created_at)
);
```

#### JSON Example

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "module_id": "image.download",
  "initial_score": 8.5,
  "final_score": 9.6,
  "total_iterations": 2,
  "strategy": "multi_round",
  "convergence_state": "success",
  "total_time_seconds": 23.7,
  "total_tokens": 5234,
  "total_improvement": 1.1,
  "success": true,
  "iterations": [
    {
      "iteration": 1,
      "score_before": 8.5,
      "score_after": 9.0,
      "improvement": 0.5,
      "issues_fixed": ["nested_function"],
      "time_seconds": 12.1,
      "tokens": 2847
    },
    {
      "iteration": 2,
      "score_before": 9.0,
      "score_after": 9.6,
      "improvement": 0.6,
      "issues_fixed": ["placeholder_docstring", "missing_self"],
      "time_seconds": 11.6,
      "tokens": 2387
    }
  ],
  "llm_model": "gpt-4o",
  "created_at": "2025-12-04T03:20:15Z"
}
```

---

### 3. E2E Task Execution Metrics

追蹤端到端任務的執行情況。

#### Schema

```sql
CREATE TABLE e2e_executions (
    id TEXT PRIMARY KEY,          -- UUID
    task_id TEXT NOT NULL,        -- "image_dog_to_svg"
    task_name TEXT,

    -- Execution
    status TEXT NOT NULL,         -- "success" | "failed" | "timeout"
    success BOOLEAN NOT NULL,

    -- Performance
    execution_time_seconds REAL,

    -- Validation
    checks_total INTEGER,
    checks_passed INTEGER,
    checks_failed INTEGER,
    failed_checks JSON,           -- List of failed check IDs

    -- Agent behavior
    modules_used JSON,            -- ["image.download", "image.svg_convert"]
    workflow_steps INTEGER,

    -- Errors
    error_message TEXT,
    error_traceback TEXT,

    -- Metadata
    agent_mode TEXT,              -- "autonomous" | "guided"
    llm_model TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_task_id (task_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

#### JSON Example

```json
{
  "id": "660f9511-f3ac-52e5-b827-557766551111",
  "task_id": "image_dog_to_svg",
  "task_name": "Download dog image and convert to SVG",
  "status": "success",
  "success": true,
  "execution_time_seconds": 27.3,
  "checks_total": 5,
  "checks_passed": 5,
  "checks_failed": 0,
  "failed_checks": [],
  "modules_used": [
    "web.search",
    "image.download",
    "image.svg_convert",
    "file.save"
  ],
  "workflow_steps": 6,
  "agent_mode": "autonomous",
  "llm_model": "gpt-4o",
  "created_at": "2025-12-04T03:25:42Z"
}
```

---

### 4. Model Comparison Metrics

比較不同 LLM 的表現。

#### Schema

```sql
CREATE TABLE model_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,     -- "gpt-4o" | "claude-3.7" | ...

    -- Task counts
    total_tasks INTEGER DEFAULT 0,
    successful_tasks INTEGER DEFAULT 0,
    failed_tasks INTEGER DEFAULT 0,

    -- Quality metrics
    avg_score REAL,
    avg_refine_iterations REAL,

    -- Performance
    avg_time_seconds REAL,
    total_tokens INTEGER DEFAULT 0,

    -- Time range
    period_start TIMESTAMP,
    period_end TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_model_name (model_name),
    UNIQUE (model_name, period_start)
);
```

---

## API 設計

### REST API Endpoints

#### 1. Module Quality API

```
GET /api/metrics/modules
  Query params:
    - module_id (optional): Filter by module
    - min_score (optional): Filter by score
    - limit (default: 100)
    - offset (default: 0)

  Response:
    {
      "total": 235,
      "modules": [
        {
          "module_id": "image.download",
          "latest_score": 9.6,
          "passed": true,
          "last_updated": "2025-12-04T03:15:23Z",
          "trend": "improving"  // "improving" | "stable" | "degrading"
        },
        ...
      ]
    }

GET /api/metrics/modules/{module_id}/history
  Query params:
    - days (default: 30): Look back N days
    - limit (default: 100)

  Response:
    {
      "module_id": "image.download",
      "history": [
        {
          "score": 9.6,
          "passed": true,
          "created_at": "2025-12-04T03:15:23Z"
        },
        {
          "score": 9.2,
          "passed": false,
          "created_at": "2025-12-03T14:22:11Z"
        },
        ...
      ]
    }

GET /api/metrics/modules/summary
  Response:
    {
      "total_modules": 47,
      "passing_modules": 42,
      "failing_modules": 5,
      "avg_score": 9.47,
      "score_distribution": {
        "10.0": 15,
        "9.5-9.9": 27,
        "9.0-9.4": 3,
        "< 9.0": 2
      }
    }
```

#### 2. Auto-Refine Performance API

```
GET /api/metrics/refine
  Query params:
    - success (optional): Filter by success status
    - days (default: 7)
    - limit (default: 50)

  Response:
    {
      "total": 128,
      "sessions": [
        {
          "id": "uuid",
          "module_id": "image.download",
          "initial_score": 8.5,
          "final_score": 9.6,
          "iterations": 2,
          "success": true,
          "time_seconds": 23.7,
          "created_at": "2025-12-04T03:20:15Z"
        },
        ...
      ]
    }

GET /api/metrics/refine/summary
  Query params:
    - days (default: 30)

  Response:
    {
      "total_sessions": 128,
      "success_rate": 0.87,
      "avg_iterations": 1.8,
      "avg_improvement": 1.2,
      "avg_time_seconds": 21.3,
      "total_tokens": 245678,

      "issue_fix_rates": {
        "nested_function": 0.95,
        "placeholder_docstring": 0.98,
        "missing_self": 0.92,
        "duplicate_imports": 1.0
      }
    }
```

#### 3. E2E Tasks API

```
GET /api/metrics/e2e
  Query params:
    - task_id (optional)
    - days (default: 7)
    - limit (default: 50)

  Response:
    {
      "total": 87,
      "executions": [
        {
          "id": "uuid",
          "task_id": "image_dog_to_svg",
          "success": true,
          "execution_time": 27.3,
          "checks_passed": 5,
          "checks_total": 5,
          "created_at": "2025-12-04T03:25:42Z"
        },
        ...
      ]
    }

GET /api/metrics/e2e/summary
  Response:
    {
      "total_executions": 87,
      "success_rate": 0.92,
      "avg_execution_time": 31.2,

      "by_task": {
        "image_dog_to_svg": {
          "success_rate": 1.0,
          "avg_time": 27.3,
          "total_runs": 15
        },
        "scrape_and_analyze": {
          "success_rate": 0.70,
          "avg_time": 39.6,
          "total_runs": 10
        }
      }
    }
```

#### 4. Model Comparison API

```
GET /api/metrics/models
  Response:
    {
      "models": [
        {
          "name": "gpt-4o",
          "success_rate": 0.97,
          "avg_score": 9.72,
          "avg_refine_iterations": 1.6,
          "total_tasks": 245
        },
        {
          "name": "claude-3.7",
          "success_rate": 0.90,
          "avg_score": 9.58,
          "avg_refine_iterations": 2.1,
          "total_tasks": 87
        }
      ]
    }
```

---

## 數據收集點 (Data Collectors)

### 1. ModuleQualityCollector

在 `QualityCheckerV2` 中埋點：

```python
class QualityCheckerV2:
    def review_module(self, module_path: str) -> Dict[str, Any]:
        # ... 現有邏輯 ...

        result = {
            "score": final_score,
            "passed": final_score >= 9.8,
            "issues": issues,
            # ...
        }

        # 📊 收集指標
        MetricsCollector.record_module_quality(
            module_id=self._extract_module_id(module_path),
            score=final_score,
            passed=result["passed"],
            issues=issues,
            score_breakdown=breakdown
        )

        return result
```

### 2. RefinePerformanceCollector

在 `AutoRefineEngine` 中埋點：

```python
class AutoRefineEngine:
    def refine_module(self, ...) -> RefineResult:
        session_id = str(uuid.uuid4())
        start_time = time.time()

        # ... 執行修復 ...

        result = RefineResult(...)

        # 📊 收集指標
        MetricsCollector.record_refine_session(
            session_id=session_id,
            module_id=module_path,
            initial_score=initial_report.score,
            final_score=result.final_score,
            iterations=len(result.iterations),
            success=result.success,
            time_seconds=time.time() - start_time,
            # ...
        )

        return result
```

### 3. E2EExecutionCollector

在 `e2e_runner.py` 中埋點：

```python
def run_e2e_task(task_spec: dict) -> ExecutionResult:
    execution_id = str(uuid.uuid4())
    start_time = time.time()

    # ... 執行任務 ...

    result = ExecutionResult(...)

    # 📊 收集指標
    MetricsCollector.record_e2e_execution(
        execution_id=execution_id,
        task_id=task_spec["id"],
        success=result.success,
        execution_time=time.time() - start_time,
        checks_passed=len([c for c in result.checks if c.passed]),
        checks_total=len(result.checks),
        # ...
    )

    return result
```

---

## MetricsCollector 實作

```python
# src/core/metrics/collector.py

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class MetricsCollector:
    """統一的指標收集器"""

    DB_PATH = Path("data/metrics/metrics.db")

    @classmethod
    def init_database(cls):
        """初始化數據庫"""
        cls.DB_PATH.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(cls.DB_PATH)
        cursor = conn.cursor()

        # 創建所有表
        cursor.executescript("""
            -- Module Quality Table
            CREATE TABLE IF NOT EXISTS module_quality (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id TEXT NOT NULL,
                module_name TEXT NOT NULL,
                score REAL NOT NULL,
                passed BOOLEAN NOT NULL,
                score_breakdown JSON,
                issues JSON,
                issues_count INTEGER DEFAULT 0,
                generated_by TEXT,
                llm_model TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_module_id ON module_quality(module_id);
            CREATE INDEX IF NOT EXISTS idx_created_at ON module_quality(created_at);

            -- Refine Sessions Table
            CREATE TABLE IF NOT EXISTS refine_sessions (
                id TEXT PRIMARY KEY,
                module_id TEXT NOT NULL,
                initial_score REAL NOT NULL,
                final_score REAL NOT NULL,
                total_iterations INTEGER NOT NULL,
                strategy TEXT,
                convergence_state TEXT,
                total_time_seconds REAL,
                total_tokens INTEGER,
                total_improvement REAL,
                success BOOLEAN NOT NULL,
                failure_reason TEXT,
                iterations JSON,
                llm_model TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_refine_module ON refine_sessions(module_id);
            CREATE INDEX IF NOT EXISTS idx_refine_created ON refine_sessions(created_at);

            -- E2E Executions Table
            CREATE TABLE IF NOT EXISTS e2e_executions (
                id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                task_name TEXT,
                status TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                execution_time_seconds REAL,
                checks_total INTEGER,
                checks_passed INTEGER,
                checks_failed INTEGER,
                failed_checks JSON,
                modules_used JSON,
                workflow_steps INTEGER,
                error_message TEXT,
                agent_mode TEXT,
                llm_model TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_e2e_task ON e2e_executions(task_id);
            CREATE INDEX IF NOT EXISTS idx_e2e_created ON e2e_executions(created_at);
        """)

        conn.commit()
        conn.close()

    @classmethod
    def record_module_quality(
        cls,
        module_id: str,
        module_name: str,
        score: float,
        passed: bool,
        issues: List[Dict],
        score_breakdown: Dict[str, float],
        generated_by: str = "unknown",
        llm_model: str = "unknown"
    ):
        """記錄模組品質"""
        conn = sqlite3.connect(cls.DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO module_quality (
                module_id, module_name, score, passed,
                score_breakdown, issues, issues_count,
                generated_by, llm_model
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            module_id,
            module_name,
            score,
            passed,
            json.dumps(score_breakdown),
            json.dumps(issues),
            len(issues),
            generated_by,
            llm_model
        ))

        conn.commit()
        conn.close()

    @classmethod
    def record_refine_session(
        cls,
        session_id: str,
        module_id: str,
        initial_score: float,
        final_score: float,
        total_iterations: int,
        strategy: str,
        convergence_state: str,
        success: bool,
        total_time_seconds: float = None,
        total_tokens: int = None,
        iterations: List[Dict] = None,
        failure_reason: str = None,
        llm_model: str = "unknown"
    ):
        """記錄修復會話"""
        conn = sqlite3.connect(cls.DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO refine_sessions (
                id, module_id, initial_score, final_score,
                total_iterations, strategy, convergence_state,
                total_time_seconds, total_tokens, total_improvement,
                success, failure_reason, iterations, llm_model
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            module_id,
            initial_score,
            final_score,
            total_iterations,
            strategy,
            convergence_state,
            total_time_seconds,
            total_tokens,
            final_score - initial_score,
            success,
            failure_reason,
            json.dumps(iterations) if iterations else None,
            llm_model
        ))

        conn.commit()
        conn.close()

    @classmethod
    def record_e2e_execution(
        cls,
        execution_id: str,
        task_id: str,
        task_name: str,
        success: bool,
        status: str,
        execution_time: float,
        checks_total: int,
        checks_passed: int,
        failed_checks: List[str] = None,
        modules_used: List[str] = None,
        workflow_steps: int = None,
        error_message: str = None,
        agent_mode: str = "autonomous",
        llm_model: str = "unknown"
    ):
        """記錄 E2E 執行"""
        conn = sqlite3.connect(cls.DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO e2e_executions (
                id, task_id, task_name, status, success,
                execution_time_seconds, checks_total, checks_passed,
                checks_failed, failed_checks, modules_used,
                workflow_steps, error_message, agent_mode, llm_model
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            execution_id,
            task_id,
            task_name,
            status,
            success,
            execution_time,
            checks_total,
            checks_passed,
            checks_total - checks_passed,
            json.dumps(failed_checks) if failed_checks else None,
            json.dumps(modules_used) if modules_used else None,
            workflow_steps,
            error_message,
            agent_mode,
            llm_model
        ))

        conn.commit()
        conn.close()
```

---

## API Server 實作

```python
# src/api/metrics_api.py

from fastapi import FastAPI, Query
from typing import Optional, List
import sqlite3
import json
from datetime import datetime, timedelta

app = FastAPI(title="Flyto2 Metrics API")

DB_PATH = "data/metrics/metrics.db"

@app.get("/api/metrics/modules")
def get_modules(
    module_id: Optional[str] = None,
    min_score: Optional[float] = None,
    limit: int = 100,
    offset: int = 0
):
    """獲取模組品質列表"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
        SELECT
            module_id,
            module_name,
            score,
            passed,
            created_at,
            ROW_NUMBER() OVER (PARTITION BY module_id ORDER BY created_at DESC) as rn
        FROM module_quality
        WHERE 1=1
    """
    params = []

    if module_id:
        query += " AND module_id = ?"
        params.append(module_id)

    if min_score is not None:
        query += " AND score >= ?"
        params.append(min_score)

    query += """
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()

    modules = [dict(row) for row in rows]

    conn.close()

    return {
        "total": len(modules),
        "modules": modules
    }

@app.get("/api/metrics/modules/{module_id}/history")
def get_module_history(
    module_id: str,
    days: int = 30,
    limit: int = 100
):
    """獲取模組歷史"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    since = datetime.now() - timedelta(days=days)

    cursor.execute("""
        SELECT score, passed, created_at
        FROM module_quality
        WHERE module_id = ? AND created_at >= ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (module_id, since.isoformat(), limit))

    rows = cursor.fetchall()
    history = [dict(row) for row in rows]

    conn.close()

    return {
        "module_id": module_id,
        "history": history
    }

@app.get("/api/metrics/refine/summary")
def get_refine_summary(days: int = 30):
    """獲取 Auto-Refine 摘要"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    since = datetime.now() - timedelta(days=days)

    cursor.execute("""
        SELECT
            COUNT(*) as total_sessions,
            SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
            AVG(total_iterations) as avg_iterations,
            AVG(total_improvement) as avg_improvement,
            AVG(total_time_seconds) as avg_time,
            SUM(total_tokens) as total_tokens
        FROM refine_sessions
        WHERE created_at >= ?
    """, (since.isoformat(),))

    row = cursor.fetchone()

    conn.close()

    return {
        "total_sessions": row[0],
        "success_rate": row[1] / row[0] if row[0] > 0 else 0,
        "avg_iterations": row[2],
        "avg_improvement": row[3],
        "avg_time_seconds": row[4],
        "total_tokens": row[5]
    }

# ... 更多 endpoints ...
```

---

## Web UI 設計

### Dashboard Layout (Wireframe)

```
┌─────────────────────────────────────────────────────────────┐
│  Flyto2 Metrics Dashboard                    [Refresh] [⚙] │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  📊 Overview                                                 │
│  ┌──────────────┬──────────────┬──────────────┬───────────┐│
│  │  Modules     │ Auto-Refine  │  E2E Tasks   │  Models   ││
│  │              │              │              │           ││
│  │  Total: 47   │ Success: 87% │ Success: 92% │ GPT-4o   ││
│  │  Pass:  42   │ Avg Iter:1.8 │ Avg: 31.2s   │ Claude   ││
│  │  Fail:  5    │ Tokens: 245K │ Total: 87    │ Gemini   ││
│  └──────────────┴──────────────┴──────────────┴───────────┘│
│                                                               │
│  📈 Module Quality Trends (Last 30 Days)                    │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                                                          ││
│  │  10.0 ┤                                    ●──●──●      ││
│  │   9.5 ┤                          ●──●──●               ││
│  │   9.0 ┤            ●──●──●                             ││
│  │   8.5 ┤  ●──●──●                                       ││
│  │   8.0 ┤                                                 ││
│  │       └─────────────────────────────────────────────────││
│  │         Dec 1    Dec 8    Dec 15   Dec 22   Dec 29     ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  🔧 Auto-Refine Performance                                 │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Issue Type            Fix Rate    Avg Iterations       ││
│  │  ─────────────────────────────────────────────────────  ││
│  │  nested_function       95%         1.2                  ││
│  │  placeholder_doc       98%         1.1                  ││
│  │  missing_self          92%         1.5                  ││
│  │  duplicate_imports     100%        1.0                  ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  🎯 E2E Task Success Rates                                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Task                  Success    Avg Time    Runs      ││
│  │  ─────────────────────────────────────────────────────  ││
│  │  image_dog_to_svg      100%       27.3s       15        ││
│  │  scrape_and_analyze    70%        39.6s       10        ││
│  │  text_summarize        85%        15.2s       20        ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  🤖 Model Comparison                                        │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Model       Success   Avg Score   Avg Iter   Tasks    ││
│  │  ──────────────────────────────────────────────────────  ││
│  │  GPT-4o      97%       9.72        1.6         245      ││
│  │  Claude-3.7  90%       9.58        2.1         87       ││
│  │  Gemini      57%       8.20        2.8         34       ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### UI 技術棧

**Option 1: Vue 3 (與現有 UI 統一)**

```vue
<!-- src/ui/web/frontend/src/views/MetricsDashboard.vue -->
<template>
  <div class="metrics-dashboard">
    <div class="overview">
      <MetricCard
        title="Modules"
        :value="stats.total_modules"
        :subtext="`${stats.passing_modules} passing`"
      />
      <MetricCard
        title="Auto-Refine"
        :value="`${stats.refine_success_rate}%`"
        :subtext="`${stats.avg_iterations} avg iterations`"
      />
      <!-- ... -->
    </div>

    <div class="chart">
      <LineChart :data="qualityTrends" title="Module Quality Trends" />
    </div>

    <!-- ... -->
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMetricsSummary, getQualityTrends } from '@/api/metrics'

const stats = ref({})
const qualityTrends = ref([])

onMounted(async () => {
  stats.value = await getMetricsSummary()
  qualityTrends.value = await getQualityTrends()
})
</script>
```

**Option 2: Standalone Dashboard (React + Recharts)**

適合作為獨立的監控介面。

---

## 實作計劃

### Phase 1: 數據層 (2-3 天)
- [x] 設計並創建 PostgreSQL schema (已完成 - db_schema.sql)
- [x] 實作 DatabaseManager (已完成 - db_manager.py with cloud PostgreSQL support)
- [x] 實作 MetricsCollector (已完成 - collector.py with 16 tests passed)
- [ ] 在現有系統中埋點
  - QualityCheckerV2
  - AutoRefineEngine (待完成後)
  - E2E Runner (待完成後)

### Phase 2: API 層 (1-2 天)
- [x] 實作 FastAPI endpoints (已完成 - api.py with 19 tests passed)
- [x] 添加數據聚合查詢 (已完成 - get_summary_stats, get_model_comparison)
- [x] 添加過濾和分頁 (已完成 - limit, min_score, days parameters)
- [x] API 文檔 (Swagger) (已完成 - automatic via FastAPI)

### Phase 3: UI 層 (2-3 天)
- [ ] 設計 Dashboard layout
- [ ] 實作核心 widgets
  - Overview cards
  - Quality trend chart
  - Auto-refine performance table
  - E2E success rates
  - Model comparison
- [ ] 集成到現有 Vue app

### Phase 4: 優化 (1-2 天)
- [ ] 添加實時更新 (WebSocket)
- [ ] 性能優化（數據庫索引）
- [ ] 導出功能（CSV/PDF）
- [ ] Alert 系統（分數下降警告）

---

## 啟動與使用

### 初始化數據庫

```bash
python -m src.core.metrics.init_db
```

### 啟動 API Server

```bash
uvicorn src.api.metrics_api:app --reload --port 9002
```

### 訪問 Dashboard

```
http://localhost:5173/metrics
```

### 查看 API 文檔

```
http://localhost:9002/docs
```

---

## 監控指標說明

### 核心 KPIs

1. **Module Pass Rate**: 模組通過率（≥ 9.8 分）
   - 目標: > 90%

2. **Auto-Refine Success Rate**: 自動修復成功率
   - 目標: > 85%

3. **E2E Task Success Rate**: 端到端任務成功率
   - 目標: > 80%

4. **Average Quality Score**: 平均品質分數
   - 目標: > 9.5

5. **Auto-Refine Efficiency**: 平均修復迭代次數
   - 目標: < 2.0

### 警報閾值

```yaml
alerts:
  module_pass_rate_below: 0.85
  refine_success_rate_below: 0.80
  avg_score_below: 9.3
  e2e_success_rate_below: 0.75
  avg_refine_iterations_above: 2.5
```

---

## 未來擴展

1. **實時監控**
   - WebSocket 推送
   - 實時圖表更新

2. **預測分析**
   - 品質趨勢預測
   - 異常檢測

3. **A/B 測試**
   - 不同 prompt 策略比較
   - 不同 LLM 模型比較

4. **Cost Analysis**
   - Token 使用成本
   - 時間成本分析

5. **Integration**
   - Slack/Discord 通知
   - Grafana 集成
   - Prometheus metrics export

---

這樣 Flyto2 就有了完整的「自我監控」能力！
