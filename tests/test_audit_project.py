from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDITOR = REPO_ROOT / "scripts" / "audit_project.py"


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


if __name__ == "__main__":
    unittest.main()
