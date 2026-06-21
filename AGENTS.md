# Agent Instructions

This repository is a deprecated Flyto2 legacy distribution shell.

Before making changes:

- Read `PROJECT.md`, `ARCHITECTURE.md`, `STATE.md`, and `DECISIONS.md`.
- Do not add product authority, entitlement logic, workflow runtime logic, or
  security scanning logic here.
- Keep this repo limited to legacy release/download metadata and compatibility
  notes.

Flyto2 product authority lives in:

- `flyto-core` for execution kernel and automation runtime primitives.
- `flyto-cloud` for Cloud / Apps / Automation product surfaces.
- `flyto-code`, `flyto-engine`, and `flyto-ai` for Security surfaces.
- Future `flyto-data`, company-agent, and big-data repos for their product
  lines.

Use `git -C /Users/chester/flytohub/flyto2 ...` for git operations.
