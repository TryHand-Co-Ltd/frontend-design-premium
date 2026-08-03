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

## Upstream `frontend-design` version handling

Direct source installations load the upstream at runtime and record a tested
upstream content digest and revision label. The Codex and Claude Code plugin
packages bundle that same tested snapshot during their deterministic builds, so
marketplace consumers do not need a separate upstream installation.

| Event | Required action | Version bump |
|-------|---------------|-------------|
| Upstream installed/reinstalled with same digest | No action | None |
| Upstream upgraded, digest unchanged | No action | None |
| Upstream upgraded, digest changed, behavioral diff is **cosmetic only** | Run evals, confirm, update `upstream-tested.digest` in SKILL.md | PATCH |
| Upstream upgraded, digest changed, **observable change** in visual direction, subject/audience inference, or planning verbosity | Run full evals, review diffs against 6+ project baselines, update tested digest | MINOR |
| Upstream upgraded, digest changed, **breaking change** to premium contract precedence, safety invariants, or access rules | Run full compatibility eval, update tested digest, document migration | MAJOR |

### Upgrade workflow

When upstream changes:

1. Upgrade `frontend-design` separately in a controlled environment using the target harness.
2. Run `python scripts/resolve_frontend_design.py --status` to get the new fingerprint.
3. Run `python scripts/validate_skill.py` for structural validation.
4. Run the eval suite and compare outputs against the previous tested upstream.
5. Review changed outputs: business-context grounding, register classification, visual direction, DESIGN.md content.
6. If changes are acceptable, update `upstream-tested.digest` in `SKILL.md`, `integrations/pilot.json`, and the vendored upstream metadata.
7. Bump premium version per the table above.
8. Build both marketplace packages and confirm their vendored digest matches.
9. Update CHANGELOG with the upstream revision and summary of behavioral changes.

## What versioning does NOT cover

- Individual project `DESIGN.md` files (project-specific, not part of the skill)
- Internal script changes that don't change the agent's behavior (e.g., reconcile_check.py improvements)

## Release checklist

Before tagging a release:

1. `npx -p @google/design.md designmd lint assets/DESIGN.template.md` — **0 errors, 0 warnings**
2. `python scripts/validate_skill.py --strict` — PASS (checks upstream compatibility)
3. `uvx --from skills-ref agentskills.exe validate $PWD` — PASS
4. Internal markdown links — no broken links (ignore regex false positives in code blocks)
5. `python scripts/install.py --check` — all targets MATCH
6. `CHANGELOG.md` updated
7. `SKILL.md` version bumped
8. `evals/golden-test-report.md` updated if behaviour changed
9. `python scripts/build_codex_plugin.py` and the Codex package validator — PASS
10. `python scripts/build_claude_plugin.py` and `claude plugin validate --strict` — PASS

### After tagging

- **Consumers** run `python scripts/install.py --upgrade` to pull the new version.
- Consumers with a **copy install** (not symlink/junction) run `python scripts/install.py --upgrade --mode copy` (the upgrade always applies `force=True`).
