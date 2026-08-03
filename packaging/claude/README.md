# Claude Code plugin package

This repository is a public Claude Code marketplace named `tryhand`.
The published plugin is self-contained and bundles the compatibility-tested
`frontend-design` skill alongside `frontend-design-premium`.

Build the published plugin tree and review archive:

```bash
python scripts/build_claude_plugin.py
```

Validate and test locally:

```bash
claude plugin validate --strict .
claude plugin validate --strict packaging/claude/plugins/frontend-design-premium
claude plugin marketplace add .
claude plugin install frontend-design-premium@tryhand
```

The build also writes `dist/frontend-design-premium-claude-<version>.zip` and
`dist/SHA256SUMS.claude` for release review. For a direct source installation
that resolves a separately installed upstream skill, see the repository
[`README.md`](../../README.md).

Install from GitHub:

```bash
claude plugin marketplace add TryHand-Co-Ltd/frontend-design-premium
claude plugin install frontend-design-premium@tryhand
```
