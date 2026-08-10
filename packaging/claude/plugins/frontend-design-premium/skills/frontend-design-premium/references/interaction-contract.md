# Production Interaction Contract

Use the sections relevant to the components being changed. This reference expands the foundational invariants in `SKILL.md`; project conventions may refine visuals but should not weaken behavior. For composite/advanced controls also read `data-entry-patterns.md`; for navigation/responsive shells read `navigation-layout.md`; for offline, optimistic, session, conflict, and system feedback read `async-resilience.md`.

## Interactive controls

For every control verify:

- semantic element/role matches action versus navigation;
- visible label or accessible name;
- default, hover, focus-visible, active/pressed, disabled, and busy states;
- keyboard and touch equivalence;
- practical target size (WCAG minimum 24×24 CSS px; prefer about 44×44 for important touch controls);
- focused content is not obscured by sticky UI, sheets, or virtual keyboards;
- no color-only state communication;
- no layout shift between states.

A card/row that navigates should normally contain a real stretched link. Avoid nested interactive elements inside one giant click handler. If row actions exist, ensure activating them does not also trigger row navigation.

Use `cursor: pointer` on enabled authored click targets. Use a non-interactive cursor for disabled controls; cursor styling never replaces semantics or state styling.

## Button system

Combine intent and emphasis rather than inventing unrelated variants:

| Intent | Typical use | Default emphasis guidance |
|---|---|---|
| Brand/primary | Main safe page action | Solid |
| Neutral | Cancel, secondary, utility | Outline or ghost |
| Success | Explicit positive completion when semantically meaningful | Solid/outline based on hierarchy |
| Warning | Risky but recoverable continuation | Outline or solid in focused warning context |
| Info | Informational utility | Outline/ghost |
| Danger | Delete, revoke, irreversible action | Ghost/outline in normal UI; solid in confirmation |

Requirements:

- use specific verbs; avoid generic `OK`, `Submit`, or `Done` when the action can be named;
- keep one clear primary action per decision area;
- separate dangerous actions spatially from benign frequent actions;
- spinner/progress and label occupy reserved dimensions;
- disabled is not the only pending signal—expose busy state;
- icon-only buttons have localized accessible names and, when useful, tooltips.

## Tables and data lists

### Semantics

- Use `<table>`, `<caption>` or an external accessible name, `<thead>`, `<tbody>`, `<th scope>`, and real buttons for sorting.
- Use `aria-sort` only on the active sorted header.
- Use ARIA `grid` only when implementing the full composite keyboard model is justified.
- For virtualized/partial DOM datasets, expose total/index metadata where needed and test assistive technology behavior.

### Dataset controls

- Expose current range and total when known.
- Label pagination navigation and mark the current page.
- Give pagination targets sufficient size/spacing.
- Keep page size choices limited and persist a user choice when appropriate.
- Disable previous/next at actual boundaries without removing them and shifting layout.
- For cursor APIs, do not fake arbitrary page numbers unless the backend supports stable random access.
- Load-more preserves current items and appends once; guard double activation.
- Infinite scroll needs an accessible/manual alternative, loading announcement, state restoration, and virtualization for large DOMs.

### Viewport-sized table regions and scroll ownership

Treat “make the table sync with the screen” as a table-surface requirement, not a page-shell rewrite.

- Name one vertical scroll owner for each active layout mode. A bounded table panel may own an internal `overflow: auto` region; a sibling long form normally keeps natural block height and document scrolling.
- End the table's `display: flex` / `min-height: 0` chain at the table panel or a table-specific wrapper. Do not add `100vh`, `h-dvh`, fixed height, or `overflow: hidden` to a shared page, shared tab shell, or route ancestor solely to size the table.
- If the application already has a canonical viewport shell and content scroller, preserve it. Let the form content remain natural-height inside that established scroller; do not create a second nested form scroller.
- Keep table toolbar and pagination in the table frame while the row viewport scrolls. Changing page size may change scroll height, never the frame footprint.
- On tab switches, reset panel-specific height and overflow rules. An inactive table panel must not leave clipping or fixed-height constraints on the active form panel.
- At short viewports and 200% zoom, every form field, validation message, and action must remain reachable. Sticky form actions may remain sticky, but they do not make the form body fixed.

### Row states and actions

- Keep row height stable during loading and inline actions.
- Provide selection count and bulk-action scope.
- Confirm dangerous bulk actions with exact count and consequence.
- After a row mutation, announce outcome and put focus in a logical surviving location.
- Distinguish empty dataset from no filter/search results. The latter offers clear/reset filters.
- Keep horizontal overflow obvious on narrow screens; do not clip columns silently. Choose scroll, priority columns, stacked records, or detail navigation using `navigation-layout.md`.

### Table enhancements (admin & data-heavy apps)

**Sticky header:**
- Pin the table header on vertical scroll so column labels stay visible. Use `position: sticky; top: <header-height>` on `<thead>`.
- The sticky header must inherit the table/surface background to avoid transparency overlap with scrolling rows.
- Only the header row sticks — do not pin individual column cells below the header.

**Column freeze / sticky columns:**
- Freeze identifier columns (name, ID, checkbox) on horizontal scroll so the row identity stays visible.
- Use `position: sticky; left: <offset>` on the leftmost 1–2 columns. Set an explicit `z-index` higher than normal cells to layer above scrolling columns.
- Clearly communicate which columns are frozen through visual separation (right border on the last frozen column, slightly different background).
- Do not freeze columns on touch-dominant interfaces — scroll inertia conflicts with sticky positioning.

**Sort single vs multi:**
- Default to single-column sort. Shift-click enables multi-column sort.
- Annotate sort direction with a visible arrow (▲/▼) on the active column header.
- For multi-column sort, show the sort order index (1, 2, 3) next to the direction arrow.
- Persist sort state in URL when the table is the page's primary content.

**Column visibility persistence:**
- Offer a column visibility toggle when the table has 8+ columns.
- Persist user choices to localStorage or user preferences API — not to the backend except when preference sync across devices is a product requirement.
- Show the toggle as a dropdown or sheet, not a separate settings page.
- The toggle label reads "Columns" and lists each column with a checkbox.

## Search field

Structure:

- visible label or programmatic name;
- search icon if useful but not as the only label;
- custom clear button shown when non-empty;
- loading indicator in a reserved adornment slot;
- result count/status region.

Behavior:

1. Update visible input immediately.
2. Suppress remote dispatch during IME composition.
3. Debounce the committed query (300 ms default).
4. Cancel the prior request with framework cancellation/`AbortController`, or compare request IDs before committing.
5. Clear immediately, cancel pending work, reset results, and refocus input.
6. Explicit Enter may bypass debounce only when it is not an IME commit.
7. Reset/clamp pagination when query/filter semantics change.

Test slow response ordering: type query A, then B; A must never overwrite B.

## Forms and validation

- Add `novalidate`/`noValidate` to product forms to suppress browser-owned message bubbles.
- Keep correct `type`, `inputmode`, `autocomplete`, `required`, and length/format metadata when useful; app/schema validation remains source of UI truth.
- Validate at a humane time: usually submit, then on change/blur for fields already in error. Avoid shouting during initial typing.
- On invalid submit, show a summary for long forms, inline text for each field, associate via `aria-describedby`, set invalid state, and focus/scroll the first error.
- Preserve non-sensitive entered data after server errors.
- Map server field errors to fields and global failures to persistent form-level status.
- Prevent double submit and stale mutation completion after unmount/navigation.
- Do not use placeholder as the only label.

### Textarea

Set `resize: none`. Provide enough rows and either auto-grow within a sensible cap or an expansion affordance for expected long input. Preserve scrolling and keyboard access when capped.

### Password/secret/key

- Mask by default with `type="password"` where appropriate.
- Reveal through a real button, not pointer-down-only behavior.
- Toggle accessible name between localized “Show …” and “Hide …”; expose pressed state if the component model uses a toggle button.
- Preserve value, caret, focus, validation, and autofill behavior across toggles.
- Use `current-password` for an existing login credential and `new-password` for creation/reset. Treat API keys/tokens according to product security and password-manager policy.
- Do not expose the value in DOM attributes beyond the control value, telemetry, error copy, toast, route, clipboard without intent, or persistent storage without threat review.
- Clear revealed state on remount/navigation; consider auto-remasking after inactivity only if it does not create confusing edits.

### Sticky form actions (long forms)

- When a form is taller than the viewport, keep the primary action bar (Save/Cancel) accessible without scrolling back to the bottom.
- Stick the action bar to the bottom of the viewport on scroll using `position: sticky; bottom: 0` or `fixed` positioning with padding for the footer.
- The sticky bar should have a background to avoid content transparency. Do not use `pointer-events: none` or overlay traps.
- For mobile, keep the bar attached to the bottom of the form (not the viewport) so it does not cover content when the keyboard is open. Detect `visualViewport` height changes to toggle between sticky and static.
- On validation error, scroll to the first invalid field — the sticky bar remains visible.
- Keep the form body in natural flow. Scope any bounded scrolling to the application's established content scroller; never inherit the table panel's fixed-height or `overflow: hidden` contract.

### Unsaved changes guard

- Warn before the user navigates away from a dirty form. Use an app-owned dialog for in-app navigation (router events) and `beforeunload` for actual page/tab close.
- The dialog says: "You have unsaved changes. Discard them?" with actions "Keep editing" (default focus) and "Discard".
- Use a narrow `beforeunload` handler only — set `e.returnValue = ''` and return a string for legacy browsers. Do not show a product dialog on browser close.
- Mark the form dirty on any field change after initial load. Reset dirty state on successful save.
- In-app navigation (router-level) guard: use the framework's navigation guard (Next.js `router.events`, React Router `unstable_useBlocker`, or similar).
- Do not block navigation when the form has no unsaved changes.

## Dialog and alert dialog

Use a proven accessible primitive when available.

Required behavior:

- accessible name and optional concise description;
- focus moves inside on open;
- Tab/Shift+Tab remain within a modal;
- background is actually inert when marked modal;
- Escape and explicit Cancel close when cancellation is allowed;
- focus returns to the trigger or next logical context;
- scroll lock does not change page width;
- nested dialogs are avoided;
- mobile layout remains usable with keyboard and zoom.

For destructive confirmation:

- title names the action;
- body names object, scope, side effects, and recoverability;
- confirm button uses the **destructive verb** and **destructive visual intent** (`danger`/`destructive` variant), never a neutral color;
- least destructive action (Cancel) receives initial focus for serious consequences;
- mutation pending stays inside the dialog and blocks duplicate confirmation — **do not close the dialog before the async operation completes**;
- error remains in the dialog with retry/cancel path;
- success closes dialog and updates/focuses the parent context.

Never substitute browser `alert`, `confirm`, or `prompt`.

## Soft-delete, archive, and restore

Prefer reversible removal when the product can support it. Document the policy in `UX-CONTRACT.md` (`Soft-delete vs hard-delete policy`).

### Soft-delete / archive

- Soft-delete marks a record inactive (or archived) without destroying it. Archive is the same pattern when the product vocabulary prefers “Archive” over “Delete”.
- Confirm with an app-owned dialog. Body must say the action is **reversible** (and for how long, if retention is limited) and what the user will see afterward (hidden from default lists, retained in audit/trash).
- Confirm button uses a clear verb: `Archive`, `Move to trash`, or `Deactivate` — not a generic `OK`. Prefer **warning** intent when reversible; reserve high-emphasis **danger** for irreversible hard-delete.
- On success: remove or restyle the row in the current list, clamp/reset paging if the page becomes empty, announce via toast with an **Undo** / **Restore** action when technically honest, and keep focus in a sensible next target.
- Filtered “Active only” lists must not strand the user on an empty out-of-range page after soft-delete.

### Restore

- Expose restore from trash/archive views and, when offered, from the success toast Undo window.
- Restore returns the record to its prior active state, reappears in the owning list with the same identity, and announces success without requiring a second confirmation for routine restores.
- If restore is blocked (retention expired, dependency missing, permission), explain why in-page — do not fail silently.

### Hard-delete

- Use only when the business requires permanent destruction (compliance wipe, explicit "Delete forever", or no recoverable store).
- Confirm with danger intent; name the object and state that recovery is impossible. Typed confirmation only for rare, high-impact irreversible operations.
- Do not offer Undo for a hard-delete that the API cannot reverse.
- After success: update the list, clamp paging, toast acknowledgment, and keep audit/activity trails consistent with product policy.

### Intent axis — DO NOT flatten

Do NOT use the same destructive button variant (e.g., red `bg-red-600`) for **both** soft-delete/restore and hard-delete. The visual distinction communicates severity:

| Action | Button variant | Example verb |
|--------|---------------|-------------|
| Soft-delete / archive / deactivate | **Warning** (amber, orange) or outline | `Deactivate`, `Archive`, `Move to trash` |
| Hard-delete / destroy | **Danger** (red) | `Delete forever`, `Permanently delete` |
| Restore | **Default** (primary) or outline | `Restore`, `Undo` |

Using danger red for every confirm dialog desensitises users and increases the chance of accidental permanent deletion. A soft-delete confirmation should look different from a hard-delete confirmation.

### Consistency

- The same entity type uses the same delete class (soft vs hard) everywhere unless an explicit business variant is named in the UX contract.
- Row actions, bulk actions, and detail-page actions share labels, confirmation strength, and post-success navigation/feedback.

## Toasts, status, errors, and empty states

### Toast/status

- One shared viewport/queue and placement.
- `status`/polite announcements for routine completion; assertive alert only for urgent interruption.
- Deduplicate repeats and avoid stacking floods.
- Pause dismissal on hover/focus if users need time; critical content remains elsewhere.
- Keep Undo available long enough and ensure it truly restores state.
- Never put secrets or raw backend errors in a toast.

### Empty states

- **Empty dataset:** explain what belongs here and provide the primary create/import action when allowed.
- **No results:** state no match and provide clear/reset filters.
- **No permission:** explain access boundary without implying no data exists.
- **Failure:** state what failed and provide retry/recovery.

Keep the component footprint stable when moving among these states.

## Tooltips and popovers

- Tooltips supplement; they do not contain essential instructions or interactive controls.
- Open on both hover and keyboard focus after a small consistent delay.
- Keep open while pointer is over trigger or tooltip; dismiss with Escape.
- Associate as a description and keep focus on the trigger.
- Interactive hover content is a popover/non-modal dialog, not a tooltip.
- Do not depend on the HTML `title` attribute as the product tooltip system.

## Scroll containers

- Establish the product's global scrollbar baseline once in the application stylesheet. Every new scroll container in that application document receives the theme without a per-container opt-in class.
- Scope the global baseline to surfaces the product owns. Do not attempt to style browser chrome, cross-origin frames, or embedded third-party documents.
- Define tokenized thumb/track, hover/active, and dark/light/high-contrast/forced-colors behavior. In forced colors, allow the platform to preserve system contrast when required.
- Use a component-level scrollbar class only for a documented geometry or semantic exception such as stable gutter, compact density, or an intentionally distinct surface—not to activate the base colors.
- Keep enough width and contrast to perceive and operate; never set `scrollbar-width: none` for scrollable content without an equivalent visible control.
- Use `scrollbar-color`/`scrollbar-width` and compatible `::-webkit-scrollbar*` styling as required by browser support.
- Use `scrollbar-gutter: stable` for classic-scrollbar layout stability.
- Keep keyboard scrolling, touch momentum, and visible overflow cues.

## Transitions and motion patterns

Coordinate transition behavior across screens so the product feels intentional rather than animated incidentally.

### Design principles for motion

- **Motion must have a reason.** Every transition should communicate a state change, spatial relationship, or hierarchy — never decoration.
- **Duration over speed.** Prefer 200–300 ms for most micro-interactions; reserve 300–500 ms for page/route transitions. Below 100 ms feels instantaneous (no feedback), above 500 ms feels slow.
- **Easing tells the story.** Use `ease-out` for exits (fast start, slow end — content leaves decisively), `ease-in-out` for property changes (neutral), and `ease-out` with slight cubic-bezier for entrances (natural, non-mechanical). Avoid `linear` for anything other than color/opacity.
- **Reduced motion is not optional.** Every animated interaction must degrade gracefully under `prefers-reduced-motion: reduce`. Skip enter/exit animations entirely or use opacity-only fades at greatly reduced duration.
- **One orchestrated moment > scatter.** A single well-timed page-load sequence (staggered reveal with 50–100 ms delay between items) creates more perceived polish than 12 independent micro-animations.

### Page and route transitions

| Surface type | Recommended treatment | Rationale |
|---|---|---|
| Same-app SPA navigation | Staggered content fade-in (200 ms, `ease-out`) with skeleton placeholders preserving geometry | Content arrives incrementally; no layout shift |
| Full page reload / MPA | Browser-native load, no custom overlay | Custom load screens add latency to perceived performance and break browser UI expectations |
| Wizard / multi-step form | Slide content horizontally (250 ms, cubic-bezier) only when direction has meaning; otherwise opacity cross-fade | Directional slide communicates forward/backward progress but can feel busy in a tool context |
| Modal / dialog | See Dialog section below | — |
| Tab panel switch | Immediate content swap with optional 150 ms opacity cross-fade for same-viewport panels | Tabs are a selection, not a navigation; animation should not delay reading |

Implementation heuristics:

```tsx
// Staggered list entrance — use only on initial page load, not on every render
<motion.div
  initial={{ opacity: 0, y: 12 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ delay: index * 0.05, duration: 0.2, ease: "easeOut" }}
>

// Respect reduced motion: skip transform, keep opacity
@media (prefers-reduced-motion: reduce) {
  .stagger-item {
    opacity: 1 !important;
    transform: none !important;
  }
}
```

### Dialog and modal animations

- **Open:** Scale (1.05 → 1) + opacity (0 → 1) with a spring or 250 ms `ease-out`. Overlay fades in simultaneously (200 ms).
- **Close:** Opacity (1 → 0) with a faster 150–200 ms `ease-out`, no scale transform. Overlay fades out with the same duration.
- **Reduced motion:** Opacity-only, 100 ms. Remove scale transform entirely.
- **Content changes inside an open dialog** (loading, error, success): transition via opacity cross-fade (150 ms), not slide or scale. The dialog frame itself stays stable.
- **Multiple dialogs:** Avoid nesting. When unavoidable, animate the newer dialog independently without re-animating the overlay.

```tsx
// Open — spring entrance
const openTransition = {
  type: "spring",
  damping: 25,
  stiffness: 300,
};

// Close — quick exit, no spring
const closeTransition = {
  duration: 0.15,
  ease: "easeOut",
};
```

### List item appear and remove

| Action | Animation | Notes |
|--------|-----------|-------|
| Item inserted (known position) | Opacity 0→1 + subtle translateY (10px → 0), 200 ms | Do not re-animate the entire list; only the new item |
| Item inserted (prepend/append, unknown order) | Opacity fade only, 150 ms | Prevents jarring displacement |
| Item removed | Opacity 1→0 + height collapse, 200 ms | Collapse height after opacity hits 0 to avoid empty white space |
| Reorder | Opacity-only cross-fade at target position, 150 ms | Drag reorder uses the drag library’s own FLIP animation; avoid double-animating |
| Batch remove (bulk action) | Dim items first (200 ms), then remove with staggered opacity fade (50 ms delay per item, max 400 ms total) | Communicates scope before action |

Use the `<AnimatePresence>` / `TransitionGroup` pattern for exit animations so removed elements do not disappear before their animation completes.

```tsx
// AnimatePresence handles unmounting elements after exit animation finishes
<AnimatePresence>
  {items.map((item) => (
    <motion.div
      key={item.id}
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, height: 0, marginBottom: 0, paddingTop: 0, paddingBottom: 0 }}
      transition={{ duration: 0.2 }}
    >
      {item.name}
    </motion.div>
  ))}
</AnimatePresence>
```

### Skeleton loading animation

| Style | Character | When to use |
|-------|-----------|------------|
| **Pulse** | Opacity oscillates between ~0.3 and 1 over 1.5–2 s | Default for most surfaces. Less visually dominant than shimmer. |
| **Shimmer** | A linear-gradient highlight sweeps across the skeleton shape over 1.5–2 s | High-density data surfaces (tables, card grids) where pulse makes too many elements blink simultaneously. |
| **No animation** | Static skeleton with correct geometry | Reduced motion; content that arrives predictably (server-rendered shell). |

**Critical rule:** The skeleton must match the final layout geometry exactly — same aspect ratio, same border radius, same text line count, same spacing. Layout shift when content replaces skeleton is a CLS failure.

```css
/* Pulse — simple, low cognitive load */
.skeleton-pulse {
  animation: skeleton-pulse 1.5s ease-in-out infinite;
  background-color: var(--color-muted);
  border-radius: var(--radius-md);
}
@keyframes skeleton-pulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

/* Shimmer — use only for dense lists/tables */
.skeleton-shimmer {
  background: linear-gradient(
    90deg,
    var(--color-muted) 25%,
    var(--color-muted-foreground) 37%,
    var(--color-muted) 63%
  );
  background-size: 400% 100%;
  animation: skeleton-shimmer 1.5s linear infinite;
}
@keyframes skeleton-shimmer {
  0% { background-position: 100% 50%; }
  100% { background-position: 0 50%; }
}
```

### Reduced motion enforcement

- Test every animated component with `prefers-reduced-motion: reduce` enabled.
- Replace all motion-based transitions with opacity-only fades at ≤100 ms.
- Disable staggered entrance delays — content appears immediately.
- Disable FLIP/reorder animations — items appear at target position instantly.
- Do not disable skeleton animations entirely; keep pulse at greatly reduced opacity range (0.5 → 0.7) so loading state remains visible.

## Stable layout and async work

Reserve geometry for:

- images/video via dimensions or `aspect-ratio`;
- skeletons that match final rows/cards;
- field help/error slots where practical;
- adornments, spinners, and validation icons;
- scrollbar gutters;
- sticky headers and safe-area insets;
- late-loaded fonts with metric-compatible fallbacks or an appropriate font-display strategy.

Async rules:

- distinguish initial load, refresh, pagination, and mutation;
- keep usable stale content during background refresh;
- cancel or ignore stale work;
- make progress perceivable without flashing for sub-threshold waits;
- preserve controls and scroll position;
- provide retry and avoid infinite spinner states.

## Responsive and input diversity

Test at minimum:

- keyboard only;
- touch/no hover;
- 200% zoom or equivalent reflow;
- narrow phone and small laptop;
- long localized text and large dynamic values;
- reduced motion and high contrast where supported;
- slow network, offline/failure, empty and large datasets;
- session expiry, stale/conflicting data, and long localized values when applicable.
