# Navigation and Layout Patterns

Read the applicable sections when changing information architecture, responsive shells, navigation widgets, dense data layouts, or alternate input/output modes. Visual variants come from `DESIGN.md`; this contract defines behavior and state.

## Breadcrumbs

Use breadcrumbs only for real hierarchy, not browser history or a progress indicator.

- Render a labeled navigation landmark and an ordered list.
- Parent segments are links; the current page is plain text or a non-activating current item with `aria-current="page"`.
- Keep labels aligned with page and navigation vocabulary. Do not expose raw route identifiers.
- Use one localized separator through CSS/decorative markup so screen readers do not announce noise.
- On narrow widths, preserve the current page and nearest useful ancestor; collapse intermediate items into an accessible disclosure rather than unreadable ellipses.
- Do not make the last item a link to itself. Update breadcrumbs with route changes and restore focus at the route destination.

## Tabs

Use tabs for peer views of the same context. Use links/navigation when each destination is independently meaningful, bookmarkable, or nested.

- Use the project's proven tabs primitive and the WAI-ARIA tabs keyboard model when implementing true in-page tabs.
- Expose `tablist`, selected tab, associated `tabpanel`, and deterministic IDs.
- Arrow keys move among tabs; activation may be automatic only when panels appear without noticeable latency. Otherwise require Enter/Space.
- Keep focus and selection distinct. Disabled tabs remain rare and have an understandable reason.
- Make overflow obvious: horizontal scrolling with controls or an accessible overflow menu. Preserve the active tab in view.
- Put route-backed tab state in the URL when Back, refresh, sharing, or deep linking matters.
- The underline, pill, icon, and spacing treatment belong to `DESIGN.md`; do not invent a new visual variant per screen.
- Give each tab panel its own height and overflow contract. A viewport-bounded table panel must not force a sibling long-form panel into the same fixed-height or internal-scroll model; switching tabs must restore the active panel's intended scroll owner.

## Sidebar, navigation drawer, and mobile bottom sheet

Choose from content and task, not viewport alone:

- Persistent sidebar for frequent top-level product navigation on sufficient width.
- Collapsible rail only when icons remain understandable and every item retains an accessible name/tooltip.
- Overlay navigation drawer for narrow layouts; make the background inert, trap focus, close with Escape, and restore focus to the trigger.
- Push layouts only when the content is deliberately resized and remains usable; prevent unexpected content shifts.
- Bottom sheet for short, mobile-first choices or contextual actions. Use a full page or dialog for long forms, destructive explanations, or content that requires reliable keyboard/zoom space.

Persist a user's desktop collapse preference when useful, but do not let a stale narrow-screen state hide navigation. Mark the current route, support keyboard operation, respect safe areas, and keep critical actions reachable with the virtual keyboard open.

## Responsive tables and dense data

Do not automatically turn every table into cards. Choose a strategy from comparison needs:

1. **Horizontal scroll:** default when column relationships and row comparison matter. Freeze identifiers only when it does not create focus/overlap problems; show an overflow cue.
2. **Priority columns:** hide secondary columns behind a column chooser or row detail, never silently. Persist the choice where useful.
3. **Stacked/card representation:** use when each record can be understood independently and labels are repeated. Preserve the same actions, status, ordering, and accessible names.
4. **Dedicated detail view:** use when the dataset cannot remain comprehensible at narrow widths.

Test sticky headers/columns at zoom, with keyboard focus, long localized values, and classic scrollbars. Focused content must not be covered by sticky UI.

## Truncation and overflow

- Prefer wrapping for instructions, errors, primary labels, and values users must compare.
- Use single-line ellipsis only when row geometry matters and the full value remains available by focus/click, not hover alone.
- Use multi-line clamping only for previews; expose an explicit expand action for important content.
- Detect actual overflow before adding a tooltip. Do not show duplicate tooltips for visible text.
- Preserve access to identifiers through copy/view actions. Never truncate secrets into a value that appears safe to share.
- Localize with flexible containers rather than fixed character counts; Japanese and mixed-script text do not map cleanly to English length assumptions.

## Keyboard shortcuts and command palettes

Shortcuts are conditional enhancements, never the only route to an operation.

- Prefer platform-aware conventions and display them using the user's platform notation.
- Scope shortcuts so typing, IME composition, assistive technology, and browser/OS commands win.
- Do not bind single printable characters globally without a user-controlled mode.
- Provide discoverability near the action and in a shortcut/help surface.
- Support Escape consistently: close the topmost dismissible layer, clear a transient mode, or return focus as documented.
- Command palettes need search semantics, IME-safe input, grouped results, keyboard navigation, no-results/loading states, and focus restoration.

## Context menus

Prefer visible actions or a menu button. Add a custom context menu only when expert workflows justify it.

- Keep the native browser menu unless replacement is intentional and complete.
- Every context-menu command has a keyboard and touch-accessible alternative.
- Open from right-click and the platform context-menu key/Shift+F10 where supported.
- Position within the viewport, move focus into the menu, implement the menu keyboard model, close with Escape, and restore focus.
- Do not hide essential or destructive actions exclusively in a context menu.

## Print and alternate output

Add print treatment only for printable product workflows such as reports, invoices, records, or handouts.

- Hide navigation, transient controls, toasts, and nonessential chrome.
- Preserve titles, timestamps, filters, attribution, and URLs when they provide necessary context.
- Expand content that would otherwise be hidden behind scroll containers, tabs, or disclosures when appropriate.
- Avoid orphaned headings and clipped tables; define page breaks deliberately.
- Do not print masked secrets, private off-screen content, or interactive-only status without a textual equivalent.
- Test the actual print preview, not only `@media print` declarations.

## Document title

Every navigable route owns a clear `document.title` (or framework equivalent such as Next.js `metadata.title` / Vue `useTitle`).

- Format: `{Page} — {Product}` or the project’s established pattern; keep it stable across a session.
- Update the title on client-side route changes, including tabs that represent distinct bookmarkable views.
- Reflect meaningful context when it helps orientation (e.g. `Edit: Acme Corp — Users`), but never put secrets, tokens, or PII that should not appear in history/OS window switchers.
- Loading and error routes still set an honest title (`Loading…`, `Page not found`, `Access denied`) rather than leaving a stale previous page title.
- Titles must follow the active locale; Japanese products localize page and product segments.

Document the policy in `UX-CONTRACT.md` (`Route document title policy`).

## Route errors and 403 pages

Own failure and authorization boundaries as first-class routes, not blank screens or browser-native errors.

- **Not found (404):** Explain that the page or resource does not exist (or no longer exists). Offer navigation home/dashboard and search when available. Do not imply the user lacks permission.
- **Forbidden (403):** Explain the access boundary (“You need the Admin role”). Link to an allowed destination. Prefer 403 over 404 when the resource exists but the user cannot access it — hiding existence is a deliberate security choice, not the default UX.
- **Server/route error (5xx or render failure):** State that something went wrong, provide retry/reload, and keep chrome usable. Do not dump stack traces or raw backend payloads in production UI.
- Keep shell navigation reachable on error pages so users are not trapped.
- Match empty/error language and layout density to sibling product screens; do not invent a one-off marketing-style error page inside an admin app.
- When permission UI and routing interact, follow `references/permission-ui.md` for hide vs disable vs 403.

Document behavior in `UX-CONTRACT.md` (`Route error / 403 page behavior`).

## Focus visibility and responsive stability

- Focused controls and targets must not be entirely or partially hidden by sticky headers, bottom bars, cookie banners, sheets, or virtual keyboards.
- Use `scroll-padding`, `scroll-margin`, safe-area insets, and deliberate focus scrolling rather than arbitrary timeouts.
- Reserve persistent navigation geometry and scrollbar gutters to avoid route-to-route layout shifts.
- At 200% zoom and narrow widths, provide reflow rather than requiring two-dimensional scrolling except for content such as genuine data tables.
