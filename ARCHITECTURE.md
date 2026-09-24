# Architecture

`flyto2` is a **distribution control plane**, not an application runtime.

## Authority Split

Product repositories are source authorities:

- `flyto-flow` — Flyto2 Flow;
- `flyto-runtime` — Flyto2 Runtime;
- `flyto-engine` — Flyto2 Agent Firewall source and security contracts.

This repository is the distribution authority for approved outputs from those repositories.

## Data Flow

```text
source repo
  └─ test/build/sign/SBOM/provenance
          │
          ▼
candidate release bundle
          │
          ▼
flyto2 distribution verification
  ├─ product registry
  ├─ source/commit verification
  ├─ checksum verification
  ├─ SBOM verification
  ├─ provenance/attestation verification
  ├─ native signing evidence check
  └─ immutable tag check
          │
          ▼
namespaced GitHub Release
          │
          ├─ website downloads
          ├─ application updaters
          ├─ enterprise deployment
          └─ offline mirror
```

## Repository Surfaces

- `products/catalog.json` — registered product identities and source ownership.
- `release-policy.json` — shared release evidence and immutability rules.
- `schemas/release-manifest.schema.json` — machine-readable release contract.
- `docs/DISTRIBUTION.md` — lifecycle, versioning, promotion, rollback, migration.
- `docs/SUPPLY_CHAIN.md` — SBOM, checksum, provenance, attestation, and signing policy.
- `scripts/verify.py` — local structural verification.
- GitHub workflows — verification and, when implemented, trusted ingest/promotion.

## Version Boundary

Each product has independent SemVer. Distribution tags are namespaced:

```text
flow/vX.Y.Z
runtime/vX.Y.Z
agent-firewall/vX.Y.Z
```

Historical root tags are immutable and remain available.

## Storage Boundary

Normal Git history contains metadata and policy only. Installer binaries belong in immutable release assets, approved artifact registries/CDNs, or controlled offline mirrors.

## Security Boundary

Do not add:

- product execution/runtime behavior;
- billing or entitlement decisions;
- RBAC/tenant policy engines;
- signing private keys;
- release credentials or personal access tokens;
- customer-specific offline licenses.

Cross-repository publication should use short-lived trusted identity such as GitHub OIDC/GitHub App or an equivalent protected release mechanism.

## Verification Boundary

The distribution verifier checks consistency and required release evidence. Product repositories remain responsible for product-specific tests, vulnerability policy, license policy, platform packaging, and native signing.
