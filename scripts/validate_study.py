"""Fail-closed offline validation of scientific study.yaml metadata."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def validate_study(root: Path, relative: str, expected_id: str) -> list[str]:
    """Return precise errors; no remote access, code execution or data loading."""
    try:
        import yaml
        from jsonschema import Draft202012Validator
    except ImportError:
        return ["STUDY_DEPENDENCIES_UNAVAILABLE: install requirements-research.txt"]
    path = root / relative
    if not path.is_file() or path.is_symlink():
        return ["STUDY_INVALID_PATH: " + relative]
    try:
        if path.stat().st_size > 131072:
            return ["STUDY_TOO_LARGE: " + relative]
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        schema = json.loads((root / "schemas/study.v1.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return ["STUDY_INVALID_FORMAT: " + relative + ": " + type(exc).__name__]
    errors = ["STUDY_SCHEMA: " + relative + " /" + "/".join(map(str, e.path)) + ": " + e.message
              for e in Draft202012Validator(schema).iter_errors(data)]
    if not isinstance(data, dict):
        return sorted(set(errors))
    if data.get("paper_id") != expected_id:
        errors.append("STUDY_WRONG_ID: " + relative)
    hypotheses = data.get("hypotheses")
    if isinstance(hypotheses, list):
        ids = [h.get("id") for h in hypotheses if isinstance(h, dict)]
        if len(ids) != len(set(ids)):
            errors.append("STUDY_DUPLICATE_HYPOTHESES: " + relative)
    evidence = data.get("evidence")
    if isinstance(evidence, dict) and evidence.get("protocol_frozen") is True:
        if not isinstance(data.get("research_question"), str) or not data["research_question"].strip():
            errors.append("STUDY_FROZEN_MISSING_QUESTION: " + relative)
        if data.get("study_type") in ("empirical","simulation","methods") and (
            not isinstance(data.get("analysis"), dict) or not data["analysis"].get("methods")):
            errors.append("STUDY_FROZEN_MISSING_ANALYSIS: " + relative)
    return sorted(set(errors))


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--path",required=True,help="Relative study.yaml path")
    parser.add_argument("--paper-id",required=True)
    args=parser.parse_args()
    from validate_registry_v2 import safe_path
    if not safe_path(args.path):
        parser.exit(2, "STUDY_INVALID_PATH\n")
    errors=validate_study(args.root,args.path,args.paper_id)
    for error in errors:
        print("FAIL:",error)
    print("study-contract: "+("FAIL" if errors else "PASS"))
    return 1 if errors else 0


if __name__=="__main__":
    raise SystemExit(main())
