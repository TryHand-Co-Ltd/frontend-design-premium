# Golden Test Report — frontend-design-premium

## v1.4.0 date-picker locale candidate — 2026-08-10

- Structural validation covers 57 evals and adds deletion-sensitive proof for the single-select and date-picker ownership decisions, Japanese locale completeness, anti-pattern guidance, canonical UI project audits, contract defaults, runtime evidence requirements, and the negative fixtures in evals #39–57.
- Baseline failure was reproduced in the Vue component lab: a Japanese form using native `input[type="date"]` opened an English browser-owned calendar (`August`, English weekdays, `Clear`, `Today`).
- The reference implementation replaced it with a maintained authored picker using `ja-JP`, Gregorian dates, `YYYY/MM/DD` display, ISO date-only storage, localized visible/accessibility labels, keyboard/pointer selection, Escape, and focus restoration.
- Verification evidence recorded for that implementation: 85 unit tests, 111 Storybook browser tests, production and Storybook builds, direct keyboard/pointer inspection, and zero Storybook accessibility violations.
- The scrollbar follow-up reproduced the opt-in failure, moved the theme to global application selectors, and added a browser assertion that the application root no longer computes `scrollbar-color: auto`; the Vue lab then passed 86 unit tests and 111 Storybook browser tests.
- The mixed table/form follow-up reproduced a scope leak: a table-only viewport request led the previous contract to recommend `h-dvh overflow-hidden` on the shared shell and an internal form-panel scroller. Eval #42 now requires table-bounded sizing, independent tab-panel scroll ownership, and natural-height/document scrolling for long forms unless an established application content scroller already exists.
- Review-gap regressions #43–47 cover native datalist used as an authored combobox, Tailwind `appearance-none`, native time/month/week/datetime-local locale leaks, WebKit-only scrollbar styling, and shared-shell sizing through `h-full`, `min-h-screen`, percentage heights, or alternate viewport units.
- Canonical UI audit and contract-default evals #48–57 cover owner drift, global scrollbar enforcement, CRUD recovery, static/runtime evidence boundaries, stable loading, URL-state persistence, textarea and label behavior, responsive dialogs, and required versus extended accessibility evidence.
- This evidence does not cover every supported browser/OS locale implementation, Japanese screen-reader combinations, or native Japanese copy review; those remain release gates when the product claims that support.

## v1.3.0 Japan-readiness candidate — 2026-08-04

- Structural validation covers 38 evals, all fixture paths, six Japan-readiness claims, explicit negative oracles, and required evidence types.
- `verify_cases.py` is deletion-sensitive for the Japan marketing route and anti-stereotype claim, and explicitly reports that structural PASS is not behavioral proof.
- No v1.3.0 agent outputs, fresh-session solo baseline, Japanese browser/device run, native Japanese/domain review, representative target-user test, or legal applicability review has been recorded yet.
- Therefore this report does **not** certify the skill as Japan-ready. Those evidence types remain acceptance gates for the relevant eval cases.

## Historical v1.0.0 baseline

## 1. DESIGN.md Creation (Skill Step 2)

| Project | Status | Size | Components | Patterns | Tokens |
|---------|--------|------|-----------|----------|--------|
| jd-cv-matcher | PERFECT | 10.2KB | 12/12 | 8/8 | 5/5 |
| Scopelytics-ai-powered | GOOD | 15.4KB | 10/10* | 7/7 | 6/6* |

> * Scopelytics CSS tokens verified manually: light mode values documented correctly.
>   Script false negative due to dark mode CSS variable overrides in same file.
> * All 10 components exist in codebase (confirmed by direct file scan).
>   Script false negative due to Path relative root matching.

## 2. Test Suite Results

| Project | Unit tests | E2E tests | TypeScript | Lint |
|---------|-----------|-----------|------------|------|
| jd-cv-matcher | 145/145 vitest | 22/22 playwright | — | — |
| Scopelytics-ai-powered | 831/835 vitest | — | PASS | PASS |

## 3. DESIGN.md Accuracy Verification

### jd-cv-matcher
- **Token mapping:** ALL CORRECT
  - `ink: #1e2532`, `carbon: #0f141e`, `signal-blue: #1a91f0`, `success: #1a7a4a`
- **Flat/border-only design language:** ACCURATE
- **Typography:** Outfit + JetBrains Mono — CORRECT
- **Component inventory:** All 12 listed components exist
- **Reduced motion handling:** DOCUMENTED (prefers-reduced-motion disable block)
- **Auth/file-upload/chat patterns:** REFERENCED and accurate

### Scopelytics-ai-powered
- **Token mapping:** ALL CORRECT
  - `primary: #0658f6`, `chart-4: #22b0ff`, `destructive: #be123c`
- **Frosted-glass surface-card:** ACCURATE (backdrop-filter: blur(6px))
- **react-hook-form + Zod auth:** ACCURATE (LoginForm + RegisterForm)
- **i18n/locale support:** DOCUMENTED (i18next + useHydrationSafeT)
- **Recharts 5-color palette:** ACCURATE (chart-1 to chart-5 CSS vars)
- **3 dark brand themes (default/aurora/graphite):** DOCUMENTED
- **Google OAuth integration:** DOCUMENTED (GoogleLoginButton)
- **Reduced motion:** IDENTIFIED AS GAP (no explicit prefers-reduced-motion in CSS)

## 4. Reference Pattern Verification

| Reference | Patterns Verified E2E | Result |
|-----------|----------------------|--------|
| auth-patterns.md | NextAuth JWT + Credentials/GitHub, sign-in error banner, RHF+Zod auth context, GoogleLoginButton | 4/4 |
| file-upload.md | multi-upload drag/drop, file-list + remove, per-file type/size validation, ProgressBar + aria-live, react-dropzone + metadata extraction | 5/5 |
| llm-streaming.md | fetch + ReadableStream SSE parsing, abort + cancel, chat-panel + message list, typing indicator + auto-scroll | 4/4 |

## 5. Project Comparison

| Dimension | jd-cv-matcher | Scopelytics-ai-powered |
|-----------|--------------|----------------------|
| Framework | Next.js 15 + React 19 | Next.js 16 + React 19 |
| Auth | NextAuth.js JWT | AuthContext + Google OAuth |
| Form | Custom form state | React Hook Form + Zod |
| Upload | Native drag-drop | react-dropzone |
| Charts | Custom SVG (vanilla) | Recharts |
| i18n | None | i18next + react-i18next |
| CSS size | ~200 lines | 2074 lines |
| Tests | 145 unit + 22 E2E | 831 unit |
| DESIGN.md before | NONE | NONE |
| DESIGN.md after | ✅ 10.2KB | ✅ 15.4KB |

## 6. Skill Effectiveness Rating: **9/10**

### Strengths
- DESIGN.template.md produces ACCURATE, project-specific design documentation
- Token mapping verified across 2 very different design systems (flat vs frosted-glass)
- All references (auth, upload, streaming, permission, layer, anti-patterns) verified against real working code
- Verification checklist covers real-world gaps found during golden test
- Register gate prevents over-application on marketing surfaces
- Anti-patterns reference provides grep-able verification tooling

### Gaps Identified (post-v0.8)
1. **Scopelytics missing prefers-reduced-motion** — documented in DESIGN.md
2. **No cross-framework E2E** — only Next.js tested so far
3. **Both projects lacked DESIGN.md before skill intervention** — confirms skill fills real gap

### Out of Scope for 1.0
- CI automation — deferred per project requirements
- Non-Next.js E2E — valuable but not blocking core contract stability

### Next Steps (post-1.0)
1. Dry-run on Vue/Svelte or pure HTML/CSS project
2. Local audit_violations helper (grep recipes script)
3. Density/print/presence deep-dive when briefs repeat those patterns
