# Bugfix

Use this workflow for distribution-contract bugs:

1. Confirm the issue belongs to release metadata, product registration, verification, promotion, channel indexes, historical release continuity, or download routing.
2. Preserve published tag/artifact immutability.
3. Make the smallest contract or automation fix.
4. Run `python3 scripts/verify.py` and strict Indexer verification.
5. Record user/operator-visible changes in `CHANGELOG.md`.

If the bug changes product behavior or product-specific packaging implementation, move it to the owning source repository.
