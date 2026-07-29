#!/usr/bin/env python3
"""
Eval runner for frontend-design-premium.

This is a structured evaluation harness. It does not automate an agent;
it provides the scaffolding to run each eval prompt with and without
the skill, and record results for comparison.

Usage:
    python scripts/run_evals.py             # list all evals
    python scripts/run_evals.py --run 1     # record output for eval #1
    python scripts/run_evals.py --run all   # run all evals
    python scripts/run_evals.py --report    # show recorded results
    python scripts/run_evals.py --checklist # print checklist for manual QA

Setup:
    1. Create an empty test project (e.g. next-app or vite-react).
    2. Activate this skill in your agent harness.
    3. Feed each prompt to the agent and save the output.
    4. Run ``--report`` to compare against expected_output.
"""

import io
import json
import sys
import subprocess
import os
from pathlib import Path
from datetime import datetime

# Force UTF-8 for stdout to handle Vietnamese prompts on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

EVALS_PATH = Path(__file__).resolve().parent.parent / "evals" / "evals.json"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "evals" / "results"
SKILL_DIR = Path(__file__).resolve().parent.parent


def load_evals():
    with open(EVALS_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data["evals"], data.get("skill_name", "unknown")


def list_evals(evals):
    print(f"{'ID':>3}  {'Prompt':<70}  {'Output recorded':<16}")
    print("-" * 95)
    for e in evals:
        result_path = RESULTS_DIR / f"eval-{e['id']:02d}.md"
        recorded = "✓" if result_path.exists() else "—"
        prompt = e["prompt"][:68] + ".." if len(e["prompt"]) > 70 else e["prompt"]
        print(f"{e['id']:>3}  {prompt:<70}  {recorded:<16}")
    print()


def print_checklist(evals):
    print("=" * 70)
    print("  Eval Checklist — frontend-design-premium")
    print("=" * 70)
    print()
    for e in evals:
        prompt_short = e["prompt"][:60] + ".." if len(e["prompt"]) > 62 else e["prompt"]
        print(f"  [{e['id']:02d}] {prompt_short}")
        print(f"       Expected: {e['expected_output'][:80]}...")
        print(f"       Files:    {', '.join(e['files']) if e['files'] else '(free text)'}")
        print()
    print("Instructions:")
    print("  1. Create a test project at e.g. /tmp/eval-project")
    print("  2. cd into it")
    print("  3. Feed the prompt to the agent WITH this skill active")
    print("  4. Save agent output to evals/results/eval-NN.md")
    print("  5. Repeat WITHOUT the skill (disabled/baseline)")
    print("  6. Compare against expected_output")
    print("  7. Run --report to review")
    print()


def run_eval(evals, eval_id):
    target = [e for e in evals if e["id"] == eval_id]
    if not target:
        print(f"Error: eval #{eval_id} not found")
        sys.exit(1)
    eval_data = target[0]

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RESULTS_DIR / f"eval-{eval_id:02d}.md"

    print(f"Eval #{eval_id}")
    print(f"Prompt: {eval_data['prompt']}")
    print(f"Expected: {eval_data['expected_output'][:120]}...")
    print()
    print("To record results:")
    print(f"  1. Set up a test project")
    print(f"  2. Run the agent with this prompt and skill active")
    print(f"  3. Save agent output to:\n       {output_path}")
    print(f"  4. (Optional) Run baseline without skill and save to:\n       {output_path.with_suffix('.baseline.md')}")
    print()

    if output_path.exists():
        print(f"Existing result file found: {output_path}")
        cont = input("Overwrite? [y/N] ").strip().lower()
        if cont == "y":
            _capture_output(output_path, eval_data)
    else:
        _capture_output(output_path, eval_data)


def _capture_output(output_path, eval_data):
    print("\nPaste the agent output (Ctrl+D / Ctrl+Z on a new line to finish):")
    print("-" * 40)
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except (EOFError, KeyboardInterrupt):
        pass
    print("-" * 40)

    content = "\n".join(lines)
    timestamp = datetime.now().isoformat(timespec="seconds")
    header = (
        f"# Eval #{eval_data['id']} Result\n\n"
        f"- **Prompt:** {eval_data['prompt']}\n"
        f"- **Recorded:** {timestamp}\n"
        f"- **Status:** \n\n"
        f"## Output\n\n"
    )
    output_path.write_text(header + content, encoding="utf-8")
    print(f"Saved to {output_path}")


def print_report(evals):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results = sorted(RESULTS_DIR.glob("eval-*.md"))
    baseline_results = sorted(RESULTS_DIR.glob("eval-*.baseline.md"))

    if not results and not baseline_results:
        print("No results recorded yet. Run --run <id> first.")
        return

    print("=" * 70)
    print("  Eval Results Report")
    print("=" * 70)
    print()

    for e in evals:
        result_path = RESULTS_DIR / f"eval-{e['id']:02d}.md"
        baseline_path = RESULTS_DIR / f"eval-{e['id']:02d}.baseline.md"
        result_exists = result_path.exists()
        baseline_exists = baseline_path.exists()

        status = "✓" if result_exists else "—"
        baseline_status = "✓" if baseline_exists else "—"

        prompt_short = e["prompt"][:50] + ".." if len(e["prompt"]) > 52 else e["prompt"]
        print(f"  [{e['id']:02d}] {prompt_short}")
        print(f"        Skill: {status}   Baseline: {baseline_status}")
        if result_exists:
            size = len(result_path.read_text(encoding="utf-8"))
            print(f"        Output: {size} chars")
        if result_exists and baseline_exists:
            print(f"        Both recorded — compare manually against expected_output.")
        print()

    print()
    print("Expected outputs are in evals/evals.json")
    print()


def check_validation():
    """Quick pre-flight: validate skill structure."""
    print("Checking skill structure...")
    try:
        result = subprocess.run(
            [sys.executable, str(SKILL_DIR / "scripts" / "validate_skill.py")],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            print("  Validation: OK")
        else:
            print(f"  Validation warnings:\n{result.stdout}{result.stderr}")
    except Exception as exc:
        print(f"  Validation error: {exc}")

    # Check evals.json
    try:
        evals, skill_name = load_evals()
        print(f"  Evals loaded: {len(evals)} cases")
        print(f"  Skill: {skill_name}")
    except (json.JSONDecodeError, KeyError) as exc:
        print(f"  Evals JSON error: {exc}")
        sys.exit(1)

    print()


def main():
    evals, skill_name = load_evals()

    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h", "help"):
        print(f"frontend-design-premium Eval Runner ({skill_name})")
        print()
        print("Commands:")
        print("  (no args)    List all evals")
        print("  --run <id>   Record output for eval <id> (or 'all')")
        print("  --report     Show recorded results summary")
        print("  --checklist  Print structured eval checklist")
        print("  --validate   Run pre-flight validation")
        print()
        list_evals(evals)
        return

    cmd = sys.argv[1]

    if cmd == "--list":
        list_evals(evals)

    elif cmd == "--run":
        check_validation()
        if len(sys.argv) < 3:
            print("Specify eval ID or 'all'")
            sys.exit(1)
        target = sys.argv[2]
        if target == "all":
            for e in evals:
                run_eval(evals, e["id"])
                print()
        else:
            try:
                run_eval(evals, int(target))
            except ValueError:
                print(f"Invalid eval ID: {target}")
                sys.exit(1)

    elif cmd == "--report":
        print_report(evals)

    elif cmd == "--checklist":
        print_checklist(evals)

    elif cmd == "--validate":
        check_validation()

    else:
        print(f"Unknown command: {cmd}")
        print("Use --help for usage.")
        sys.exit(1)


if __name__ == "__main__":
    main()
