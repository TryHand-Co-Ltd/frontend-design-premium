# UX Contract

> Keep this file only when the project needs a durable cross-screen contract. Replace examples with real product decisions.
>
> **Read-only review:** When performing a read-only contract audit, report gaps without creating or modifying this file. Identify missing source references or untraced UI consequences in the audit output, not by editing the contract.

## Product context

- Audience:
- Primary jobs:
- Target market(s):
- Active locales:
- Language/content register and native-review policy:
- Timezone/calendar policy:
- Accessibility target: WCAG 2.2 AA

## Business-context sources

Record the authoritative sources that ground the UI behavior in this contract. Do **not** copy business policy into this file; reference the maintained source instead.

| Domain / scope | Authoritative source | Source type | Reviewed date |
|---|---|---|---|
| Permission model | _path / ADR number_ | ADR / Permission policy | |
| Data lifecycle | _path / API contract_ | API / Domain spec | |
| Deletion / retention | _path_ | Privacy policy / ADR | |
| Billing / payment | _path_ | Billing spec | |
| Legal / regulatory copy | _path_ | Product brief / Legal review | |
| Market / content conventions | _research path / style guide_ | User research / Content guide | |

## Visual contract

- Project `DESIGN.md`:
- Token ownership model (`DESIGN.md` generated / existing runtime canonical):
- Runtime design-system/token source:
- Mapping/export/adapters:
- Token drift gate:
- Supported themes:
- Design-context owner/review policy:

Keep visual rationale and token values in `DESIGN.md`; do not duplicate them here.

## Canonical UI Map

Complete only applicable rows. An unresolved owner blocks implementation for that capability. Native/typed variants are valid only when product ownership is explicitly accepted.

| Capability | Canonical owner | Source of truth | Allowed variants | Verification |
|---|---|---|---|---|
| Table Selection | | | page / all-results | component + E2E |
| Select/Listbox | | | native / authored | keyboard + popup |
| Date | | | typed / native / authored | locale + keyboard + E2E |
| Form | | | create / edit | validation E2E |
| Scrollbar | | | geometry exceptions | computed style |
| Toast | | | success / warning / info / error | live-region test |
| CRUD | | | return / stay | full-flow E2E |

## Component behavior

| Component | Default | Hover | Focus | Active | Disabled | Busy | Error |
|---|---|---|---|---|---|---|---|
| Button | | | | | | | |
| Icon button | | | | | | | |
| Input | | | | n/a | | | |
| Secret input | masked | | | | | | |
| Search | clear + debounce | | | | | | |
| Textarea | resize none | | | | | | |
| Table/list | | | | | | | |

## Dataset navigation

- Admin tables:
- Exploratory lists:
- URL state:
- Page size:
- Empty/no-results/error/loading treatment:
- Back/scroll restoration:
- Selection scope (page / all-results), selected count, filter/sort/paging behavior, keyboard operation, bulk confirmation, and post-action focus:

## Flow ledger

| Operation | Trigger | Pending | Success destination | Success feedback | Failure recovery | Focus outcome | Source ref |
|---|---|---|---|---|---|---|---|
| Create | | | | | | | |
| Edit | | | | | | | |
| Delete | | | | | | | |
| Search | | | | | | | |
| Bulk action | | | | | | | |
| Upload/background job | | | | | | | |
| Cancel/back | | | | | | | |
| Soft-delete | | | | | | | |
| Hard-delete (irreversible) | | | | | | | |

## Navigation and responsive behavior

- Route document title policy:
- Route error / 403 page behavior:
- Breadcrumb/tab/route-state policy:
- Sidebar/drawer/bottom-sheet transformation:
- Responsive table strategy:
- Truncation/full-value access:
- Focus restoration and sticky-obstruction policy:

## Overlays and feedback

- Dialog primitive:
- Destructive confirmation levels:
- Toast placement/duration/deduplication:
- Alert/banner scope and persistence:
- Tooltip delay/dismissal:
- Unsaved-changes behavior:
- Layer/z-index contract (dialog > drawer > popover > toast stacking order):

> Deletion/retention lifecycle is recorded in **Business-context sources** above, not duplicated here.

## Async and resilience

- Mutation default (pessimistic/optimistic/queued):
- Idempotency and duplicate-submit policy:
- Auto-save/draft recovery:
- Offline/read-stale/write behavior:
- Retry/backoff/timeout behavior:
- Version conflict and multi-tab behavior:
- Session expiry/re-authentication:
- Long-running progress and return path:
- Stale-request cancellation/invalidation and pending-state ownership:
- Dialog/form preservation and retry after mutation failure:

## Validation

- Schema/validation layer:
- Trigger timing:
- Error summary/inline policy:
- Server error mapping:
- Sensitive-value handling:
- `noValidate`, first-invalid focus, duplicate-submit prevention, unsaved changes, and submit recovery:

## Permission and clipboard

- Permission UI strategy (hide vs disable vs 403 page):
- Clipboard copy policy (truncated preview + copy button, no secret in toast):
- Disabled-state explanation (tooltip with reason):

> Permission/role policy is recorded in **Business-context sources** above. This section records only the UI consequences (hide vs disable, accessible explanation, clipboard access).

## Migration status (only for an inconsistent established product)

- Migration ledger location:
- Canonical primitives and owners:
- Current risk-prioritized slices:
- Legacy import/token enforcement:
- Rollout/rollback and removal gates:

## Verification

- Required static commands:
- Browser/device/locale/theme matrix:
- Accessibility checks:
- Native-language/domain review and target-user evidence:
- Japan readiness matrix (IME, mixed scripts, normalization, long names/addresses, visual regression), when applicable:
- Component-state/visual regression coverage:
- Canonical sibling flow used for comparison:
- Project audit command/result:
- CRUD full-flow evidence:
- Failure-path evidence:
