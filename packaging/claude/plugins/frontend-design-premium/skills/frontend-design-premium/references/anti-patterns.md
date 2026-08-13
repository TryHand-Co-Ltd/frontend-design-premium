# Anti-patterns — grep-able violations and how to fix them

Read this during **verification** (`references/verification-checklist.md` step 6). Before declaring done, search the changed code for each anti-pattern below. Fix every match; none are optional.

## Canonical ownership and project-audit violations

- A screen-local select, date field, validation adapter, toast viewport, scrollbar theme, or CRUD transition duplicates a maintained shared owner.
- `select` or `input[type="date"]` appears without an explicit native/typed/authored ownership decision.
- Base scrollbar styling exists only under `.custom-scrollbar`, `.scrollbar`, or another opt-in class, or uses only `::-webkit-scrollbar*` without `scrollbar-color`/`scrollbar-width`.
- A shared page/form shell receives `h-screen`, `h-dvh`, `100vh`, `100dvh`, or `overflow: hidden` solely to make a table fit.
- Product forms omit `novalidate`/`noValidate`, or validation/recovery differs by screen without a named variant.
- Literal product textareas omit `resize-none`/`resize: none`, lack adequate height/auto-grow, or bypass the canonical Textarea owner.
- Invalid native fields lack a working visible label, `aria-invalid`, or an existing help/error target referenced by `aria-describedby`.
- Modal edit/delete surfaces use fixed dimensions that overflow the visual viewport/safe area or make their actions unreachable.
- Literal `href="#"` links or enabled buttons without a real action create false affordances.
- CRUD redirects, loading, toast, confirmation, focus, or failure recovery drift from `UX-CONTRACT.md`.
- Completion is claimed from static grep/audit while configured accessibility, localization, state-matrix, CRUD, or failure-path commands were not run.

## How to use

Each entry lists:

- **What to search for** — a grep pattern or code smell.
- **Why it is wrong** — the consequence.
- **How to fix** — the replacement pattern.

Run these searches against the diff or the changed files, not the entire codebase, unless the brief explicitly asks for a full audit.

---

## A. Native dialogs (alert, confirm, prompt)

**Search:** `(?:window\.)?(?:alert|confirm|prompt)\s*\(`

**Why wrong:** Blocks the browser thread, unstyled, untranslated, inaccessible to screen readers, no focus management, no Escape handling. The product cannot own the experience or log the interaction.

**Fix:** Replace with app-owned `<Dialog>` / `<AlertDialog>` with accessible label, focus trap, Escape dismiss, and semantic action labels.

```tsx
// Wrong
if (!confirm("Delete this analysis?")) return;

// Right
// <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
//   <AlertDialogTitle>Delete analysis</AlertDialogTitle>
//   <AlertDialogDescription>This cannot be undone.</AlertDialogDescription>
//   <AlertDialogAction onClick={handleDelete}>Delete</AlertDialogAction>
//   <AlertDialogCancel>Cancel</AlertDialogCancel>
// </AlertDialog>
```

> **False positive notes:** The old pattern `\balert\s*\(` matches Svelte `{#each alerts as alert}` and `{#if alert.type}`. The current pattern `(?:window\.)?(?:alert|confirm|prompt)\s*\(` requires an opening parenthesis after the keyword, which avoids Svelte template syntax. Also avoid matching `alert` as a variable name — only match as a function call.
> For Svelte projects, also check `svelte:window` listeners that call `alert()`.

---

## B. Clickable div/span without role

**Search:** `onClick\s*=\s*\{[^}]+\}\s*(?!.*role=)` ... but only on `<div>`, `<span>`, `<p>`, `<section>`.

Also search: `cursor-pointer` or `cursor:\s*pointer` on non-interactive elements.

**Why wrong:** Not keyboard-operable, no focus indicator, no screen-reader semantics, no disabled state handling.

**Fix:** Use `<button>` for actions, `<a>` for navigation. If a non-semantic element absolutely must be interactive, add `role="button"`, `tabIndex={0}`, `onKeyDown`, and an accessible name.

```tsx
// Wrong
<div onClick={handleClick} className="cursor-pointer">...</div>

// Right
<button onClick={handleClick} type="button">...</button>
```

---

## C. Search without debounce

**Search:** `onChange\s*=\s*\{[^}]*\bfetch\b[^}]*\}` or `onChange.*=>.*api\.` or `onChange.*=>.*axios` without `setTimeout`/`debounce`/`useDebounce` nearby.

Also search: `onChange.*=>.*setTimeout` without corresponding `clearTimeout`.

**Why wrong:** Fires a request on every keystroke. Wastes bandwidth, hurts backend, creates race conditions.

**Fix:** Debounce at 300ms (default). Cancel stale requests via `AbortController` or ignore outdated responses.

```tsx
// Wrong
const handleChange = (e) => fetch(`/api/search?q=${e.target.value}`);

// Right — 300ms debounce + stale cancel
useEffect(() => {
  const timer = setTimeout(() => {
    controller.current?.abort();
    controller.current = new AbortController();
    fetch(`/api/search?q=${query}`, { signal: controller.current.signal });
  }, 300);
  return () => clearTimeout(timer);
}, [query]);
```

---

## D. Search without clear button

**Search:** `<input[^>]*type=["'](search|text)["'][^>]*>` where the parent component does not contain `clear` or `"×"` or `"✕"` or `XButton` or `onClear`.

**Why wrong:** Users cannot quickly reset the query. On mobile the keyboard must be dismissed first, which is frustrating.

**Fix:** Add an **app-owned** clear button (X) when the input has a value. Must be keyboard-accessible, have a localized aria-label, clear the value, cancel pending requests, and return focus to the input.

> **Do NOT rely on the browser's native clear button** (`<input type="search">` shows a native X in some browsers). The native clear is inconsistent across browsers, unstyled, inaccessible (no keyboard focus, no aria-label), and untranslated. Always provide an app-owned clear button.

```tsx
// Wrong
<input type="search" />  {/* relies on browser native X */}

// Right
<input ref={inputRef} value={query} onChange={handleChange} />
{query && (
  <button
    onClick={() => { setQuery(""); controller.current?.abort(); inputRef.current?.focus(); }}
    aria-label="Clear search"
  >✕</button>
)}
```

---

## E. IME-unsafe search

**Search:** `onKeyDown.*Enter` or `onKeyPress.*Enter` that is not inside `if (e.key === 'Enter' && !e.isComposing)`.

**Why wrong:** On Japanese/Chinese/Korean IME, Enter commits composition characters. Firing search on that Enter submits half-typed text, losing the composition session.

**Fix:** Check `e.isComposing` or guard `compositionstart`/`compositionend`.

```tsx
// Wrong
<input onKeyDown={(e) => { if (e.key === 'Enter') search(); }} />

// Right
<input onKeyDown={(e) => { if (e.key === 'Enter' && !e.isComposing) search(); }} />
```

Also: Do not fire debounced search while `InputEvent.isComposing` is true.

---

## F. textarea without resize: none

**Search:** `<textarea[^>]*>` that is not followed by `resize` in the same component's style or class.

**Why wrong:** Default `resize: both` lets users drag the corner, which breaks form layout. Adjacent controls shift unexpectedly.

**Fix:** `resize: none` on all product textareas. Compensate with adequate default height and auto-grow if needed.

```tsx
// Wrong
<textarea className="...">  // user can drag to resize

// Right
<textarea className="... resize-none" />  // or style={{ resize: 'none' }}
```

---

## G. Secret input without reveal

**Search:** `<input[^>]*type=["']password["'][^>]*>` where the parent does not contain `show`/`hide`/`reveal`/`eye`/`toggle`.

**Why wrong:** Users cannot verify what they typed. Password managers work, but the product should not force a blind workflow.

**Fix:** Add a keyboard-accessible show/hide toggle with changing accessible label.

```tsx
// Wrong
<Input type="password" />

// Right
<div>
  <Input type={showPassword ? "text" : "password"} />
  <button
    onClick={() => setShowPassword(!showPassword)}
    aria-label={showPassword ? "Hide password" : "Show password"}
  >{showPassword ? <EyeOff /> : <Eye />}</button>
</div>
```

---

## H. Form without novalidate

**Search:** `<form[^>]*>` (without `noValidate` / `novalidate`) that has any `<input[^>]*required` or `type="email"` or `pattern=` inside.

**Why wrong:** Browser-native validation bubbles appear, unstyled, untranslated, inconsistent with product design. They surface HTML5 messages that bypass the app's validation system.

**Fix:** Add `noValidate` to all product forms. Own validation via the chosen form library (React Hook Form, Formik) or manual state.

```tsx
// Wrong
<form onSubmit={handleSubmit}>
  <input required />

// Right
<form onSubmit={handleSubmit} noValidate>
  <input required />
  {errors.email && <span role="alert">{errors.email}</span>}
</form>
```

---

## I. Skeleton/footer causing layout shift

**Search:** Skeleton or loader or footer that does not reserve space (no fixed `height`, `min-height`, or `aspect-ratio`).

**Why wrong:** Content arriving late pushes buttons, headers, or pagination down — users click the wrong target.

**Fix:** Always set explicit dimensions on placeholders. Keep footer height stable regardless of content length.

```tsx
// Wrong
{loading && <Loader />}  {/* no height → pushes content below */}

// Right
{loading && <div className="h-20"><Loader /></div>}  {/* reserves 80px */}
```

---

## J. Disabled control still interactive

**Search:** `className.*disabled:` or `aria-disabled` on elements that still have `onClick`, `onChange`, or `href`.

Also search: `cursor: not-allowed` on an element that is still clickable.

**Why wrong:** Disabled but clickable controls confuse users and create security holes (e.g., double-submit).

**Fix:** Guard handlers early. Do not attach pointer events to disabled elements.

```tsx
// Wrong
<button onClick={handleSubmit} disabled className="opacity-50 cursor-pointer" />

// Right
<button onClick={handleSubmit} disabled className="opacity-50 cursor-not-allowed" />
// Or more robustly: prevent default in handler:
if (disabled) return;
```

---

## K. Missing stale-request cancellation

**Search:** `fetch\(` or `axios\.` inside a `useEffect` or callback that does not have a corresponding `AbortController` or `ignore` flag.

Also search: `useEffect.*fetch` without a cleanup that aborts.

**Why wrong:** Older responses can overwrite newer ones after the user types more characters, navigates, or unmounts the component. This is especially dangerous with Japanese IME and auto-complete searches.

**Fix:** Use `AbortController` or a stale flag.

```tsx
// Wrong
useEffect(() => {
  fetch(`/api/search?q=${query}`).then(setResults);
}, [query]);

// Right
useEffect(() => {
  const ctrl = new AbortController();
  fetch(`/api/search?q=${query}`, { signal: ctrl.signal })
    .then(r => r.json())
    .then(setResults)
    .catch(e => { if (e.name !== 'AbortError') throw e; });
  return () => ctrl.abort();
}, [query]);
```

---

## L. Sortable table headers without button + aria-sort

**Search:** `<th[^>]*onClick[^>]*>` that does not contain `role` or `aria-sort` in the same tag.

Also search: `onClick.*setSort` or `onClick.*onSort` without matching `aria-sort`.

**Why wrong:** A clickable `<th>` without `role="columnheader button"` and `aria-sort` is not announced by screen readers as a sort control. The current sort direction is invisible to assistive technology. Keyboard users cannot activate sort unless the header contains a `<button>`.

**Fix:** Wrap the sort trigger in a `<button>` inside the `<th>`, or add `role="columnheader button"` + `tabIndex={0}` + `onKeyDown` + `aria-sort`.

```tsx
// Wrong
<TableHead onClick={() => setSort("name")}>Name</TableHead>

// Right
<TableHead>
  <button
    onClick={() => setSort("name")}
    aria-sort={sortField === "name" ? (sortDir === "asc" ? "ascending" : "descending") : "none"}
  >
    Name
    {sortField === "name" ? <SortIcon dir={sortDir} /> : null}
  </button>
</TableHead>
```

---

## M. Missing document title

**Search:** Routes/pages that do not set `document.title` or the framework's title API (`Helmet`, `useDocumentTitle`, Next.js `metadata.export`).

Also search: Non-dynamic title that is identical for every route (single `index.html` `<title>`).

**Why wrong:** Every route needs a unique document title for bookmarks, history, tab identification, and screen-reader announcements. A static title across all pages provides no navigation context.

**Fix:** Set the title per route — either via the framework's head API or by calling `document.title = "..."` in a `useEffect`.

```tsx
// Wrong — static title in index.html
<title>SAP Transport System</title>

// Right — per-route title
export default function TransportListPage() {
  useEffect(() => { document.title = "Transports | Transport System"; }, []);
  // ...
}
```

---

## N. Missing 403 / forbidden page

**Search:** Route guard or permission check that returns `null`, redirects to login, or shows a 404 instead of a dedicated 403 page.

**Why wrong:** When an authenticated user lacks permission for a resource, redirecting to login (already authenticated) or showing a 404 (resource exists but hidden) creates a confusing experience. A 403 page should explain the permission gap and offer a way forward.

**Fix:** Implement a `<ForbiddenPage>` or `<AccessDenied>` component for 403 responses. Differentiate from 404 (`<NotFoundPage>`).

```tsx
// Wrong
if (!hasRole("admin")) return <NotFoundPage />;

// Right
if (!hasRole("admin")) return <ForbiddenPage resource="transports" />;
```

---

## O. Deprecated/unsafe patterns

| Pattern | Search | Fix |
|---------|--------|-----|
| `dangerouslySetInnerHTML` without sanitization | `dangerouslySetInnerHTML` | Use DOMPurify or a safe renderer |
| `localStorage` without try/catch | `localStorage\.` (outside try) | Wrap in try/catch for private browsing mode |
| `innerHTML` assignments | `\.innerHTML\s*=` | Use `textContent` or safe DOM methods |
| CSS `!important` without comment | `!important` | Add /* reason */ or refactor specificity |
| `onClick` on `<a>` without `href="..."` | `<a[^>]*onClick[^>]*>` without href | Use `<button>` if no navigation; add `href` for real links |
| Sortable `<th>` no button/`aria-sort` | `<th[^>]*onClick[^>]*>` (không `role`/`aria-sort` | Add `<button>` + `aria-sort` inside `<th>` |
| Static `document.title` | `<title>` same on all routes | Set per-route dynamic title |
| 403 returned as 404 | `if.*role.*NotFound` or redirect khi thiếu quyền | Return dedicated `<ForbiddenPage>` |

---

## P. Native select used when authored popup geometry is required

**Search:** `<select` in a screen whose design requires the opened option popup to match the trigger's width, border, radius, spacing, scrolling, or placement.

Also search for CSS that targets `option`, `select option`, `appearance: none`, or the Tailwind/utility form `appearance-none` and claims to style the opened native popup.

**Why wrong:** The opened native select popup is browser- or operating-system-owned on major platforms. Styling the closed `<select>` or its `<option>` elements cannot guarantee the popup's outer dimensions, border thickness, radius, option rendering, or collision behavior.

**Fix:** First make the decision explicit. Keep native select only when platform-owned popup geometry is accepted. When geometry is authored, replace it with the project's maintained accessible Select/Listbox primitive; share trigger/content border, radius, width, and density tokens; portal the popup; and use collision-aware bounded scrolling. Do not build a custom ARIA listbox from scratch.

**Verification:** Open the popup in a real browser. Compare trigger and listbox bounding rectangles (outer width difference no greater than 1 CSS px), computed border widths/tokens, alignment, focus/selection, keyboard behavior, long options, scrolling, zoom, and viewport-edge collision.

---

## Q. Native date/time picker used when localized popup UI is required

**Search:** `type=["'](date|time|month|week|datetime-local)["']` and equivalent `input[type=...]` selectors on a surface whose active locale, picker labels, footer actions, geometry, or interaction must be app-owned and consistent.

Also search for `lang="ja"` or a formatted closed value being cited as proof that the opened native calendar is Japanese.

**Why wrong:** Native date, time, month, week, and datetime-local pickers are browser- or operating-system-owned. Page language and input styling cannot guarantee their headings, labels, actions such as Today/Clear, geometry, or platform behavior. A Japanese form can therefore display an English picker even when the closed field looks correct.

**Fix:** Make the ownership decision explicit for every picker type. Keep a native picker only when its platform-owned popup locale and behavior are accepted across the supported matrix. When the product owns the popup UI, use the project's maintained accessible date/time picker primitive, load the complete locale pack, separate typed storage from display formatting, and preserve keyboard, pointer, Escape, focus-restoration, collision, bounded-height, and scrolling behavior.

**Verification:** Open the calendar in a real browser. Check month/year, weekday headers, navigation, Today/Clear/Apply/Cancel actions, placeholders, validation, and accessible names in the active locale. Exercise keyboard and pointer selection, Escape, restored trigger focus, 200% zoom, and narrow/short viewport collision. For Japanese UI, reject `August`, `Clear`, `Today`, or other fallback English.

---

## R. Scrollbar theme requires per-container opt-in

**Search:** Scrollbar selectors scoped only to utility classes such as `.custom-scrollbar`, `.ui-scroll-container`, or component-local wrappers while other `overflow`, `overflow-x-*`, or `overflow-y-*` regions exist. Also search for `::-webkit-scrollbar` rules without standards-based `scrollbar-color` and `scrollbar-width` declarations.

Also search for newly added overflow containers that must remember a special class solely to receive thumb/track colors.

**Why wrong:** The component looks correct only when its author remembers an unrelated opt-in class, or only in WebKit/Blink when engine-fallback pseudo-elements are used without the standards properties Firefox supports. New tables, dialogs, menus, and panels silently fall back to the browser default, causing visual drift and repeated review fixes.

**Fix:** Put the tokenized scrollbar baseline in the application's global stylesheet so all product-owned scroll surfaces inherit thumb, track, hover, active, width, and engine-compatible styling. Keep per-container classes only for explicit geometry or semantic exceptions such as stable gutter or compact density. Preserve a forced-colors/high-contrast path and do not target browser chrome or third-party documents.

**Verification:** Create or locate a scroll container with no scrollbar utility class. In a real browser, confirm the application root and that container have non-default computed `scrollbar-color`, WebKit thumb/track styles, no unwanted native arrow buttons when the design removes them, and usable forced-colors behavior.

---

## S. Table viewport sizing leaks into sibling form

**Search:** A table-related change adds `h-dvh`, `h-screen`, `h-full`, `min-h-screen`, `100vh`, `100dvh`, `100svh`, `height: 100%`, fixed height, or `overflow-hidden` to a shared route/page/tab ancestor. Also inspect shared wrappers where one tab is a bounded table and another is a long form.

**Why wrong:** Table-specific flex and overflow constraints change the scroll owner for every sibling. The table may look correctly screen-sized while the form becomes clipped, trapped in a nested scroller, or visually “fixed”; fields and actions can become unreachable at short viewports or 200% zoom.

**Fix:** Scope the bounded flex/min-height chain to the table panel or table-specific wrapper. Preserve the long form's natural height and document scrolling, or its existing canonical application content scroller. Keep only the form action bar sticky when appropriate. Do not change a shared ancestor's height/overflow solely to satisfy the table.

**Verification:** Switch between table and form tabs at short and tall viewport heights and at 200% zoom. Confirm the table frame keeps one footprint for 10/20/50 rows and scrolls internally, while the form's own height grows with its fields, every field remains reachable, and no nested or competing vertical scrollbars appear.

---

## T. Native datalist used as an authored combobox

**Search:** `<datalist` or an `<input list="...">`/`list='...'` binding where popup geometry, localization, accessibility behavior, option states, or interaction must be app-owned.

**Why wrong:** The opened datalist popup is browser-owned. Styling the input or `<option>` elements cannot guarantee popup width, border, placement, localization, keyboard behavior, or consistent assistive-technology support across the supported matrix.

**Fix:** Keep `<datalist>` only when platform-owned suggestions are explicitly acceptable. When the product owns the combobox experience, use the project's maintained accessible Combobox/Autocomplete primitive with authored popup geometry, localized states, IME-safe filtering, keyboard navigation, focus restoration, bounded scrolling, and form integration.

**Verification:** Open the authored combobox in every supported browser. Verify trigger/popup geometry, Japanese visible and accessible copy, IME composition, Arrow-key navigation, Enter selection, Escape, empty/loading/error/disabled states, long options, zoom, and viewport-edge collision.

---

## Verification checklist

Before finalising any diff that touches UI code, grep for at least:

```bash
# Native dialogs (matches function calls, not Svelte template syntax)
rg '(?:window\.)?(?:alert|confirm|prompt)\s*\(' src/

# Clickable non-semantic
rg 'onClick.*className.*cursor-pointer' src/ | rg -v 'button|a '

# Search without clear
rg -U '<input[^>]*\b(search|text)\b[^>]*>' src/ | rg -v 'clear|XButton|onClear'

# IME unsafe
rg 'onKey(Down|Press).*Enter' src/ | rg -v 'isComposing'

# Secret without reveal
rg 'type="password"' src/ | rg -v 'show|toggle|eye|reveal'

# Sortable header without button/aria-sort
rg '<th[^>]*onClick[^>]*>' src/ | rg -v 'role|aria-sort'

# Forms without noValidate (with validation inputs)
rg '<form[^>]*>' src/ | rg -v 'noValidate' | rg '<input[^>]*(required|type=.email.)'

# Static document title
rg '<title>' public/index.html public/index.htm 2>/dev/null || rg '<title>' src/index.html 2>/dev/null

# 403 as 404 pattern
rg 'if.*role.*NotFound' src/; rg 'redirect.*403' src/

# Native select/datalist where popup geometry is authored (review each match in context)
rg "<select|<datalist|\blist=['\"]|select\s+option|appearance:\s*none|appearance-none" src/

# Native date/time picker where popup locale/geometry is authored (review each match in context)
rg "type=['\"](date|time|month|week|datetime-local)['\"]|input\[type=['\"]?(date|time|month|week|datetime-local)" src/

# Scrollbar base that depends on an opt-in utility or WebKit-only fallback
rg '\.(custom-scrollbar|ui-scroll-container).*scrollbar|overflow-(x|y|auto)|::-webkit-scrollbar' src/

# Table sizing leaked to a shared page/tab shell (review each match and its siblings)
rg 'h-dvh|h-screen|h-full|min-h-screen|100vh|100dvh|100svh|height:\s*100%|overflow-hidden|min-h-0' src/
```

At least the first two searches must return zero results for non-trivial UI changes.
