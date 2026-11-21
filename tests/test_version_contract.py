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
            before = program_path.read_bytes()
            problems = validate(destination)
            self.assertEqual(problems, [], problems)
            self.assertEqual(program_path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
