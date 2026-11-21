"""Negative tests for closed schemas, provenance and submodule trust."""
from __future__ import annotations
import json
import shutil
import tempfile
import unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from validate_repository import validate

PROJECT={"id":"msc-example","title":"Public project","repository":"MatPomGit/msc-example",
"url":"https://github.com/MatPomGit/msc-example","role":"primary","primary_program":"arc-neuro",
"line":"ndd","status":"active","visibility":"public","public_listing":False,
"default_branch":"main","snapshot_sha":None,"pages_url":None,"submodule_path":None}
PAPER={"id":"MSC-CR-P05","title":"Hypothesis","area":"ndd",
"research_state":"planned","publication_stage":"published","relation":"primary",
"owner":{"mode":"external","repository":"MatPomGit/msc-example","project_id":"msc-example"},
"manuscript":{"path":"manuscripts/P05/main.tex","format":"latex"},
"study_plan":None,"public_listing":False,"doi":None,
"preprint_url":None,"preregistration_url":None,"publication_url":None,"stage_evidence":None}

class MetadataTests(unittest.TestCase):
    def fixture(self,d):
        root=Path(d)/"arc"
        shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns(".git","site","__pycache__"))
        meta=json.loads((root/"program.json").read_text(encoding="utf-8"))
        meta.update(repository_visibility="public",programme="arc-neuro")
        (root/"program.json").write_text(json.dumps(meta),encoding="utf-8")
        state=root/"PROJECT_STATE.yaml"
        state.write_text(state.read_text().replace("programme: arc-REPLACE","programme: arc-neuro")
              .replace("projects_registered: 0","projects_registered: 1")
              .replace("papers_registered: 0","papers_registered: 1")
              .replace("phase: scaffold","phase: active"),encoding="utf-8")
        (root/"areas/index.json").write_text(json.dumps({"lines":[{"id":"ndd","title":"NDD"}]}),encoding="utf-8")
        (root/"portfolio/projects.json").write_text(json.dumps({"schema_version":2,"projects":[PROJECT.copy()]}),encoding="utf-8")
        (root/"portfolio/papers.json").write_text(json.dumps({"schema_version":2,"papers":[PAPER.copy()]}),encoding="utf-8")
        return root
    def test_published_requires_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            issues=validate(self.fixture(d))
            self.assertTrue(any("status evidence" in e for e in issues),issues)
            self.assertTrue(any("lacks DOI" in e for e in issues),issues)
    def test_private_metadata_extra_field_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            f=root/"portfolio/projects.json"
            o=json.loads(f.read_text())
            o["projects"][0]["private_summary"]="DO_NOT_PUBLISH"
            f.write_text(json.dumps(o),encoding="utf-8")
            self.assertTrue(any("Undeclared project metadata" in e for e in validate(root)))
    def test_undeclared_area_line_metadata_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            f=root/"areas/index.json"
            o=json.loads(f.read_text())
            o["lines"][0]["confidential_programme_name"]="PRIVATE"
            f.write_text(json.dumps(o),encoding="utf-8")
            self.assertTrue(any("Undeclared research line metadata" in e for e in validate(root)))
    def test_undeclared_programme_field_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            f=root/"program.json"
            o=json.loads(f.read_text())
            o["internal_token_reference"]="PRIVATE"
            f.write_text(json.dumps(o),encoding="utf-8")
            self.assertTrue(any("Undeclared programme metadata" in e for e in validate(root)))
    def test_extra_paper_field_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            f=root/"portfolio/papers.json"
            o=json.loads(f.read_text())
            o["papers"][0]["private_submission_url"]="https://secret.example"
            f.write_text(json.dumps(o),encoding="utf-8")
            self.assertTrue(any("Undeclared paper metadata" in e for e in validate(root)))
    def test_valid_published_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            f=root/"portfolio/papers.json"
            o=json.loads(f.read_text())
            o["papers"][0].update(publication_url="https://example.org/article",
                stage_evidence={"kind":"publication_record","sha256":"a"*64,"checked_on":"2026-11-20"})
            f.write_text(json.dumps(o),encoding="utf-8")
            self.assertEqual([],validate(root))
    def test_unauthorised_submodule_url_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            f=root/"portfolio/papers.json"
            f.write_text(json.dumps({"schema_version":2,"papers":[]}),encoding="utf-8")
            st=root/"PROJECT_STATE.yaml"
            st.write_text(st.read_text().replace("papers_registered: 1","papers_registered: 0"),encoding="utf-8")
            f=root/"portfolio/projects.json"
            o=json.loads(f.read_text())
            o["projects"][0].update(submodule_path="projects/msc-example",snapshot_sha="a"*40)
            f.write_text(json.dumps(o),encoding="utf-8")
            (root/".gitmodules").write_text('[submodule "msc-example"]\n  path = projects/msc-example\n  url = https://evil.example/msc-example\n',encoding="utf-8")
            self.assertTrue(any("Untrusted submodule URL" in e for e in validate(root)))
    def test_unregistered_submodule_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            (root/".gitmodules").write_text('[submodule "unknown"]\n  path = projects/unknown\n  url = https://github.com/MatPomGit/unknown\n',encoding="utf-8")
            self.assertTrue(any("Unregistered submodule" in e for e in validate(root)))
if __name__=="__main__":
    unittest.main()
