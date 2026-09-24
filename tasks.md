# Tasks

## Current

- [x] Define Flyto2 as the distribution authority rather than a product source repo.
- [x] Register Flyto2 Flow, Flyto2 Runtime, and Flyto2 Agent Firewall.
- [x] Add dedicated Markdown download pages and stable/beta channel files for each product.
- [x] Prohibit the repository-wide GitHub `/releases/latest` alias as a product updater contract.
- [x] Define independent namespaced SemVer tags.
- [x] Preserve historical root releases as Flyto2 Flow pre-rename lineage.
- [x] Define checksum, CycloneDX SBOM, provenance, and signing requirements.
- [x] Define a release-manifest schema.
- [x] Implement trusted candidate ingest from product repositories (`ingest-release.yml`).
- [x] Implement namespaced GitHub Release publication.
- [x] Implement stable/beta channel pointer promotion.
- [x] Align Flyto2 Runtime to emit the required candidate bundle.
- [ ] Align Flyto2 Flow and Flyto2 Agent Firewall to emit the candidate bundle.
- [ ] Move flyto2.com download discovery to distribution manifests.
- [ ] Add enterprise/offline mirror generation.

## Ongoing

- Keep SECURITY.md accurate.
- Keep signing secrets and binary installers out of Git history.
- Keep source ownership and product registry synchronized when products are added or renamed.
