"""Version-contract regression checks for current and legacy ARC metadata."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


class VersionContractTests(unittest.TestCase):
    def test_schema_two_accepts_current_and_legacy_template_metadata(self):
        schema = json.loads((ROOT / "schemas/program.v2.schema.json").read_text(encoding="utf-8"))
        program = json.loads((ROOT / "program.json").read_text(encoding="utf-8"))
        self.assertEqual(program["schema_version"], 2)
        self.assertEqual(program["template_version"], "0.1.0")
        for value in ("0.1.0", "2.0.0"):
            with self.subTest(template_version=value):
                candidate = dict(program, template_version=value)
                Draft202012Validator(schema).validate(candidate)

    def test_validators_accept_legacy_v2_without_rewriting(self):
        from scripts.validate_repository import validate
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "arc"
            shutil.copytree(ROOT, destination, ignore=shutil.ignore_patterns(".git", "__pycache__", ".venv"))
            program_path = destination / "program.json"
            state_path = destination / "PROJECT_STATE.yaml"
            program = json.loads(program_path.read_text(encoding="utf-8"))
            program["template_version"] = "2.0.0"
            program_path.write_text(json.dumps(program, indent=2) + "\n", encoding="utf-8")
            state = state_path.read_text(encoding="utf-8")
            state_path.write_text(state.replace("template_version: 0.1.0", "template_version: 2.0.0"), encoding="utf-8")
            from scripts.migrate_arc import execute
            tracked = [
                "program.json", "PROJECT_STATE.yaml", "areas/index.json",
                "portfolio/projects.json", "portfolio/papers.json",
                "portfolio/dependencies.json",
            ]
            before = {name: (destination / name).read_bytes() for name in tracked}
            problems = validate(destination)
            self.assertEqual(problems, [], problems)
            for mode in ("plan", "apply"):
                with self.subTest(mode=mode):
                    result = execute(destination, mode=mode)
                    self.assertEqual(result["status"], "ALREADY_V2", result)
            self.assertEqual(
                {name: (destination / name).read_bytes() for name in tracked}, before
            )

    def test_invalid_template_version_type_yields_diagnostic(self):
        from scripts.validate_repository import validate
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "arc"
            shutil.copytree(ROOT, destination, ignore=shutil.ignore_patterns(".git", "__pycache__", ".venv"))
            path = destination / "program.json"
            original = json.loads(path.read_text(encoding="utf-8"))
            for invalid in ([], {}, None, 42):
                with self.subTest(value=invalid):
                    path.write_text(json.dumps(dict(original, template_version=invalid)) + "\n", encoding="utf-8")
                    issues = validate(destination)
                    self.assertTrue(any("Unexpected program template version" in x for x in issues), issues)

    def test_version_mismatch_between_state_and_program_is_rejected(self):
        from scripts.validate_repository import validate
        from scripts.migrate_arc import execute
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "arc"
            shutil.copytree(ROOT, destination, ignore=shutil.ignore_patterns(".git", "__pycache__", ".venv"))
            state_path = destination / "PROJECT_STATE.yaml"
            state_path.write_text(
                state_path.read_text(encoding="utf-8").replace(
                    "template_version: 0.1.0", "template_version: 2.0.0"
                ), encoding="utf-8"
            )
            self.assertTrue(any("PROJECT_STATE mismatch: template_version" in x
                                for x in validate(destination)))
            before = {name: (destination / name).read_bytes()
                      for name in ("program.json", "PROJECT_STATE.yaml", "portfolio/papers.json")}
            for mode in ("plan", "apply"):
                result = execute(destination, mode=mode)
                self.assertEqual(result["status"], "BLOCKED", result)
            self.assertEqual(
                {name: (destination / name).read_bytes() for name in before}, before
            )


if __name__ == "__main__":
    unittest.main()
