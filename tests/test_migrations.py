"""E2E migration checks: no invented research, no silent loss or early writes."""
from __future__ import annotations
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from migrate_arc import execute
from validate_repository import validate


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)/"arc"
        shutil.copytree(ROOT,self.root,ignore=shutil.ignore_patterns(".git","site","__pycache__"))
        self.prepare_v1()

    def tearDown(self):
        self.temp.cleanup()

    def save(self,path,obj):
        (self.root/path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n")

    def prepare_v1(self):
        meta=json.loads((self.root/"program.json").read_text())
        meta["schema_version"]=1
        meta["template_version"]="1.0.0"
        meta["programme"]="arc-neuro"
        meta["repository_visibility"]="public"
        meta.pop("repository_full_name",None)
        meta.pop("manuscript_root",None)
        self.save("program.json",meta)
        self.save("areas/index.json",{"schema_version":1,"lines":[{"id":"ndd","title":"NDD"}]})
        for name,arr in (("projects",[]),("papers",[])):
            self.save("portfolio/"+name+".json",{"schema_version":1,name:arr})
        self.save("portfolio/dependencies.json",{"schema_version":1,"tools":[],"equipment":[],"datasets":[]})
        state=self.root/"PROJECT_STATE.yaml"
        body=state.read_text()
        body=body.replace("schema_version: 2","schema_version: 1")
        body=body.replace("template_version: 0.1.0","template_version: 1.0.0")
        body=body.replace("programme: arc-REPLACE","programme: arc-neuro")
        state.write_text(body)
        self.assertEqual([],validate(self.root),"Legacy v1 should remain valid")

    def git_init(self):
        subprocess.run(["git","init","-q",str(self.root)],check=True,capture_output=True)
        subprocess.run(["git","-C",str(self.root),"add","-A"],check=True,capture_output=True)
        subprocess.run(["git","-C",str(self.root),"-c","user.name=ARC Test",
                        "-c","user.email=arc-test@example.org","commit","-qm","baseline"],
                       check=True,capture_output=True)
        return subprocess.check_output(["git","-C",str(self.root),"rev-parse","HEAD"],
                                       text=True).strip()

    def local(self):
        path=self.root/"manuscripts/MSC-CR-P05/main.tex"
        path.parent.mkdir(parents=True)
        path.write_text("\\documentclass{article}\\begin{document}Plan\\end{document}\n")
        return "manuscripts/MSC-CR-P05/main.tex"

    def test_v1_empty_migrates_with_exact_git_sha(self):
        sha=self.git_init()
        before=(self.root/"program.json").read_bytes()
        plan=execute(self.root,"plan",repository="MatPomGit/arc-neuro")
        self.assertEqual(plan["status"],"READY")
        self.assertEqual(before,(self.root/"program.json").read_bytes())
        result=execute(self.root,"apply",repository="MatPomGit/arc-neuro",
                       expected_sha=sha)
        self.assertEqual(result["status"],"APPLIED")
        migrated=json.loads((self.root/"program.json").read_text())
        self.assertEqual(migrated["schema_version"],2)
        self.assertEqual(migrated["template_version"],"1.0.0")
        self.assertIn("template_version: 1.0.0", (self.root/"PROJECT_STATE.yaml").read_text())
        self.assertEqual([],validate(self.root))
        self.assertEqual(execute(self.root,"plan")["status"],"ALREADY_V2")

    def test_unregistered_local_source_requires_explicit_mapping(self):
        file=self.local()
        result=execute(self.root,"plan",repository="MatPomGit/arc-neuro")
        self.assertEqual(result["status"],"BLOCKED")
        self.assertTrue(any("Unmapped local source" in s for s in result["blockers"]))
        mapping={"schema_version":1,"sources":{file:{"mode":"local",
            "title":"Verified cognition protocol","area":"ndd"}}}
        plan=execute(self.root,"plan",repository="MatPomGit/arc-neuro",mapping=mapping)
        self.assertEqual(plan["status"],"READY")
        self.assertEqual(plan["article_count"],1)
        sha=self.git_init()
        with self.assertRaisesRegex(ValueError,"Public local sources"):
            execute(self.root,"apply",repository="MatPomGit/arc-neuro",
                    mapping=mapping,expected_sha=sha)
        result=execute(self.root,"apply",repository="MatPomGit/arc-neuro",
                       mapping=mapping,expected_sha=sha,confirm_public_sources=True)
        self.assertEqual(result["status"],"APPLIED")
        self.assertEqual([],validate(self.root))
        self.assertEqual((self.root/file).read_text(),
                         "\\documentclass{article}\\begin{document}Plan\\end{document}\n")

    def test_invalid_mapping_does_not_modify_source(self):
        self.local()
        before=(self.root/"program.json").read_bytes()
        mapdata={"schema_version":1,"sources":{
            "manuscripts/MSC-CR-P05/main.tex":{"mode":"local","title":"Article","area":"invalid"}}}
        result=execute(self.root,"plan",repository="MatPomGit/arc-neuro",mapping=mapdata)
        self.assertEqual(result["status"],"BLOCKED")
        self.assertEqual(before,(self.root/"program.json").read_bytes())

    def test_prevents_wrong_sha_or_dirty_git(self):
        sha=self.git_init()
        with self.assertRaisesRegex(ValueError,"mismatch"):
            execute(self.root,"apply",repository="MatPomGit/arc-neuro",
                    expected_sha="a"*40)
        body=self.root/"RESEARCH.md"
        body.write_text(body.read_text()+"\nExtra\n")
        with self.assertRaisesRegex(ValueError,"tracked working tree modified"):
            execute(self.root,"apply",repository="MatPomGit/arc-neuro",
                    expected_sha=sha)

    def test_external_v1_article_keeps_source_and_stage(self):
        project={"id":"msc-example","title":"Public project","repository":"MatPomGit/msc-example",
                 "url":"https://github.com/MatPomGit/msc-example","role":"primary",
                 "primary_program":"arc-neuro","line":"ndd","status":"active",
                 "visibility":"public","public_listing":False,"default_branch":"main",
                 "snapshot_sha":None,"pages_url":None,"submodule_path":None}
        self.save("portfolio/projects.json",{"schema_version":1,"projects":[project]})
        paper={"id":"MSC-CR-P05","title":"Public hypothesis","owner_project_id":"msc-example",
               "canonical_repository":"MatPomGit/msc-example","manuscript_path":"manuscripts/P05",
               "stage":"concept","doi":None,"preprint_url":None,"preregistration_url":None,
               "publication_url":None,"stage_evidence":None}
        self.save("portfolio/papers.json",{"schema_version":1,"papers":[paper]})
        s=self.root/"PROJECT_STATE.yaml"
        s.write_text(s.read_text().replace("projects_registered: 0","projects_registered: 1")
                     .replace("papers_registered: 0","papers_registered: 1")
                     .replace("phase: scaffold","phase: active"))
        sha=self.git_init()
        report=execute(self.root,"apply",repository="MatPomGit/arc-neuro",expected_sha=sha)
        self.assertEqual(report["status"],"APPLIED")
        item=json.loads((self.root/"portfolio/papers.json").read_text())["papers"][0]
        self.assertEqual(item["owner"]["repository"],"MatPomGit/msc-example")
        self.assertEqual(item["publication_stage"],"concept")
        self.assertEqual(item["manuscript"]["path"],"manuscripts/P05")
        self.assertIsNone(item["public_summary"])
        self.assertEqual([],validate(self.root))

    def test_unverified_legacy_stage_not_promoted(self):
        p={"id":"MSC-CR-P05","title":"Study","owner_project_id":"msc-example",
           "canonical_repository":"MatPomGit/msc-example","manuscript_path":"manuscripts/P05",
           "stage":"draft","doi":None,"preprint_url":None,"preregistration_url":None,
           "publication_url":None,"stage_evidence":None}
        project={"id":"msc-example","title":"Study","repository":"MatPomGit/msc-example",
                 "url":"https://github.com/MatPomGit/msc-example","role":"primary",
                 "primary_program":"arc-neuro","line":"ndd","status":"active",
                 "visibility":"public","public_listing":False,"default_branch":"main",
                 "snapshot_sha":None,"pages_url":None,"submodule_path":None}
        self.save("portfolio/projects.json",{"schema_version":1,"projects":[project]})
        self.save("portfolio/papers.json",{"schema_version":1,"papers":[p]})
        st=self.root/"PROJECT_STATE.yaml"
        st.write_text(st.read_text().replace("projects_registered: 0","projects_registered: 1")
                      .replace("papers_registered: 0","papers_registered: 1")
                      .replace("phase: scaffold","phase: active"))
        result=execute(self.root,"plan",repository="MatPomGit/arc-neuro")
        self.assertEqual(result["status"],"BLOCKED")
        self.assertTrue(any("Research state needs explicit mapping" in e
                            for e in result["blockers"]))

    def test_rolls_back_when_postvalidation_fails(self):
        # Existing source lacking a required page still causes post-migration failure.
        (self.root/"pages/index.md").unlink()
        sha=self.git_init()
        before=(self.root/"program.json").read_text()
        with self.assertRaisesRegex(ValueError,"Post-migration validation failed"):
            execute(self.root,"apply",repository="MatPomGit/arc-neuro",expected_sha=sha)
        self.assertEqual(before,(self.root/"program.json").read_text())
        self.assertEqual(json.loads(before)["schema_version"],1)

    def test_inventory_and_incomplete_v2_cannot_claim_success(self):
        info=execute(self.root,"inventory")
        self.assertEqual(info["status"],"INVENTORY")
        self.assertEqual(info["registered_papers"],0)
        meta=json.loads((self.root/"program.json").read_text())
        meta["schema_version"]=2
        self.save("program.json",meta)
        for mode in ("plan","apply"):
            with self.subTest(mode=mode):
                before=(self.root/"program.json").read_bytes()
                result=execute(self.root,mode,repository="MatPomGit/arc-neuro")
                self.assertEqual(result["status"],"BLOCKED")
                self.assertTrue(result["blockers"])
                self.assertEqual(before,(self.root/"program.json").read_bytes())

    def test_already_v2_requires_valid_full_repository(self):
        sha=self.git_init()
        result=execute(self.root,"apply",repository="MatPomGit/arc-neuro",
                       expected_sha=sha)
        self.assertEqual(result["status"],"APPLIED")
        self.assertEqual(execute(self.root,"plan")["status"],"ALREADY_V2")
        bad=self.root/"portfolio/papers.json"
        bad.write_text('{"schema_version":2,"papers":[{"id":"MSC-TEST-P01"}]}')
        self.assertEqual(execute(self.root,"plan")["status"],"BLOCKED")
        self.assertEqual(execute(self.root,"apply")["status"],"BLOCKED")


    def test_apply_rejects_untracked_local_manuscript_source(self):
        sha = self.git_init()
        source = self.local()  # Created after commit; tracked Git files remain clean.
        mapping = {"schema_version": 1, "sources": {
            source: {"mode": "local", "title": "Verified prospective study",
                     "area": "ndd"}}}
        self.assertEqual("READY", execute(
            self.root, "plan", repository="MatPomGit/arc-neuro",
            mapping=mapping)["status"])
        before = (self.root / "program.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "Uncommitted manuscript source"):
            execute(self.root, "apply", repository="MatPomGit/arc-neuro",
                    mapping=mapping, expected_sha=sha, confirm_public_sources=True)
        self.assertEqual(before, (self.root / "program.json").read_bytes())


if __name__=="__main__":
    unittest.main()
