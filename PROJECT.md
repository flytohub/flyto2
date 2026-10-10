# Project

`flyto2` is the official Flyto2 distribution and release-governance repository.

It is **not** a product source monorepo. Product implementation remains in its owning source authority, while this repository owns the shared release namespace, distribution metadata, release evidence requirements, channel promotion contract, and historical download continuity.

## Distribution Scope

Current registered installable products:

- **Flyto2 Flow** — distribution tags: `flow/vX.Y.Z`.
- **Flyto2 Runtime** — distribution tags: `runtime/vX.Y.Z`.
- **Flyto2 Agent Firewall** — distribution tags: `agent-firewall/vX.Y.Z`.
- **Flyto2 Voice** — distribution tags: `voice/vX.Y.Z`.

Historical root `v0.x` releases are preserved as the pre-rename Flyto2 Flow lineage.

## Public Source Privacy

This public repository does not publish names or URLs of private/internal implementation repositories. Source ownership is verified by trusted CI configuration outside the committed public catalog.

## Role

This repository may own:

- product registration and immutable public identity;
- version/tag namespace rules;
- release manifest schemas;
- release verification and promotion automation;
- checksums, SBOM policy, provenance/attestation policy, and signature metadata;
- channel pointers for stable/beta distribution;
- download/index metadata for website, updaters, enterprise, and offline mirrors.

This repository must not own:

- product runtime/business logic;
- billing, entitlements, tenant state, or security enforcement decisions;
- product source trees;
- code-signing private keys, customer licenses, credentials, or secrets;
- binary installers committed to normal Git history;
- private/internal source-repository identifiers in public metadata.

## Success Criteria

A production release should be able to answer, machine-readably:

1. what product and version is this;
2. what immutable source revision produced it, without disclosing private repository identity;
3. what CI workflow/run approved it;
4. what artifact digest was published;
5. what SBOM describes it;
6. what provenance/attestation binds it to the build;
7. what signing evidence applies;
8. which channel currently points to it.
