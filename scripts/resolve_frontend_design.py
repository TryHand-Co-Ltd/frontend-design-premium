#!/usr/bin/env python3
"""Locate the live installed frontend-design Agent Skill without vendoring it."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

UPSTREAM_RAW_URL = (
    "https://raw.githubusercontent.com/anthropics/skills/main/skills/"
    "frontend-design/SKILL.md"
)


def skill_name(path: Path) -> str | None:
    try:
        head = path.read_text(encoding="utf-8")[:4096]
    except (OSError, UnicodeError):
        return None
    match = re.search(r"(?m)^name:\s*['\"]?([^'\"\n]+)", head)
    return match.group(1).strip() if match else None


def normalize_candidate(path: Path) -> Path:
    return path / "SKILL.md" if path.is_dir() else path


def candidate_paths(explicit: str | None = None) -> list[Path]:
    paths: list[Path] = []
    if explicit:
        paths.append(Path(explicit).expanduser())

    for variable in ("FRONTEND_DESIGN_SKILL", "ANTHROPIC_FRONTEND_DESIGN_SKILL"):
        if os.environ.get(variable):
            paths.append(Path(os.environ[variable]).expanduser())

    here = Path(__file__).resolve().parents[1]
    paths.extend(
        [
            here.parent / "frontend-design" / "SKILL.md",
            here.parent / "anthropic-skills" / "skills" / "frontend-design" / "SKILL.md",
        ]
    )

    cwd = Path.cwd().resolve()
    for root in (cwd, *cwd.parents):
        paths.extend(
            [
                root / ".agents" / "skills" / "frontend-design" / "SKILL.md",
                root / ".claude" / "skills" / "frontend-design" / "SKILL.md",
                root / ".pi" / "skills" / "frontend-design" / "SKILL.md",
                root / "skills" / "frontend-design" / "SKILL.md",
            ]
        )

    home = Path.home()
    paths.extend(
        [
            home / ".agents" / "skills" / "frontend-design" / "SKILL.md",
            home / ".claude" / "skills" / "frontend-design" / "SKILL.md",
            home / ".pi" / "agent" / "skills" / "frontend-design" / "SKILL.md",
        ]
    )

    unique: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        normalized = normalize_candidate(path).resolve(strict=False)
        key = os.path.normcase(str(normalized))
        if key not in seen:
            seen.add(key)
            unique.append(normalized)
    return unique


def find_skill(explicit: str | None = None) -> Path | None:
    own_skill = Path(__file__).resolve().parents[1] / "SKILL.md"
    for path in candidate_paths(explicit):
        if path == own_skill:
            continue
        if path.is_file() and skill_name(path) == "frontend-design":
            return path
    return None


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def remote_status(local: Path) -> dict[str, object]:
    local_bytes = local.read_bytes()
    result: dict[str, object] = {
        "local_sha256": sha256(local_bytes),
        "remote_url": UPSTREAM_RAW_URL,
    }
    try:
        request = urllib.request.Request(
            UPSTREAM_RAW_URL,
            headers={"User-Agent": "frontend-design-premium/0.1"},
        )
        with urllib.request.urlopen(request, timeout=15) as response:
            remote_bytes = response.read()
        result.update(
            {
                "remote_sha256": sha256(remote_bytes),
                "matches_remote": local_bytes == remote_bytes,
            }
        )
    except (OSError, urllib.error.URLError) as error:
        result["remote_error"] = str(error)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", help="Explicit frontend-design directory or SKILL.md")
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--print-path", action="store_true", help="Print only the path")
    output.add_argument("--print-content", action="store_true", help="Print the full SKILL.md")
    output.add_argument("--json", action="store_true", help="Print machine-readable details")
    parser.add_argument(
        "--check-remote",
        action="store_true",
        help="Compare the installed file with Anthropic's current GitHub main version",
    )
    args = parser.parse_args()

    found = find_skill(args.path)
    if not found:
        checked = "\n  - ".join(str(path) for path in candidate_paths(args.path))
        print(
            "frontend-design was not found. Install the upstream skill or set "
            "FRONTEND_DESIGN_SKILL. Checked:\n  - " + checked,
            file=sys.stderr,
        )
        return 2

    details: dict[str, object] = {
        "name": "frontend-design",
        "path": str(found),
        "sha256": sha256(found.read_bytes()),
    }
    if args.check_remote:
        details["upstream"] = remote_status(found)

    if args.print_content:
        print(found.read_text(encoding="utf-8"), end="")
    elif args.json or args.check_remote:
        print(json.dumps(details, ensure_ascii=False, indent=2))
    else:
        print(found)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
