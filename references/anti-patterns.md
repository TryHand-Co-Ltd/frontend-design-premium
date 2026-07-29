# Anti-patterns — grep-able violations and how to fix them

Read this during **verification** (`references/verification-checklist.md` step 6). Before declaring done, search the changed code for each anti-pattern below. Fix every match; none are optional.

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
```

At least the first two searches must return zero results for non-trivial UI changes.
