#!/usr/bin/env python3
"""Deterministic, read-only audit for frontend-design-premium projects."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 1
SOURCE_SUFFIXES = {".vue", ".tsx", ".jsx", ".ts", ".js", ".svelte", ".html", ".css", ".scss"}
IGNORED_PARTS = {"node_modules", ".git", "dist", "build", "coverage", ".next", ".nuxt"}
MAP_COLUMNS = ("Capability", "Canonical owner", "Source of truth", "Allowed variants", "Verification")
KNOWN_CAPABILITIES = {"Table Selection", "Select/Listbox", "Date", "Form", "Scrollbar", "Toast", "CRUD"}


@dataclass(frozen=True)
class Finding:
    file: str
    line: int | None
    rule_id: str
    severity: str
    category: str
    message: str
    remediation: str

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["ruleId"] = payload.pop("rule_id")
        return payload


@dataclass(frozen=True)
class AuditResult:
    mode: str
    project_root: Path
    findings: tuple[Finding, ...]

    def to_dict(self) -> dict[str, object]:
        ordered = sorted(
            self.findings,
            key=lambda item: (item.category, item.rule_id, item.file, item.line or 0, item.message),
        )
        return {
            "schemaVersion": SCHEMA_VERSION,
            "mode": self.mode,
            "projectRoot": str(self.project_root),
            "findings": [item.to_dict() for item in ordered],
            "summary": {
                "total": len(ordered),
                "errors": sum(item.severity == "error" for item in ordered),
                "warnings": sum(item.severity == "warning" for item in ordered),
                "violations": sum(item.category == "violation" for item in ordered),
                "unresolved": sum(item.category == "unresolved" for item in ordered),
            },
        }


def finding(
    rule_id: str,
    message: str,
    remediation: str,
    *,
    file: str = "premium-ui.json",
    line: int | None = None,
    severity: str = "error",
    category: str = "violation",
) -> Finding:
    return Finding(file, line, rule_id, severity, category, message, remediation)


def relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return str(path.resolve())


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def load_manifest(path: Path) -> tuple[dict[str, Any], list[Finding]]:
    if not path.exists():
        return {}, []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return {}, [finding(
            "config.invalid-json",
            f"Cannot parse project manifest: {error}",
            "Fix the JSON syntax or pass --config with a valid premium-ui.json file.",
            file=str(path),
            category="unresolved",
        )]
    if not isinstance(payload, dict):
        return {}, [finding(
            "config.invalid-json",
            "Project manifest must contain a JSON object.",
            "Replace the top-level JSON value with an object.",
            file=str(path),
            category="unresolved",
        )]
    return payload, []


def parse_canonical_map(text: str) -> tuple[set[str], bool]:
    lines = text.splitlines()
    expected = [column.casefold() for column in MAP_COLUMNS]
    for index, raw_line in enumerate(lines):
        cells = [cell.strip() for cell in raw_line.strip().strip("|").split("|")]
        if [cell.casefold() for cell in cells] != expected:
            continue
        rows: set[str] = set()
        for candidate in lines[index + 2 :]:
            if not candidate.strip().startswith("|"):
                break
            row = [cell.strip() for cell in candidate.strip().strip("|").split("|")]
            if len(row) == len(MAP_COLUMNS) and row[0] in KNOWN_CAPABILITIES and all(row[1:]):
                rows.add(row[0])
        return rows, True
    return set(), False


def source_roots(project_root: Path, manifest: dict[str, Any]) -> list[Path]:
    configured = manifest.get("sourceRoots")
    if isinstance(configured, list) and all(isinstance(value, str) for value in configured):
        roots = [project_root / value for value in configured]
    else:
        roots = [project_root / value for value in ("src", "app", "pages")]
    existing = [root for root in roots if root.exists() and root.is_dir()]
    return existing or [project_root]


def iter_source_files(project_root: Path, manifest: dict[str, Any]) -> Iterable[Path]:
    seen: set[Path] = set()
    for root in source_roots(project_root, manifest):
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
                continue
            if any(part in IGNORED_PARTS for part in path.parts):
                continue
            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                yield path


def inspect_contracts(project_root: Path, manifest: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    if manifest.get("profile") != "product-admin":
        return findings
    if not (project_root / "DESIGN.md").exists():
        findings.append(finding(
            "contract.design-missing",
            "A product/admin project has no maintained DESIGN.md.",
            "Create DESIGN.md or document the maintained equivalent in project policy.",
            file="DESIGN.md",
        ))
    map_value = manifest.get("canonicalMap", "UX-CONTRACT.md")
    map_path = project_root / map_value if isinstance(map_value, str) else project_root / "UX-CONTRACT.md"
    if not map_path.exists():
        findings.append(finding(
            "contract.ux-missing",
            "A product/admin project has no maintained UX contract.",
            "Create UX-CONTRACT.md with a Canonical UI Map.",
            file=relative(project_root, map_path),
            category="unresolved",
        ))
        findings.append(finding(
            "canonical.map-missing",
            "Canonical UI ownership cannot be resolved because its map is missing.",
            "Add the exact five-column Canonical UI Map to the configured UX contract.",
            file=relative(project_root, map_path),
            category="unresolved",
        ))
        return findings
    text = map_path.read_text(encoding="utf-8")
    rows, found_header = parse_canonical_map(text)
    if not found_header:
        findings.append(finding(
            "canonical.map-missing",
            "The configured UX contract has no Canonical UI Map with the required columns.",
            "Add the exact Capability, Canonical owner, Source of truth, Allowed variants, and Verification columns.",
            file=relative(project_root, map_path),
            category="unresolved",
        ))
        return findings
    required = manifest.get("requiredCapabilities", [])
    if not isinstance(required, list):
        required = []
    for capability in sorted(value for value in required if isinstance(value, str)):
        if capability not in rows:
            findings.append(finding(
                "canonical.owner-unresolved",
                f"Canonical owner is unresolved for {capability}.",
                f"Add a complete {capability} row to the Canonical UI Map before implementation.",
                file=relative(project_root, map_path),
                category="unresolved",
            ))
    if rows and required and rows != set(required):
        missing = sorted(set(required) - rows)
        if missing:
            findings.append(finding(
                "canonical.map-incomplete",
                f"Canonical UI Map is incomplete: {', '.join(missing)}.",
                "Complete every capability declared in requiredCapabilities.",
                file=relative(project_root, map_path),
                category="unresolved",
            ))
    return findings


def inspect_source(project_root: Path, manifest: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    ownership = manifest.get("ownership", {})
    ownership = ownership if isinstance(ownership, dict) else {}
    for path in iter_source_files(project_root, manifest):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        name = relative(project_root, path)

        patterns = (
            (r'href\s*=\s*["\']#["\']', "affordance.empty-href", "Empty hash links look actionable but have no destination.", "Use a real route/action or render non-interactive text."),
            (r"<form\b(?![^>]*(?:novalidate|noValidate))[^>]*>", "form.novalidate-missing", "Application-owned form does not declare its validation owner.", "Add noValidate/novalidate and implement the canonical validation contract."),
        )
        for pattern, rule_id, message, remediation in patterns:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                findings.append(finding(rule_id, message, remediation, file=name, line=line_number(text, match.start())))

        for match in re.finditer(r"<button\b([^>]*)>", text, flags=re.IGNORECASE):
            attributes = match.group(1)
            if re.search(r"(?:disabled|@click|v-on:click|onclick|onClick|type\s*=\s*[\"']submit[\"'])", attributes):
                continue
            findings.append(finding(
                "affordance.actionless-button",
                "Enabled literal button has no detectable action or submit behavior.",
                "Connect the button to a real action, make it a submit button, or disable/remove it.",
                file=name,
                line=line_number(text, match.start()),
            ))

        for match in re.finditer(r"<textarea\b([^>]*)>", text, flags=re.IGNORECASE):
            attributes = match.group(1)
            has_resize_none = bool(
                re.search(r"\bresize-none\b", attributes)
                or re.search(r"resize\s*:\s*none", attributes, flags=re.IGNORECASE)
            )
            if has_resize_none:
                continue
            findings.append(finding(
                "form.textarea-resize-missing",
                "Literal product textarea does not show evidence of the canonical resize-none rule.",
                "Use the shared Textarea owner or apply resize-none/resize: none with adequate height or auto-grow behavior.",
                file=name,
                line=line_number(text, match.start()),
            ))

        if re.search(r"<select\b", text, flags=re.IGNORECASE) and ownership.get("Select/Listbox") != "native":
            findings.append(finding(
                "ownership.native-select-undecided",
                "Native select is used without an explicit native ownership decision.",
                "Record Select/Listbox as native or reuse the authored canonical owner.",
                file=name,
                line=line_number(text, re.search(r"<select\b", text, flags=re.IGNORECASE).start()),
                category="unresolved",
            ))
        date_match = re.search(r"<input\b[^>]*type\s*=\s*[\"']date[\"']", text, flags=re.IGNORECASE)
        if date_match and ownership.get("Date") != "native":
            findings.append(finding(
                "ownership.native-date-undecided",
                "Native date input is used without an explicit native ownership decision.",
                "Record Date as native or reuse the typed/authored canonical owner.",
                file=name,
                line=line_number(text, date_match.start()),
                category="unresolved",
            ))

        has_table = bool(re.search(r"<table\b|DataTable|data-table", text, flags=re.IGNORECASE))
        has_form = bool(re.search(r"<form\b|AppForm", text, flags=re.IGNORECASE))
        viewport_locked = bool(re.search(r"(?:h-screen|h-dvh|min-h-screen|100vh|100dvh)", text))
        overflow_hidden = bool(re.search(r"overflow-hidden|overflow\s*:\s*hidden", text))
        if has_table and has_form and viewport_locked and overflow_hidden:
            findings.append(finding(
                "layout.shared-shell-overflow",
                "Table viewport sizing leaks into a shared page/form shell.",
                "Give the table body its own bounded scroll surface and let the page/form shell size naturally.",
                file=name,
                line=1,
            ))

        if path.suffix.lower() in {".css", ".scss"} and "::-webkit-scrollbar" in text:
            webkit_offset = text.index("::-webkit-scrollbar")
            if "scrollbar-color" not in text and "scrollbar-width" not in text:
                findings.append(finding(
                    "scrollbar.webkit-only",
                    "Scrollbar theme uses only WebKit engine selectors.",
                    "Add global scrollbar-color and scrollbar-width standards properties plus fallbacks.",
                    file=name,
                    line=line_number(text, webkit_offset),
                ))
            selector_prefix = text[max(0, text.rfind("}", 0, webkit_offset) + 1):webkit_offset]
            if re.search(r"\.(?:custom-scrollbar|scrollbar|ui-scroll)", selector_prefix):
                findings.append(finding(
                    "scrollbar.opt-in-base",
                    "Base scrollbar theming is activated by an opt-in class.",
                    "Apply base scrollbar tokens globally; reserve classes for geometry or semantic exceptions.",
                    file=name,
                    line=line_number(text, webkit_offset),
                ))
    return findings


def inspect_evidence(project_root: Path, manifest: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    commands = manifest.get("commands", {})
    commands = commands if isinstance(commands, dict) else {}
    required = manifest.get("requiredCommands", [])
    required = required if isinstance(required, list) else []
    for command in sorted(value for value in required if isinstance(value, str)):
        if not isinstance(commands.get(command), str) or not commands[command].strip():
            findings.append(finding(
                "evidence.command-missing",
                f"Required runtime verification command is missing: {command}.",
                f"Configure commands.{command} and run it separately; the static auditor will not execute it.",
            ))

    evidence = manifest.get("evidence", {})
    evidence = evidence if isinstance(evidence, dict) else {}
    for key, rule_id, message in (
        ("crudFullFlow", "evidence.crud-flow-missing", "Declared CRUD full-flow evidence is missing."),
        ("failurePaths", "evidence.failure-path-missing", "Declared failure-path evidence is missing."),
    ):
        value = evidence.get(key)
        if value is None:
            continue
        if not isinstance(value, str) or not (project_root / value).is_file():
            findings.append(finding(
                rule_id,
                message,
                f"Point evidence.{key} to an existing project-owned test or report and run its command separately.",
            ))
    return findings


def audit_project(project_root: Path, mode: str, config_path: Path | None = None) -> AuditResult:
    root = project_root.resolve()
    manifest_path = config_path.resolve() if config_path else root / "premium-ui.json"
    manifest, config_findings = load_manifest(manifest_path)
    if config_findings:
        return AuditResult(mode, root, tuple(config_findings))
    findings = [
        *inspect_contracts(root, manifest),
        *inspect_source(root, manifest),
        *inspect_evidence(root, manifest),
    ]
    return AuditResult(mode, root, tuple(findings))


def exit_code(result: AuditResult) -> int:
    if any(item.rule_id == "config.invalid-json" for item in result.findings):
        return 2
    if result.mode == "report":
        return 0
    if any(item.category == "unresolved" for item in result.findings):
        return 2
    if any(item.category == "violation" and item.severity == "error" for item in result.findings):
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--mode", choices=("report", "strict"), required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--no-write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = audit_project(args.project_root, args.mode, args.config)
    rendered = json.dumps(result.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    sys.stdout.write(rendered)
    if not args.no_write:
        output = args.output or args.project_root / "premium-audit.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    return exit_code(result)


if __name__ == "__main__":
    raise SystemExit(main())
