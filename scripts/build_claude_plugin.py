#!/usr/bin/env python3
"""Build the self-contained Claude Code marketplace plugin and review archive."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "packaging" / "claude" / "plugins" / "frontend-design-premium"
PREMIUM_OUT = PLUGIN_ROOT / "skills" / "frontend-design-premium"
UPSTREAM_OUT = PLUGIN_ROOT / "skills" / "frontend-design"
VENDORED_UPSTREAM = ROOT / "packaging" / "codex" / "vendor" / "frontend-design"
EXPECTED_UPSTREAM_DIGEST = (
    "1608ea77fbb6fc30d13a97d12cfa8ebf31358d40f0dd97beed24829d6b3f45dd"
)
TEXT_SUFFIXES = {".json", ".md", ".py", ".txt", ".yaml", ".yml"}


def normalized_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def reset_directory(path: Path) -> None:
    resolved = path.resolve()
    expected_parent = (PLUGIN_ROOT / "skills").resolve()
    if resolved.parent != expected_parent or resolved.name not in {
        "frontend-design",
        "frontend-design-premium",
    }:
        raise RuntimeError(f"Refusing to reset unexpected path: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True)


def copy_tree(source: Path, destination: Path) -> None:
    shutil.copytree(source, destination, dirs_exist_ok=True)
    for path in destination.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n"))


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    data = source.read_bytes()
    if source.suffix.lower() in TEXT_SUFFIXES:
        data = data.replace(b"\r\n", b"\n")
    destination.write_bytes(data)
    shutil.copymode(source, destination)


def build_zip(plugin_root: Path, output: Path) -> None:
    fixed_time = (2026, 8, 3, 0, 0, 0)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(p for p in plugin_root.rglob("*") if p.is_file()):
            relative = path.relative_to(plugin_root).as_posix()
            info = zipfile.ZipInfo(relative, fixed_time)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())


def main() -> int:
    manifest_path = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    version = manifest["version"]

    actual_upstream_digest = normalized_sha256(VENDORED_UPSTREAM / "SKILL.md")
    if actual_upstream_digest != EXPECTED_UPSTREAM_DIGEST:
        raise SystemExit(
            "Vendored frontend-design digest mismatch: "
            f"expected {EXPECTED_UPSTREAM_DIGEST}, got {actual_upstream_digest}"
        )

    reset_directory(PREMIUM_OUT)
    copy_file(ROOT / "SKILL.md", PREMIUM_OUT / "SKILL.md")
    copy_tree(ROOT / "references", PREMIUM_OUT / "references")
    copy_tree(ROOT / "assets", PREMIUM_OUT / "assets")
    (PREMIUM_OUT / "scripts").mkdir()
    copy_file(
        ROOT / "scripts" / "resolve_frontend_design.py",
        PREMIUM_OUT / "scripts" / "resolve_frontend_design.py",
    )

    reset_directory(UPSTREAM_OUT)
    copy_tree(VENDORED_UPSTREAM, UPSTREAM_OUT)
    copy_file(ROOT / "LICENSE", PLUGIN_ROOT / "LICENSE")
    copy_file(
        ROOT / "packaging" / "codex" / "plugins" / "frontend-design-premium" / "THIRD_PARTY_NOTICES.md",
        PLUGIN_ROOT / "THIRD_PARTY_NOTICES.md",
    )

    archive_path = ROOT / "dist" / f"frontend-design-premium-claude-{version}.zip"
    build_zip(PLUGIN_ROOT, archive_path)
    archive_digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    checksum_path = ROOT / "dist" / "SHA256SUMS.claude"
    checksum_path.write_text(
        f"{archive_digest}  {archive_path.name}\n",
        encoding="utf-8",
    )

    print(f"Plugin: {PLUGIN_ROOT}")
    print(f"Marketplace: {ROOT}")
    print(f"Review archive: {archive_path}")
    print(f"SHA-256: {archive_digest}")
    print(f"Upstream frontend-design: {actual_upstream_digest} (MATCH)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
