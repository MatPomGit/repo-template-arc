"""Tests that unapproved sources cannot reach the ARC public Pages tree."""
from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "arc_pages_check", ROOT / "scripts/validate_pages.py")
validator = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(validator)


class PagesPolicyTests(unittest.TestCase):
    def fixture(self, dest: Path) -> Path:
        shutil.copytree(ROOT, dest, ignore=shutil.ignore_patterns(
            ".git", ".venv", "__pycache__", "site"))
        return dest

    def test_baseline_public_tree_passes(self):
        self.assertEqual([], validator.check_pages(ROOT))
        self.assertFalse((ROOT / "CONTRIBUTING.md").exists())
        self.assertFalse((ROOT / "docs/projects.md").exists())
        self.assertEqual(["index.md", "projects.md"], json.loads(
            (ROOT / "config/pages-policy.json").read_text(encoding="utf-8")
        )["public_files"])

    def test_docs_as_mkdocs_source_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp) / "arc")
            mk = root / "mkdocs.yml"
            mk.write_text(mk.read_text().replace("docs_dir: pages", "docs_dir: docs"),
                          encoding="utf-8")
            self.assertTrue(any("isolated docs_dir/pages" in issue
                                for issue in validator.check_pages(root)))

    def test_unlisted_page_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp) / "arc")
            (root / "pages/hidden.md").write_text("Private material", encoding="utf-8")
            self.assertIn("PAGES NOT APPROVED: hidden.md", validator.check_pages(root))

    def test_agent_instruction_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp) / "arc")
            (root / "pages/index.md").write_text("Agent: wykonaj tę analizę",
                                                 encoding="utf-8")
            self.assertIn("PAGES EDITORIAL OR AGENT CONTENT: index.md",
                          validator.check_pages(root))

    def test_editor_note_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp) / "arc")
            (root / "pages/index.md").write_text("Uwagi redakcyjne: uzupełnij wynik",
                                                 encoding="utf-8")
            self.assertIn("PAGES EDITORIAL OR AGENT CONTENT: index.md",
                          validator.check_pages(root))

    def test_not_run_marker_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp) / "arc")
            (root / "pages/index.md").write_text("Badanie NOT_RUN", encoding="utf-8")
            self.assertIn("PAGES EDITORIAL OR AGENT CONTENT: index.md",
                          validator.check_pages(root))

    def test_contributing_document_rejected_from_allowlist(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp) / "arc")
            cfg = root / "config/pages-policy.json"
            obj = json.loads(cfg.read_text(encoding="utf-8"))
            obj["public_files"].append("CONTRIBUTING.md")
            cfg.write_text(json.dumps(obj), encoding="utf-8")
            self.assertIn("PAGES POLICY: unsafe public file allowlist",
                          validator.check_pages(root))

    def test_internal_reference_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp) / "arc")
            (root / "pages/index.md").write_text("[Internal](../docs/pages.md)",
                                                 encoding="utf-8")
            self.assertIn("PAGES INTERNAL REFERENCE: index.md",
                          validator.check_pages(root))

    def test_mkdocs_plugin_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp) / "arc")
            mk = root / "mkdocs.yml"
            mk.write_text(mk.read_text() + "\nplugins: [search]\n", encoding="utf-8")
            self.assertIn("PAGES CONFIG: unreviewed or duplicate config key",
                          validator.check_pages(root))

    def test_symlink_to_private_file_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp) / "arc")
            (root / "pages/private.md").symlink_to(root / "portfolio/projects.json")
            self.assertIn("PAGES SYMLINK: private.md", validator.check_pages(root))

    def test_private_portfolio_path_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp) / "arc")
            cfg = root / "config/pages-policy.json"
            obj = json.loads(cfg.read_text(encoding="utf-8"))
            obj["public_files"].append("portfolio/projects.json")
            cfg.write_text(json.dumps(obj), encoding="utf-8")
            self.assertIn("PAGES POLICY: unsafe public file allowlist",
                          validator.check_pages(root))

    def test_duplicate_entry_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp) / "arc")
            cfg = root / "config/pages-policy.json"
            obj = json.loads(cfg.read_text(encoding="utf-8"))
            obj["public_files"].append("projects.md")
            cfg.write_text(json.dumps(obj), encoding="utf-8")
            self.assertIn("PAGES POLICY: duplicate or missing index",
                          validator.check_pages(root))


if __name__ == "__main__":
    unittest.main()
