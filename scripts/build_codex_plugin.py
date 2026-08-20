#!/usr/bin/env python3
"""Build the self-contained Codex marketplace and review archive."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "packaging" / "codex"
TEMPLATE = PACKAGE_ROOT / "plugins" / "frontend-design-premium"
VENDORED_UPSTREAM = PACKAGE_ROOT / "vendor" / "frontend-design"
DIST_ROOT = ROOT / "dist" / "codex-marketplace"
PLUGIN_OUT = DIST_ROOT / "plugins" / "frontend-design-premium"
PREMIUM_OUT = PLUGIN_OUT / "skills" / "frontend-design-premium"
UPSTREAM_OUT = PLUGIN_OUT / "skills" / "frontend-design"
EXPECTED_UPSTREAM_DIGEST = (
    "1608ea77fbb6fc30d13a97d12cfa8ebf31358d40f0dd97beed24829d6b3f45dd"
)
TEXT_SUFFIXES = {".json", ".md", ".py", ".txt", ".yaml", ".yml"}


def normalized_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


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


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def build_zip(plugin_root: Path, output: Path) -> None:
    fixed_time = (2026, 8, 3, 0, 0, 0)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(p for p in plugin_root.rglob("*") if p.is_file()):
            relative = path.relative_to(plugin_root).as_posix()
            info = zipfile.ZipInfo(relative, fixed_time)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())


def main() -> int:
    manifest_path = TEMPLATE / ".codex-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    version = manifest["version"]

    actual_upstream_digest = normalized_sha256(VENDORED_UPSTREAM / "SKILL.md")
    if actual_upstream_digest != EXPECTED_UPSTREAM_DIGEST:
        raise SystemExit(
            "Vendored frontend-design digest mismatch: "
            f"expected {EXPECTED_UPSTREAM_DIGEST}, got {actual_upstream_digest}"
        )

    if DIST_ROOT.exists():
        shutil.rmtree(DIST_ROOT)
    copy_tree(TEMPLATE, PLUGIN_OUT)

    PREMIUM_OUT.mkdir(parents=True)
    copy_file(ROOT / "SKILL.md", PREMIUM_OUT / "SKILL.md")
    copy_tree(ROOT / "agents", PREMIUM_OUT / "agents")
    copy_tree(ROOT / "references", PREMIUM_OUT / "references")
    copy_tree(ROOT / "assets", PREMIUM_OUT / "assets")
    (PREMIUM_OUT / "scripts").mkdir()
    copy_file(
        ROOT / "scripts" / "resolve_frontend_design.py",
        PREMIUM_OUT / "scripts" / "resolve_frontend_design.py",
    )
    copy_file(
        ROOT / "scripts" / "audit_project.py",
        PREMIUM_OUT / "scripts" / "audit_project.py",
    )

    copy_tree(VENDORED_UPSTREAM, UPSTREAM_OUT)
    copy_file(ROOT / "LICENSE", PLUGIN_OUT / "LICENSE")

    marketplace = {
        "name": "tryhand-preview",
        "interface": {"displayName": "TryHand Preview"},
        "plugins": [
            {
                "name": "frontend-design-premium",
                "source": {
                    "source": "local",
                    "path": "./plugins/frontend-design-premium",
                },
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL",
                },
                "category": "Developer Tools",
            }
        ],
    }
    write_json(DIST_ROOT / ".agents" / "plugins" / "marketplace.json", marketplace)

    archive_path = ROOT / "dist" / f"frontend-design-premium-codex-{version}.zip"
    build_zip(PLUGIN_OUT, archive_path)
    archive_digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    checksum_path = ROOT / "dist" / "SHA256SUMS.codex"
    checksum_path.write_text(
        f"{archive_digest}  {archive_path.name}\n",
        encoding="utf-8",
    )

    print(f"Plugin: {PLUGIN_OUT}")
    print(f"Marketplace: {DIST_ROOT}")
    print(f"Review archive: {archive_path}")
    print(f"SHA-256: {archive_digest}")
    print(f"Upstream frontend-design: {actual_upstream_digest} (MATCH)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
