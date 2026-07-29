# Evals — frontend-design-premium

This directory contains structured eval cases for verifying that the skill produces correct, production-quality output.

## Contents

- **`evals.json`** — 24 eval cases with prompts, expected outputs, and file lists (12 with fixtures).
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
     "files": ["src/app/example/page.tsx"]
   }
   ```

2. The `files` field lists the files that the eval is expected to create or modify. Use an empty array for pure design/conversation evals.

3. Run through the full workflow above to record baseline and skill-enabled results.

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

## Notes

- The runner is a **structured capture tool**, not an automated agent harness. It does not run headless browsers or send prompts to an LLM. It helps you record results consistently.
- Eval prompts in Vietnamese (e.g. eval #1) are deliberate — the skill must handle non-English briefs and produce English-level contract decisions.
- Expected outputs are intentionally dense. No single implementation will match every clause; treat `expected_output` as a coverage guide, not a checklist.
