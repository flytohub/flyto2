# 2026-06-21 Legacy Shell Memory

## Summary

Added project memory for the deprecated `flyto2` legacy shell so future agents
do not confuse it with the active Flyto2 product system.

## Boundaries

- Keep this repo to README, SECURITY, release/download, and archive metadata.
- Do not implement product runtime, entitlement, security backend, workflow
  engine, or enterprise deployment here.
- Route active product work to the owning Flyto2 repo.

## Verification

- Product gate should no longer report `memory_incomplete` for `flyto2`.
