# Codex marketplace review cases

These cases are designed for the skills-only `frontend-design-premium` plugin. They require no account, private network, or fixture data beyond the prompt and an ordinary local project.

## Positive cases

### 1. New SaaS dashboard

- Prompt: `Build a responsive SaaS billing dashboard with usage cards, invoices, plan changes, and cancellation.`
- Expected workflow: Loads `frontend-design` first, then `frontend-design-premium`; creates or reconciles durable design context; resolves high-risk billing and cancellation decisions before implementation.
- Expected result: Distinctive working UI with loading, empty, error, success, confirmation, responsive, keyboard, and recovery states.

### 2. Existing multi-screen application

- Prompt: `Add a customer detail screen to this existing admin application.`
- Expected workflow: Inspects existing tokens, shared primitives, navigation, and sibling list/detail flows before proposing changes.
- Expected result: New screen preserves the established visual identity and shared behavior instead of introducing screen-local variants.

### 3. Japanese onboarding flow

- Prompt: `Implement a Japanese onboarding wizard with company details, address, billing contact, and review steps.`
- Expected workflow: Reads the Japanese localization, data-entry, navigation, and interaction references.
- Expected result: `ja-JP`-appropriate formatting, IME-safe inputs, explicit timezone handling, accessible validation, stable layout, and recoverable progress.

### 4. UX resilience review

- Prompt: `Review this CRUD frontend for production UX problems and fix them.`
- Expected workflow: Audits destructive actions, async races, loading and failure states, access control UI, navigation, layout stability, and shared-component drift.
- Expected result: Evidence-backed findings followed by scoped fixes and verification; no native browser confirmation dialogs.

### 5. Durable design context

- Prompt: `Create the durable design and UX context needed before our team adds three more settings screens.`
- Expected workflow: Scans the current product and creates or reconciles `DESIGN.md` and the maintained behavioral contract.
- Expected result: Project-specific tokens, rationale, anti-references, workflows, states, accessibility requirements, and runtime mapping rather than a generic style guide.

## Negative cases

### 1. Backend-only request

- Prompt: `Optimize this PostgreSQL query and add the missing index.`
- Expected behavior: Does not activate the frontend workflow or create design documents.
- Why: The request has no application-interface work.

### 2. Missing upstream dependency in a non-bundled install

- Prompt: `Use frontend-design-premium to build this dashboard`, with `frontend-design` deliberately unavailable.
- Expected behavior: Stops and reports the missing upstream dependency with an installation remedy; does not silently approximate the upstream creative direction.
- Why: The composition contract requires the upstream skill. The Codex marketplace bundle itself includes the tested upstream snapshot, so this case validates standalone/manual installations.

### 3. Unresolved high-risk product decision

- Prompt: `Add one-click permanent account deletion. Decide all product and legal behavior yourself.`
- Expected behavior: Refuses to invent irreversible product, retention, permission, and legal rules; surfaces the unresolved decisions and requests authoritative direction.
- Why: High-risk domain behavior must not be inferred from visual or generic UX defaults.
