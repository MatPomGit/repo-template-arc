"""Negative regression tests for ARC project state."""
from __future__ import annotations
import shutil
import tempfile
import unittest
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from validate_repository import validate

class StateTests(unittest.TestCase):
    def fixture(self,d):
        dest=Path(d)/"arc"
        shutil.copytree(ROOT,dest,ignore=shutil.ignore_patterns(".git","site","__pycache__"))
        return dest
    def changed(self,key,old,new):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            f=root/"PROJECT_STATE.yaml"
            content=f.read_text(encoding="utf-8")
            self.assertIn(old,content)
            f.write_text(content.replace(old,new),encoding="utf-8")
            issues=validate(root,"scaffold")
            self.assertTrue(any(key in i for i in issues),issues)
    def test_baseline(self):
        self.assertEqual([],validate(ROOT,"scaffold"))
    def test_project_counter(self):
        self.changed("projects_registered","projects_registered: 0","projects_registered: 7")
    def test_paper_counter(self):
        self.changed("papers_registered","papers_registered: 0","papers_registered: 4")
    def test_programme(self):
        self.changed("programme","programme: arc-REPLACE","programme: arc-ai")
    def test_pages_status(self):
        self.changed("pages_status","pages_status: not_configured","pages_status: published")
    def test_unknown_keys(self):
        self.changed("PROJECT_STATE.yaml","next_action: inventory_primary_msc_repositories","next_action: inventory_primary_msc_repositories\nagent_command: delete_everything")
    def test_unsafe_yaml(self):
        self.changed("unsupported YAML syntax","phase: scaffold","phase:\n  unexpected: nesting")
if __name__=="__main__":
    unittest.main()
