from __future__ import annotations

import json
import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDITOR = REPO_ROOT / "scripts" / "audit_project.py"
VERIFY_CASES_PATH = REPO_ROOT / "scripts" / "verify_cases.py"

VERIFY_CASES_SPEC = importlib.util.spec_from_file_location("verify_cases_under_test", VERIFY_CASES_PATH)
assert VERIFY_CASES_SPEC is not None and VERIFY_CASES_SPEC.loader is not None
VERIFY_CASES = importlib.util.module_from_spec(VERIFY_CASES_SPEC)
VERIFY_CASES_SPEC.loader.exec_module(VERIFY_CASES)


class AuditProjectCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directories: list[tempfile.TemporaryDirectory[str]] = []

    def tearDown(self) -> None:
        for directory in self._temporary_directories:
            directory.cleanup()

    def project(self, files: dict[str, str]) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self._temporary_directories.append(temporary)
        root = Path(temporary.name)
        for relative_path, content in files.items():
            target = root / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        return root

    def run_audit(
        self,
        root: Path,
        mode: str,
        *,
        no_write: bool = False,
        config: Path | None = None,
        output: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, str(AUDITOR), str(root), "--mode", mode]
        if no_write:
            command.append("--no-write")
        if config is not None:
            command.extend(["--config", str(config)])
        if output is not None:
            command.extend(["--output", str(output)])
        return subprocess.run(command, capture_output=True, text=True, check=False)

    @staticmethod
    def payload(completed: subprocess.CompletedProcess[str]) -> dict[str, object]:
        return json.loads(completed.stdout)

    def rule_ids(self, completed: subprocess.CompletedProcess[str]) -> list[str]:
        payload = self.payload(completed)
        return [finding["ruleId"] for finding in payload["findings"]]

    @staticmethod
    def canonical_map(rows: list[tuple[str, str]] | None = None) -> str:
        rows = rows if rows is not None else [
            ("Select/Listbox", "AppSelect"),
            ("Date", "AppDateField"),
            ("Form", "AppForm"),
            ("Scrollbar", "styles/base.css"),
            ("CRUD", "order routes"),
        ]
        body = "\n".join(
            f"| {capability} | {owner} | UX-CONTRACT.md | native / authored | E2E |"
            for capability, owner in rows
        )
        return (
            "# UX Contract\n\n## Canonical UI Map\n\n"
            "| Capability | Canonical owner | Source of truth | Allowed variants | Verification |\n"
            "|---|---|---|---|---|\n"
            f"{body}\n"
        )

    def product_files(
        self,
        *,
        canonical_rows: list[tuple[str, str]] | None = None,
        ownership: dict[str, str] | None = None,
        source: str | None = None,
        required_commands: list[str] | None = None,
        evidence: dict[str, str] | None = None,
    ) -> dict[str, str]:
        manifest = {
            "profile": "product-admin",
            "sourceRoots": ["src"],
            "locale": "ja-JP",
            "canonicalMap": "UX-CONTRACT.md",
            "requiredCapabilities": ["Select/Listbox", "Date", "Form", "Scrollbar", "CRUD"],
            "ownership": ownership or {
                "Select/Listbox": "authored",
                "Date": "typed",
            },
            "requiredCommands": required_commands or [],
            "commands": {},
            "evidence": evidence or {},
        }
        return {
            "premium-ui.json": json.dumps(manifest, ensure_ascii=False),
            "DESIGN.md": "# Design\n\nScrollbar tokens are global.\n",
            "UX-CONTRACT.md": self.canonical_map(canonical_rows),
            "src/App.vue": source
            or '<template><form novalidate @submit.prevent="save"><AppSelect /><input type="text"><button type="submit">保存</button></form></template>',
            "src/styles.css": "* { scrollbar-color: #64748b #f8fafc; scrollbar-width: thin; }\n",
            "package.json": json.dumps({"scripts": {}}),
        }

    def violating_files(self) -> dict[str, str]:
        files = self.product_files(
            source='<template><form><a href="#">保存</a><button>削除</button></form></template>'
        )
        files["src/styles.css"] = ".custom-scrollbar::-webkit-scrollbar-thumb { background: #64748b; }\n"
        return files

    def test_malformed_manifest_returns_two(self) -> None:
        root = self.project({"premium-ui.json": "{"})
        completed = self.run_audit(root, "strict", no_write=True)
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(self.payload(completed)["findings"][0]["ruleId"], "config.invalid-json")

    def test_report_mode_records_violation_but_returns_zero(self) -> None:
        completed = self.run_audit(self.project(self.violating_files()), "report", no_write=True)
        self.assertEqual(completed.returncode, 0)
        self.assertIn("affordance.empty-href", self.rule_ids(completed))

    def test_strict_mode_returns_one_for_contract_violations(self) -> None:
        completed = self.run_audit(self.project(self.violating_files()), "strict", no_write=True)
        self.assertEqual(completed.returncode, 1)

    def test_unresolved_owner_returns_two_in_strict_mode(self) -> None:
        files = self.product_files(canonical_rows=[])
        completed = self.run_audit(self.project(files), "strict", no_write=True)
        self.assertEqual(completed.returncode, 2)
        self.assertIn("canonical.owner-unresolved", self.rule_ids(completed))

    def test_json_schema_and_finding_shape_are_stable(self) -> None:
        completed = self.run_audit(self.project(self.violating_files()), "report", no_write=True)
        payload = self.payload(completed)
        self.assertEqual(
            set(payload),
            {"schemaVersion", "mode", "projectRoot", "findings", "summary"},
        )
        self.assertEqual(
            set(payload["findings"][0]),
            {"file", "line", "ruleId", "severity", "category", "message", "remediation"},
        )
        ordering = [
            (item["category"], item["ruleId"], item["file"], item["line"] or 0, item["message"])
            for item in payload["findings"]
        ]
        self.assertEqual(ordering, sorted(ordering))

    def test_explicit_native_ownership_suppresses_native_control_findings(self) -> None:
        files = self.product_files(
            ownership={"Select/Listbox": "native", "Date": "native"},
            source='<template><form novalidate><select aria-label="部署"></select><input type="date"></form></template>',
        )
        completed = self.run_audit(self.project(files), "strict", no_write=True)
        ids = self.rule_ids(completed)
        self.assertNotIn("ownership.native-select-undecided", ids)
        self.assertNotIn("ownership.native-date-undecided", ids)

    def test_unreadable_canonical_map_returns_structured_config_finding(self) -> None:
        root = self.project(self.product_files())
        (root / "UX-CONTRACT.md").write_bytes(b"\x81\xff\x81")

        completed = self.run_audit(root, "strict", no_write=True)

        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stderr, "")
        self.assertIn("canonical.map-unreadable", self.rule_ids(completed))

    def test_directory_canonical_map_returns_structured_config_finding(self) -> None:
        files = self.product_files()
        files.pop("UX-CONTRACT.md")
        root = self.project(files)
        (root / "UX-CONTRACT.md").mkdir()

        completed = self.run_audit(root, "strict", no_write=True)

        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stderr, "")
        self.assertIn("canonical.map-unreadable", self.rule_ids(completed))

    def test_default_submit_button_inside_form_is_actionable(self) -> None:
        files = self.product_files(
            source='<template><form novalidate @submit.prevent="save"><button>保存</button></form></template>'
        )

        completed = self.run_audit(self.project(files), "strict", no_write=True)

        self.assertNotIn("affordance.actionless-button", self.rule_ids(completed))

    def test_vue_click_modifier_is_detected_as_a_button_action(self) -> None:
        files = self.product_files(
            source='<template><button type="button" @click.stop="open">開く</button></template>'
        )

        completed = self.run_audit(self.project(files), "strict", no_write=True)

        self.assertNotIn("affordance.actionless-button", self.rule_ids(completed))

    def test_form_attribute_greater_than_does_not_hide_novalidate(self) -> None:
        files = self.product_files(
            source=(
                '<template><form id="order" data-tip="a > b" novalidate></form>'
                '<button type=submit form=order>保存</button></template>'
            )
        )

        completed = self.run_audit(self.project(files), "strict", no_write=True)

        ids = self.rule_ids(completed)
        self.assertNotIn("form.novalidate-missing", ids)
        self.assertNotIn("affordance.actionless-button", ids)

    def test_jsx_arrow_handler_does_not_truncate_form_attributes(self) -> None:
        files = self.product_files(
            source=(
                '<form onSubmit={(event) => save(event)} noValidate>'
                '<button type="submit">Save</button></form>'
            )
        )

        completed = self.run_audit(self.project(files), "strict", no_write=True)

        self.assertNotIn("form.novalidate-missing", self.rule_ids(completed))

    def test_tag_shaped_attribute_text_does_not_create_phantom_form(self) -> None:
        files = self.product_files(
            source='<div data-example="<form>">Documentation example</div>'
        )

        completed = self.run_audit(self.project(files), "strict", no_write=True)

        self.assertNotIn("form.novalidate-missing", self.rule_ids(completed))

    def test_tag_shaped_javascript_string_does_not_create_phantom_form(self) -> None:
        files = self.product_files(
            source='const example = "<form>"; export default function Page() { return <div /> }'
        )

        completed = self.run_audit(self.project(files), "strict", no_write=True)

        self.assertNotIn("form.novalidate-missing", self.rule_ids(completed))

    def test_tag_shaped_string_inside_jsx_expression_does_not_create_phantom_form(self) -> None:
        files = self.product_files(
            source='<div>{show ? "<form>" : null}</div>'
        )

        completed = self.run_audit(self.project(files), "strict", no_write=True)

        self.assertNotIn("form.novalidate-missing", self.rule_ids(completed))

    def test_tag_shaped_comment_inside_jsx_expression_does_not_create_phantom_form(self) -> None:
        files = self.product_files(
            source='<div>{condition && (\n// <form>\nvalue\n)}</div>'
        )

        completed = self.run_audit(self.project(files), "strict", no_write=True)

        self.assertNotIn("form.novalidate-missing", self.rule_ids(completed))

    def test_real_form_inside_jsx_expression_is_still_audited(self) -> None:
        files = self.product_files(
            source='<div>{show ? <form>Draft</form> : null}</div>'
        )

        completed = self.run_audit(self.project(files), "strict", no_write=True)

        self.assertIn("form.novalidate-missing", self.rule_ids(completed))

    def test_tag_shaped_top_level_javascript_regex_does_not_create_phantom_form(self) -> None:
        files = self.product_files(
            source='const pattern = /<form>/; export default function Page() { return <div /> }'
        )

        completed = self.run_audit(self.project(files), "strict", no_write=True)

        self.assertNotIn("form.novalidate-missing", self.rule_ids(completed))

    def test_tag_shaped_regex_inside_jsx_expression_does_not_create_phantom_form(self) -> None:
        files = self.product_files(
            source='<div>{/<form>/.test(value) ? "match" : "miss"}</div>'
        )

        completed = self.run_audit(self.project(files), "strict", no_write=True)

        self.assertNotIn("form.novalidate-missing", self.rule_ids(completed))

    def test_external_form_button_defaults_to_submit(self) -> None:
        files = self.product_files(
            source=(
                '<template><form id="order" novalidate></form>'
                '<button form="order">保存</button></template>'
            )
        )

        completed = self.run_audit(self.project(files), "strict", no_write=True)

        self.assertNotIn("affordance.actionless-button", self.rule_ids(completed))

    def test_unquoted_native_date_reports_recorded_ownership_conflict(self) -> None:
        files = self.product_files(
            ownership={"Select/Listbox": "authored", "Date": "typed"},
            source='<template><form novalidate><input type=date></form></template>',
        )

        completed = self.run_audit(self.project(files), "strict", no_write=True)

        ids = self.rule_ids(completed)
        self.assertIn("ownership.native-date-conflict", ids)
        self.assertNotIn("ownership.native-date-undecided", ids)

    def test_recorded_authored_select_reports_conflict_not_undecided(self) -> None:
        files = self.product_files(
            ownership={"Select/Listbox": "authored", "Date": "typed"},
            source='<template><form novalidate><select aria-label="部署"></select></form></template>',
        )

        completed = self.run_audit(self.project(files), "strict", no_write=True)

        ids = self.rule_ids(completed)
        self.assertIn("ownership.native-select-conflict", ids)
        self.assertNotIn("ownership.native-select-undecided", ids)

    def test_missing_runtime_evidence_is_reported_without_execution(self) -> None:
        root = self.project(self.product_files(required_commands=["e2e"]))
        completed = self.run_audit(root, "strict", no_write=True)
        self.assertIn("evidence.command-missing", self.rule_ids(completed))
        self.assertFalse((root / "command-was-run").exists())

    def test_scrollbar_and_shared_shell_rules_are_reported(self) -> None:
        files = self.product_files(
            source='<template><main class="h-screen overflow-hidden"><form novalidate><table></table></form></main></template>'
        )
        files["src/styles.css"] = ".custom-scrollbar::-webkit-scrollbar-thumb { background: red; }"
        completed = self.run_audit(self.project(files), "strict", no_write=True)
        ids = self.rule_ids(completed)
        self.assertIn("scrollbar.opt-in-base", ids)
        self.assertIn("scrollbar.webkit-only", ids)
        self.assertIn("layout.shared-shell-overflow", ids)

    def test_shared_shell_variants_report_the_real_constraint_line(self) -> None:
        files = self.product_files(
            source=(
                '<template>\n<header>Orders</header>\n'
                '<main class="h-full overflow-hidden">\n'
                '<section><table></table><form novalidate></form></section>\n'
                '</main>\n</template>'
            )
        )

        completed = self.run_audit(self.project(files), "strict", no_write=True)
        findings = self.payload(completed)["findings"]
        finding = next(item for item in findings if item["ruleId"] == "layout.shared-shell-overflow")

        self.assertEqual(finding["line"], 3)

    def test_scrollbar_audit_checks_real_selectors_and_both_standard_properties(self) -> None:
        files = self.product_files()
        files["src/styles.css"] = (
            "/* docs mention ::-webkit-scrollbar only */\n"
            ":root { scrollbar-color: #64748b #f8fafc; }\n"
            ".custom-scrollbar::-webkit-scrollbar-thumb { background: red; }\n"
        )

        completed = self.run_audit(self.project(files), "strict", no_write=True)
        findings = self.payload(completed)["findings"]
        by_rule = {item["ruleId"]: item for item in findings}

        self.assertEqual(by_rule["scrollbar.webkit-only"]["line"], 3)
        self.assertEqual(by_rule["scrollbar.opt-in-base"]["line"], 3)

    def test_scrollbar_audit_ignores_supports_selector_probe(self) -> None:
        files = self.product_files()
        files["src/styles.css"] = (
            "@supports selector(::-webkit-scrollbar) {\n"
            "  .panel { color: black; }\n"
            "}\n"
        )

        completed = self.run_audit(self.project(files), "strict", no_write=True)

        self.assertNotIn("scrollbar.webkit-only", self.rule_ids(completed))

    def test_unrelated_standard_scrollbar_rule_does_not_cover_webkit_surface(self) -> None:
        files = self.product_files()
        files["src/styles.css"] = (
            ".special { scrollbar-color: #64748b #f8fafc; scrollbar-width: thin; }\n"
            ".panel::-webkit-scrollbar-thumb { background: red; }\n"
        )

        completed = self.run_audit(self.project(files), "strict", no_write=True)

        self.assertIn("scrollbar.webkit-only", self.rule_ids(completed))

    def test_scrollbar_surface_matching_does_not_use_class_prefixes(self) -> None:
        files = self.product_files()
        files["src/styles.css"] = (
            ".panel { scrollbar-color: #64748b #f8fafc; scrollbar-width: thin; }\n"
            ".panel2::-webkit-scrollbar-thumb { background: red; }\n"
        )

        completed = self.run_audit(self.project(files), "strict", no_write=True)

        self.assertIn("scrollbar.webkit-only", self.rule_ids(completed))

    def test_scrollbar_state_selector_uses_the_same_owning_surface(self) -> None:
        files = self.product_files()
        files["src/styles.css"] = (
            ".panel { scrollbar-color: #64748b #f8fafc; scrollbar-width: thin; }\n"
            ".panel:hover::-webkit-scrollbar-thumb { background: red; }\n"
        )

        completed = self.run_audit(self.project(files), "strict", no_write=True)

        self.assertNotIn("scrollbar.webkit-only", self.rule_ids(completed))

    def test_scrollbar_escaped_colon_class_preserves_the_owning_surface(self) -> None:
        files = self.product_files()
        files["src/styles.css"] = (
            ".dark\\:panel { scrollbar-color: #64748b #f8fafc; scrollbar-width: thin; }\n"
            ".dark\\:panel:hover::-webkit-scrollbar-thumb { background: red; }\n"
        )

        completed = self.run_audit(self.project(files), "strict", no_write=True)

        self.assertNotIn("scrollbar.webkit-only", self.rule_ids(completed))

    def test_scrollbar_selector_lists_are_evaluated_per_surface(self) -> None:
        files = self.product_files()
        files["src/styles.css"] = (
            ".b { scrollbar-color: #64748b #f8fafc; scrollbar-width: thin; }\n"
            ".a, .b::-webkit-scrollbar-thumb { background: red; }\n"
        )

        completed = self.run_audit(self.project(files), "strict", no_write=True)

        self.assertNotIn("scrollbar.webkit-only", self.rule_ids(completed))

    def test_scrollbar_custom_properties_do_not_count_as_standard_declarations(self) -> None:
        files = self.product_files()
        files["src/styles.css"] = (
            ".panel { --scrollbar-color: red; --scrollbar-width: thin; }\n"
            ".panel::-webkit-scrollbar-thumb { background: red; }\n"
        )

        completed = self.run_audit(self.project(files), "strict", no_write=True)

        self.assertIn("scrollbar.webkit-only", self.rule_ids(completed))

    def test_nested_scss_declarations_do_not_cover_parent_surface(self) -> None:
        files = self.product_files()
        files["src/styles.scss"] = (
            ".special {\n"
            "  .inner { scrollbar-color: red blue; scrollbar-width: thin; }\n"
            "}\n"
            ".special::-webkit-scrollbar-thumb { background: red; }\n"
        )

        completed = self.run_audit(self.project(files), "strict", no_write=True)

        self.assertIn("scrollbar.webkit-only", self.rule_ids(completed))

    def test_table_local_overflow_does_not_flag_natural_height_form(self) -> None:
        files = self.product_files(
            source=(
                '<template><main class="min-h-screen">'
                '<section class="h-full overflow-hidden"><table></table></section>'
                '<form novalidate>Natural height form</form>'
                '</main></template>'
            )
        )

        completed = self.run_audit(self.project(files), "strict", no_write=True)

        self.assertNotIn("layout.shared-shell-overflow", self.rule_ids(completed))

    def test_unreadable_source_returns_structured_unresolved_finding(self) -> None:
        root = self.project(self.product_files())
        (root / "src" / "Legacy.vue").write_bytes(b"\x81\xff\x81")

        completed = self.run_audit(root, "strict", no_write=True)

        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stderr, "")
        self.assertIn("source.unreadable", self.rule_ids(completed))

    def test_output_write_failure_returns_structured_operational_finding(self) -> None:
        root = self.project(self.product_files())
        output = root / "audit-output"
        output.mkdir()

        completed = self.run_audit(root, "report", output=output)

        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stderr, "")
        self.assertIn("output.write-failed", self.rule_ids(completed))

    def test_output_options_write_the_stable_report(self) -> None:
        root = self.project(self.product_files())
        output = root / "artifacts" / "audit.json"
        completed = self.run_audit(root, "report", output=output)
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(json.loads(output.read_text(encoding="utf-8")), self.payload(completed))

    def test_explicit_config_path_is_supported(self) -> None:
        files = self.product_files()
        manifest = files.pop("premium-ui.json")
        files["config/premium.json"] = manifest
        root = self.project(files)
        completed = self.run_audit(root, "strict", no_write=True, config=root / "config/premium.json")
        self.assertNotIn("config.invalid-json", self.rule_ids(completed))

    def test_textarea_without_resize_none_is_a_contract_violation(self) -> None:
        files = self.product_files(
            source='<template><form novalidate><label for="note">備考</label><textarea id="note"></textarea></form></template>'
        )
        completed = self.run_audit(self.project(files), "strict", no_write=True)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("form.textarea-resize-missing", self.rule_ids(completed))

    def test_textarea_with_canonical_resize_style_passes_resize_audit(self) -> None:
        files = self.product_files(
            source='<template><form novalidate><label for="note">備考</label><textarea id="note" class="resize-none"></textarea></form></template>'
        )
        completed = self.run_audit(self.project(files), "strict", no_write=True)
        self.assertNotIn("form.textarea-resize-missing", self.rule_ids(completed))


class DocumentationContractTests(unittest.TestCase):
    EXPECTED_COLUMNS = (
        "Capability",
        "Canonical owner",
        "Source of truth",
        "Allowed variants",
        "Verification",
    )

    def test_skill_requires_resolution_before_implementation(self) -> None:
        skill = (REPO_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Canonical UI Resolution Gate", skill)
        self.assertIn("python <this-skill-dir>/scripts/audit_project.py", skill)

    def test_contract_template_has_exact_canonical_map_columns(self) -> None:
        template = (REPO_ROOT / "assets" / "UX-CONTRACT.template.md").read_text(encoding="utf-8")
        header = "| " + " | ".join(self.EXPECTED_COLUMNS) + " |"
        self.assertIn(header, template)

    def test_loading_contract_defaults_to_spinner_and_makes_skeleton_explicit(self) -> None:
        matrix = (REPO_ROOT / "references" / "decision-matrix.md").read_text(encoding="utf-8")
        self.assertIn("App-owned loading indicator/spinner", matrix)
        self.assertIn("Skeleton is optional", matrix)
        self.assertIn("prompt, business requirement, or canonical project contract", matrix)

    def test_url_state_is_default_with_documented_business_override(self) -> None:
        skill = (REPO_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Persist committed search, active filters, sort, page, and page size in URL", skill)
        self.assertIn("transient, sensitive, non-shareable, or architecture-constrained", skill)

    def test_form_and_responsive_dialog_contracts_are_explicit(self) -> None:
        interaction = (REPO_ROOT / "references" / "interaction-contract.md").read_text(encoding="utf-8")
        self.assertIn('aria-invalid="true"', interaction)
        self.assertIn("Clicking a visible label", interaction)
        self.assertIn("visual viewport and safe-area bounds", interaction)
        self.assertIn("virtual keyboard", interaction)

    def test_basic_keyboard_is_required_but_extended_mobile_evidence_is_advisory(self) -> None:
        checklist = (REPO_ROOT / "references" / "verification-checklist.md").read_text(encoding="utf-8")
        self.assertIn("Required accessibility baseline", checklist)
        self.assertIn("Recommended extended verification", checklist)
        self.assertIn("touch-target measurement", checklist)
        self.assertIn("200% zoom matrix", checklist)

    def verify_root(self, overrides: dict[str, str]) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        files = (
            "SKILL.md",
            "references/data-entry-patterns.md",
            "references/anti-patterns.md",
            "references/verification-checklist.md",
            "evals/evals.json",
            "evals/fixtures/native-select-popup-mismatch.tsx",
        )
        for relative in files:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            content = overrides.get(relative, (REPO_ROOT / relative).read_text(encoding="utf-8"))
            target.write_text(content, encoding="utf-8")
        return root

    def run_single_select_contract(self, root: Path) -> tuple[bool, list[str]]:
        original_root = VERIFY_CASES.ROOT
        try:
            VERIFY_CASES.ROOT = root
            return VERIFY_CASES.single_select_contract()
        finally:
            VERIFY_CASES.ROOT = original_root

    def test_single_select_proof_fails_without_skill_contract_bullet(self) -> None:
        skill = (REPO_ROOT / "SKILL.md").read_text(encoding="utf-8")
        skill = "\n".join(
            line for line in skill.splitlines()
            if not line.startswith("- For every single-select dropdown")
        )

        status, failures = self.run_single_select_contract(self.verify_root({"SKILL.md": skill}))

        self.assertFalse(status, failures)

    def test_single_select_proof_fails_without_data_entry_section(self) -> None:
        patterns = (REPO_ROOT / "references" / "data-entry-patterns.md").read_text(encoding="utf-8")
        patterns = re.sub(
            r"(?ms)^Decide whether the popup may remain platform-owned.*?(?=^Treat trigger)",
            "",
            patterns,
        )

        status, failures = self.run_single_select_contract(
            self.verify_root({"references/data-entry-patterns.md": patterns})
        )

        self.assertFalse(status, failures)


if __name__ == "__main__":
    unittest.main()
