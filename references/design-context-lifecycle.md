# DESIGN.md Context Lifecycle

Use this reference whenever an application UI is created, substantially extended, redesigned, or reviewed for consistency. `DESIGN.md` preserves project-specific visual taste across screens, sessions, people, and agents. It complements rather than replaces the behavioral `UX-CONTRACT.md`.

## Contract ownership

- The installed `frontend-design` skill creates the task-specific aesthetic direction.
- Project-root `DESIGN.md` records the durable visual identity and rationale accepted for this product.
- Project-root `UX-CONTRACT.md`, or an existing equivalent, records durable workflow, state, navigation, and feedback behavior.
- Runtime theme/token files implement the contract in code. Choose whether DESIGN.md generates tokens or an established runtime token package remains canonical, then document the mapping using `token-mapping.md`. Do not let documentation and code become competing sources of truth; change both in the same changeset when a system decision changes.
- Explicit product requirements and an established maintained design system win over inferred preferences.

Do not force a marketing register onto a product surface. Classify the surface before designing:

- **Brand:** expression and memorability can lead, while usability and accessibility remain mandatory.
- **Product:** task clarity, earned familiarity, density, state coverage, and consistency lead.
- **Hybrid:** define which routes use each register while retaining one identity.

## Preflight discovery

Before visual planning:

1. Locate `DESIGN.md` from the project root or nearest documented workspace root.
2. Look for existing equivalents such as a design-system guide, brand guide, token documentation, Figma variable export, Storybook, or theme package.
3. Read product context: brief, PRD, `PRODUCT.md`, route map, supported locales, accessibility target, and comparable screens.
4. Inspect implementation sources: CSS variables, Tailwind/theme config, typography setup, spacing/radius/elevation tokens, icon library, motion utilities, shared components, charts, and theme switching.
5. When a runnable UI exists, inspect representative rendered screens at a narrow phone and small laptop/desktop width. Code declarations alone do not prove the visual result.

## Existing DESIGN.md: read and reconcile

Read the complete file before planning. Treat exact token values that are defined there as normative and its prose as the primary guide to intent and application.

- Preserve unknown frontmatter keys and custom sections; the format intentionally permits extensions.
- Do not silently rewrite the North Star, reference, palette, typography, density, or shape language to suit one feature.
- Compare the requested UI with both `DESIGN.md` and the strongest shared implementation. A one-off screen is not evidence of a new system rule.
- If code and `DESIGN.md` disagree, identify whether the file is stale or the code has drifted. Follow an explicit maintained contract; otherwise use shared tokens and canonical screens as evidence, then reconcile deliberately.
- For a read-only audit, report drift but do not modify the artifact.

Update `DESIGN.md` only when the task introduces or approves a durable system-level decision. Update the corresponding code tokens/components in the same changeset and explain the decision briefly.

## Missing DESIGN.md: create proactively

Create a project-root `DESIGN.md` for a new application or a substantial application feature when no maintained equivalent exists. Do not create one for a throwaway prototype, isolated asset, or read-only review unless the user requests it.

### Existing application: scan mode

Infer before asking:

1. Extract actual shared token values and semantic roles.
2. Inspect representative components in all applicable states and themes.
3. Identify the dominant layout rhythm, density, shape/elevation grammar, icon family, motion character, and content voice.
4. Derive a specific visual reference and anti-references from consistent evidence. Do not invent a rebrand.
5. Record contradictions as drift or unresolved decisions instead of averaging incompatible patterns.
6. Create the file from `assets/DESIGN.template.md`, replacing every prompt with project evidence.

Ask one compact question only when ambiguity would produce a materially different identity, such as playful versus institutional, dense versus spacious, or editorial versus utilitarian.

### New application: seed mode

Derive the first version from the brief, business context, target users, physical usage scene, and the creative direction produced with `frontend-design`.

A useful seed establishes:

- a specific North Star/reference and deliberate anti-references;
- brand/product/hybrid register;
- palette roles and theme strategy;
- type roles and locale-capable fallbacks;
- layout grid, density, breakpoints, and spacing rhythm;
- shape and elevation grammar;
- iconography, motion, data-visualization, and content character;
- visual states for foundational components.

Do not fill uncertainty with generic adjectives such as "clean, modern, premium." Prefer a concrete reference that implies a coherent world. Do not prescribe a 4px or 8px scale unless the project evidence or chosen direction supports it.

**Critical: no empty maps.** A seed with empty `colors: {}` / `typography: {}` / etc. is NOT complete. Every frontmatter section must either have concrete values or be listed in the `omitted:` array with a reason.

**✅ Correct — define tokens:**
```yaml
colors:
  primary: "#1a91f0"
typography:
  sans:
    fontFamily: "Inter, system-ui, sans-serif"
```

**✅ Correct — omit a section entirely:**
```yaml
omitted:
  - section: spacing
    reason: "inherited from upstream frontend-design"
  - section: rounded
    reason: "not applicable to this project"
# Do NOT define spacing: or rounded: when they are in omitted.
```

**❌ Wrong — these all break the lint or provide no value:**
- `colors: {}` — passes lint but useless to the agent
- `colors: omitted` — invalid YAML; linter sees each character as a color name
- `primary: omitted` — `omitted` is a top-level array, not a per-token value
- Typography as string: `sans: "Inter"` (must be object with `fontFamily`)

An empty map passes `designmd lint` but provides no value to the agent. A section listed in `omitted:` should be explained in the prose body.

**Quality gate — do NOT mark the seed as done until:**

1. `npx -p @google/design.md designmd lint DESIGN.md` returns **0 errors**.
2. Every color value is a valid CSS color (hex, oklch, hsl, rgb) — not `""` (empty string) and not `calc(...)`.
3. Every `typography.*` entry is an **object** with `fontFamily` (and optionally `fontSize`, `lineHeight`) — not a bare string like `sans: "Inter"`.
4. `rounded` values are CSS length or `DEFAULT` — not expressions like `calc(...)`.
5. No section exists as both a defined key AND in `omitted:` (redundant-omission warning).
6. `components:` is a map of component names to config objects — not a list (`- ""`).

> **Why this gate?** A DESIGN.md that passes `designmd lint` with 0 errors ensures the agent can reliably read tokens. Empty colors, `calc` values, string typography, and list-format components all cause lint errors that block the agent from understanding the design system. Verify before declaring done.

## Format contract

Follow the current Google Labs DESIGN.md format:

- optional YAML frontmatter for tokens, using `version: alpha` while that remains current;
- exact values in `colors`, `typography`, `rounded`, `spacing`, and `components` when known;
- Markdown prose that explains why, where, and where not to use those values;
- these `##` sections, when present, in canonical order:
  1. Overview
  2. Colors
  3. Typography
  4. Layout
  5. Elevation & Depth
  6. Shapes
  7. Components
  8. Do's and Don'ts

Use `omitted` with a reason when a canonical token group is intentionally absent. Keep extension material such as iconography, motion, themes, data visualization, and content voice within suitable canonical sections or preserved custom sections. Never create duplicate `##` headings.

## Taste quality bar

A useful `DESIGN.md` must answer:

- What specific thing should this interface feel like, and for whom?
- Is this surface asking for brand expression or product familiarity?
- What is the one memorable signature, and where must restraint win?
- What must the product never resemble?
- Which colors are semantic versus expressive?
- How do typography, density, shape, elevation, icons, and motion reinforce the same intent?
- How do Japanese or other supported scripts affect font fallback, line height, density, and truncation?
- What changes between themes without changing semantic hierarchy?

Tokens without rationale are not enough. Prose without implementation values is difficult to verify. Preserve both.

## Validation and drift control

After creating or changing `DESIGN.md`:

```bash
npx -p @google/design.md designmd lint DESIGN.md
```

Use the dot-free alias above on Windows. On other platforms, `npx @google/design.md lint DESIGN.md` is also supported.

When a previous version is available, compare before and after:

```bash
npx -p @google/design.md designmd diff DESIGN.before.md DESIGN.md
```

Then:

1. verify token references and contrast findings;
2. trace changed tokens through the project mapping manifest to CSS variables, Tailwind/framework adapters, and shared consumers;
3. compare generated/exported tokens with runtime theme files when the project uses export automation;
4. inspect representative screens in every supported theme and locale;
5. run component-state stories and visual regression tests when the repository supports them;
6. check that a feature-level change did not alter unrelated shared components.

Because the format is alpha, re-check the official specification before changing parser/export automation. Do not add a package dependency only to run a one-off lint command unless the repository wants it.

## Reconcile drift report

When reconciling an existing `DESIGN.md` against a mature codebase, produce a **drift report** that surfaces intentional deviations and undocumented discrepancies.

### When to produce a drift report

- A substantial feature touches shared components in a project with an existing `DESIGN.md`.
- The agent is asked to review or audit the design system.
- Behavioral contracts (UX-CONTRACT.md or equivalent) are missing or appear stale.
- The codebase shows patterns that contradict documented rules.

Do not produce a report for a one-line fix, a new isolated component that follows existing conventions, or any change the user has explicitly scoped as visual-only.

### Report structure

Keep the report compact. Use a simple table:

| DESIGN.md Rule | Evidence from code | Verdict | Action |
|---|---|---|---|
| "Flat by default — no shadows on static content" | `adminCardClass` uses `shadow-[0_1px_3px_0_rgba(0,0,0,0.04)]` — shadow always present | **DRIFT** | Recommend updating DESIGN.md to reflect intentional use of subtle elevation; or remove shadow if flat was the intended rule |
| "Pill radius for all buttons" | Button component uses `rounded-lg` (8px), not pill | **DRIFT** | Check whether this was an intentional scope rule (admin vs public) or an overlooked component; update DESIGN.md or fix the component |
| "No bold body text — hierarchy through scale only" | `adminSectionTitleClass` uses `font-semibold` | **DRIFT** | Either add a rule exception for section titles or switch to regular weight with increased font-size gap |
| "--ring: oklch(0.708 0 0)" | `globals.css`: `--ring: #4b8eff` | **DRIFT** | Update DESIGN.md to match canonical CSS value |
| "Buttons use `var(--color-primary)`" | Button: `bg-primary-600` (Tailwind utility referencing same variable) | **MATCH** | No action needed |

### What to check

1. **Color values** — compare every DESIGN.md color token against runtime CSS variable values.
2. **Radius and spacing** — compare `rounded.*` and `spacing.*` values against CSS and component usage.
3. **Typography** — compare families, sizes, weights, line-height.
4. **Design rules** — read each prose rule in DESIGN.md and check at least one representative implementation (e.g., "flat surfaces" → check shadow presence on cards; "pill buttons" → check Button component; "no bold" → check section titles).
5. **Component tokens** — compare `components.*` values against shared component styles.
6. **Missing sections** — note canonical sections that DESIGN.md omits (Layout, Elevation, Shapes, Iconography, Motion).

### Drift resolution policy

- **Intentional evolution:** If the codebase intentionally evolved beyond DESIGN.md (e.g., admin section added shadows for hierarchy), update DESIGN.md to document the new rule and its reasoning.
- **Unintentional drift:** If code drifted without a deliberate decision, the agent should fix the code to match DESIGN.md rather than expanding the scope of the drift. Create a shared primitive or apply consistent token usage.
- **Ambiguous:** When intent is unclear, ask one compact question: "Cards in the admin section use subtle elevation (`shadow-[...]`). DESIGN.md says flat. Should I update DESIGN.md or remove the shadow?"

### Output format

Append the drift report to the commit message or task summary. Never silently edit DESIGN.md rules to match code — always explain the discrepancy and the resolution.

```text
## Reconcile drift

| Rule | Evidence | Verdict | Action |
|------|----------|---------|--------|
| "Flat surfaces" | Card has shadow | DRIFT | Updated DESIGN.md to allow subtle admin elevation |
| "Pill buttons" | Button uses 8px radius | DRIFT | Scoped pill to public CTAs only; updated DESIGN.md |
| "No bold" | Section title uses semibold | DRIFT | Added exception for section headings |

3 drifts found. 2 resolved by updating DESIGN.md. 1 resolved by fixing code.
```

### What not to do

- Do not silently rewrite `DESIGN.md` to match code without recording the discrepancy.
- Do not produce a drift report for every token — group related findings.
- Do not force the user to resolve every drift immediately. Record them, fix what is safe, and escalate blocked decisions.
- Do not use the drift report as a justification for a big-bang redesign.

## UX contract companion

For a new or substantial multi-screen application, create `UX-CONTRACT.md` from `assets/UX-CONTRACT.template.md` when no maintained equivalent documents shared behavior. Keep it focused on decisions that must remain consistent:

- operation and navigation outcomes;
- canonical state model;
- dataset navigation;
- validation and feedback;
- destructive action levels;
- async, offline, conflict, and recovery policy;
- locale and accessibility behavior.

Do not duplicate visual prose in both files. Link to `DESIGN.md` from the UX contract and keep visual taste in one place.
