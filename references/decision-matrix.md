# Product Decision Matrix

Use this file only when a choice affects product behavior. Infer from the brief and repository first. Ask one compact question batch only if evidence does not select a safe option.

## Dataset navigation

| Context | Default | Why | Required safeguards |
|---|---|---|---|
| Admin grid, audit log, report, searchable records | Server pagination | Users need position, repeatability, and bounded work | URL/restorable state, total/range, page-size policy, clamp after deletion |
| Exploratory catalog or media list | Load more | Preserves flow without hiding the footer or position | Visible control, loading state, item count, Back restoration |
| Social/activity feed where consumption is the goal | Infinite scroll | Minimizes interruption | Virtualization when needed, accessible announcements, restore position, reachable footer alternative |
| Small bounded list | Render all | Lowest interaction cost | Confirm upper bound and performance |
| Unknown or potentially large dataset | Pagination | Safest operational default | Ask only if product intent suggests exploration/feed behavior |

Questions when blocked:

1. Is the user's job to locate/revisit a specific record, or continuously explore?
2. Must the URL be shareable and browser Back restore exact position?
3. Is total count known and affordable?
4. Is the footer or end-of-results meaningful?
5. Does the API expose page/size, cursor, or only an unbounded list?

Do not invent client pagination over a server endpoint that returns incomplete data.

## Post-save navigation

| Operation | Default outcome |
|---|---|
| Create from list | Return to owning list; preserve filters when the new record can appear under them; toast success; focus/scroll to new row when practical |
| Edit opened from list | Follow sibling edit flows; absent precedent, return to owning list and preserve state |
| Inline edit | Stay in context; acknowledge near the edited item; do not navigate away |
| Multi-step setup/wizard | Continue to the explicit next step or completion destination |
| Create-and-add-another workflow | Only stay in create when the UI explicitly offers and the user chooses this variant |

If sibling flows conflict, identify the majority/canonical flow, then consolidate rather than copying the nearest inconsistency.

## Confirmation strength

| Risk | Treatment |
|---|---|
| Reversible, low-impact change | No confirmation; immediate feedback and optional Undo |
| Destructive but recoverable | Confirmation or Undo depending on recovery reliability and project pattern |
| Irreversible delete, permission/security change, bulk action, external side effect, financial cost | App-owned confirmation with object, scope, consequence, explicit verb |
| Rare catastrophic operation | Strong confirmation; typed object name or phrase may be appropriate |

Never use browser `confirm()`. Do not put the safe and dangerous actions next to each other with identical emphasis.

## Loading treatment

| Wait type | Default |
|---|---|
| Initial page/data load | Skeleton matching final geometry; use spinner only when shape is unknowable |
| Table page/filter change | Keep headers and container stable; show row skeleton/overlay; prevent stale overwrite |
| Button mutation | Keep label width/height stable; busy indicator; prevent duplicate activation |
| Background refresh | Preserve usable content; subtle progress/status; do not blank the screen |
| Very fast local operation | Avoid flashing a loader; use a short threshold before showing it |

## Mutation feedback

| Risk and system capability | Default |
|---|---|
| Financial, security, permission, destructive, inventory-sensitive, or external side effect | Pessimistic confirmation; do not claim success before server acknowledgement |
| Frequent low-risk idempotent toggle with reliable rollback | Optimistic update with visible pending state and exact rollback |
| Long-running server job | Server-confirmed job creation, persistent progress/status, and a return path |
| Offline-capable field work with designed conflict/storage policy | Queued mutation with explicit local/sync/failed states |
| Unknown duplicate or conflict behavior | Pessimistic; ask or inspect the API contract before adding optimism |

## Responsive data transformation

| User need | Default |
|---|---|
| Compare values across rows/columns | Horizontal table scroll with visible overflow and stable identifier |
| Scan independent records | Stacked/card representation with repeated labels may be appropriate |
| Only a few columns are critical on mobile | Priority columns plus an explicit detail/column path |
| Dense spreadsheet-like editing | Preserve grid/table semantics; consider a dedicated wider workflow instead of lossy cards |

Never hide fields or actions silently. The same permission, status, order, and business operation must survive the responsive representation.

## Ask vs infer

Ask when the answer changes API contracts, routing, irreversible side effects, permissions, legal copy, locale/calendar/timezone meaning, conflict/offline guarantees, or user-visible workflow shared by many screens.

Infer when existing components, routes, tests, design docs, or sibling screens establish a clear convention. Do not ask about minor visual values that upstream `frontend-design` and project tokens can decide.
