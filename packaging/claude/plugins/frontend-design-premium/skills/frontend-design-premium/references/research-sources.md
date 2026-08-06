# Research Basis

This skill deliberately composes the upstream visual-design skill instead of copying it. The production rules are grounded in the following primary or authoritative sources. Re-check links when revising the skill because platform behavior and guidance evolve.

## Agent Skills and Claude

- [Agent Skills specification](https://agentskills.io/specification) — required `SKILL.md` format, frontmatter constraints, progressive disclosure, relative references, and `<500` line guidance.
- [Best practices for skill creators](https://agentskills.io/skill-creation/best-practices) — start from real corrections, keep the main skill concise, use gotchas/checklists/validation loops, and calibrate prescriptiveness.
- [Claude Code skills documentation](https://docs.anthropic.com/en/docs/claude-code/skills) — skill locations, activation, supporting files, live changes, stacked skills, and lifecycle.
- [Anthropic `skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) — description triggering, progressive disclosure, eval-driven iteration.
- [Anthropic `frontend-design`](https://github.com/anthropics/skills/tree/main/skills/frontend-design) — separately installed aesthetic base loaded at runtime.

The standard frontmatter does not define `extends`, `inherits`, or dependency resolution. Runtime composition is therefore the portable approach: load the installed `frontend-design` each invocation and keep premium rules in a separate skill. A metadata dependency key is informational only and must not be treated as enforcement.

## Durable design context

- [Google Labs DESIGN.md](https://github.com/google-labs-code/design.md) — living design-context format, CLI lint/diff/export behavior, and Windows `designmd` alias.
- [DESIGN.md format specification](https://github.com/google-labs-code/design.md/blob/main/docs/spec.md) — frontmatter token schema, canonical section order, unknown-content preservation, token references, and contrast findings.
- [DESIGN.md philosophy](https://github.com/google-labs-code/design.md/blob/main/PHILOSOPHY.md) — prose-first design intent, specific references, negative constraints, restraint, and extensibility for motion/iconography/domain context.
- [W3C Design Tokens Format Module](https://www.designtokens.org/tr/2025.10/format/) — portable token groups, aliases/references, and interchange semantics.
- [MDN CSS custom properties](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_cascading_variables/Using_CSS_custom_properties) — runtime semantic variables, inheritance, and fallback behavior.
- [Tailwind theme variables](https://tailwindcss.com/docs/theme) — mapping theme namespaces to generated utility APIs and CSS variables.

The format is alpha. Re-check it before parser/export automation. Exact tokens that are defined provide stable values, while prose carries the visual rationale and usage constraints needed to preserve taste across sessions. Exported tokens still require an explicit project adapter and ownership model; successful export alone does not prove rendered consistency.

## Accessibility and interaction

- [WAI-ARIA APG: Dialog (Modal)](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) — inert background, focus movement/trap/restoration, Escape, and least-destructive focus for hard-to-reverse actions.
- [WAI-ARIA APG: Alert Dialog](https://www.w3.org/WAI/ARIA/apg/patterns/alertdialog/) and [example](https://www.w3.org/WAI/ARIA/apg/patterns/alertdialog/examples/alertdialog/) — destructive confirmation semantics and accessible naming.
- [WAI-ARIA APG: Button](https://www.w3.org/WAI/ARIA/apg/patterns/button/) — action semantics, keyboard behavior, focus outcomes, labels, and disabled/toggle states.
- [WAI-ARIA APG: Tooltip](https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/) — hover and focus activation, Escape dismissal, and description association. APG marks this pattern work-in-progress; test implementations.
- [WAI-ARIA APG: Table](https://www.w3.org/WAI/ARIA/apg/patterns/table/), [Grid](https://www.w3.org/WAI/ARIA/apg/patterns/grid/), and [grid/table properties](https://www.w3.org/WAI/ARIA/apg/practices/grid-and-table-properties/) — native table preference, interactive-grid distinction, sort and virtualized row metadata.
- [Sortable table example](https://www.w3.org/WAI/ARIA/apg/patterns/table/examples/sortable-table/) — real sort buttons, hover/focus parity, pointer cursor, and full header hit target.
- [WCAG 2.2 Target Size (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) — 24×24 CSS pixel minimum or spacing exceptions; larger targets are encouraged.
- [WCAG 2.2 Consistent Identification](https://www.w3.org/WAI/WCAG22/Understanding/consistent-identification) — repeating functions should be identified consistently across pages.
- [WCAG 2.2 Error Identification](https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html) and [ARIA live error technique](https://www.w3.org/WAI/WCAG22/Techniques/aria/ARIA19) — textual, associated, perceivable error feedback.
- [WAI-ARIA APG: Date Picker Dialog](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/examples/datepicker-dialog/) — calendar keyboard and focus behavior.
- [WAI-ARIA APG patterns index](https://www.w3.org/WAI/ARIA/apg/patterns/) — breadcrumbs, tabs, accordions, disclosures, comboboxes, listboxes, menus, sliders, meters, toolbars, and composite keyboard models.
- [WCAG 2.2 Focus Not Obscured](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html), [Dragging Movements](https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html), and [Accessible Authentication](https://www.w3.org/WAI/WCAG22/Understanding/accessible-authentication-minimum.html) — sticky-overlay focus visibility, non-drag alternatives, and password-manager/paste-friendly authentication.

## Forms, search, locale, and stability

- [MDN `<form>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/form) and [constraint validation](https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Constraint_validation) — `novalidate` suppresses interactive native validation while the Constraint Validation API remains available.
- [MDN password input](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/password), [autocomplete](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/autocomplete), and [password guidance](https://developer.mozilla.org/en-US/docs/Web/Security/Authentication/Passwords) — semantic input/autocomplete behavior and password-manager compatibility.
- [MDN debounce](https://developer.mozilla.org/en-US/docs/Glossary/Debounce), [`InputEvent.isComposing`](https://developer.mozilla.org/en-US/docs/Web/API/InputEvent/isComposing), [`compositionend`](https://developer.mozilla.org/en-US/docs/Web/API/Element/compositionend_event), and [`AbortController`](https://developer.mozilla.org/en-US/docs/Web/API/AbortController) — responsive and race-safe search, including IME.
- [MDN `Intl.DateTimeFormat`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat) and [internationalization guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Internationalization) — explicit locales, calendars, formats, and timezone behavior.
- [MDN `scrollbar-gutter`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/scrollbar-gutter) — reserving scrollbar space to avoid layout shifts.
- [web.dev: Optimize Cumulative Layout Shift](https://web.dev/articles/optimize-cls) — reserve dimensions for media and late content and manage font-related shifts.
- [MDN File drag and drop](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API/File_drag_and_drop) and [`<input type="file">`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/file) — drop-zone picker alternatives, accepted files, and native input behavior.
- [MDN online/offline events](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/onLine) — connectivity signals are inherently unreliable hints and require request-level handling.

## Japan-market content, layout, and regulation

- [Digital Agency Design System: Style guides](https://design.digital.go.jp/dads/guidance/style-guides/) — a design system is a foundation; each service still needs a style guide grounded in its information architecture and users.
- [Digital Agency Design System: Typography](https://design.digital.go.jp/dads/foundations/typography/) and [typography accessibility](https://design.digital.go.jp/dads/foundations/typography/accessibility/) — Japanese-capable fonts, readable baseline sizing, non-italic emphasis, and standard/dense text roles.
- [W3C Japanese Layout Requirements (JLREQ)](https://www.w3.org/International/jlreq/?lang=en) — Japanese composition, mixed scripts, line length, punctuation, and line-breaking requirements.
- [Digital Agency Design System: Input text usage](https://design.digital.go.jp/dads/components/input-text/usage/) — Japanese form labels, required-state presentation, correction guidance, and validation timing baseline.
- [Digital Agency: Web accessibility introduction guidebook](https://www.digital.go.jp/resources/introduction-to-web-accessibility-guidebook) — Japanese public-sector accessibility practice referencing WCAG and JIS X 8341-3.
- [Personal Information Protection Commission: laws and guidelines](https://www.ppc.go.jp/personalinfo/legal/) — authoritative starting point for APPI/personal-information obligations; legal/product owners determine applicability.
- [Consumer Affairs Agency: mail-order final confirmation guidance](https://www.no-trouble.caa.go.jp/what/mailorder/guidelines.html) — ecommerce disclosure, review, correction, and final-confirmation considerations; re-check current authority for each implementation.

These sources are baselines and routing evidence, not a universal Japanese theme or substitute for target-user research, domain policy, native content review, or legal advice.

## Product UX decisions

- [Material Design: Confirmation & acknowledgement](https://m1.material.io/patterns/confirmation-acknowledgement.html) — confirm consequential actions, acknowledge completion, and avoid confirming negligible/reversible changes.
- [Nielsen Norman Group: Confirmation dialogs](https://www.nngroup.com/articles/confirmation-dialog/) — reserve confirmations for serious consequences, use explicit actions, typed confirmation only for rare high-risk cases, and avoid fatigue.
- [Nielsen Norman Group: Infinite scrolling](https://www.nngroup.com/articles/infinite-scrolling-tips/) and [pagination alternatives](https://www.nngroup.com/articles/alternatives-pagination-listing-pages/) — choose pagination/load-more/infinite scrolling from user goals, position recovery, footer access, and dataset size.

## Component and visual verification

- [Storybook UI testing](https://storybook.js.org/docs/writing-tests) — stories as renderable state cases, interaction tests, automated accessibility checks, visual regression, and CI reuse.
- [Storybook accessibility testing](https://storybook.js.org/docs/writing-tests/accessibility-testing) — automated checks complement but do not replace manual keyboard and assistive-technology review.

## Maintenance policy

When updating this skill:

1. Read the latest upstream `frontend-design`; do not copy it into this repository.
2. Re-check Agent Skills/Claude frontmatter and composition capabilities.
3. Validate every strict rule against a real failure case or authoritative source.
4. Add new corrections to core `SKILL.md` only if agents repeatedly miss them; otherwise update the focused reference.
5. Lint/diff DESIGN.md examples with the current official CLI and preserve unknown extensions.
6. Run eval prompts and compare against a no-skill or previous-skill baseline.
7. Add high-risk patterns to focused references; do not turn core `SKILL.md` into an exhaustive component catalog.
8. For large migrations, measure canonical primitive adoption and legacy retirement; do not equate a broad visual rewrite with behavioral consistency.
