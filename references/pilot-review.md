# Pilot frontend review policy

This policy is the semantic review contract for Pilot pull requests that touch
`apps/web/**`, project-root `DESIGN.md`, or project-root `UX-CONTRACT.md`.
Reviewers must load the pinned upstream `frontend-design` snapshot and the
pinned `frontend-design-premium` snapshot shipped by the Pilot before reviewing
the complete pull-request diff.

## Finding levels

- **P0 — critical:** exploitable security or privacy exposure, data loss,
  inaccessible critical workflow, or another defect unsafe to release.
- **P1 — major:** broken workflow, permission mismatch, localization failure,
  responsive failure, or a material violation of the maintained design or UX
  contract.
- **P2 — defect:** clear inconsistency, missing interaction state, usability or
  accessibility defect, or an objective premium-skill violation in changed
  code.
- **P3 — suggestion:** subjective polish or taste improvement whose absence
  does not make the workflow incorrect.

P0, P1, and P2 findings require changes. P3 findings are advisory. Every
finding must name a concrete file and line or the narrowest relevant code area,
describe user impact, and propose a verifiable correction. Do not inflate
subjective taste disagreements into blocking findings.

## Review procedure

1. Confirm the vendored snapshot manifest and both skill digests pass the
   repository's deterministic validation.
2. Read the project's maintained business context, `DESIGN.md`, and applicable
   `UX-CONTRACT.md` before judging intent.
3. Review the full diff and the affected user workflow, not isolated styling
   lines. Check security and permission boundaries before visual polish.
4. Apply the premium verification checklist, including keyboard, touch,
   narrow viewport, localization, loading, empty, error, success, and recovery
   states where applicable.
5. Report only actionable findings introduced or exposed by the change. Mark a
   review as passing when no P0-P2 finding remains; P3 suggestions may remain.

Pilot repositories intentionally keep merge authority flexible. This policy
defines the expected result and review language; it does not require a paid
GitHub branch-protection feature.
