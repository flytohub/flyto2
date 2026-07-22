# Flyto2 Legacy Distribution Whitepaper

## Abstract

The flyto2 repository is a deprecated distribution and routing shell. It
exists because historical links, releases, and security reports continue to
arrive after active implementation moved into product-specific repositories.
Its purpose is preservation and redirection, not product development.

## Why Preserve The Repository

Deleting a legacy repository breaks release URLs, external references, and
security-reporting paths. Leaving it unexplained invites contributors and
automation to treat obsolete metadata as current architecture. A bounded shell
preserves discoverability while making deprecation machine-readable and
human-readable.

## Authority Model

This checkout owns only legacy release discovery, security disclosure routing,
and repository-selection guidance. It exposes no API, CLI, package, MCP server,
runtime configuration, deployment, or active application. Historical artifacts
retain the license, compatibility, and checksum information shipped with their
specific release.

Active authority belongs to:

- flyto-core for execution, automation, recipes, and MCP runtime;
- flyto-indexer for code intelligence and verification;
- flyto-cloud for hosted product and application workflows;
- flyto-code, flyto-engine, and flyto-ai for security surfaces;
- flyto-docs, flyto-blog, and flyto-landing-page for public information.

## Safety And Maintenance

No credentials, runtime code, billing rules, entitlements, tenant policy, or
deployment logic should be added here. Security reports continue through
private GitHub reporting or security@flyto2.com so users following old links
still reach a maintained channel.

## Verification

The repository gate checks required routing and security documents, Markdown,
local links, deterministic documentation packaging, brand/contact policy, and
strict Flyto2 Indexer classification. There is intentionally no application
build or release publisher.

## End State

The repository remains deprecated until historical traffic and release
retention no longer require it. Any reactivation would require a new project
charter, architecture, ownership, tests, release process, and explicit
migration decision; legacy presence alone is not authorization to restart
product development.

