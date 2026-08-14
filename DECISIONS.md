# Decisions

## 2026-08-14 - Legacy routing changes use the governed coding route

Decision: keep the local legacy contract, deterministic documentation bundle,
patch hygiene, and strict Indexer verification in `.flyto/coding.yaml`.

Reason: this repository must remain useful to old visitors without regaining
product authority. A committed verifier makes that deprecation boundary
testable before any public copy change lands.

## 2026-06-21 - Keep flyto2 as deprecated legacy shell

Decision: keep this repository classified as deprecated and do not place active
Flyto2 product authority here.

Reason: Flyto2 is now organized across product-line repositories with
`flyto-core` as the shared execution kernel. Reusing this repo as a product root
would blur ownership and conflict with the five-line product model.
