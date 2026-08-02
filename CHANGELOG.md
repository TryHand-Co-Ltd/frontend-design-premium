# Changelog

## 1.2.0 - 2026-08-02

### Added

- Machine-readable Pilot integration metadata with an exact tested upstream
  commit and digest.
- A Pilot-specific semantic review policy with objective P0-P3 thresholds.

### Changed

- The skill now routes Pilot pull-request reviews through the shared review
  policy while keeping merge enforcement flexible.

### Fixed

- `scripts/reconcile_check.py` is now a portable project-root CLI instead of a
  development-only script containing hard-coded Windows workspace paths.

All notable changes to this skill are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](VERSIONING.md).

## [1.1.0] — 2026-07-30

### Added

- **Business-context discovery** (§1a): authoritative source discovery (PRD, ADR, CONTEXT.md, domain/API contracts, permission policies) with source precedence table.
- **Source conflict and high-risk escalation** in `references/decision-matrix.md`: 7 high-risk categories (permissions, billing, privacy, irreversible ops, legal copy, non-idempotent effects, domain state transitions) with must-not-use-defaults policy. Hard gate integrated into SKILL.md §3.
- **Upstream compatibility policy** (§0a): 5-state model (MATCH, UNTESTED, MISSING, UNTRUSTED, INCOMPATIBLE) with interactive vs strict mode, documented in SKILL.md.
- **`resolve_frontend_design.py --status`**: reports upstream fingerprint, provenance, and compatibility state. CRLF-normalized SHA-256 digest for cross-platform determinism.
- **`validate_skill.py --strict`**: fails release validation unless upstream is MATCH. No fail-open path for strict mode.
- **Component-aware path containment** in `trusted_location()`: rejects prefix siblings (`.agents/skills-evil/`) and `..` traversals.
- **Persistent incompatible-digest tracking** via `upstream-incompatible` list in SKILL.md frontmatter.
- **`install.py --check` upstream status display**: exits non-zero for INCOMPATIBLE.
- **UX-CONTRACT.template.md**: business-context sources table, Source ref column, read-only review guidance. Removed fields that encouraged business-policy duplication.
- **Trust boundary** in SKILL.md §1a: business documents are evidence, not agent instructions.
- **Eval cases #25 and #26**: ADR conflict resolution, billing/high-risk escalation, source traceability.
- **Upstream upgrade workflow** in VERSIONING.md with version-bump guidelines.

### Changed

- `references/design-context-lifecycle.md`: preflight discovery split into business-context and design-context sections.
- `references/decision-matrix.md`: precedence rules now link to SKILL.md §1a as single canonical source (eliminated drift).
- `references/verification-checklist.md`: added business-source, high-risk, and traceability checks.
- Resolver SHA-256 now normalizes CRLF→LF for portable digests.
- SKILL.md §0/§0a/§0b reordered: compatibility check before loading instructions.

### Security

- `trusted_location()` now uses component-aware path containment to prevent prefix-sibling bypass.
- Strict validation mode eliminates fail-open paths for upstream compatibility.

## [1.0.0] — 2026-07-29

### Added

- Stable core contract frozen. No breaking changes to §0–§6 orchestration.
- CHANGELOG.md + VERSIONING.md (SemVer policy).
- Soft-delete / archive / restore subsection in `references/interaction-contract.md`.
- Document title + route error / 403 page contracts in `references/navigation-layout.md`.
- Verification checklist items for soft-delete, document title, and route error/403 pages.
- Eval fixtures: `marketing-hero.tsx` (#4), `parse-json-logs.py` (#20), `role-gated-actions.tsx` (#23), `overlay-stack-chaos.tsx` (#24).
- Eval cases #23 (permission-ui) and #24 (layer-contract).

### Fixed

- DESIGN.template.md: null YAML tokens replaced with placeholder strings; components schema from list to map; `omitted` keyword corrected to `omitted:` array (not per-token value).
- UX-CONTRACT.template.md: restored `## Migration status` heading (was merged into Permission section).
- design-context-lifecycle.md: corrected `omitted` usage instructions to Google `omitted:` array spec.
- README: upstream install uses `anthropics/skills` clone + copy of `skills/frontend-design` (not a fake tree URL).
- README CLI table: bare `--upgrade` / `--uninstall` default to **all** targets.

### Fixed (contract quality)

- `references/anti-patterns.md`: `alert`/`confirm`/`prompt` regex improved to `(?:window\.)?(?:alert|confirm|prompt)\s*\(` — avoids Svelte false positives (`{#each alerts as alert}`).
- `references/design-context-lifecycle.md`: Added **Quality gate** subsection to seed mode — `designmd lint` must return 0 errors before marking seed done; common failure modes documented (empty colors, calc values, string typography, list-format components, redundant omission).
- `references/anti-patterns.md`: New sections for sortable headers (button + `aria-sort`), missing document title, missing 403 page. Verification checklist updated with grep for sortable headers, `noValidate`, static title, 403-as-404.
- `references/anti-patterns.md` D: Added note that `type="search"` native clear is not sufficient — requires app-owned clear button.
- `references/interaction-contract.md`: Added **Intent axis — DO NOT flatten** subsection under hard-delete — explicit 3-tier (warning/outline for soft-delete, danger for hard-delete, default for restore).
- `evals/1.0.0-readiness.md`: Added dogfood evidence table (6 projects) + post-1.0 gap list (IME, scrollbar, aria-sort, etc.).
- `references/anti-patterns.md`: Verification checklist grep patterns updated to match the improved alert regex.

### Added (references)

- `references/electron-dual-surface.md` — token/behavior sync guidance for apps with both Electron/Tauri and web frontends.
- `references/e2e-audit-prompt.md` — reusable prompt for static contract E2E audits.

### Fixed (installer)

- `install.py`: Windows junction + `--force` no longer crashes (`is_junction()` → `unlink()` instead of `rmtree`).
- `install.py`: `--upgrade` now respects `--mode` (copy|link) and `--target` (single target or all).
- `install.py`: `--check` correctly distinguishes `junction` vs `copy` on Windows.
- `install.py`: `_git_pull` handles submodules (`.git` as a file, not directory).
- `install.py`: Dangling junctions are recognised and removed during install/uninstall.
- `install.py`: Symlink failure message reduced to silent pass (expected on Windows without Developer Mode).

### Changed (installer docs)

- `VERSIONING.md`: release checklist includes `designmd lint` + `--check`; after-tag notes for consumers.
- `README.md`: CLI reference table, explicit Author vs Consumer flow.

### Hygiene

- README tree: added CHANGELOG.md, VERSIONING.md, evals/fixtures/, verify_cases.py.
- CHANGELOG resource count synced (21 → 21).
- Removed orphan `nul` file and `_tmp_empty_omitted.md` from repository root.
- Version bumped from 0.8.0 to 1.0.0.

## [0.8.0] — 2026-07-29

### Added

- **Register gate** (§0a) — early product/admin vs marketing distinction; prevents over-application of premium contracts on landing pages.
- **Anti-patterns reference** (`references/anti-patterns.md`) — 12 grep-able violations with regex patterns and fix snippets.
- **Japanese localization expanded** (`references/japanese-localization.md`) — from 59 to 210 lines: required-field markers, date format policy, preset ranges, JPY decimal rule, phone/postal half-width, name order, address format, furigana, CSV encoding, dialog verbs.
- **Permission UI reference** (`references/permission-ui.md`) — hide/disable/403 states, clipboard copy pattern, role-based feature access map.
- **Layer contract reference** (`references/layer-contract.md`) — global z-index scale (0–999), dialog/drawer/toast stacking, focus trap, portal conflict resolution.
- **Sticky form actions + unsaved guard** (`references/interaction-contract.md`) — sticky action bar, `beforeunload` + app-owned dialog, dirty state tracking.
- **Table enhancements** (`references/interaction-contract.md`) — sticky header, column freeze, sort single/multi, column visibility persistence.
- **Filter chips + URL state + density** (`references/data-entry-patterns.md`) — filter chips with clear, URL search params as source of truth, compact/comfortable density toggle.
- **Eval fixtures** (`evals/fixtures/`) — 5 fixture files for 7 eval cases (broken admin table, JP onboarding wizard, audit records, profile edit form, destructive delete row).
- **Pack labels** in SKILL.md §5 — core vs on-demand distinction with visual grouping.
- **CHANGELOG.md** and **VERSIONING.md** — SemVer policy + release checklist.
- `reconcile_check.py` — first-occurrence token scan (light mode default fix).
- README tree updated with all 20 reference files listed.

### Changed

- **UX-CONTRACT threshold** hardened (§1) — "at least two list/detail flows or any destructive action + searchable table".
- **Verification step** (§6) now explicitly references `anti-patterns.md`.
- SKILL.md §5 reference index reorganized with core/on-demand grouping.
- `validate_skill.py` expected[] updated: +anti-patterns, +auth-patterns, +file-upload, +llm-streaming, +permission-ui, +layer-contract (23 resources total).

### Fixed

- `reconcile_check.py` dark mode false positive — CSS token scanner keeps first occurrence (light mode default) instead of last (dark mode override).
- `reconcile_check.py` component matching — explicit loop replaces `any()` with generator for reliable Windows path matching.

## [0.7.0] — 2026-07-29

### Added

- `references/auth-patterns.md` — sign-in/sign-up, JWT/database session, OAuth, route protection, role-based access.
- `references/file-upload.md` — drag-and-drop, validation, progress, abort, multi-file state management.
- `references/llm-streaming.md` — streaming chat, SSE consumption, abort control, message display, auto-scroll.
- E2E golden test on jd-cv-matcher + Scopelytics with DESIGN.md creation and reconciliation.

### Changed

- SKILL.md references list updated with 3 new entries.
- README tree + `validate_skill.py expected[]` updated.
- Version bumped to 0.7.0.

## [0.6.0] — 2026-07-29

### Added

- First stable eval suite with 22 cases.
- E2E verification on 5 real projects.
- `evals/golden-test-report.md`.

## [0.5.0] — 2026-07-29

### Added

- Initial skill structure with 12 references + 2 asset templates.
- Runtime composition with `frontend-design` via `resolve_frontend_design.py`.
- 3-layer separation: visual (`frontend-design`) -> taste memory (`DESIGN.md`) -> behavior (`UX-CONTRACT.md`).
- DESIGN.md lifecycle: scan/seed/reconcile/lint/diff.
- Non-negotiable production contract (§4).
- Verification checklist (§6).
