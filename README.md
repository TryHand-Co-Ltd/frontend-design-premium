# frontend-design-premium

A production UX Agent Skill that composes with Anthropic's [`frontend-design`](https://github.com/anthropics/skills/tree/main/skills/frontend-design) skill.

Pilot projects can vendor an exact release together with the exact tested
upstream snapshot. [`integrations/pilot.json`](integrations/pilot.json) is the
machine-readable compatibility and review-policy contract used by the Pilot
Base; [`references/pilot-review.md`](references/pilot-review.md) defines its
P0-P3 semantic review levels.

`frontend-design` provides the brief-specific visual direction. `frontend-design-premium` turns that direction into durable project context and adds the production behavior usually required by real applications: cross-screen consistency, data workflows, advanced inputs, resilient async states, localization, accessibility, layout stability, and verification.

## Why composition instead of a fork?

The Agent Skills specification does not currently define `extends`, `inherits`, or portable dependency resolution. Copying the upstream skill would cause the two versions to drift.

This skill therefore uses runtime composition:

1. It requires the installed `frontend-design` skill to be loaded before planning or implementation.
2. It does not vendor or copy upstream instructions.
3. Each activation reads the currently installed upstream file, so upstream upgrades are picked up without merging this repository.
4. `scripts/resolve_frontend_design.py` provides a fallback for harnesses without native skill loading.

`metadata.upstream-skill` is descriptive metadata only. The runtime loading instructions in `SKILL.md` enforce the dependency.

## Requirements

- A separately installed `frontend-design` Agent Skill.
- Python 3 for the bundled resolver, installer, and validator.
- Node.js only when running the optional Google DESIGN.md CLI.
- `uvx` only when running the official Agent Skills reference validator.

## Quick start

### 1. Check upstream dependency

Verify the required `frontend-design` skill is installed:

```bash
python scripts/install.py --check
```

If missing, install it separately (the premium skill depends on it at runtime).
`frontend-design` is distributed as an agent skill — clone or copy it into the same harness `skills/` directory
where you install this premium skill:

```bash
# Example: install upstream from Anthropic's skills repo
git clone https://github.com/anthropics/skills.git /tmp/anthropics-skills
cp -R /tmp/anthropics-skills/skills/frontend-design ~/.agents/skills/frontend-design
# Or symlink: ln -s /tmp/anthropics-skills/skills/frontend-design ~/.agents/skills/frontend-design

# Then install this premium skill
cd ~/frontend-design-premium
python scripts/install.py --target all
```

### 2. Install this skill

```bash
# Single target
python scripts/install.py --target agents

# Or all supported harnesses
python scripts/install.py --target all
```

The installer prefers a **symlink** so repository edits stay live. On Windows it falls back to a **directory junction**, then to a **copy** if neither link method works.

Restart the harness if it does not support live skill discovery.

### 3. CLI reference

| Command | What it does |
|---------|-------------|
| `python scripts/install.py --version` | Print skill version (`v1.0.0`) |
| `python scripts/install.py --check` | Compare source version against each installed target |
| `python scripts/install.py --list-targets` | Show install status per harness (link type + version) |
| `python scripts/install.py --target agents` | Install to `.agents/skills/` (default) |
| `python scripts/install.py --target all` | Install to every supported harness |
| `python scripts/install.py --force` | Replace an existing installation |
| `python scripts/install.py --mode copy` | Copy instead of link (for air-gapped or CI) |
| `python scripts/install.py --upgrade` | `git pull` + reinstall **all** targets (pass `--target agents` to limit) |
| `python scripts/install.py --uninstall` | Remove from **all** targets (same default as `--upgrade`; pass `--target …` to limit) |

> **Author (live edits):** `--target all` once. No reinstall needed — symlink/junction sees repo changes immediately.
> **Consumer (pull updates):** `python scripts/install.py --upgrade` fetches latest changes and reinstalls. If source is not a git repo, `--upgrade` skips pull and reinstalls from current source.

### 4. Use the skill

A short request is sufficient:

```text
/frontend-design-premium Build the API key management workflow from the current product plan.
```

To debug dependency loading in a harness that supports stacked skills:

```text
/frontend-design /frontend-design-premium Build the API key management workflow.
```

Normal use should not require manual stacking because the premium skill explicitly loads its upstream dependency.

### 5. Team installation

**Author flow** (one person per team):

```bash
git clone https://github.com/TryHand-Co-Ltd/frontend-design-premium
cd frontend-design-premium
python scripts/install.py --target all
```

Repo lives on a shared filesystem or is push-pulled. Symlink/junction means changes propagate instantly.

**Consumer flow** (other team members):

```bash
# Same shared repo, or clone fresh
python scripts/install.py --target all
# Pull updates later:
python scripts/install.py --upgrade
```

> **Windows without symlink privileges:** Falls back to junction → copy. Junctions work without Developer Mode. With a **copy**, consumers must run `--upgrade --mode copy` after every pull. Enable Developer Mode (Windows 10+) for symlink support (avoids the junction → copy fallback).

**Alternative — Git submodule:**

```bash
git submodule add https://github.com/TryHand-Co-Ltd/frontend-design-premium .skills/frontend-design-premium
git submodule update --remote .skills/frontend-design-premium
python .skills/frontend-design-premium/scripts/install.py --upgrade
```

The submodule path replaces `scripts/` with `.skills/frontend-design-premium/scripts/` in commands above. `--upgrade` runs `git pull` inside the submodule, so `submodule update --remote` is only needed to switch the pinned commit.

## Durable project context

The skill separates three responsibilities:

1. **`frontend-design`** creates the visual direction appropriate to the brief.
2. **Project-root `DESIGN.md`** preserves the accepted North Star, register, references, anti-references, visual rationale, and normative token values across screens, sessions, and agents.
3. **`UX-CONTRACT.md` or an existing equivalent** preserves workflow, state, navigation, feedback, recovery, locale, and accessibility decisions.

When an established application has no `DESIGN.md`, the skill scans its theme, tokens, shared components, Storybook, and representative rendered screens. It documents the existing identity instead of silently rebranding it. For a new application, it seeds the file from business context and the upstream creative direction.

An existing `DESIGN.md` is not overwritten for a single feature. System-level changes must update the design context and runtime tokens or components in the same changeset.

Templates:

- [`assets/DESIGN.template.md`](assets/DESIGN.template.md)
- [`assets/UX-CONTRACT.template.md`](assets/UX-CONTRACT.template.md)

Validate a generated project file with the cross-platform command:

```bash
npx -p @google/design.md designmd lint DESIGN.md
```

See [`references/design-context-lifecycle.md`](references/design-context-lifecycle.md) for scan, seed, reconcile, lint, diff, and drift-control behavior.

## Token ownership and runtime mapping

[`references/token-mapping.md`](references/token-mapping.md) requires one explicit ownership model:

- **DESIGN.md-generated:** `DESIGN.md` exports runtime token artifacts.
- **Existing runtime canonical:** a mature token package remains authoritative while `DESIGN.md` mirrors exact accepted values and explains their use.

Every changed durable token must follow one traceable path:

```text
DESIGN.md or canonical runtime tokens
  -> generated CSS, Tailwind, or DTCG tokens
  -> framework theme adapter
  -> shared component
```

The same color, radius, spacing, or typography value must not be copied independently into CSS, Tailwind configuration, and a ThemeProvider. Structural linting, generated-file checks, component-state stories, and visual regression provide complementary drift gates.

## Large-codebase consistency migration

[`references/consistency-migration.md`](references/consistency-migration.md) defines a phased approach for products with many screens or duplicate component systems:

1. Inventory current primitives and freeze new drift.
2. Select canonical visual and behavioral contracts.
3. Harden shared primitives and compatibility adapters.
4. Migrate complete workflows in risk order.
5. Enforce canonical usage and observe rollout health.
6. Remove legacy variants after verified adoption.

The migration prioritizes destructive, security, permission, authentication, sensitive-data, and high-traffic workflows before low-risk cosmetic differences. It avoids an unreviewable big-bang rewrite and requires a maintained migration ledger, rollout and rollback criteria, and explicit legacy-removal gates.

## Production contracts

The skill provides focused guidance for:

- cross-screen behavior ledgers and canonical state models;
- pagination, cursor navigation, load more, infinite scroll, and bounded datasets;
- semantic controls with hover, focus, active, disabled, busy, and error states;
- app-owned dialogs instead of `alert()`, `confirm()`, or `prompt()`;
- forms, validation, masked secrets, textareas, and unsaved changes;
- clearable, debounced, IME-safe, stale-request-safe search;
- Japanese locale, date, calendar, timezone, formatting, and copy behavior;
- breadcrumbs, tabs, sidebars, drawers, bottom sheets, responsive tables, truncation, shortcuts, context menus, and print;
- bulk selection, upload, comboboxes, date ranges, inline editing, disclosure, accordions, steppers, sliders, chips, and non-drag alternatives;
- optimistic or queued mutations, autosave, draft recovery, offline behavior, uncertain completion, conflicts, multi-tab use, session expiry, progress, banners, badges, audit timelines, and presence;
- WCAG 2.2 AA, keyboard and touch parity, focus visibility, reduced motion, zoom and reflow, and accessible authentication;
- stable geometry across loading, error, success, theme, locale, and responsive states;
- component stories, interaction tests, automated accessibility checks, browser workflows, and visual regression when supported by the repository.

Patterns are conditional. The skill does not force every component or interaction into every product; it selects behavior from business intent, risk, existing contracts, and repository evidence.

## Repository structure

```text
frontend-design-premium/
├── CHANGELOG.md
├── SKILL.md
├── VERSIONING.md
├── assets/
│   ├── DESIGN.template.md
│   └── UX-CONTRACT.template.md
├── evals/
│   ├── 1.0.0-readiness.md
│   ├── evals.json
│   ├── fixtures/
│   │   ├── a1-b1-consistency.tsx
│   │   ├── audit-records-mobile.tsx
│   │   ├── broken-admin-table.tsx
│   │   ├── destructive-delete-row.tsx
│   │   ├── jp-onboarding-wizard.tsx
│   │   ├── marketing-hero.tsx
│   │   ├── overlay-stack-chaos.tsx
│   │   ├── parse-json-logs.py
│   │   ├── profile-edit-form.tsx
│   │   └── role-gated-actions.tsx
│   ├── golden-test-report.md
├── references/
│   ├── anti-patterns.md              # Grep-able violations + how to fix
│   ├── async-resilience.md
│   ├── auth-patterns.md              # Sign-in/sign-up, session, OAuth, route protection
│   ├── consistency-migration.md
│   ├── consistency-system.md
│   ├── data-entry-patterns.md
│   ├── decision-matrix.md
│   ├── design-context-lifecycle.md
│   ├── e2e-audit-prompt.md           # Reusable E2E audit prompt
│   ├── electron-dual-surface.md      # Token/behavior sync for Electron + web
│   ├── file-upload.md                # Drag-and-drop, validation, progress, abort
│   ├── interaction-contract.md
│   ├── japanese-localization.md
│   ├── layer-contract.md             # Z-index scale, overlay stacking, focus trap
│   ├── llm-streaming.md              # Streaming chat, SSE, abort, message display
│   ├── navigation-layout.md
│   ├── permission-ui.md              # Hide/disable/403, clipboard copy, role access
│   ├── research-sources.md
│   ├── token-mapping.md
│   └── verification-checklist.md
└── scripts/
    ├── check_eval_fixtures.py
    ├── install.py
    ├── reconcile_check.py
    ├── resolve_frontend_design.py
    ├── run_evals.py
    ├── validate_skill.py
    └── verify_cases.py
```

`SKILL.md` keeps the orchestration workflow and non-negotiable rules concise. Focused references are loaded only when relevant, following the Agent Skills progressive-disclosure model.

## Validation

Run the repository validator:

```bash
python scripts/validate_skill.py
```

It checks frontmatter, directory naming, description constraints, line budget, required resources, DESIGN template structure, eval coverage, and upstream resolution.

Run the official Agent Skills reference validator:

```bash
uvx --from skills-ref agentskills validate "$PWD"
```

On Windows, use the executable suffix if required by command resolution:

```bash
uvx --from skills-ref agentskills.exe validate "$PWD"
```

Validate the bundled DESIGN template:

```bash
npx -p @google/design.md designmd lint assets/DESIGN.template.md
```

## Maintenance

Before releasing a change:

1. Read the latest installed and remote `frontend-design` instructions.
2. Re-check Agent Skills and DESIGN.md specifications for format changes.
3. Keep strict rules tied to real failure modes or authoritative guidance.
4. Add repeated high-risk corrections to focused references rather than expanding `SKILL.md` into a component catalog.
5. Run the eval suite against the previous version or a no-skill baseline.
6. Re-run structural, link, token, accessibility, browser, and visual checks that apply to the change.

Research sources and rationale are maintained in [`references/research-sources.md`](references/research-sources.md).
