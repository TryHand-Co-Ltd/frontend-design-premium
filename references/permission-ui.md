# Permission and Authorization UI

Read this when implementing or modifying UI for permission-gated features, role-based access, API key display, clipboard interactions, or account-level controls.

## Permission states

Every permission-sensitive feature has four possible UI states. Choose the right one based on severity and context:

| State | When to use | Visual | Behavior |
|-------|------------|--------|----------|
| **Visible + enabled** | User has the required permission | Normal interactive control | Action works normally |
| **Visible + disabled** | User can see the feature but cannot act (read-only role, view-only access) | Greyed out, `cursor: not-allowed`, tooltip explains why | `onClick` handler returns early; `disabled` attribute on native elements |
| **Hidden** | Feature is irrelevant to this role (e.g., "Admin settings" for a regular user) | Not rendered in DOM | User cannot discover the feature exists |
| **403 page / redirect** | User navigated directly to a forbidden route (typed URL, stale bookmark) | Dedicated error page or inline banner | HTTP 403 page with explanation + link to home/dashboard |

### Rules

- **Hide** features that are completely irrelevant to the role. Do not show "Billing" to a user who can never pay.
- **Disable** features the user can see but not use. Always include a tooltip or help text explaining why (`role="tooltip"`, not `title` attribute).
- **Never** rely on client-side hiding alone for security. Server-side authorization is the source of truth; client-side hiding is UX convenience.
- **Disabled + tooltip** is more transparent than hidden. Users understand "you need the Admin role" better than "where did the button go?"
- Show a **403 page** for direct navigation to forbidden routes, not a 404 (which implies the page does not exist).

```tsx
// Disabled with explanation
<Button
  disabled={!canDelete}
  onClick={handleDelete}
  aria-disabled={!canDelete}
>
  Delete
</Button>
{!canDelete && (
  <Tooltip content="You need the Admin role to delete analyses">
    <IconHelp />
  </Tooltip>
)}

// Hidden for irrelevant roles
{isAdmin && <AdminSidebar />}

// 403 page
function ForbiddenPage() {
  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <h1>Access denied</h1>
      <p>You do not have permission to access this page.</p>
      <Button onClick={() => router.push("/dashboard")}>
        Go to dashboard
      </Button>
    </div>
  );
}
```

## Clipboard copy

### ID / key copy pattern

```tsx
function CopyButton({ value, label }: { value: string; label?: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for non-HTTPS or denied permission
      const textarea = document.createElement("textarea");
      textarea.value = value;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="inline-flex items-center gap-1.5">
      <code className="text-sm">{label ?? value}</code>
      <button
        onClick={handleCopy}
        aria-label={copied ? "Copied" : "Copy to clipboard"}
        className="p-1 hover:bg-muted rounded"
      >
        {copied ? <CheckIcon className="size-3.5 text-success" /> : <CopyIcon className="size-3.5" />}
      </button>
    </div>
  );
}
```

### Rules

- Show a **truncated preview** (`sk-xxx...xxxx`) for long API keys/secrets, never the full value by default.
- Add a **copy button** next to the truncated value. Clicking copies the full value to clipboard.
- On copy, show a brief **"Copied" toast** or icon state change. Do **not** include the copied value in the toast message (leaking secrets into notification history).
- Provide a **"Show" toggle** (eye icon) to reveal the full value temporarily, same as password reveal pattern.
- Test `navigator.clipboard.writeText` on HTTPS only. Provide `document.execCommand("copy")` fallback for localhost or non-HTTPS.
- Never log copied values to console, analytics, or error trackers.

## Role-based feature access

Define a permission map per route group:

```ts
const FEATURE_PERMISSIONS = {
  "analysis.delete": ["admin", "manager"],
  "user.invite": ["admin"],
  "billing.view": ["admin", "finance"],
  "report.export": ["admin", "manager", "analyst"],
} as const;

function canAccess(feature: keyof typeof FEATURE_PERMISSIONS, userRole: string): boolean {
  return FEATURE_PERMISSIONS[feature].includes(userRole);
}
```

Use this map in components instead of hardcoding role checks:

```tsx
// Instead of: if (user.role === "admin")
// Use:
{canAccess("analysis.delete", user.role) && <DeleteButton />}
```

## Do's and Don'ts

- **Do:** Use `aria-disabled` (not just CSS class) for disabled-but-visible controls so screen readers announce them as disabled.
- **Do:** Show 403 pages for forbidden direct navigation, not 404.
- **Do:** Use a permission map rather than inline role checks.
- **Do:** Copy to clipboard with a short "Copied" toast — never include the copied value in the toast.
- **Don't:** Hide features that the user might legitimately wonder about ("Where is the delete button?") — disable + explain instead.
- **Don't:** Rely on client-side hiding for security; always enforce on the server.
- **Don't:** Reveal full API keys/secrets by default — always truncate + mask + copy.
- **Don't:** Log clipboard contents.
