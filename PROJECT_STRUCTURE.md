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
│   └── PROJECT_STRUCTURE.md     # This file
│
├── 📦 Installation
│   ├── setup.py                 # Package setup
│   ├── requirements.txt         # Core dependencies
│   ├── requirements-dev.txt     # Development dependencies
│   └── requirements-integrations.txt  # Optional integrations
│
├── 📖 docs/                     # Detailed Documentation
│   ├── DSL.md                   # YAML workflow syntax
│   ├── ARCHITECTURE.md          # System architecture
│   ├── METADATA_API.md          # REST API reference
│   └── UI_BUILDER_INTEGRATION.md  # UI integration guide
│
├── 💻 src/                      # Source Code
│   ├── core/                    # Core workflow engine
│   │   ├── engine/              # Workflow execution engine
│   │   │   ├── variable_resolver.py
│   │   │   └── workflow_engine.py
│   │   ├── modules/             # Module system
│   │   │   ├── registry.py      # Module registry
│   │   │   ├── base.py          # Base module class
│   │   │   ├── browser_modules.py
│   │   │   ├── api_modules.py
│   │   │   └── atomic/          # Atomic modules
│   │   └── browser/             # Browser automation
│   │       └── driver.py        # Playwright driver
│   │
│   ├── integrations/            # Third-party integrations (optional)
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
│   ├── google_search.yaml       # Google search example
│   └── test_simple.yaml         # Simple test workflow
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
  - `modules/` - All workflow modules (browser, API, AI, etc.)
  - `browser/` - Playwright browser automation driver

- **integrations/** - Third-party service integrations
  - Optional dependencies, install what you need
  - Example: OpenAI, Anthropic, Gemini

- **ui/web/backend/** - REST API for UI builders
  - Metadata API endpoints
  - FastAPI-based server

- **cli/** - Command-line interface
  - Workflow execution from terminal

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

**Last updated**: 2024-11-29
**Repository**: https://github.com/flytohub/flyto2
