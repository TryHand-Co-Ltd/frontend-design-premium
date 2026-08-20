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
CLAUDE_PACKAGE_SKILL = (
    ROOT
    / "packaging"
    / "claude"
    / "plugins"
    / "frontend-design-premium"
    / "skills"
    / "frontend-design-premium"
)
CURSOR_PACKAGE_ROOT = (
    ROOT
    / "packaging"
    / "cursor"
    / "plugins"
    / "frontend-design-premium"
)
CURSOR_PACKAGE_SKILL = CURSOR_PACKAGE_ROOT / "skills" / "frontend-design-premium"
PACKAGE_TEXT_SUFFIXES = {".json", ".md", ".py", ".txt", ".yaml", ".yml"}


def package_bytes(path: Path) -> bytes:
    """Return bytes in the canonical form used by deterministic package builders."""
    data = path.read_bytes()
    if path.suffix.lower() in PACKAGE_TEXT_SUFFIXES:
        return data.replace(b"\r\n", b"\n")
    return data


def package_source_pairs(package_skill: Path) -> list[tuple[Path, Path]]:
    """Map canonical source files to their generated package destinations."""
    pairs = [
        (SKILL, package_skill / "SKILL.md"),
        (
            ROOT / "scripts" / "audit_project.py",
            package_skill / "scripts" / "audit_project.py",
        ),
        (
            ROOT / "scripts" / "resolve_frontend_design.py",
            package_skill / "scripts" / "resolve_frontend_design.py",
        ),
    ]
    for source_dir_name in ("references", "assets"):
        source_dir = ROOT / source_dir_name
        for source_path in source_dir.rglob("*"):
            if source_path.is_file():
                pairs.append(
                    (
                        source_path,
                        package_skill
                        / source_dir_name
                        / source_path.relative_to(source_dir),
                    )
                )
    return pairs


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
        "references/canonical-ui-resolution.md",
        "references/design-context-lifecycle.md",
        "references/token-mapping.md",
        "references/consistency-migration.md",
        "references/interaction-contract.md",
        "references/navigation-layout.md",
        "references/data-entry-patterns.md",
        "references/async-resilience.md",
        "references/consistency-system.md",
        "references/japan-market-context.md",
        "references/japanese-content-design.md",
        "references/japanese-visual-layout.md",
        "references/japanese-localization.md",
        "references/japan-regulated-flows.md",
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

    version_manifests = [
        ROOT
        / "packaging"
        / "codex"
        / "plugins"
        / "frontend-design-premium"
        / ".codex-plugin"
        / "plugin.json",
        ROOT
        / "packaging"
        / "claude"
        / "plugins"
        / "frontend-design-premium"
        / ".claude-plugin"
        / "plugin.json",
        CURSOR_PACKAGE_ROOT / "plugin.json",
    ]
    for manifest_path in version_manifests:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("version") != skill_version:
                errors.append(
                    f"{manifest_path.relative_to(ROOT)} version does not match SKILL.md"
                )
        except (json.JSONDecodeError, OSError) as error:
            errors.append(f"invalid {manifest_path.relative_to(ROOT)}: {error}")

    marketplace_path = ROOT / ".claude-plugin" / "marketplace.json"
    try:
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
        plugins = marketplace.get("plugins", [])
        plugin = next(
            (item for item in plugins if item.get("name") == name),
            None,
        )
        if plugin is None:
            errors.append(".claude-plugin/marketplace.json is missing the skill plugin")
        elif plugin.get("version") != skill_version:
            errors.append(".claude-plugin/marketplace.json version does not match SKILL.md")
    except (json.JSONDecodeError, OSError) as error:
        errors.append(f"invalid .claude-plugin/marketplace.json: {error}")

    cursor_marketplace_path = ROOT / ".cursor-plugin" / "marketplace.json"
    try:
        cursor_marketplace = json.loads(
            cursor_marketplace_path.read_text(encoding="utf-8")
        )
        metadata = cursor_marketplace.get("metadata", {})
        if metadata.get("version") != skill_version:
            errors.append(
                ".cursor-plugin/marketplace.json metadata version does not match SKILL.md"
            )
        plugin_root = metadata.get("pluginRoot", "")
        cursor_plugins = cursor_marketplace.get("plugins", [])
        cursor_plugin = next(
            (item for item in cursor_plugins if item.get("name") == name),
            None,
        )
        if cursor_plugin is None:
            errors.append(".cursor-plugin/marketplace.json is missing the skill plugin")
        else:
            if cursor_plugin.get("version") != skill_version:
                errors.append(
                    ".cursor-plugin/marketplace.json plugin version does not match SKILL.md"
                )
            source = cursor_plugin.get("source", "")
            resolved_source = ROOT / plugin_root / source
            if resolved_source.resolve() != CURSOR_PACKAGE_ROOT.resolve():
                errors.append(
                    ".cursor-plugin/marketplace.json source does not resolve to the Cursor package"
                )
    except (json.JSONDecodeError, OSError) as error:
        errors.append(f"invalid .cursor-plugin/marketplace.json: {error}")

    cursor_manifest_path = CURSOR_PACKAGE_ROOT / "plugin.json"
    try:
        cursor_manifest = json.loads(cursor_manifest_path.read_text(encoding="utf-8"))
        if cursor_manifest.get("$schema") != (
            "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
        ):
            errors.append("Cursor Agent Plugin must declare the 1.0.0 schema")
        if cursor_manifest.get("name") != name:
            errors.append("Cursor Agent Plugin name does not match SKILL.md")
    except (json.JSONDecodeError, OSError) as error:
        errors.append(f"invalid {cursor_manifest_path.relative_to(ROOT)}: {error}")

    generated_packages = (
        ("Claude", CLAUDE_PACKAGE_SKILL, "scripts/build_claude_plugin.py"),
        ("Cursor", CURSOR_PACKAGE_SKILL, "scripts/build_cursor_plugin.py"),
    )
    for package_name, package_skill, builder in generated_packages:
        for source_path, packaged_path in package_source_pairs(package_skill):
            relative = packaged_path.relative_to(ROOT)
            if not packaged_path.is_file():
                errors.append(
                    f"{package_name} package is missing generated source: {relative}"
                )
            elif packaged_path.read_bytes() != package_bytes(source_path):
                errors.append(
                    f"{package_name} package source drift: {relative}; run {builder}"
                )

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

            cases_by_id = {
                case.get("id"): case
                for case in eval_cases
                if isinstance(case, dict) and isinstance(case.get("id"), int)
            }
            for case_id, case in cases_by_id.items():
                files = case.get("files", [])
                if not isinstance(files, list):
                    errors.append(f"eval #{case_id} files must be a list")
                    continue
                for fixture in files:
                    if not isinstance(fixture, str) or not fixture:
                        errors.append(f"eval #{case_id} has an invalid fixture path")
                    elif not (eval_path.parent / fixture).is_file():
                        errors.append(f"eval #{case_id} missing fixture: evals/{fixture}")

            required_japan_claims = {
                "market_context",
                "native_copy_typography",
                "ime_non_search",
                "regulated_escalation",
                "anti_stereotype",
                "runtime_verification",
            }
            claim_matrix = evals.get("japan_readiness_claims", {})
            if not isinstance(claim_matrix, dict):
                errors.append("japan_readiness_claims must be an object")
                claim_matrix = {}
            missing_claims = required_japan_claims - set(claim_matrix)
            if missing_claims:
                errors.append(
                    "Japan readiness claim matrix missing: "
                    + ", ".join(sorted(missing_claims))
                )
            for claim in sorted(required_japan_claims):
                case_ids = claim_matrix.get(claim, [])
                if not isinstance(case_ids, list) or not case_ids:
                    errors.append(f"Japan readiness claim {claim!r} has no eval cases")
                    continue
                for case_id in case_ids:
                    case = cases_by_id.get(case_id)
                    if case is None:
                        errors.append(
                            f"Japan readiness claim {claim!r} references missing eval #{case_id}"
                        )
                        continue
                    case_claims = case.get("claims", [])
                    if claim not in case_claims:
                        errors.append(
                            f"eval #{case_id} must declare claim {claim!r}"
                        )
                    if not case.get("negative_oracle"):
                        errors.append(
                            f"eval #{case_id} needs a negative_oracle for {claim!r}"
                        )
                    evidence = case.get("evidence_required", [])
                    if not isinstance(evidence, list) or not evidence:
                        errors.append(
                            f"eval #{case_id} needs evidence_required for {claim!r}"
                        )
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
