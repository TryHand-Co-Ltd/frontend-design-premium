#!/usr/bin/env python3
"""Check a project's DESIGN.md against its frontend source tree.

This is a portable structural check, not a visual reviewer. It catches an
uninitialized design context, missing canonical sections, an empty source tree,
and an explicitly supplied CSS file with no custom properties.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CANONICAL_SECTIONS = (
    "## Overview",
    "## Colors",
    "## Typography",
    "## Layout",
    "## Elevation & Depth",
    "## Shapes",
    "## Components",
    "## Do's and Don'ts",
)
IGNORED_DIRECTORIES = {
    ".git",
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    "coverage",
    "node_modules",
}


def css_tokens(path: Path) -> dict[str, str]:
    """Return the first value declared for each CSS custom property."""
    text = path.read_text(encoding="utf-8")
    tokens: dict[str, str] = {}
    for match in re.finditer(r"--([\w-]+)\s*:\s*([^;]+)", text):
        tokens.setdefault(match.group(1), match.group(2).strip())
    return tokens


def component_files(root: Path) -> list[Path]:
    """Return TypeScript/JavaScript component files below a source root."""
    suffixes = {".jsx", ".tsx", ".vue", ".svelte"}
    return sorted(
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix in suffixes
        and not any(part in IGNORED_DIRECTORIES for part in path.parts)
    )


def reconcile(design: Path, source: Path, css: Path | None) -> list[str]:
    errors: list[str] = []
    if not design.is_file():
        return [f"design context does not exist: {design}"]
    if not source.is_dir():
        return [f"frontend source directory does not exist: {source}"]

    design_text = design.read_text(encoding="utf-8")
    missing_sections = [section for section in CANONICAL_SECTIONS if section not in design_text]
    if missing_sections:
        errors.append("DESIGN.md is missing sections: " + ", ".join(missing_sections))
    if re.search(r"(?m)^status:\s*uninitialized\s*$", design_text):
        errors.append("DESIGN.md is still uninitialized")
    if re.search(r"\[[^\]\n]{4,}\]", design_text):
        errors.append("DESIGN.md still contains bracketed template prompts")

    components = component_files(source)
    if not components:
        errors.append(f"no frontend component files found below {source}")
    else:
        print(f"components: {len(components)}")

    if css is not None:
        if not css.is_file():
            errors.append(f"CSS token source does not exist: {css}")
        else:
            tokens = css_tokens(css)
            if not tokens:
                errors.append(f"no CSS custom properties found in {css}")
            else:
                print(f"css custom properties: {len(tokens)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="project repository root")
    parser.add_argument("--design", default="DESIGN.md", help="path relative to project")
    parser.add_argument("--source", default="apps/web", help="frontend source path")
    parser.add_argument("--css", help="optional CSS token file relative to project")
    args = parser.parse_args()

    project = args.project.resolve()
    design = project / args.design
    source = project / args.source
    css = project / args.css if args.css else None
    try:
        errors = reconcile(design, source, css)
    except (OSError, UnicodeError) as error:
        print(f"reconciliation failed: {error}", file=sys.stderr)
        return 1
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print("DESIGN.md reconciliation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
