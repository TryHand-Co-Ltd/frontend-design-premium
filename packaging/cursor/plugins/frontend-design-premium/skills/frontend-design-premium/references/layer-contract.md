# Layer and Z-Index Contract

Read this when combining multiple overlay elements: dialogs, drawers, toasts, tooltips, popovers, selects, command palettes, and floating buttons. Every overlay needs a predictable stack order, focus management, and interaction isolation.

## Stacking order

Define a global z-index scale. Every overlay type gets one slot; never use arbitrary z-index values.

```
Layer         Z-index range    Examples
─────────────────────────────────────────────
Base content  0–99             Page content, headers, sidebars
Sticky UI     100–199          Sticky headers, sticky form bars
Dropdown      200–299          Select dropdown, combobox list, autocomplete
Popover       300–399          Tooltip, popover, date picker
Header/Footer 400–499          App header (with dropdowns), mobile nav
Backdrop      500–599          Dialog/drawer backdrop overlay
Dialog        600–699          Modal dialog, alert dialog, full-screen takeover
Sheet/Drawer  700–799          Side panel, slide-in drawer
Command       800–899          Command palette, search modal
Toast         900–999          Toast/sonner notifications (always top)
```

### Rules

- Use a single CSS custom property per layer, not raw numbers:
  ```css
  --z-dropdown: 200;
  --z-dialog: 600;
  --z-toast: 900;
  ```
- Never use `z-index: 9999` or `z-index: 2147483647`. If a component needs to go above its natural layer, re-examine the stacking context.
- Each overlay creates its own **stacking context** via `position: relative`, `isolation: isolate`, `transform`, `filter`, or `will-change`. Be aware that a child of a `transform`-based animation may have a limited z-index scope.
- `position: fixed` overlays (toast, command palette) stack relative to the viewport, not a parent context — this is correct for global overlays.

## Dialog behavior

- **Backdrop:** Covers the viewport behind the dialog. `position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: var(--z-backdrop)`. Click on backdrop closes the dialog unless the action is destructive or data-lossy.
- **Dialog surface:** Centers in viewport. `position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: var(--z-dialog)`.
- **Focus trap:** When the dialog opens, focus moves to the first focusable element or the dialog itself. Tab/Shift+Tab cycles within the dialog. On close, focus returns to the trigger element.
- **Escape:** Closes the dialog. On destructive dialogs, Escape is equivalent to Cancel (not Confirm).
- **Inert background:** Use `aria-hidden` or [`inert`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/inert) on the background content while the dialog is open to prevent accidental interaction.
- **Responsive bounds:** Keep the surface within the visual viewport and safe-area insets. Long content scrolls inside the body while the title and actions remain reachable; the virtual keyboard must not cover the active field or required action.

```tsx
// Dialog z-index via CSS variable
<Dialog open={open} onOpenChange={setOpen}>
  <div className="fixed inset-0 bg-black/50" style={{ zIndex: 'var(--z-backdrop)' }} />
  <div
    className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-xl bg-card p-6 shadow-xl"
    style={{ zIndex: 'var(--z-dialog)' }}
    role="dialog"
    aria-modal="true"
    aria-labelledby="dialog-title"
  >
    {children}
  </div>
</Dialog>
```

## Drawer / Sheet behavior

- **Ownership:** Declare the drawer modal or non-modal. Modal drawers use a backdrop, inert background, focus trap, Escape, and focus restoration. Persistent/non-modal drawers omit modal semantics and follow a documented canonical focus/navigation variant.
- **Slide direction:** From the right for details/operations; from the left for navigation on mobile.
- **Width:** 400px–480px as a content standard; full-width on mobile (< 768px).
- **Stacking:** Drawer sits at `z-index: var(--z-sheet)`, below dialog but above popover. If a dialog opens from within a drawer, the dialog appears above the drawer.
- **Backdrop:** Required for modal drawers; optional/absent for a documented persistent non-modal drawer.
- **Escape:** Closes a dismissible drawer; a persistent variant documents its close/navigation affordance.
- **Focus:** Modal drawers trap focus and restore it on close. Non-modal drawers preserve normal document focus order unless their canonical contract defines another accessible model.

## Toast / Notification behavior

- **Stacking:** Always topmost (`z-index: var(--z-toast)`). Toasts must never be obscured by dialogs, drawers, or the command palette.
- **Placement:** Fixed position, typically `top-right` or `bottom-right`. Use one placement across the entire app.
- **Deduplication:** Identical toasts within a short window (2s) replace, not stack. A "Analysis saved" toast that fires twice in 1s should show once.
- **Duration:** Informational toasts auto-dismiss after 4–6s. Error toasts persist until dismissed. Destructive-action confirmations persist until dismissed.
- **Pause on hover:** Auto-dismiss pauses when the user's pointer is over the toast.
- **Stack limit:** Maximum 3–5 visible toasts. Older toasts are pushed out or collapsed.
- **Accessibility:** `role="status"` or `role="alert"` + `aria-live="polite"`.

## Command palette (Cmd+K)

- **Stacking:** `z-index: var(--z-command)` — above dialogs but below toasts.
- **Trigger:** `metaKey + k` (or `ctrl + k`). Must be preventable when an input is focused.
- **Backdrop:** Optional semi-transparent backdrop. Click or Escape closes.
- **Focus:** On open, focus moves to the search input. On close, return to the trigger element.

## Tooltip and popover behavior

- **Stacking:** `z-index: var(--z-popover)` — above dropdowns but below dialogs.
- **Dismiss:** Tooltips dismiss on Escape or when the trigger loses hover/focus. Popovers dismiss on Escape, click outside, or scroll.
- **Placement:** Auto-flip to stay within the viewport. Do not overflow or clip.
- **Delay:** Show after 300ms hover (tooltip) or immediately (popover). Hide after 100ms.

## Select / Combobox dropdown

- **Stacking:** `z-index: var(--z-dropdown)` — below popovers. Dropdowns must appear above form content but below dialogs.
- **Portal:** Render dropdowns via a portal to the document body to avoid clipping by `overflow: hidden` parents.
- **Scroll:** If the dropdown is taller than the viewport, max-height + internal scroll. The select input should scroll into view when the dropdown opens.

## Z-index conflicts

When two overlays overlap (e.g., a select dropdown inside a dialog):

1. The **innermost** overlay (dropdown inside dialog) must appear within the dialog's stacking context, but above the dialog surface.
2. Portal the innermost overlay to the document body so it can use the global z-index scale.
3. If portaling is not possible, the dialog creates a new stacking context via `isolation: isolate`, and internal overlays use `z-index` relative to within the dialog.

### Common conflict patterns

| Conflict | Resolution |
|----------|------------|
| Select dropdown clipped by dialog | Portal select popup to `document.body` |
| Toast hidden behind dialog | Ensure `--z-toast` > `--z-dialog` |
| Drawer header behind sticky header | Drawer is `position: fixed` so it overlaps everything except toasts |
| Tooltip inside scrolling container | Portal tooltip to body; use `position: fixed` |
| Date picker inside form inside modal | Portal the picker popover to body or the modal root |

## Analytics and testing

- Test overlays at narrow viewports: dialogs should not overflow, toasts should not be hidden, drawers should become full-width.
- Test with multiple overlays open: dialog + select + toast simultaneously.
- Test keyboard navigation: Tab through a dialog, open a select inside it, Tab must stay within the dialog.
- Test `prefers-reduced-motion`: all overlay entrances/exits must work with `transition: none`.
