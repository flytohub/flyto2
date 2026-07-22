# State

## Current State

- Deprecated legacy distribution shell.
- Contains README download pointers and security disclosure policy.
- No source code, package manifest, app runtime, release pipeline, or deployable
  artifact is present in this checkout.
- Documentation CI verifies the retired-repository contract; it does not build
  or publish a product release.

## Release Blockers

- This repo must not be treated as production product authority.
- Any active Flyto2 product implementation should happen in the appropriate
  active repo.

## Verification

For this repo, verification is limited to:

- project memory completeness
- security policy presence
- internal route and document presence
- deterministic documentation bundle creation
- strict Flyto2 Indexer verification
