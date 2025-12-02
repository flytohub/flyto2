# Self-Awareness System - 完整集成指南

## 🎯 目标

将 `IMPLEMENTATION_GUIDE_V4.md` 和 `IMPLEMENTATION_GUIDE_V4_CRITICAL_SUPPLEMENTS.md` 转换为**可查询的向量数据库**，让系统启动时自动加载架构知识。

---

## 📦 新增文件

```
flyto2/
├── src/core/knowledge/
│   └── doc_ingestion.py              # 文档摄取引擎 + Self-Awareness 系统
├── src/core/
│   └── startup_hooks.py              # 启动 hooks (自动初始化)
├── scripts/
│   ├── ingest_implementation_guides.py   # CLI 工具
│   └── test_self_awareness.py            # 测试脚本
└── docs/
    └── SELF_AWARENESS_SYSTEM.md          # 完整文档
```

---

## 🚀 快速开始

### 步骤 1: 首次摄取实现指南

```bash
cd /Library/其他專案/tickets/flyto2

# 将实现指南摄取到 VectorDB
python scripts/ingest_implementation_guides.py

# 输出:
# 📚 Ingesting Implementation Guides into VectorDB
#
# Processing: IMPLEMENTATION_GUIDE_V4.md
#   Found 156 sections
# Processing: IMPLEMENTATION_GUIDE_V4_CRITICAL_SUPPLEMENTS.md
#   Found 87 sections
#
# ✅ Ingestion complete: 243 chunks added
```

### 步骤 2: 测试查询

```bash
# 查询如何实现 Planner
python scripts/ingest_implementation_guides.py --query "How to implement Evolution Planner?"

# 查询 VectorDB Schema
python scripts/ingest_implementation_guides.py --query "VectorDB schema definition"

# 查询 RAG 配置
python scripts/ingest_implementation_guides.py --query "RAG pipeline configuration"
```

### 步骤 3: 集成到启动流程

在主程序中添加启动 hook：

```python
# In main.py or cli.py
from src.core.startup_hooks import run_all_startup_hooks

async def main():
    # 启动时自动初始化 Self-Awareness
    await run_all_startup_hooks()

    # 系统现在已经"知道"自己的架构
    # 开始正常运行
    await start_application()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 💡 使用场景

### 场景 1: AI Agent 查询实现标准

**EvolutionPlanner 需要知道标准的 plan schema**:

```python
# In src/core/evolution/planner.py
from src.core.knowledge.doc_ingestion import get_self_awareness

class EvolutionPlanner:
    def __init__(self):
        self.self_awareness = get_self_awareness()

    async def analyze_and_plan(self, ticket):
        # 查询标准的 plan 格式
        schema_guide = await self.self_awareness.ask_self(
            "What is the JSON schema for evolution plan output?"
        )

        # 使用标准格式生成 plan
        plan = await self._generate_plan_following_schema(schema_guide)

        return plan
```

### 场景 2: ImplementationAgent 参考代码模板

**生成新模块时参考标准模板**:

```python
# In src/core/evolution/implementation.py
class ImplementationAgent:
    async def generate_new_file(self, step: Dict) -> Dict:
        # 查询 BaseModule 模板
        template = await self.self_awareness.ask_self(
            "Show me the BaseModule template structure"
        )

        # 基于模板生成代码
        code = self._generate_from_template(template, step)

        return {
            "file_path": step["file_path"],
            "new_content": code
        }
```

### 场景 3: PatchValidator 检查代码规范

**验证生成的代码是否符合项目标准**:

```python
# In src/core/evolution/patch_validator.py
class PatchValidator:
    async def validate_code_standards(self, code: str) -> bool:
        # 查询代码规范
        standards = await self.self_awareness.ask_self(
            "What are the coding standards for Flyto2?"
        )

        # 检查代码是否符合规范
        return self._check_compliance(code, standards)
```

### 场景 4: 开发者快速查询

**开发者想知道某个组件如何实现**:

```bash
# 快速查找 PR Engine 的实现
python scripts/ingest_implementation_guides.py --query "PR Engine workflow"

# 查找 Webhook 处理逻辑
python scripts/ingest_implementation_guides.py --query "PR Merge Webhook implementation"

# 查找测试模板
python scripts/ingest_implementation_guides.py --query "Module test template"
```

---

## 🔄 自动更新机制

### 方式 1: 启动时自动检查更新

```python
# src/core/startup_hooks.py 已实现
async def init_self_awareness():
    from src.core.knowledge.doc_ingestion import DocumentIngestionEngine

    # 自动检查文档是否有更新（基于 file hash）
    engine = DocumentIngestionEngine()
    await engine.ingest_all_guides(force=False)  # 只更新变更的文档

    # 初始化 Self-Awareness
    system = get_self_awareness()
    await system.initialize()
```

### 方式 2: Git Hook 自动更新

创建 `.git/hooks/post-merge`:

```bash
#!/bin/bash
# 当 git pull 后自动更新文档向量

echo "🔄 Updating implementation guides in VectorDB..."
python scripts/ingest_implementation_guides.py
```

```bash
chmod +x .git/hooks/post-merge
```

### 方式 3: Cron Job 定期更新

```bash
# 每天凌晨 2 点自动更新
0 2 * * * cd /Library/其他專案/tickets/flyto2 && python scripts/ingest_implementation_guides.py
```

---

## 🏗️ 架构设计

### 文档摄取流程

```
┌─────────────────────────────────────────┐
│  IMPLEMENTATION_GUIDE_V4.md             │
│  IMPLEMENTATION_GUIDE_V4_SUPPLEMENTS.md │
└──────────────┬──────────────────────────┘
               │
               ▼
    ┌──────────────────────┐
    │ DocumentIngestion    │
    │ Engine               │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │ 1. Parse Markdown    │
    │    (split by ##)     │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │ 2. Classify Chunks   │
    │    - type            │
    │    - category        │
    │    - importance      │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │ 3. Create Vectors    │
    │    with metadata     │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │ VectorDB (Qdrant)    │
    │                      │
    │ Collection:          │
    │ flyto2_knowledge     │
    └──────────────────────┘
```

### 查询流程

```
┌─────────────────────────────┐
│ AI Agent or Developer       │
│ asks: "How to implement X?" │
└──────────────┬──────────────┘
               │
               ▼
    ┌──────────────────────┐
    │ SelfAwareness        │
    │ System               │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │ RAG Retriever        │
    │                      │
    │ Query VectorDB with: │
    │ filter: source=docs  │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │ Top 3-5 Relevant     │
    │ Sections             │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │ Format Answer        │
    │ with Sources         │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │ Return to Agent      │
    └──────────────────────┘
```

---

## 📊 VectorDB Schema

每个文档 chunk 使用统一的 schema:

```python
{
    # Required fields
    "type": "architecture|module|practice|pain_point",
    "category": "evolution|vector_db|ollama|browser|general",
    "importance": "critical|high|medium|low",
    "status": "active",
    "source": "documentation",
    "timestamp": "2025-12-02T10:30:00",

    # Document-specific fields
    "doc_source": "IMPLEMENTATION_GUIDE_V4.md",
    "section_title": "Evolution Planner",
    "section_level": 2,  # ## = level 2

    # Content
    "content": "# Evolution Planner\n\nComplete implementation..."
}
```

---

## 🎯 核心优势

### 1. 自我一致性 (Self-Consistency)

AI agents 生成的代码**自动遵循**实现指南中的标准：

```
Before (无 Self-Awareness):
  EvolutionPlanner 生成的 plan 格式可能不一致
  ↓
After (有 Self-Awareness):
  Planner 查询标准格式 → 生成的 plan 自动符合 schema
```

### 2. 知识传承 (Knowledge Transfer)

新增的 AI agents **自动学习**系统架构：

```
传统方式:
  需要重新训练模型，或手动编写提示词

Self-Awareness:
  新 agent 启动 → 查询实现指南 → 立即知道如何工作
```

### 3. 文档驱动 (Documentation-Driven)

更新文档 = 更新 AI 行为：

```
1. 修改 IMPLEMENTATION_GUIDE_V4.md
   (例如：更新 VectorDB schema 增加新字段)
   ↓
2. 重新摄取: python scripts/ingest_implementation_guides.py
   ↓
3. AI agents 自动获取新 schema
   ↓
4. 生成的代码自动包含新字段
```

### 4. 快速查询 (Quick Reference)

开发者无需翻阅长文档：

```bash
# 传统方式: 打开 3000+ 行文档，搜索关键词
vim IMPLEMENTATION_GUIDE_V4.md
/VectorDB Schema

# Self-Awareness: 直接查询
python scripts/ingest_implementation_guides.py --query "VectorDB Schema"
# 立即得到相关章节
```

---

## 🧪 测试和验证

### 运行测试脚本

```bash
# 完整 demo (包含 4 个场景)
python scripts/test_self_awareness.py

# 输出:
# 🧠 Self-Awareness System Demo
#
# Demo 1: AI Agent Self-Reference
# Demo 2: Module Generation with Self-Awareness
# Demo 3: Consistency Check
# Demo 4: Incremental Update
```

### 验证摄取成功

```bash
# 检查状态
python scripts/ingest_implementation_guides.py --status

# 输出:
# 📊 Implementation Guide Status
#
# Testing knowledge base with sample queries:
#   ✓ VectorDB Schema
#   ✓ Evolution Pipeline
#   ✓ RAG configuration
#
# ✅ Knowledge base is operational
```

### 手动查询测试

```python
from src.core.knowledge.doc_ingestion import get_self_awareness

async def test():
    system = get_self_awareness()

    # 测试查询
    result = await system.ask_self("How does PR Engine work?")

    if result["success"]:
        print("✓ Query successful")
        print(f"Found {len(result['sources'])} sources")
    else:
        print("✗ Query failed")

import asyncio
asyncio.run(test())
```

---

## 📝 最佳实践

### 1. 文档结构化

在实现指南中使用**清晰的分节**:

```markdown
## Component Name

### Purpose
描述组件用途

### Implementation
**文件**: `src/core/path/to/file.py`

```python
# 完整代码实现
```

### Usage Example
```python
# 使用示例
```
```

这样每个 ## 会被解析为一个独立的 chunk，便于查询。

### 2. 使用标记标识重要性

```markdown
## [CRITICAL] VectorDB Schema Definition

## [HIGH] Evolution Pipeline Flow

## [MEDIUM] Helper Utilities
```

系统会自动识别 `[CRITICAL]` 等标记，设置正确的 importance。

### 3. 保持文档同步

**原则**: 代码变更 → 立即更新文档 → 重新摄取

```bash
# Workflow
1. git commit -m "feat: Add new validator"
2. vim IMPLEMENTATION_GUIDE_V4_CRITICAL_SUPPLEMENTS.md
   # 添加 validator 实现说明
3. python scripts/ingest_implementation_guides.py
   # 重新摄取
4. git commit -m "docs: Update implementation guide"
```

---

## 🔍 监控和调试

### 查看摄取统计

```python
from src.core.knowledge.knowledge_store import KnowledgeStore

store = KnowledgeStore()

# 统计各类型文档数量
stats = {
    "architecture": await store.count(filters={"type": "architecture"}),
    "module": await store.count(filters={"type": "module"}),
    "practice": await store.count(filters={"type": "practice"}),
}

print(stats)
# {'architecture': 120, 'module': 85, 'practice': 38}
```

### 查询质量分析

```python
test_queries = [
    "Evolution Planner implementation",
    "VectorDB schema fields",
    "RAG configuration options"
]

for query in test_queries:
    result = await system.ask_self(query)
    if result["success"]:
        top_score = result["results"][0]["score"]
        print(f"{query}: {top_score:.0%}")
```

---

## 🚀 总结

### 实现效果

```
启动 Flyto2
    ↓
run_all_startup_hooks()
    ↓
init_self_awareness()
    ↓
检查实现指南是否已摄取
    ├─ 已摄取 → 检查 hash 是否变更
    │             ├─ 未变更 → 跳过
    │             └─ 已变更 → 增量更新
    └─ 未摄取 → 完整摄取 (243 chunks)
    ↓
系统现在"知道"自己的架构
    ↓
AI agents 可以查询实现标准
    ↓
生成的代码自动符合规范
```

### 核心价值

1. **自我意识**: 系统通过 RAG 理解自己的设计
2. **一致性保证**: AI 自动遵循架构标准
3. **知识传承**: 新 agent 自动学习系统架构
4. **文档驱动**: 更新文档即更新 AI 行为
5. **快速查询**: 开发者快速获取实现细节

### 一句话总结

**让 Flyto2 成为第一个通过 RAG 理解并遵循自己架构蓝图的 AI Agent 框架**。

---

## 📚 相关文档

- [Self-Awareness System 详细文档](docs/SELF_AWARENESS_SYSTEM.md)
- [V4 基础架构](IMPLEMENTATION_GUIDE_V4.md)
- [V4 关键补充](IMPLEMENTATION_GUIDE_V4_CRITICAL_SUPPLEMENTS.md)
- [VectorDB Schema](src/core/knowledge/vector_schema.py)
- [RAG Retriever](src/core/utils/rag_retriever.py)
