# Self-Awareness System - 自举式架构知识库

## 📖 概述

Self-Awareness System 让 Flyto2 通过 RAG 理解自己的架构和实现指南。

**核心理念**:
- 实现指南文档自动摄取到 VectorDB
- AI agents 可以查询"我应该怎么实现X？"
- 系统启动时自动初始化架构知识

---

## 🚀 快速开始

### 1. 初始摄取实现指南

```bash
# 首次运行 - 将实现指南摄取到 VectorDB
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

### 2. 查询架构知识

```bash
# 查询如何实现某个组件
python scripts/ingest_implementation_guides.py --query "How should I implement the Evolution Planner?"

# 输出:
# 🤔 Question: How should I implement the Evolution Planner?
#
# 📖 Answer:
#
# **1. EvolutionPlanner 完整实现** (relevance: 92%)
#
# # EvolutionPlanner 完整实现
#
# **文件**: `src/core/evolution/planner.py`
#
# ```python
# class EvolutionPlanner:
#     async def analyze_and_plan(self, ticket) -> Dict[str, Any]:
#         # 1. Gather context (RAG + Module Catalog)
#         # 2. Build planning prompt
#         # 3. Execute LLM planning
#         # 4. Parse and validate
# ...
#
# 📚 Sources: EvolutionPlanner 完整实现, Planner/Designer/Implementation 三大AI Agent, Evolution Pipeline
```

### 3. 检查状态

```bash
python scripts/ingest_implementation_guides.py --status

# 输出:
# 📊 Implementation Guide Status
#
# Testing knowledge base with sample queries:
#
#   ✓ VectorDB Schema
#   ✓ Evolution Pipeline
#   ✓ RAG configuration
#
# ✅ Knowledge base is operational
```

---

## 🔧 使用方式

### 在代码中查询架构知识

```python
from src.core.knowledge.doc_ingestion import get_self_awareness

# 获取 self-awareness 系统
system = get_self_awareness()

# 查询实现指南
result = await system.ask_self("How do I create a new atomic module?")

if result["success"]:
    print(result["answer"])
    # 输出完整的实现指南片段
```

### AI Agents 自我参照

**场景**: EvolutionDesigner 在设计新模块时，查询标准模式

```python
# In EvolutionDesigner
async def create_solution_design(self, plan: Dict) -> Dict:
    # 查询标准模块模式
    pattern_guide = await self.self_awareness.ask_self(
        "What is the standard pattern for atomic modules?"
    )

    # 使用查询到的模式来生成设计
    design = self._apply_standard_pattern(pattern_guide)

    return design
```

**场景**: ImplementationAgent 生成代码时参考现有实现

```python
# In ImplementationAgent
async def generate_new_file(self, step: Dict) -> Dict:
    # 查询类似模块的实现示例
    examples = await self.self_awareness.ask_self(
        f"Show me example implementation of {step['module_type']} module"
    )

    # 基于示例生成代码
    code = self._generate_from_template(examples)

    return code
```

---

## 🔄 启动时自动初始化

在主程序启动时自动初始化：

```python
# In main.py or cli.py
from src.core.startup_hooks import run_all_startup_hooks

async def main():
    # 运行所有启动 hooks (包括 self-awareness)
    await run_all_startup_hooks()

    # 现在系统已经"知道"自己的架构
    # 可以开始正常运行
    await start_application()
```

启动输出:
```
🚀 Running startup hooks...
  ▸ Self-Awareness System...
🧠 Initializing Self-Awareness System...
✓ Found 243 architecture documents in knowledge base
✅ Self-Awareness System ready
  ✓ Self-Awareness System ready
  ▸ Module Catalog...
  ✓ Module Catalog ready
  ▸ System Health Check...
  ✓ System Health Check ready
✅ All startup hooks complete
```

---

## 📊 架构设计

### 文档摄取流程

```
IMPLEMENTATION_GUIDE_V4.md
    ↓
DocumentIngestionEngine
    ↓
1. Parse Markdown (split by ## headers)
    ↓
2. Classify chunks (type, category, importance)
    ↓
3. Create vectors
    ↓
4. Store in Qdrant with metadata:
   - type: architecture/module/practice
   - category: evolution/vector_db/ollama
   - importance: critical/high/medium
   - section_title, doc_source
    ↓
VectorDB (Qdrant)
```

### 查询流程

```
Question: "How to implement Planner?"
    ↓
SelfAwarenessSystem.ask_self()
    ↓
RAG Retriever (query VectorDB)
    ↓
Filter: source=documentation
    ↓
Top 3 most relevant sections
    ↓
Format answer with sources
    ↓
Return structured result
```

---

## 🎯 使用场景

### 1. AI Agents 自我参照

**Planner 查询标准计划格式**:
```python
format_guide = await self_awareness.ask_self(
    "What is the JSON schema for evolution plan?"
)
# 返回完整的 schema 定义
```

**Designer 查询文件路径规范**:
```python
path_rules = await self_awareness.ask_self(
    "Where should atomic modules be placed?"
)
# 返回: src/core/modules/atomic/{category}/{operation}.py
```

### 2. 开发者快速查询

**快速查找实现细节**:
```bash
# 如何配置 RAG？
python scripts/ingest_implementation_guides.py --query "RAG configuration"

# VectorDB schema 是什么？
python scripts/ingest_implementation_guides.py --query "VectorDB schema fields"

# 如何创建 PR？
python scripts/ingest_implementation_guides.py --query "PR Engine workflow"
```

### 3. 自动化工具

**代码生成工具查询模板**:
```python
# 新模块生成器查询标准模板
template = await self_awareness.ask_self(
    "Show me the BaseModule template"
)

# 使用模板生成新模块
new_module = generate_from_template(template)
```

---

## 🔄 增量更新机制

### 自动检测文档变更

```python
# DocumentIngestionEngine 自动检测文件变更
async def ingest_all_guides(self, force: bool = False):
    for doc_path in self.implementation_docs:
        # 计算文件 hash
        current_hash = self._compute_file_hash(doc_path)

        # 检查是否已摄取（hash 匹配）
        if not force and await self._is_already_ingested(doc_path):
            logger.info("✓ Already ingested (no changes)")
            continue

        # 有变更，重新摄取
        await self._ingest_document(doc_path)
        await self._store_file_hash(doc_path)
```

### 定期更新

**方式 1: Cron Job**
```bash
# 每天自动更新一次
0 0 * * * cd /path/to/flyto2 && python scripts/ingest_implementation_guides.py
```

**方式 2: Git Hook**
```bash
# .git/hooks/post-merge
#!/bin/bash
# 当 pull 后自动更新文档
python scripts/ingest_implementation_guides.py
```

**方式 3: 启动时检查**
```python
# 启动时自动检查更新
async def init_self_awareness():
    system = get_self_awareness()

    # 检查文档是否有更新
    ingestion = DocumentIngestionEngine()
    await ingestion.ingest_all_guides(force=False)  # 只更新变更的

    await system.initialize()
```

---

## 📈 优势

### 1. 一致性保证

AI agents 生成的代码自动遵循实现指南中的标准和模式。

### 2. 自我修正

当实现偏离标准时，AI 可以查询正确做法并自我纠正。

### 3. 知识传承

新加入的 AI agents 自动"学习"系统架构，无需重新训练。

### 4. 文档驱动开发

文档即代码，更新文档自动更新 AI 的行为。

---

## 🔍 监控和调试

### 查看摄取统计

```python
from src.core.knowledge.knowledge_store import KnowledgeStore

store = KnowledgeStore()

# 查询文档类型分布
architecture_count = await store.count(filters={"type": "architecture"})
module_count = await store.count(filters={"type": "module"})
practice_count = await store.count(filters={"type": "practice"})

print(f"Architecture: {architecture_count}")
print(f"Modules: {module_count}")
print(f"Practices: {practice_count}")
```

### 测试查询质量

```python
# 测试不同问题的检索质量
test_queries = [
    "How to implement Evolution Planner?",
    "VectorDB schema definition",
    "RAG pipeline configuration",
    "PR merge webhook flow"
]

for query in test_queries:
    result = await self_awareness.ask_self(query)
    score = result["results"][0]["score"] if result["success"] else 0
    print(f"{query}: {score:.0%}")
```

---

## 🎓 最佳实践

### 1. 文档结构化

在实现指南中使用清晰的结构：

```markdown
## Component Name

### Purpose
Clear description...

### Implementation
**File**: `src/core/path/to/file.py`

```python
# Complete implementation
```

### Usage
```python
# Example usage
```
```

### 2. 添加元数据标记

在重要部分添加标记帮助分类：

```markdown
## [CRITICAL] VectorDB Schema

This is a critical component...
```

### 3. 保持文档同步

**规则**: 代码变更时同步更新实现指南

```bash
# 更新代码
git commit -m "feat: Add new validator"

# 同步更新文档
vim IMPLEMENTATION_GUIDE_V4_CRITICAL_SUPPLEMENTS.md

# 重新摄取
python scripts/ingest_implementation_guides.py --force
```

---

## 🚀 未来扩展

### 1. 多语言支持

摄取其他语言的文档（中文、英文同时支持）

### 2. 代码示例索引

直接索引 `src/` 下的代码，提供"Show me actual implementation"查询

### 3. 版本控制

保留不同版本的实现指南，支持"Show me how it was implemented in V3"

### 4. 交互式更新

AI agents 执行任务后自动建议文档更新

---

## 📚 相关文件

- `src/core/knowledge/doc_ingestion.py` - 文档摄取引擎
- `src/core/knowledge/vector_schema.py` - VectorDB schema
- `scripts/ingest_implementation_guides.py` - CLI 工具
- `src/core/startup_hooks.py` - 启动 hooks
- `IMPLEMENTATION_GUIDE_V4.md` - V4 基础架构
- `IMPLEMENTATION_GUIDE_V4_CRITICAL_SUPPLEMENTS.md` - 关键补充

---

## ✅ 总结

Self-Awareness System 让 Flyto2 成为一个**自我意识的系统**：

- ✅ AI 可以查询自己的架构
- ✅ 自动遵循实现标准
- ✅ 文档驱动的一致性
- ✅ 启动时自动初始化
- ✅ 增量更新支持

**一句话**: 让 AI 通过 RAG 理解并遵循自己的设计蓝图。
