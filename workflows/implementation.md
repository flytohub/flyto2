# Implementation

Allowed implementation scope includes:

- product registry and distribution identity;
- release policy and manifest schemas;
- checksum/SBOM/provenance/signing verification;
- trusted release ingest and promotion automation;
- stable/beta channel metadata;
- website/updater distribution indexes;
- historical release/download compatibility;
- enterprise/offline mirror metadata;
- README, SECURITY, project memory, and distribution documentation.

Do not add product runtime code, billing/entitlement logic, security-enforcement business logic, or signing private keys here.

Binary installers must remain release assets or registry/CDN objects rather than normal Git content.
