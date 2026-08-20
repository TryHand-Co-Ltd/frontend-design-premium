# Canonical UI Resolution and Project Audit

Use this gate for product, admin, SaaS, dashboard, form, table, and CRUD work. Resolve ownership before implementing or materially changing an applicable capability.

## Project UI Resolution

Inspect the current framework/UI stack, locale provider and locale policy, project-root `DESIGN.md` and `UX-CONTRACT.md` (or maintained equivalents), runtime tokens/theme adapters, shared components/behavior utilities, and at least one relevant sibling workflow.

Then resolve applicable rows in the maintained UX contract:

| Capability | Canonical owner | Source of truth | Allowed variants | Verification |
|---|---|---|---|---|
| Table Selection | Shared table-selection primitive | UX contract | page / all-results | component + E2E |
| Select/Listbox | Shared select primitive | DESIGN + UX contract | native / authored | keyboard + popup |
| Date | Shared date primitive | UX contract | typed / native / authored | locale + keyboard + E2E |
| Form | Shared field/schema adapter | UX contract | create / edit | validation E2E |
| Scrollbar | Global application stylesheet | DESIGN.md | geometry exceptions | computed style |
| Toast | Shared notification provider | UX contract | success / warning / info / error | live-region test |
| CRUD | Shared routes/service behavior | UX contract | return / stay | full-flow E2E |

Only applicable rows are required. Keep Table Selection and Select/Listbox separate. An unresolved owner or unresolved high-risk behavior blocks implementation for that capability.

## Ownership precedence and reuse gate

Resolve conflicts in this order:

1. Maintained business/domain/API contract.
2. Maintained `UX-CONTRACT.md` or equivalent.
3. Maintained shared primitive.
4. Consistent sibling workflow.
5. Premium default.

When a canonical owner exists, reuse it or extend it through a business-named variant. Do not introduce an equivalent screen-local component, hook, stylesheet, validation flow, toast, or CRUD behavior. Copy count does not establish authority, and contracts must not be rewritten merely to legitimize drift.

When a deliberate system decision changes, update the contract, runtime owner, and verification evidence in the same changeset. When no owner exists and the behavior will recur, create one shared primitive and record the decision. For a legacy product, migrate the touched workflow and prevent new drift; do not require a big-bang rewrite.

The absence of a UI library does not automatically make native controls canonical. If a maintained project primitive exists, reuse it. Otherwise choose native or authored ownership from product requirements: native is valid when platform-owned geometry, locale, and interaction are accepted; authored is required when the product owns those behaviors.

## Optional project manifest

`premium-ui.json` makes ownership and evidence machine-readable without forcing a framework:

```json
{
  "profile": "product-admin",
  "sourceRoots": ["src"],
  "locale": "ja-JP",
  "canonicalMap": "UX-CONTRACT.md",
  "requiredCapabilities": ["Table Selection", "Select/Listbox", "Date", "Form", "Scrollbar", "Toast", "CRUD"],
  "ownership": {
    "Select/Listbox": "authored",
    "Date": "typed"
  },
  "requiredCommands": ["unit", "e2e", "accessibility", "premium"],
  "commands": {
    "unit": "npm run test:unit",
    "e2e": "npm run test:e2e",
    "accessibility": "npm run test:a11y",
    "premium": "npm run verify:premium"
  },
  "evidence": {
    "crudFullFlow": "tests/e2e/orders-crud.spec.ts",
    "failurePaths": "tests/e2e/orders-failures.spec.ts"
  }
}
```

`ownership` records an intentional native, typed, or authored choice; it is not a waiver for missing accessibility or runtime verification. Evidence paths must point to project-owned tests or reports. The auditor checks their presence but never executes them.

## Project audit

Run from the skill directory:

```text
python scripts/audit_project.py <project-root> --mode report
python scripts/audit_project.py <project-root> --mode strict
```

From another working directory use `python <this-skill-dir>/scripts/audit_project.py ...`. The auditor never executes project commands or edits source/config/contract/product files. It writes `premium-audit.json` by default (or the declared `--output <path>`); pass `--no-write` for stdout-only inspection. `--config <path>` selects a non-default manifest.

- Exit `0`: clean strict audit, or report-mode findings recorded successfully.
- Exit `1`: strict contract violations.
- Exit `2`: malformed/unreadable configuration or source, unresolved canonical ownership, or audit-artifact write failure prevents a complete result.

The JSON report contains a stable schema, file/line when available, rule ID, severity, category, message, remediation, and summary counts. Unreadable configured source/contract files and output-write failures are returned as structured findings rather than tracebacks. Static inspection can detect missing contracts, ownership gaps, selected anti-patterns, and missing evidence declarations. It cannot prove keyboard operation, focus restoration, popup collision, localization quality, accessibility, CRUD correctness, or failure recovery.

The initial form audit includes `form.novalidate-missing` and `form.textarea-resize-missing`. The textarea rule checks literal product markup for `resize-none`/`resize: none`; using the canonical shared Textarea owner remains preferred. Label activation, dynamic `aria-invalid`, live `aria-describedby`, first-error focus, responsive modal behavior, and other runtime interactions require project-owned component/browser evidence.

Run every configured project command separately and report its real result. Never claim runtime compliance from the static audit alone.
