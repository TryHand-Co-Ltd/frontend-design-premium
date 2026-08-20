# Consistency Migration Playbook

Use this for established products with many screens, duplicate primitives, contradictory behavior, or visual drift. Do not attempt a big-bang redesign. Migrate through shared foundations and risk-prioritized vertical slices while keeping the product releasable.

## Success criteria

A migration is successful when equivalent operations use the same maintained primitives and contracts, not when every screen merely looks similar in one screenshot.

Define measurable outcomes before changing code:

- canonical shared primitives and token ownership are named;
- project `DESIGN.md` and UX contract reflect accepted system decisions;
- high-risk flows have consistent navigation, feedback, focus, error, and recovery;
- legacy variants have owners, migration status, and removal criteria;
- new drift is blocked by review/CI;
- migrated screens pass behavior, accessibility, locale/theme, and visual regression checks.

## Migration ledger

Create one maintained ledger in the team's existing planning system or design-system docs. Do not create a parallel tracker that nobody owns.

| Surface/route | Operation | Current primitive | Canonical target | Visual drift | Behavior drift | Risk | Dependencies | Owner | Status | Verification |
|---|---|---|---|---|---|---|---|---|---|---|

Suggested status: `inventoried → decision-needed → adapter-ready → migrating → verified → legacy-removed`.

Track exact variants such as `LegacyConfirm`, `window.confirm`, screen-local toast, custom button classes, duplicated pagination, direct color literals, or divergent post-save routes. A component name alone is not enough; record behavior and token source.

## Phase 0: Establish evidence and freeze new drift

1. Inventory routes, workflows, shared packages, Storybook stories, token sources, and duplicated primitives.
2. Search for high-risk bypasses: native dialogs, raw destructive mutations, screen-local validation/toasts, inaccessible click targets, hardcoded colors, unbounded tables, and inconsistent navigation.
3. Sample rendered screens across product areas, themes, locales, viewport classes, and permission levels.
4. Build the behavior ledger from `consistency-system.md` and the token map from `token-mapping.md`.
5. Add a lightweight review rule: new work must use the chosen candidate primitives or document why it cannot. Do not wait for the full migration to stop new drift.

Output: inventory, baseline screenshots/tests, risk ranking, and explicit unresolved decisions. No mass refactor yet.

## Phase 1: Select canonical contracts

Choose the strongest maintained pattern using evidence, not majority count alone. A frequently copied pattern can still be unsafe.

For each family—Button, field/form, dialog, toast/alert, table/pagination, search, navigation, loading/progress—decide:

- public API and named variants;
- visual token owner and runtime mapping;
- state model and keyboard/focus behavior;
- locale and responsive behavior;
- success/failure/navigation outcomes;
- compatibility and deprecation policy.

Update `DESIGN.md` for accepted visual system decisions and `UX-CONTRACT.md` for behavior. Resolve system-wide business questions before migrating many screens; do not let each migration ticket reopen them.

## Phase 2: Harden shared foundations

Implement or repair canonical primitives before screen-by-screen work.

- Add complete states, semantics, tests, stories, and theme/locale coverage.
- Introduce adapters around legacy APIs when they can map honestly to the canonical primitive.
- Preserve behavior through compatibility props only when a real business variant exists. Do not encode every historical accident as a permanent option.
- Add deprecation warnings or static rules after a replacement path exists.
- Use codemods only for mechanical transformations with deterministic mappings; review semantic changes manually.

Examples:

```text
LegacyDangerButton → Button intent="danger" emphasis="outline"
LegacyModal → Dialog or AlertDialog based on interaction contract
screen toast helpers → shared notification service
raw hex → semantic token only after role is confirmed
```

Output: stable migration targets with component, interaction, accessibility, and visual tests.

## Phase 3: Migrate risk-prioritized vertical slices

Do not migrate alphabetically or by CSS similarity. Prioritize:

1. destructive, permission, security, financial, and bulk actions;
2. authentication/session and sensitive-data flows;
3. high-traffic create/edit/search/table workflows;
4. accessibility blockers and mobile-critical paths;
5. high-drift areas that generate repeated implementation work;
6. low-risk cosmetic inconsistencies.

Migrate complete workflows rather than isolated controls. A new Button with an old confirmation, stale toast, and divergent post-save route is not a consistent flow.

For each slice:

1. inspect sibling and upstream/downstream routes;
2. capture current intended behavior and known bugs;
3. replace shared primitives and token aliases;
4. reconcile navigation, pending, success, failure, focus, responsive, locale, offline/conflict, and permission states;
5. run targeted tests and browser QA;
6. release behind a feature flag only when behavior risk or rollout size justifies it;
7. update the ledger immediately.

## Phase 4: Enforce and observe

After enough migration paths exist:

- forbid new imports of retired primitives;
- lint for native dialogs, forbidden raw tokens, and screen-local duplicates when signal is reliable;
- require canonical component stories/state tests for shared changes;
- run representative visual regression rather than snapshotting every unstable page;
- monitor user-visible errors, failed mutations, abandonment, support reports, and performance regressions;
- compare metrics by workflow, not only aggregate release health.

Automated enforcement must link to a supported replacement and exception process. Do not add a rule that developers must routinely bypass.

## Phase 5: Remove legacy safely

Remove a legacy primitive only when:

- repository references are gone or explicitly exempted;
- runtime telemetry/feature flags show the new path is stable when applicable;
- tests cover the canonical replacement;
- deprecated token aliases and adapters have no consumers;
- rollback or release recovery is understood;
- documentation and examples point only to the maintained path.

Delete compatibility branches created by the migration when their callers are gone. Leaving every adapter indefinitely recreates the inconsistent system behind a cleaner import name.

## Cadence for a 100+ screen product

Calendar weeks depend on team size and release constraints. A practical sequence is:

- **Iteration 1:** Phase 0 inventory and freeze new drift.
- **Iteration 2:** canonical decisions plus the first hardened primitives.
- **Following iterations:** one or more risk-prioritized vertical slices while foundations continue.
- **Continuous:** enforcement, telemetry, ledger maintenance, and legacy removal.

Do not promise “Week 1/2/3” completion without route count, ownership, test coverage, and dependency evidence.

## Definition of done for one migrated workflow

- Uses canonical tokens and shared primitives with no unexplained local override.
- Matches the behavior ledger for labels, pending, success, error, navigation, focus, and recovery.
- Covers default, loading, empty/no-results, error, permission, responsive, locale/theme, and applicable offline/conflict states.
- No native dialog, duplicate submit, stale request overwrite, or inaccessible click target remains.
- Tests and browser evidence cover the risky path.
- Migration ledger and deprecation status are updated.
- Old code created obsolete by this slice is removed when safe.

## Rollback and compatibility

Separate reversible migration mechanics from intentional product behavior changes. If both must ship together, document them and increase rollout protection.

- Keep data/API compatibility unless the migration explicitly owns a contract change.
- Prefer adapters and route-level flags over maintaining two independent component systems.
- Roll back by slice, not by reverting unrelated foundation fixes.
- Never preserve a security, accessibility, or data-loss defect solely for visual compatibility; isolate and communicate the correction.
