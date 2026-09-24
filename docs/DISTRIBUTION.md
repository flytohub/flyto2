# Distribution Architecture

## Purpose

`flytohub/flyto2` is the release-distribution authority for installable Flyto2 products. It does not own product source code.

The model separates two concerns:

- **source authority** — the repository that develops, tests, and owns a product;
- **distribution authority** — the repository that verifies, names, catalogs, promotes, and publishes approved artifacts.

This keeps Flow, Runtime, and Agent Firewall independently versioned while giving users, updaters, the website, and enterprise deployment systems one trusted release contract.

## Product ownership

| Product | Source authority | Distribution namespace |
| --- | --- | --- |
| Flyto2 Flow | `flytohub/flyto-flow` | `flow/vX.Y.Z` |
| Flyto2 Runtime | `flytohub/flyto-runtime` | `runtime/vX.Y.Z` |
| Flyto2 Agent Firewall | `flytohub/flyto-engine` | `agent-firewall/vX.Y.Z` |

The product catalog is an allowlist. Distribution automation must fail closed if a request names an unregistered product, unexpected source repository, or invalid tag namespace.

## Versioning

Products use independent SemVer.

A product source tag and distribution tag may use different namespaces, but both must resolve to the same immutable source commit recorded in the release manifest.

Example:

```text
source repo: flytohub/flyto-flow
source tag:  v1.2.0
source SHA:  abcdef...

distribution repo: flytohub/flyto2
distribution tag:  flow/v1.2.0
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

### 1. Build in the source repository

The owning product repository:

- checks out an exact commit;
- runs its product-specific test and release gates;
- builds target artifacts;
- performs native platform signing where applicable;
- generates SHA-256 checksums;
- generates the CycloneDX SBOM;
- emits provenance/attestation evidence;
- exports a candidate release manifest.

### 2. Ingest into the distribution repository

The distribution workflow receives only immutable candidate inputs and verifies:

- product id is registered;
- source repository matches the catalog;
- source tag resolves to the declared source commit;
- expected CI/release workflow succeeded;
- every artifact digest matches;
- required SBOM exists and is parseable;
- provenance identifies the declared source/build;
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

Machine-readable channel entry points:

```text
products/flow/stable.json
products/flow/beta.json

products/runtime/stable.json
products/runtime/beta.json

products/agent-firewall/stable.json
products/agent-firewall/beta.json
```

The repository-wide GitHub `/releases/latest` alias is **not** an authoritative product channel. A new Runtime release must not accidentally become the Flow updater target, and vice versa.

The public website should eventually expose equivalent product-specific routes such as:

```text
flyto2.com/downloads/flow
flyto2.com/downloads/runtime
flyto2.com/downloads/agent-firewall
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

### Phase 2 — source-repo candidate generation

Align each source repository to output a candidate bundle with identical release evidence fields. Keep product-specific build logic in the source repo.

### Phase 3 — central ingest and promotion

Add a `workflow_dispatch`/trusted cross-repository ingest workflow in `flyto2`. It verifies candidate evidence and creates the namespaced distribution release.

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
- own Agent Firewall enforcement policy;
- own Runtime execution behavior;
- own Flow workflow semantics;
- replace source-repository CI;
- store code-signing private keys.
