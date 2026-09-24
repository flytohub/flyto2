# State

## Current State

- Repository role changed from deprecated legacy shell to **Flyto2 Distribution Hub** on 2026-09-24.
- Distribution contract is defined for Flyto2 Flow, Flyto2 Runtime, and Flyto2 Agent Firewall.
- Historical root `v0.x` releases remain published and are classified as the pre-rename Flyto2 Flow lineage.
- Product source code remains outside this repository.
- No installer binaries are committed in the checkout.
- Product registry, product-specific Markdown download pages, stable/beta channel files, release policy, release-manifest schema, distribution architecture, and supply-chain policy are now repository-owned contracts.
- Existing historical releases have not yet been migrated or republished into namespaced tags.

## Migration Status

### Contract

- Product registry: defined.
- Independent version namespaces: defined.
- Stable/beta channels: defined per product, with dedicated Markdown entry points and channel JSON files.
- Release manifest schema: defined.
- CycloneDX SBOM requirement: defined.
- SHA-256 checksum requirement: defined.
- Provenance/attestation requirement: defined.
- Native platform signing boundary: defined.

### Ingest and promotion

- Candidate ingest, namespaced release publication and channel promotion:
  `.github/workflows/ingest-release.yml` + `scripts/ingest_release.py`
  (2026-09-24). No cross-repository credential: the public source repository's
  run and candidate artifact are read with this repository's own token.
- Runtime source-repo candidate bundle: emitted by `flyto-runtime`'s
  **macOS App** workflow with `candidate: true` (both Mac architectures,
  notarized, CycloneDX SBOM, build provenance and SBOM attestations,
  `SHA256SUMS`, `release-manifest.json`).
- `scripts/verify.py` exercises the ingest rules on a synthetic candidate
  (one accepted, five tampered variants refused) and a promotion on a copy.

### Still To Implement

- Flow source-repo candidate bundle alignment.
- Agent Firewall source-repo candidate bundle alignment.
- Windows Runtime installer (needs an Authenticode certificate decision).
- Website/updater consumption of distribution manifests.
- Enterprise/offline mirror generation.

## Release Blockers

A new stable release must not be promoted until the source repository, commit, build evidence, artifact digest, SBOM, and provenance satisfy `release-policy.json`.

Published historical tags and assets must not be rewritten during migration.

## Verification

Repository verification covers:

- required distribution files;
- registered product uniqueness and tag namespaces;
- release policy structure;
- release-manifest schema structure;
- source-ownership links and public documentation;
- prohibition on product source/package roots in this checkout;
- deterministic documentation/contract bundle;
- strict Flyto2 Indexer verification.
