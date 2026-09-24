# Supported Distribution Surfaces

## Product Registry

`products/catalog.json` is the allowlist for products that may be distributed through this repository. It binds each stable product id to one source repository and one distribution tag namespace.

Current products are Flyto2 Flow, Flyto2 Runtime, and Flyto2 Agent Firewall.

## Independent Version Namespaces

Each product uses independent SemVer and a namespaced distribution tag:

- `flow/vX.Y.Z`;
- `runtime/vX.Y.Z`;
- `agent-firewall/vX.Y.Z`.

Historical root tags remain immutable and are treated as the pre-rename Flow lineage.

## Release Manifest Contract

`schemas/release-manifest.schema.json` defines a product-neutral contract for release identity, source commit, build run, artifact digests, SBOM, and provenance.

The goal is one machine-readable contract for website downloads, updaters, enterprise deployment, and offline mirrors.

## Supply Chain Evidence

`release-policy.json` and `docs/SUPPLY_CHAIN.md` require production release evidence including:

- exact source repository/tag/commit;
- build workflow/run identity;
- SHA-256 checksums;
- CycloneDX SBOM;
- provenance or artifact attestation;
- native platform signing evidence where supported.

## Distribution Promotion

A release is built by its source repository, verified by the distribution layer, published under a namespaced tag, and then promoted through a channel pointer such as `beta` or `stable`.

Promotion changes the pointer, not the underlying artifact.

## Historical Release Continuity

Existing GitHub Releases remain available. Old release URLs are not rewritten merely to fit the new naming model.

## Security Disclosure Routing

`SECURITY.md` remains the private vulnerability disclosure entry point for Flyto2 distribution and historical artifacts.

## Verification Contract

Repository CI verifies the distribution contract, product registry, release policy, release-manifest schema, public links, deterministic metadata bundle, and the boundary that prevents product runtime source from being added here.
