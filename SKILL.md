---
name: frontend-design-premium
description: Production UX and durable design-context layer that must be used together with the upstream frontend-design skill when building, modifying, reviewing, or refactoring application UI. Use for dashboards, admin tools, SaaS screens, forms, tables, CRUD flows, multi-screen apps, design systems, and localized products—even when the request only says “build”, “implement”, or names one screen. Proactively creates or maintains project DESIGN.md taste context, enforces cross-screen behavioral consistency, resilient interaction states, localization, layout stability, accessibility, and verification.
compatibility: Requires the separately installed frontend-design Agent Skill. Python 3 is optional for bundled resolver and validation scripts.
metadata:
  author: frontend-design-premium contributors
  version: "1.0.0"
  upstream-skill: frontend-design
---

# Frontend Design Premium

Treat `frontend-design` as the visual-design base, project-root `DESIGN.md` as durable taste memory, and this skill as the production-behavior contract. Deliver a UI that is distinctive, operationally coherent, and consistent across future screens and agent sessions.

## 0. Load the upstream skill first

This is composition, not a fork. The Agent Skills standard has no `extends` field, so enforce inheritance at runtime:

1. Load and follow the installed skill named `frontend-design` before planning or coding. Use the harness's native Skill mechanism when available.
2. If native skill loading is unavailable, locate it with `python <this-skill-dir>/scripts/resolve_frontend_design.py --print-path`, then read that `SKILL.md` completely.
3. Do not rely on a copied excerpt of upstream instructions. Loading the installed file is what keeps this skill aligned when `frontend-design` is upgraded.
4. If the dependency cannot be found, stop and report the missing `frontend-design` installation instead of silently approximating it.

Apply both skills. Upstream owns subject-specific aesthetic direction; this skill owns product behavior, consistency, safety, accessibility, and verification. Explicit business rules and an established project contract win. Never trade away accessibility, data safety, or cross-screen consistency for a visual flourish.

## 0a. Register gate — product/admin vs marketing landing page

Before reading any reference, classify the target:

- **Product / admin / SaaS / dashboard / forms / CRUD / tool:** premium behavior wins. You will read all relevant references, establish DESIGN.md, enforce consistency contracts, verify interaction states, and follow the full workflow below.
- **Marketing landing page / brand site / content site / one-shot hero:** upstream `frontend-design` owns the creative direction. This premium skill adds **only** accessibility, layout stability, scrollbar, and reduced-motion rules from §4. Do **not** force UX-CONTRACT.md, consistency-system.md, data-entry-patterns.md, async-resilience.md, interaction-contract.md, or Japanese localization on a marketing page that has no interactive application behavior.

If the brief mixes both (landing + admin), treat each route group by its register. The authenticated/admin section follows the full premium contract; the marketing shell follows upstream with premium polish only.

Apply this gate once at the start. Revisit only when the brief pivots between registers.

## 1. Establish durable project context

Always read `references/design-context-lifecycle.md` before creating, substantially extending, or redesigning an application UI.

1. Find and read the complete project-root `DESIGN.md` and any maintained product/design-system equivalent before visual planning.
2. If an application project has no maintained design context, create `DESIGN.md` proactively from `assets/DESIGN.template.md`: scan existing tokens, components, and rendered screens for an established app; derive a seed from the brief and upstream creative direction for a new app.
3. Do not overwrite an existing visual identity for one feature. Update `DESIGN.md` only for a durable, approved system decision, and update runtime tokens/components in the same changeset.
4. Trace every changed durable token through one documented path from `DESIGN.md` or the established canonical token source to runtime CSS/theme adapters and shared components. Read `references/token-mapping.md`; do not hand-copy the same value into independent systems.
5. For a substantial multi-screen app (at least two list/detail flows **or** any destructive action + searchable table) with no maintained behavioral equivalent, create or maintain `UX-CONTRACT.md` from `assets/UX-CONTRACT.template.md`. A single throwaway screen does not need a contract.

`DESIGN.md` owns visual intent, rationale, and normative values it defines. The UX contract owns workflow, state, navigation, feedback, recovery, locale, and accessibility behavior. Runtime token ownership and generated/adapted outputs must be explicit. Do not duplicate or let them drift.

## 2. Inspect behavior before deciding

Before implementation, inspect the brief and repository for:

- routes and list/detail/create/edit transitions;
- shared components, tokens, form abstractions, overlays, toasts, loaders, and i18n setup;
- at least one comparable completed workflow;
- API paging/filter/sort contracts and async, offline, authorization, and conflict behavior;
- tests, Storybook/component states, browser support, responsive conventions, and accessibility utilities.

For an existing product, preserve the strongest established behavior and fix divergence through shared primitives rather than screen-local patches. Build a private behavior map before coding: `operation → trigger → pending → success destination → success feedback → failure recovery`. Compare the new flow with sibling flows. Do not show this map unless the user asks or a decision is blocked.

## 3. Resolve product decisions with minimal friction

Infer decisions from the business plan, existing code, API shape, and sibling screens. Ask only when different choices materially change workflow or data behavior. Batch unresolved decisions into one compact structured question; use a goal-grilling/decision tool when available.

If the user says “just do it” or provides no answer, use these defaults:

- Admin/searchable data grid: server pagination.
- Exploratory catalog/feed: explicit **Load more**; infinite scroll only when continuous consumption is the product goal.
- Successful create: return to the owning list, preserve relevant list state, and announce success.
- Successful edit: follow the canonical sibling edit flow; if none exists, return to the owning list.
- Destructive or hard-to-reverse action: app-owned confirmation dialog; offer Undo when technically honest.
- Search request debounce: 300 ms, IME-safe, with stale-request cancellation.
- Accessibility target: WCAG 2.2 AA.

Read `references/decision-matrix.md` when choosing pagination/load-more/infinite-scroll, save destinations, confirmation strength, or loading treatment.

## 4. Non-negotiable production contract

### Cross-screen consistency is a feature

The same operation must keep the same label, component, state model, feedback, and navigation outcome everywhere unless the business process genuinely differs. A create flow that returns from `A1` to list `A` establishes the default for equivalent `B1 → B`. Apply this rule to save/cancel/back, toast, loading, empty/error state, placeholder, hover/focus, tooltip, dialog, validation, and destructive actions.

When a difference is intentional, encode it as an explicit variant with a business name—not an accidental one-off conditional. Read `references/consistency-system.md` for the behavior ledger and state matrix.

### Lists and tables

Every non-trivial data table needs a deliberate dataset-navigation strategy. Do not ship an unbounded table.

- Prefer native semantic `<table>` for read-oriented tabular data; use an ARIA grid only for genuinely spreadsheet-like keyboard interaction.
- Keep filtering, sorting, page/cursor, page size, and selection behavior coherent and restorable. Put shareable state in the URL when architecture allows.
- Reset or clamp paging after filter changes and deletion; never strand users on an empty out-of-range page.
- Provide loading, empty, no-results, partial-error, and total/range states without changing the table's footprint unexpectedly.
- Make sortable headers real buttons with hover, focus, active, and `aria-sort` behavior.

### Interaction states and pointer semantics

Anything clickable must look and behave clickable:

- Use a native `<button>` for actions and `<a>` for navigation. Do not make a `div` clickable when semantic HTML works.
- Every enabled pointer target gets a deliberate hover style and `cursor: pointer`; also define visible keyboard focus, pressed/active, and disabled/busy states.
- Hover may enhance but must never be the only way to discover content or actions. Touch and keyboard users receive equivalent access.
- Disabled controls must not look interactive or trigger handlers. Explain unavailable actions when the reason is not obvious.

### Scrollbars and layout stability

Style authored scroll containers to fit the project's token system, including thumb, track, hover, and high-contrast behavior. Keep the scrollbar usable; never hide it merely for aesthetics. Use standards-based properties plus engine fallbacks only as needed. Reserve scrollbar space with `scrollbar-gutter: stable` where appearance could shift layout.

The layout must not jump, reflow unexpectedly, or move controls during loading and feedback:

- reserve image/media, async content, error/help text, scrollbar, and skeleton space;
- keep skeleton and final content dimensions compatible;
- keep buttons the same size while busy—replace or overlay content instead of widening labels;
- avoid font swaps and late banners that move primary controls;
- anchor overlays and popovers without affecting document flow.

### Dialogs, confirmations, and feedback

Never call browser `alert()`, `confirm()`, or `prompt()` for product UI. Use app-owned, accessible dialog/alert-dialog primitives with focus placement, focus trap/inert background, Escape behavior, accessible title/description, and focus restoration.

Confirm destructive, irreversible, privacy-sensitive, permission-changing, bulk, or costly actions. Name the object and consequence; label the action with the real verb (`Delete`, not `OK`). Initially focus the least destructive action when consequences are serious. Require typed confirmation only for rare, high-impact irreversible operations. Do not create confirmation fatigue for routine reversible saves.

Toasts/status messages use one shared system, semantic tone, stable placement, deduplication, and accessible live regions. A toast acknowledges; it never contains the only copy of critical information or replaces an inline error that needs correction.

### Buttons and semantic tones

Model button presentation on two axes:

- **Emphasis:** solid, outline, ghost/link.
- **Intent:** brand/primary, neutral, success, warning, info, danger.

Derive colors, radius, type, borders, shadow, and motion from the upstream aesthetic and project tokens. Preserve semantic meaning across screens:

- `success`: completed/positive commit;
- `warning`: caution or risky-but-recoverable continuation;
- `info`: neutral information or secondary guidance;
- `danger`: destructive, security-sensitive, or hard-to-reverse action.

Do not communicate intent by color alone. Keep icon, label, focus ring, contrast, sizing, and disabled/busy behavior consistent. In normal screens, keep danger actions visually separated from safe primary actions; reserve high-emphasis danger for the final confirmation.

### Forms and sensitive values

- Put `novalidate`/`noValidate` on product forms and own the validation experience. Do not invoke native validation bubbles with `reportValidity()`.
- Keep semantic types and useful constraint metadata where they aid keyboards, autofill, parsing, or app validation; disabling browser UI does not mean discarding semantics.
- Show errors in text, associate them with fields, preserve entered values, focus/scroll to the first invalid field on submit, and include a correction hint.
- Prevent duplicate submit. During submit, preserve button dimensions and make busy state perceivable.
- Set `resize: none` on textareas. Compensate with sufficient default height and auto-grow or an alternate expansion affordance when long input is expected.
- Password, token, API key, secret, and equivalent inputs are masked by default. Add a keyboard-accessible show/hide button with changing accessible label/state. Use the correct password/autocomplete semantics and never place secrets in URLs, analytics, logs, toast text, or persistent client storage without an explicit security design.
- Warn before navigation when unsaved changes would be lost; use an app-owned dialog for in-app navigation and the narrow browser lifecycle mechanism only for actual page unload.

### Search

Every search field has an explicit clear (`X`) button when non-empty. The button is keyboard accessible, has a localized accessible label, clears immediately, cancels pending work, refreshes results correctly, and returns focus to the input.

Debounce remote search (300 ms default), but do not delay local clearing or explicit Enter submission. Do not fire while IME composition is active; run after composition ends. Cancel superseded requests or ignore stale responses so older results cannot overwrite newer ones. Reflect a committed query in route state when users need Back/Forward or shareable results.

### Locale and Japanese products

All component-library locale packs, application messages, dates, times, numbers, currency, collation, calendar labels, validation copy, aria labels, empty states, and pagination labels follow the active product locale.

For Japanese UI, use `ja-JP` and an explicit domain timezone (often `Asia/Tokyo`, but do not assume it for global data). Japanese language does not automatically mean the Japanese imperial calendar; use Gregorian unless product requirements call for era notation. Make search and debounce safe for Japanese IME input. Read `references/japanese-localization.md` whenever the active locale is Japanese or locale-sensitive components are touched.

### Accessibility and responsive behavior

Target WCAG 2.2 AA. Preserve native semantics, keyboard operation, visible focus, sufficient contrast, reduced motion, zoom/reflow, screen-reader names/status, and practical touch targets. Focus must not be obscured by sticky UI or virtual keyboards. Every drag interaction needs a non-drag alternative, and authentication must allow password managers and paste. Icon-only controls require accessible names and tooltips when the icon is not universally understood. Test no-hover, keyboard-only, narrow viewport, long text, empty data, slow network, and reduced motion.

### Advanced and conditional patterns

Do not force every application to use every pattern. When applicable, follow the focused contracts for breadcrumbs/tabs/navigation shells, responsive tables, bulk selection, upload, combobox/date range, inline edit, disclosure/stepper, optimistic/queued work, drafts, offline/conflict/session recovery, progress, alerts, badges, audit timelines, presence, shortcuts, print, and context menus. Choose behavior from product risk and task intent; visuals remain governed by `DESIGN.md`.

## 5. Implement as a system

Prefer extending existing shared primitives. When multiple screens need the behavior, create or repair the shared component/hook/token rather than duplicating markup and timing constants. Keep visual tokens separate from behavioral invariants so upstream aesthetic upgrades do not break product semantics.

For a large inconsistent product, do not perform a big-bang redesign or preserve every historical accident as a variant. Inventory drift, select canonical contracts, harden shared primitives, migrate risk-prioritized workflows, enforce new usage, then retire legacy code using `references/consistency-migration.md`.

Read references only when relevant. References are grouped into **core** (always consider for product/admin apps) and **on-demand packs** (read only when the brief touches that domain).

### Core (always relevant for product/admin apps)

- `references/anti-patterns.md` — grep-able violations to search during verification.
- `references/design-context-lifecycle.md` — DESIGN.md scan/seed/reconcile/lint/diff behavior.
- `references/token-mapping.md` — DESIGN.md-to-CSS/Tailwind/theme ownership, adapters, exports, drift gates.
- `references/consistency-migration.md` — inventory, canonicalization, risk-prioritized rollout, enforcement, legacy retirement.
- `references/interaction-contract.md` — foundational controls, forms, tables, overlays, toasts, state behavior.
- `references/navigation-layout.md` — breadcrumbs, tabs, navigation shells, responsive tables, truncation, shortcuts, menus, print.
- `references/data-entry-patterns.md` — bulk selection, upload, combobox, date range, inline edit, disclosures, steppers, sliders, chips, drag, filter chips, density.
- `references/async-resilience.md` — optimistic work, drafts, offline, conflict, session expiry, progress, alerts, audit logs.
- `references/consistency-system.md` — multi-screen flows, shared primitives, behavior ledger.
- `references/decision-matrix.md` — product-choice defaults and escalation questions.
- `references/verification-checklist.md` — mandatory pre-done verification.
- `references/japanese-localization.md` — Japanese locale (read when locale is or includes `ja`).

### On-demand packs (read when the brief touches the domain)

- **Auth:** `references/auth-patterns.md` — sign-in/sign-up, session, OAuth, route protection, role-based access.
- **File upload:** `references/file-upload.md` — drag-and-drop, validation, progress, abort, multi-file state.
- **LLM streaming:** `references/llm-streaming.md` — streaming chat, SSE, abort, message display, auto-scroll.
- **Permission UI:** `references/permission-ui.md` — hide/disable/403, clipboard copy, role-based feature access.
- **Layer/overlay:** `references/layer-contract.md` — z-index scale, dialog/drawer/toast stacking, focus trap, portal conflicts.
- **Electron dual-surface:** `references/electron-dual-surface.md` — token/behavior sync for apps with both Electron and web frontends.
- **E2E audit:** `references/e2e-audit-prompt.md` — reusable prompt for static contract audits.
- **Research:** `references/research-sources.md` — rationale and source links.

## 6. Verify before finishing

Always read and run through `references/verification-checklist.md` before declaring the task complete.

At minimum:

1. Confirm `DESIGN.md` was read or appropriately created/reconciled; lint it after changes, verify the documented runtime token mapping, and inspect drift against generated/adapted tokens and shared components.
2. Run the repository's formatter, typecheck, tests, and build that cover the change.
3. Exercise the changed workflow in a real browser when available, including success, failure, loading, empty/no-results, keyboard, and one narrow viewport.
4. Compare the result with at least one sibling screen for visual language, navigation, feedback, labels, and state behavior.
5. Exercise applicable offline, stale/conflict, session, locale/theme, long-content, and reduced-motion states rather than testing only the happy path.
6. Search changed code for the grep-able violations catalogued in `references/anti-patterns.md` — native dialogs, uncancelled search races, non-semantic click targets, missing states, screen-local duplicates, and other common issues. Every match is a bug; fix all of them.
7. Add or update component-state stories, interaction/accessibility tests, and visual regression coverage when the repository supports them.
8. Fix failures and repeat verification.

Report only: what changed, any business decision made, verification run, and unresolved risk. Keep the narration short; a minimal implementation request should still produce a production-ready result.
