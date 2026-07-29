# Async Resilience and System Feedback

Read this reference for remote mutations, background work, connectivity changes, multi-tab or multi-user data, sessions, progress, notifications, and recovery. Do not imply certainty the system does not have.

## Mutation strategy

Classify each mutation before choosing feedback:

- **Pessimistic:** wait for server confirmation before committing UI. Default for financial, security, permission, destructive, inventory-sensitive, or externally visible effects.
- **Optimistic:** update immediately only when success is highly likely, the operation is idempotent or deduplicated, rollback is understandable, and conflicts can be reconciled.
- **Queued:** accept locally for later sync only when storage, ordering, identity, expiry, and user expectations are explicitly designed.

A disabled button and spinner alone do not define correctness. Prevent duplicate activation, attach an idempotency key when the API supports it, and keep late responses from overwriting newer state.

## Optimistic updates

- Mark optimistic data as pending without making routine use visually noisy.
- Preserve the previous canonical value and enough context to roll back exactly.
- On failure, restore or reconcile state, explain what was not saved, and provide retry when safe.
- If related data has changed, refetch authoritative state rather than replaying a stale snapshot.
- Do not show a success toast before the system has earned the claim. Use neutral pending/saved language accurately.
- Undo is not a substitute for server failure handling; it is a separate user-initiated inverse action.

## Auto-save and draft recovery

Define what is saved, where, how often, and for how long.

- Separate local draft, syncing, saved, offline/queued, conflict, and failed states.
- Debounce routine field changes, flush safely on explicit navigation when possible, and never save while IME composition is active.
- Do not auto-save incomplete destructive/permission changes that require an explicit commit.
- Persist sensitive data only after a security review. Scope local drafts by user/account/resource and expire them.
- On return after interruption, explain that a draft exists and let users restore or discard it; never silently replace newer server data.
- “Saved” means server-confirmed or explicitly labeled local-only. Avoid timestamps that imply stronger durability than exists.

## Offline and degraded connectivity

Browser online/offline signals are hints, not proof that the application server is reachable.

- Detect failures from real requests and show one stable connectivity/degraded banner instead of repeated toasts.
- Preserve readable cached/stale content and label its freshness when decisions depend on recency.
- For blocked mutations, keep user input and offer retry. Queue writes only when conflict, ordering, authentication, and storage behavior are designed.
- On reconnect, revalidate authoritative data before claiming synchronization.
- Avoid infinite retries. Use bounded exponential backoff with cancellation and an explicit Retry path where appropriate.
- Distinguish offline, timeout, server unavailable, permission failure, and validation failure; recovery differs.

## Concurrency, stale data, and multi-tab use

- Use version/ETag/update timestamp contracts where available. Do not overwrite a newer record silently.
- On conflict, show what changed and offer reload, compare/merge, copy my edits, or force overwrite only when permissions and risk allow.
- Broadcast logout, role changes, and critical local mutations across tabs when the architecture supports it.
- Revalidate after tab visibility returns for time-sensitive data, without unexpectedly discarding in-progress input.
- Leader-election or single-tab ownership is required for jobs that must not run once per open tab.
- Presence indicators are advisory unless backed by a reliable lease/heartbeat; do not imply exclusive editing from a stale dot.

## Session expiry and authorization changes

- Warn before expiry only when the product can accurately extend or renew the session.
- Preserve non-sensitive drafts through re-authentication and return users to the interrupted task.
- A 401 should trigger the approved re-auth flow; a 403 should explain the access boundary. Do not loop retries or expose hidden data.
- If permissions change while a dialog/form is open, stop the mutation, retain safe input, refresh capabilities, and explain the next step.
- Remove or disable unavailable actions according to product policy, but never rely on UI hiding as authorization.

## Progress indicators

Choose semantics from the underlying work:

- **Determinate progress:** total work is known and measurement is meaningful. Expose current value, total/max, label, and completion.
- **Indeterminate progress:** work is active but cannot be measured. Do not show a fake percentage.
- **Meter:** display a known value in a range, not task progress.
- **Multi-stage job:** show named stages and current stage when percentage would mislead.

Avoid flashing progress for sub-threshold work. Long operations need elapsed context, cancel when supported, timeout/recovery, and a way to leave and return if the server continues the job. Completion announcements must not steal focus.

## Alerts, banners, and system notices

- Inline alert: scoped to the field, form, panel, or action that needs correction.
- Page banner: persistent condition affecting the current page, such as degraded data or permission limitation.
- Global banner: rare application-wide condition such as outage, maintenance, or session risk.
- Toast: transient acknowledgement, never the only home for a critical or actionable condition.

Use semantic tone, icon/text beyond color, concise consequence, and a recovery action. Alerts should not auto-dismiss while still true. Dismissal persistence must match scope and version of the notice. Reserve assertive live announcements for genuinely urgent interruption.

## Notification badges and counts

- A badge summarizes status; the destination contains the actual information.
- Provide an accessible name such as “Notifications, 12 unread”; do not announce every background count tick.
- Define zero behavior and an overflow representation such as `99+` without changing control width.
- Updating a count must not reorder navigation or animate perpetually. Respect reduced motion.
- Mark-as-read requires a clear product rule: viewed list, opened item, explicit action, or server acknowledgement.

## Activity timeline and audit log

- Order events consistently and label timezone; distinguish event time from ingestion/display time.
- Each item states actor, action, object, outcome, and relevant metadata in readable text.
- Grouping by date or session must not hide exact timestamps required for audit.
- Use semantic lists/headings; connector lines and avatars are decorative support, not the only source of sequence or actor identity.
- Paginate large audit logs and expose filters/export only when authorization permits.
- Immutable audit records must not appear editable. Corrections are new events, not silent rewrites.

## Avatar and presence

- Provide resilient fallback initials/icon with deterministic color and an accessible text identity nearby or in the control name.
- Treat status dots as supplemental; include text for online/away/busy when it affects decisions.
- Define stale/offline timeout and privacy policy. Do not expose presence where users have not consented or business rules forbid it.
- Images reserve dimensions, handle loading/error, and avoid layout shift.

## Retry and uncertain completion

When a request times out after reaching the server, the outcome may be unknown.

- Do not tell users an action failed if it may have completed.
- Check operation status or refetch before allowing a duplicate high-impact mutation.
- Retry automatically only for safe/idempotent operations and transient failures.
- Include a support/request ID for unresolved server errors when available, while keeping raw internals out of user copy.
