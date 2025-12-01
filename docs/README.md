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

## 📂 Detailed Documentation

### Getting Started
- [CLI.md](getting-started/CLI.md) - Complete CLI reference
- [DSL.md](getting-started/DSL.md) - YAML workflow syntax

### Module Development
- [MODULES.md](modules/MODULES.md) - Complete module registry (100+ modules)
- [MODULE_SPECIFICATION.md](modules/MODULE_SPECIFICATION.md) - Module specification
- [WRITING_MODULES.md](modules/WRITING_MODULES.md) - How to create modules

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
