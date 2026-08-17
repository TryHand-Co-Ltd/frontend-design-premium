# Evals — frontend-design-premium

This directory contains structured eval cases for verifying that the skill produces correct, production-quality output.

## Contents

- **`evals.json`** — 57 eval cases with prompts, expected outputs, file lists, and a machine-validated Japan-readiness claim matrix.
- **`fixtures/`** — Broken/input fixtures wired from `evals.json` `files` entries.
- **`results/`** — Recorded agent output for each eval (created by the runner).

## How to run evals

### Quick start

```bash
# List all evals
python scripts/run_evals.py

# Print a checklist for manual QA
python scripts/run_evals.py --checklist

# Show recorded results
python scripts/run_evals.py --report

# Validate skill structure
python scripts/run_evals.py --validate
```

### Recording eval output

Each eval records agent output for comparison against `expected_output`.

```bash
# Record a single eval
python scripts/run_evals.py --run 1

# Record all evals sequentially
python scripts/run_evals.py --run all
```

When prompted, paste the agent output into the terminal.

The runner saves output to `evals/results/eval-NN.md`.

### Full eval workflow

1. **Set up a clean test project** — a fresh Next.js or Vite app, or a representative real project:

   ```bash
   npx create-next-app@latest eval-project --typescript
   cd eval-project
   ```

2. **Run with the skill enabled.** Activate `frontend-design-premium` in your harness, feed the eval prompt, and paste the result:

   ```bash
   python scripts/run_evals.py --run 1
   ```

3. **Run without the skill (baseline).** Disable the skill or deactivate it, feed the same prompt, and save to the baseline file:

   ```bash
   # Save manually to evals/results/eval-01.baseline.md
   ```

4. **Compare.** Use the difference report:

   ```bash
   python scripts/run_evals.py --report
   ```

   Compare each result against the `expected_output` field in `evals.json`.

5. **Update `.gitignore`** if needed to avoid committing transient outputs.

### What to check

For each eval, verify:

- Does the output match the expected behavior described in `expected_output`?
- Are the right reference files loaded (no unnecessary ones)?
- Are production contracts applied correctly?
- Are there hallucinated patterns not present in the codebase?
- Can the output be implemented without further clarification?

## Adding a new eval

To add a case:

1. Append to the `evals` array in `evals.json`:

   ```json
   {
     "id": 13,
     "prompt": "Your eval prompt here",
     "expected_output": "What the skill should produce",
      "files": ["src/app/example/page.tsx"],
      "claims": ["optional_machine_validated_claim"],
      "evidence_required": ["browser-workflow"],
      "negative_oracle": "What broken or trivial output must fail this eval."
   }
   ```

2. The `files` field lists the files that the eval is expected to create or modify. Use an empty array for pure design/conversation evals.

3. For Japan-readiness cases, update `japan_readiness_claims` and include explicit evidence types plus a negative oracle. Every fixture path must exist.

4. Run through the full workflow above to record baseline and skill-enabled results.

## Eval categories

| IDs | Category | Description |
|-----|----------|-------------|
| 1–3 | Production behavior | Tables, CRUD, search, dialogs, Japanese locale |
| 4 | Negative scope | Marketing-only task — skill should not force CRUD contracts |
| 5–6 | DESIGN.md lifecycle | Seed (new app) and scan (existing app) |
| 7–8 | Advanced inputs | Wizard, upload, combobox, responsive table |
| 9 | Async resilience | Optimistic updates, autosave, multi-tab, session expiry |
| 10 | Long-running operations | CSV import, background processing, offline recovery |
| 11 | Keyboard and accessibility | Shortcuts, command palette, drag alternatives |
| 12 | Token mapping and theming | Ownership model, drift gates, theme switching |
| 13–19 | Packs / migration / forms | Auth, upload, streaming, migration, profile, tokens |
| 20 | Non-UI decline | Backend Python task — skill must not activate UI contracts |
| 21–22 | Destructive + UX contract | AlertDialog danger + UX-CONTRACT draft |
| 23–24 | On-demand packs | Permission UI (hide/disable/403) + overlay layer contract |
| 25–26 | Business authority | ADR/API evidence, conflict handling, high-risk escalation |
| 27–38 | Japan readiness | Market/locale separation, IME beyond search, content/typography, representative audiences, regulated escalation, anti-stereotype, marketing routing |
| 39 | Single-select popup | Native-versus-authored decision, trigger/popup geometry, accessibility, and browser verification |
| 40 | Date-picker locale | Native-versus-authored decision, complete Japanese calendar locale, typed storage, and browser verification |
| 41 | Global scrollbar baseline | Automatic product-owned surface coverage, standards and engine fallbacks, forced colors, and runtime evidence |
| 42 | Table/form scroll ownership | Table-bounded viewport sizing, natural-height forms, independent tab contracts, and regression verification |
| 43–47 | Review-gap regressions | Native datalist, `appearance-none`, sibling native pickers, WebKit-only scrollbars, and shared-shell height variants |
| 48–52 | Canonical UI project audit | Canonical-owner drift, opt-in scrollbar gaps, CRUD failure paths, stable JSON findings, and runtime-evidence boundaries |
| 53–57 | Contract defaults and accessibility | Default loading indicator, URL-state persistence, textarea/label rules, responsive dialogs, and required-versus-extended evidence |

## Notes

- The runner is a **structured capture tool**, not an automated agent harness. It does not run headless browsers or send prompts to an LLM. It helps you record results consistently.
- `validate_skill.py` and `verify_cases.py` prove structure, claim coverage, fixture wiring, and negative-oracle presence only. They do not prove natural Japanese, browser behavior, target-user fit, or legal applicability.
- Japan-ready acceptance must attach the `evidence_required` types declared by the case. Native Japanese/domain review cannot be replaced by keyword counts or machine translation.
- Eval prompts in Vietnamese (e.g. eval #1) are deliberate — the skill must handle non-English briefs and produce English-level contract decisions.
- Expected outputs are intentionally dense. No single implementation will match every clause; treat `expected_output` as a coverage guide, not a checklist.
