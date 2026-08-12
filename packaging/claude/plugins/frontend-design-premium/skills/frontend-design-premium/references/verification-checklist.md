# Verification Checklist

Use this before finishing every implementation or review. Mark non-applicable items mentally; do not dump the checklist into the user response.

## Mandatory project audit sequence

For product/admin work, complete this sequence before claiming compliance:

1. Run `audit_project.py` in strict mode and resolve contract/static findings.
2. Check `DESIGN.md`, runtime tokens, canonical owners, and sibling workflows for drift.
3. Search for false affordances and the grep-able patterns in `anti-patterns.md`.
4. Run project-owned accessibility and localization checks.
5. Exercise the browser state matrix: loading, empty/no-results, error, slow/stale, success, keyboard, narrow viewport, locale/theme, and reduced motion as applicable.
6. Verify complete create/read/update/delete behavior, navigation, list restoration, feedback, confirmation, and focus.
7. Verify server failure-path recovery, retry, duplicate prevention, stale requests, and destructive-dialog recovery.

The static auditor does not execute or replace steps 4–7. Record exact commands and results as completion evidence.

## Dependency, business context, and design context

- [ ] The current installed `frontend-design` skill was loaded completely.
- [ ] **Business-context entry points** were located and relevant sources read before design work:
      PRD, ADR, CONTEXT.md, domain/API contracts, permission policy, or equivalent.
- [ ] Authoritative policy was distinguished from implementation evidence using the
      precedence table (`SKILL.md §1a`).
- [ ] Conflicting authoritative sources were surfaced explicitly — not silently inferred.
- [ ] **High-risk categories** (permissions, billing, privacy, irreversible operations, legal copy,
      non-idempotent side effects, domain state transitions) were resolved from authoritative
      sources or escalated — never through generic defaults.
- [ ] Project `DESIGN.md` and any maintained product/UX contract were read before planning.
- [ ] A missing `DESIGN.md` was appropriately created for a new/substantial application task, or intentionally not created for a throwaway/read-only scope.
- [ ] Existing visual identity was not silently overwritten for one feature.
- [ ] Any system-level design change updated `DESIGN.md` and runtime tokens/components together.
- [ ] Token ownership is explicit: DESIGN.md-generated or established runtime source; changed values trace through one mapping to CSS/theme adapters/shared components.
- [ ] Generated token artifacts were regenerated rather than hand-edited, and manual duplicate values/aliases were not introduced.
- [ ] `DESIGN.md` follows canonical section order, preserves custom content, resolves token references, and passes the official lint when changed.
- [ ] The result follows its specific North Star, register, anti-references, and existing tokens rather than generic “modern/premium” defaults.
- [ ] No aesthetic choice weakened accessibility, data safety, behavior, or cross-screen consistency.

## Repository consistency

- [ ] A comparable sibling flow and shared primitive were inspected.
- [ ] Create/edit/delete/cancel/back destinations match the canonical workflow.
- [ ] Labels, toast wording, dialog behavior, loading, empty/error states, and focus outcomes match shared patterns.
- [ ] Repeated behavior lives in a shared primitive/hook/token rather than a screen-local duplicate.
- [ ] Any intentional difference has a documented business reason or named variant.
- [ ] Responsive transformation preserves actions, permissions, status, ordering, and full-value access.
- [ ] For a large migration, the ledger, canonical target, risk priority, compatibility path, rollout/rollback, and legacy-removal criteria are explicit.
- [ ] A migrated workflow is complete end-to-end rather than mixing new visuals with old dialog/toast/navigation behavior.

## Interaction

- [ ] Click targets use button/link semantics where possible.
- [ ] Enabled targets have hover, focus-visible, active, pointer cursor, disabled, and busy states as applicable.
- [ ] Keyboard, touch/no-hover, and Escape behavior work.
- [ ] Target size/spacing, contrast, accessible names, and focus order are sufficient.
- [ ] Focus is not obscured by sticky UI, sheets, banners, or the virtual keyboard.
- [ ] Icon-only controls have localized accessible names.
- [ ] Drag interactions have a non-drag alternative.

## Navigation and layout

- [ ] Breadcrumbs represent hierarchy, mark the current page, and collapse accessibly.
- [ ] Tabs distinguish focus/selection, implement the correct keyboard model, and preserve route state when needed.
- [ ] Sidebar/drawer/bottom-sheet behavior matches viewport, content length, focus, scroll lock, and safe areas.
- [ ] Truncated important values remain available without hover-only access.
- [ ] Shortcuts/context menus have visible keyboard/touch alternatives and do not conflict with text input or IME.
- [ ] Print behavior was tested when printable output is part of the workflow.
- [ ] Each navigable route sets an honest, localized `document.title` (including loading/error/403).
- [ ] 404 / 403 / route-error pages are app-owned, distinguishable, and leave chrome navigable.

## Tables and lists

- [ ] Pagination/load-more/infinite/render-all is deliberate and matches API/product intent.
- [ ] Filter/sort/page/cursor/selection state is restorable where needed.
- [ ] Loading, empty, no-results, error, and boundary states exist.
- [ ] Sorting semantics and pagination labels/current state are accessible.
- [ ] Delete/filter changes cannot leave an invalid empty page.
- [ ] Narrow-screen overflow or alternate representation is usable and visible.
- [ ] Selection distinguishes page from all-results scope; bulk actions report exact scope and partial failures.
- [ ] Scroll ownership is explicit per active panel: a viewport-bounded table scrolls internally without imposing its height/overflow contract on a sibling form panel or shared shell.
- [ ] In mixed table/form tabs, switching to the form restores natural-height/document scrolling or the established application content scroller; no table-owned `100vh`/`h-dvh`/fixed-height/`overflow: hidden` constraint clips the form.
- [ ] Table page sizes such as 10/20/50 keep the same table frame footprint, while the full long form remains reachable at short/tall viewports and 200% zoom without competing vertical scroll owners.

## Forms and advanced inputs

- [ ] Native browser validation bubbles are disabled with `novalidate`/`noValidate`; no `reportValidity()` UX.
- [ ] Every single-select makes the native or authored popup decision explicit; native is used only when platform-owned popup geometry is acceptable.
- [ ] Native-select audits include CSS `appearance: none` and utility classes such as `appearance-none`; removing native chrome is not treated as evidence that the opened platform popup is authored.
- [ ] Every `<datalist>`/`input[list]` makes the native or authored decision explicit; authored combobox requirements use the project's maintained accessible Combobox/Autocomplete primitive instead of a browser-owned datalist popup.
- [ ] For an authored Select/Listbox, the open popup matches the trigger's outer width within 1 CSS px, aligns to it, and shares border-width/color, radius-family, and density tokens.
- [ ] The open popup was verified in a real browser for keyboard/focus/selection, long options, narrow viewports, 200% zoom, viewport-edge collision, bounded height, and scrolling.
- [ ] Every date picker makes the native or authored decision explicit; native is used only when browser/OS-owned locale, labels, geometry, and behavior are acceptable on supported platforms.
- [ ] The same ownership decision and locale verification covers native `time`, `month`, `week`, and `datetime-local` pickers rather than auditing only `date`.
- [ ] An authored calendar loads the complete active locale and localizes month/year, weekdays, navigation, today/clear/apply/cancel actions, placeholders, validation, and accessible names without fallback English.
- [ ] The open calendar was verified in a real browser for keyboard and pointer selection, Escape, trigger focus restoration, locale copy, 200% zoom, narrow/short viewports, collision, bounded height, and scrolling.
- [ ] App validation shows text errors, correction guidance, field association, and first-error focus.
- [ ] Duplicate submits are blocked without changing button dimensions.
- [ ] Textareas have `resize: none` plus adequate/autogrowing space.
- [ ] Sensitive fields are masked by default with an accessible show/hide control.
- [ ] Correct autocomplete semantics are used; secrets never leak to route/log/toast/analytics/storage.
- [ ] Password managers and paste are not blocked without an exceptional documented reason.
- [ ] Unsaved-change loss is guarded where applicable.
- [ ] Combobox/date-range/slider composite keyboard, focus, selection, clear, loading, and error states work.
- [ ] File upload has a picker alternative, validation, per-file progress/error/retry/cancel, and safe preview behavior.
- [ ] Inline edit/disclosure/accordion/stepper preserves values, focus, validation, and cancellation semantics.

## Search and async resilience

- [ ] Non-empty search has a working localized clear button.
- [ ] Remote search is debounced (300 ms default), IME-safe, and cancelable/stale-safe.
- [ ] Clear and explicit submit are not needlessly delayed.
- [ ] Initial load, background refresh, page load, and mutation use appropriate distinct feedback.
- [ ] No indefinite spinner or stale response overwrite is possible.
- [ ] Optimistic updates are eligible, visibly pending, rollback-safe, and conflict-aware.
- [ ] Auto-save distinguishes local/syncing/saved/offline/failed and can recover or discard a draft safely.
- [ ] Offline, timeout, uncertain completion, bounded retry, and reconnect revalidation are handled when applicable.
- [ ] Multi-tab/multi-user conflicts do not silently overwrite newer data.
- [ ] Session expiry and permission changes preserve safe work and return users through the approved re-auth flow.
- [ ] Determinate/indeterminate progress truthfully reflects measurable work and offers recovery for long jobs.

## Dialogs, destructive actions, and system feedback

- [ ] No product flow calls `alert()`, `confirm()`, or `prompt()`.
- [ ] Modal focus, inert background, Escape, scroll lock, accessible naming, and focus restoration work.
- [ ] Dangerous actions show the object, scope, consequence, and explicit action verb.
- [ ] Soft-delete vs hard-delete matches the UX contract; reversible removals offer Undo/Restore when honest.
- [ ] Serious dialogs initially focus the least destructive action.
- [ ] Confirmation is not overused for routine reversible actions; Undo is offered when reliable.
- [ ] Inline alert/page banner/global banner/toast scope matches the persistence and recovery need.
- [ ] Notification badges have accessible counts, stable geometry, and a defined mark-as-read policy.
- [ ] Audit timelines expose actor/action/time/timezone in text; presence is labeled, fresh enough, and privacy-safe.

## Business-source traceability (UX-CONTRACT.md)

- [ ] `UX-CONTRACT.md` records UI consequences only — business policy is referenced, not duplicated.
- [ ] Each authoritative business rule has a source reference (ADR path, API contract, permission policy).
- [ ] Flow-ledger entries include a source reference where the behavior originates from business policy.
- [ ] The business-context sources table is populated for permission model, data lifecycle, deletion, billing, and legal copy.

## Locale

- [ ] All owned component copy and accessibility labels use the active locale.
- [ ] Dates, ranges, times, numbers, currency, collation, timezone, and calendar match the product contract.
- [ ] Japanese locale was tested with IME and no fallback English when applicable.
- [ ] Long localized text does not clip or move critical controls.
- [ ] Typography fallbacks and line heights render every supported script without breaking density.

## Japan readiness (when market, audience, locale, or data contract triggers it)

- [ ] Japan market, Japanese locale, and Japanese content/visual design were classified independently; an English Japan-market UI and a Japanese non-Japan UI route correctly.
- [ ] Target audience, domain, device context, information density, language/register, trust needs, and supporting evidence are explicit.
- [ ] Japanese-facing marketing work received Japanese content and typography review without being forced through application-only CRUD contracts.
- [ ] Upstream English writing/aesthetic defaults did not override natural Japanese, domain trust, established product conventions, accessibility, or authoritative sources.
- [ ] Japanese copy uses a consistent register, terminology/glossary, action vocabulary, punctuation, and error-recovery style; no owned UI, accessible name, date-picker, email, or component-library English leaks remain.
- [ ] Critical copy was reviewed by a native Japanese reviewer with relevant domain context; reviewer/evidence is recorded or the missing review is reported as release risk.
- [ ] Japanese-capable fonts, approximately 16px body baseline, script-appropriate line height, mixed-script fallback, no default italic, kinsoku behavior, semantic ruby, and representative full-width line measure were inspected.
- [ ] Density follows task and audience evidence; the result does not use sakura/red-sun/washi/brush/anime/“Zen”/decorative-kana shorthand without product evidence.
- [ ] IME composition was exercised in submit, Enter/shortcuts, autosave, validation, counters, combobox/autocomplete, command palette, and search where applicable; no premature action or stale response occurred.
- [ ] Full-/half-width, kana/Kanji/Latin, diacritics, whitespace, and search normalization match the backend/domain contract; client-only normalization does not change identity or matching semantics.
- [ ] Personal and corporate names, furigana, foreign-resident/Latin-name paths, domestic/international phones, all 47 prefectures, editable address auto-fill, building names, and long identifiers were tested as applicable.
- [ ] Date-only/JST/source-timezone, Gregorian/era, calendar/fiscal year (`年度`), weekday/holiday, JPY and tax/rounding/invoice behavior follow explicit domain contracts.
- [ ] Windows Chrome/Edge with Japanese IME, macOS Safari/Chrome with Japanese input, iOS Japanese keyboard, and Android Japanese keyboard were covered to the level promised by product support.
- [ ] Japanese screen-reader output was tested for high-accessibility products; WCAG 2.2 AA verification was supplemented with JIS X 8341-3-oriented checks when applicable.
- [ ] 200% zoom/reflow, user/fallback font behavior, long Japanese text, mixed scripts, and representative `ja-JP` visual regression were inspected.
- [ ] Representative target-user usability evidence exists for consequential Japan-native claims; source review or Japanese-character presence alone is not treated as behavioral proof.
- [ ] Privacy, commerce, subscription, payment, identity, consent, or legal behavior cites current authoritative sources and maintained policy; unresolved authority was escalated rather than guessed.

## Stability, visual, and component QA

- [ ] Scrollbars are tokenized, visible/usable, and layout-stable.
- [ ] The application stylesheet provides a global scrollbar baseline; a new scroll container receives thumb/track/hover/active styling without an opt-in class.
- [ ] WebKit scrollbar pseudo-elements are treated as engine fallbacks, not the complete contract; standards-based `scrollbar-color` and `scrollbar-width` cover Firefox where supported.
- [ ] Computed `scrollbar-color` on the application root is not the browser default in normal color mode, while forced-colors/high-contrast behavior remains system-operable.
- [ ] Images, skeletons, errors/help, spinners, fonts, and async content reserve compatible geometry.
- [ ] No control moves between idle/loading/success/error states.
- [ ] Narrow viewport, zoom/reflow, reduced motion, empty, slow, and error states were inspected.
- [ ] Light/dark/high-contrast themes preserve semantic hierarchy and avoid startup theme flash where applicable.
- [ ] Component stories cover applicable visual and behavioral states.
- [ ] Interaction and automated accessibility tests cover composite widgets.
- [ ] Visual regression compares representative states, themes, locales, and viewports when tooling exists.
- [ ] Token drift checks compare exports/adapters with their declared owner and search for deprecated aliases or raw old values.
- [ ] Browser screenshots or live inspection confirm the result rather than relying only on source declarations.

## Engineering checks

- [ ] Formatter/linter passes.
- [ ] Typecheck passes.
- [ ] Relevant unit/component/integration tests pass.
- [ ] Production build passes when feasible.
- [ ] Browser workflow covers success, failure, keyboard, responsive, and applicable recovery paths.
- [ ] Changed code was searched for native dialogs, non-semantic click handlers, duplicated constants, uncancelled request races, and unhandled conflicts.

Only after applicable checks pass, report concise evidence: changed files/behavior, decisions, commands/tests, browser coverage, and remaining risk.
