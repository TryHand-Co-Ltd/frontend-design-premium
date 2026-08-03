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

Install from GitHub:

```bash
claude plugin marketplace add TryHand-Co-Ltd/frontend-design-premium
claude plugin install frontend-design-premium@tryhand
```
