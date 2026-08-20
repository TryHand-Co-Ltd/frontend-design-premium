# Authentication and Authorization Patterns

Read this when implementing or modifying sign-in, sign-up, session handling, route protection, or account management. Auth affects every screen; inconsistencies between flows erode trust faster than visual mismatches.

## Authentication model

### Choose a provider strategy

| Approach | Use when | Examples |
|----------|----------|----------|
| Credentials only | Internal tools, admin panels, email+password login | CMS, corporate apps |
| OAuth / social login | Consumer-facing, reduced friction, passkey support | GitHub, Google, Apple |
| Hybrid | Both credential and OAuth paths, progressive auth | Atlas Match (Credentials + GitHub) |
| Magic link / email OTP | Passwordless, high-trust, low-support | Enterprise portals |
| API key / token | Machine-to-machine, CLI access, integrations | Developer platforms |

### Session strategy

- **JWT (stateless):** Preferred for server-rendered apps and when database lookups on every request are unacceptable. Tokens should include user id, role, and expiration; never secrets.
- **Database (stateful):** Required when immediate session revocation is needed (admin block, password change invalidates all sessions). Use with server components that query session on every render.

For NextAuth.js / Auth.js:

```ts
// JWT strategy (default)
session: { strategy: "jwt" },
callbacks: {
  async jwt({ token, user }) {
    if (user) token.id = user.id;
    return token;
  },
  async session({ session, token }) {
    if (token.id && session.user) session.user.id = token.id;
    return session;
  },
},
```

### Sign-in flow

Structure:

1. User enters email + password (or clicks OAuth provider).
2. Client calls `signIn("credentials", { email, password, redirect: false })`.
3. Server validates credentials, returns session token or error.
4. On error, display inline banner at the top of the form (never `alert()`).
5. On success, redirect to the authenticated home or the page the user was trying to reach.

```tsx
const handleSubmit = async (e: FormEvent) => {
  e.preventDefault();
  setLoading(true);
  setError(null);

  const result = await signIn("credentials", {
    email, password, redirect: false,
  });

  if (result?.error) {
    setError("メールアドレスまたはパスワードが正しくありません");
    setLoading(false);
    return;
  }

  router.push(callbackUrl || "/");
  router.refresh();
};
```

Rules:
- Use `redirect: false` to handle errors in-app rather than query parameters.
- Error message must be generic to avoid leaking whether the email exists.
- Use `<form noValidate>` — the app owns validation feedback.
- Loading state disables the submit button and shows a spinner or "Signing in…".

### Sign-up flow

Structure:

1. User fills name, email, password, password confirmation.
2. Client validates: email format, password strength, passwords match.
3. Server creates user (hash password with bcrypt/argon2), returns session.
4. On success, redirect to app with a welcome experience.
5. On duplicate email, show inline error on the email field.

Patterns:

```tsx
// Server: create user with hashed password
const passwordHash = await bcrypt.hash(password, 12);
const user = await prisma.user.create({
  data: { name, email, passwordHash },
});

// Create session after signup
await signIn("credentials", { email, password, redirect: false });
```

Rules:
- Password requirements shown before submit, not after error.
- "Already have an account? Sign in" link at the bottom.
- OAuth signup should link accounts by email when safe.

## Route protection

### Client-side: redirect unauthenticated users

```tsx
// In a layout or page component
const { data: session } = useSession();

if (!session) {
  return <RedirectToSignIn />;
}
```

### Server-side: protect API routes

```tsx
import { auth } from "@/lib/auth";

export async function GET() {
  const session = await auth();
  if (!session?.user) {
    return Response.json({ error: "Unauthorized" }, { status: 401 });
  }
  // proceed
}
```

### Role-based access

Define a route permission map:

```ts
export const ROUTE_PERMISSIONS = {
  ADMIN_ONLY: ["/admin", "/corporate", "/user"],
  AUTHENTICATED: ["/dashboard", "/analyses"],
  PUBLIC: ["/", "/about", "/login"],
} as const;
```

For each protected route, check role membership in middleware or layout:

```tsx
// middleware or layout check
if (!session || !allowedRoles.includes(session.user.role)) {
  redirect("/auth/signin?callbackUrl=" + encodeURIComponent(pathname));
}
```

## OAuth integration

### GitHub example

```ts
GitHub({
  clientId: process.env.AUTH_GITHUB_ID ?? "",
  clientSecret: process.env.AUTH_GITHUB_SECRET ?? "",
  allowDangerousEmailAccountLinking: true, // link accounts by email
}),
```

### OAuth button

```tsx
<Button onClick={() => signIn("github", { callbackUrl: "/" })}>
  <GitHubIcon />
  GitHub
</Button>
```

Rules:
- OAuth buttons always show the provider name and icon.
- Never auto-redirect on OAuth — let the user choose.
- Handle the case where OAuth returns an error (user cancelled, email exists).

## Session display and user menu

Show who is signed in:

```tsx
// Header: user avatar + name + logout
{session?.user && (
  <div className="flex items-center gap-2">
    {session.user.image && (
      <img src={session.user.image} alt="" className="size-8 rounded-full" />
    )}
    <span className="text-sm">{session.user.name}</span>
    <button onClick={() => signOut()}>Sign out</button>
  </div>
)}
```

## Error states

| State | Pattern |
|-------|---------|
| Invalid credentials | Inline error banner, preserve email, clear password |
| Network error | Common error banner with retry |
| OAuth provider down | Fall back to credentials; show status message |
| Session expired | 401 interceptor → save state → redirect to signin → return after auth |

## Password rules

- Min length: 8 characters (recommend 12+ for sensitive apps).
- Require mixed case, number, special character only when the product justifies it.
- Show requirements as a list **before** the user starts typing.
- Allow paste and password manager autofill — do not block.
- Use `current-password` / `new-password` autocomplete values.

## Do's and Don'ts

- **Do:** Use `<form noValidate>` and app-owned validation feedback.
- **Do:** Show a single generic error for invalid credentials — never reveal which field is wrong.
- **Do:** Preserve callbackUrl so users return to their intended page after login.
- **Do:** Handle `DB_FEATURES_DISABLED` / offline-auth environments gracefully (show a banner, hide auth UI).
- **Don't:** Use `alert()`, `confirm()`, or `prompt()` for auth errors.
- **Don't:** Store raw passwords, expose passwordHash, or log credential values.
- **Don't:** Auto-sign-in after failed signup — let the user verify their credentials.
- **Don't:** Redirect on OAuth without user interaction.
