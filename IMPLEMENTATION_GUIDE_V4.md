# Flyto2 V4 企业级自我进化架构 - 完整实施指南

**版本**: V4.0
**日期**: 2025-12-02
**状态**: Implementation Ready

---

## 📋 目录

1. [核心目标与理念](#1-核心目标与理念)
2. [整体架构](#2-整体架构)
3. [Phase 1: 核心基础设施](#3-phase-1-核心基础设施)
4. [Phase 2: 智能化增强](#4-phase-2-智能化增强)
5. [Phase 3: 自动化闭环](#5-phase-3-自动化闭环)
6. [Telegram Bot 集成](#6-telegram-bot-集成)
7. [测试策略](#7-测试策略)
8. [部署与运维](#8-部署与运维)

---

## 1. 核心目标与理念

### 1.1 用户期望的理想状态

**你只做一件事：审PR和Merge**

- Windows开机 → 跑 `start_bot_with_memory.bat`
- TG Bot 自动运行
- 系统自己：
  - 发现错误
  - 分析根因
  - 提出解法
  - 生成代码
  - 开PR
  - 等你审核
- 你在GitHub上点 `Approve & Merge`
- 系统自动更新VectorDB

### 1.2 解决的核心痛点

| 痛点 | V4 解决方案 |
|------|------------|
| **Ollama不知道有哪些模块** | Module Catalog + VectorDB双轨索引 |
| **爬虫卡住没自我修正** | ErrorCenter + DebugEngine + Evolution Pipeline |
| **VectorDB不知道塞什么** | 统一Schema + QualityFilter + 明确存储时机 |
| **不知道何时更新** | 明确触发点：Error/Practice/PR/Catalog更新 |

---

## 2. 整体架构

### 2.1 系统分层

```
┌─────────────────────────────────────────────────────┐
│           控制层 (Telegram Bot + CLI)                │
│  /start /test /practice /competition /evolve /debug │
└─────────────────────────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────┐
│                    进化层                            │
│  ErrorCenter → DebugEngine → EvolutionOrchestrator  │
│     ↓              ↓                  ↓              │
│  Planner → Designer → Implementation → Validator    │
└──────────────────────────┬──────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────┐
│                    AI 层                             │
│  LLMOrchestrator: Ollama → GPT → Claude            │
│  + RAG Retriever (Qdrant 659 points)               │
└──────────────────────────┬──────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────┐
│                  记忆层                              │
│  VectorDB (Qdrant) + Module Catalog + Metrics      │
└──────────────────────────┬──────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────┐
│                  执行层                              │
│  Workflow Engine + Atomic Modules (120+ modules)    │
└─────────────────────────────────────────────────────┘
```

### 2.2 核心数据流

```
[User Request]
    ↓
[Workflow Execution]
    ↓
[Error Occurs] → [ErrorCenter] → [error_events.jsonl + VectorDB]
    ↓
[DebugEngine Analysis] → [Priority Report]
    ↓
[Evolution Ticket Created]
    ↓
[Planner: RAG + Module Catalog]
    ↓
[Designer: JSON Plan]
    ↓
[LLMOrchestrator: Ollama→GPT→Claude]
    ↓
[Implementation: Generate Patch]
    ↓
[PatchValidator: Format + Static + Sandbox]
    ↓
[PR Engine: Create Branch + Open PR]
    ↓
[Human Review on GitHub]
    ↓
[Merge] → [Webhook] → [Update VectorDB + Catalog]
```

---

## 3. Phase 1: 核心基础设施

### 3.1 Module Catalog System

#### 3.1.1 目标

让AI能够：
1. 知道有哪些atomic modules可用
2. 了解每个module的输入输出
3. 看到使用示例和场景
4. 快速搜索相关模块

#### 3.1.2 文件结构

```
flyto2/
├── modules/
│   ├── catalog.json           # 主目录文件
│   └── catalog_schema.json    # Schema定义
├── scripts/
│   ├── update_module_catalog.py      # 更新catalog
│   ├── sync_catalog_to_vdb.py        # 同步到VectorDB
│   └── validate_catalog.py           # 验证catalog完整性
└── src/core/catalog/
    ├── __init__.py
    ├── catalog_manager.py     # Catalog管理器
    └── module_scanner.py      # 扫描modules目录
```

#### 3.1.3 Catalog Schema 定义

**文件**: `modules/catalog_schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["version", "updated_at", "modules"],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Catalog version (semantic versioning)"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time",
      "description": "Last update timestamp (ISO 8601)"
    },
    "modules": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/module"
      }
    }
  },
  "definitions": {
    "module": {
      "type": "object",
      "required": ["id", "layer", "category", "description", "inputs", "outputs"],
      "properties": {
        "id": {
          "type": "string",
          "pattern": "^[a-z_]+\\.[a-z_]+\\.[a-z_]+$",
          "description": "Module ID (e.g., browser.stealth.goto)"
        },
        "layer": {
          "type": "string",
          "enum": ["atomic", "composite", "utility"],
          "description": "Module layer classification"
        },
        "category": {
          "type": "string",
          "enum": [
            "browser", "element", "string", "array", "math",
            "object", "file", "datetime", "data", "api",
            "ai", "notification", "test", "meta", "training"
          ],
          "description": "Module category"
        },
        "description": {
          "type": "string",
          "minLength": 10,
          "maxLength": 200,
          "description": "Short English description (10-200 chars)"
        },
        "inputs": {
          "type": "object",
          "description": "Input parameters with types",
          "patternProperties": {
            "^[a-z_]+$": {
              "type": "string",
              "pattern": "^(string|int|float|bool|array|object)(\\?)?$"
            }
          }
        },
        "outputs": {
          "type": "object",
          "description": "Output fields with types",
          "patternProperties": {
            "^[a-z_]+$": {
              "type": "string"
            }
          }
        },
        "tags": {
          "type": "array",
          "items": {
            "type": "string",
            "pattern": "^[a-z_-]+$"
          },
          "uniqueItems": true,
          "description": "Searchable tags"
        },
        "examples": {
          "type": "array",
          "minItems": 1,
          "maxItems": 3,
          "items": {
            "type": "string",
            "minLength": 10
          },
          "description": "1-3 usage examples"
        },
        "file_path": {
          "type": "string",
          "description": "Relative path to module file"
        },
        "test_path": {
          "type": "string",
          "description": "Relative path to test file"
        },
        "version": {
          "type": "string",
          "pattern": "^\\d+\\.\\d+\\.\\d+$"
        },
        "status": {
          "type": "string",
          "enum": ["stable", "beta", "deprecated"],
          "default": "stable"
        },
        "last_updated": {
          "type": "string",
          "format": "date-time"
        }
      }
    }
  }
}
```

#### 3.1.4 Catalog 示例

**文件**: `modules/catalog.json`

```json
{
  "version": "1.0.0",
  "updated_at": "2025-12-02T20:00:00Z",
  "modules": [
    {
      "id": "browser.goto",
      "layer": "atomic",
      "category": "browser",
      "description": "Navigate to a URL in headless browser with configurable timeout",
      "inputs": {
        "url": "string",
        "timeout_ms": "int?",
        "wait_until": "string?"
      },
      "outputs": {
        "page_handle": "string",
        "final_url": "string",
        "status_code": "int"
      },
      "tags": ["navigation", "headless", "basic", "browser"],
      "examples": [
        "Open a product page: browser.goto(url='https://example.com/product/123')",
        "Navigate with timeout: browser.goto(url='...', timeout_ms=5000)",
        "Wait for network idle: browser.goto(url='...', wait_until='networkidle')"
      ],
      "file_path": "src/core/modules/atomic/browser/goto.py",
      "test_path": "tests/modules/test_browser_goto.py",
      "version": "1.2.0",
      "status": "stable",
      "last_updated": "2025-11-20T10:30:00Z"
    },
    {
      "id": "browser.stealth.goto",
      "layer": "atomic",
      "category": "browser",
      "description": "Navigate to URL with stealth mode to bypass anti-bot protection (Cloudflare, etc.)",
      "inputs": {
        "url": "string",
        "proxy": "string?",
        "user_agent": "string?",
        "timeout_ms": "int?"
      },
      "outputs": {
        "page_handle": "string",
        "anti_bot_detected": "bool",
        "bypassed": "bool"
      },
      "tags": ["navigation", "anti-bot", "stealth", "proxy", "cloudflare"],
      "examples": [
        "Bypass Cloudflare on Amazon: browser.stealth.goto(url='https://amazon.com/dp/...')",
        "Use proxy for stealth: browser.stealth.goto(url='...', proxy='http://proxy:8080')",
        "Custom user agent: browser.stealth.goto(url='...', user_agent='Mozilla/5.0...')"
      ],
      "file_path": "src/core/modules/atomic/browser/stealth_goto.py",
      "test_path": "tests/modules/test_browser_stealth_goto.py",
      "version": "1.0.0",
      "status": "beta",
      "last_updated": "2025-12-01T15:00:00Z"
    },
    {
      "id": "string.split",
      "layer": "atomic",
      "category": "string",
      "description": "Split a string by delimiter into an array",
      "inputs": {
        "text": "string",
        "delimiter": "string",
        "max_splits": "int?"
      },
      "outputs": {
        "result": "array"
      },
      "tags": ["text", "parsing", "array"],
      "examples": [
        "Split CSV line: string.split(text='a,b,c', delimiter=',')",
        "Split by space: string.split(text='hello world', delimiter=' ')",
        "Limit splits: string.split(text='a,b,c,d', delimiter=',', max_splits=2)"
      ],
      "file_path": "src/core/modules/atomic/string/split.py",
      "test_path": "tests/modules/test_string_split.py",
      "version": "1.0.0",
      "status": "stable",
      "last_updated": "2025-10-15T09:00:00Z"
    }
  ]
}
```

#### 3.1.5 CatalogManager 实现

**文件**: `src/core/catalog/catalog_manager.py`

```python
"""
Module Catalog Manager

Responsibilities:
- Load and validate catalog.json
- Query modules by ID, category, tags
- Update catalog when modules change
- Sync catalog to VectorDB
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class CatalogManager:
    """Manage module catalog with validation and search capabilities"""

    def __init__(self, catalog_path: str = "modules/catalog.json"):
        self.catalog_path = Path(catalog_path)
        self.catalog: Dict[str, Any] = {}
        self.modules: List[Dict[str, Any]] = []
        self.module_index: Dict[str, Dict[str, Any]] = {}

    def load(self) -> bool:
        """
        Load catalog from JSON file

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.catalog_path.exists():
                logger.warning(f"Catalog not found: {self.catalog_path}")
                self._create_empty_catalog()
                return False

            with open(self.catalog_path, 'r', encoding='utf-8') as f:
                self.catalog = json.load(f)

            self.modules = self.catalog.get('modules', [])
            self._build_index()

            logger.info(f"Loaded {len(self.modules)} modules from catalog")
            return True

        except Exception as e:
            logger.error(f"Failed to load catalog: {e}")
            return False

    def save(self) -> bool:
        """Save catalog to JSON file"""
        try:
            self.catalog['updated_at'] = datetime.utcnow().isoformat() + 'Z'
            self.catalog['modules'] = self.modules

            # Create directory if not exists
            self.catalog_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.catalog_path, 'w', encoding='utf-8') as f:
                json.dump(self.catalog, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved catalog with {len(self.modules)} modules")
            return True

        except Exception as e:
            logger.error(f"Failed to save catalog: {e}")
            return False

    def _build_index(self):
        """Build internal index for fast lookup"""
        self.module_index = {
            module['id']: module
            for module in self.modules
        }

    def _create_empty_catalog(self):
        """Create empty catalog structure"""
        self.catalog = {
            "version": "1.0.0",
            "updated_at": datetime.utcnow().isoformat() + 'Z',
            "modules": []
        }
        self.modules = []
        self.save()

    def get_module(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Get module by ID"""
        return self.module_index.get(module_id)

    def search_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all modules in a category"""
        return [
            module for module in self.modules
            if module.get('category') == category
        ]

    def search_by_tags(self, tags: List[str], match_all: bool = False) -> List[Dict[str, Any]]:
        """
        Search modules by tags

        Args:
            tags: List of tags to search
            match_all: If True, module must have ALL tags; if False, ANY tag

        Returns:
            List of matching modules
        """
        results = []
        tags_set = set(tags)

        for module in self.modules:
            module_tags = set(module.get('tags', []))

            if match_all:
                if tags_set.issubset(module_tags):
                    results.append(module)
            else:
                if tags_set.intersection(module_tags):
                    results.append(module)

        return results

    def search_by_description(self, keyword: str) -> List[Dict[str, Any]]:
        """Search modules by keyword in description"""
        keyword_lower = keyword.lower()
        return [
            module for module in self.modules
            if keyword_lower in module.get('description', '').lower()
        ]

    def add_or_update_module(self, module_data: Dict[str, Any]) -> bool:
        """
        Add new module or update existing one

        Args:
            module_data: Module metadata dict

        Returns:
            True if successful
        """
        try:
            module_id = module_data.get('id')
            if not module_id:
                logger.error("Module ID is required")
                return False

            # Update timestamp
            module_data['last_updated'] = datetime.utcnow().isoformat() + 'Z'

            # Check if exists
            existing = self.get_module(module_id)

            if existing:
                # Update
                for i, module in enumerate(self.modules):
                    if module['id'] == module_id:
                        self.modules[i] = module_data
                        break
                logger.info(f"Updated module: {module_id}")
            else:
                # Add new
                self.modules.append(module_data)
                logger.info(f"Added module: {module_id}")

            self._build_index()
            return self.save()

        except Exception as e:
            logger.error(f"Failed to add/update module: {e}")
            return False

    def remove_module(self, module_id: str) -> bool:
        """Remove module from catalog"""
        try:
            original_count = len(self.modules)
            self.modules = [m for m in self.modules if m['id'] != module_id]

            if len(self.modules) < original_count:
                self._build_index()
                self.save()
                logger.info(f"Removed module: {module_id}")
                return True
            else:
                logger.warning(f"Module not found: {module_id}")
                return False

        except Exception as e:
            logger.error(f"Failed to remove module: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get catalog statistics"""
        categories = {}
        tags = {}
        layers = {}
        statuses = {}

        for module in self.modules:
            # Count by category
            category = module.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1

            # Count by tags
            for tag in module.get('tags', []):
                tags[tag] = tags.get(tag, 0) + 1

            # Count by layer
            layer = module.get('layer', 'unknown')
            layers[layer] = layers.get(layer, 0) + 1

            # Count by status
            status = module.get('status', 'unknown')
            statuses[status] = statuses.get(status, 0) + 1

        return {
            "total_modules": len(self.modules),
            "by_category": categories,
            "by_layer": layers,
            "by_status": statuses,
            "top_tags": dict(sorted(tags.items(), key=lambda x: x[1], reverse=True)[:10]),
            "version": self.catalog.get('version'),
            "last_updated": self.catalog.get('updated_at')
        }

    def to_llm_context(self, module_ids: List[str] = None,
                      category: str = None,
                      tags: List[str] = None) -> str:
        """
        Generate LLM-friendly context string for available modules

        Args:
            module_ids: Specific module IDs to include (None = all)
            category: Filter by category
            tags: Filter by tags

        Returns:
            Formatted string for LLM prompt
        """
        # Filter modules
        if module_ids:
            filtered = [self.get_module(mid) for mid in module_ids if self.get_module(mid)]
        elif category:
            filtered = self.search_by_category(category)
        elif tags:
            filtered = self.search_by_tags(tags, match_all=False)
        else:
            filtered = self.modules

        if not filtered:
            return "No modules available."

        lines = ["Available Modules:\n"]

        for module in filtered:
            lines.append(f"- {module['id']} ({module['category']})")
            lines.append(f"  Description: {module['description']}")
            lines.append(f"  Inputs: {', '.join([f'{k}={v}' for k,v in module.get('inputs', {}).items()])}")
            lines.append(f"  Outputs: {', '.join(module.get('outputs', {}).keys())}")
            lines.append(f"  Tags: {', '.join(module.get('tags', []))}")

            examples = module.get('examples', [])
            if examples:
                lines.append(f"  Example: {examples[0]}")
            lines.append("")

        return "\n".join(lines)


# Singleton instance
_catalog_manager = None

def get_catalog_manager() -> CatalogManager:
    """Get singleton catalog manager"""
    global _catalog_manager
    if _catalog_manager is None:
        _catalog_manager = CatalogManager()
        _catalog_manager.load()
    return _catalog_manager
```

#### 3.1.6 ModuleScanner 实现

**文件**: `src/core/catalog/module_scanner.py`

```python
"""
Module Scanner

Automatically scan atomic modules and extract metadata
"""

import ast
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ModuleScanner:
    """Scan Python module files and extract metadata"""

    def __init__(self, modules_root: str = "src/core/modules/atomic"):
        self.modules_root = Path(modules_root)

    def scan_all(self) -> List[Dict[str, Any]]:
        """
        Scan all modules in atomic directory

        Returns:
            List of module metadata dicts
        """
        modules = []

        if not self.modules_root.exists():
            logger.error(f"Modules root not found: {self.modules_root}")
            return modules

        # Scan all Python files
        for py_file in self.modules_root.rglob("*.py"):
            if py_file.name.startswith("_"):
                continue

            try:
                metadata = self.scan_file(py_file)
                if metadata:
                    modules.append(metadata)
            except Exception as e:
                logger.warning(f"Failed to scan {py_file}: {e}")

        logger.info(f"Scanned {len(modules)} modules")
        return modules

    def scan_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from a single module file

        Args:
            file_path: Path to module Python file

        Returns:
            Module metadata dict or None if not a valid module
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()

            tree = ast.parse(source)

            # Find class definition
            class_def = None
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Look for BaseModule subclass
                    for base in node.bases:
                        if isinstance(base, ast.Name) and 'Module' in base.id:
                            class_def = node
                            break
                    if class_def:
                        break

            if not class_def:
                return None

            # Extract module metadata
            module_id = self._extract_module_id(file_path)
            description = self._extract_docstring(class_def)

            # Try to extract from class attributes
            inputs = {}
            outputs = {}

            for node in class_def.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            if target.id == 'required_params':
                                inputs = self._extract_params(node.value)

            metadata = {
                "id": module_id,
                "layer": "atomic",
                "category": self._infer_category(file_path),
                "description": description or f"Module: {module_id}",
                "inputs": inputs or {"value": "string"},  # Default
                "outputs": {"result": "any"},  # Default
                "tags": self._infer_tags(module_id, description),
                "examples": [],  # To be filled manually
                "file_path": str(file_path.relative_to(Path.cwd())),
                "test_path": self._infer_test_path(file_path),
                "version": "1.0.0",
                "status": "stable"
            }

            return metadata

        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")
            return None

    def _extract_module_id(self, file_path: Path) -> str:
        """Infer module ID from file path"""
        # Example: src/core/modules/atomic/browser/goto.py → browser.goto
        parts = file_path.relative_to(self.modules_root).parts

        if len(parts) >= 2:
            category = parts[0]  # browser
            name = parts[-1].replace('.py', '')  # goto
            return f"{category}.{name}"
        else:
            return file_path.stem

    def _infer_category(self, file_path: Path) -> str:
        """Infer category from file path"""
        parts = file_path.relative_to(self.modules_root).parts
        return parts[0] if parts else "unknown"

    def _extract_docstring(self, node: ast.ClassDef) -> Optional[str]:
        """Extract docstring from class"""
        if node.body and isinstance(node.body[0], ast.Expr):
            if isinstance(node.body[0].value, ast.Constant):
                docstring = node.body[0].value.value
                # Get first line only
                if docstring:
                    return docstring.split('\n')[0].strip()
        return None

    def _extract_params(self, node) -> Dict[str, str]:
        """Extract parameters from AST node"""
        # This is simplified - real implementation would parse Dict/List structures
        return {}

    def _infer_tags(self, module_id: str, description: str) -> List[str]:
        """Infer tags from module ID and description"""
        tags = []

        # Add category as tag
        if '.' in module_id:
            tags.append(module_id.split('.')[0])

        # Extract keywords from description
        if description:
            keywords = ['browser', 'string', 'array', 'data', 'file',
                       'api', 'async', 'json', 'html', 'http']
            desc_lower = description.lower()
            for kw in keywords:
                if kw in desc_lower:
                    tags.append(kw)

        return list(set(tags))

    def _infer_test_path(self, file_path: Path) -> str:
        """Infer test file path from module file path"""
        rel_path = file_path.relative_to(self.modules_root)
        test_path = Path("tests/modules") / f"test_{rel_path}"
        return str(test_path)
```

#### 3.1.7 更新脚本实现

**文件**: `scripts/update_module_catalog.py`

```python
#!/usr/bin/env python3
"""
Update Module Catalog

Scan all atomic modules and update catalog.json
Also sync new/updated modules to VectorDB
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.catalog.catalog_manager import get_catalog_manager
from src.core.catalog.module_scanner import ModuleScanner
from src.core.utils.vector_db_manager import vector_store


async def sync_module_to_vdb(module: dict) -> bool:
    """
    Sync a module to VectorDB

    Creates a knowledge entry that AI can search for when planning solutions
    """
    try:
        # Build searchable content
        content = f"""Module: {module['id']}

Description: {module['description']}

Category: {module['category']}
Layer: {module['layer']}

Inputs: {', '.join([f"{k} ({v})" for k, v in module.get('inputs', {}).items()])}
Outputs: {', '.join([f"{k} ({v})" for k, v in module.get('outputs', {}).items()])}

Tags: {', '.join(module.get('tags', []))}

Usage Examples:
{chr(10).join(f"- {ex}" for ex in module.get('examples', []))}

Status: {module.get('status', 'stable')}
File: {module.get('file_path', 'unknown')}
"""

        metadata = {
            "type": "module",
            "module_id": module['id'],
            "category": module['category'],
            "layer": module['layer'],
            "tags": module.get('tags', []),
            "language": "en",
            "importance": 0.9,  # Modules are important reference
            "source": "module_catalog",
            "status": module.get('status', 'stable')
        }

        await vector_store(content=content, metadata=metadata)
        return True

    except Exception as e:
        print(f"   ❌ Failed to sync {module['id']} to VDB: {e}")
        return False


async def main():
    """Main update process"""
    print("\n🔄 Module Catalog Update")
    print("=" * 70)

    # Step 1: Scan modules
    print("\n1️⃣ Scanning atomic modules...")
    scanner = ModuleScanner()
    scanned_modules = scanner.scan_all()
    print(f"   ✅ Found {len(scanned_modules)} modules")

    # Step 2: Load existing catalog
    print("\n2️⃣ Loading existing catalog...")
    catalog = get_catalog_manager()
    existing_count = len(catalog.modules)
    print(f"   📚 Current catalog: {existing_count} modules")

    # Step 3: Update catalog
    print("\n3️⃣ Updating catalog...")
    added = 0
    updated = 0

    for module in scanned_modules:
        existing = catalog.get_module(module['id'])

        if existing:
            # Only update if structure changed
            if (existing.get('description') != module['description'] or
                existing.get('file_path') != module['file_path']):
                catalog.add_or_update_module(module)
                updated += 1
        else:
            catalog.add_or_update_module(module)
            added += 1

    print(f"   ✅ Added: {added}, Updated: {updated}")

    # Step 4: Sync to VectorDB
    print("\n4️⃣ Syncing to VectorDB...")
    synced = 0

    # Only sync new and updated modules
    modules_to_sync = scanned_modules if (added + updated) > 0 else []

    for module in modules_to_sync:
        if await sync_module_to_vdb(module):
            synced += 1

    print(f"   ✅ Synced {synced} modules to VectorDB")

    # Step 5: Show statistics
    print("\n5️⃣ Catalog Statistics:")
    stats = catalog.get_statistics()
    print(f"   Total Modules: {stats['total_modules']}")
    print(f"   By Category:")
    for cat, count in sorted(stats['by_category'].items()):
        print(f"      - {cat}: {count}")
    print(f"   By Status:")
    for status, count in stats['by_status'].items():
        print(f"      - {status}: {count}")

    print("\n" + "=" * 70)
    print("✅ Module Catalog Update Complete!")
    print("=" * 70)

    print("\n💡 Next Steps:")
    print("   1. Review catalog: cat modules/catalog.json | less")
    print("   2. Test search: python scripts/test_catalog_search.py")
    print("   3. Verify VDB: python scripts/check_qdrant_status.py")


if __name__ == "__main__":
    asyncio.run(main())
```

#### 3.1.8 使用示例

```bash
# 1. 初次建立catalog
python scripts/update_module_catalog.py

# 2. 新增module后更新
# 编辑 src/core/modules/atomic/browser/stealth_goto.py
python scripts/update_module_catalog.py

# 3. 查询catalog
python scripts/query_catalog.py --category browser --tags anti-bot

# 4. 验证catalog完整性
python scripts/validate_catalog.py
```

---

### 3.2 ErrorCenter - 统一错误管理

#### 3.2.1 目标

1. 所有错误统一收集到一个地方
2. 自动生成error_signature（用于去重和聚类）
3. 记录到 `metrics/error_events.jsonl`
4. 同步到VectorDB供RAG查询
5. 提供统计和分析接口

#### 3.2.2 文件结构

```
flyto2/
├── src/core/errors/
│   ├── __init__.py
│   ├── error_center.py         # 核心ErrorCenter类
│   ├── error_signature.py      # 生成signature
│   └── error_archiver.py       # 存档到VDB
└── metrics/
    └── error_events.jsonl      # 错误日志（每行一个JSON）
```

#### 3.2.3 ErrorCenter 实现

**文件**: `src/core/errors/error_center.py`

```python
"""
Error Center - Unified Error Management

All errors in the system flow through here:
1. Collect error with context
2. Generate error_signature for deduplication
3. Log to metrics/error_events.jsonl
4. Archive to VectorDB for RAG
5. Track statistics
"""

import json
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from collections import defaultdict

from .error_signature import generate_error_signature

logger = logging.getLogger(__name__)


class ErrorEvent:
    """Represents a single error event"""

    def __init__(
        self,
        error: Exception,
        context: Dict[str, Any],
        module_id: str = None,
        workflow: str = None,
        category: str = "unknown"
    ):
        self.event_id = self._generate_event_id()
        self.timestamp = datetime.utcnow().isoformat() + 'Z'
        self.error_type = type(error).__name__
        self.error_message = str(error)
        self.module_id = module_id
        self.workflow = workflow
        self.category = category
        self.context = context

        # Generate signature for deduplication
        self.signature = generate_error_signature(
            error_type=self.error_type,
            error_message=self.error_message,
            module_id=module_id
        )

    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        timestamp = datetime.utcnow().isoformat()
        hash_input = f"{timestamp}{id(self)}".encode()
        return hashlib.sha256(hash_input).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization"""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "error_signature": self.signature,
            "module_id": self.module_id,
            "workflow": self.workflow,
            "category": self.category,
            "context": self.context
        }

    def to_vdb_entry(self) -> Dict[str, Any]:
        """Convert to VectorDB entry format"""
        # Build Problem/Cause/Context/Fix card
        content = f"""[Problem]
{self.error_type}: {self.error_message}

[Cause]
Error occurred in module: {self.module_id or 'unknown'}
Workflow: {self.workflow or 'unknown'}

[Context]
Category: {self.category}
Timestamp: {self.timestamp}
Error Signature: {self.signature}
{self._format_context()}

[Suggested Fix]
To be determined. Check similar past errors.

[Status]
unresolved
"""

        metadata = {
            "type": "error",
            "error_signature": self.signature,
            "error_type": self.error_type,
            "module_id": self.module_id,
            "workflow": self.workflow,
            "category": self.category,
            "language": "en",
            "importance": 0.8,
            "source": "error_center",
            "event_id": self.event_id
        }

        return {"content": content, "metadata": metadata}

    def _format_context(self) -> str:
        """Format context for readable output"""
        if not self.context:
            return "No additional context"

        lines = []
        for key, value in self.context.items():
            if isinstance(value, (dict, list)):
                value = json.dumps(value, indent=2)
            lines.append(f"{key}: {value}")

        return "\n".join(lines)


class ErrorCenter:
    """Central error management system"""

    def __init__(self, log_file: str = "metrics/error_events.jsonl"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # In-memory statistics
        self.stats = {
            "total_errors": 0,
            "by_signature": defaultdict(int),
            "by_type": defaultdict(int),
            "by_module": defaultdict(int),
            "by_category": defaultdict(int)
        }

        # Load existing stats
        self._load_stats()

    def _load_stats(self):
        """Load stats from existing log file"""
        if not self.log_file.exists():
            return

        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        event = json.loads(line)
                        self._update_stats(event)
        except Exception as e:
            logger.warning(f"Failed to load error stats: {e}")

    def _update_stats(self, event: Dict[str, Any]):
        """Update statistics with new event"""
        self.stats["total_errors"] += 1
        self.stats["by_signature"][event.get("error_signature", "unknown")] += 1
        self.stats["by_type"][event.get("error_type", "unknown")] += 1

        module_id = event.get("module_id")
        if module_id:
            self.stats["by_module"][module_id] += 1

        category = event.get("category", "unknown")
        self.stats["by_category"][category] += 1

    async def log_error(
        self,
        error: Exception,
        context: Dict[str, Any],
        module_id: str = None,
        workflow: str = None,
        category: str = "unknown",
        archive_to_vdb: bool = True
    ) -> ErrorEvent:
        """
        Log an error event

        Args:
            error: The exception that occurred
            context: Additional context (params, state, etc.)
            module_id: Module where error occurred
            workflow: Workflow name
            category: Error category
            archive_to_vdb: Whether to archive to VectorDB

        Returns:
            ErrorEvent object
        """
        # Create event
        event = ErrorEvent(
            error=error,
            context=context,
            module_id=module_id,
            workflow=workflow,
            category=category
        )

        # Log to file
        self._write_to_log(event)

        # Update stats
        self._update_stats(event.to_dict())

        # Archive to VectorDB
        if archive_to_vdb:
            try:
                await self._archive_to_vdb(event)
            except Exception as e:
                logger.error(f"Failed to archive error to VDB: {e}")

        logger.info(f"Logged error: {event.signature}")
        return event

    def _write_to_log(self, event: ErrorEvent):
        """Write event to JSONL log file"""
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(event.to_dict(), ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Failed to write error log: {e}")

    async def _archive_to_vdb(self, event: ErrorEvent):
        """Archive error to VectorDB"""
        from src.core.utils.vector_db_manager import vector_store

        entry = event.to_vdb_entry()
        await vector_store(
            content=entry["content"],
            metadata=entry["metadata"]
        )

    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent N errors"""
        errors = []

        if not self.log_file.exists():
            return errors

        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
                for line in reversed(lines[-limit:]):
                    if line.strip():
                        errors.append(json.loads(line))
        except Exception as e:
            logger.error(f"Failed to read recent errors: {e}")

        return errors

    def get_errors_by_signature(self, signature: str) -> List[Dict[str, Any]]:
        """Get all errors with a specific signature"""
        errors = []

        if not self.log_file.exists():
            return errors

        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        event = json.loads(line)
                        if event.get("error_signature") == signature:
                            errors.append(event)
        except Exception as e:
            logger.error(f"Failed to read errors: {e}")

        return errors

    def get_top_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequent error signatures"""
        sorted_sigs = sorted(
            self.stats["by_signature"].items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {
                "signature": sig,
                "count": count,
                "examples": self.get_errors_by_signature(sig)[:3]
            }
            for sig, count in sorted_sigs[:limit]
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        return {
            "total_errors": self.stats["total_errors"],
            "unique_signatures": len(self.stats["by_signature"]),
            "by_type": dict(self.stats["by_type"]),
            "by_module": dict(self.stats["by_module"]),
            "by_category": dict(self.stats["by_category"]),
            "top_signatures": self.get_top_errors(5)
        }

    def should_trigger_evolution(self, signature: str, threshold: int = 3) -> bool:
        """
        Check if error signature should trigger evolution

        Args:
            signature: Error signature
            threshold: Minimum occurrences to trigger

        Returns:
            True if should trigger evolution
        """
        count = self.stats["by_signature"].get(signature, 0)
        return count >= threshold


# Singleton
_error_center = None

def get_error_center() -> ErrorCenter:
    """Get singleton error center"""
    global _error_center
    if _error_center is None:
        _error_center = ErrorCenter()
    return _error_center


# Convenience function
async def log_error(
    error: Exception,
    context: Dict[str, Any],
    module_id: str = None,
    workflow: str = None,
    category: str = "unknown"
) -> ErrorEvent:
    """Quick error logging"""
    center = get_error_center()
    return await center.log_error(
        error=error,
        context=context,
        module_id=module_id,
        workflow=workflow,
        category=category
    )
```

#### 3.2.4 ErrorSignature 生成

**文件**: `src/core/errors/error_signature.py`

```python
"""
Error Signature Generation

Generate stable, unique signatures for errors to enable:
- Deduplication
- Clustering similar errors
- Tracking error recurrence
"""

import hashlib
import re
from typing import Optional


def generate_error_signature(
    error_type: str,
    error_message: str,
    module_id: str = None
) -> str:
    """
    Generate stable error signature

    Strategy:
    1. Normalize error message (remove variables, paths, IDs)
    2. Combine error_type + normalized_message + module_id
    3. Hash to get short signature

    Args:
        error_type: Exception class name
        error_message: Error message string
        module_id: Module where error occurred

    Returns:
        Short error signature (e.g., "err_browser_timeout_a7f2")
    """
    # Normalize message
    normalized = _normalize_error_message(error_message)

    # Build signature components
    components = [error_type, normalized]
    if module_id:
        components.append(module_id)

    # Join and hash
    signature_input = "|".join(components).encode('utf-8')
    hash_digest = hashlib.sha256(signature_input).hexdigest()[:8]

    # Build human-readable signature
    category = _infer_category(error_type, normalized, module_id)
    return f"err_{category}_{hash_digest}"


def _normalize_error_message(message: str) -> str:
    """
    Normalize error message by removing dynamic parts

    Examples:
        "Timeout after 30000ms" → "Timeout after Xms"
        "File '/tmp/abc123.txt' not found" → "File 'X' not found"
        "Element #button-123 not found" → "Element X not found"
    """
    if not message:
        return "unknown"

    # Convert to lowercase
    normalized = message.lower()

    # Remove numbers
    normalized = re.sub(r'\d+', 'X', normalized)

    # Remove file paths
    normalized = re.sub(r'/[\w/.-]+', '/X', normalized)
    normalized = re.sub(r'[a-z]:\\[\w\\.-]+', 'X:\\X', normalized, flags=re.IGNORECASE)

    # Remove URLs
    normalized = re.sub(r'https?://[^\s]+', 'http://X', normalized)

    # Remove UUIDs and hashes
    normalized = re.sub(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', 'X', normalized)
    normalized = re.sub(r'[a-f0-9]{32,}', 'X', normalized)

    # Remove timestamps
    normalized = re.sub(r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}', 'X', normalized)

    # Trim whitespace
    normalized = ' '.join(normalized.split())

    return normalized[:200]  # Limit length


def _infer_category(error_type: str, message: str, module_id: str = None) -> str:
    """
    Infer error category for signature

    Returns short category name (e.g., "timeout", "notfound", "parse")
    """
    error_type_lower = error_type.lower()
    message_lower = message.lower()

    # Check error type
    if 'timeout' in error_type_lower:
        return 'timeout'
    elif 'notfound' in error_type_lower or 'not found' in message_lower:
        return 'notfound'
    elif 'permission' in error_type_lower or 'permission' in message_lower:
        return 'permission'
    elif 'connection' in error_type_lower or 'connection' in message_lower:
        return 'connection'
    elif 'parse' in error_type_lower or 'parse' in message_lower:
        return 'parse'
    elif 'validation' in error_type_lower or 'invalid' in message_lower:
        return 'validation'
    elif 'module' in message_lower and 'not found' in message_lower:
        return 'module'

    # Check module_id
    if module_id:
        if 'browser' in module_id:
            return 'browser'
        elif 'string' in module_id or 'array' in module_id or 'object' in module_id:
            return 'data'
        elif 'file' in module_id:
            return 'file'
        elif 'api' in module_id or 'http' in module_id:
            return 'api'

    return 'general'
```

#### 3.2.5 使用示例

```python
# 在workflow engine中使用
try:
    result = await module.execute()
except Exception as e:
    from src.core.errors import log_error

    await log_error(
        error=e,
        context={
            "module": module.module_id,
            "params": module.params,
            "step_id": step.get('id')
        },
        module_id=module.module_id,
        workflow=self.workflow_name,
        category="execution_error"
    )
    raise
```

---

### 3.3 DebugEngine - 系统健康分析

#### 3.3.1 目标

1. 每小时自动分析系统状态
2. 识别最频繁的错误
3. 识别成功率下降的workflow
4. 生成优先级报告
5. 提供TG Bot `/debug` 命令支持

#### 3.3.2 文件结构

```
flyto2/
├── src/core/debug/
│   ├── __init__.py
│   ├── debug_engine.py          # 核心分析引擎
│   └── report_generator.py      # 报告生成器
└── metrics/
    └── debug_reports/
        └── 2025-12-02_20-00.json  # 每小时报告
```

#### 3.3.3 DebugEngine 实现

**文件**: `src/core/debug/debug_engine.py`

```python
"""
Debug Engine - System Health Analyzer

Analyzes system health and generates actionable reports:
- Most frequent errors
- Workflows with declining success rates
- Modules that fail often
- Priority recommendations
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
from collections import defaultdict

from src.core.errors.error_center import get_error_center

logger = logging.getLogger(__name__)


class DebugEngine:
    """Analyze system health and generate reports"""

    def __init__(self, reports_dir: str = "metrics/debug_reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.error_center = get_error_center()

    def analyze(self, hours: int = 24) -> Dict[str, Any]:
        """
        Analyze recent system performance

        Args:
            hours: Look back N hours

        Returns:
            Analysis report dict
        """
        logger.info(f"Starting debug analysis (last {hours} hours)")

        # Get recent errors
        recent_errors = self._get_recent_errors(hours)

        # Analyze errors
        error_analysis = self._analyze_errors(recent_errors)

        # Analyze workflows (if metrics available)
        workflow_analysis = self._analyze_workflows(hours)

        # Analyze modules
        module_analysis = self._analyze_modules(recent_errors)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            error_analysis,
            workflow_analysis,
            module_analysis
        )

        report = {
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "period_hours": hours,
            "error_analysis": error_analysis,
            "workflow_analysis": workflow_analysis,
            "module_analysis": module_analysis,
            "recommendations": recommendations
        }

        # Save report
        self._save_report(report)

        return report

    def _get_recent_errors(self, hours: int) -> List[Dict[str, Any]]:
        """Get errors from last N hours"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        cutoff_str = cutoff.isoformat()

        errors = []
        log_file = Path("metrics/error_events.jsonl")

        if not log_file.exists():
            return errors

        try:
            with open(log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        event = json.loads(line)
                        if event.get('timestamp', '') >= cutoff_str:
                            errors.append(event)
        except Exception as e:
            logger.error(f"Failed to read error log: {e}")

        return errors

    def _analyze_errors(self, errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze error patterns"""
        if not errors:
            return {
                "total": 0,
                "unique_signatures": 0,
                "top_errors": []
            }

        # Count by signature
        by_signature = defaultdict(list)
        for error in errors:
            sig = error.get('error_signature', 'unknown')
            by_signature[sig].append(error)

        # Sort by frequency
        sorted_errors = sorted(
            by_signature.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )

        # Build top errors list
        top_errors = []
        for sig, instances in sorted_errors[:10]:
            first = instances[0]
            top_errors.append({
                "signature": sig,
                "count": len(instances),
                "error_type": first.get('error_type'),
                "module_id": first.get('module_id'),
                "category": first.get('category'),
                "first_seen": instances[-1].get('timestamp'),
                "last_seen": instances[0].get('timestamp'),
                "sample_message": first.get('error_message', '')[:100]
            })

        return {
            "total": len(errors),
            "unique_signatures": len(by_signature),
            "top_errors": top_errors
        }

    def _analyze_workflows(self, hours: int) -> Dict[str, Any]:
        """Analyze workflow performance"""
        # Try to load practice/competition metrics
        analysis = {
            "analyzed": False,
            "workflows": []
        }

        metrics_files = [
            "metrics/daily_practice.json",
            "metrics/speed_races.json"
        ]

        workflow_stats = defaultdict(lambda: {"success": 0, "failure": 0})

        for metrics_file in metrics_files:
            path = Path(metrics_file)
            if not path.exists():
                continue

            try:
                with open(path, 'r') as f:
                    data = json.load(f)

                # Parse based on file type
                if "practices" in data:
                    for practice in data.get("practices", []):
                        workflow = practice.get("workflow", "unknown")
                        status = practice.get("status", "unknown")
                        if status == "success":
                            workflow_stats[workflow]["success"] += 1
                        else:
                            workflow_stats[workflow]["failure"] += 1

                analysis["analyzed"] = True

            except Exception as e:
                logger.warning(f"Failed to analyze {metrics_file}: {e}")

        # Calculate success rates
        workflows = []
        for workflow, stats in workflow_stats.items():
            total = stats["success"] + stats["failure"]
            success_rate = stats["success"] / total if total > 0 else 0

            workflows.append({
                "workflow": workflow,
                "total_runs": total,
                "success": stats["success"],
                "failure": stats["failure"],
                "success_rate": success_rate
            })

        # Sort by failure count
        workflows.sort(key=lambda x: x["failure"], reverse=True)
        analysis["workflows"] = workflows[:10]

        return analysis

    def _analyze_modules(self, errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze module-level failures"""
        module_errors = defaultdict(int)

        for error in errors:
            module_id = error.get('module_id')
            if module_id:
                module_errors[module_id] += 1

        # Sort by error count
        sorted_modules = sorted(
            module_errors.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return {
            "total_modules_with_errors": len(module_errors),
            "top_failing_modules": [
                {"module_id": mod, "error_count": count}
                for mod, count in sorted_modules[:10]
            ]
        }

    def _generate_recommendations(
        self,
        error_analysis: Dict,
        workflow_analysis: Dict,
        module_analysis: Dict
    ) -> List[Dict[str, Any]]:
        """Generate prioritized recommendations"""
        recommendations = []

        # Check top errors
        top_errors = error_analysis.get("top_errors", [])
        if top_errors:
            for i, error in enumerate(top_errors[:3]):
                if error["count"] >= 3:
                    recommendations.append({
                        "priority": "P0" if i == 0 else "P1",
                        "type": "error_signature",
                        "signature": error["signature"],
                        "description": f"{error['error_type']} in {error['module_id'] or 'unknown module'}",
                        "occurrences": error["count"],
                        "action": f"Run /evolve on error signature: {error['signature']}",
                        "impact": "high" if error["count"] > 10 else "medium"
                    })

        # Check workflows with low success rates
        workflows = workflow_analysis.get("workflows", [])
        for workflow in workflows:
            if workflow["success_rate"] < 0.5 and workflow["total_runs"] >= 5:
                recommendations.append({
                    "priority": "P1",
                    "type": "workflow",
                    "workflow": workflow["workflow"],
                    "description": f"Workflow success rate dropped to {workflow['success_rate']:.0%}",
                    "action": f"Review workflow: {workflow['workflow']}",
                    "impact": "medium"
                })

        # Check modules
        failing_modules = module_analysis.get("top_failing_modules", [])
        if failing_modules:
            top_module = failing_modules[0]
            if top_module["error_count"] >= 5:
                recommendations.append({
                    "priority": "P1",
                    "type": "module",
                    "module_id": top_module["module_id"],
                    "description": f"Module has {top_module['error_count']} recent failures",
                    "action": f"Review module: {top_module['module_id']}",
                    "impact": "medium"
                })

        # Sort by priority
        priority_order = {"P0": 0, "P1": 1, "P2": 2}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 99))

        return recommendations

    def _save_report(self, report: Dict[str, Any]):
        """Save report to file"""
        try:
            timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M")
            report_file = self.reports_dir / f"{timestamp}.json"

            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved debug report: {report_file}")

        except Exception as e:
            logger.error(f"Failed to save report: {e}")

    def generate_text_report(self, report: Dict[str, Any]) -> str:
        """Generate human-readable text report"""
        lines = [
            f"Flyto2 Debug Report ({report['timestamp']})",
            "=" * 70,
            "",
            f"Period: Last {report['period_hours']} hours",
            ""
        ]

        # Error Analysis
        error_analysis = report["error_analysis"]
        lines.extend([
            "1️⃣ Error Analysis",
            f"   Total Errors: {error_analysis['total']}",
            f"   Unique Signatures: {error_analysis['unique_signatures']}",
            ""
        ])

        if error_analysis["top_errors"]:
            lines.append("   Top Errors:")
            for i, error in enumerate(error_analysis["top_errors"][:5], 1):
                lines.append(
                    f"   [{i}] {error['signature']} - {error['count']} occurrences"
                )
                lines.append(f"       Type: {error['error_type']}")
                lines.append(f"       Module: {error['module_id'] or 'unknown'}")
                lines.append("")

        # Workflow Analysis
        workflow_analysis = report["workflow_analysis"]
        if workflow_analysis["analyzed"]:
            lines.append("2️⃣ Workflow Analysis")
            for wf in workflow_analysis["workflows"][:5]:
                lines.append(
                    f"   {wf['workflow']}: {wf['success_rate']:.0%} success "
                    f"({wf['success']}/{wf['total_runs']} runs)"
                )
            lines.append("")

        # Module Analysis
        module_analysis = report["module_analysis"]
        if module_analysis["top_failing_modules"]:
            lines.append("3️⃣ Module Analysis")
            for mod in module_analysis["top_failing_modules"][:5]:
                lines.append(
                    f"   {mod['module_id']}: {mod['error_count']} errors"
                )
            lines.append("")

        # Recommendations
        recommendations = report["recommendations"]
        if recommendations:
            lines.extend([
                "4️⃣ Recommended Actions",
                ""
            ])
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"   [{rec['priority']}] {rec['description']}")
                lines.append(f"       Action: {rec['action']}")
                lines.append(f"       Impact: {rec['impact']}")
                lines.append("")

        lines.extend([
            "=" * 70,
            "✅ Debug Analysis Complete",
            ""
        ])

        return "\n".join(lines)


# Singleton
_debug_engine = None

def get_debug_engine() -> DebugEngine:
    """Get singleton debug engine"""
    global _debug_engine
    if _debug_engine is None:
        _debug_engine = DebugEngine()
    return _debug_engine
```

#### 3.3.4 定时任务脚本

**文件**: `scripts/run_debug_analysis.py`

```python
#!/usr/bin/env python3
"""
Run Debug Analysis

Can be called by cron or scheduler every hour
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.debug.debug_engine import get_debug_engine


async def main():
    """Run analysis and print report"""
    print("\n🔍 Running System Debug Analysis...")
    print("=" * 70)

    engine = get_debug_engine()
    report = engine.analyze(hours=24)

    # Generate text report
    text_report = engine.generate_text_report(report)
    print(text_report)

    # Check if critical issues
    recommendations = report.get("recommendations", [])
    p0_issues = [r for r in recommendations if r["priority"] == "P0"]

    if p0_issues:
        print("\n⚠️ CRITICAL ISSUES DETECTED!")
        print(f"   {len(p0_issues)} P0 issues require immediate attention")
        print("\n💡 Recommended: Run /evolve to address these issues")
        return 1
    else:
        print("\n✅ No critical issues detected")
        return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
```

#### 3.3.5 Cron 设置

```bash
# 每小时运行debug analysis
0 * * * * cd /path/to/flyto2 && python scripts/run_debug_analysis.py >> logs/debug_analysis.log 2>&1
```

---

## 4. Phase 2: 智能化增强

### 4.1 LLMOrchestrator - 多模型Pipeline

#### 4.1.1 目标

1. Ollama优先（便宜、快速）
2. 失败自动fallback到GPT-4
3. 再失败fallback到Claude
4. 每个结果都要过Validator
5. 全程可审计

#### 4.1.2 文件结构

```
flyto2/
└── src/core/ai/
    ├── __init__.py
    ├── llm_orchestrator.py      # 主orchestrator
    ├── validators.py             # Format/Static/Sandbox validators
    └── llm_task.py              # Task定义
```

#### 4.1.3 LLMOrchestrator 实现

**文件**: `src/core/ai/llm_orchestrator.py`

```python
"""
LLM Orchestrator - Multi-Model Pipeline

Tries models in order: Ollama → GPT → Claude
Each result must pass validators before being accepted
"""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum

from src.core.utils.http_client import HTTPClient
from .validators import FormatValidator, StaticValidator, SandboxValidator
from .llm_task import LLMTask, LLMResult

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Available LLM providers"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    CLAUDE = "claude"


class LLMOrchestrator:
    """
    Orchestrate LLM requests with automatic fallback

    Flow:
    1. Try Ollama (local, fast, cheap)
    2. If fails or invalid → Try GPT-4
    3. If fails or invalid → Try Claude
    4. If all fail → Raise error

    Each response validated by:
    - FormatValidator: JSON structure
    - StaticValidator: Code syntax
    - SandboxValidator: Safe execution
    """

    def __init__(self):
        self.http_client = HTTPClient()
        self.validators = [
            FormatValidator(),
            StaticValidator(),
            # SandboxValidator() can be expensive, use selectively
        ]

    async def solve(self, task: LLMTask) -> LLMResult:
        """
        Solve a task using multi-model pipeline

        Args:
            task: LLM task definition

        Returns:
            LLMResult with validated response

        Raises:
            UnresolvedTaskError: If all models fail
        """
        logger.info(f"Solving task: {task.task_id}")

        # Try each provider in order
        providers = [LLMProvider.OLLAMA, LLMProvider.OPENAI, LLMProvider.CLAUDE]

        for provider in providers:
            try:
                result = await self._try_provider(provider, task)

                # Validate result
                if self._validate_result(result, task):
                    logger.info(f"Task solved by {provider.value}")
                    return result
                else:
                    logger.warning(f"{provider.value} result failed validation")

            except Exception as e:
                logger.warning(f"{provider.value} failed: {e}")
                continue

        # All providers failed
        raise UnresolvedTaskError(
            f"All LLM providers failed for task: {task.task_id}"
        )

    async def _try_provider(
        self,
        provider: LLMProvider,
        task: LLMTask
    ) -> LLMResult:
        """Try a specific provider"""
        if provider == LLMProvider.OLLAMA:
            return await self._try_ollama(task)
        elif provider == LLMProvider.OPENAI:
            return await self._try_openai(task)
        elif provider == LLMProvider.CLAUDE:
            return await self._try_claude(task)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def _try_ollama(self, task: LLMTask) -> LLMResult:
        """Try Ollama"""
        response = await self.http_client.ask_ollama(
            prompt=task.prompt,
            system_prompt=task.system_prompt,
            model="llama3.2",
            timeout=120
        )

        if not response["success"]:
            raise Exception(response.get("error", "Ollama failed"))

        return LLMResult(
            task_id=task.task_id,
            provider=LLMProvider.OLLAMA.value,
            raw_response=response["content"],
            success=True
        )

    async def _try_openai(self, task: LLMTask) -> LLMResult:
        """Try OpenAI GPT-4"""
        response = await self.http_client.ask_openai(
            prompt=task.prompt,
            system_prompt=task.system_prompt,
            model="gpt-4o",
            timeout=60
        )

        if not response["success"]:
            raise Exception(response.get("error", "OpenAI failed"))

        return LLMResult(
            task_id=task.task_id,
            provider=LLMProvider.OPENAI.value,
            raw_response=response["content"],
            success=True
        )

    async def _try_claude(self, task: LLMTask) -> LLMResult:
        """Try Claude"""
        # Implement Claude API call (similar to OpenAI)
        # For now, placeholder
        raise NotImplementedError("Claude integration pending")

    def _validate_result(self, result: LLMResult, task: LLMTask) -> bool:
        """
        Validate result with all validators

        Returns:
            True if all validators pass
        """
        for validator in self.validators:
            try:
                if not validator.validate(result, task):
                    logger.warning(f"Validator {validator.__class__.__name__} failed")
                    return False
            except Exception as e:
                logger.error(f"Validator error: {e}")
                return False

        return True


class UnresolvedTaskError(Exception):
    """Raised when no LLM provider can solve the task"""
    pass


# Singleton
_orchestrator = None

def get_llm_orchestrator() -> LLMOrchestrator:
    """Get singleton orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = LLMOrchestrator()
    return _orchestrator
```

---


---

#### 4.1.4 Validators 实现

**文件**: `src/core/ai/validators.py`

```python
"""
LLM Result Validators

Three-layer validation:
1. FormatValidator: JSON structure
2. StaticValidator: Code syntax
3. SandboxValidator: Safe execution
"""

import ast
import json
import logging
from typing import Dict, Any
from .llm_task import LLMTask, LLMResult

logger = logging.getLogger(__name__)


class BaseValidator:
    """Base validator interface"""

    def validate(self, result: LLMResult, task: LLMTask) -> bool:
        """
        Validate result

        Args:
            result: LLM result to validate
            task: Original task

        Returns:
            True if valid, False otherwise
        """
        raise NotImplementedError


class FormatValidator(BaseValidator):
    """Validate JSON structure and schema"""

    def validate(self, result: LLMResult, task: LLMTask) -> bool:
        """Check if result matches expected format"""
        try:
            # Parse JSON
            data = json.loads(result.raw_response)

            # Check required fields based on task type
            if task.expected_format == "json":
                return self._validate_json_structure(data, task.expected_schema)
            elif task.expected_format == "diff":
                return self._validate_diff_format(result.raw_response)
            else:
                return True

        except json.JSONDecodeError as e:
            logger.warning(f"Format validation failed: Invalid JSON - {e}")
            return False
        except Exception as e:
            logger.error(f"Format validation error: {e}")
            return False

    def _validate_json_structure(self, data: Dict, schema: Dict = None) -> bool:
        """Validate JSON against schema"""
        if not schema:
            return True

        # Simple schema validation (can be enhanced with jsonschema library)
        for key, value_type in schema.items():
            if key not in data:
                logger.warning(f"Missing required field: {key}")
                return False

        return True

    def _validate_diff_format(self, text: str) -> bool:
        """Validate unified diff format"""
        lines = text.split('\n')
        has_diff_header = any(line.startswith('diff --git') for line in lines)
        has_hunks = any(line.startswith('@@') for line in lines)

        return has_diff_header and has_hunks


class StaticValidator(BaseValidator):
    """Validate Python code syntax"""

    def validate(self, result: LLMResult, task: LLMTask) -> bool:
        """Check if generated code is syntactically valid"""
        if task.task_type != "code_generation":
            return True

        try:
            # Extract Python code from result
            code = self._extract_code(result.raw_response)

            if not code:
                return True  # No code to validate

            # Parse with AST
            ast.parse(code)

            # Check for dangerous imports
            if not self._check_safe_imports(code):
                logger.warning("Static validation failed: Dangerous imports detected")
                return False

            return True

        except SyntaxError as e:
            logger.warning(f"Static validation failed: Syntax error - {e}")
            return False
        except Exception as e:
            logger.error(f"Static validation error: {e}")
            return False

    def _extract_code(self, text: str) -> str:
        """Extract Python code from markdown or raw text"""
        # Look for ```python ... ```
        if '```python' in text:
            start = text.find('```python') + 9
            end = text.find('```', start)
            if end > start:
                return text[start:end].strip()

        # Look for ```\n...\n```
        if '```' in text:
            start = text.find('```') + 3
            end = text.find('```', start)
            if end > start:
                return text[start:end].strip()

        # Assume entire text is code
        return text

    def _check_safe_imports(self, code: str) -> bool:
        """Check for dangerous imports"""
        dangerous_modules = ['os.system', 'subprocess', 'eval', 'exec', '__import__']

        for danger in dangerous_modules:
            if danger in code:
                return False

        return True


class SandboxValidator(BaseValidator):
    """Validate code execution in sandbox (expensive, use sparingly)"""

    def validate(self, result: LLMResult, task: LLMTask) -> bool:
        """Run code in isolated sandbox"""
        # This is expensive and requires proper sandboxing
        # For V4, we'll skip this or use it selectively

        logger.info("SandboxValidator: Skipped (not implemented)")
        return True
```

#### 4.1.5 LLMTask 定义

**文件**: `src/core/ai/llm_task.py`

```python
"""
LLM Task Definitions
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import uuid


@dataclass
class LLMTask:
    """Represents a task for LLM to solve"""

    task_id: str
    task_type: str  # "code_generation", "analysis", "planning", etc.
    prompt: str
    system_prompt: str = ""
    expected_format: str = "json"  # "json", "text", "diff"
    expected_schema: Dict[str, Any] = None
    context: Dict[str, Any] = None

    def __post_init__(self):
        if not self.task_id:
            self.task_id = str(uuid.uuid4())[:8]

        if self.expected_schema is None:
            self.expected_schema = {}

        if self.context is None:
            self.context = {}


@dataclass
class LLMResult:
    """Represents LLM result"""

    task_id: str
    provider: str  # "ollama", "openai", "claude"
    raw_response: str
    success: bool
    parsed_data: Dict[str, Any] = None
    validation_errors: list = None

    def __post_init__(self):
        if self.parsed_data is None:
            self.parsed_data = {}

        if self.validation_errors is None:
            self.validation_errors = []
```

---

## 5. Phase 3: 自动化闭环

### 5.1 Evolution Orchestrator

这是整个V4的核心：**错误→分析→设计→实现→验证→PR**的完整闭环。

#### 5.1.1 文件结构

```
flyto2/
├── src/core/evolution/
│   ├── __init__.py
│   ├── orchestrator.py          # 主orchestrator
│   ├── planner.py               # 分析和规划
│   ├── designer.py              # 设计解决方案
│   ├── implementation.py        # 生成代码
│   └── ticket.py                # Evolution ticket定义
├── metrics/
│   ├── evolution_tickets/       # 所有tickets
│   │   └── ticket_<id>.json
│   └── evolution_history.jsonl  # 历史记录
└── scripts/
    └── trigger_evolution.py     # 手动触发进化
```

#### 5.1.2 EvolutionOrchestrator 实现

**文件**: `src/core/evolution/orchestrator.py`

```python
"""
Evolution Orchestrator

Complete evolution pipeline:
1. ErrorCenter triggers ticket
2. Planner analyzes with RAG + Module Catalog
3. Designer creates solution plan (JSON)
4. Implementation generates patches
5. Validator checks patches
6. PR Engine creates pull request
7. Human reviews and merges
8. Webhook updates VectorDB
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from .ticket import EvolutionTicket, TicketStatus
from .planner import EvolutionPlanner
from .designer import EvolutionDesigner  
from .implementation import ImplementationAgent
from src.core.ai.llm_orchestrator import get_llm_orchestrator
from src.core.errors.error_center import get_error_center

logger = logging.getLogger(__name__)


class EvolutionOrchestrator:
    """Orchestrate complete evolution process"""

    def __init__(self):
        self.tickets_dir = Path("metrics/evolution_tickets")
        self.tickets_dir.mkdir(parents=True, exist_ok=True)

        self.planner = EvolutionPlanner()
        self.designer = EvolutionDesigner()
        self.implementation = ImplementationAgent()
        self.llm_orchestrator = get_llm_orchestrator()
        self.error_center = get_error_center()

    async def trigger_from_error_signature(
        self,
        error_signature: str
    ) -> EvolutionTicket:
        """
        Trigger evolution from error signature

        Args:
            error_signature: Error signature from ErrorCenter

        Returns:
            Evolution ticket
        """
        logger.info(f"Triggering evolution for: {error_signature}")

        # Get errors with this signature
        errors = self.error_center.get_errors_by_signature(error_signature)

        if not errors:
            raise ValueError(f"No errors found with signature: {error_signature}")

        # Create ticket
        ticket = EvolutionTicket(
            trigger="error_signature",
            error_signature=error_signature,
            context={
                "error_count": len(errors),
                "first_error": errors[0] if errors else None,
                "recent_errors": errors[:5]
            }
        )

        self._save_ticket(ticket)

        # Run evolution pipeline
        try:
            await self._run_pipeline(ticket)
        except Exception as e:
            ticket.status = TicketStatus.FAILED
            ticket.error = str(e)
            self._save_ticket(ticket)
            raise

        return ticket

    async def _run_pipeline(self, ticket: EvolutionTicket):
        """Run complete evolution pipeline"""
        
        # Step 1: Planning
        ticket.status = TicketStatus.PLANNING
        self._save_ticket(ticket)

        plan = await self.planner.analyze_and_plan(ticket)
        ticket.plan = plan
        self._save_ticket(ticket)

        # Step 2: Design
        ticket.status = TicketStatus.DESIGNING
        self._save_ticket(ticket)

        design = await self.designer.create_solution_design(plan)
        ticket.design = design
        self._save_ticket(ticket)

        # Step 3: Implementation
        ticket.status = TicketStatus.IMPLEMENTING
        self._save_ticket(ticket)

        patches = await self.implementation.generate_patches(design)
        ticket.patches = patches
        self._save_ticket(ticket)

        # Step 4: Validation
        ticket.status = TicketStatus.VALIDATING
        self._save_ticket(ticket)

        validation_result = await self._validate_patches(patches)

        if not validation_result["success"]:
            ticket.status = TicketStatus.VALIDATION_FAILED
            ticket.validation_errors = validation_result["errors"]
            self._save_ticket(ticket)
            return

        # Step 5: Create PR (will implement in PR Engine section)
        ticket.status = TicketStatus.PR_CREATED
        # pr_url = await self._create_pr(ticket)
        # ticket.pr_url = pr_url
        self._save_ticket(ticket)

        logger.info(f"Evolution pipeline complete: {ticket.ticket_id}")

    async def _validate_patches(self, patches: Dict) -> Dict[str, Any]:
        """Validate generated patches"""
        # Placeholder - will use PatchValidator
        return {"success": True, "errors": []}

    def _save_ticket(self, ticket: EvolutionTicket):
        """Save ticket to file"""
        ticket_file = self.tickets_dir / f"ticket_{ticket.ticket_id}.json"
        
        with open(ticket_file, 'w') as f:
            import json
            json.dump(ticket.to_dict(), f, indent=2, ensure_ascii=False)


# Singleton
_orchestrator = None

def get_evolution_orchestrator() -> EvolutionOrchestrator:
    """Get singleton orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = EvolutionOrchestrator()
    return _orchestrator
```

#### 5.1.3 Evolution Ticket 定义

**文件**: `src/core/evolution/ticket.py`

```python
"""
Evolution Ticket

Tracks complete evolution process from trigger to PR merge
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
import uuid


class TicketStatus(Enum):
    """Ticket lifecycle status"""
    CREATED = "created"
    PLANNING = "planning"
    DESIGNING = "designing"
    IMPLEMENTING = "implementing"
    VALIDATING = "validating"
    VALIDATION_FAILED = "validation_failed"
    PR_CREATED = "pr_created"
    HUMAN_REVIEW = "human_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    MERGED = "merged"
    FAILED = "failed"


@dataclass
class EvolutionTicket:
    """Represents an evolution ticket"""

    ticket_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + 'Z')
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + 'Z')

    # Trigger
    trigger: str = "manual"  # "error_signature", "manual", "scheduled"
    error_signature: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

    # Status
    status: TicketStatus = TicketStatus.CREATED

    # Pipeline artifacts
    plan: Optional[Dict] = None
    design: Optional[Dict] = None
    patches: Optional[Dict] = None
    validation_errors: list = field(default_factory=list)

    # PR info
    pr_url: Optional[str] = None
    pr_number: Optional[int] = None
    branch_name: Optional[str] = None

    # Result
    error: Optional[str] = None
    merged_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization"""
        return {
            "ticket_id": self.ticket_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "trigger": self.trigger,
            "error_signature": self.error_signature,
            "context": self.context,
            "status": self.status.value if isinstance(self.status, TicketStatus) else self.status,
            "plan": self.plan,
            "design": self.design,
            "patches": self.patches,
            "validation_errors": self.validation_errors,
            "pr_url": self.pr_url,
            "pr_number": self.pr_number,
            "branch_name": self.branch_name,
            "error": self.error,
            "merged_at": self.merged_at
        }
```

---

## 6. Telegram Bot 集成

### 6.1 指令总表

| 类别 | 指令 | 功能 | 优先级 |
|------|------|------|--------|
| **基础** | `/start` | 启动菜单 | P0 |
| | `/status` | 系统状态 | P0 |
| | `/help` | 帮助信息 | P0 |
| **测试** | `/test_all` | 运行所有测试 | P1 |
| | `/test_module <id>` | 测试指定模块 | P1 |
| **实战** | `/practice` | 启动练习精灵 | P0 |
| | `/practice_stats` | 练习统计 | P2 |
| **竞赛** | `/competition` | 竞赛中心 | P1 |
| | `/leaderboard` | 排行榜 | P2 |
| **进化** | `/evolve` | 触发进化 | P0 |
| | `/debug` | 系统分析报告 | P0 |
| | `/auto` | 自动进化开关 | P1 |
| **模块** | `/modules` | 查看模块目录 | P1 |
| | `/new_module` | 新建模块精灵 | P2 |
| **记忆** | `/memory_search` | 搜索知识库 | P1 |
| | `/memory_stats` | 记忆统计 | P2 |
| **PR** | `/prs` | 查看待审PR | P1 |

### 6.2 `/debug` 指令实现示例

**文件**: `scripts/interactive_evolution_bot.py` (部分代码)

```python
async def handle_debug_command(update, context):
    """Handle /debug command"""
    await update.message.reply_text("🔍 Running system analysis...")

    # Run debug analysis
    from src.core.debug.debug_engine import get_debug_engine

    engine = get_debug_engine()
    report = engine.analyze(hours=24)

    # Generate text report
    text_report = engine.generate_text_report(report)

    # Send report (split if too long)
    if len(text_report) > 4000:
        parts = [text_report[i:i+4000] for i in range(0, len(text_report), 4000)]
        for part in parts:
            await update.message.reply_text(f"```\n{part}\n```", parse_mode='Markdown')
    else:
        await update.message.reply_text(f"```\n{text_report}\n```", parse_mode='Markdown')

    # Add action buttons
    recommendations = report.get("recommendations", [])
    if recommendations:
        keyboard = []
        for i, rec in enumerate(recommendations[:3]):
            if rec["type"] == "error_signature":
                keyboard.append([
                    InlineKeyboardButton(
                        f"🔁 Evolve {rec['signature'][:20]}",
                        callback_data=f"evolve:{rec['signature']}"
                    )
                ])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Quick Actions:",
            reply_markup=reply_markup
        )
```

### 6.3 `/modules` 指令实现

```python
async def handle_modules_command(update, context):
    """Handle /modules command"""
    from src.core.catalog.catalog_manager import get_catalog_manager

    catalog = get_catalog_manager()
    stats = catalog.get_statistics()

    # Build message
    message = f"""📚 Module Catalog

Total Modules: {stats['total_modules']}

By Category:
"""

    for cat, count in sorted(stats['by_category'].items()):
        message += f"  {cat}: {count}\n"

    message += f"\nStatus:\n"
    for status, count in stats['by_status'].items():
        message += f"  {status}: {count}\n"

    message += f"\nLast updated: {stats['last_updated']}"

    # Add search button
    keyboard = [[
        InlineKeyboardButton("🔍 Search Modules", callback_data="modules:search")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(message, reply_markup=reply_markup)
```

---

## 7. 测试策略

### 7.1 单元测试

每个组件都需要单元测试：

```
tests/
├── test_catalog_manager.py
├── test_error_center.py
├── test_debug_engine.py
├── test_llm_orchestrator.py
└── test_evolution_orchestrator.py
```

### 7.2 集成测试

**文件**: `tests/integration/test_evolution_pipeline.py`

```python
"""
Test complete evolution pipeline
"""

import pytest
from src.core.evolution.orchestrator import get_evolution_orchestrator
from src.core.errors.error_center import get_error_center


@pytest.mark.asyncio
async def test_complete_evolution_pipeline():
    """Test error → ticket → plan → design → patch → PR"""
    
    # 1. Create mock error
    error_center = get_error_center()
    await error_center.log_error(
        error=Exception("Timeout on Amazon"),
        context={"url": "https://amazon.com/dp/123"},
        module_id="browser.goto",
        workflow="daily_practice",
        category="scrape_failure"
    )

    # 2. Trigger evolution
    orchestrator = get_evolution_orchestrator()
    ticket = await orchestrator.trigger_from_error_signature("err_timeout_xxxx")

    # 3. Verify ticket created
    assert ticket is not None
    assert ticket.status.value in ["pr_created", "validation_failed"]

    # 4. Check plan generated
    assert ticket.plan is not None
    assert "required_modules" in ticket.plan

    # 5. Check design generated
    assert ticket.design is not None
    assert "changes" in ticket.design
```

---

## 8. 部署与运维

### 8.1 Windows 启动脚本

**文件**: `start_bot_with_memory.bat`

```bat
@echo off
cd /d %~dp0

echo ========================================
echo Flyto2 V4 - Starting with Memory
echo ========================================

REM Activate virtualenv
call venv\Scripts\activate

REM Set environment variables
set QDRANT_URL=http://localhost:6333
if not defined OPENAI_API_KEY (
    echo WARNING: OPENAI_API_KEY not set
)

REM Start bot
echo Starting Telegram Bot...
python scripts/interactive_evolution_bot.py --with-memory

pause
```

### 8.2 定时任务设置

**Windows Task Scheduler**:
- 任务: Run Debug Analysis
- 触发: 每小时
- 操作: `python scripts/run_debug_analysis.py`

**Linux Cron**:
```bash
# 每小时运行debug analysis
0 * * * * cd /path/to/flyto2 && python scripts/run_debug_analysis.py >> logs/debug.log 2>&1

# 每天凌晨更新module catalog
0 0 * * * cd /path/to/flyto2 && python scripts/update_module_catalog.py >> logs/catalog.log 2>&1
```

### 8.3 监控指标

**关键指标**:
1. Error count (最近24小时)
2. Evolution tickets (active/completed/failed)
3. Module catalog size
4. VectorDB size
5. Workflow success rate

**Prometheus metrics示例**:
```python
from prometheus_client import Counter, Gauge

error_counter = Counter('flyto2_errors_total', 'Total errors', ['signature'])
evolution_tickets_gauge = Gauge('flyto2_evolution_tickets', 'Active tickets')
module_count_gauge = Gauge('flyto2_modules_total', 'Total modules')
```

---

## 9. 实施检查清单

### Phase 1: 核心基础设施

- [ ] 创建 `modules/catalog.json` schema
- [ ] 实现 `CatalogManager`
- [ ] 实现 `ModuleScanner`
- [ ] 创建 `update_module_catalog.py` 脚本
- [ ] 运行一次catalog更新
- [ ] 验证module同步到VectorDB

- [ ] 创建 `ErrorCenter` 类
- [ ] 创建 `generate_error_signature()` 函数
- [ ] 创建 `metrics/error_events.jsonl`
- [ ] 集成到workflow engine
- [ ] 测试error logging

- [ ] 创建 `DebugEngine` 类
- [ ] 实现 `analyze()` 方法
- [ ] 创建 `run_debug_analysis.py` 脚本
- [ ] 设置定时任务
- [ ] 测试debug报告生成

### Phase 2: 智能化增强

- [ ] 创建 `LLMOrchestrator` 类
- [ ] 实现Ollama→GPT→Claude pipeline
- [ ] 创建 `Validators` (Format/Static)
- [ ] 测试multi-model fallback

### Phase 3: 自动化闭环

- [ ] 创建 `EvolutionOrchestrator` 类
- [ ] 实现 `Planner`, `Designer`, `Implementation`
- [ ] 创建 `EvolutionTicket` 数据结构
- [ ] 测试完整evolution pipeline

### TG Bot集成

- [ ] 添加 `/debug` 指令
- [ ] 添加 `/modules` 指令
- [ ] 添加 `/evolve` 指令
- [ ] 添加 `/memory_search` 指令
- [ ] 测试所有指令

### 部署

- [ ] 创建 `start_bot_with_memory.bat`
- [ ] 设置定时任务
- [ ] 配置监控
- [ ] 准备文档

---

## 10. 常见问题 FAQ

### Q: Catalog更新频率?
**A**: 新增module时手动运行，或每天定时更新一次。

### Q: ErrorCenter会拖慢performance吗?
**A**: 不会，异步写入JSONL，不阻塞主流程。

### Q: DebugEngine报告太长怎么办?
**A**: TG Bot自动分段发送，或提供"View in File"按钮。

### Q: Evolution失败了怎么办?
**A**: Ticket保留完整log，人工review后可重试或reject。

### Q: VectorDB什么时候清理?
**A**: 提供 `/memory_cleanup` 指令，手动清理>90天或低质量数据。

---

## 11. 下一步行动

**立即开始**:
1. 运行 `python scripts/update_module_catalog.py` 建立catalog
2. 集成ErrorCenter到现有workflow engine
3. 运行 `python scripts/run_debug_analysis.py` 看第一份报告

**本周完成**:
1. Phase 1所有组件
2. TG Bot `/debug` 和 `/modules` 指令
3. 第一次完整test

**下周目标**:
1. Phase 2 LLMOrchestrator
2. Phase 3 Evolution Pipeline
3. 第一个auto-generated PR!

---

**文档版本**: V4.0
**最后更新**: 2025-12-02
**维护者**: Flyto2 Team

如有问题，请查阅 `/docs` 或提issue到GitHub。
