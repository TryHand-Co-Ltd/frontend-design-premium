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
| Initial page/data load | App-owned loading indicator/spinner in a stable reserved region |
| Table page/filter change | Keep headers and container stable; show an app-owned loading indicator/overlay; prevent stale overwrite |
| Button mutation | Keep label width/height stable; busy indicator; prevent duplicate activation |
| Background refresh | Preserve usable content; subtle progress/status; do not blank the screen |
| Very fast local operation | Avoid flashing a loader; use a short threshold before showing it |

Skeleton is optional. Use it only when the prompt, business requirement, or canonical project contract explicitly asks for skeleton treatment. A spinner is acceptable by default, including for initial page and table loading, provided it reserves compatible geometry, remains perceivable, cannot become indefinite, and cannot be cleared or overwritten by stale work.

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

## Source conflict and precedence

Use the canonical source precedence table in `SKILL.md §1a` — this file does not restate it to avoid drift.

When two authoritative sources disagree or a maintained document appears stale:

1. Check the repository's own context index or contributor conventions for an explicit conflict-resolution rule.
2. Apply the §1a precedence. If the conflict crosses precedence levels, the higher-precedence source wins.
3. A stale document (verified date older than a known re-architecture) must not silently win over current code evidence, even if it has higher nominal precedence.
4. If conflict persists after applying precedence, surface it explicitly and block the affected decision branch — do not average, guess, or silently pick a winner.
5. When the conflict is resolved, record the resolution in the relevant contract (`UX-CONTRACT.md` or equivalent) with a reference to the authoritative source and the date reviewed.

## High-risk escalation — must not use defaults

Defaults in this skill are safe for ordinary UX choices. They must **not** be applied when unresolved evidence affects:

| Category | Why no default | Expected action |
|----------|---------------|----------------|
| Permissions or security | Wrong rule is a data-exposure bug | Read the permission policy / ADR; ask if ambiguous |
| Money, billing, or payment | Cost or financial liability | Read the billing spec / ADR; ask before implementing |
| Privacy, retention, or PII | Regulatory or trust failure | Read the privacy policy / contract; ask if ambiguous |
| Irreversible lifecycle changes | Hard-delete, deactivate, archive with consequences | Read the domain lifecycle / state-transition spec |
| Legal or regulatory copy | Liability from wrong wording | Read the legal brief / product spec; ask before writing |
| Non-idempotent external side effects | Double-dispatch, email, webhook, charge | Read the API contract; do not optimistically retry |
| Shared domain workflow / state transitions | Business logic error | Read the domain ADR / state machine spec |

If the authoritative source is unavailable and the decision cannot be deferred, use the available grilling/decision workflow. If neither is available, ask **one compact blocking question** that pauses only the affected decision branch. Do not fall through to generic defaults for these categories.

## Ask vs infer

Ask when the answer changes API contracts, routing, irreversible side effects, permissions, legal copy, locale/calendar/timezone meaning, conflict/offline guarantees, or user-visible workflow shared by many screens.

Infer when existing components, routes, tests, design docs, or sibling screens establish a clear convention. Do not ask about minor visual values that upstream `frontend-design` and project tokens can decide.
