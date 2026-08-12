"""Verify structural case-study coverage and Japan-readiness proof wiring.

This command validates skill contracts, eval claims, negative oracles, and
fixture wiring. It deliberately does not claim browser behavior or native-copy
quality; those require the evidence types declared by each eval.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def contains(relative: str, *patterns: str) -> bool:
    text = read(relative)
    return all(re.search(pattern, text, re.IGNORECASE | re.MULTILINE) for pattern in patterns)


legacy_checks = {
    "Table pagination + load-more decision": contains("SKILL.md", r"pagination", r"load.?more"),
    "Hover style + pointer semantics": contains("SKILL.md", r"hover", r"pointer"),
    "Custom scrollbar and stability": contains("SKILL.md", r"scrollbar", r"layout stability"),
    "No browser-native dialogs": contains("SKILL.md", r"alert\(\).*confirm\(\).*prompt\(\)"),
    "Button emphasis and semantic intent": contains("SKILL.md", r"emphasis", r"intent"),
    "Cross-screen consistency": contains("SKILL.md", r"Cross-screen consistency"),
    "Textarea resize contract": contains("references/interaction-contract.md", r"resize:\s*none"),
    "Password mask and reveal": contains("references/interaction-contract.md", r"Password/secret/key", r"reveal"),
    "Disable native validation UI": contains("SKILL.md", r"noValidate|novalidate"),
    "Clearable debounced IME-safe search": contains("SKILL.md", r"clear", r"debounce", r"IME"),
    "Destructive app-owned confirmation": contains("SKILL.md", r"destructive", r"confirmation"),
    "Proactive DESIGN.md lifecycle": contains("SKILL.md", r"DESIGN\.md", r"create"),
    "Runtime composition with frontend-design": contains("SKILL.md", r"Load the upstream skill", r"composition"),
}


required_japan_headings = {
    "references/japan-market-context.md": [
        "## Separate the three decisions",
        "## Market gate",
        "## Evidence precedence",
        "## Anti-stereotype guardrail",
    ],
    "references/japanese-content-design.md": [
        "## Voice and register",
        "## Actions and guidance",
        "## Review gate",
    ],
    "references/japanese-visual-layout.md": [
        "## Typography foundation",
        "## Composition and line breaking",
        "## Density and hierarchy",
    ],
    "references/japanese-localization.md": [
        "## Japanese IME and interactive input",
        "### Names",
        "### Addresses",
        "## Minimum locale and input test pass",
    ],
    "references/japan-regulated-flows.md": [
        "## Authority gate",
        "## Privacy and consent",
        "## Commerce and subscriptions",
    ],
}


def japan_reference_structure() -> tuple[bool, list[str]]:
    failures: list[str] = []
    for relative, headings in required_japan_headings.items():
        path = ROOT / relative
        if not path.is_file():
            failures.append(f"missing {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for heading in headings:
            if heading not in text:
                failures.append(f"{relative} missing {heading!r}")
    return not failures, failures


def japan_routing() -> tuple[bool, list[str]]:
    failures: list[str] = []
    skill = read("SKILL.md")
    gate_heading = "## 0b. Japan-market gate"
    if gate_heading not in skill:
        return False, [f"SKILL.md missing routing token {gate_heading!r}"]
    gate = skill.split(gate_heading, 1)[1].split("## 1.", 1)[0]
    required_in_gate = [
        "Japanese locale",
        "Japan market",
        "Japanese content/visual design",
        "including marketing",
        "references/japan-market-context.md",
        "references/japanese-content-design.md",
        "references/japanese-visual-layout.md",
        "references/japanese-localization.md",
        "references/japan-regulated-flows.md",
    ]
    for token in required_in_gate:
        if token not in gate:
            failures.append(f"Japan-market gate missing routing token {token!r}")
    register = skill.split(gate_heading, 1)[0]
    if "Japan-targeted marketing page is not exempt" not in register:
        failures.append("register gate does not explicitly retain Japan-targeted marketing rules")
    if re.search(r"Do \*\*not\*\* force .*Japanese localization on a marketing page", skill):
        failures.append("legacy marketing exemption still bypasses Japan-facing rules")
    return not failures, failures


def japan_eval_proof() -> tuple[bool, list[str]]:
    failures: list[str] = []
    data = json.loads(read("evals/evals.json"))
    cases = {case["id"]: case for case in data.get("evals", [])}
    required_claims = {
        "market_context",
        "native_copy_typography",
        "ime_non_search",
        "regulated_escalation",
        "anti_stereotype",
        "runtime_verification",
    }
    matrix = data.get("japan_readiness_claims", {})
    if set(matrix) != required_claims:
        failures.append(
            "claim matrix must contain exactly: " + ", ".join(sorted(required_claims))
        )
    for claim in sorted(required_claims):
        ids = matrix.get(claim, [])
        if not ids:
            failures.append(f"claim {claim!r} has no eval")
        for case_id in ids:
            case = cases.get(case_id)
            if case is None:
                failures.append(f"claim {claim!r} references missing eval #{case_id}")
                continue
            if claim not in case.get("claims", []):
                failures.append(f"eval #{case_id} does not declare {claim!r}")
            if not case.get("negative_oracle"):
                failures.append(f"eval #{case_id} has no negative_oracle")
            if not case.get("evidence_required"):
                failures.append(f"eval #{case_id} has no evidence_required")
            for fixture in case.get("files", []):
                if not (ROOT / "evals" / fixture).is_file():
                    failures.append(f"eval #{case_id} missing evals/{fixture}")

    runtime_ids = matrix.get("runtime_verification", [])
    if not any(
        "automated-interaction-test" in cases[case_id].get("evidence_required", [])
        for case_id in runtime_ids
        if case_id in cases
    ):
        failures.append("runtime verification lacks an automated interaction-test case")
    if not any(
        any("native" in evidence for evidence in cases[case_id].get("evidence_required", []))
        for case_id in matrix.get("native_copy_typography", [])
        if case_id in cases
    ):
        failures.append("native copy/typography lacks native-review evidence")

    ime_fixture = read("evals/fixtures/jp-ime-autosave.tsx")
    if "onCompositionStart" in ime_fixture or "isComposing" in ime_fixture:
        failures.append("IME negative fixture is already guarded; it no longer falsifies the claim")
    checkout_fixture = read("evals/fixtures/japan-checkout.tsx")
    if "aria-label=\"Confirm order\"" not in checkout_fixture or ">OK<" not in checkout_fixture:
        failures.append("checkout negative fixture no longer contains copy leakage")
    return not failures, failures


def single_select_contract() -> tuple[bool, list[str]]:
    failures: list[str] = []
    required = {
        "SKILL.md": [
            r"single-select|select dropdown",
            r"native.*authored|authored.*native",
            r"data-entry-patterns\.md",
        ],
        "references/data-entry-patterns.md": [
            r"Single-select dropdowns",
            r"1 CSS px",
            r"listbox",
            r"portal",
            r"collision",
        ],
        "references/anti-patterns.md": [
            r"Native select used when authored popup geometry is required",
            r"<select",
            r"option",
        ],
        "references/verification-checklist.md": [
            r"native.*authored|authored.*native",
            r"1 CSS px",
            r"open popup",
            r"long option",
        ],
    }
    for relative, patterns in required.items():
        for pattern in patterns:
            if not contains(relative, pattern):
                failures.append(f"{relative} missing /{pattern}/")

    data = json.loads(read("evals/evals.json"))
    case = next((item for item in data.get("evals", []) if item.get("id") == 39), None)
    if case is None:
        failures.append("missing eval #39")
    else:
        fixture = ROOT / "evals" / "fixtures/native-select-popup-mismatch.tsx"
        if not fixture.is_file():
            failures.append("eval #39 fixture is missing")
        else:
            fixture_text = fixture.read_text(encoding="utf-8")
            if "<select" not in fixture_text or "<option" not in fixture_text:
                failures.append("eval #39 fixture no longer reproduces the native-select mismatch")
        if not case.get("negative_oracle") or not case.get("evidence_required"):
            failures.append("eval #39 needs a negative oracle and runtime evidence")
    return not failures, failures


def date_picker_contract() -> tuple[bool, list[str]]:
    failures: list[str] = []
    required = {
        "SKILL.md": [
            r"date picker",
            r"browser.*owned|operating-system.*owned",
            r"data-entry-patterns\.md",
        ],
        "references/data-entry-patterns.md": [
            r"Date and date-range pickers",
            r"native.*authored|authored.*native",
            r"locale pack",
            r"focus restoration",
            r"real browser",
        ],
        "references/japanese-localization.md": [
            r"native.*date input|input\[type=.date.\]",
            r"August",
            r"YYYY/MM/DD",
            r"ISO 8601",
        ],
        "references/anti-patterns.md": [
            r"Native date/time picker used when localized popup UI is required",
            r"date\|time\|month\|week\|datetime-local",
            r"browser.*owned|operating-system.*owned",
        ],
        "references/verification-checklist.md": [
            r"native.*authored|authored.*native",
            r"calendar.*locale",
            r"today.*clear|clear.*today",
            r"open.*real browser|real browser.*open",
        ],
    }
    for relative, patterns in required.items():
        for pattern in patterns:
            if not contains(relative, pattern):
                failures.append(f"{relative} missing /{pattern}/")

    data = json.loads(read("evals/evals.json"))
    case = next((item for item in data.get("evals", []) if item.get("id") == 40), None)
    if case is None:
        failures.append("missing eval #40")
    else:
        fixture = ROOT / "evals" / "fixtures/native-date-picker-english-leak.tsx"
        if not fixture.is_file():
            failures.append("eval #40 fixture is missing")
        else:
            fixture_text = fixture.read_text(encoding="utf-8")
            if 'type="date"' not in fixture_text or 'lang="ja"' not in fixture_text:
                failures.append("eval #40 fixture no longer reproduces the native date-picker leak")
        if not case.get("negative_oracle") or not case.get("evidence_required"):
            failures.append("eval #40 needs a negative oracle and runtime evidence")
    return not failures, failures


def global_scrollbar_contract() -> tuple[bool, list[str]]:
    failures: list[str] = []
    required = {
        "SKILL.md": [
            r"global.*scrollbar|scrollbar.*global",
            r"opt-in|per-container",
            r"forced.?colors|high-contrast",
        ],
        "references/interaction-contract.md": [
            r"global.*scrollbar|scrollbar.*global",
            r"opt-in class|per-container opt-in",
            r"thumb/track",
            r"forced.?colors|high-contrast",
        ],
        "references/anti-patterns.md": [
            r"Scrollbar theme requires per-container opt-in",
            r"overflow",
            r"global",
        ],
        "references/verification-checklist.md": [
            r"global scrollbar baseline",
            r"new scroll container",
            r"computed.*scrollbar-color|scrollbar-color.*computed",
        ],
    }
    for relative, patterns in required.items():
        for pattern in patterns:
            if not contains(relative, pattern):
                failures.append(f"{relative} missing /{pattern}/")

    data = json.loads(read("evals/evals.json"))
    case = next((item for item in data.get("evals", []) if item.get("id") == 41), None)
    if case is None:
        failures.append("missing eval #41")
    else:
        fixture = ROOT / "evals" / "fixtures/scrollbar-opt-in-gap.tsx"
        if not fixture.is_file():
            failures.append("eval #41 fixture is missing")
        else:
            fixture_text = fixture.read_text(encoding="utf-8")
            if "overflow-x-auto" not in fixture_text or "ui-scroll-container" in fixture_text:
                failures.append("eval #41 fixture no longer reproduces the scrollbar opt-in gap")
        if not case.get("negative_oracle") or not case.get("evidence_required"):
            failures.append("eval #41 needs a negative oracle and runtime evidence")
    return not failures, failures


def table_form_scroll_ownership_contract() -> tuple[bool, list[str]]:
    failures: list[str] = []
    required = {
        "SKILL.md": [
            r"scroll ownership|scroll owner",
            r"table panel|table surface",
            r"form panel|long form",
        ],
        "references/interaction-contract.md": [
            r"bounded.*table|table.*bounded",
            r"natural.*height|document scrolling",
            r"shared.*ancestor|shared.*shell",
        ],
        "references/anti-patterns.md": [
            r"Table viewport sizing leaks into sibling form",
            r"h-dvh|100vh|overflow-hidden",
            r"scroll owner",
        ],
        "references/verification-checklist.md": [
            r"table.*form|form.*table",
            r"scroll owner|scroll ownership",
            r"200% zoom",
        ],
    }
    for relative, patterns in required.items():
        for pattern in patterns:
            if not contains(relative, pattern):
                failures.append(f"{relative} missing /{pattern}/")

    data = json.loads(read("evals/evals.json"))
    case = next((item for item in data.get("evals", []) if item.get("id") == 42), None)
    if case is None:
        failures.append("missing eval #42")
    else:
        fixture = ROOT / "evals" / "fixtures/shared-table-form-fixed-shell.vue"
        if not fixture.is_file():
            failures.append("eval #42 fixture is missing")
        else:
            fixture_text = fixture.read_text(encoding="utf-8")
            required_smells = ["h-dvh", "overflow-hidden", "<form"]
            if not all(smell in fixture_text for smell in required_smells):
                failures.append("eval #42 fixture no longer reproduces shared-shell clipping")
        if not case.get("negative_oracle") or not case.get("evidence_required"):
            failures.append("eval #42 needs a negative oracle and runtime evidence")
    return not failures, failures


def review_gap_regressions() -> tuple[bool, list[str]]:
    failures: list[str] = []
    required = {
        "references/anti-patterns.md": [
            r"appearance-none",
            r"Native datalist used as an authored combobox",
            r"date\|time\|month\|week\|datetime-local",
            r"::-webkit-scrollbar.*scrollbar-color.*scrollbar-width",
            r"h-full.*min-h-screen.*100dvh.*100svh.*height:\s*100%",
        ],
        "references/verification-checklist.md": [
            r"appearance-none",
            r"datalist.*input\[list\]|input\[list\].*datalist",
            r"time.*month.*week.*datetime-local",
            r"WebKit.*scrollbar-color.*scrollbar-width",
        ],
    }
    for relative, patterns in required.items():
        for pattern in patterns:
            if not contains(relative, pattern):
                failures.append(f"{relative} missing /{pattern}/")

    data = json.loads(read("evals/evals.json"))
    cases = {item.get("id"): item for item in data.get("evals", [])}
    fixture_smells = {
        43: ("native-datalist-combobox-gap.tsx", ["<datalist", 'list="customers"']),
        44: ("native-select-appearance-none.tsx", ["appearance-none", "<select"]),
        45: (
            "native-picker-sibling-locale-gap.tsx",
            ['type="time"', 'type="month"', 'type="week"', 'type="datetime-local"'],
        ),
        46: ("webkit-only-scrollbar-gap.css", ["::-webkit-scrollbar", "::-webkit-scrollbar-thumb"]),
        47: ("shared-shell-height-variants.vue", ["h-full", "min-h-screen", "height: 100%", "<form"]),
    }
    for case_id, (fixture_name, smells) in fixture_smells.items():
        case = cases.get(case_id)
        if case is None:
            failures.append(f"missing eval #{case_id}")
            continue
        fixture = ROOT / "evals" / "fixtures" / fixture_name
        if not fixture.is_file():
            failures.append(f"eval #{case_id} fixture is missing")
        else:
            fixture_text = fixture.read_text(encoding="utf-8")
            if not all(smell in fixture_text for smell in smells):
                failures.append(f"eval #{case_id} fixture no longer reproduces its review gap")
        if not case.get("negative_oracle") or not case.get("evidence_required"):
            failures.append(f"eval #{case_id} needs a negative oracle and runtime evidence")

    return not failures, failures


def canonical_project_audit_contract() -> tuple[bool, list[str]]:
    failures: list[str] = []
    required = {
        "SKILL.md": [
            r"Canonical UI Resolution Gate",
            r"audit_project\.py.*--mode strict",
            r"screen-local implementation",
        ],
        "references/canonical-ui-resolution.md": [
            r"Capability.*Canonical owner.*Source of truth.*Allowed variants.*Verification",
            r"business/domain/API contract",
            r"never executes them",
        ],
        "assets/UX-CONTRACT.template.md": [
            r"Table Selection",
            r"Select/Listbox",
            r"CRUD full-flow evidence",
        ],
        "references/verification-checklist.md": [
            r"Mandatory project audit sequence",
            r"failure-path",
            r"static auditor does not execute",
        ],
    }
    for relative, patterns in required.items():
        for pattern in patterns:
            if not contains(relative, pattern):
                failures.append(f"{relative} missing /{pattern}/")

    data = json.loads(read("evals/evals.json"))
    cases = {item.get("id"): item for item in data.get("evals", [])}
    fixtures = {
        48: ("canonical-owner-drift.vue", ["<select", 'href="#"']),
        49: ("scrollbar-opt-in.css", [".custom-scrollbar", "::-webkit-scrollbar-thumb"]),
        50: ("crud-failure-gap.md", ["happy paths", "not specified"]),
    }
    for case_id in range(48, 53):
        case = cases.get(case_id)
        if case is None:
            failures.append(f"missing eval #{case_id}")
            continue
        if not case.get("negative_oracle") or not case.get("evidence_required"):
            failures.append(f"eval #{case_id} needs a negative oracle and runtime evidence")
        if case_id in fixtures:
            fixture_name, smells = fixtures[case_id]
            fixture = ROOT / "evals" / "fixtures" / fixture_name
            if not fixture.is_file():
                failures.append(f"eval #{case_id} fixture is missing")
            else:
                fixture_text = fixture.read_text(encoding="utf-8")
                if not all(smell in fixture_text for smell in smells):
                    failures.append(f"eval #{case_id} fixture no longer reproduces its project-audit gap")
    return not failures, failures


def report(name: str, status: bool, failures: list[str] | None = None) -> bool:
    print(f"  {'PASS' if status else 'FAIL'}: {name}")
    for failure in failures or []:
        print(f"       -> {failure}")
    return status


def main() -> int:
    all_ok = True
    print("Legacy structural contracts")
    for name, status in legacy_checks.items():
        all_ok &= report(name, status)

    print("\nJapan-readiness structural proof")
    status, failures = japan_reference_structure()
    all_ok &= report("Direct references and required contracts", status, failures)
    status, failures = japan_routing()
    all_ok &= report("Independent market/locale/content routing", status, failures)
    status, failures = japan_eval_proof()
    all_ok &= report("Claim matrix, negative oracles, evidence, and fixtures", status, failures)

    print("\nSingle-select popup structural proof")
    status, failures = single_select_contract()
    all_ok &= report("Native/authored decision, geometry, anti-pattern, and eval", status, failures)

    print("\nDate-picker locale structural proof")
    status, failures = date_picker_contract()
    all_ok &= report("Native/authored decision, Japanese locale, anti-pattern, and eval", status, failures)

    print("\nGlobal scrollbar structural proof")
    status, failures = global_scrollbar_contract()
    all_ok &= report("Global baseline, no opt-in gap, forced colors, and eval", status, failures)

    print("\nTable/form scroll-ownership structural proof")
    status, failures = table_form_scroll_ownership_contract()
    all_ok &= report("Table viewport sizing remains scoped away from forms", status, failures)

    print("\nReview-gap regression proof")
    status, failures = review_gap_regressions()
    all_ok &= report("Datalist, utility, picker, engine, and height variants", status, failures)

    print("\nCanonical UI project-audit proof")
    status, failures = canonical_project_audit_contract()
    all_ok &= report("Resolution, reuse, static audit, and runtime boundary", status, failures)

    print(
        "\nBoundary: PASS proves repository wiring only; browser behavior, native-copy "
        "quality, target-user fit, and legal applicability require declared external evidence."
    )
    print(f"Overall: {'STRUCTURAL COVERAGE PASS' if all_ok else 'STRUCTURAL COVERAGE FAIL'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
