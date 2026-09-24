# Changelog

## Unreleased

### Added

- Reactivated the repository contract as the Flyto2 Distribution Hub.
- Added product registration for Flyto2 Flow, Flyto2 Runtime, and Flyto2 Agent Firewall.
- Added dedicated Markdown product/download pages plus per-product `stable.json` and `beta.json` channel entry points.
- Added independent product tag namespaces and stable/beta release-channel policy.
- Added `release-policy.json` for immutable versioning, required release evidence, signing, and artifact-storage rules.
- Added a machine-readable release manifest schema.
- Added distribution architecture and software-supply-chain documentation.
- Added CycloneDX SBOM, SHA-256 checksum, provenance/attestation, and native-signing requirements.

### Changed

- Reclassified historical `v0.x` desktop releases as the pre-rename Flyto2 Flow lineage without rewriting historical tags or assets.
- Changed repository authority from deprecated routing shell to release/distribution authority while keeping product source ownership in product-specific repositories.
- Updated repository verification to validate distribution metadata and preserve the no-runtime-source boundary.
