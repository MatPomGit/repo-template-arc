"""End-to-end CLI checks on an isolated ARC clone. No network or deployment."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEW_ID = "MSC-AI-P01"


class ArcCliLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "arc"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(
            ".git", "__pycache__", ".venv", "site", ".pytest_cache"))

    def tearDown(self):
        self.temp.cleanup()

    def cli(self, script: str, *args: str, code: int = 0):
        result = subprocess.run(
            [sys.executable, str(self.root / "scripts" / script),
             *([] if script == "build_public_catalog.py"
                else ["--root", str(self.root)]), *args],
            cwd=self.root, text=True, capture_output=True,
            timeout=25, check=False,
        )
        self.assertEqual(result.returncode, code,
                         f"{script}: stdout={result.stdout}\nstderr={result.stderr}")
        return result.stdout + result.stderr

    def initialize(self, visibility="public"):
        return self.cli(
            "init_arc.py", "--programme", "arc-ai",
            "--repository", "MatPomGit/arc-ai",
            "--title", "AI Research Programme",
            "--owner", "Research Author",
            "--scope", "Methods for reliable AI research",
            "--visibility", visibility, "--area", "learning",
            "--apply",
        )

    def manuscript(self, *extra):
        return self.cli(
            "new_manuscript.py", "--id", NEW_ID,
            "--title", "Prospective learning protocol", "--area", "learning",
            "--study-type", "methods", *extra,
        )

    def test_complete_public_lifecycle_and_no_accidental_disclosure(self):
        before = (self.root / "program.json").read_bytes()
        original_version = (self.root / "VERSION").read_bytes()
        preview = self.cli(
            "init_arc.py", "--programme", "arc-ai",
            "--repository", "MatPomGit/arc-ai",
            "--title", "AI Research Programme",
            "--owner", "Research Author",
            "--scope", "Methods for reliable AI research",
            "--visibility", "public", "--area", "learning",
        )
        self.assertIn("DRY_RUN", preview)
        self.assertEqual(before, (self.root / "program.json").read_bytes())
        self.initialize()
        self.assertIn("DRY_RUN", self.manuscript())
        tex = self.root / "manuscripts" / NEW_ID / "main.tex"
        self.assertFalse(tex.exists())
        self.assertIn("APPLIED", self.manuscript("--apply"))
        self.assertTrue(tex.is_file())
        self.cli("validate_study.py", "--path",
                 f"manuscripts/{NEW_ID}/study.yaml", "--paper-id", NEW_ID)
        self.cli("validate_repository.py", "--phase", "scaffold",
                 "--repo-visibility", "public",
                 "--repo-full-name", "MatPomGit/arc-ai")
        self.cli("build_public_catalog.py")
        self.cli("build_article_catalog.py")
        catalog = self.root / "pages" / "articles.md"
        body = catalog.read_text(encoding="utf-8")
        self.assertNotIn(NEW_ID, body)
        self.assertIn("Brak zatwierdzonych", body)
        self.cli("validate_pages.py")
        register = json.loads((self.root / "portfolio/papers.json").read_text())
        self.assertEqual(len(register["papers"]), 1)
        paper = register["papers"][0]
        self.assertEqual(paper["publication_stage"], "concept")
        self.assertIsNone(paper["stage_evidence"])
        self.assertFalse(paper["public_listing"])
        self.assertEqual(paper["owner"]["mode"], "local")
        self.assertIn(r"\author{}", tex.read_text(encoding="utf-8"))
        before_registry = (self.root / "portfolio/papers.json").read_bytes()
        before_catalog = catalog.read_bytes()
        self.assertIn("ALREADY_EXISTS", self.manuscript("--apply"))
        self.cli("build_article_catalog.py")
        self.assertEqual(before_registry, (self.root / "portfolio/papers.json").read_bytes())
        self.assertEqual(before_catalog, catalog.read_bytes())
        self.assertEqual((self.root / "VERSION").read_bytes(), original_version)
        self.assertEqual(self.cli("migrate_arc.py", "--mode", "plan").count("ALREADY_V2"), 1)

    def test_private_arc_stays_out_of_public_article_catalog(self):
        self.initialize("private")
        self.manuscript("--apply")
        self.cli("validate_repository.py", "--phase", "scaffold",
                 "--repo-visibility", "private",
                 "--repo-full-name", "MatPomGit/arc-ai")
        self.cli("build_article_catalog.py")
        self.assertNotIn(NEW_ID, (self.root / "pages/articles.md").read_text())
        self.assertEqual(
            json.loads((self.root / "program.json").read_text())["repository_visibility"],
            "private")

    def test_second_initialization_refused_without_mutation(self):
        self.initialize()
        program = self.root / "program.json"
        original = program.read_bytes()
        result = self.cli(
            "init_arc.py", "--programme", "arc-ai",
            "--repository", "MatPomGit/arc-ai",
            "--title", "AI Research Programme", "--owner", "Research Author",
            "--scope", "Methods for reliable AI research",
            "--visibility", "public", "--area", "learning", "--apply",
            code=2,
        )
        self.assertIn("re-initialize", result)
        self.assertEqual(program.read_bytes(), original)

    def test_inconsistent_v2_is_blocked_by_cli_and_never_claims_ready(self):
        self.initialize()
        registry = self.root / "portfolio/papers.json"
        source = json.loads(registry.read_text())
        source["schema_version"] = 1
        registry.write_text(json.dumps(source))
        result = self.cli("migrate_arc.py", "--mode", "plan", code=1)
        self.assertIn('"status": "BLOCKED"', result)
        self.assertNotIn("ALREADY_V2", result)
        self.assertEqual(json.loads(registry.read_text())["schema_version"], 1)


if __name__ == "__main__":
    unittest.main()
