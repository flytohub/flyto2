# Decisions

## 2026-09-24 - Reactivate flyto2 as the Flyto2 Distribution Hub

Decision: `flytohub/flyto2` is the official distribution authority for installable Flyto2 products, while product source authority remains in product-specific repositories.

Reason: Flyto2 now has multiple independently releasable products. A shared distribution contract provides one trusted place for version namespaces, release manifests, checksums, SBOM, provenance, signatures, channels, historical continuity, and download discovery without recreating a monorepo.

Current registered products are Flyto2 Flow, Flyto2 Runtime, and Flyto2 Agent Firewall.

This decision supersedes the 2026-06-21 deprecated-shell classification for current repository purpose.

## 2026-09-24 - Product versions remain independent

Decision: use namespaced distribution tags such as `flow/vX.Y.Z`, `runtime/vX.Y.Z`, and `agent-firewall/vX.Y.Z`.

Reason: a patch to one product must not force synchronized version changes across unrelated products.

## 2026-09-24 - Preserve historical releases as Flow lineage

Decision: existing root `v0.x` Flyto2 desktop releases remain immutable and are documented as the pre-rename Flyto2 Flow lineage.

Reason: rewriting tags or assets would break historical links and destroy release auditability.

## 2026-09-24 - Release evidence is mandatory

Decision: stable/beta promotion requires exact source identity, SHA-256 checksums, CycloneDX SBOM, build provenance/attestation, release manifest, and native platform signing evidence where supported.

Reason: distribution must establish what was built, from which source, by which build, with which dependency inventory, and whether the downloaded bytes are the approved bytes.

## 2026-09-24 - Binary artifacts are release assets, not Git content

Decision: installer binaries and mutable build outputs are not committed to normal Git history.

Reason: Git stores the distribution contract and metadata; immutable release assets, registries/CDNs, and controlled offline mirrors store distributable binaries.

## 2026-08-14 - Legacy routing changes used the governed coding route

Historical decision: the former legacy shell kept a local verifier and strict Indexer validation.

Status: superseded in purpose, retained as provenance. The verifier is now being evolved into the distribution-contract verifier.

## 2026-06-21 - Keep flyto2 as deprecated legacy shell

Historical decision: the repository was classified as deprecated and non-authoritative.

Status: **superseded by the 2026-09-24 distribution-hub decision**. The source-code boundary remains: `flyto2` is distribution authority, not product implementation authority.
