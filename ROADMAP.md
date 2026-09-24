# Roadmap

## Now — Distribution Contract

- Keep Flyto2 Flow, Runtime, and Agent Firewall source ownership separate.
- Preserve historical `v0.x` releases as the pre-rename Flow lineage.
- Enforce product registry, product-specific Markdown/download entry points, stable/beta channel files, namespaced versions, release evidence, and immutable published tags.
- Keep binary installers out of Git history.

## Now — Candidate Ingest

- Done for Flyto2 Runtime: `ingest-release.yml` verifies source commit, CI run, checksums, CycloneDX SBOM, provenance, and signing evidence, and creates namespaced GitHub Releases.
- Next: Flyto2 Flow and Flyto2 Agent Firewall emit the same candidate bundle.

## Next — Channel Distribution

- Publish machine-readable `stable` and `beta` channel indexes.
- Point flyto2.com downloads at verified distribution metadata.
- Move application/CLI updaters away from hard-coded release filenames.

## Later — Enterprise / Offline

- Generate offline mirror indexes from immutable release manifests.
- Preserve digests, SBOM, provenance, and native signatures in air-gapped delivery.
- Add retention and LTS policy only when product support policy requires it.

## Not Planned

- Product runtime source code.
- Billing or entitlement logic.
- Security enforcement/business logic.
- Mutable replacement of published release assets.
- Long-lived release credentials stored in this repository.
