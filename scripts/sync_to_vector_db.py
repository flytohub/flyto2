#!/usr/bin/env python3
"""
Sync Flyto2 Project Knowledge to Vector Database

Stores comprehensive project information including:
- Current implementation status
- Known issues and blockers
- Architecture changes (atomization)
- Perfect Flow Bot implementation
- Real test results
- Dependencies and requirements
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.utils.vector_db_manager import vector_store


async def sync_project_knowledge():
    """Sync all current project knowledge to vector DB"""

    print("🔄 Syncing Flyto2 Project Knowledge to Vector Database")
    print("=" * 60)

    timestamp = datetime.now().isoformat()

    # Knowledge entries to store
    knowledge_entries = [
        # 1. Critical Dependencies
        {
            "content": """
CRITICAL DEPENDENCY: Ollama Local LLM

Status: REQUIRED BUT NOT RUNNING (as of 2025-12-02)

Impact:
- AI workflow generation: BLOCKED
- AI Error Solver: BLOCKED
- Telegram Bot AI features: BLOCKED
- Training system AI consultation: BLOCKED

Installation:
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Start server
ollama serve

# Download model
ollama pull llama3.2
```

Test connection:
```bash
curl http://localhost:11434/api/generate -d '{"model": "llama3.2", "prompt": "hello"}'
```

Without Ollama running, the entire AI-powered workflow generation pipeline is non-functional.
""",
            "metadata": {
                "category": "dependency",
                "type": "critical",
                "component": "ollama",
                "status": "required_not_running",
                "priority": "P0",
                "updated": timestamp
            }
        },

        # 2. Perfect Flow Bot Implementation
        {
            "content": """
Perfect Flow Bot - Telegram Bot with AI-Driven Workflow Generation

Location: scripts/telegram_bot_perfect.py
Launcher: START_PERFECT_BOT.sh
Documentation: PERFECT_FLOW.md

Flow:
1. User sends task via Telegram (e.g., "爬蟲 google.com")
2. Intent Detection → Classify task type (crawl/api/notification)
3. AI YAML Generation → Ollama generates workflow YAML
4. Test Execution → WorkflowEngine executes the workflow
5. If Failure → Show 3 options:
   - 🙋 Let user solve manually
   - 🤖 Let bot solve (uses AI Error Solver)
   - 💰 Ask OpenAI (premium, not implemented)
6. Retry → Continue testing until success (max 3 attempts)
7. Success → Option to create PR or use directly

Features Implemented:
✅ Intent detection (100% working)
✅ Telegram bot framework with inline keyboards
✅ AI workflow generation (requires Ollama)
✅ Workflow execution integration
✅ Three-way error resolution options
✅ AI Error Solver integration
🚧 OpenAI resolution (planned)
🚧 GitHub PR creation (planned)

Environment Variables Required:
- TELEGRAM_BOT_TOKEN (required)
- TELEGRAM_ALLOWED_USERS (optional, comma-separated user IDs)
- OLLAMA_URL (optional, defaults to http://localhost:11434)
- OPENAI_API_KEY (optional, for premium option)

Current Status: Code complete, blocked by Ollama dependency
""",
            "metadata": {
                "category": "feature",
                "type": "telegram_bot",
                "component": "perfect_flow_bot",
                "status": "implemented",
                "file": "scripts/telegram_bot_perfect.py",
                "updated": timestamp
            }
        },

        # 3. Atomization Refactoring
        {
            "content": """
Atomization Refactoring - November 2025

Goal: Convert monolithic files into atomic, reusable modules

Phase 1 - Utility Abstractions (Completed):
1. src/core/utils/notifier.py (125 lines)
   - Unified notification system
   - Replaces duplicate _notify() methods across 8+ files
   - Supports: console, callback, file backends

2. src/core/utils/vector_db_manager.py (188 lines)
   - Singleton vector DB connection manager
   - One-liner search/store interface
   - Eliminates ~240 lines of duplicate code

3. src/core/utils/http_client.py (267 lines)
   - Unified HTTP client with retry logic
   - Ollama/OpenAI helper methods
   - JSON extraction support

Phase 2 - Healing Modules (Completed):
Created 6 atomic modules in src/core/healing/atomic/:
1. vector_query.py (62 lines) - Query similar solutions
2. prompt_builder.py (111 lines) - Build AI prompts
3. ai_consulter.py (137 lines) - Consult AI for solutions
4. solution_executor.py (94 lines) - Execute solutions
5. similarity_trainer.py (156 lines) - Train on solutions
6. solution_archiver.py (151 lines) - Archive solutions

Result: Refactored ai_error_solver.py from 670 to 194 lines (-71%)

Phase 3 - Training Modules (Completed):
Created 4 atomic modules in src/core/training/atomic/:
1. robots_parser.py (123 lines) - Parse robots.txt
2. html_pattern_detector.py (142 lines) - Detect HTML patterns
3. schema_inferrer.py (218 lines) - Infer data schemas
4. recommendation_generator.py (158 lines) - Generate recommendations

Benefits:
- Single responsibility per module
- Reusable across different systems
- Easier testing and maintenance
- Reduced code duplication
- Clear separation of concerns

Architecture Principle: "No hardcoded error handling - all errors go to AI"
""",
            "metadata": {
                "category": "refactoring",
                "type": "architecture",
                "component": "atomization",
                "status": "completed",
                "modules_created": 13,
                "lines_reduced": 476,
                "updated": timestamp
            }
        },

        # 4. Real Test Results
        {
            "content": """
End-to-End Test Results (2025-12-02)

Test Command: python3 test_end_to_end.py
Results: 1/3 tests passing

✅ PASS: Intent Detection
- IntentDetector correctly identifies task types
- Test cases: "爬蟲 google.com", "幫我爬蟲google 搜尋蝦皮"
- Returns: type, confidence, task_type
- Status: 100% functional

❌ FAIL: Workflow Engine
- Issue: Status naming mismatch
- Engine returns: result['status'] = 'success'
- Test expects: result['status'] = 'completed'
- Impact: Medium - Test failure only, not functional issue
- Fix needed: Standardize status naming

❌ FAIL: Full Crawl Test
- Issue: Ollama connection refused
- Error: Connection to localhost:11434 failed
- Root cause: Ollama service not running
- Impact: CRITICAL - Blocks all AI workflow generation
- Dependency chain blocked:
  * SmartExecutor → AIErrorSolver → Ollama
  * PerfectBot → Workflow Generation → Ollama
  * Training System → AI Consultation → Ollama

Actual Usability Assessment:
- Architecture Design: 9/10
- Code Completeness: 8/10
- Actual Functionality: 3/10 (due to Ollama dependency)

Quote from analysis: "沒有 Ollama，這個專案就像沒有引擎的車"
(Without Ollama, this project is like a car without an engine)

Priority Fixes:
1. P0: Start Ollama or add graceful fallback
2. P1: Standardize WorkflowEngine status naming
3. P2: Add dependency health checks on startup
4. P3: Document all critical dependencies clearly
""",
            "metadata": {
                "category": "testing",
                "type": "end_to_end",
                "status": "partially_passing",
                "pass_rate": "1/3",
                "blocker": "ollama_not_running",
                "updated": timestamp
            }
        },

        # 5. AI Error Solver Architecture
        {
            "content": """
AI Error Solver - Self-Healing System Architecture

Location: src/core/healing/ai_error_solver.py
Status: Implemented and refactored

Core Philosophy: "No hardcoded error handling - feed all errors to AI"

Flow:
1. Error occurs during workflow execution
2. Query vector DB for similar past solutions
3. Build AI prompt with context:
   - Error message and type
   - Execution context
   - Similar solutions (if found)
   - System environment info
4. Consult AI (Ollama/OpenAI) for solution
5. Parse AI response → Extract commands to execute
6. Execute solution commands
7. If successful:
   - Archive solution to vector DB
   - Train similarity model (AI prediction vs actual solution)
8. Return result to caller

Atomic Modules Used:
- VectorQueryModule.query_similar_solutions()
- PromptBuilderModule.build_error_resolution_prompt()
- AIConsulterModule.consult()
- SolutionExecutorModule.execute()
- SolutionArchiverModule.archive()
- SimilarityTrainerModule.train()

Features:
✅ Vector DB similarity search (ChromaDB/Qdrant)
✅ AI consultation with local LLM (Ollama) or cloud (OpenAI)
✅ Solution execution with safety checks
✅ Automatic solution archiving
✅ Similarity training for continuous improvement
✅ Notification callback support
✅ Dry-run mode for testing
✅ Multi-backend notification (console, callback, file)

Dependencies:
- Ollama (local LLM) or OpenAI API key
- Vector DB (ChromaDB with local embedding or Qdrant)
- Atomic modules in src/core/healing/atomic/

Integration Points:
- SmartExecutor: Used in error retry loop
- PerfectBot: Used in "🤖 Let bot solve" option
- Training System: Used in autonomous improvement

Current Limitation: Requires Ollama to be running for local AI
""",
            "metadata": {
                "category": "feature",
                "type": "ai_system",
                "component": "error_solver",
                "status": "implemented",
                "file": "src/core/healing/ai_error_solver.py",
                "updated": timestamp
            }
        },

        # 6. Known Issues and Blockers
        {
            "content": """
Known Issues and Blockers (2025-12-02)

CRITICAL (P0):
1. Ollama Not Running
   - Impact: All AI features non-functional
   - Affected: Workflow generation, error solving, training
   - Fix: Start Ollama service OR implement graceful fallback
   - Command: ollama serve

2. SmartExecutor Syntax Error (FIXED)
   - Was: Line 99 unterminated string literal
   - Impact: Entire system unusable
   - Status: ✅ Fixed in recent commit
   - Fix: Combined multi-line string into single line

MEDIUM (P1):
3. WorkflowEngine Status Naming
   - Issue: Returns 'success', test expects 'completed'
   - Impact: Test failures, not functional issue
   - Fix: Standardize to one naming convention
   - Location: src/core/engine/workflow_engine.py

4. README.md Outdated
   - Issue: Doesn't reflect current architecture
   - Missing: Ollama dependency, Perfect Bot, atomization
   - Missing: Real test results and known issues
   - Fix: Update with honest current status

LOW (P2):
5. Browser Modules Untested
   - Status: Code exists and looks complete
   - Issue: No real-world browser automation test
   - Risk: Unknown if Playwright integration actually works
   - Fix: Create browser automation E2E test

6. OpenAI Integration Not Implemented
   - Feature: "💰 Ask OpenAI" option in PerfectBot
   - Status: 🚧 Planned, not implemented
   - Impact: Low - Ollama provides same functionality

7. GitHub PR Creation Not Implemented
   - Feature: Auto-create PR after successful workflow
   - Status: 🚧 Planned, not implemented
   - Impact: Low - manual PR creation works fine

User Feedback:
- "你這專案 超級不AI的" (This project is super not-AI)
  → Context: Bot was retrying 3x with same params instead of using AI
  → Fixed: Integrated AI Error Solver into retry loop

- "很多你實際覺得可以行 但都不行" (Many things you think work actually don't)
  → Response: Created REAL_STATUS.md with honest assessment
  → Action: Running actual E2E tests, not just assuming things work

Development Principle:
"Walk through the entire project flow - many things assumed to work actually don't"
""",
            "metadata": {
                "category": "issues",
                "type": "bug_tracker",
                "status": "documented",
                "critical_count": 2,
                "critical_fixed": 1,
                "updated": timestamp
            }
        },

        # 7. Module Registry Status
        {
            "content": """
Module Registry - Current Status (2025-12-02)

Total Modules Registered: 123 modules

Categories:
- browser: 9 modules (launch, goto, click, type, extract, screenshot, close, etc.)
- element: 3 modules (query, text, attribute)
- string: 7 modules (uppercase, lowercase, split, replace, etc.)
- array: 10 modules (filter, sort, map, reduce, etc.)
- file: 6 modules (read, write, exists, delete, etc.)
- data: 5 modules (csv, json, templates)
- math: 6 modules (calculate, round, floor, etc.)
- datetime: 4 modules (format, parse, add, subtract)
- object: 5 modules (keys, values, merge, etc.)
- api: HTTP modules
- notification: Slack, Discord, Telegram, Email
- ai: OpenAI, Ollama
- training: 4 new atomic modules
- healing: 6 new atomic modules

Atomic Modules Architecture:
- Each module: Single responsibility
- Composable: Combine into complex workflows
- Reusable: Used across different systems
- Testable: Isolated unit testing
- Documented: Metadata in registry

Registry Location: src/core/modules/registry.py
Module Base Class: src/core/modules/base.py

Recent Additions (Atomization Phase):
✅ 6 healing atomic modules
✅ 4 training atomic modules
✅ 3 utility abstractions (notifier, vector_db_manager, http_client)

Module Development Pattern:
```python
from src.core.modules.base import BaseModule
from src.core.modules.registry import register_module

@register_module('module.name')
class MyModule(BaseModule):
    module_name = "Display Name"
    module_description = "What it does"

    def validate_params(self):
        # Validate params
        pass

    async def execute(self):
        # Execute logic
        return {"status": "success", "result": data}
```

Quality: High code completeness (8/10), architecture design (9/10)
""",
            "metadata": {
                "category": "system",
                "type": "module_registry",
                "status": "operational",
                "module_count": 123,
                "updated": timestamp
            }
        },

        # 8. Project Philosophy and Direction
        {
            "content": """
Flyto2 Project Philosophy and Direction

Core Principles:

1. "No Hardcoded Error Handling - All Errors Go to AI"
   - Don't write if/else for every error type
   - Feed errors to AI Error Solver
   - Let AI figure out the solution
   - Archive successful solutions for future use

2. "Git-Native Workflow Automation"
   - Workflows as YAML files, not database entries
   - Version control via git
   - PR-based workflow review
   - Portable and deployable anywhere

3. "Atomic and Composable"
   - Every function should be atomic
   - Single responsibility per module
   - Combine atomic modules into complex workflows
   - Reusable components across different systems

4. "AI-First, Not Rule-First"
   - Use AI for decision making, not hardcoded rules
   - Intent detection over command parsing
   - AI-generated workflows over templates
   - Continuous learning from solutions

5. "Honest Assessment Over Optimism"
   - Test everything end-to-end
   - Document what actually works vs what should work
   - Real status reports (see REAL_STATUS.md)
   - User quote: "很多你實際覺得可以行 但都不行"

Architecture Decisions:

1. Local-First AI (Ollama)
   - Privacy: Data never leaves machine
   - Cost: No cloud API fees
   - Offline: Works without internet
   - Fallback: Can use OpenAI if needed

2. Vector DB for Knowledge
   - Store: Successful solutions, training data
   - Search: Similarity-based solution lookup
   - Learn: Continuous improvement
   - Backends: ChromaDB (local), Qdrant (production)

3. Telegram as Interface
   - Mobile-first: Control from phone
   - Interactive: Inline keyboard options
   - Real-time: Instant feedback
   - Simple: No complex UI needed

4. YAML Workflows
   - Human-readable: Easy to understand
   - Version-controlled: Git integration
   - Portable: Run anywhere
   - Standard: No proprietary format

Perfect Flow (User Vision):
TG input → Bot thinks → Generate YAML → Test →
  → If fail: [User solve] [Bot solve] [Ask OpenAI] →
  → Retry → Success → Create PR → User verifies

Current Challenge: "這專案就像沒有引擎的車" without Ollama running

Next Steps:
1. Fix Ollama dependency (detect, guide, fallback)
2. Complete E2E testing
3. Document real status in README
4. Sync knowledge to vector DB ← You are here
""",
            "metadata": {
                "category": "philosophy",
                "type": "project_direction",
                "status": "documented",
                "updated": timestamp
            }
        }
    ]

    # Store all knowledge entries
    print(f"\n📦 Storing {len(knowledge_entries)} knowledge entries...\n")

    for i, entry in enumerate(knowledge_entries, 1):
        try:
            await vector_store(
                content=entry["content"],
                metadata=entry["metadata"],
                collection_name="flyto2_project_knowledge"
            )

            category = entry["metadata"]["category"]
            comp = entry["metadata"].get("component", entry["metadata"].get("type", ""))
            print(f"✅ [{i}/{len(knowledge_entries)}] Stored: {category}/{comp}")

        except Exception as e:
            print(f"❌ [{i}/{len(knowledge_entries)}] Failed: {e}")

    print("\n" + "=" * 60)
    print("✅ Vector DB sync complete!")
    print("\n💡 Knowledge stored:")
    print("   - Critical dependencies (Ollama)")
    print("   - Perfect Flow Bot implementation")
    print("   - Atomization refactoring results")
    print("   - Real test results and issues")
    print("   - AI Error Solver architecture")
    print("   - Module registry status")
    print("   - Project philosophy and direction")
    print("\n🔍 Query example:")
    print("   from src.core.utils.vector_db_manager import vector_search")
    print("   results = await vector_search('How to fix Ollama error?')")


async def main():
    try:
        await sync_project_knowledge()
    except Exception as e:
        print(f"\n❌ Sync failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
