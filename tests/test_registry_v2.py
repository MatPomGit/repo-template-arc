"""ARC v2: local and external ownership, provenance and negative cases."""
from __future__ import annotations
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from validate_repository import validate

def paper(mode="local"):
    return {"id":"MSC-CR-P05","title":"Prospective study","area":"ndd",
            "research_state":"planned","publication_stage":"concept","relation":"primary",
            "owner":{"mode":mode,"repository":"MatPomGit/arc-neuro" if mode=="local"
                     else "MatPomGit/msc-example","project_id":None if mode=="local" else "msc-example"},
            "manuscript":{"path":"manuscripts/MSC-CR-P05/main.tex" if mode=="local"
                          else "manuscripts/P05/main.tex","format":"latex"},
            "study_plan":None,"public_listing":False,"doi":None,
            "preprint_url":None,"preregistration_url":None,"publication_url":None,"stage_evidence":None}

class RegistryV2Tests(unittest.TestCase):
    @staticmethod
    def write(root,path,data):
        (root/path).write_text(json.dumps(data),encoding="utf-8")

    def fixture(self,folder):
        root=Path(folder)/"arc"
        shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns(".git","site","__pycache__"))
        meta=json.loads((root/"program.json").read_text())
        meta.update(programme="arc-neuro",repository_visibility="public",
                    repository_full_name="MatPomGit/arc-neuro")
        self.write(root,"program.json",meta)
        self.write(root,"areas/index.json",{"schema_version":1,"lines":[{"id":"ndd","title":"NDD"}]})
        state=root/"PROJECT_STATE.yaml"
        state.write_text(state.read_text().replace("programme: arc-REPLACE","programme: arc-neuro")
                         .replace("papers_registered: 0","papers_registered: 1")
                         .replace("phase: scaffold","phase: active"))
        self.write(root,"portfolio/papers.json",{"schema_version":2,"papers":[paper()]})
        f=root/"manuscripts/MSC-CR-P05/main.tex"
        f.parent.mkdir(parents=True)
        f.write_text("\\documentclass{article}\n\\begin{document}Draft\\end{document}\n")
        return root

    def test_baseline_and_local_owner_without_project(self):
        self.assertEqual([],validate(ROOT))
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual([],validate(self.fixture(d)))

    def test_external_owner_registered(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            self.write(root,"portfolio/papers.json",{"schema_version":2,"papers":[paper("external")]})
            project={"id":"msc-example","title":"Study","repository":"MatPomGit/msc-example",
                     "url":"https://github.com/MatPomGit/msc-example","role":"primary",
                     "primary_program":"arc-neuro","line":"ndd","status":"active",
                     "visibility":"public","public_listing":False,"default_branch":"main",
                     "snapshot_sha":None,"pages_url":None,"submodule_path":None}
            self.write(root,"portfolio/projects.json",{"schema_version":2,"projects":[project]})
            st=root/"PROJECT_STATE.yaml"
            st.write_text(st.read_text().replace("projects_registered: 0","projects_registered: 1"))
            self.assertEqual([],validate(root))

    def test_unregistered_external_owner_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            self.write(root,"portfolio/papers.json",{"schema_version":2,"papers":[paper("external")]})
            self.assertTrue(any("Unknown canonical project" in e for e in validate(root)))

    def test_duplicate_id_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            self.write(root,"portfolio/papers.json",{"schema_version":2,"papers":[paper(),paper()]})
            st=root/"PROJECT_STATE.yaml"
            st.write_text(st.read_text().replace("papers_registered: 1","papers_registered: 2"))
            self.assertTrue(any("duplicate MSC" in e for e in validate(root)))

    def test_missing_local_source_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            (root/"manuscripts/MSC-CR-P05/main.tex").unlink()
            self.assertTrue(any("file missing" in e for e in validate(root)))

    def test_paper_dependency_allowed_and_ambiguous_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            dep={"schema_version":2,"tools":[{"paper_id":"MSC-CR-P05","ref":"lib-test"}],
                 "equipment":[],"datasets":[]}
            self.write(root,"portfolio/dependencies.json",dep)
            self.assertEqual([],validate(root))
            dep["tools"][0]["project_id"]="msc-example"
            self.write(root,"portfolio/dependencies.json",dep)
            self.assertTrue(any("exactly one owner" in e for e in validate(root)))

    def test_publication_requires_evidence_and_doi(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            p=paper()
            p["publication_stage"]="published"
            self.write(root,"portfolio/papers.json",{"schema_version":2,"papers":[p]})
            issues=validate(root)
            self.assertTrue(any("status evidence" in e for e in issues),issues)
            self.assertTrue(any("lacks DOI" in e for e in issues),issues)

    def test_wrong_schema_version_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            self.write(root,"portfolio/papers.json",{"schema_version":1,"papers":[paper()]})
            self.assertTrue(any("requires schema_version 2" in e for e in validate(root)))

    def test_noncanonical_owner_and_bad_path_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            p=paper()
            p["owner"]["repository"]="Other/arc-neuro"
            p["manuscript"]["path"]="../outside.tex"
            self.write(root,"portfolio/papers.json",{"schema_version":2,"papers":[p]})
            self.assertTrue(any("Invalid manuscript" in e for e in validate(root)))

    def test_json_schemas_parse(self):
        for name in ("program","papers","projects","dependencies"):
            cfg=json.loads((ROOT/"schemas"/(name+".v2.schema.json")).read_text())
            self.assertEqual(cfg["properties"]["schema_version"]["const"],2)

if __name__=="__main__": unittest.main()
