# 📑 Documentation Index

Complete file organization guide for Flyto2 project.

---

## 📂 Root Directory Files

### Essential Files
- **README.md** - Project overview, features, installation
- **QUICKSTART.md** - Unified quick start guide (Developer/Bot/Monitoring)
- **CONTRIBUTING.md** - Contribution guidelines, PR process, and repository maintenance
- **LICENSE** - MIT License
- **DOCUMENTATION_INDEX.md** - This file (complete file organization guide)

### Configuration Files
- **requirements.txt** - Core Python dependencies
- **requirements-dev.txt** - Development dependencies
- **requirements-integrations.txt** - Optional integration dependencies
- **setup.py** - Package setup configuration

### Launch Scripts
- **START_BOT.bat** - Windows one-click bot launcher

---

## 📚 Documentation Structure (`docs/`)

### 🚀 Getting Started (`docs/getting-started/`)
Quick start guides and basic usage:
- **CLI.md** - Command-line interface reference and usage
- **DSL.md** - YAML workflow syntax specification
- **PARAMETER_BEST_PRACTICES.md** - Workflow parameter design guide
- **PROMPT_GUIDE.md** - AI assistant prompt engineering

**When to use:**
- New users learning the system
- Writing workflows for the first time
- Looking up CLI commands or YAML syntax

### 🏗️ Architecture (`docs/architecture/`)
System design and structure:
- **ARCHITECTURE.md** - Core engine architecture
- **PROJECT_STRUCTURE.md** - Directory and file organization
- **LEVEL_4_ARCHITECTURE.md** - Advanced monitoring system design
- **TELEGRAM_BOT_ARCHITECTURE.md** - Telegram bot structure

**When to use:**
- Understanding system internals
- Contributing to core engine
- Designing new features

### 🧩 Modules (`docs/modules/`)
Module development and reference:
- **MODULES.md** - Complete module registry (100+ modules)
- **MODULE_SPECIFICATION.md** - Official module specification
- **MODULE_QUICK_REFERENCE.md** - Quick lookup table
- **WRITING_MODULES.md** - Module development guide
- **MODULE_CATEGORIES.md** - Category organization
- **MODULE_QUALITY_SYSTEM.md** - Quality tracking system
- **MODULE_PHASE2_FEATURES.md** - Advanced module features
- **DYNAMIC_MODULE_REGISTRY.md** - Runtime module registration

**When to use:**
- Looking up available modules
- Creating new modules
- Understanding module architecture

### 🚢 Deployment (`docs/deployment/`)
Installation and deployment guides:
- **WINDOWS_SETUP.md** - Windows installation and setup
- **TELEGRAM_BOT_SETUP.md** - Telegram bot deployment

**When to use:**
- Setting up production environment
- Deploying on Windows
- Configuring Telegram bot

### 📘 Advanced Guides (`docs/guides/`)
Advanced topics and integrations:
- **META_WORKFLOWS.md** - Self-modifying workflows
- **META_WORKFLOW_SAFETY.md** - Safe meta-programming practices
- **CASE_STUDY_META_WORKFLOW.md** - Real-world meta-workflow example
- **UI_BUILDER_INTEGRATION.md** - Visual workflow editor integration
- **UI_MODULE_INTEGRATION.md** - Module UI components
- **PHASE2_UI_INTEGRATION.md** - Advanced UI features
- **LOCAL_AI_AGENT.md** - Local AI integration guide

**When to use:**
- Building advanced workflows
- Integrating with UI builders
- Implementing meta-workflows

### 📦 Archive (`archive/`)
Historical and internal documents (not for general use):
- **IMPLEMENTATION_SUMMARY.md** - Meta-workflow implementation (historical)
- **METADATA_API.md** - UI Builder API integration report (historical)
- **PROJECT_AUDIT_REPORT.md** - Project audit 2025-11-30 (one-time review)

**Note:** These are kept for historical reference only. Current documentation supersedes these files.

---

## 🔧 Source Code Structure (`src/`)

### Core Engine (`src/core/`)
```
src/core/
├── engine/              # Workflow execution engine
│   ├── workflow_engine.py    # Main engine
│   └── variable_resolver.py  # Variable interpolation
├── modules/             # All modules
│   ├── atomic/         # Core modules (no dependencies)
│   ├── third_party/    # External integrations
│   ├── base.py         # BaseModule class
│   └── registry.py     # Module registration
└── browser/            # Playwright browser driver
    └── driver.py
```

### CLI Interface (`src/cli/`)
```
src/cli/
└── main.py            # CLI entry point
```

---

## 🧪 Tests (`tests/`)

```
tests/
├── test_modules.py              # Module tests
├── test_phase2_features.py      # Phase 2 feature tests
├── test_engine.py               # Engine tests
└── workflows/                   # Test workflows
    └── _test/                   # Test YAML files
```

---

## 📦 Workflows (`workflows/`)

### Production Workflows
```
workflows/
├── api_pipeline.yaml                 # Pure API workflow
├── google_search.yaml                # Browser automation
├── ai_content_summarizer.yaml        # Browser + AI
├── github_to_slack.yaml              # GitHub alerts
├── daily_report_email.yaml           # Email reports
└── multi_channel_alert.yaml          # Multi-platform broadcast
```

### Meta Workflows (`workflows/meta/`)
Self-modifying and monitoring workflows:
```
workflows/meta/
├── monitor_regressions.yaml          # Daily monitoring
├── auto_merge_pr.yaml                # PR auto-merge
└── README.md                         # Meta workflow docs
```

### Test Workflows (`workflows/_test/`)
Unit test workflows for module validation

---

## 🛠️ Scripts (`scripts/`)

### Validation Scripts
- **validate_all_modules.py** - Validate all module definitions
- **lint_modules.py** - Lint module code
- **run_quality_tests.sh** - Run quality tests

### Management Scripts
- **update_metrics.py** - Update quality metrics
- **deployment_manager.py** - Manage module deployments
- **start_bot_windows.ps1** - Windows bot launcher script
- **setup_windows_tasks.ps1** - Windows scheduled tasks setup

### Utility Scripts
- **README.md** - Scripts documentation

---

## 📊 Metrics (`metrics/`)

Quality and deployment tracking:
- **module_quality.json** - Current quality status
- **module_deployment_history.json** - Deployment history
- **test_results_YYYYMMDD_HHMMSS.txt** - Test results (latest only)

---

## 🌍 Internationalization (`i18n/`)

Translation files:
```
i18n/
├── en.json           # English
├── zh.json           # Chinese
└── ja.json           # Japanese
```

---

## 📋 Examples (`examples/`)

Example configurations and workflows

---

## 🔍 Quick File Finder

### I want to...

**Learn the basics**
→ Start with `QUICKSTART.md` → Choose your path

**Run a workflow**
→ `docs/getting-started/CLI.md`

**Write a workflow**
→ `docs/getting-started/DSL.md`

**Find available modules**
→ `docs/modules/MODULES.md` or `docs/modules/MODULE_QUICK_REFERENCE.md`

**Create a module**
→ `docs/modules/WRITING_MODULES.md`

**Understand architecture**
→ `docs/architecture/ARCHITECTURE.md`

**Deploy on Windows**
→ `docs/deployment/WINDOWS_SETUP.md`

**Setup Telegram bot**
→ `docs/deployment/TELEGRAM_BOT_SETUP.md`

**Build UI integration**
→ `docs/guides/UI_BUILDER_INTEGRATION.md`

**Work with meta-workflows**
→ `docs/guides/META_WORKFLOWS.md`

**Contribute code**
→ `CONTRIBUTING.md`

**Check quality metrics**
→ `metrics/module_quality.json`

**View test results**
→ `metrics/test_results_*.txt` (latest)

---

## 📏 File Naming Conventions

### Documentation Files
- **ALL_CAPS.md** - Major documentation files
- **lowercase.md** - Supporting files
- Prefix `_` for test/internal files

### Python Files
- **snake_case.py** - All Python files
- **test_*.py** - Test files

### YAML Files
- **snake_case.yaml** - Workflow files
- Prefix `test_` for test workflows

### Directories
- **lowercase** - All directories
- **snake_case** - Multi-word directories

---

## 🔄 File Update Frequency

### Frequently Updated
- `metrics/module_quality.json` - Updated after each test run
- `metrics/test_results_*.txt` - New file per test run (old ones cleaned)

### Occasionally Updated
- Module files in `src/core/modules/`
- `docs/modules/MODULES.md` - When modules added
- Workflow files in `workflows/`

### Rarely Updated
- `docs/getting-started/DSL.md` - Stable specification
- `docs/architecture/ARCHITECTURE.md` - Core design
- `CONTRIBUTING.md` - Contribution guidelines

---

## 🗂️ Version Control

### Tracked Files
All files except:
- `.env` - Environment variables (secrets)
- `venv/` - Virtual environment
- `__pycache__/` - Python cache
- `.pytest_cache/` - Pytest cache
- Old test results (keep latest only)

### Important: Keep Updated
When adding new files, update this index!

---

**Last Updated:** 2025-12-01

**Maintained By:** Project maintainers

**Questions?** See `docs/README.md` or open an issue.
