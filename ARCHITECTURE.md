# Architecture

`flyto2` is a **distribution control plane**, not an application runtime.

## Authority Split

Product implementation stays in the source authority that owns each product. This public repository intentionally does **not** publish private/internal source-repository names or URLs.

This repository is the distribution authority for approved outputs from those source authorities.

## Data Flow

```text
source authority
  └─ test/build/sign/SBOM/provenance
          │
          ▼
candidate release bundle
          │
          ▼
flyto2 distribution verification
  ├─ product registry
  ├─ trusted source-authority verification
  ├─ source-revision verification
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

- `products/catalog.json` — registered public product identities and distribution namespaces.
- `release-policy.json` — shared release evidence and immutability rules.
- `schemas/release-manifest.schema.json` — machine-readable public release contract.
- `docs/DISTRIBUTION.md` — lifecycle, versioning, promotion, rollback, migration.
- `docs/SUPPLY_CHAIN.md` — SBOM, checksum, provenance, attestation, and signing policy.
- `scripts/verify.py` — local structural verification.
- GitHub workflows — verification and trusted ingest/promotion.

## Version Boundary

Each product has independent SemVer. Distribution tags are namespaced:

```text
flow/vX.Y.Z
runtime/vX.Y.Z
agent-firewall/vX.Y.Z
voice/vX.Y.Z
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
- customer-specific offline licenses;
- private/internal repository names or URLs.

Trusted cross-repository publication should use private CI configuration and short-lived trusted identity such as GitHub OIDC/GitHub App or an equivalent protected release mechanism.

## Verification Boundary

The public distribution verifier checks product identity, public release metadata, consistency, and required release evidence. Private source-authority allowlists belong in CI configuration/secrets and are not committed here.
