# Agent Instructions

This repository is the Flyto2 **distribution and release-governance authority**.

Before making changes:

- Read `PROJECT.md`, `ARCHITECTURE.md`, `STATE.md`, and `DECISIONS.md`.
- Run `flyto-index context --path . --query "distribution release metadata SBOM provenance"`
  before editing, then search with `rg` and run `flyto-index impact` when a
  named symbol exists. Inspect every affected public release route.
- Do not add product runtime, billing, entitlement, tenant, or security-enforcement
  business logic here.
- Keep this repo focused on product registration, version namespaces, release
  manifests, checksums, SBOM/provenance/signing policy, promotion, channel
  metadata, historical release continuity, and download discovery.
- Never commit installer binaries, signing private keys, release credentials, or
  customer-specific licenses to normal Git history.

Flyto2 source authority remains in product repositories:

- `flyto-flow` for Flyto2 Flow.
- `flyto-runtime` for Flyto2 Runtime.
- `flyto-engine` for Flyto2 Agent Firewall source/backend/connectors.
- `flyto-core` for execution kernel and automation runtime primitives.
- `flyto-cloud` for hosted Cloud product surfaces.
- `flyto-code` and related Security repos for security UI/product surfaces.

Use `git -C /Users/chester/flytohub/flyto2 ...` for git operations.

After changes, run `flyto-index verify . --full-scan --strict` and confirm the
documentation workflow still performs explicit lint, test, build, and verify
steps. A reusable workflow alone is not sufficient local evidence.

## Flyto2 Project Memory Contract

Every Flyto2 repository must keep this project-memory scaffold current:

- `AGENTS.md`: agent operating rules, repo-specific constraints, verification commands.
- `CLAUDE.md`: Claude-facing handoff rules when this repo is edited outside Codex.
- `PROJECT.md`: product purpose, owned surfaces, users, and non-goals.
- `ARCHITECTURE.md`: module boundaries, runtime shape, data flow, and integration points.
- `STATE.md`: current status, known risks, release/deploy state, and last verification.
- `ROADMAP.md`: near-term, later, and explicitly out-of-scope work.
- `tasks.md`: actionable checklist with owners/status when known.
- `DECISIONS.md`: durable architectural/product decisions with dates and rationale.
- `CHANGELOG.md`: user-visible or operator-visible changes.
- `docs/README.md`: index for durable docs in this repo.
- `workflows/*.md`: repeatable agent workflows for idea capture, planning, implementation, bugfix, refactor, investigation, and wrap-up.
- `handoffs/_registry.md`: index of handoffs; new handoffs use `YYYY-MM-DD-topic.md`.

When changing behavior, public copy, deployment, security posture, or frontend UX, update the relevant memory files in the same change. Do not leave stale brand, email, module count, route, or deployment information behind.

## Flyto2 Frontend Quality Gate

Any frontend, website, dashboard, extension webview, app screen, or generated UI in this repository must avoid these eight failures:

1. Ignoring accessibility: every interactive control needs keyboard access, visible focus, semantic HTML or ARIA, sufficient contrast, and useful alt/labels.
2. Missing responsive design: verify mobile, tablet, and desktop; no clipped text, overflow, hidden primary actions, or broken navigation.
3. Weak visual hierarchy: users must immediately see page purpose, primary action, status, and next step.
4. Template-looking UI: reuse Flyto2 design tokens and local components, but tailor layout and copy to the actual product surface.
5. Useless elements: remove decorative or placeholder UI that does not help the workflow, trust, navigation, or comprehension.
6. Unclear hierarchy: controls, cards, tables, panels, and modals must have clear grouping, spacing, headings, and state.
7. Unintuitive navigation: current location, back/forward paths, and cross-links to docs/blog/product pages must be obvious.
8. Hard-to-understand content: copy must be concrete, scannable, current, and consistent with Flyto2 terminology.

Frontend verification must include the relevant automated checks plus manual or screenshot review for responsive layout, accessibility states, navigation clarity, loading/empty/error states, and content readability. Public pages must preserve SEO basics: canonical URL, sitemap coverage, metadata, structured data when relevant, and no broken internal or external links.

## Repo notes

Merged from `CLAUDE.md` so Codex and Claude read one set of rules.

This repo is active as the Flyto2 Distribution Hub, but it must not become a
product source monorepo.

When assisting here:

- Explore the current repository with `flyto-index context`, search with `rg`,
  and inspect `flyto-index impact` before changing public distribution or
  release-policy text.
- Preserve historical release URLs and immutable published identities.
- Route product implementation work to the correct source repo.
- Do not copy credentials, local secrets, signing keys, customer licenses, or
  deployment tokens into files.
- Keep release contracts machine-readable and fail closed on identity/digest
  mismatch.

Before finishing, run `python3 scripts/verify.py` and
`flyto-index verify . --full-scan --strict`, and report the exact local
verification performed.

If a task asks for runtime, marketplace, workflow, crawler, entitlement,
security enforcement, AI governance, GEO, or i18n implementation, inspect the
corresponding source repo instead of implementing product behavior here.
