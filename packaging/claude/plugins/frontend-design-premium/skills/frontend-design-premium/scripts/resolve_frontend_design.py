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


def normalized_sha256(path: Path) -> str:
    """Compute SHA-256 of file content after normalizing CRLF to LF.

    This ensures the digest is portable across Windows (CRLF) and
    Unix (LF) without requiring .gitattributes eol=lf on the upstream.
    """
    raw = path.read_bytes()
    normalized = raw.replace(b"\r\n", b"\n")
    return hashlib.sha256(normalized).hexdigest()


def remote_status(local: Path) -> dict[str, object]:
    local_bytes = local.read_bytes().replace(b"\r\n", b"\n")
    result: dict[str, object] = {
        "local_sha256": hashlib.sha256(local_bytes).hexdigest(),
        "remote_url": UPSTREAM_RAW_URL,
    }
    try:
        request = urllib.request.Request(
            UPSTREAM_RAW_URL,
            headers={"User-Agent": "frontend-design-premium/0.1"},
        )
        with urllib.request.urlopen(request, timeout=15) as response:
            remote_bytes = response.read().replace(b"\r\n", b"\n")
        result.update(
            {
                "remote_sha256": hashlib.sha256(remote_bytes).hexdigest(),
                "matches_remote": local_bytes == remote_bytes,
            }
        )
    except (OSError, urllib.error.URLError) as error:
        result["remote_error"] = str(error)
    return result






def _parse_frontmatter_block(text: str, key: str) -> dict[str, str] | None:
    """Parse a YAML block value under a given key from SKILL.md frontmatter.

    Returns a dict of sub-keys to values, or None if the key is not found.
    The block ends at the next top-level key (same indent as the block key)
    or at the end of the frontmatter.

    Example input:
      upstream-tested:
        revision: "..."
        digest: "..."
        tested-with-premium: "..."

    Returns {"revision": "...", "digest": "...", "tested-with-premium": "..."}
    """
    lines = text.splitlines()
    result: dict[str, str] = {}
    key_line: int | None = None
    key_indent: int = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(f"{key}:"):
            key_line = i
            key_indent = len(line) - len(line.lstrip())
            break
    if key_line is None:
        return None

    for line in lines[key_line + 1:]:
        if not line.strip():
            # Blank line — still inside frontmatter, not end of block
            continue
        indent = len(line) - len(line.lstrip())
        if indent <= key_indent:
            # Reached a key at same or lesser indent — block ended
            break
        if ":" not in line:
            continue
        sub_key, _, raw_value = line.partition(":")
        value = raw_value.strip().strip("'").strip('"')
        if value:
            result[sub_key.strip()] = value
    return result


def _is_valid_sha256(s: str) -> bool:
    """Return True if s is a 64-character lowercase hex string (SHA-256)."""
    return bool(re.fullmatch(r"[0-9a-f]{64}", s))


def load_tested_revisions() -> dict[str, str]:
    """Read tested-upstream metadata from SKILL.md frontmatter.

    Returns a dict mapping digest hex strings to revision labels.
    Only valid SHA-256 digests are included.
    """
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

    block = _parse_frontmatter_block(frontmatter, "upstream-tested")
    if block is None:
        return {}
    raw_digest = block.get("digest", "")
    if _is_valid_sha256(raw_digest):
        return {raw_digest: block.get("revision", "recorded")}
    return {}


def _parse_quoted_list(text: str, key: str) -> list[str]:
    """Parse a YAML list value from SKILL.md frontmatter.

    Supports both block and inline styles:
      key:
        - "item1"
        - item2
      key: ["item1", "item2"]
      key: []
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{key}:"):
            raw = line.strip()
            # Inline style: key: ["a", "b"] or key: []
            bracket_start = raw.find("[")
            if bracket_start >= 0:
                bracket_end = raw.rfind("]")
                if bracket_end > bracket_start:
                    inner = raw[bracket_start + 1:bracket_end]
                    if inner.strip():
                        return [
                            x.strip().strip("'").strip('"')
                            for x in inner.split(",")
                            if x.strip()
                        ]
                    return []
            # Block style: iterate subsequent lines
            result: list[str] = []
            key_indent = len(line) - len(line.lstrip())
            for sub_line in lines[i + 1:]:
                if not sub_line.strip():
                    continue
                sub_indent = len(sub_line) - len(sub_line.lstrip())
                if sub_indent <= key_indent:
                    break
                item = sub_line.strip()
                if item.startswith("-"):
                    val = item[1:].strip().strip("'").strip('"')
                    if val:
                        result.append(val)
            return result
    return []


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

    raw = _parse_quoted_list(frontmatter, "upstream-incompatible")
    return [d for d in raw if _is_valid_sha256(d)]


SUPPORTED_ROOTS: list[Path] = [
    Path.home() / ".agents" / "skills",
    Path.home() / ".claude" / "skills",
    Path.home() / ".pi" / "agent" / "skills",
]


def bundled_plugin_skill_root() -> Path | None:
    """Return the containing Codex or Claude plugin's skills root."""
    try:
        skills_root = Path(__file__).resolve().parents[2]
    except IndexError:
        return None
    plugin_root = skills_root.parent
    plugin_manifests = (
        plugin_root / ".codex-plugin" / "plugin.json",
        plugin_root / ".claude-plugin" / "plugin.json",
    )
    if skills_root.name == "skills" and any(path.is_file() for path in plugin_manifests):
        return skills_root
    return None


def trusted_location(path: Path) -> bool:
    """Return True if the candidate lives under a supported skill root.

    Uses component-aware path containment to reject prefix siblings:
      .agents/skills/frontend-design          -> trusted
      .agents/skills-evil/frontend-design      -> NOT trusted
      ../skills/frontend-design                -> NOT trusted
    """
    try:
        resolved = path.resolve()
    except (OSError, RuntimeError):
        return False
    resolved_parts = os.path.normcase(str(resolved)).split(os.sep)
    roots = list(SUPPORTED_ROOTS)
    bundled_root = bundled_plugin_skill_root()
    if bundled_root is not None:
        roots.append(bundled_root)
    for root in roots:
        try:
            root_resolved = root.resolve()
        except (OSError, RuntimeError):
            continue
        root_parts = os.path.normcase(str(root_resolved)).split(os.sep)
        if len(resolved_parts) < len(root_parts):
            continue
        # Every component of root_parts must match exactly
        if resolved_parts[:len(root_parts)] == root_parts:
            return True
    return False


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
        "digest": normalized_sha256(found),
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
        "sha256": normalized_sha256(found),
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
