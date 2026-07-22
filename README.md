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

## API

This repository exposes no API, command-line interface, package, MCP server, or
runtime contract. Use the API and CLI references in the active owning
repository; do not infer current endpoints from historical release artifacts.

## Configuration

There are no runtime settings, environment variables, credentials, or deploy
profiles in this checkout. Current configuration belongs to the active product
repository and [docs.flyto2.com](https://docs.flyto2.com).

## Historical Downloads

The [Releases](https://github.com/flytohub/flyto2/releases) page is the only
authority for artifacts that were actually published. Filenames, supported
platforms, signatures, and requirements vary by release; this deprecated
repository does not promise a current desktop build or compatibility level.

Verify checksums and release notes before running a historical artifact. For
current installation paths, start at [docs.flyto2.com](https://docs.flyto2.com).

## Architecture

This repository has no runtime architecture. See `ARCHITECTURE.md` for the
legacy-shell boundary and active repo routing.

## Documentation

- [Legacy routing guide](docs/LEGACY_ROUTING.md)
- [Supported repository surfaces](docs/FEATURES.md)
- [Security policy](SECURITY.md)

## Testing

There is no app test suite in this repository. Verification is limited to:

- project memory completeness
- security policy presence
- secret scan cleanliness
- Flyto2 product-gate classification

The repository workflow also runs explicit Markdown lint, local documentation
tests, a deterministic documentation bundle build, and strict Flyto2 Indexer
verification.

## Contributing

Changes are limited to correcting legacy links, release metadata, security
routing, and deprecation documentation. Open product features against the
active repository listed in [the routing guide](docs/LEGACY_ROUTING.md).

## License

Historical release artifacts retain the license and notices shipped with their
specific release. This legacy documentation checkout does not override those
terms or grant rights to code maintained in another Flyto2 repository.

## Links

- Website: [flyto2.com](https://flyto2.com)
- Documentation: [docs.flyto2.com](https://docs.flyto2.com)
