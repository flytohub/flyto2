# Flyto2 Distribution Hub Handoff

- Date: 2026-09-24
- Owner: codex
- Branch: main
- Status: contract implemented locally; not committed or pushed in this handoff

## Decision

`flytohub/flyto2` is no longer treated as a deprecated legacy-only shell. It is now the Flyto2 distribution and release-governance authority.

Product source authority remains separate:

- `flyto-flow` → Flyto2 Flow
- `flyto-runtime` → Flyto2 Runtime
- `flyto-engine` → Flyto2 Agent Firewall

Historical root `v0.x` releases are preserved as the pre-rename Flyto2 Flow lineage.

## Implemented

- Rewrote README around the Distribution Hub model.
- Added `products/catalog.json`.
- Added dedicated product Markdown pages and per-product `stable.json` / `beta.json` channel files for Flow, Runtime, and Agent Firewall.
- Explicitly prohibited the repository-wide GitHub `/releases/latest` alias as a product updater/download contract.
- Added `release-policy.json`.
- Added `schemas/release-manifest.schema.json`.
- Added `docs/DISTRIBUTION.md`.
- Added `docs/SUPPLY_CHAIN.md`.
- Updated project memory, repository routing, workflows, and Agent rules.
- Updated local/CI verification from the legacy-shell contract to the distribution contract.
- Defined independent namespaces:
  - `flow/vX.Y.Z`
  - `runtime/vX.Y.Z`
  - `agent-firewall/vX.Y.Z`
- Defined required release evidence: exact source identity, build run, SHA-256 checksums, CycloneDX SBOM, provenance/attestation, release manifest, and native platform signing where supported.

## Still To Implement

- Trusted cross-repository candidate ingest workflow.
- Namespaced GitHub Release publisher.
- Stable/beta channel index publisher.
- Candidate-bundle alignment in Flow, Runtime, and Agent Firewall source repositories.
- Website/updater consumption of distribution manifests.
- Enterprise/offline mirror generation.

## Verification

Passed locally after the contract rewrite:

- `python3 scripts/verify.py`
- `git diff --check`
- JSON parsing for product catalog, release policy, release-manifest schema, and documentation manifest
- `flyto-index scan .`
- `flyto-index verify . --full-scan --strict --json`
  - 18 pass
  - 0 warn
  - 0 fail

No product runtime source, installer binary, credential, or signing key was added.
