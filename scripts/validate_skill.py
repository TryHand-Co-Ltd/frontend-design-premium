#!/usr/bin/env python3
"""Validate this skill's portable structure and local references."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
DESIGN_TEMPLATE = ROOT / "assets" / "DESIGN.template.md"
PILOT_MANIFEST = ROOT / "integrations" / "pilot.json"


def where_npx() -> str | None:
    """Find the npx executable, trying .cmd extension on Windows first."""
    for candidate in ["npx.cmd", "npx.exe", "npx"]:
        try:
            result = subprocess.run(
                [candidate, "--version"],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                return candidate
        except FileNotFoundError:
            continue
    return None


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("SKILL.md frontmatter is not closed")
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if line.startswith((" ", "\t")) or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip("'\"")
    return values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on UNTESTED, MISSING, UNTRUSTED, or INCOMPATIBLE upstream",
    )
    args, _ = parser.parse_known_args()

    errors: list[str] = []
    warnings: list[str] = []

    if not SKILL.is_file():
        print(f"ERROR: missing {SKILL}", file=sys.stderr)
        return 1

    text = SKILL.read_text(encoding="utf-8")
    try:
        meta = frontmatter(text)
    except ValueError as error:
        errors.append(str(error))
        meta = {}

    version_match = re.search(r'(?m)^\s+version:\s*["\']?([^"\'\n]+)', text)
    skill_version = version_match.group(1).strip() if version_match else ""

    name = meta.get("name", "")
    description = meta.get("description", "")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        errors.append("name must contain lowercase letters, digits, and single hyphens only")
    if not 1 <= len(name) <= 64:
        errors.append("name must be 1-64 characters")
    if ROOT.name != name:
        errors.append(f"directory name {ROOT.name!r} must match skill name {name!r}")
    if not 1 <= len(description) <= 1024:
        errors.append("description must be 1-1024 characters")
    if "frontend-design" not in description:
        errors.append("description must declare the frontend-design dependency")
    if "DESIGN.md" not in description or "references/design-context-lifecycle.md" not in text:
        errors.append("skill must declare and load the DESIGN.md lifecycle")
    for required_reference in (
        "references/token-mapping.md",
        "references/consistency-migration.md",
    ):
        if required_reference not in text:
            errors.append(f"skill must route applicable work to {required_reference}")

    line_count = len(text.splitlines())
    if line_count >= 500:
        errors.append(f"SKILL.md has {line_count} lines; keep it below 500")

    relative_refs = set(
        re.findall(r"(?<![\w.-])((?:references|assets|scripts)/[A-Za-z0-9_.-]+)", text)
    )
    for relative in sorted(relative_refs):
        if not (ROOT / relative).is_file():
            errors.append(f"missing referenced file: {relative}")

    expected = [
        "references/design-context-lifecycle.md",
        "references/token-mapping.md",
        "references/consistency-migration.md",
        "references/interaction-contract.md",
        "references/navigation-layout.md",
        "references/data-entry-patterns.md",
        "references/async-resilience.md",
        "references/consistency-system.md",
        "references/japanese-localization.md",
        "references/decision-matrix.md",
        "references/anti-patterns.md",
        "references/permission-ui.md",
        "references/layer-contract.md",
        "references/auth-patterns.md",
        "references/file-upload.md",
        "references/llm-streaming.md",
        "references/verification-checklist.md",
        "references/research-sources.md",
        "assets/DESIGN.template.md",
        "assets/UX-CONTRACT.template.md",
        "references/e2e-audit-prompt.md",
        "references/electron-dual-surface.md",
        "references/pilot-review.md",
        "evals/evals.json",
        "integrations/pilot.json",
    ]
    for relative in expected:
        if not (ROOT / relative).is_file():
            errors.append(f"missing expected resource: {relative}")

    if PILOT_MANIFEST.is_file():
        try:
            pilot = json.loads(PILOT_MANIFEST.read_text(encoding="utf-8"))
            if pilot.get("schema_version") != 1:
                errors.append("integrations/pilot.json schema_version must be 1")
            skill = pilot.get("skill", {})
            if skill.get("name") != name:
                errors.append("integrations/pilot.json skill name does not match")
            if skill.get("version") != skill_version:
                errors.append("integrations/pilot.json skill version does not match")
            upstream = pilot.get("upstream", {})
            if not re.fullmatch(r"[0-9a-f]{40}", upstream.get("revision", "")):
                errors.append("integrations/pilot.json upstream revision must be a full commit SHA")
            if not re.fullmatch(r"[0-9a-f]{64}", upstream.get("skill_sha256", "")):
                errors.append("integrations/pilot.json upstream digest must be SHA-256")
            review_policy = pilot.get("pilot", {}).get("review_policy", "")
            if not review_policy or not (ROOT / review_policy).is_file():
                errors.append("integrations/pilot.json review policy is missing")
        except (json.JSONDecodeError, OSError) as error:
            errors.append(f"invalid integrations/pilot.json: {error}")

    eval_path = ROOT / "evals" / "evals.json"
    if eval_path.is_file():
        try:
            evals = json.loads(eval_path.read_text(encoding="utf-8"))
            if evals.get("skill_name") != name:
                errors.append("evals/evals.json skill_name does not match")
            eval_cases = evals.get("evals", [])
            if len(eval_cases) < 10:
                errors.append("fewer than ten production/design-context eval prompts")
            eval_ids = [case.get("id") for case in eval_cases if isinstance(case, dict)]
            if len(eval_ids) != len(set(eval_ids)):
                errors.append("eval IDs must be unique")
        except (json.JSONDecodeError, OSError) as error:
            errors.append(f"invalid evals/evals.json: {error}")

    if DESIGN_TEMPLATE.is_file():
        design_text = DESIGN_TEMPLATE.read_text(encoding="utf-8")
        if not design_text.startswith("---\n") or "\nversion: alpha\n" not in design_text:
            errors.append("DESIGN template must use alpha YAML frontmatter")
        canonical_sections = [
            "## Overview",
            "## Colors",
            "## Typography",
            "## Layout",
            "## Elevation & Depth",
            "## Shapes",
            "## Components",
            "## Do's and Don'ts",
        ]
        positions = [design_text.find(section) for section in canonical_sections]
        if any(position < 0 for position in positions):
            errors.append("DESIGN template is missing a canonical section")
        elif positions != sorted(positions):
            errors.append("DESIGN template sections are not in canonical order")

        # Run designmd lint
        npx_cmd = where_npx()
        if npx_cmd is None:
            warnings.append("designmd lint skipped — npx not found in PATH")
        else:
            try:
                result = subprocess.run(
                    [npx_cmd, "-p", "@google/design.md", "designmd", "lint", str(DESIGN_TEMPLATE)],
                    capture_output=True, text=True, timeout=120,
                )
                if result.returncode != 0:
                    errors.append(f"designmd lint crashed: {result.stderr[:200]}")
                else:
                    report = json.loads(result.stdout)
                    n_errors = report["summary"]["errors"]
                    n_warnings = report["summary"]["warnings"]
                    if n_errors > 0:
                        errors.append(f"designmd lint: {n_errors} error(s), {n_warnings} warning(s)")
                    elif n_warnings > 0:
                        print(f"designmd lint: 0 errors, {n_warnings} warnings (expected — font stack commas)")
                    else:
                        print(f"designmd lint: 0 errors, 0 warnings")
            except FileNotFoundError:
                warnings.append("designmd lint skipped — npx not available via subprocess")
            except (json.JSONDecodeError, KeyError):
                warnings.append("designmd lint skipped — could not parse output")
            except subprocess.TimeoutExpired:
                warnings.append("designmd lint skipped — timed out")

    upstream_status_ok = True
    try:
        from resolve_frontend_design import compatibility_status, find_skill

        upstream = find_skill()
        if upstream:
            compat = compatibility_status(upstream)
            state = compat.get("status", "UNKNOWN")
            print(f"upstream: {upstream}  [{state}]")
            if state not in ("MATCH",):
                msg = f"upstream compatibility: {state} — {compat.get('message', '')}"
                if args.strict:
                    errors.append(msg)
                else:
                    warnings.append(msg)
                upstream_status_ok = False
        else:
            msg = "frontend-design dependency is not currently discoverable"
            if args.strict:
                errors.append(msg)
            else:
                warnings.append(msg)
            upstream_status_ok = False
    except Exception as error:
        msg = f"upstream resolver exception: {error}"
        if args.strict:
            errors.append(msg)
        else:
            warnings.append(msg)
        upstream_status_ok = False

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if errors:
        return 1
    print(
        f"OK: {name} ({line_count} SKILL.md lines, "
        f"{len(relative_refs)} referenced resources)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
