# Legacy Routing Guide

Use the narrowest current owner for new work:

| Need | Current source of truth |
| --- | --- |
| Open-source execution, browser automation, MCP tools, recipes, evidence, or replay | [`flyto-core`](https://github.com/flytohub/flyto-core) |
| Hosted automation, app builder, marketplace, accounts, billing, or deployment | [`flyto-cloud`](https://github.com/flytohub/flyto-cloud) |
| Code and security product workflows | [`flyto-code`](https://github.com/flytohub/flyto-code), [`flyto-engine`](https://github.com/flytohub/flyto-engine), and [`flyto-ai`](https://github.com/flytohub/flyto-ai) |
| Repository intelligence, impact analysis, and dependency graphs | [`flyto-indexer`](https://github.com/flytohub/flyto-indexer) |
| Public product documentation | [`flyto-docs`](https://github.com/flytohub/flyto-docs) |
| Website, download discovery, and pricing | [flyto2.com](https://flyto2.com) |
| Public technical articles | [blog.flyto2.com](https://blog.flyto2.com) |

Do not open feature work against this repository. For a historical artifact,
identify the exact release and report the issue to the current owning repo when
possible. Security reports go to `security@flyto2.com`.
