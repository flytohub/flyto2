# Product Registry

[← Back to Flyto2 Distribution Hub](../README.md)

`products/catalog.json` is the machine-readable allowlist of products that may be distributed from `flytohub/flyto2`.

## Product pages

Each product has its own Markdown entry point and independent release channels:

- [**Flyto2 Flow**](flow/README.md) — [stable](flow/stable.json) · [beta](flow/beta.json)
- [**Flyto2 Runtime**](runtime/README.md) — [stable](runtime/stable.json) · [beta](runtime/beta.json)
- [**Flyto2 Agent Firewall**](agent-firewall/README.md) — [stable](agent-firewall/stable.json) · [beta](agent-firewall/beta.json)

The repository-wide GitHub `/releases/latest` alias is not a product channel and must not be used by the website or updaters.

## Registration contract

Registration does not move source ownership into this repository. A product entry defines:

- stable product identifier;
- public display name;
- source repository;
- distribution tag namespace;
- Markdown product/download page;
- stable channel file;
- beta channel file;
- explicit historical lineage where required.

A release workflow must reject an unknown product id, a source repository that does not match the catalog, a distribution tag outside the registered namespace, or a product whose page/channel contract is missing.

Do not store product implementation here. Product source remains in the registered source repository.
