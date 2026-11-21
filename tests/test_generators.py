"""Offline E2E tests for ARC initialization, manuscript generation and study plans."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"scripts"))
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

    def test_tex_special_characters_are_escaped(self):
        self.assertEqual(tex_escape("C#_% &"),r"C\#\_\% \&")

if __name__=="__main__":
    unittest.main()
