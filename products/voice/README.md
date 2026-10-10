# Flyto2 Voice

[← Back to Flyto2 Distribution Hub](../../README.md)

Flyto2 Voice is the independent always-listening voice daemon for wake phrases,
speech input, and routing recognized commands to configured applications or
agents.

## Downloads

A stable Voice release has not been promoted through the Distribution Hub yet.

The implementation repository owns the macOS installer pipeline. Private implementation repository and CI details are intentionally not published from this public distribution repository.

macOS release artifact:

```text
Flyto2-Voice-<version>-macos-<arch>.dmg
```

The DMG contains the app plus user-level Install/Uninstall commands. Stable
publication requires Developer ID signing and Apple notarization.

Windows and Linux installers are intentionally not published yet because the
current Voice runtime does not have a supported bundled speech-engine path on
those platforms.

## Release namespace

Future Distribution Hub releases use:

```text
voice/vX.Y.Z
```

## Distribution metadata

- [Product metadata](product.json)
- [Stable channel](stable.json)
- [Beta channel](beta.json)
- [Distribution architecture](../../docs/DISTRIBUTION.md)
- [Supply-chain policy](../../docs/SUPPLY_CHAIN.md)
