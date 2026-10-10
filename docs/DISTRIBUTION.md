# Distribution Architecture

## Purpose

`flytohub/flyto2` is the release-distribution authority for installable Flyto2 products. It does not own product source code.

The model separates two concerns:

- **source authority** — the implementation/build authority for a product;
- **distribution authority** — the public repository that verifies, names, catalogs, promotes, and publishes approved artifacts.

Private or internal source-authority repository names are deliberately not committed to this public repository.

## Product distribution identities

| Product | Distribution namespace |
| --- | --- |
| Flyto2 Flow | `flow/vX.Y.Z` |
| Flyto2 Runtime | `runtime/vX.Y.Z` |
| Flyto2 Agent Firewall | `agent-firewall/vX.Y.Z` |
| Flyto2 Voice | `voice/vX.Y.Z` |

The public product catalog is an allowlist of distribution identities, not a directory of private implementation repositories.

## Versioning

Products use independent SemVer.

A source tag/revision and distribution tag must refer to the same approved build, but the public manifest does not need to disclose a private repository name.

Example:

```text
source tag:        v1.2.0
source revision:   abcdef...
distribution tag: flow/v1.2.0
```

Published distribution tags are immutable. A bad release is superseded by a new version; it is not rebuilt under the same public tag.

## Historical Flyto2 releases

The existing root `v0.x` releases are preserved. They are the pre-rename lineage of Flyto2 Flow.

Migration rules:

1. never delete or rewrite historical tags solely to match the new naming model;
2. never replace an old asset under the same historical tag;
3. document the lineage in the product registry and README;
4. all new Flow releases use `flow/vX.Y.Z`;
5. website and updater migrations may map legacy versions to the Flow product id without mutating historical artifacts.

## Release lifecycle

### 1. Build in the source authority

The owning implementation/build authority:

- checks out an exact revision;
- runs product-specific test and release gates;
- builds target artifacts;
- performs native platform signing where applicable;
- generates SHA-256 checksums;
- generates the CycloneDX SBOM;
- emits provenance/attestation evidence;
- exports a candidate release manifest.

### 2. Ingest into the distribution repository

The distribution workflow receives only immutable candidate inputs and verifies:

- product id is registered;
- trusted source authority is authorized by private CI configuration;
- source tag/revision matches the candidate evidence;
- expected CI/release workflow succeeded;
- every artifact digest matches;
- required SBOM exists and is parseable;
- provenance identifies the approved revision/build;
- native signing evidence exists where the target requires it;
- the target distribution tag is unused or refers to the exact same immutable release.

A mismatch blocks publication.

### 3. Publish a namespaced GitHub Release

The accepted release is published under its product namespace. Binary artifacts remain release assets; they are not committed to Git history.

The release should contain the installable artifacts and their distribution evidence, including:

```text
release-manifest.json
SHA256SUMS
<product>-<version>.cdx.json
provenance.intoto.jsonl
<platform installers / archives>
<optional native signature or detached signature files>
```

### 4. Promote a channel pointer

After verification, the release may be promoted to `beta` or `stable`.

A channel is a mutable pointer to an immutable release. Promotion changes the pointer; it does not rebuild the artifact.

Consumers should resolve product + channel to a release manifest and then verify the selected artifact digest.

## Product-specific entry points

Distribution is centralized, but user-facing entry points are product-specific.

Repository Markdown entry points:

- [Flyto2 Flow](../products/flow/README.md)
- [Flyto2 Runtime](../products/runtime/README.md)
- [Flyto2 Agent Firewall](../products/agent-firewall/README.md)
- [Flyto2 Voice](../products/voice/README.md)

Machine-readable channel entry points:

```text
products/flow/stable.json
products/flow/beta.json

products/runtime/stable.json
products/runtime/beta.json

products/agent-firewall/stable.json
products/agent-firewall/beta.json

products/voice/stable.json
products/voice/beta.json
```

The repository-wide GitHub `/releases/latest` alias is **not** an authoritative product channel.

The public website should eventually expose equivalent product-specific routes such as:

```text
flyto2.com/downloads/flow
flyto2.com/downloads/runtime
flyto2.com/downloads/agent-firewall
flyto2.com/downloads/voice
```

## Consumer model

The same product-specific metadata can serve:

- product download pages;
- in-product auto-updaters;
- CLI bootstrap installers;
- MDM/Intune/GPO deployment;
- enterprise package mirrors;
- air-gapped update bundles;
- support and incident-response tooling.

Consumers should never scrape human-readable release notes or the global GitHub latest-release alias to discover filenames or versions.

## Recommended automation phases

### Phase 1 — contract

Maintain the product registry, release policy, schema, verifier, README, and historical mapping in this repository.

### Phase 2 — source candidate generation

Each source authority outputs a candidate bundle with identical public release-evidence fields. Product-specific build logic stays with the source authority.

### Phase 3 — central ingest and promotion

Add a trusted cross-repository ingest workflow in `flyto2`. Private source-authority mappings live in protected CI configuration, not public Git.

Use GitHub OIDC/GitHub App or another short-lived trusted mechanism for cross-repository release authorization. Do not store a reusable personal token in product source.

### Phase 4 — public channel indexes

Publish signed or attested channel manifests for `stable` and `beta`. Point the website and updaters at those indexes.

### Phase 5 — enterprise/offline mirror

Generate an offline mirror index from the same immutable manifests and artifacts. Air-gapped delivery must preserve original digests, SBOM, provenance, and signatures.

## Rollback

Rollback is channel movement, not artifact mutation.

If `flow/v1.2.1` is bad and `flow/v1.2.0` is still supported, the stable pointer may move back to `flow/v1.2.0`. The bad tag and artifacts stay immutable for auditability.

## Non-goals

The distribution repository does not:

- compile product source as the primary owner;
- own billing or entitlement decisions;
- own security enforcement policy;
- own runtime execution behavior;
- own Flow workflow semantics;
- replace source-authority CI;
- store code-signing private keys;
- disclose private/internal source-repository identities.
