# Candidate ingest, namespaced publication and channel promotion

- Date: 2026-09-24
- Owner: claude
- Branch: claude/runtime-distribution
- Status: implemented; first real ingest recorded below once run

## What changed

- `.github/workflows/ingest-release.yml` (`workflow_dispatch`: `product`,
  `source_run_id`, `promote` = none/beta/stable), on `macos-latest`:
  1. resolves the product in `products/catalog.json`;
  2. reads the source run and downloads its `*-candidate` artifact with this
     repository's own token (source repositories are public; probed on
     2026-09-24 before relying on it);
  3. resolves the manifest's source tag to a commit through the API;
  4. `scripts/ingest_release.py verify`: manifest schema, catalog identity,
     namespaced tag, channel vs. version, tag commit, run repository / id /
     workflow / commit / branch `main` / conclusion `success`, every digest and
     size, `SHA256SUMS` covering every file, CycloneDX SBOM with components,
     native signing evidence on installers;
  5. `gh attestation verify` on every installer against the shipped provenance
     and SBOM bundles, pinned to the source repository, its build workflow and
     the source commit, rejecting self-hosted runners;
  6. macOS: `stapler validate`, `spctl` on the disk image and on the app
     inside (`source=Notarized Developer ID`);
  7. publishes `<prefix>X.Y.Z` with `--latest=false` so the legacy Flow
     `/releases/latest` alias does not move; an existing tag is accepted only
     when its manifest is byte-identical;
  8. `promote` rewrites the channel JSON (and, for stable, the product page's
     downloads block) and pushes that commit to `main`.
- `scripts/verify.py` gains `verify_ingest()`; `documentation.yml` installs
  `jsonschema==4.23.0` for it.
- `products/runtime/README.md`: install steps, attestation check, generated
  downloads block.
- STATE, tasks, ROADMAP, CHANGELOG and DISTRIBUTION updated.

## Why

The Distribution Hub contract (codex, same day) left ingest, publication and
promotion unimplemented, so the notarized Runtime app had nowhere compliant to
go. Reading public candidates instead of pushing into this repository removes
the cross-repository credential the contract warned about.

## Verified

- `python3 scripts/verify.py`: contract, bundle, and ingest self-test
  (1 accepted, 5 refused: tag on another commit, failed build, non-main build,
  wrong product, swapped installer).
- `flyto-index verify . --full-scan --strict`.

## Not verified

- A real ingest run: requires this branch on `main` (workflow_dispatch only
  runs default-branch workflows) and a Runtime candidate run.

## Follow-ups

- Flow and Agent Firewall candidate bundles.
- flyto2.com and in-app updaters reading `products/<id>/<channel>.json`.
