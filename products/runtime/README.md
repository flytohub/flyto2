# Flyto2 Runtime

[← Back to Flyto2 Distribution Hub](../../README.md)

Flyto2 Runtime is the local execution layer for MCP hosts, AI Spaces, workspaces, local tools, and delegated agents.

## Downloads

<!-- downloads:start -->
No Runtime build has been promoted to the stable channel yet.
<!-- downloads:end -->

The macOS app includes everything it needs: its own Node.js, its dependencies,
and cloudflared. Nothing has to be installed first.

1. Download the disk image for your Mac: **Apple silicon** for M1 and later,
   **Intel** for older Macs (Apple menu → About This Mac shows which).
2. Open it and drag **Flyto2 Runtime** into **Applications**.
3. Open **Flyto2 Runtime** from Applications. The first launch walks you
   through setup in Terminal; later launches open the Runtime menu.

To check a download came from the Runtime source build, verify its attestation:

```bash
gh attestation verify Flyto2-Runtime-<version>-macos-arm64.dmg --repo flytohub/flyto-runtime
```

Installing from source instead: [flytohub/flyto-runtime](https://github.com/flytohub/flyto-runtime).

## How a Runtime release gets here

1. `flytohub/flyto-runtime` builds, signs and notarizes the app on both Mac
   architectures and assembles a candidate (disk images, CycloneDX SBOM,
   GitHub artifact attestations, `SHA256SUMS`, `release-manifest.json`) with
   its **macOS App** workflow, dispatched with `candidate: true`.
2. This repository's **Ingest release** workflow (`product=runtime`,
   `source_run_id=<that run>`) verifies every identity, digest, attestation and
   the notarization, then publishes `runtime/vX.Y.Z` and can move a channel.

## Release namespace

Future Distribution Hub releases use:

```text
runtime/vX.Y.Z
```

The product-specific stable and beta channel files below are the future machine-readable entry points. They intentionally do not point to a repository-wide `/releases/latest` URL.

## Distribution metadata

- [Product metadata](product.json)
- [Stable channel](stable.json)
- [Beta channel](beta.json)
- [Distribution architecture](../../docs/DISTRIBUTION.md)
- [Supply-chain policy](../../docs/SUPPLY_CHAIN.md)
