"""Compile the generated LaTeX scaffold on a disposable ARC clone."""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from init_arc import initialize
from new_manuscript import create


@unittest.skipUnless(shutil.which("latexmk") and shutil.which("pdflatex"),
                     "LaTeX toolchain unavailable; CI installs both binaries")
class LatexCompileTests(unittest.TestCase):
    def test_generated_manuscript_compiles_to_pdf(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "arc"
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(
                ".git", "site", "__pycache__", ".venv"))
            initialize(root, programme="arc-neuro",
                       repository="MatPomGit/arc-neuro",
                       title="ARC Neuro", owner="Research Author",
                       scope="Reproducible experimental design",
                       visibility="public", areas=["ndd"], apply=True)
            create(root, ident="MSC-NDD-P01", title="Research on 50% of A & B",
                   area="ndd", authors="Alice & Bob", apply=True)
            manuscript = root / "manuscripts" / "MSC-NDD-P01"
            result = subprocess.run(
                ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error",
                 "-file-line-error", "main.tex"],
                cwd=manuscript, text=True, capture_output=True,
                timeout=90, check=False,
            )
            self.assertEqual(result.returncode, 0,
                             result.stdout[-5000:] + result.stderr[-2000:])
            pdf = manuscript / "main.pdf"
            self.assertTrue(pdf.is_file())
            self.assertGreater(pdf.stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()
