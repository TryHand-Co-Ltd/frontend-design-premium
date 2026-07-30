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





def _parse_frontmatter_value(text: str, key: str) -> str | None:
    """Extract a quoted scalar value from YAML frontmatter by key.

    Handles:
      key: "value"
      key: 'value'
      key: value
    within the frontmatter block. Returns None if not found.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(f"{key}:"):
            value = stripped[len(key) + 1:].strip()
            if value.startswith('"') and value.endswith('"') and len(value) >= 2:
                return value[1:-1]
            if value.startswith("'") and value.endswith("'") and len(value) >= 2:
                return value[1:-1]
            return value
    return None


def _parse_frontmatter_list(text: str, key: str) -> list[str]:
    """Extract a YAML list from frontmatter by key.

    Handles:
      key:
        - "item1"
        - item2
    Returns empty list if not found.
    """
    lines = text.splitlines()
    result: list[str] = []
    in_block = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(f"{key}:"):
            in_block = True
            continue
        if in_block:
            if not stripped or not stripped.startswith("-"):
                # Reached next key or end of frontmatter
                if stripped and ":" in stripped.split(None, 1)[0]:
                    in_block = False
                    break
                continue
            item = stripped[1:].strip()
            if item.startswith('"') and item.endswith('"') and len(item) >= 2:
                item = item[1:-1]
            elif item.startswith("'") and item.endswith("'") and len(item) >= 2:
                item = item[1:-1]
            if item:
                result.append(item)
    return result


def load_tested_revisions() -> dict[str, str]:
    """Read tested-upstream metadata from SKILL.md frontmatter."""
    premium_skill = Path(__file__).resolve().parents[1] / "SKILL.md"
    if not premium_skill.is_file():
        return {}
    try:
        text = premium_skill.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return {}
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    frontmatter = text[4:end]

    revisions: dict[str, str] = {}
    for line in frontmatter.splitlines():
        stripped = line.strip()
        if stripped.startswith("digest:"):
            value = stripped[len("digest:"):].strip().strip('"')
            if value and len(value) > 10:
                revisions[value] = "recorded"
    return revisions


def load_incompatible_digests() -> list[str]:
    """Read incompatible-digests list from SKILL.md frontmatter."""
    premium_skill = Path(__file__).resolve().parents[1] / "SKILL.md"
    if not premium_skill.is_file():
        return []
    try:
        text = premium_skill.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return []
    if not text.startswith("---\n"):
        return []
    end = text.find("\n---\n", 4)
    if end < 0:
        return []
    frontmatter = text[4:end]

    result: list[str] = []
    in_block = False
    for line in frontmatter.splitlines():
        stripped = line.strip()
        if stripped.startswith("upstream-incompatible:"):
            in_block = True
            continue
        if in_block:
            if not stripped or not stripped.startswith("-"):
                if ":" in stripped.split(None, 1)[0]:
                    in_block = False
                break
            item = stripped[1:].strip().strip('"').strip("'")
            if item:
                result.append(item)
    return result


SUPPORTED_ROOTS: list[Path] = [
    Path.home() / ".agents" / "skills",
    Path.home() / ".claude" / "skills",
    Path.home() / ".pi" / "agent" / "skills",
]


def trusted_location(path: Path) -> bool:
    """Return True if the candidate lives under a supported skill root."""
    try:
        resolved = path.resolve()
    except (OSError, RuntimeError):
        return False
    resolved_normalized = os.path.normcase(str(resolved))
    return any(
        resolved_normalized.startswith(os.path.normcase(str(root)))
        for root in SUPPORTED_ROOTS
    )


def compatibility_status(
    found: Path,
    tested_revisions: dict[str, str] | None = None,
    incompatible_digests: list[str] | None = None,
) -> dict[str, str]:
    """Determine the compatibility state of the installed upstream.

    Returns a dict with keys: status, message, digest, path.
    """
    if tested_revisions is None:
        tested_revisions = load_tested_revisions()
    if incompatible_digests is None:
        incompatible_digests = load_incompatible_digests()
    incompatible_set = set(incompatible_digests)

    result: dict[str, str] = {
        "path": str(found),
        "digest": sha256(found.read_bytes()),
    }
    current_digest = result["digest"]

    # Check INCOMPATIBLE first — it overrides all other states
    if current_digest in incompatible_set:
        result["status"] = "INCOMPATIBLE"
        result["message"] = (
            "This upstream revision is known to break premium contracts. "
            "Upgrade to a compatible revision before using premium."
        )
        return result

    if not trusted_location(found):
        result["status"] = "UNTRUSTED"
        result["message"] = (
            f"Upstream candidate is not in a supported skill root: {found}"
        )
        return result

    if not tested_revisions:
        result["status"] = "UNTESTED"
        result["message"] = (
            "No tested revision recorded in premium metadata. "
            "Run compatibility validation before release."
        )
        return result

    if current_digest in tested_revisions:
        result["status"] = "MATCH"
        result["message"] = f"Installed upstream matches tested revision."
    else:
        result["status"] = "UNTESTED"
        result["message"] = (
            f"Installed upstream digest {current_digest[:16]}... is not in the "
            f"tested-revision list. Run compatibility validation before release."
        )

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", help="Explicit frontend-design directory or SKILL.md")
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--print-path", action="store_true", help="Print only the path")
    output.add_argument("--print-content", action="store_true", help="Print the full SKILL.md")
    output.add_argument("--json", action="store_true", help="Print machine-readable details")
    output.add_argument(
        "--status",
        action="store_true",
        help="Report upstream compatibility status and exit",
    )
    parser.add_argument(
        "--check-remote",
        action="store_true",
        help="Compare the installed file with Anthropic's current GitHub main version",
    )
    args = parser.parse_args()

    found = find_skill(args.path)
    if not found:
        if args.status:
            result = {
                "status": "MISSING",
                "message": "frontend-design could not be located",
                "path": None,
                "digest": None,
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 2
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

    if args.status:
        compat = compatibility_status(found)
        compat["sha256"] = details["sha256"]
        print(json.dumps(compat, ensure_ascii=False, indent=2))
        return 0 if compat["status"] == "MATCH" else 1

    if args.print_content:
        print(found.read_text(encoding="utf-8"), end="")
    elif args.json or args.check_remote:
        print(json.dumps(details, ensure_ascii=False, indent=2))
    else:
        print(found)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
