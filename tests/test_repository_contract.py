"""Offline tests for ARC template structure, privacy and data ownership."""
from __future__ import annotations
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from validate_repository import validate, github_repo_url, safe_public_page_url
from build_public_catalog import render, write_catalog
from check_freshness import inspect_project


def candidate():
    return {
        "id":"msc-example", "title":"Private project", "repository":"MatPomGit/msc-example",
        "url":"https://github.com/MatPomGit/msc-example", "role":"primary",
        "primary_program":"arc-neuro", "line":"ndd", "status":"active",
        "visibility":"private", "public_listing":False, "default_branch":"main",
        "snapshot_sha":"a"*40, "pages_url":None, "submodule_path":None
    }

class ARCContractTests(unittest.TestCase):
    def test_scaffold_passes(self):
        self.assertEqual(validate(ROOT,"scaffold"),[])

    def test_unconfigured_publish_is_blocked(self):
        issues=validate(ROOT,"publish")
        self.assertTrue(issues)
        self.assertTrue(any("Programme" in x or "program" in x for x in issues))

    def test_github_url_forbids_token_and_untrusted_host(self):
        self.assertTrue(github_repo_url("MatPomGit/example","https://github.com/MatPomGit/example"))
        self.assertFalse(github_repo_url("MatPomGit/example","https://token@github.com/MatPomGit/example"))
        self.assertFalse(github_repo_url("MatPomGit/example","https://example.org/MatPomGit/example"))

    def test_private_project_never_in_public_pages(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"portfolio").mkdir()
            (root/"portfolio/projects.json").write_text(json.dumps({"schema_version":2,"projects":[{
                **candidate(),"public_listing":True,"pages_url":"https://internal.example/private"
            }]}),encoding="utf-8")
            result=render(root)
            self.assertNotIn("Private project",result)
            self.assertNotIn("internal.example",result)

    def test_public_catalog_is_written_only_to_pages(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for folder in ("portfolio", "pages", "docs", "config"):
                (root/folder).mkdir()
            (root/"portfolio/projects.json").write_text(
                json.dumps({"schema_version":2,"projects":[]}), encoding="utf-8")
            (root/"config/pages-policy.json").write_text(
                json.dumps({"public_files":["index.md","projects.md"]}), encoding="utf-8")
            output=write_catalog(root)
            self.assertEqual(output, root/"pages/projects.md")
            self.assertFalse((root/"docs/projects.md").exists())
            self.assertEqual(output.read_text(encoding="utf-8"), render(root))

    def test_public_catalog_is_blocked_without_allowlist(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for folder in ("portfolio", "pages", "config"):
                (root/folder).mkdir()
            (root/"portfolio/projects.json").write_text(
                json.dumps({"schema_version":2,"projects":[]}), encoding="utf-8")
            (root/"config/pages-policy.json").write_text(
                json.dumps({"public_files":["index.md"]}), encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "not allowlisted"):
                write_catalog(root)

    def test_duplicate_project_ids_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            # Clone only required lightweight fixture files to the temporary root.
            import shutil
            dst=Path(d)
            for f in ROOT.rglob("*"):
                if f.is_file() and "__pycache__" not in f.parts:
                    dest=dst/f.relative_to(ROOT)
                    dest.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copyfile(f,dest)
            meta=json.loads((dst/"program.json").read_text(encoding="utf-8"))
            meta["programme"]="arc-neuro"
            (dst/"program.json").write_text(json.dumps(meta),encoding="utf-8")
            (dst/"areas/index.json").write_text(json.dumps({"lines":[{"id":"ndd","title":"NDD"}]}),encoding="utf-8")
            (dst/"portfolio/projects.json").write_text(json.dumps({"schema_version":2,"projects":[candidate(),candidate()]}),encoding="utf-8")
            self.assertTrue(any("duplicate project" in x.lower() for x in validate(dst,"scaffold")))

    def test_public_arc_rejects_private_metadata_even_if_hidden_from_pages(self):
        import shutil
        with tempfile.TemporaryDirectory() as d:
            dst = Path(d)
            shutil.copytree(ROOT, dst / "repo", ignore=shutil.ignore_patterns("__pycache__"))
            dst = dst / "repo"
            meta = json.loads((dst / "program.json").read_text(encoding="utf-8"))
            meta["repository_visibility"] = "public"
            meta["programme"] = "arc-neuro"
            (dst / "program.json").write_text(json.dumps(meta), encoding="utf-8")
            (dst / "areas/index.json").write_text(
                json.dumps({"lines": [{"id": "ndd", "title": "NDD"}]}), encoding="utf-8")
            (dst / "portfolio/projects.json").write_text(
                json.dumps({"schema_version":2,"projects": [candidate()]}), encoding="utf-8")
            issues = validate(dst, "scaffold")
            self.assertTrue(any("Private project metadata unsafe" in x for x in issues))

    def test_private_arc_accepts_unlisted_private_project(self):
        import shutil
        with tempfile.TemporaryDirectory() as d:
            dst = Path(d)
            shutil.copytree(ROOT, dst / "repo", ignore=shutil.ignore_patterns("__pycache__"))
            dst = dst / "repo"
            meta = json.loads((dst / "program.json").read_text(encoding="utf-8"))
            meta["repository_visibility"] = "private"
            meta["programme"] = "arc-neuro"
            (dst / "program.json").write_text(json.dumps(meta), encoding="utf-8")
            (dst / "areas/index.json").write_text(
                json.dumps({"lines": [{"id": "ndd", "title": "NDD"}]}), encoding="utf-8")
            (dst / "portfolio/projects.json").write_text(
                json.dumps({"schema_version":2,"projects": [candidate()]}), encoding="utf-8")
            state = dst / "PROJECT_STATE.yaml"
            state.write_text(state.read_text().replace("programme: arc-REPLACE", "programme: arc-neuro")
                             .replace("projects_registered: 0", "projects_registered: 1")
                             .replace("phase: scaffold", "phase: active"), encoding="utf-8")
            self.assertEqual(validate(dst, "scaffold"), [])

    def test_unconfigured_repo_cannot_register_private_project(self):
        import shutil
        with tempfile.TemporaryDirectory() as d:
            dst = Path(d)
            shutil.copytree(ROOT, dst / "repo", ignore=shutil.ignore_patterns("__pycache__"))
            dst = dst / "repo"
            meta = json.loads((dst / "program.json").read_text(encoding="utf-8"))
            meta["programme"] = "arc-neuro"
            (dst / "program.json").write_text(json.dumps(meta), encoding="utf-8")
            (dst / "areas/index.json").write_text(
                json.dumps({"lines": [{"id": "ndd", "title": "NDD"}]}), encoding="utf-8")
            (dst / "portfolio/projects.json").write_text(
                json.dumps({"schema_version":2,"projects": [candidate()]}), encoding="utf-8")
            self.assertTrue(any("Set repository_visibility" in x for x in validate(dst)))

    def test_unconfigured_empty_template_accepts_public_ci(self):
        from validate_repository import main
        from unittest.mock import patch
        with patch("sys.argv", ["validate_repository.py"]):
            self.assertEqual(main(["--root", str(ROOT), "--phase", "scaffold",
                                   "--repo-visibility", "public"]), 0)

    def test_public_pages_urls_reject_markup_injection(self):
        self.assertTrue(safe_public_page_url("https://matpomgit.github.io/msc-example/"))
        self.assertFalse(safe_public_page_url("https://host.example/)[malicious](x"))
        self.assertFalse(safe_public_page_url("https://user:pw@host.example/path"))
        self.assertFalse(safe_public_page_url("https://192.168.0.10/"))
        self.assertFalse(safe_public_page_url("https://[::1]/"))
        self.assertFalse(safe_public_page_url("https://server.local/"))

    def test_freshness_produces_stale_without_modification(self):
        fake=type("Result", (),{"returncode":0,"stdout": "b"*40+"\trefs/heads/main\n"})
        with patch("check_freshness.subprocess.run",return_value=fake):
            r=inspect_project(candidate())
        self.assertEqual(r["status"],"STALE")
        self.assertEqual(r["snapshot_sha"],"a"*40)

    def test_remote_unavailable_not_success(self):
        fake=type("Result", (),{"returncode":128,"stdout":"","stderr":"TOKEN MUST NOT BE LOGGED"})
        with patch("check_freshness.subprocess.run",return_value=fake):
            r=inspect_project(candidate())
        self.assertEqual(r["status"],"UNAVAILABLE")
        self.assertNotIn("TOKEN",json.dumps(r))

if __name__=="__main__": unittest.main()
