# Codex plugin package

This directory contains the checked-in manifest and marketplace assets used to build the public skills-only Codex plugin.

Run from the repository root:

```powershell
python scripts/build_codex_plugin.py
```

The builder creates a deterministic marketplace under `dist/codex-marketplace`,
bundles the tested upstream `frontend-design` snapshot, validates its recorded
digest, and writes a versioned review ZIP plus `SHA256SUMS.codex`. Generated
output is not committed.

Install the local preview with:

```powershell
codex plugin marketplace add ./dist/codex-marketplace
codex plugin add frontend-design-premium@tryhand-preview
```

This package is self-contained. For a direct source installation that follows
the currently installed upstream skill instead, see the repository
[`README.md`](../../README.md).
