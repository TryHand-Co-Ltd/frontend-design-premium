#!/usr/bin/env python3
"""Deterministic, non-executing audit for frontend-design-premium projects."""

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


@dataclass(frozen=True)
class HtmlTag:
    name: str
    attributes: str
    start: int
    end: int
    closing: bool
    self_closing: bool


@dataclass(frozen=True)
class CssRule:
    selector: str
    body: str
    start: int


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


def mask_comments(text: str) -> str:
    """Mask HTML/CSS block comments while preserving offsets and line numbers."""

    def replace(match: re.Match[str]) -> str:
        return "".join("\n" if char == "\n" else " " for char in match.group(0))

    return re.sub(r"<!--.*?-->|/\*.*?\*/", replace, text, flags=re.DOTALL)


def find_tag_end(text: str, start: int) -> int | None:
    html_quote: str | None = None
    expression_quote: str | None = None
    expression_depth = 0
    escaped = False
    for offset in range(start, len(text)):
        char = text[offset]
        if html_quote is not None:
            if char == html_quote:
                html_quote = None
            continue
        if expression_quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == expression_quote:
                expression_quote = None
            continue
        if expression_depth:
            if char in {'"', "'", "`"}:
                expression_quote = char
            elif char == "{":
                expression_depth += 1
            elif char == "}":
                expression_depth -= 1
            continue
        if char in {'"', "'"}:
            html_quote = char
        elif char == "{":
            expression_depth = 1
        elif char == ">":
            return offset + 1
    return None


def find_expression_end(text: str, start: int) -> int:
    """Return the offset after a balanced JSX/template expression."""
    depth = 0
    quote: str | None = None
    escaped = False
    offset = start
    while offset < len(text):
        char = text[offset]
        next_char = text[offset + 1] if offset + 1 < len(text) else ""
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        elif char in {'"', "'", "`"}:
            quote = char
        elif char == "/" and next_char == "/":
            newline = text.find("\n", offset + 2)
            offset = len(text) if newline < 0 else newline
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return offset + 1
        offset += 1
    return len(text)


def is_regex_literal_start(text: str, offset: int, boundary: int = 0) -> bool:
    prefix = text[boundary:offset].rstrip()
    if not prefix:
        return True
    if prefix[-1] in "=([{,:;!?&|+-*%^~<>":
        return True
    return bool(re.search(
        r"\b(?:return|case|throw|yield|await|typeof|instanceof|in|of|delete|void|new)\s*$",
        prefix,
    ))


def find_regex_literal_end(text: str, start: int) -> int | None:
    escaped = False
    character_class = False
    offset = start + 1
    while offset < len(text):
        char = text[offset]
        if char == "\n" and not escaped:
            return None
        if escaped:
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == "[":
            character_class = True
        elif char == "]" and character_class:
            character_class = False
        elif char == "/" and not character_class:
            offset += 1
            while offset < len(text) and text[offset].isalpha():
                offset += 1
            return offset
        offset += 1
    return None


def next_regex_literal(text: str, start: int, limit: int) -> int:
    offset = text.find("/", start, limit)
    while offset >= 0:
        if not text.startswith("//", offset) and is_regex_literal_start(text, offset, start):
            return offset
        offset = text.find("/", offset + 1, limit)
    return -1


def mask_expression_code(text: str) -> str:
    """Mask code literals/comments in an expression while retaining nested JSX tags."""
    output = list(text)
    tag_pattern = re.compile(r"<\s*/?\s*[A-Za-z][\w:-]*\b")
    offset = 0
    while offset < len(text):
        tag = tag_pattern.match(text, offset)
        if tag is not None:
            end = find_tag_end(text, tag.end())
            if end is not None:
                offset = end
                continue
        if text.startswith("//", offset):
            newline = text.find("\n", offset + 2)
            end = len(text) if newline < 0 else newline
            for index in range(offset, end):
                output[index] = " "
            offset = end
            continue
        if text[offset] == "/" and is_regex_literal_start(text, offset):
            end = find_regex_literal_end(text, offset)
            if end is not None:
                for index in range(offset, end):
                    if output[index] != "\n":
                        output[index] = " "
                offset = end
                continue
        if text[offset] in {'"', "'", "`"}:
            quote = text[offset]
            end = offset + 1
            escaped = False
            while end < len(text):
                char = text[end]
                end += 1
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == quote:
                    break
            for index in range(offset, end):
                if output[index] != "\n":
                    output[index] = " "
            offset = end
            continue
        offset += 1
    return "".join(output)


def iter_html_tags(text: str, names: set[str] | None = None) -> Iterable[HtmlTag]:
    searchable = mask_comments(text)
    pattern = re.compile(r"<\s*(?P<closing>/)?\s*(?P<name>[A-Za-z][\w:-]*)\b")
    void_tags = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
    raw_content_tags = {"script", "style"}
    stack: list[str] = []
    offset = 0
    while offset < len(searchable):
        if stack and stack[-1] in raw_content_tags:
            closing = re.search(rf"<\s*/\s*{re.escape(stack[-1])}\b", searchable[offset:], re.IGNORECASE)
            if closing is None:
                return
            candidate = offset + closing.start()
        elif not stack and searchable[offset] in {'"', "'", "`"}:
            quote = searchable[offset]
            offset += 1
            escaped = False
            while offset < len(searchable):
                char = searchable[offset]
                offset += 1
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == quote:
                    break
            continue
        elif not stack and searchable.startswith("//", offset):
            newline = searchable.find("\n", offset + 2)
            offset = len(searchable) if newline < 0 else newline + 1
            continue
        elif not stack and searchable[offset] == "/" and is_regex_literal_start(searchable, offset):
            regex_end = find_regex_literal_end(searchable, offset)
            offset = offset + 1 if regex_end is None else regex_end
            continue
        else:
            candidate = searchable.find("<", offset)
            if candidate < 0:
                return
            if stack:
                expression = searchable.find("{", offset)
                if expression >= 0 and expression < candidate:
                    expression_end = find_expression_end(searchable, expression)
                    searchable = (
                        searchable[:expression]
                        + mask_expression_code(searchable[expression:expression_end])
                        + searchable[expression_end:]
                    )
                    offset = expression + 1
                    continue
            if not stack:
                next_quote = min(
                    (position for quote in ('"', "'", "`") if (position := searchable.find(quote, offset)) >= 0),
                    default=-1,
                )
                next_comment = searchable.find("//", offset)
                next_regex = next_regex_literal(searchable, offset, candidate)
                boundaries = [position for position in (next_quote, next_comment, next_regex) if position >= 0]
                if boundaries and min(boundaries) < candidate:
                    offset = min(boundaries)
                    continue
        match = pattern.match(searchable, candidate)
        if match is None:
            offset = candidate + 1
            continue
        end = find_tag_end(searchable, match.end())
        if end is None:
            return
        name = match.group("name").casefold()
        attributes = searchable[match.end():end - 1]
        closing = bool(match.group("closing"))
        self_closing = attributes.rstrip().endswith("/")
        if names is None or name in names:
            yield HtmlTag(
                name=name,
                attributes=attributes,
                start=match.start(),
                end=end,
                closing=closing,
                self_closing=self_closing,
            )
        if closing:
            match_index = next((index for index in range(len(stack) - 1, -1, -1) if stack[index] == name), None)
            if match_index is not None:
                del stack[match_index:]
        elif not self_closing and name not in void_tags:
            stack.append(name)
        offset = end


def has_attribute(attributes: str, name: str) -> bool:
    return bool(re.search(rf"(?<![\w:-]){re.escape(name)}(?=\s|=|/|$)", attributes, re.IGNORECASE))


def attribute_value(attributes: str, name: str) -> str | None:
    match = re.search(
        rf"(?<![\w:-]){re.escape(name)}\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s/>]+))",
        attributes,
        re.IGNORECASE,
    )
    if match is None:
        return None
    return next((value for value in match.groups() if value is not None), "")


def html_regions(tags: Iterable[HtmlTag], text_length: int) -> list[tuple[HtmlTag, int]]:
    void_tags = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
    stack: list[HtmlTag] = []
    regions: list[tuple[HtmlTag, int]] = []
    for tag in tags:
        if tag.closing:
            match_index = next((
                index for index in range(len(stack) - 1, -1, -1)
                if stack[index].name == tag.name
            ), None)
            if match_index is not None:
                opening = stack[match_index]
                del stack[match_index:]
                regions.append((opening, tag.start))
        elif not tag.self_closing and tag.name not in void_tags:
            stack.append(tag)
    regions.extend((opening, text_length) for opening in stack)
    return regions


def iter_css_rules(text: str) -> Iterable[CssRule]:
    searchable = mask_comments(text)
    stack: list[tuple[str, int, int]] = []
    statement_start = 0
    quote: str | None = None
    escaped = False
    for offset, char in enumerate(searchable):
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {'"', "'"}:
            quote = char
        elif char == ";":
            statement_start = offset + 1
        elif char == "{":
            raw_selector = searchable[statement_start:offset]
            selector = raw_selector.strip()
            selector_start = statement_start + len(raw_selector) - len(raw_selector.lstrip())
            stack.append((selector, selector_start, offset + 1))
            statement_start = offset + 1
        elif char == "}":
            if stack:
                selector, selector_start, body_start = stack.pop()
                yield CssRule(selector, searchable[body_start:offset], selector_start)
            statement_start = offset + 1


def split_selectors(selector: str) -> list[str]:
    """Split a selector list without treating commas inside functions as separators."""
    selectors: list[str] = []
    start = 0
    depth = 0
    quote: str | None = None
    escaped = False
    for offset, char in enumerate(selector):
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        elif char in {'"', "'"}:
            quote = char
        elif char in "([":
            depth += 1
        elif char in ")]":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            selectors.append(selector[start:offset].strip())
            start = offset + 1
    selectors.append(selector[start:].strip())
    return [item for item in selectors if item]


def scrollbar_surfaces(selector: str) -> list[str]:
    surfaces: list[str] = []
    for item in split_selectors(selector):
        match = re.search(r"::\s*-webkit-scrollbar(?:-[a-z-]+)?", item, flags=re.IGNORECASE)
        if match is not None:
            surfaces.append(item[:match.start()].strip())
    return surfaces


def owning_surface(selector: str) -> str:
    """Remove state qualifiers while preserving the selector's element identity."""
    without_attributes = re.sub(r"\[[^\]]*\]", "", selector)
    return re.sub(r"(?<![:\\]):(?!:)[\w-]+(?:\([^()]*\))?", "", without_attributes).strip()


def selector_covers_surface(selector: str, surface: str) -> bool:
    owner = owning_surface(surface)
    for candidate in split_selectors(selector):
        if candidate in {"*", ":root", "html", "body", "html *", "body *", ":where(*)"}:
            return True
        if candidate == surface or candidate == owner:
            return True
    return False


def direct_css_body(body: str) -> str:
    """Mask nested rule bodies so only declarations owned by this rule remain."""
    output = list(body)
    depth = 0
    quote: str | None = None
    escaped = False
    for offset, char in enumerate(body):
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        elif char in {'"', "'"}:
            quote = char
        elif char == "{":
            depth += 1
            output[offset] = " "
        elif char == "}":
            output[offset] = " "
            depth = max(0, depth - 1)
        elif depth and char != "\n":
            output[offset] = " "
    return "".join(output)


def standards_cover_surface(surface: str, rules: Iterable[CssRule]) -> bool:
    properties: set[str] = set()
    for rule in rules:
        if rule.selector.startswith("@") or not selector_covers_surface(rule.selector, surface):
            continue
        body = direct_css_body(rule.body)
        if re.search(r"(?<![-\w])scrollbar-color\s*:", body, flags=re.IGNORECASE):
            properties.add("color")
        if re.search(r"(?<![-\w])scrollbar-width\s*:", body, flags=re.IGNORECASE):
            properties.add("width")
    return properties == {"color", "width"}


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
    try:
        text = map_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        findings.append(finding(
            "canonical.map-unreadable",
            f"The configured Canonical UI Map cannot be read as UTF-8 text: {error}",
            "Point canonicalMap to a readable UTF-8 contract file.",
            file=relative(project_root, map_path),
            category="unresolved",
        ))
        return findings
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
        except (OSError, UnicodeError) as error:
            findings.append(finding(
                "source.unreadable",
                f"Configured source file cannot be read as UTF-8 text: {error}",
                "Convert the source to UTF-8 or remove it from the configured source roots.",
                file=relative(project_root, path),
                category="unresolved",
            ))
            continue
        name = relative(project_root, path)

        for match in re.finditer(r'href\s*=\s*["\']#["\']', text, flags=re.IGNORECASE):
            findings.append(finding(
                "affordance.empty-href",
                "Empty hash links look actionable but have no destination.",
                "Use a real route/action or render non-interactive text.",
                file=name,
                line=line_number(text, match.start()),
            ))

        all_tags = list(iter_html_tags(text))
        tags = [
            tag for tag in all_tags
            if tag.name in {"form", "button", "textarea", "select", "input"}
        ]
        form_depth = 0
        select_tag: HtmlTag | None = None
        native_date_tag: HtmlTag | None = None
        for tag in tags:
            if tag.name == "form":
                if tag.closing:
                    form_depth = max(0, form_depth - 1)
                    continue
                if not has_attribute(tag.attributes, "novalidate"):
                    findings.append(finding(
                        "form.novalidate-missing",
                        "Application-owned form does not declare its validation owner.",
                        "Add noValidate/novalidate and implement the canonical validation contract.",
                        file=name,
                        line=line_number(text, tag.start),
                    ))
                if not tag.self_closing:
                    form_depth += 1
                continue
            if tag.closing:
                continue
            if tag.name == "button":
                button_type = (attribute_value(tag.attributes, "type") or "").casefold()
                has_action = bool(re.search(
                    r"(?:@click(?:\.[\w-]+)*|v-on:click(?:\.[\w-]+)*|onclick)(?=\s|=|$)",
                    tag.attributes,
                    flags=re.IGNORECASE,
                ))
                is_form_submit = button_type not in {"button", "reset"} and (
                    bool(form_depth) or has_attribute(tag.attributes, "form")
                )
                if (
                    has_attribute(tag.attributes, "disabled")
                    or button_type == "submit"
                    or is_form_submit
                ):
                    continue
                if not has_action:
                    findings.append(finding(
                        "affordance.actionless-button",
                        "Enabled literal button has no detectable action or submit behavior.",
                        "Connect the button to a real action, make it a submit button, or disable/remove it.",
                        file=name,
                        line=line_number(text, tag.start),
                    ))
            elif tag.name == "textarea":
                has_resize_none = bool(
                    re.search(r"\bresize-none\b", tag.attributes)
                    or re.search(r"resize\s*:\s*none", tag.attributes, flags=re.IGNORECASE)
                )
                if not has_resize_none:
                    findings.append(finding(
                        "form.textarea-resize-missing",
                        "Literal product textarea does not show evidence of the canonical resize-none rule.",
                        "Use the shared Textarea owner or apply resize-none/resize: none with adequate height or auto-grow behavior.",
                        file=name,
                        line=line_number(text, tag.start),
                    ))
            elif tag.name == "select" and select_tag is None:
                select_tag = tag
            elif tag.name == "input" and native_date_tag is None:
                input_type = (attribute_value(tag.attributes, "type") or "").casefold()
                if input_type in {"date", "time", "month", "week", "datetime-local"}:
                    native_date_tag = tag

        select_owner = ownership.get("Select/Listbox")
        if select_tag is not None and select_owner != "native":
            undecided = not isinstance(select_owner, str) or not select_owner.strip()
            findings.append(finding(
                "ownership.native-select-undecided" if undecided else "ownership.native-select-conflict",
                (
                    "Native select is used without an explicit ownership decision."
                    if undecided
                    else f"Native select conflicts with recorded Select/Listbox ownership: {select_owner}."
                ),
                "Record Select/Listbox as native or reuse the authored canonical owner.",
                file=name,
                line=line_number(text, select_tag.start),
                category="unresolved" if undecided else "violation",
            ))

        date_owner = ownership.get("Date")
        if native_date_tag is not None and date_owner != "native":
            undecided = not isinstance(date_owner, str) or not date_owner.strip()
            findings.append(finding(
                "ownership.native-date-undecided" if undecided else "ownership.native-date-conflict",
                (
                    "Native date/time input is used without an explicit ownership decision."
                    if undecided
                    else f"Native date/time input conflicts with recorded Date ownership: {date_owner}."
                ),
                "Record Date as native or reuse the typed/authored canonical owner.",
                file=name,
                line=line_number(text, native_date_tag.start),
                category="unresolved" if undecided else "violation",
            ))

        searchable = mask_comments(text)
        for container, region_end in html_regions(all_tags, len(searchable)):
            raw_tag = searchable[container.start:container.end]
            viewport_match = re.search(
                r"(?:h-screen|h-dvh|h-svh|h-lvh|h-full|min-h-screen|100vh|100dvh|100svh|100lvh|height\s*:\s*100%)",
                raw_tag,
                flags=re.IGNORECASE,
            )
            overflow_hidden = bool(re.search(
                r"overflow-hidden|overflow\s*:\s*hidden",
                raw_tag,
                flags=re.IGNORECASE,
            ))
            if viewport_match is None or not overflow_hidden:
                continue
            region = searchable[container.end:region_end]
            has_table = bool(re.search(r"<table\b|DataTable|data-table", region, flags=re.IGNORECASE))
            has_form = bool(re.search(r"<form\b|AppForm", region, flags=re.IGNORECASE))
            if has_table and has_form:
                findings.append(finding(
                    "layout.shared-shell-overflow",
                    "Table viewport sizing leaks into a shared page/form shell.",
                    "Give the table body its own bounded scroll surface and let the page/form shell size naturally.",
                    file=name,
                    line=line_number(text, container.start + viewport_match.start()),
                ))
                break

        if path.suffix.lower() in {".css", ".scss"}:
            css_rules = list(iter_css_rules(text))
            webkit_rules = [
                (rule, surface)
                for rule in css_rules
                if not rule.selector.startswith("@")
                for surface in scrollbar_surfaces(rule.selector)
            ]
            uncovered = next((
                rule for rule, surface in webkit_rules
                if not standards_cover_surface(surface, css_rules)
            ), None)
            if uncovered is not None:
                findings.append(finding(
                    "scrollbar.webkit-only",
                    "Scrollbar theme does not provide both standards-based scrollbar properties.",
                    "Add global scrollbar-color and scrollbar-width standards properties plus fallbacks.",
                    file=name,
                    line=line_number(text, uncovered.start),
                ))
            opt_in = next((
                rule for rule, _surface in webkit_rules
                if re.search(r"\.(?:custom-scrollbar|scrollbar|ui-scroll)\b", rule.selector)
            ), None)
            if opt_in is not None:
                findings.append(finding(
                    "scrollbar.opt-in-base",
                    "Base scrollbar theming is activated by an opt-in class.",
                    "Apply base scrollbar tokens globally; reserve classes for geometry or semantic exceptions.",
                    file=name,
                    line=line_number(text, opt_in.start),
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
    operational_failures = {"config.invalid-json", "output.write-failed"}
    if any(item.rule_id in operational_failures for item in result.findings):
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
    if not args.no_write:
        output = args.output or args.project_root / "premium-audit.json"
        try:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(rendered, encoding="utf-8")
        except OSError as error:
            result = AuditResult(result.mode, result.project_root, (*result.findings, finding(
                "output.write-failed",
                f"Audit report artifact cannot be written: {error}",
                "Choose a writable --output file or pass --no-write for stdout-only inspection.",
                file=str(output),
                category="unresolved",
            )))
            rendered = json.dumps(result.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    sys.stdout.write(rendered)
    return exit_code(result)


if __name__ == "__main__":
    raise SystemExit(main())
