"""Generate a canonical local MSC manuscript; default is dry-run."""
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from _generator_io import safe_target, write_batch

MSC = re.compile(r"^MSC-[A-Z0-9]+(?:-[A-Z0-9]+)*$")
STUDY_TYPES = {"empirical", "simulation", "methods", "review", "theoretical"}


def tex_escape(value: str) -> str:
    special = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "%": r"\%",
               "&": r"\&", "#": r"\#", "$": r"\$", "_": r"\_",
               "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(special.get(char, char) for char in value)


def create(root: Path, *, ident: str, title: str, area: str,
           study_type: str = "empirical", authors: str | None = None,
           apply: bool = False) -> list[str]:
    root = root.absolute()
    if not root.is_dir() or root.is_symlink() or not MSC.fullmatch(ident):
        raise ValueError("Invalid ARC directory or MSC identifier")
    if authors is not None and (not isinstance(authors, str) or "\n" in authors or "\r" in authors):
        raise ValueError("Author list must be supplied explicitly on one line")
    if study_type not in STUDY_TYPES:
        raise ValueError("Unsupported study type")
    if not isinstance(title, str) or not title.strip() or any(c in title for c in "\r\n"):
        raise ValueError("Title must be a nonempty single line")
    meta = json.loads((root / "program.json").read_text(encoding="utf-8"))
    repository = meta.get("repository_full_name")
    if (meta.get("schema_version") != 2 or meta.get("programme") == "arc-REPLACE"
            or meta.get("repository_visibility") not in ("public", "private")
            or not isinstance(repository, str) or not repository.endswith("/" + meta["programme"])):
        raise ValueError("Configure ARC v2 before creating manuscripts")
    areas = json.loads((root / "areas/index.json").read_text(encoding="utf-8")).get("lines", [])
    if area not in {x.get("id") for x in areas if isinstance(x, dict)}:
        raise ValueError("Unregistered research area")
    manuscript_root = meta.get("manuscript_root")
    if manuscript_root not in ("manuscripts", "papers"):
        raise ValueError("Unsupported manuscript root")
    directory = root / manuscript_root
    if manuscript_root == "papers":
        directory = directory / area
    directory = directory / ident
    files = {name: directory / name for name in ("main.tex", "study.yaml", "references.bib", "README.md")}
    for path in files.values():
        safe_target(root, path)
    reg_path = root / "portfolio/papers.json"
    state_path = root / "PROJECT_STATE.yaml"
    register = json.loads(reg_path.read_text(encoding="utf-8"))
    if register.get("schema_version") != 2 or not isinstance(register.get("papers"), list):
        raise ValueError("Expected registry schema_version=2")
    if any(not isinstance(p, dict) for p in register["papers"]):
        raise ValueError("Invalid paper records")
    existing = [p for p in register["papers"] if p.get("id") == ident]
    if existing:
        from validate_repository import validate
        from validate_study import validate_study
        try:
            import yaml
        except ImportError as exc:
            raise ValueError("Cannot verify existing manuscript without PyYAML") from exc
        record = existing[0]
        recorded_owner = record.get("owner")
        recorded_manuscript = record.get("manuscript")
        study_path = str(files["study.yaml"].relative_to(root))
        matches = (
            len(existing) == 1
            and record.get("title") == title
            and record.get("area") == area
            and record.get("relation") == "primary"
            and isinstance(recorded_owner, dict)
            and recorded_owner.get("mode") == "local"
            and recorded_owner.get("repository") == repository
            and recorded_owner.get("project_id") is None
            and isinstance(recorded_manuscript, dict)
            and recorded_manuscript.get("format") == "latex"
            and recorded_manuscript.get("path") == str(files["main.tex"].relative_to(root))
            and record.get("study_plan") == study_path
            and all(f.is_file() and f.stat().st_size > 0 for f in files.values())
        )
        if matches:
            errors = validate_study(root, study_path, ident)
            if errors:
                matches = False
            else:
                try:
                    current_study = yaml.safe_load(files["study.yaml"].read_text(encoding="utf-8"))
                except (OSError, ValueError, yaml.YAMLError):
                    matches = False
                else:
                    matches = isinstance(current_study, dict) and current_study.get("study_type") == study_type
            if matches and authors is not None:
                source_now = files["main.tex"].read_text(encoding="utf-8")
                matches = r"\author{" + tex_escape(authors) + "}" in source_now
            if matches:
                matches = not validate(root)
        if matches:
            return []
        raise ValueError("MSC identifier already in use for different or invalid content")
    if directory.exists() or directory.is_symlink():
        raise FileExistsError("Manuscript directory already exists")

    source = (
        "\\documentclass[11pt,a4paper]{article}\n"
        "\\usepackage[T1]{fontenc}\n\\usepackage[utf8]{inputenc}\n"
        "\\usepackage{lmodern}\n\\usepackage[hidelinks]{hyperref}\n"
        "\\title{" + tex_escape(title) + "}\n"
        "\\author{" + tex_escape(authors or "") + "}\n"
        "\\date{}\n\\begin{document}\n\\maketitle\n"
        "\\begin{abstract}\n\\end{abstract}\n"
        "\\section{Wprowadzenie}\n"
        "\\section{Cel i pytania badawcze}\n"
        "\\section{Materiał i metody}\n"
        "\\section{Plan analizy}\n"
        "\\section{Wyniki}\n"
        "\\section{Dyskusja}\n"
        "\\bibliographystyle{plain}\n"
        "% Enable bibliography after adding verified references:\n"
        "% \\bibliography{references}\n"
        "\\end{document}\n"
    )
    study = (
        "schema_version: 1\npaper_id: " + json.dumps(ident) +
        "\nstudy_type: " + json.dumps(study_type) +
        "\nresearch_question: null\nhypotheses: []\n"
        "design:\n  type: not_specified\n  unit_of_analysis: null\n"
        "  population: null\n  sample_size: null\n"
        "outcomes:\n  primary: null\n  secondary: []\n"
        "analysis:\n  methods: []\n  validation: null\n"
        "evidence:\n  empirical_results: not_available\n"
        "  protocol_frozen: false\n"
    )
    record = {
        "id": ident, "title": title, "area": area, "research_state": "planned",
        "publication_stage": "concept", "relation": "primary",
        "owner": {"mode": "local", "repository": repository, "project_id": None},
        "manuscript": {"path": str(files["main.tex"].relative_to(root)), "format": "latex"},
        "study_plan": str(files["study.yaml"].relative_to(root)),
        "public_listing": False, "public_summary": None, "doi": None, "preprint_url": None,
        "preregistration_url": None, "publication_url": None,
        "stage_evidence": None,
    }
    state = state_path.read_text(encoding="utf-8")
    match = re.search(r"^papers_registered: (\d+)$", state, flags=re.M)
    if not match or int(match.group(1)) != len(register["papers"]):
        raise ValueError("PROJECT_STATE counter inconsistent with paper register")
    state = state.replace(match.group(0), "papers_registered: " + str(len(register["papers"]) + 1), 1)
    if "phase: scaffold" in state:
        state = state.replace("phase: scaffold", "phase: planned", 1)
    state = re.sub(r"^updated: (?:null|\d{4}-\d{2}-\d{2})$", "updated: " +
                   date.today().isoformat(), state, count=1, flags=re.M)
    register["papers"].append(record)
    register["papers"].sort(key=lambda x: x["id"])
    updates = {
        files["main.tex"]: source,
        files["study.yaml"]: study,
        files["references.bib"]: "% Verified references will be added here.\n",
        files["README.md"]: "# " + title + "\n\nID: " + ident +
                            "\n\nWstępny manuskrypt naukowy; brak wyników empirycznych.\n",
        reg_path: json.dumps(register, ensure_ascii=False, indent=2) + "\n",
        state_path: state,
    }
    if apply:
        write_batch(root, updates, set(files.values()))
    return [str(p.relative_to(root)) for p in updates]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--area", required=True)
    parser.add_argument("--authors", help="Explicit confirmed manuscript authors; never inferred from ARC owner")
    parser.add_argument("--study-type", choices=sorted(STUDY_TYPES), default="empirical")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        paths = create(args.root, ident=args.id, title=args.title, area=args.area,
                       study_type=args.study_type, authors=args.authors, apply=args.apply)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, "BLOCKED: " + str(exc) + "\n")
    print(("ALREADY_EXISTS" if not paths else "APPLIED" if args.apply else "DRY_RUN") +
          ": " + ", ".join(paths))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
