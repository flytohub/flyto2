# Flyto2 Distribution Hub

Official release and software-supply-chain distribution repository for installable Flyto2 products.

This repository is the **distribution authority** for Flyto2. Product source code stays in the product repository that owns it; `flyto2` owns the release catalog, version namespace, release manifests, checksums, SBOM requirements, provenance requirements, signatures, channels, and historical download continuity.

## Products

| Product | Purpose | Source repository | Distribution tag namespace |
| --- | --- | --- | --- |
| [**Flyto2 Flow**](products/flow/README.md) | Visual workflow and self-hosted automation product. This is the renamed lineage of the historical Flyto2 desktop releases. | [flyto-flow](https://github.com/flytohub/flyto-flow) | `flow/vX.Y.Z` |
| [**Flyto2 Runtime**](products/runtime/README.md) | Local execution layer for MCP hosts, AI Spaces, workspaces, local tools, and delegated agents. | [flyto-runtime](https://github.com/flytohub/flyto-runtime) | `runtime/vX.Y.Z` |
| [**Flyto2 Agent Firewall**](products/agent-firewall/README.md) | Endpoint, MCP, browser, and enterprise connector suite for AI/agent activity enforcement and evidence. | [flyto-engine](https://github.com/flytohub/flyto-engine) | `agent-firewall/vX.Y.Z` |

New installable products must be added to [`products/catalog.json`](products/catalog.json) before they can be promoted through this repository.

## Downloads by product

Use the product page instead of the repository-wide GitHub `releases/latest` alias:

- [**Flyto2 Flow downloads**](products/flow/README.md#downloads) — includes the current historical v0.7.4 macOS, Windows, and Linux downloads.
- [**Flyto2 Runtime downloads**](products/runtime/README.md#downloads) — product-specific release channel; centralized promotion is not active yet.
- [**Flyto2 Agent Firewall downloads**](products/agent-firewall/README.md#downloads) — product-specific connector distribution; centralized promotion is not active yet.

Each product page links its own `stable.json` and `beta.json`. Consumers and updaters must resolve the product-specific channel, not whichever product happened to publish the newest GitHub Release.

## What belongs here

`flyto2` owns release distribution, not product implementation.

It may contain:

- product catalog and release-channel metadata;
- release policy and naming rules;
- release manifest schemas;
- verification and promotion automation;
- checksums, signatures, SBOM references, and provenance metadata;
- documentation for online, enterprise, and offline distribution;
- compatibility mapping for historical Flyto2 releases.

It must not contain:

- Flow, Runtime, Agent Firewall, or other product source code;
- business logic, billing, entitlement, tenant, or policy engines;
- credentials, signing private keys, customer data, or deployment secrets;
- mutable copies of binaries committed to Git history.

Binary installers belong in immutable GitHub Release assets or an approved artifact registry/CDN, never in normal Git commits.

## Versioning

Each product versions independently with SemVer.

```text
flow/v1.2.0
runtime/v0.9.3
agent-firewall/v1.0.1
```

A Runtime patch does not force Flow or Agent Firewall to change version.

Historical root tags such as `v0.7.4` are preserved exactly as published. They are the **pre-rename Flyto2 Flow lineage** and must not be deleted, retagged, or rewritten. New Flow releases use the `flow/` namespace.

Distribution channels are pointers, not separate versions:

- `stable` — production-approved release;
- `beta` — prerelease approved for broader testing.

Air-gapped or enterprise packaging is a delivery mode, not a SemVer fork.

## Required release evidence

A release is not eligible for `stable` promotion until its distribution bundle provides the evidence required by [`release-policy.json`](release-policy.json).

At minimum, a production release carries:

1. **Immutable source identity** — source repository, exact commit SHA, source tag, and build workflow/run.
2. **Installable artifacts** — platform/architecture-specific package names and SHA-256 digests.
3. **Checksums** — a canonical `SHA256SUMS` file.
4. **SBOM** — CycloneDX JSON is required for each releasable product bundle; SPDX may be published in addition.
5. **Provenance** — SLSA/in-toto-compatible build provenance or GitHub artifact attestation tied to the exact source commit and workflow.
6. **Signing evidence** — native platform signing where applicable plus artifact attestation/signature metadata.
7. **Release manifest** — one machine-readable manifest conforming to [`schemas/release-manifest.schema.json`](schemas/release-manifest.schema.json).

Platform signing and artifact attestation solve different problems. Apple notarization / Developer ID and Windows Authenticode establish platform trust; provenance and Sigstore/GitHub attestations establish how the artifact was built. Production releases should carry both where the platform supports native signing.

## Artifact naming

Use product, version, operating system, and architecture in the filename.

```text
Flyto2-Flow-1.2.0-macos-arm64.dmg
Flyto2-Flow-1.2.0-windows-x64.exe
Flyto2-Flow-1.2.0-linux-x64.AppImage

Flyto2-Runtime-0.9.3-macos-arm64.tar.gz
Flyto2-Runtime-0.9.3-windows-x64.zip
Flyto2-Runtime-0.9.3-linux-x64.tar.gz

Flyto2-Agent-Firewall-1.0.1-windows-x64.zip
Flyto2-Agent-Firewall-1.0.1-macos-arm64.tar.gz
Flyto2-Agent-Firewall-1.0.1-linux-arm64.tar.gz
```

Release metadata uses stable product identifiers: `flow`, `runtime`, and `agent-firewall`.

## Distribution model

The release path is intentionally one-way:

```text
product source repo
    │
    ├─ test / build
    ├─ native code signing
    ├─ generate SBOM
    ├─ generate checksum
    └─ generate provenance / attestation
            │
            ▼
flytohub/flyto2
    │
    ├─ verify product registration
    ├─ verify exact source commit and CI evidence
    ├─ verify artifact digest
    ├─ verify SBOM and provenance
    ├─ create namespaced GitHub Release
    └─ promote beta/stable channel pointer
            │
            ├─ GitHub Releases
            ├─ flyto2.com downloads
            ├─ application updaters
            └─ enterprise/offline mirror
```

The distribution repository must verify a product output; it must not silently rebuild a different source revision and call it the same release.

See [Distribution Architecture](docs/DISTRIBUTION.md) for the full promotion flow and [Supply Chain Policy](docs/SUPPLY_CHAIN.md) for SBOM, signing, provenance, and attestation requirements.

## Release manifest

Every promoted release has a machine-readable manifest. A simplified example:

```json
{
  "schema_version": 1,
  "product": "flow",
  "display_name": "Flyto2 Flow",
  "version": "1.2.0",
  "channel": "stable",
  "distribution_tag": "flow/v1.2.0",
  "source": {
    "repository": "flytohub/flyto-flow",
    "commit": "0123456789abcdef0123456789abcdef01234567",
    "tag": "v1.2.0"
  },
  "artifacts": [
    {
      "name": "Flyto2-Flow-1.2.0-macos-arm64.dmg",
      "platform": "macos",
      "arch": "arm64",
      "kind": "installer",
      "sha256": "..."
    }
  ],
  "sbom": {
    "format": "CycloneDX",
    "path": "flyto2-flow-1.2.0.cdx.json",
    "sha256": "..."
  },
  "provenance": {
    "type": "slsa",
    "path": "provenance.intoto.jsonl",
    "sha256": "..."
  }
}
```

The schema is intentionally product-neutral so future installers can join the same release system without inventing another updater contract.

## Repository layout

```text
flyto2/
├── products/
│   ├── catalog.json
│   ├── README.md
│   ├── flow/
│   │   ├── README.md
│   │   ├── product.json
│   │   ├── stable.json
│   │   └── beta.json
│   ├── runtime/
│   │   ├── README.md
│   │   ├── product.json
│   │   ├── stable.json
│   │   └── beta.json
│   └── agent-firewall/
│       ├── README.md
│       ├── product.json
│       ├── stable.json
│       └── beta.json
├── schemas/
│   └── release-manifest.schema.json
├── docs/
│   ├── DISTRIBUTION.md
│   ├── SUPPLY_CHAIN.md
│   └── LEGACY_ROUTING.md
├── scripts/
│   └── verify.py
├── release-policy.json
├── SECURITY.md
└── README.md
```

## Historical downloads

Existing GitHub Releases remain available for compatibility. The current historical `v0.x` desktop assets are treated as the pre-rename **Flyto2 Flow** lineage.

Do not infer current platform support from an old release. Historical artifacts retain the names, signatures, licenses, and compatibility information that shipped with that exact release.

For new product downloads, the long-term public entry point is [flyto2.com](https://flyto2.com), backed by verified distribution metadata from this repository.

## Security

Report vulnerabilities privately according to [SECURITY.md](SECURITY.md). Do not place signing keys, release credentials, customer-specific offline licenses, or private build evidence in this repository.

## Source ownership

Use the owning repository for implementation work:

- [flyto-flow](https://github.com/flytohub/flyto-flow) — Flyto2 Flow.
- [flyto-runtime](https://github.com/flytohub/flyto-runtime) — Flyto2 Runtime.
- [flyto-engine](https://github.com/flytohub/flyto-engine) — Agent Firewall backend/connectors and security product contracts.
- [flyto-core](https://github.com/flytohub/flyto-core) — shared execution kernel and automation primitives.
- [flyto-cloud](https://github.com/flytohub/flyto-cloud) — hosted Cloud product.
- [flyto-docs](https://github.com/flytohub/flyto-docs) — public technical documentation.

Changes to a product are made and tested in that product repository. Changes to how an approved product artifact is named, verified, attested, promoted, indexed, mirrored, or downloaded belong here.

## Status

The distribution contract and naming model are active. Historical releases are preserved in place. Product-by-product migration into namespaced releases is tracked in [ROADMAP.md](ROADMAP.md).
