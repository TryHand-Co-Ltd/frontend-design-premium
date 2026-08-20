# Cursor Agent Plugin package

This repository exposes a Cursor-compatible Agent Plugin through
`.cursor-plugin/marketplace.json`. The package is self-contained and bundles
the compatibility-tested `frontend-design` skill alongside
`frontend-design-premium`.

Build the checked-in plugin tree and deterministic review archive:

```bash
python scripts/build_cursor_plugin.py
```

Validate the repository metadata and package contents:

```bash
python scripts/validate_skill.py
```

Test locally by copying or symlinking the generated package directory:

```bash
mkdir -p ~/.cursor/plugins/local
ln -s "$PWD/packaging/cursor/plugins/frontend-design-premium" \
  ~/.cursor/plugins/local/frontend-design-premium
```

Restart Cursor or run **Developer: Reload Window**, then confirm both
`/frontend-design` and `/frontend-design-premium` are available.

The build also writes `dist/frontend-design-premium-cursor-<version>.zip` and
`dist/SHA256SUMS.cursor` for GitHub release review. Public Marketplace
submission is performed separately at `https://cursor.com/marketplace/publish`
after the release commit is merged.
