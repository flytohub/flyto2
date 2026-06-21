# Architecture

This repository has no runtime architecture.

It contains:

- `README.md` for legacy download and link metadata.
- `SECURITY.md` for vulnerability disclosure policy.
- Project memory files that explain why the repo is deprecated.

## Boundaries

Do not add:

- workflow execution runtime
- connector protocol code
- crawler or browser automation runtime
- billing, entitlement, or capability decisions
- RBAC, tenant isolation, audit log, or evidence authority
- SaaS provider integrations
- enterprise airgap deployment logic

Those responsibilities belong to active Flyto2 repos, especially `flyto-core`,
`flyto-cloud`, `flyto-code`, `flyto-engine`, and `flyto-ai`.
