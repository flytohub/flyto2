# Software Supply Chain Policy

## Goal

Every Flyto2 production installer should be traceable from the downloaded bytes back to the exact source repository, source commit, build workflow, dependency inventory, and release decision.

The required evidence is part of the release, not optional documentation.

## Required controls

### Checksums

Every distributed file must have a SHA-256 digest recorded in both the canonical checksum file and release manifest.

The checksum file itself must be included in release evidence.

### SBOM

CycloneDX JSON is the required canonical SBOM format for Flyto2 distribution.

Generate the SBOM from the final release candidate or the closest ecosystem-supported final-package view, not only from a developer lockfile. It should describe the dependencies that can materially ship with or execute as part of the delivered product.

SPDX may be published in addition where useful to customers or compliance tooling.

A stable release is blocked when the required SBOM is missing.

### Provenance

A production release must carry build provenance or an artifact attestation that binds at least:

- source repository;
- exact source commit;
- build workflow identity;
- build run identity;
- subject artifact digest.

SLSA/in-toto-compatible provenance and GitHub artifact attestations are acceptable mechanisms when they preserve those properties.

### Artifact attestation

Prefer keyless OIDC-backed attestations for CI-generated artifacts so long-lived signing secrets are not required for provenance.

Attestation is not a substitute for native platform code signing.

### Native platform signing

Where a platform has a native trust system, release packaging should use it:

- macOS: Developer ID signing and notarization for distributable desktop installers/apps;
- Windows: Authenticode signing for executable installers and other supported binaries;
- Linux: detached signature/attestation and verified package or image digest as appropriate to the delivery format.

The release manifest records the existence or reference for native signing evidence.

### OCI/container releases

Container images should be distributed by immutable digest. Generate SBOM and provenance attestations for the published image and record the image digest in the release metadata.

Tags are convenience aliases; the digest is the immutable identity.

## Evidence relationship

For one release, the trust graph should be:

```text
source repository + commit
          │
          ▼
trusted CI workflow/run
          │
          ├──────────────► provenance / attestation
          │
          ▼
final artifact ──────────► SHA-256
          │
          ├──────────────► native platform signature
          │
          └──────────────► SBOM
                              │
                              ▼
                     release-manifest.json
                              │
                              ▼
                   immutable distribution tag
```

A release should be rejected if these identities disagree.

## Secret handling

Never commit:

- Apple signing certificates/private keys;
- Windows code-signing private keys;
- Sigstore private keys when keyless signing is available;
- GitHub personal access tokens;
- customer offline licenses;
- registry credentials.

Use GitHub environments, OIDC, GitHub Apps, platform signing services, hardware-backed keys, or equivalent protected secret stores.

## Dependency and vulnerability policy

An SBOM is inventory, not a vulnerability verdict.

Product source repositories remain responsible for their own dependency, vulnerability, license, and release-blocking policies. The distribution repository verifies that required evidence exists and corresponds to the artifact; it does not silently override a product-specific risk decision.

## Reproducibility

Where reproducible builds are practical, record reproducibility evidence. Reproducibility is desirable but not required to establish the first distribution contract.

Immutability is required: once a public distribution tag and artifact digest are published, rebuilding different bytes under that identity is prohibited.

## Offline and air-gapped delivery

An offline mirror must include the original:

- artifact;
- release manifest;
- SHA-256 checksum;
- SBOM;
- provenance/attestation evidence that can be verified offline when supported;
- native signature metadata;
- mirror index.

Mirroring must not repackage the artifact in a way that changes its digest unless the repackaged object is treated as a new explicitly identified artifact with its own evidence.
