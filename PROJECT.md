# Project

`flyto2` is the official Flyto2 distribution and release-governance repository.

It is **not** a product source monorepo. Product source authority stays with the repository that owns each product, while this repository owns the shared release namespace, distribution metadata, release evidence requirements, channel promotion contract, and historical download continuity.

## Distribution Scope

Current registered installable products:

- **Flyto2 Flow** — source: `flytohub/flyto-flow`; distribution tags: `flow/vX.Y.Z`.
- **Flyto2 Runtime** — source: `flytohub/flyto-runtime`; distribution tags: `runtime/vX.Y.Z`.
- **Flyto2 Agent Firewall** — source: `flytohub/flyto-engine`; distribution tags: `agent-firewall/vX.Y.Z`.

Historical root `v0.x` releases are preserved as the pre-rename Flyto2 Flow lineage.

## Role

This repository may own:

- product registration and immutable identity;
- version/tag namespace rules;
- release manifest schemas;
- release verification and promotion automation;
- checksums, SBOM policy, provenance/attestation policy, and signature metadata;
- channel pointers for stable/beta distribution;
- download/index metadata for website, updaters, enterprise, and offline mirrors.

This repository must not own:

- product runtime/business logic;
- billing, entitlements, tenant state, or security enforcement decisions;
- product source trees;
- code-signing private keys, customer licenses, credentials, or secrets;
- binary installers committed to normal Git history.

## Success Criteria

A production release should be able to answer, machine-readably:

1. what product and version is this;
2. what exact source repository, source tag, and commit produced it;
3. what CI workflow/run built it;
4. what artifact digest was published;
5. what SBOM describes it;
6. what provenance/attestation binds it to the build;
7. what signing evidence applies;
8. which channel currently points to it.
