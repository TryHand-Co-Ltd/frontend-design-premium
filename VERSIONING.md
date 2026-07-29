# Versioning Policy

This skill follows **Semantic Versioning 2.0.0** for changes visible to agent-consumers.

## Version components

Given version `MAJOR.MINOR.PATCH`:

| Component | When to bump | Example |
|-----------|-------------|---------|
| **MAJOR** | Breaking change to orchestration (§0–§6), inheritance model, register gate, or non-negotiable contracts. Consumer must update how they load or apply the skill. | Replacing runtime composition with a different mechanism, removing a core non-negotiable, changing the register gate logic. |
| **MINOR** | Adding a reference, expanding a contract (non-breaking), adding eval fixtures, updating DESIGN template. Consumer workflow unchanged. | New `references/permission-ui.md`, new sections in `japanese-localization.md`, adding pack labels in §5. |
| **PATCH** | Typo fix, regex anti-pattern refinement, fixture correction, validator fix, documentation update. No visible change to agent behavior. | Fixed reconcile_check.py encoding, updated anti-pattern grep pattern, corrected README tree. |

## Pre-release tags

- `0.x.y` — pre-1.0 development. Minor bumps may include breaking changes without a MAJOR bump.
- `1.x.y` — stable core contract. Breaking changes require MAJOR bump.

## What versioning covers

- `SKILL.md` orchestration workflow (§0–§6)
- `references/` files completeness and contract content
- `assets/` templates
- `scripts/` validators and installers
- `evals/` eval cases and fixtures

## What versioning does NOT cover

- Upstream `frontend-design` skill changes (handled by runtime loading)
- Individual project `DESIGN.md` files (project-specific, not part of the skill)
- Internal script changes that don't change the agent's behavior (e.g., reconcile_check.py improvements)

## Release checklist

Before tagging a release:

1. `npx -p @google/design.md designmd lint assets/DESIGN.template.md` — **0 errors, 0 warnings**
2. `python scripts/validate_skill.py` — PASS
3. `uvx --from skills-ref agentskills.exe validate $PWD` — PASS
4. Internal markdown links — no broken links (ignore regex false positives in code blocks)
5. `python scripts/install.py --check` — all targets MATCH
6. `CHANGELOG.md` updated
7. `SKILL.md` version bumped
8. `evals/golden-test-report.md` updated if behaviour changed

### After tagging

- **Consumers** run `python scripts/install.py --upgrade` to pull the new version.
- Consumers with a **copy install** (not symlink/junction) run `python scripts/install.py --upgrade --mode copy` (the upgrade always applies `force=True`).
