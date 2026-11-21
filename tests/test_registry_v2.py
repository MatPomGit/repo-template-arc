"""ARC v2: local and external ownership, provenance and negative cases."""
from __future__ import annotations
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from validate_repository import validate
from validate_registry_v2 import PAPER_FIELDS, DEP_FIELDS

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

    def test_legacy_papers_area_layout_is_supported(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            meta=json.loads((root/"program.json").read_text())
            meta["manuscript_root"]="papers"
            self.write(root,"program.json",meta)
            old=root/"manuscripts/MSC-CR-P05/main.tex"
            new=root/"papers/ndd/MSC-CR-P05/main.tex"
            new.parent.mkdir(parents=True)
            old.rename(new)
            content={"schema_version":2,"papers":[paper()]}
            content["papers"][0]["manuscript"]["path"]="papers/ndd/MSC-CR-P05/main.tex"
            self.write(root,"portfolio/papers.json",content)
            self.assertEqual([],validate(root))

    def test_wrong_id_in_local_folder_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            alt=root/"manuscripts/MSC-OTHER-P01/main.tex"
            alt.parent.mkdir(parents=True)
            alt.write_text("draft")
            obj=paper()
            obj["manuscript"]["path"]="manuscripts/MSC-OTHER-P01/main.tex"
            self.write(root,"portfolio/papers.json",{"schema_version":2,"papers":[obj]})
            self.assertTrue(any("path is not standard" in e for e in validate(root)))

    def test_local_repository_owner_must_match_full_name(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            obj=paper()
            obj["owner"]["repository"]="Other/arc-neuro"
            self.write(root,"portfolio/papers.json",{"schema_version":2,"papers":[obj]})
            self.assertTrue(any("Local owner must match" in e for e in validate(root)))

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

    def test_private_external_related_reference_can_be_redacted(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            p=paper("external")
            p["relation"]="related"
            p["owner"]={"mode":"external","repository":None,"project_id":None,
                        "redacted":True}
            p["manuscript"]=None
            self.write(root,"portfolio/papers.json",{"schema_version":2,"papers":[p]})
            self.assertEqual([],validate(root))
            schema=json.loads((root/"schemas/papers.v2.schema.json").read_text())
            self.assertEqual([],list(Draft202012Validator(schema).iter_errors(
                {"schema_version":2,"papers":[p]})))

    def test_redacted_external_reference_cannot_publish_or_claim_local_source(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            schema=json.loads((root/"schemas/papers.v2.schema.json").read_text())
            p=paper("external")
            p["relation"]="related"
            p["owner"]={"mode":"external","repository":None,"project_id":None,
                        "redacted":True}
            p["manuscript"]=None
            for field,value in (("public_listing",True),
                                ("relation","primary"),
                                ("manuscript",{"path":"manuscripts/MSC-CR-P05/main.tex",
                                               "format":"latex"})):
                with self.subTest(field=field):
                    test=dict(p)
                    test[field]=value
                    self.write(root,"portfolio/papers.json",{"schema_version":2,"papers":[test]})
                    self.assertTrue(any("redacted external" in x for x in validate(root)))
                    self.assertTrue(list(Draft202012Validator(schema).iter_errors(
                        {"schema_version":2,"papers":[test]})))

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

    def test_legacy_v1_scaffold_without_v2_schema_files(self):
        """Legacy programme config and registries remain auditable pre-migration."""
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            for schema in ("program", "projects", "papers", "dependencies"):
                (root/"schemas"/(schema+".v2.schema.json")).unlink()
            meta=json.loads((root/"program.json").read_text())
            meta["schema_version"]=1
            meta["template_version"]="1.0.0"
            meta.pop("repository_full_name")
            meta.pop("manuscript_root")
            self.write(root,"program.json",meta)
            for path in ("portfolio/projects.json","portfolio/papers.json","portfolio/dependencies.json"):
                obj=json.loads((root/path).read_text())
                obj["schema_version"]=1
                if path.endswith("papers.json"):
                    obj["papers"]=[]
                self.write(root,path,obj)
            state=root/"PROJECT_STATE.yaml"
            state.write_text(state.read_text().replace("schema_version: 2","schema_version: 1")
                             .replace("template_version: 0.1.0","template_version: 1.0.0")
                             .replace("papers_registered: 1","papers_registered: 0")
                             .replace("phase: active","phase: planned"))
            self.assertEqual([],validate(root))

    def test_local_manuscript_rejects_wrong_area_and_extra_segments(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            source=root/"manuscripts/MSC-CR-P05/main.tex"
            for root_dir,path in (
                ("papers","papers/cognition/MSC-CR-P05/main.tex"),
                ("manuscripts","manuscripts/unexpected/MSC-CR-P05/main.tex"),
                ("papers","papers/ndd/extra/MSC-CR-P05/main.tex"),
            ):
                with self.subTest(path=path):
                    target=root/path
                    target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_bytes(source.read_bytes())
                    meta=json.loads((root/"program.json").read_text())
                    meta["manuscript_root"]=root_dir
                    self.write(root,"program.json",meta)
                    record=paper()
                    record["manuscript"]["path"]=path
                    self.write(root,"portfolio/papers.json",
                               {"schema_version":2,"papers":[record]})
                    self.assertTrue(any("path is not standard" in e for e in validate(root)))

    def test_repository_identity_compares_with_trusted_input(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            self.assertEqual([],validate(root,verified_repository="MatPomGit/arc-neuro"))
            result=validate(root,verified_repository="Other/arc-neuro")
            self.assertTrue(any("differs from verified GitHub" in e for e in result),result)

    def test_dependency_json_schema_matches_python_xor_semantics(self):
        schema=json.loads((ROOT/"schemas/dependencies.v2.schema.json").read_text())
        checker=Draft202012Validator(schema)
        variants=(
            ({"paper_id":"MSC-CR-P05","ref":"lib-test"},True),
            ({"paper_id":None,"ref":"lib-test"},False),
            ({"paper_id":"","ref":"lib-test"},False),
            ({"paper_id":"   ","ref":"lib-test"},False),
            ({"paper_id":"MSC-CR-P05","project_id":None,"ref":"lib-test"},False),
            ({"paper_id":"MSC-CR-P05","project_id":"msc-example","ref":"lib-test"},False),
            ({"ref":"lib-test"},False),
        )
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            for group in ("tools","equipment","datasets"):
                for row,expected in variants:
                    with self.subTest(group=group,row=row):
                        data={"schema_version":2,"tools":[],"equipment":[],"datasets":[]}
                        data[group]=[row]
                        self.write(root,"portfolio/dependencies.json",data)
                        self.assertEqual(expected,checker.is_valid(data),row)
                        self.assertEqual(expected,not validate(root),row)

    def test_local_manuscript_git_provenance(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            def git(*args):
                result=subprocess.run(["git","-C",str(root),*args],
                                      capture_output=True,text=True,check=True)
                return result.stdout.strip()
            git("init","-q")
            git("add",".")
            git("-c","user.name=ARC Test","-c","user.email=arc-test@example.invalid",
                "commit","-q","-m","test manuscript")
            commit=git("rev-parse","HEAD")
            blob=git("rev-parse",f"{commit}:manuscripts/MSC-CR-P05/main.tex")
            record=paper()
            record["manuscript"].update(commit_sha=commit,blob_sha=blob)
            self.write(root,"portfolio/papers.json",
                       {"schema_version":2,"papers":[record]})
            self.assertEqual([],validate(root))
            record["manuscript"]["blob_sha"]="0"*40
            self.write(root,"portfolio/papers.json",
                       {"schema_version":2,"papers":[record]})
            self.assertTrue(any("disagrees with pinned commit" in e
                                for e in validate(root)))
            record["manuscript"].update(commit_sha="0"*40,blob_sha=blob)
            self.write(root,"portfolio/papers.json",
                       {"schema_version":2,"papers":[record]})
            self.assertTrue(any("UNAVAILABLE local manuscript" in e
                                for e in validate(root)))

    def test_local_blob_only_checks_current_contents(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            record=paper()
            record["manuscript"]["blob_sha"]="0"*40
            self.write(root,"portfolio/papers.json",
                       {"schema_version":2,"papers":[record]})
            self.assertTrue(any("disagrees with current file" in e
                                for e in validate(root)))

    def test_json_schemas_parse(self):
        for name in ("program","papers","projects","dependencies"):
            cfg=json.loads((ROOT/"schemas"/(name+".v2.schema.json")).read_text())
            self.assertEqual(cfg["properties"]["schema_version"]["const"],2)
            Draft202012Validator.check_schema(cfg)
        paper_cfg=json.loads((ROOT/"schemas/papers.v2.schema.json").read_text())
        fields=set(paper_cfg["properties"]["papers"]["items"]["properties"])
        self.assertEqual(fields,PAPER_FIELDS)
        dependencies=json.loads((ROOT/"schemas/dependencies.v2.schema.json").read_text())
        dep_fields=set(dependencies["properties"]["tools"]["items"]["properties"])
        self.assertEqual(dep_fields,DEP_FIELDS)
        program=json.loads((ROOT/"program.json").read_text())
        cfg=json.loads((ROOT/"schemas/program.v2.schema.json").read_text())
        self.assertEqual(set(program),set(cfg["required"]))

if __name__=="__main__": unittest.main()
