# 📚 Flyto2 Documentation

Complete documentation for the Flyto2 workflow automation engine.

---

## 🚀 Start Here

- [**Quick Start**](../QUICKSTART.md) - Get started in 5 minutes
- [**CLI Reference**](getting-started/CLI.md) - Complete CLI usage
- [**Module Registry**](modules/MODULES.md) - All 100+ available modules
- [**Module Development**](modules/WRITING_MODULES.md) - Create custom modules
- [**Contributing**](../CONTRIBUTING.md) - Contribution guidelines

---

## 📂 Advanced Documentation

Detailed references are organized in subdirectories:

### `getting-started/` - Complete References
- [CLI.md](getting-started/CLI.md) - Full CLI reference
- [DSL.md](getting-started/DSL.md) - Complete YAML syntax
- [PARAMETER_BEST_PRACTICES.md](getting-started/PARAMETER_BEST_PRACTICES.md) - Advanced patterns

### `modules/` - Module Development
- [MODULES.md](modules/MODULES.md) - Complete module registry (100+ modules)
- [MODULE_SPECIFICATION.md](modules/MODULE_SPECIFICATION.md) - Spec reference
- [WRITING_MODULES.md](modules/WRITING_MODULES.md) - Module development
- [MODULE_QUICK_REFERENCE.md](modules/MODULE_QUICK_REFERENCE.md) - Quick lookup
- [MODULE_CATEGORIES.md](modules/MODULE_CATEGORIES.md) - Category system
- [MODULE_PHASE2_FEATURES.md](modules/MODULE_PHASE2_FEATURES.md) - Advanced features
- [MODULE_QUALITY_SYSTEM.md](modules/MODULE_QUALITY_SYSTEM.md) - Quality tracking
- [DYNAMIC_MODULE_REGISTRY.md](modules/DYNAMIC_MODULE_REGISTRY.md) - Runtime registration

### `guides/` - Advanced Topics
- [META_WORKFLOWS.md](guides/META_WORKFLOWS.md) - Self-improving workflows
- [META_WORKFLOW_SAFETY.md](guides/META_WORKFLOW_SAFETY.md) - Safety protocols
- [UI_MODULE_INTEGRATION.md](guides/UI_MODULE_INTEGRATION.md) - UI integration
- [PHASE2_UI_INTEGRATION.md](guides/PHASE2_UI_INTEGRATION.md) - Advanced UI

### `architecture/` - System Design
- [PROJECT_STRUCTURE.md](architecture/PROJECT_STRUCTURE.md) - File organization
- [LEVEL_4_ARCHITECTURE.md](architecture/LEVEL_4_ARCHITECTURE.md) - Monitoring system
- [TELEGRAM_BOT_ARCHITECTURE.md](architecture/TELEGRAM_BOT_ARCHITECTURE.md) - Bot design

### `deployment/` - Production Setup
- [WINDOWS_SETUP.md](deployment/WINDOWS_SETUP.md) - Windows deployment
- [TELEGRAM_BOT_SETUP.md](deployment/TELEGRAM_BOT_SETUP.md) - Bot setup

---

## 🎯 Common Tasks

### Run a Workflow
```bash
python -m src.cli.main workflows/example.yaml --param keyword=python
```
→ [CLI Reference](getting-started/CLI.md)

### Create Custom Module
```python
@register_module(module_id='my.module', ...)
class MyModule(BaseModule): ...
```
→ [Writing Modules](modules/WRITING_MODULES.md)

### Find Module
Browse [Complete Registry](modules/MODULES.md)

### Deploy to Production
See [QUICKSTART.md](../QUICKSTART.md#windows-monitoring-setup)

---

## 💬 Support

- 🐛 [Report Issues](https://github.com/flytohub/flyto2/issues)
- 💬 [Discussions](https://github.com/flytohub/flyto2/discussions)
- 🤝 [Contributing](../CONTRIBUTING.md)

---

**Navigation**: [← Back to Main](../README.md)
