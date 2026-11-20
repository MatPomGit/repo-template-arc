"""Regression tests for Unicode character budgets in ARC documentation."""
from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "arc_docs_check", ROOT / "scripts/validate_documentation.py")
validator = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(validator)


class DocumentationPolicyTests(unittest.TestCase):
    def fixture(self, dest: Path) -> Path:
        shutil.copytree(ROOT, dest, ignore=shutil.ignore_patterns(
            ".git", ".venv", "__pycache__", "site"))
        return dest

    def test_scaffold_respects_document_budgets(self):
        self.assertEqual([], validator.check_documentation(ROOT))

    def test_unicode_codepoints_not_utf8_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp) / "arc")
            cfg = root / "config/documentation-policy.json"
            value = json.loads(cfg.read_text(encoding="utf-8"))
            value["exact_limits"]["SUPPORT.md"] = 100
            cfg.write_text(json.dumps(value), encoding="utf-8")
            (root / "SUPPORT.md").write_text("ą" * 100, encoding="utf-8")
            self.assertEqual([], validator.check_documentation(root))

    def test_overlong_architecture_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp) / "arc")
            (root / "ARCHITECTURE.md").write_text("x" * 12001, encoding="utf-8")
            self.assertTrue(any("DOC LENGTH EXCEEDED: ARCHITECTURE.md" in e
                                for e in validator.check_documentation(root)))

    def test_new_adr_is_capped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp) / "arc")
            (root / "docs/adr/0003-extra.md").write_text("x" * 6501, encoding="utf-8")
            self.assertTrue(any("DOC LENGTH EXCEEDED: docs/adr/0003-extra.md" in e
                                for e in validator.check_documentation(root)))

    def test_missing_governance_document_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp) / "arc")
            (root / "GOVERNANCE.md").unlink()
            self.assertIn("DOC MISSING: GOVERNANCE.md",
                          validator.check_documentation(root))

    def test_invalid_policy_path_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp) / "arc")
            cfg = root / "config/documentation-policy.json"
            policy = json.loads(cfg.read_text(encoding="utf-8"))
            policy["exact_limits"]["../private.md"] = 900
            cfg.write_text(json.dumps(policy), encoding="utf-8")
            self.assertIn("DOC POLICY: invalid limit or path ../private.md",
                          validator.check_documentation(root))

    def test_boolean_schema_version_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp) / "arc")
            cfg = root / "config/documentation-policy.json"
            policy = json.loads(cfg.read_text(encoding="utf-8"))
            policy["schema_version"] = True
            cfg.write_text(json.dumps(policy), encoding="utf-8")
            self.assertIn("DOC POLICY: unsupported schema_version",
                          validator.check_documentation(root))

    def test_symlink_to_external_file_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp) / "arc")
            external = Path(tmp) / "external.md"
            external.write_text("private", encoding="utf-8")
            (root / "SUPPORT.md").unlink()
            (root / "SUPPORT.md").symlink_to(external)
            self.assertIn("DOC SYMLINK: SUPPORT.md",
                          validator.check_documentation(root))

    def test_new_public_page_is_limited(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp) / "arc")
            (root / "pages/additional.md").write_text("x" * 6001, encoding="utf-8")
            self.assertTrue(any("DOC LENGTH EXCEEDED: pages/additional.md" in e
                                for e in validator.check_documentation(root)))


if __name__ == "__main__":
    unittest.main()
