"""Offline E2E tests for ARC initialization, manuscript generation and study plans."""
from __future__ import annotations

import json
import shutil
from unittest.mock import patch
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"scripts"))
import _generator_io
from _generator_io import write_batch
from init_arc import initialize
from new_manuscript import create, tex_escape
from validate_repository import validate
from validate_study import validate_study


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)/"arc"
        shutil.copytree(ROOT,self.root,ignore=shutil.ignore_patterns(".git","site","__pycache__"))

    def tearDown(self):
        self.tmp.cleanup()

    def init(self, apply=True):
        return initialize(self.root,programme="arc-neuro",repository="MatPomGit/arc-neuro",
                          title="ARC Neuro",owner="Research Author",scope="Study of cognition",
                          visibility="public",areas=["ndd"],apply=apply)

    def new(self, **kwargs):
        args={"ident":"MSC-ADHD-P01","title":"Interakcje i poznanie","area":"ndd",
              "study_type":"empirical","apply":True}
        args.update(kwargs)
        return create(self.root,**args)

    def test_init_dry_run_is_read_only(self):
        before=(self.root/"program.json").read_bytes()
        paths=self.init(apply=False)
        self.assertTrue(paths)
        self.assertEqual(before,(self.root/"program.json").read_bytes())

    def test_initialized_program_contract_passes(self):
        self.init()
        self.assertEqual([],validate(self.root))

    def test_initialized_readme_is_reader_facing(self):
        self.init()
        readme = (self.root / "README.md").read_text(encoding="utf-8")
        self.assertIn("# ARC Neuro", readme)
        self.assertIn("Study of cognition", readme)
        self.assertNotIn("stanowi szablon", readme)
        self.assertNotIn("REPLACE", readme)

    def test_cannot_reinitialize_an_arc(self):
        self.init()
        with self.assertRaisesRegex(ValueError,"re-initialize"):
            self.init()

    def test_created_local_manuscript_and_study_pass_contracts(self):
        self.init()
        self.new()
        self.assertEqual([],validate(self.root))
        path="manuscripts/MSC-ADHD-P01/study.yaml"
        self.assertEqual([],validate_study(self.root,path,"MSC-ADHD-P01"))
        papers=json.loads((self.root/"portfolio/papers.json").read_text())["papers"]
        self.assertEqual(len(papers),1)
        self.assertEqual(papers[0]["owner"]["project_id"],None)
        self.assertEqual(papers[0]["owner"]["mode"],"local")
        self.assertEqual(papers[0]["publication_stage"],"concept")

    def test_manuscript_dry_run_and_idempotence(self):
        self.init()
        preview=self.new(apply=False)
        self.assertTrue(preview)
        self.assertFalse((self.root/"manuscripts").exists())
        self.new()
        old=(self.root/"portfolio/papers.json").read_bytes()
        self.assertEqual([],self.new())
        self.assertEqual(old,(self.root/"portfolio/papers.json").read_bytes())

    def test_conflict_and_unregistered_area_fail_without_mutation(self):
        self.init()
        self.new()
        old=(self.root/"portfolio/papers.json").read_bytes()
        with self.assertRaisesRegex(ValueError,"already in use"):
            self.new(title="Inny tytuł")
        with self.assertRaisesRegex(ValueError,"Unregistered"):
            self.new(ident="MSC-ADHD-P02",area="unknown")
        self.assertEqual(old,(self.root/"portfolio/papers.json").read_bytes())

    def test_manuscript_path_and_invalid_metadata(self):
        self.init()
        with self.assertRaises(ValueError):
            self.new(ident="bad-name")
        with self.assertRaises(ValueError):
            self.new(title="Invalid\nTitle")
        self.assertFalse((self.root/"manuscripts").exists())

    def test_study_paper_id_mismatch_and_frozen_protocol(self):
        self.init()
        self.new()
        path=self.root/"manuscripts/MSC-ADHD-P01/study.yaml"
        txt=path.read_text()
        path.write_text(txt.replace("MSC-ADHD-P01","MSC-OTHER-P01"))
        self.assertTrue(any("STUDY_WRONG_ID" in x for x in validate_study(
            self.root,"manuscripts/MSC-ADHD-P01/study.yaml","MSC-ADHD-P01")))
        path.write_text(txt.replace("protocol_frozen: false","protocol_frozen: true"))
        self.assertTrue(any("STUDY_FROZEN_MISSING_QUESTION" in x for x in validate_study(
            self.root,"manuscripts/MSC-ADHD-P01/study.yaml","MSC-ADHD-P01")))
        self.assertTrue(any("STUDY_FROZEN_MISSING_QUESTION" in x for x in validate(self.root)))

    def test_legacy_papers_layout(self):
        self.init()
        p=self.root/"program.json"
        meta=json.loads(p.read_text())
        meta["manuscript_root"]="papers"
        p.write_text(json.dumps(meta))
        self.new()
        self.assertTrue((self.root/"papers/ndd/MSC-ADHD-P01/main.tex").is_file())
        self.assertEqual([],validate(self.root))

    def test_authorship_is_not_inferred_from_programme_owner(self):
        self.init()
        self.new()
        source=(self.root/"manuscripts/MSC-ADHD-P01/main.tex").read_text()
        self.assertIn(r"\author{}",source)
        self.assertNotIn(r"\author{Research Author}",source)

    def test_invalid_paper_register_is_blocked_before_write(self):
        self.init()
        register=self.root/"portfolio/papers.json"
        register.write_text(json.dumps({"schema_version":2,"papers":["invalid-record"]}))
        with self.assertRaisesRegex(ValueError,"Invalid paper records"):
            self.new()
        self.assertFalse((self.root/"manuscripts").exists())

    def test_study_validator_rejects_parent_symlink(self):
        self.init()
        self.new()
        folder=self.root/"manuscripts/MSC-ADHD-P01"
        outside=Path(self.tmp.name)/"outside"
        folder.rename(outside)
        folder.symlink_to(outside, target_is_directory=True)
        rel="manuscripts/MSC-ADHD-P01/study.yaml"
        self.assertTrue(any("STUDY_INVALID_PATH" in e
                            for e in validate_study(self.root,rel,"MSC-ADHD-P01")))
        errors=validate(self.root)
        self.assertTrue(any("STUDY_INVALID_PATH" in e for e in errors),errors)

    def test_study_validator_rejects_schema_symlink(self):
        self.init()
        self.new()
        schema=self.root/"schemas/study.v1.schema.json"
        outside=Path(self.tmp.name)/"schema.json"
        schema.rename(outside)
        schema.symlink_to(outside)
        errors=validate_study(self.root,"manuscripts/MSC-ADHD-P01/study.yaml","MSC-ADHD-P01")
        self.assertTrue(any("STUDY_INVALID_PATH" in e for e in errors),errors)

    def test_existing_manuscript_rejects_mutated_owner_and_null_manuscript(self):
        for mutation in ("owner", "null_manuscript", "area"):
            with self.subTest(mutation=mutation):
                self.init() if not (self.root/"manuscripts").exists() else None
                if not (self.root/"manuscripts/MSC-ADHD-P01").exists():
                    self.new()
                reg=self.root/"portfolio/papers.json"
                data=json.loads(reg.read_text())
                row=data["papers"][0]
                if mutation=="owner":
                    row["owner"]["mode"]="external"
                elif mutation=="null_manuscript":
                    row["manuscript"]=None
                else:
                    row["area"]="different"
                reg.write_text(json.dumps(data))
                with self.assertRaisesRegex(ValueError,"already in use"):
                    self.new()
                # Restore the baseline for the next mutation.
                data["papers"][0]["owner"]={"mode":"local","repository":"MatPomGit/arc-neuro","project_id":None}
                data["papers"][0]["manuscript"]={"path":"manuscripts/MSC-ADHD-P01/main.tex","format":"latex"}
                data["papers"][0]["area"]="ndd"
                reg.write_text(json.dumps(data))

    def test_existing_manuscript_rejects_study_and_state_corruption(self):
        self.init()
        self.new()
        path=self.root/"manuscripts/MSC-ADHD-P01/study.yaml"
        original=path.read_text()
        path.write_text(original.replace("study_type: \"empirical\"","study_type: \"simulation\""))
        with self.assertRaisesRegex(ValueError,"already in use"):
            self.new()
        path.write_text(original.replace("paper_id: \"MSC-ADHD-P01\"","paper_id: \"MSC-OTHER-P01\""))
        with self.assertRaisesRegex(ValueError,"already in use"):
            self.new()
        path.write_text(original)
        state=self.root/"PROJECT_STATE.yaml"
        state.write_text(state.read_text().replace("papers_registered: 1","papers_registered: 2"))
        with self.assertRaisesRegex(ValueError,"already in use"):
            self.new()

    def test_existing_valid_edited_manuscript_remains_idempotent(self):
        self.init()
        self.new()
        source=self.root/"manuscripts/MSC-ADHD-P01/main.tex"
        source.write_text(source.read_text()+"\n% Research notes\n")
        self.assertEqual([],self.new())

    def test_init_rejects_owner_unsafe_in_state(self):
        for owner in ("*Example", "null", " Researcher", "!tag", "{x}"):
            with self.subTest(owner=owner):
                with self.assertRaisesRegex(ValueError,"Owner cannot"):
                    initialize(self.root,programme="arc-neuro",repository="MatPomGit/arc-neuro",
                               title="Program",owner=owner,scope="Study",visibility="public",
                               areas=["ndd"],apply=True)
                self.assertEqual("arc-REPLACE",json.loads(
                    (self.root/"program.json").read_text())["programme"])

    def test_batch_rollback_on_second_or_third_replace(self):
        self.init()
        for fail_at in (2,3):
            with self.subTest(fail_at=fail_at):
                files=[self.root/"program.json",self.root/"PROJECT_STATE.yaml",
                       self.root/"manuscripts/new/file.tex"]
                original={p:p.read_bytes() for p in files[:2]}
                updates={files[0]:"replacement-one",files[1]:"replacement-two",
                         files[2]:"new manuscript"}
                original_replace=os.replace
                count=[0]
                def inject_once(src,dst):
                    count[0]+=1
                    if count[0]==fail_at:
                        raise OSError("injected replace failure")
                    return original_replace(src,dst)
                with patch.object(_generator_io.os,"replace",side_effect=inject_once):
                    with self.assertRaisesRegex(OSError,"injected replace failure"):
                        write_batch(self.root,updates,new={files[2]})
                for path,expected in original.items():
                    self.assertEqual(expected,path.read_bytes())
                self.assertFalse(files[2].exists())
                self.assertFalse((self.root/"manuscripts/new").exists())
                self.assertFalse(list(self.root.rglob(".arc-stage-*")))
                self.assertFalse(list(self.root.rglob(".arc-restore-*")))

    def test_init_quotes_yaml_ambiguous_owner(self):
        import yaml
        for owner in ("true", "- Alice", "0123", 'Alice "Lab"'):
            with self.subTest(owner=owner), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "arc"
                shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(
                    ".git", "site", "__pycache__"))
                initialize(root, programme="arc-neuro",
                           repository="MatPomGit/arc-neuro", title="ARC Neuro",
                           owner=owner, scope="Study of cognition",
                           visibility="public", areas=["ndd"], apply=True)
                state = yaml.safe_load((root / "PROJECT_STATE.yaml").read_text())
                self.assertIsInstance(state["scientific_owner"], str)
                self.assertEqual(owner, state["scientific_owner"])
                self.assertEqual([], validate(root))

    def test_tex_special_characters_are_escaped(self):
        self.assertEqual(tex_escape("C#_% &"),r"C\#\_\% \&")

if __name__=="__main__":
    unittest.main()
