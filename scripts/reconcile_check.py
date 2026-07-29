"""Reconcile DESIGN.md against actual codebase — verify tokens, components, patterns."""
import re
from pathlib import Path


def scan_tokens(filepath):
    """Extract CSS custom properties. Keeps the FIRST occurrence (light mode default)."""
    text = Path(filepath).read_text(encoding="utf-8")
    tokens = {}
    for m in re.finditer(r"--([\w-]+)\s*:\s*([^;]+)", text):
        key = m.group(1)
        val = m.group(2).strip()
        if key not in tokens:
            tokens[key] = val
    return tokens


def scan_components(root, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = {
            "node_modules",
            ".next",
            "coverage",
            ".git",
            ".mypy_cache",
            ".pytest_cache",
            ".ruff_cache",
        }
    components = []
    for p in Path(root).rglob("*.tsx"):
        if any(part in p.parts for part in exclude_dirs):
            continue
        components.append(p.relative_to(root))
    return components


def check_tokens(design_frontmatter_keys, css_tokens):
    all_ok = True
    for name, expected in design_frontmatter_keys.items():
        found = False
        for css_key, css_val in css_tokens.items():
            if name in css_key or css_key.endswith(name):
                if expected.lower() in css_val.lower():
                    found = True
                    break
        if not found:
            all_ok = False
            print(f"  FAIL {name}: {expected} -- NOT FOUND in CSS")
    if all_ok:
        print("  PASS: All token mappings verified")


def check_components(comp_list, actual_comps):
    missing = []
    actual_strs = [str(c).replace("\\", "/") for c in actual_comps]
    for comp in comp_list:
        cl = comp.lower()
        matched = False
        for a in actual_strs:
            if cl in a.lower():
                matched = True
                break
        if not matched:
            missing.append(comp)
    print(
        f"  Total: {len(comp_list)}, Missing: {len(missing)}, Matched: {len(comp_list) - len(missing)}"
    )
    if missing:
        for m in missing:
            print(f"    [MISSING] {m}")


def check_patterns(text, patterns):
    for p in patterns:
        found = re.search(p, text, re.IGNORECASE)
        status = "PASS" if found else "MISS"
        print(f"  {status}: {p}")


import sys
import os
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

def main():
    # === jd-cv-matcher ===
    print("=" * 60)
    print("RECONCILIATION: jd-cv-matcher")
    print("=" * 60)

    design_text = Path("D:/Personal/jd-cv-matcher/DESIGN.md").read_text(encoding="utf-8")
    css_tokens = scan_tokens("D:/Personal/jd-cv-matcher/src/styles/globals.css")
    actual_comps = scan_components("D:/Personal/jd-cv-matcher/src")

    print("\nToken mapping check:")
    check_tokens(
        {
            "ink": "#1e2532",
            "carbon": "#0f141e",
            "signal-blue": "#1a91f0",
            "success": "#1a7a4a",
            "destructive": "#d64545",
        },
        css_tokens,
    )

    print("\nComponent inventory check:")
    check_components(
        [
            "button",
            "card",
            "badge",
            "app-header",
            "chat-panel",
            "cv-multi-upload",
            "analysis-results-view",
            "ranking-table",
            "charts",
            "match-score-badge",
            "skeleton",
            "pdf-export",
        ],
        actual_comps,
    )

    print("\nPattern coverage:")
    check_patterns(
        design_text,
        [
            r"flat.*design",
            r"border.*card",
            r"signal.blue",
            r"tabular.nums",
            r"fade.in",
            r"score.fil",
            r"outfit|dm sans",
            r"jetbrains",
        ],
    )

    # === Scopelytics ===
    print("\n" + "=" * 60)
    print("RECONCILIATION: Scopelytics")
    print("=" * 60)

    design_text2 = Path("D:/Workspace/scopelytics-ai-powered/DESIGN.md").read_text(encoding="utf-8")
    css_tokens2 = scan_tokens("D:/Workspace/scopelytics-ai-powered/frontend/app/globals.css")

    print("\nToken mapping check:")
    check_tokens(
        {
            "primary": "#0658f6",
            "background": "#f8f8f8",
            "foreground": "#151515",
            "destructive": "#be123c",
            "chart-4": "#22b0ff",
            "muted-foreground": "#707070",
        },
        css_tokens2,
    )

    print("\nComponent inventory check:")
    actual_comps2 = scan_components("D:/Workspace/scopelytics-ai-powered/frontend")
    check_components(
        [
            "ui/button",
            "ui/card",
            "ui/dialog",
            "auth/LoginForm",
            "upload/FileUploader",
            "layout/AppHeader",
            "landing/HeroSection",
            "dashboard/DashboardHeader",
            "analysis/AnalysisWorkspace",
            "admin/AdminShell",
        ],
        actual_comps2,
    )

    print("\nPattern coverage:")
    check_patterns(
        design_text2,
        [
            r"surface.card|backdrop.filter",
            r"react.hook.form|react-hook-form",
            r"i18n|locale|useHydrationSafeT",
            r"recharts|chart",
            r"sonner|toast",
            r"prefers-reduced-motion",
            r"google.*oauth|GoogleLoginButton",
        ],
    )

    print("\nDone. RECONCILIATION COMPLETE")


if __name__ == "__main__":
    main()
