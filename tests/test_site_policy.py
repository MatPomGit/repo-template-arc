"""Output HTML audit regression tests, without internet or MkDocs dependencies."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from validate_site import check_site

class SiteTests(unittest.TestCase):
    def site(self,d):
        site=Path(d)/"site"
        (site/"projects").mkdir(parents=True)
        (site/"index.html").write_text("<h1>Program badawczy</h1>",encoding="utf-8")
        (site/"projects/index.html").write_text("<h1>Publiczne projekty</h1>",encoding="utf-8")
        return site
    def test_html_site_passes(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual([],check_site(self.site(d)))
    def test_agent_prompt_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            site=self.site(d)
            (site/"index.html").write_text("<h1>Agent: wykonaj teraz</h1>",encoding="utf-8")
            self.assertTrue(any("SITE UNSAFE HTML" in e for e in check_site(site)))
    def test_internal_reference_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            site=self.site(d)
            (site/"index.html").write_text('<a href="../docs/secret.md">Tajne</a>',encoding="utf-8")
            self.assertTrue(any("SITE INTERNAL URL" in e for e in check_site(site)))
    def test_extra_private_directory_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            site=self.site(d)
            (site/"private").mkdir()
            (site/"private/file.html").write_text("private",encoding="utf-8")
            self.assertTrue(any("SITE UNSAFE PATH" in e for e in check_site(site)))
if __name__=="__main__":
    unittest.main()
