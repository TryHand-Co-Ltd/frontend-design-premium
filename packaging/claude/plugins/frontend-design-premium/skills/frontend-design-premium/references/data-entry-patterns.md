# Data Entry and Composite Interaction Patterns

Read the relevant sections for advanced inputs, bulk workflows, direct manipulation, or composite widgets. Prefer a proven accessible library primitive over hand-assembling ARIA behavior.

## Multi-select and bulk actions

- Use a checkbox per item and a labeled header checkbox with checked/unchecked/indeterminate states.
- Distinguish “select this page” from “select all matching results.” Never imply the latter when only loaded rows are selected.
- Keep selection stable across sort/filter/page changes only when users can understand the scope; otherwise clear it and announce why.
- Show exact selected count and make the bulk-action toolbar persistent without shifting the table unexpectedly.
- Shift-click range selection is a progressive enhancement when ordering is stable. Platform modifier selection may supplement but not replace checkboxes.
- After a bulk mutation, report succeeded/failed counts, preserve recoverable failures, and put focus in a logical surviving location.
- Dangerous bulk actions name scope, count, consequence, and recovery in an app-owned confirmation.

## File upload and drop zones

A drop zone always includes a visible file-picker button; drag and drop is never the only method.

States: idle, drag-over, validating, queued, uploading, paused/cancelled when supported, success, partial success, error, retry, and removed.

- State accepted types, count, and size limits before selection; validate on both client and server.
- Use the native file input for selection and preserve its accessible label.
- Do not trust extension/MIME alone or expose local file paths.
- Show each file name, size, progress when measurable, status, cancel/remove, and actionable error.
- For long/large uploads, define cancellation, resumability/chunk retry, navigation behavior, duplicate handling, and session expiry.
- Preview untrusted content safely; revoke object URLs and avoid decoding huge media on the main thread.
- Announce status changes without flooding live regions. Keep layout stable as rows enter progress/error states.

## Combobox, autocomplete, and typeahead

Use a maintained combobox primitive that follows the WAI-ARIA pattern.

- Keep input value, committed value, highlighted option, and popup state distinct.
- Define minimum characters and debounce only for remote work. Suppress dispatch during IME composition and cancel/ignore stale responses.
- Provide loading, grouped results when needed, no-results, create-new when legitimate, retry, and clear behavior.
- Arrow keys navigate options; Enter commits the highlighted option only when not completing IME composition; Escape closes without erasing committed data.
- Expose active descendant/selection correctly and keep the highlighted option visible.
- For multi-select, render removable chips with keyboard removal and an accessible summary when values overflow.
- Do not silently commit arbitrary text when the field requires an entity ID. Preserve user input after recoverable request errors.

## Date and date-range pickers

- Distinguish date-only values, local date-time, and absolute instants in the data model.
- Provide a typed input path in addition to the calendar when practical, with localized format guidance and deterministic parsing.
- Date ranges define inclusive/exclusive semantics, valid order, min/max, unavailable dates, and timezone before implementation.
- Presets such as Today, This week, Last 7 days, or Custom must follow domain definitions, not labels alone.
- Separate draft selection from committed filters when an Apply button exists; Cancel restores the prior committed range and Clear has an explicit outcome.
- Calendar keyboard behavior, focus, today, selected, range start/end, disabled dates, month navigation, and announcements must remain distinct.
- Japanese locale does not imply era notation. Follow `references/japanese-localization.md`.

## Inline editing

Use inline editing for short, localized changes where surrounding context is valuable. Use a full form for complex validation, dependencies, permissions, or destructive effects.

- Enter edit mode through a semantic control, not undiscoverable text click alone.
- Move focus to the editor and preserve the original value for cancellation.
- Define commit behavior explicitly: Save button, Ctrl/Cmd+Enter, Enter for single-line, or blur only when accidental commits are safe.
- Escape cancels and restores the original value; validation/error keeps the editor open with recovery.
- Prevent duplicate/stale saves. Optimistic commit requires honest rollback and conflict handling.
- On success, return focus to the edited value or next logical item and announce the result without moving the row.

## Expandable rows, disclosure, and accordion

Use a disclosure for one independent show/hide region and an accordion for a related set. An expanded table row must preserve valid table structure.

- The trigger is a button with accessible name and expanded state, linked to the controlled region.
- Do not make the entire row the only toggle when it contains links, checkboxes, or actions.
- Define whether multiple accordion panels may remain open. Do not force one-open behavior without a product reason.
- Keep focus on the trigger when toggling. If opening reveals a task requested by the user, move focus only when that is the expected next action.
- Animate height/opacity only when motion remains smooth, interruptible, and reduced-motion safe. Avoid measuring transitions that cause layout thrash.
- Lazy detail content needs loading, error, retry, stale-request, and collapse-during-load behavior.

## Stepper and multi-step forms

- Show current step, total or meaningful stage names, completed status, and optional/skippable status without using color alone.
- Validate the current step before advancing; retain values and errors when navigating back.
- Define whether completed steps are revisitable and whether URL/deep-link state is valid.
- Persist drafts when the workflow is long or interruption is likely. Communicate save status and expiry.
- Branching steps must not report misleading totals. Recompute the visible path deliberately.
- Review/confirm steps display the actual committed values and offer targeted edit links.
- Final submission is idempotent and distinguishable from per-step draft saving.

## Slider and range input

Prefer a native range input when it meets visual and interaction needs. A custom slider must implement the complete keyboard and touch model.

- Expose label, current value, min, max, and step. Show units and formatted values outside pointer-only tooltips.
- Support arrows and expected larger increments; keep focus visible on the active thumb.
- Multi-thumb sliders prevent ambiguous crossing or clearly swap semantics, maintain logical tab order, and expose each thumb's label/value.
- Provide numeric inputs when precise values matter or touch drag is difficult.
- Do not use a slider for a small set of named options better represented by radio buttons.

## Tags, chips, and badges

- Use tags/badges for status or metadata; chips may represent removable values, filters, or compact actions. Do not make static status look clickable.
- Semantic color has a text/icon/shape equivalent and meets contrast requirements.
- Removable chips use a real remove button with a specific accessible name and predictable focus after removal.
- For overflow, show a count/summary with an accessible expansion path rather than clipping silently.
- Keep label vocabulary, casing, height, radius, and icon policy aligned with `DESIGN.md`.

## Filter chips and URL state

### Filter chips

- Render active filters as removable chips between the search bar and the data list.
- Each chip shows the filter name and value (e.g., `Status: Active` followed by a remove button).
- The remove button on the chip clears that single filter, cancels pending requests, and refreshes results.
- A "Clear all" button appears when 2+ filters are active. It clears all filters at once.
- Filter chips stack horizontally with wrapping. Do not clip or overflow — scroll on small screens if needed.
- Adding or removing a filter must not reset unrelated filters.

### URL state for filters and pagination

- Persist active filters, search query, current page, page size, and sort direction in URL search params.
- This enables browser Back/Forward navigation, shareable/bookmarkable filtered views, and preserved state on page refresh.
- Use `useSearchParams` (Next.js) or `useSearchParams` (React Router) to read/write filter state.
- Do not duplicate state: URL is the source of truth. Component state derives from URL.
- On page load, read initial filter state from URL. If no URL params exist, use sensible defaults (no filters, page 1).

```tsx
// Example: sync filters with URL
const searchParams = useSearchParams();
const router = useRouter();

const status = searchParams.get("status") ?? "";
const page = parseInt(searchParams.get("page") ?? "1", 10);

function setFilter(key: string, value: string) {
  const params = new URLSearchParams(searchParams.toString());
  if (value) params.set(key, value);
  else params.delete(key);
  params.set("page", "1"); // reset to first page on filter change
  router.push("?" + params.toString());
}
```

## Density: compact and comfortable

Offer a density toggle when the primary view is a dense data table or list. This is common in ops/admin SaaS.

| Mode | Row height | Padding | Font size | When to use |
|------|-----------|---------|-----------|-------------|
| **Comfortable** (default) | 48-56px | `py-3` `px-4` | 14px | Default for most users, easier scanning |
| **Compact** | 32-40px | `py-1.5` `px-3` | 13px | Users who need to see many rows at once |

### Implementation

- Store the preference in localStorage (key: `density`).
- Apply a `.density-compact` class on the table or a CSS custom property `--row-height`.
- Do not change column count or responsiveness — compact mode only reduces vertical space.
- Toggle: a small icon button (rows-dense / rows-normal) near the search/filter bar.
- Label: "Compact view" / "Comfortable view" with accessible state.

```css
/* CSS variable approach */
table[data-density="compact"] {
  --row-py: 4px;
  --cell-font-size: 0.8125rem;
}

table[data-density="comfortable"] {
  --row-py: 12px;
  --cell-font-size: 0.875rem;
}
```

### When NOT to offer density

- Consumer-facing marketing pages or landing sections — density control confuses non-admin users.
- Single-purpose screens with a fixed small dataset.
- Kanban/card views — use card size instead of table density.

## Drag, reorder, and direct manipulation

Any drag operation has a non-drag alternative such as move up/down, destination menu, or keyboard reorder.

- Announce the grabbed item, position, valid destinations, and completed position when custom interaction is justified.
- Provide a sufficiently large handle and do not make scrolling impossible on touch.
- Persist reorder only after a clear commit or use honest optimistic rollback.
- Preserve focus and offer Undo for accidental reorder where reliable.

## Form validation patterns (Formik + Yup / React Hook Form + Zod)

These two libraries dominate React production forms. They share the same architectural concerns: client-side schema validation, server error recovery, common error banners, and inline field errors. The patterns below apply to both; pick the library that matches your codebase.

### Common pattern: two error layers

Real applications always display two error layers regardless of library:

1. **Common error banner** — a top-of-form alert for server-level failures (network error, authentication denied, session expired). State managed independently from the form library:

   ```tsx
   const [commonError, setCommonError] = useState("");

   // In JSX
   {commonError && (
     <div role="alert" className="bg-error-50 text-error-600 p-3 rounded-md">
       {commonError}
     </div>
   )}
   ```

2. **Inline field errors** — per-field messages set via `setFieldError` (Formik) / `setError` (RHF) or schema validation.

### Formik + Yup

```tsx
const { handleChange, handleSubmit, values, errors, setFieldError } =
  useFormik({
    initialValues: { email: "", password: "" },
    validationSchema: yup.object({
      email: yup.string().email().required(),
    }),
    onSubmit(values, { setFieldError }) {
      // client pre-check before server round-trip
    },
  });
```

**Server error to field mapping:**

```tsx
// onSubmit
onSubmit: async (values, { setFieldError }) => {
  try {
    await api.login(values);
  } catch (err) {
    if (err.field === "email") {
      setFieldError("email", "このメールアドレスは登録されていません");
    } else {
      setCommonError("ログインに失敗しました。もう一度お試しください");
    }
  }
}
```

**Post-submit field recovery:**

```tsx
const handleChange = (e) => {
  setFieldError(e.target.name, ""); // clear stale server error
  setCommonError("");                // clear banner error on any edit
  formik.handleChange(e);
};
```

### React Hook Form + Zod

```tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const loginSchema = z.object({
  email: z.string().email("正しいメールアドレスを入力してください"),
  password: z.string().min(8, "パスワードは8文字以上必要です"),
});

type LoginForm = z.infer<typeof loginSchema>;

const {
  register,
  handleSubmit,
  setError,
  formState: { errors, isSubmitting },
} = useForm<LoginForm>({
  resolver: zodResolver(loginSchema),
});
```

**Server error to field mapping:**

```tsx
const onSubmit = async (data: LoginForm) => {
  try {
    await api.login(data);
  } catch (err) {
    if (err.field) {
      setError(err.field, {
        message: err.message || "入力内容を確認してください",
      });
    } else {
      setCommonError("サーバーエラーが発生しました");
    }
  }
};
```

**Post-submit field recovery:**

```tsx
// Use the `onChange` event from register to clear server errors
// or create a wrapped handler:
const handleFieldChange = (field: keyof LoginForm) => (e: React.ChangeEvent<HTMLInputElement>) => {
  if (errors[field]) setError(field, {}); // clear without message
  setCommonError("");
  field.onChange(e); // original register onChange
};

// Usage: <Input {...register("email", { onChange: handleFieldChange("email") })} />
```

### Client pre-check pattern (both)

Validate *before* submit to keep the form responsive and avoid unnecessary API calls. This is for business logic that the schema cannot express (e.g., corporate-email-only rules):

```tsx
// Formik
onSubmit(values) {
  let hasError = false;
  if (!yup.string().email().isValidSync(values.email)) {
    setFieldError("email", "正しいメールアドレスを入力してください");
    hasError = true;
  }
  if (hasError) return;
}

// RHF + Zod — use trigger() or manual check
const onSubmit = async (data: LoginForm) => {
  const result = loginSchema.safeParse(data);
  if (!result.success) {
    // Zod will have already populated errors via resolver;
    // add extra business checks after
    if (data.email.endsWith("@gmail.com")) {
      setError("email", { message: "企業メールアドレスをご使用ください" });
      return;
    }
  }
};
```

### Guidelines (library-agnostic)

- Use schema validation (`validationSchema` / `resolver`) for structural rules (required, format, min/max).
- Use `setFieldError` / `setError` + `commonError` for server-level or business-logic validation.
- Never use `alert()`, `confirm()`, or `prompt()` for form feedback — use the app-owned error UI.
- Apply `novalidate`/`noValidate` on `<form>` to disable native browser bubbles.
- Keep loading state (`isPending` / `isSubmitting`) to prevent double submit. Button must show busy state without changing width.
- On invalid submit, focus/scroll to the first field in error.
- For Japanese forms, error messages should explain what is wrong and how to fix, not just state failure (e.g., "パスワードは8文字以上で、英小文字と数字が必要です" rather than "パスワードが無効です").

## Accessible authentication inputs

- Allow password managers and paste; do not make users transcribe credentials or solve memory/puzzle tests unnecessarily.
- Use correct autocomplete values, reveal controls, and accessible error recovery.
- Support passkeys, magic links, or one-time codes with appropriate semantics when the product offers them.
- Re-authentication for sensitive actions preserves the user's pending task and explains why it is required.
