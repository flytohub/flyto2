# Flyto2

Deprecated legacy distribution shell for Flyto2.

Flyto2 is now organized across product-line repositories. This repository is
kept for legacy release/download metadata and security-policy routing only.

Current open-source entry points:

- [flyto-core](https://github.com/flytohub/flyto-core) — execution kernel,
  browser automation, MCP-native runtime, recipes, evidence, and replay.
- [flyto-indexer](https://github.com/flytohub/flyto-indexer) — code
  intelligence MCP for impact analysis, dependency graphs, and AI coding gates.
- [flyto-docs](https://github.com/flytohub/flyto-docs) — public technical
  documentation and citation surface.
- [flyto2.com](https://flyto2.com) — product site, downloads, pricing, and
  public route discovery.
- [AI workflow automation alternatives](https://blog.flyto2.com/posts/ai-workflow-automation-alternatives)
  — how Flyto2 compares with n8n, Zapier, Make, Playwright, and LangGraph.

## Status

- Repository status: deprecated
- Runtime status: no active runtime in this checkout
- Product authority: active Flyto2 repos, not this legacy shell

## Installation

No installation is required for this repository.

Historical desktop artifacts, if still published, are listed on the
[Releases](https://github.com/flytohub/flyto2/releases) page.

## Usage

Use this repo only to find legacy release links or security reporting
instructions. Do not start new product implementation work here.

Active work should move to the owning Flyto2 repository:

- `flyto-core` for execution kernel, automation runtime, crawler runtime, and
  connector primitives.
- `flyto-cloud` for Cloud / Apps / Automation, no-code workflows, app builder,
  templates, marketplace, and crawler apps.
- `flyto-code`, `flyto-engine`, and `flyto-ai` for Security product surfaces.
- `flyto-data` and future intelligence/company-agent repos for upcoming product
  lines.

## Download

Download the latest version for your platform from the [Releases](https://github.com/flytohub/flyto2/releases) page.

| Platform | File |
|----------|------|
| macOS (Apple Silicon) | `Flyto2_x.x.x_aarch64.dmg` |
| Windows | `Flyto2_x.x.x_x64-setup.exe` |
| Linux | `Flyto2_x.x.x_amd64.AppImage` |

## System Requirements

- **macOS**: 10.15+ (Apple Silicon)
- **Windows**: 10+
- **Linux**: Ubuntu 20.04+ or equivalent

## Architecture

This repository has no runtime architecture. See `ARCHITECTURE.md` for the
legacy-shell boundary and active repo routing.

## Testing

There is no app test suite in this repository. Verification is limited to:

- project memory completeness
- security policy presence
- secret scan cleanliness
- Flyto2 product-gate classification

## Links

- Website: [flyto2.com](https://flyto2.com)
- Documentation: [docs.flyto2.com](https://docs.flyto2.com)
