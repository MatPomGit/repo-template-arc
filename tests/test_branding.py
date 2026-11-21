"""Public ARC branding: reviewed local programme and project logos only."""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_public_catalog import render
from site_branding import approved_logo, expected_config
from validate_pages import check_pages


class BrandingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "arc"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(
            ".git", "site", "__pycache__", ".venv"))

    def tearDown(self):
        self.tmp.cleanup()

    def install(self, path: str) -> None:
        image = self.root / "pages" / path
        image.parent.mkdir(parents=True, exist_ok=True)
        image.write_bytes(b"\x89PNG\r\n\x1a\n" + b"synthetic-approved-logo")
        policy_path = self.root / "config/pages-policy.json"
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["public_files"].append(path)
        policy["approved_image_sha256"][path] = hashlib.sha256(
            image.read_bytes()).hexdigest()
        policy_path.write_text(json.dumps(policy), encoding="utf-8")

    def test_without_logo_uses_text_header(self):
        expected, logo = expected_config(self.root)
        self.assertIsNone(logo)
        self.assertEqual((self.root / "mkdocs.yml").read_text(), expected)
        self.assertEqual([], check_pages(self.root))

    def test_approved_programme_logo_appears_in_every_page_header(self):
        self.install("assets/brand/logo.png")
        expected, logo = expected_config(self.root)
        self.assertEqual(logo, "assets/brand/logo.png")
        (self.root / "mkdocs.yml").write_text(expected, encoding="utf-8")
        self.assertIn("  logo: assets/brand/logo.png", expected)
        self.assertEqual([], check_pages(self.root))

    def test_unapproved_programme_logo_blocks_header(self):
        image = self.root / "pages/assets/brand/logo.png"
        image.parent.mkdir(parents=True)
        image.write_bytes(b"logo")
        with self.assertRaisesRegex(ValueError, "Unapproved"):
            expected_config(self.root)
        self.assertTrue(any("PAGES LOGO:" in x for x in check_pages(self.root)))

    def test_wrong_logo_hash_is_rejected(self):
        self.install("assets/brand/logo.png")
        (self.root / "pages/assets/brand/logo.png").write_bytes(b"different")
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            expected_config(self.root)

    def test_approved_project_logo_only_for_public_listing(self):
        self.install("assets/projects/msc-demo.png")
        reg = self.root / "portfolio/projects.json"
        data = json.loads(reg.read_text(encoding="utf-8"))
        project = {"id": "msc-demo", "title": "Projekt demonstracyjny",
                   "pages_url": "https://example.org/demo", "visibility": "public",
                   "public_listing": True}
        data["projects"].append(project)
        reg.write_text(json.dumps(data), encoding="utf-8")
        self.assertIn('src="assets/projects/msc-demo.png"', render(self.root))
        project["public_listing"] = False
        reg.write_text(json.dumps(data), encoding="utf-8")
        self.assertNotIn("msc-demo.png", render(self.root))

    def test_readme_contains_no_editorial_instructions(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for forbidden in ("Zastąp ten akapit", "REPLACE_PROGRAM_NAME",
                          "Jeśli skonfigurowano", "Nie twórz osobnego"):
            self.assertNotIn(forbidden, readme)


if __name__ == "__main__":
    unittest.main()
