# Wrap-up

Before finishing work here:

- Confirm no product runtime source, credentials, signing private keys, or installer binaries were added to Git history.
- Confirm product ids, source repositories, and tag namespaces remain consistent.
- Run `python3 scripts/verify.py`.
- Run `flyto-index verify . --full-scan --strict`.
- Inspect `git diff --check` and the final diff.
- Update `CHANGELOG.md` for user/operator-visible changes.
- Add or update a handoff entry when distribution ownership or release contracts change.
