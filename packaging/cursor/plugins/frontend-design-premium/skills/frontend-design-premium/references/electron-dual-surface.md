# Electron + Web Dual-Surface Patterns

Projects with both an Electron desktop app and a web frontend pose unique UX challenges: tokens, behavior, and components may drift between the two surfaces. This reference helps the skill handle dual-surface projects.

## When to read this

The project has both:
- An Electron (or Tauri, Neutralino) desktop app with a renderer process using web UI
- A separate web frontend (Next.js, etc.) sharing the same backend

Examples: namitalk-ai-powered (Electron + Next.js), ai-harness-agents-mornitoring (Tauri + web)

## Principles

1. **One canonical DESIGN.md** — place it at the monorepo root. Both surfaces reference the same tokens, typography, and component contracts. If one surface uses a different CSS framework, document the token mapping.

2. **Shared tokens** — CSS custom properties or a shared token package should be the single source of truth. The web app loads them via Tailwind `@theme`; the Electron app loads them via a `<link>` or style injection.

3. **Shell components diverge, primitives converge** — The app shell (titlebar, sidebar, window chrome) is platform-specific. Primitive components (buttons, inputs, dialogs, cards) should use the same design tokens and interaction contracts.

4. **UX-CONTRACT applies to both** — Behavioral rules (no native dialogs, debounced search, noValidate forms, keyboard accessibility) apply equally to web and Electron renderer.

## What to check

### Token sync
- [ ] Both surfaces reference the same DESIGN.md (or a shared token file).
- [ ] Electron renderer has a way to load CSS custom properties (e.g., via `globals.css` import in bundler config, or a `<style>` injection at app boot).
- [ ] No hardcoded colors/fonts in the Electron codebase that differ from the web app.

### Interaction parity
- [ ] Dialog/modal behavior is consistent (both use app-owned `<Dialog>` / `<Modal>`).
- [ ] Password reveal pattern matches.
- [ ] Search debounce + clear X + IME `isComposing` present in both.
- [ ] Forms use `noValidate` in both.
- [ ] Reduced motion respected in both surfaces.

### Platform differences (document, not fight)
- [ ] Electron window controls, system menus, tray icon are platform-native.
- [ ] Web has app shell with header/footer; Electron hides those in favor of window chrome.
- [ ] Electron may use IPC for clipboard, file system, or auth — document these boundaries.
- [ ] Electron's `<webview>` / `<iframe>` behavior differs from web — note any constraints.

## Register gate for dual-surface

| Surface | Typical register | Notes |
|---------|-----------------|-------|
| Web app (public) | SITE / AUTH | Login, registration, landing |
| Web app (authenticated) | PRODUCT | My-page, admin |
| Electron renderer | PRODUCT | Desktop app with same backend |
| Electron main process | PLATFORM | Window management, tray, updates, IPC |

The Electron renderer should be classified as PRODUCT even if the web has marketing pages — the desktop app is always a product surface.

## Migration status

- [x] 2026-07 — Initial reference added to cover dual-surface projects.
