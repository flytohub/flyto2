# Flyto2 Project Structure

Clean, organized project structure following Python/GitHub best practices.

## 📁 Directory Structure

```
flyto2/                          # GitHub Repository
│
├── 📚 Documentation
│   ├── README.md                # Project homepage
│   ├── CONTRIBUTING.md          # Contribution guide
│   ├── LICENSE                  # MIT License
│   ├── PROJECT_STRUCTURE.md     # This file
│   └── GITHUB_METADATA.md       # GitHub repository metadata guide
│
├── 🎨 assets/                   # Brand Assets
│   ├── logo.svg                 # Flyto logo (vector)
│   ├── architecture.svg         # Architecture diagram
│   └── README.md                # Asset specifications
│
├── 📦 Installation
│   ├── setup.py                 # Package setup
│   ├── requirements.txt         # Core dependencies
│   ├── requirements-dev.txt     # Development dependencies
│   └── requirements-integrations.txt  # Optional integrations
│
├── 📖 docs/                     # Detailed Documentation
│   ├── DSL.md                   # YAML workflow syntax
│   ├── MODULES.md               # Complete module reference
│   ├── CLI.md                   # CLI usage guide
│   ├── WRITING_MODULES.md       # Module development guide
│   ├── ARCHITECTURE.md          # System architecture
│   └── UI_BUILDER_INTEGRATION.md  # UI integration guide
│
├── 💻 src/                      # Source Code
│   ├── core/                    # Core workflow engine
│   │   ├── engine/              # Workflow execution engine
│   │   │   ├── variable_resolver.py
│   │   │   └── workflow_engine.py
│   │   ├── modules/             # Module System (Three-tier Architecture)
│   │   │   ├── __init__.py      # Main module entry point
│   │   │   ├── registry.py      # Module registry
│   │   │   ├── base.py          # Base module class
│   │   │   │
│   │   │   ├── atomic/          # Atomic Modules (no external dependencies)
│   │   │   │   ├── browser_ops/ # Browser automation (Playwright)
│   │   │   │   ├── data/        # Data transformation (CSV, JSON)
│   │   │   │   ├── utility/     # Utilities (delay, random, hash)
│   │   │   │   ├── file/        # File operations (read, write, exists)
│   │   │   │   ├── string/      # String processing (split, replace, regex)
│   │   │   │   ├── array/       # Array manipulation (filter, sort, unique)
│   │   │   │   └── math/        # Math operations (calculate)
│   │   │   │
│   │   │   ├── third_party/     # Third-party Integrations
│   │   │   │   ├── ai/          # AI services (OpenAI, Claude, Gemini)
│   │   │   │   ├── communication/  # Messaging (Slack, Discord, Telegram, Email)
│   │   │   │   ├── database/    # Databases (PostgreSQL, MySQL, MongoDB)
│   │   │   │   ├── cloud/       # Cloud storage (AWS S3)
│   │   │   │   ├── productivity/   # Productivity tools (Notion, Google Sheets)
│   │   │   │   └── developer/   # Developer tools (GitHub, HTTP APIs)
│   │   │   │
│   │   │   └── composite/       # Composite Modules (high-level templates)
│   │   │       └── README.md    # Coming in v1.1
│   │   │
│   │   └── browser/             # Browser automation driver
│   │       └── driver.py        # Playwright driver
│   │
│   ├── integrations/            # Legacy integrations (deprecated)
│   │   ├── __init__.py
│   │   └── openai_integration.py
│   │
│   ├── ui/web/backend/          # Web API backend
│   │   ├── app.py               # FastAPI app
│   │   └── api/
│   │       └── modules_metadata.py  # Metadata API
│   │
│   └── cli/                     # Command-line interface
│       ├── __init__.py
│       └── main.py
│
├── 🧪 tests/                    # Test Suite
│   ├── test_engine.py           # Engine tests
│   ├── test_metadata_api.py     # Metadata API tests
│   └── test_api_server.py       # API server tests
│
├── 🔧 scripts/                  # Utility Scripts
│   └── start_api_server.py      # API server launcher
│
├── 📋 workflows/                # Example Workflows
│   ├── google_search.yaml       # Google search automation
│   ├── api_pipeline.yaml        # API integration pipeline
│   ├── ai_content_summarizer.yaml  # Browser + AI workflow
│   ├── multi_channel_alert.yaml # Multi-channel notifications
│   ├── daily_report_email.yaml  # Scheduled reporting
│   └── [5 more examples]        # Additional workflow templates
│
├── 📝 examples/                 # Configuration Examples
│   ├── engine.yaml              # Engine config example
│   └── NAMESPACES.yaml          # Module namespace reference
│
└── 🌍 i18n/                     # Internationalization
    ├── en.json                  # English translations
    ├── zh.json                  # Chinese translations
    └── ja.json                  # Japanese translations
```

## 🎯 Key Directories

### Source Code (`src/`)
All production code lives here. The main components are:

- **core/** - The heart of flyto2
  - `engine/` - Workflow execution, variable resolution
  - `modules/` - Three-tier module architecture (see below)
  - `browser/` - Playwright browser automation driver

- **core/modules/** - Three-tier Module System
  - **atomic/** - Atomic modules (no external dependencies)
    - `browser_ops/` - Browser automation with Playwright
    - `data/` - CSV, JSON processing
    - `utility/` - Delay, random, hash functions
    - `file/` - File operations (read, write, exists)
    - `string/` - String processing (split, replace, regex)
    - `array/` - Array manipulation (filter, sort, unique)
    - `math/` - Mathematical operations
  - **third_party/** - External service integrations
    - `ai/` - OpenAI, Claude, Gemini
    - `communication/` - Slack, Discord, Telegram, Email
    - `database/` - PostgreSQL, MySQL, MongoDB
    - `cloud/` - AWS S3
    - `productivity/` - Notion, Google Sheets
    - `developer/` - GitHub, HTTP APIs
  - **composite/** - High-level workflow templates (v1.1)

- **integrations/** - Legacy integrations (being phased out)
  - Optional dependencies, install what you need
  - Being migrated to `modules/third_party/`

- **ui/web/backend/** - REST API for UI builders
  - Metadata API endpoints
  - FastAPI-based server

- **cli/** - Command-line interface
  - Workflow execution from terminal

### Brand Assets (`assets/`)
Visual assets for branding and documentation:
- `logo.svg` - Official Flyto2 logo (vector format)
- `architecture.svg` - System architecture diagram
- `README.md` - Asset specifications and usage guidelines

### Tests (`tests/`)
All test files in one place. Run with:
```bash
pytest tests/
```

### Scripts (`scripts/`)
Utility scripts for development and deployment:
- `start_api_server.py` - Launch the metadata API server

### Documentation (`docs/`)
Detailed technical documentation:
- **DSL.md** - Complete YAML workflow syntax reference
- **METADATA_API.md** - REST API endpoints
- **UI_BUILDER_INTEGRATION.md** - How to build UIs with the metadata API
- **ARCHITECTURE.md** - System design and third-party integrations

### Examples (`examples/`)
Configuration file examples and module reference:
- `engine.yaml` - Engine configuration template
- `NAMESPACES.yaml` - All available modules with descriptions

### Workflows (`workflows/`)
Ready-to-use workflow examples demonstrating various features.

## 📦 Installation Structure

```
Core:
  requirements.txt → Core engine dependencies

Development:
  requirements-dev.txt → pytest, linting, etc.

Integrations (optional):
  requirements-integrations.txt → AI services, databases, etc.
```

## 🚀 Quick Navigation

| What you need | Where to find it |
|---------------|------------------|
| Get started | README.md |
| Write workflows | docs/DSL.md, workflows/ |
| Add modules | CONTRIBUTING.md |
| API reference | docs/METADATA_API.md |
| Run tests | tests/ |
| Examples | workflows/, examples/ |

## 🔗 GitHub Integration

This structure follows GitHub best practices:
- ✅ Clean root directory (only essentials)
- ✅ Standard files in standard places (README, LICENSE, CONTRIBUTING)
- ✅ Clear separation: docs/, src/, tests/
- ✅ Git-friendly (each directory has a clear purpose)
- ✅ Easy to navigate and contribute to

## 📝 Notes

- **No compiled files in repo**: `__pycache__/`, `*.pyc` are gitignored
- **No secrets**: `.env`, `*.key` files are gitignored
- **Browser data excluded**: Playwright browser data not committed
- **Clean commits**: Organized structure makes diffs clearer

---

**Last updated**: 2025-11-30
**Repository**: https://github.com/flytohub/flyto2
