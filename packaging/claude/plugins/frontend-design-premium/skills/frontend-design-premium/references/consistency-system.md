# Cross-Screen Consistency System

Consistency means equivalent intent produces equivalent behavior. It is not merely matching colors.

## Behavior ledger

For substantial multi-screen work, derive this ledger privately from the repository. Add it to project docs only if the team will maintain it.

| Operation | Trigger label | Pending UI | Success destination | Success feedback | Error placement | Focus outcome |
|---|---|---|---|---|---|---|
| Create | Create / localized equivalent | Stable busy button | Owning list | Shared success toast | Form summary + inline | New/updated row or list heading |
| Edit | Save changes | Stable busy button | Canonical sibling outcome | Shared success toast | Form summary + inline | Updated item or list heading |
| Delete | Delete | Dialog action busy | List/current valid context | Toast/Undo | Dialog or persistent inline | Next logical item/list heading |
| Search | Search field | Stable table/list loading | Same route or query route | Result count status | Search region | Input/result heading as appropriate |
| Cancel/back | Cancel / Back | None | Originating context | Usually none | Unsaved dialog if needed | Originating trigger/context |

Use actual project vocabulary. The same action keeps the same visible label and accessible name across screens.

## Canonical state model

Every reusable component or workflow should account for applicable states:

- idle/default;
- hover;
- keyboard focus;
- pressed/active;
- selected/current;
- disabled with known reason;
- read-only;
- busy/pending;
- success;
- warning;
- error;
- empty;
- no search results;
- partial data/stale refresh;
- optimistic/pending synchronization;
- queued/offline/retry when relevant;
- version conflict or externally changed;
- session expired or permission changed.

Do not let each screen invent its own subset, vocabulary, timing, or recovery path.

## Shared primitives to look for

Prefer the project's existing equivalents. If missing and repeated, establish one shared primitive rather than one-off UI:

- `Button` with emphasis + semantic intent + size + busy state;
- `IconButton` with accessible name and tooltip policy;
- `TextField`, `PasswordField`/`SecretField`, `SearchField`, `TextArea`;
- `FormField`, error summary, and validation adapter;
- `Dialog`, `AlertDialog`, drawer/popover primitives;
- `Toast`/status region;
- `DataTable`, selection/bulk toolbar, paginator/load-more control, empty/no-results/error states;
- `Combobox`, date/date-range picker, upload queue, disclosure/accordion, and stepper when repeated;
- `LoadingSkeleton`, determinate/indeterminate progress, connectivity banner, and retry state;
- responsive navigation/sidebar/drawer, breadcrumbs, and tabs;
- locale provider and formatters;
- route helpers for list/detail/create/edit transitions;
- unsaved-changes, draft recovery, session-expiry, and conflict guards.

Centralize behavior constants such as debounce/autosave delay, toast timing, retry policy, z-index layers, focus ring, control heights, and dialog widths. Do not scatter magic numbers across screens.

## Flow consistency review

For every changed workflow, compare with at least one sibling flow:

1. Entry point and label.
2. URL/route shape.
3. Page title and breadcrumbs.
4. Form field layout, required markers, help, and errors.
5. Save/cancel/back placement.
6. Busy/disabled behavior and duplicate-submit protection.
7. Success destination and list-state restoration.
8. Toast/status wording and duration.
9. Delete/restore behavior.
10. Focus after navigation, dialog close, save, and deletion.
11. Responsive transformation, truncation, selection scope, and overflow behavior.
12. Offline, retry, session expiry, stale data, and conflict recovery when applicable.

If the sibling is itself inconsistent, do not blindly reproduce it. Find the shared primitive or dominant product convention, make the smallest scoped correction, and mention the intentional consolidation.

## Route and state invariants

- A detail/create/edit route always has an unambiguous owner list or parent context.
- Browser Back should not surprise users by losing filters, page, cursor, sort, or scroll position.
- Creating from a filtered list must define whether the new record matches the filter. Do not imply it disappeared without explanation.
- After deleting the last row on a page, clamp to the previous valid page or refresh the cursor; do not show an accidental empty page.
- Preserve user input after server errors except sensitive values that must be cleared for security.
- Prevent old requests from replacing state after route/query changes.

## Feedback vocabulary

Tie action and feedback verbs together:

- `Save changes` → `Changes saved`
- `Create user` → `User created`
- `Delete project` → `Project deleted`

Localize naturally rather than mechanically, but retain semantic identity. Avoid mixing `Save`, `Submit`, `Update`, and `Done` for the same operation.

## Intentional variation

Variation is valid only when the business process differs. Encode the reason as a named variant such as:

- `saveBehavior="return-to-list" | "stay-inline" | "continue-wizard"`;
- `destructiveLevel="recoverable" | "irreversible" | "catastrophic"`;
- `datasetNavigation="page" | "cursor-load-more" | "infinite"`.

Do not expose variants that have no real use case. The goal is explicit behavior, not abstraction for its own sake.

## Large-scale reconciliation

When inconsistency spans many routes or duplicate component families, use `consistency-migration.md`. Do not normalize 100+ screens through one unreviewable rewrite. Inventory drift, choose canonical contracts, harden shared targets, migrate complete high-risk workflows, enforce new usage, and remove legacy adapters only after their consumers are gone.
