# Planning

Planning rule: keep this repository focused on **distribution authority**, not product implementation.

A change belongs here when it affects:

- product registration;
- distribution tag/version namespace;
- release manifests or channel indexes;
- release verification/promotion;
- checksums, SBOM, provenance, attestation, or signature metadata;
- download discovery;
- enterprise/offline release mirroring;
- historical release continuity.

A change belongs in the product source repository when it changes runtime behavior, UI, business logic, billing, entitlement, security enforcement, or product-specific packaging implementation.

Before adding a new distribution surface, define its machine-readable contract and failure behavior. Release verification should fail closed on identity or digest mismatch.
