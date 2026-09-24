# Flyto2 Distribution Hub

## Abstract

Flyto2 has multiple independently releasable products. A single source monorepo would blur ownership, while unrelated release pages would fragment user trust, updater logic, SBOM delivery, provenance, and enterprise distribution.

The `flytohub/flyto2` repository therefore acts as a distribution control plane: product repositories own source; this repository owns the contract that turns an approved build into an official Flyto2 release.

## Why Centralize Distribution

A shared distribution authority gives every product the same answers to operational questions:

- What is the current stable version?
- What exact source commit produced this installer?
- Which CI run built it?
- What is the SHA-256 digest?
- What dependencies shipped with it?
- What SBOM and provenance correspond to the artifact?
- Is the package natively signed?
- Which release should an updater or offline mirror consume?

Centralizing those answers does not require centralizing source code.

## Authority Model

Source authority remains product-specific:

- Flyto2 Flow: `flytohub/flyto-flow`;
- Flyto2 Runtime: `flytohub/flyto-runtime`;
- Flyto2 Agent Firewall: `flytohub/flyto-engine`.

Distribution authority lives here:

- product registration;
- release tag namespace;
- release manifest schema;
- checksum/SBOM/provenance/signing requirements;
- immutable public release identity;
- channel promotion;
- historical release continuity;
- website/updater/offline distribution metadata.

## Historical Continuity

The original Flyto2 desktop releases predate the Flyto2 Flow name. Their root `v0.x` tags remain immutable and form the historical Flow lineage.

The migration creates a clean future namespace without rewriting the past.

## Supply Chain Model

A production release is accepted only when the downloaded bytes can be tied to an exact source and trusted build through checksums, SBOM, provenance/attestation, and platform signing where applicable.

CycloneDX is the canonical distribution SBOM format. Artifact attestation and native code signing are complementary: one proves build origin, while the other participates in platform trust.

## Operational Model

Product repositories build candidates. The distribution layer verifies candidates and publishes immutable namespaced releases. Stable/beta indexes point to those immutable releases.

Enterprise and air-gapped mirrors consume the same evidence rather than inventing a separate package lineage.

## Non-Goals

The Distribution Hub does not become a product runtime, billing system, policy engine, or source-code monorepo. It does not keep signing private keys or customer credentials in Git.

## End State

The desired end state is one Flyto2 download and updater contract across all installable products, with independent product development and versioning underneath it.
