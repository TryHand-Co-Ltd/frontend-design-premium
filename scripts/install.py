#!/usr/bin/env python3
"""Install this skill by linking or copying it into supported skill directories.

Usage:
  python scripts/install.py [--target agents|claude|pi|all] [--mode link|copy] [--force]
  python scripts/install.py --version
  python scripts/install.py --check
  python scripts/install.py --upgrade [--target all] [--mode link|copy]
  python scripts/install.py --list-targets
  python scripts/install.py --uninstall [--target all]
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
SKILL_NAME = "frontend-design-premium"
TARGETS = {
    "agents": Path.home() / ".agents" / "skills" / SKILL_NAME,
    "claude": Path.home() / ".claude" / "skills" / SKILL_NAME,
    "pi": Path.home() / ".pi" / "agent" / "skills" / SKILL_NAME,
}
IGNORE = shutil.ignore_patterns(".git", ".venv", "__pycache__", "*.pyc")

UPSTREAM_NAME = "frontend-design"
UPSTREAM_TARGETS = {
    "agents": Path.home() / ".agents" / "skills" / UPSTREAM_NAME,
    "claude": Path.home() / ".claude" / "skills" / UPSTREAM_NAME,
    "pi": Path.home() / ".pi" / "agent" / "skills" / UPSTREAM_NAME,
}


def _read_version() -> str | None:
    """Read version from SKILL.md frontmatter."""
    skill_path = SOURCE / "SKILL.md"
    if not skill_path.is_file():
        return None
    text = skill_path.read_text(encoding="utf-8")
    m = re.search(r'version:\s*"([^"]+)"', text)
    return m.group(1) if m else None


def _read_installed_version(target: Path) -> str | None:
    """Read version from an installed copy of the skill."""
    skill_path = target / "SKILL.md"
    if not skill_path.is_file():
        return None
    text = skill_path.read_text(encoding="utf-8")
    m = re.search(r'version:\s*"([^"]+)"', text)
    return m.group(1) if m else None


def _git_pull() -> bool:
    """Run git pull in SOURCE directory. Returns True on success or if not a git repo."""
    git_dir = SOURCE / ".git"
    if not git_dir.exists():
        print("NOTICE: source is not a git repository; skipping git pull", file=sys.stderr)
        return True
    # Submodules and worktrees store .git as a FILE containing a gitdir pointer
    if git_dir.is_file():
        print("NOTICE: .git is a file (submodule/worktree); using git --git-dir")
        # git -C SOURCE pull still works with submodules
        pass
    result = subprocess.run(
        ["git", "-C", str(SOURCE), "pull", "--ff-only"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"ERROR: git pull failed:\n{result.stderr.strip()}", file=sys.stderr)
        return False
    if result.stdout.strip():
        print(f"OK: git pull — {result.stdout.strip().split(chr(10))[0]}")
    else:
        print("OK: already up to date")
    return True


def _check_upstream(target_name: str) -> bool:
    """Verify upstream frontend-design is installed for this target."""
    upstream_path = UPSTREAM_TARGETS.get(target_name)
    if upstream_path and upstream_path.is_dir():
        return True
    # Try other targets as fallback
    for name, path in UPSTREAM_TARGETS.items():
        if path.is_dir():
            return True
    return False


def remove_existing(path: Path) -> None:
    # Handle dangling junctions: is_junction() may return True even if exists() is False
    # because the reparse point still exists while the target is gone.
    if path.is_symlink() or (os.name == "nt" and path.is_junction()):
        path.unlink()
    elif path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        # Some other type (e.g. broken reparse point not caught above)
        path.unlink()


def install(target: Path, mode: str, force: bool) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    # Check existence AND dangling junction (exists()=False but reparse point lingers)
    target_exists = target.exists() or target.is_symlink() or (os.name == "nt" and target.is_junction())
    if target_exists:
        if not force:
            raise FileExistsError(f"{target} already exists; use --force to replace it")
        remove_existing(target)

    if mode == "link":
        try:
            target.symlink_to(SOURCE, target_is_directory=True)
            return "linked"
        except OSError:
            pass  # Expected on Windows without Developer Mode; fall through to junction

        if os.name == "nt":
            result = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(target), str(SOURCE)],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                return "junctioned"
            print(
                f"junction failed for {target}: "
                f"{result.stderr.strip() or result.stdout.strip()}; copying instead"
            )

    shutil.copytree(SOURCE, target, ignore=IGNORE)
    return "copied"


def _do_version() -> int:
    ver = _read_version()
    if ver:
        print(f"{SKILL_NAME} v{ver}")
        return 0
    print("ERROR: cannot read version from SKILL.md", file=sys.stderr)
    return 1


def _link_type(path: Path) -> str:
    """Return 'symlink', 'junction', 'copy', or '?' for a given path.

    Works for live and dangling junctions (where exists()=False but the
    reparse point still exists on disk).
    """
    if path.is_symlink():
        return "symlink"
    if os.name == "nt" and path.is_junction():
        return "junction"
    if path.is_dir():
        # Real directory — probe by reading SKILL.md to see if it matches source
        skill_file = path / "SKILL.md"
        if skill_file.is_file():
            return "copy"
        return "dir"
    return "?"


def _do_check() -> int:
    source_ver = _read_version()
    if not source_ver:
        print("ERROR: cannot read version from source", file=sys.stderr)
        return 1

    print(f"Source: {SOURCE} v{source_ver}")
    any_installed = False
    for name, path in TARGETS.items():
        if _target_installed(path):
            any_installed = True
            lt = _link_type(path)
            installed_ver = _read_installed_version(path)
            if installed_ver:
                status = "MATCH" if installed_ver == source_ver else f"MISMATCH (installed {installed_ver})"
                print(f"  {name}: {path} v{installed_ver} [{lt}] {status}")
            else:
                print(f"  {name}: {path} [?] [{lt}] DANGLING — cannot read version")
        else:
            print(f"  {name}: not installed")

    if not any_installed:
        print("Skill is not installed in any target location.")
        return 1

    # Check upstream
    upstream_installed_for = []
    for name, path in UPSTREAM_TARGETS.items():
        if path.is_dir():
            upstream_installed_for.append(name)
    if not upstream_installed_for:
        print(f"WARNING: upstream '{UPSTREAM_NAME}' is not installed for any target.", file=sys.stderr)
        print(f"  Install upstream separately (this script does not install {UPSTREAM_NAME}).", file=sys.stderr)
    else:
        # Show upstream compatibility status
        upstream_incompatible = False
        try:
            sys.path.insert(0, str(SOURCE / "scripts"))
            from resolve_frontend_design import compatibility_status, find_skill
            upstream = find_skill()
            if upstream:
                compat = compatibility_status(upstream)
                state = compat.get("status", "?")
                msg = compat.get("message", "")
                print(f"  upstream: {' '.join(UPSTREAM_TARGETS)} [{state}]")
                if state != "MATCH":
                    print(f"    {msg}")
                    upstream_incompatible = True
                    if state == "INCOMPATIBLE":
                        print(f"    WARNING: INCOMPATIBLE upstream blocks release.", file=sys.stderr)
        except Exception as error:
            print(f"  upstream status check unavailable: {error}")
        if upstream_incompatible:
            return 1
    return 0


def _do_upgrade(target_names: list[str], mode: str, force: bool) -> int:
    # Step 1: git pull
    if not _git_pull():
        return 1

    # Step 2: re-read version after pull
    new_ver = _read_version()
    print(f"Source version: {new_ver or 'unknown'}")

    # Step 3: reinstall to each target
    failed = False
    for name in target_names:
        path = TARGETS[name]
        try:
            result = install(path, mode, force=True)
            print(f"  {result}: {name} -> {SOURCE}")
        except (OSError, FileExistsError) as error:
            failed = True
            print(f"  ERROR: {name}: {error}", file=sys.stderr)

    if not failed:
        print("Upgrade complete. Restart the harness if it does not support live skill discovery.")
    return 1 if failed else 0


def _do_list_targets() -> int:
    print("Skill installation targets:")
    for name, path in TARGETS.items():
        if _target_installed(path):
            lt = _link_type(path)
            ver = _read_installed_version(path) or "?"
            print(f"  {name}: {path} v{ver} [{lt}]")
        else:
            print(f"  {name}: not installed")
    return 0


def _target_installed(path: Path) -> bool:
    """Return True if the path holds an installed skill (symlink, junction, or copy)."""
    if path.is_symlink():
        return True
    if os.name == "nt" and path.is_junction():
        return True
    if path.is_dir():
        return (path / "SKILL.md").is_file()
    return False


def _do_uninstall(target_names: list[str]) -> int:
    for name in target_names:
        path = TARGETS[name]
        if not _target_installed(path):
            print(f"  {name}: not installed — skipping")
            continue
        remove_existing(path)
        print(f"  removed: {name} ({path})")
    print("Done.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        choices=(*TARGETS, "all"),
        default=None,
        help="target harness location (default: agents for install; all for --upgrade/--uninstall)",
    )
    parser.add_argument(
        "--mode",
        choices=("link", "copy"),
        default="link",
        help="link keeps repository edits live; falls back to copy if unsupported",
    )
    parser.add_argument("--force", action="store_true", help="replace an existing installation")
    parser.add_argument("--version", action="store_true", help="print version and exit")
    parser.add_argument("--check", action="store_true", help="check installed versions against source")
    parser.add_argument("--upgrade", action="store_true", help="git pull + reinstall all targets (default: --target all; respects --mode)")
    parser.add_argument("--list-targets", action="store_true", help="list installation status per target")
    parser.add_argument("--uninstall", action="store_true", help="remove skill from target(s) (default: --target all)")

    args = parser.parse_args()

    # Resolve effective target: None → context-dependent default
    target = args.target  # Keep None for dispatch below

    # Dispatch action commands
    if args.version:
        return _do_version()
    if args.check:
        return _do_check()
    if args.upgrade:
        effective_target = "all" if target is None else target
        names = list(TARGETS) if effective_target == "all" else [effective_target]
        return _do_upgrade(names, args.mode, args.force)
    if args.list_targets:
        return _do_list_targets()
    if args.uninstall:
        effective_target = "all" if target is None else target
        names = list(TARGETS) if effective_target == "all" else [effective_target]
        return _do_uninstall(names)

    # Default: install (--target not given → agents)
    effective_target = "agents" if target is None else target

    # Pre-flight: check upstream
    if effective_target != "all":
        upstream_ok = _check_upstream(effective_target)
        if not upstream_ok:
            print(
                f"WARNING: upstream skill '{UPSTREAM_NAME}' is not installed for target '{effective_target}'.",
                file=sys.stderr,
            )
            print("  This skill requires frontend-design to function.", file=sys.stderr)
            print(f"  Install upstream separately (this script does not install {UPSTREAM_NAME}).\n", file=sys.stderr)

    names = list(TARGETS) if effective_target == "all" else [effective_target]
    failed = False
    for name in names:
        try:
            result = install(TARGETS[name], args.mode, args.force)
            print(f"{result}: {TARGETS[name]} -> {SOURCE}")
        except (OSError, FileExistsError) as error:
            failed = True
            print(f"ERROR: {error}", file=sys.stderr)

    print("Restart the harness if it does not support live skill discovery.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
