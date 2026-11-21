"""Configure an empty ARC v2 clone. Default: read-only dry run."""
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from _generator_io import safe_target, write_batch

PROGRAMMES = {"arc-neuro", "arc-xr", "arc-robo", "arc-ai"}
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
AREA = re.compile(r"^[a-z][a-z0-9-]{2,63}$")


def initialize(root: Path, *, programme: str, repository: str,
               title: str, owner: str, scope: str, visibility: str,
               areas: list[str], apply: bool = False) -> list[str]:
    root = root.absolute()
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Invalid ARC directory")
    if programme not in PROGRAMMES or not REPO.fullmatch(repository) or repository.split("/")[1] != programme:
        raise ValueError("Repository must be Owner/arc-programme")
    if visibility not in ("public", "private"):
        raise ValueError("Explicit public or private visibility required")
    if any(not isinstance(value, str) or not value.strip() or "\n" in value or "\r" in value
           for value in (title, owner, scope)) or "#" in owner or ":" in owner:
        raise ValueError("Invalid title, owner or scope")
    if (owner != owner.strip() or owner == "null" or owner.startswith(("!", "&", "*", "[", "{"))
            or any(ord(char) < 32 for char in owner)):
        raise ValueError("Owner cannot be serialized as a PROJECT_STATE scalar")
    if len(set(areas)) != len(areas) or any(not AREA.fullmatch(x) for x in areas):
        raise ValueError("Invalid or duplicate research area")

    program_path = root / "program.json"
    program = json.loads(program_path.read_text(encoding="utf-8"))
    if (program.get("schema_version") != 2 or program.get("programme") != "arc-REPLACE"
            or program.get("repository_full_name") is not None
            or program.get("repository_visibility") != "unconfigured"):
        raise ValueError("Refusing to re-initialize an existing ARC")
    area_path = root / "areas/index.json"
    if json.loads(area_path.read_text(encoding="utf-8")).get("lines"):
        raise ValueError("Existing research areas require manual review")

    state_path = root / "PROJECT_STATE.yaml"
    state = state_path.read_text(encoding="utf-8")
    substitutions = (
        ("programme: arc-REPLACE", "programme: " + programme),
        ("scientific_owner: REPLACE_OWNER", "scientific_owner: " + json.dumps(owner, ensure_ascii=False)),
        ("phase: scaffold", "phase: planned"),
        ("updated: null", "updated: " + date.today().isoformat()),
        ("known_blockers:\n  - configure_programme_owner_scope_and_projects", "known_blockers: []"),
        ("next_action: inventory_primary_msc_repositories", "next_action: design_initial_research_protocol"),
    )
    for old, new in substitutions:
        if old not in state:
            raise ValueError("State placeholder missing: " + old.split(":")[0])
        state = state.replace(old, new, 1)

    readme_path = root / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    readme = readme.replace("# ARC — szablon programu badawczego", "# " + title)
    readme = readme.replace("**Typ:** program ARC (`arc-*`)", "**Program:** `" + programme + "`")
    readme = readme.replace(
        "Zakres programu wynika z jego głównych pytań naukowych, a nie wyłącznie z zastosowanej aparatury czy oprogramowania. Programy ARC obejmują neuronaukę i psychoinformatykę, rzeczywistość rozszerzoną, robotykę oraz metody sztucznej inteligencji.",
        scope,
    )
    readme = readme.replace(
        "Repozytorium stanowi szablon struktury programów ARC. Szczegółowe informacje o konfiguracji znajdują się w [dokumentacji technicznej](TEMPLATE_SETUP.md), a warunki rozpowszechniania w [licencji](LICENSE).",
        "Repozytorium przedstawia program " + title + ". Zasady wykorzystania materiałów określa [licencja](LICENSE), a opis techniczny znajduje się w [dokumentacji](TEMPLATE_SETUP.md).",
    )
    research_path = root / "RESEARCH.md"
    research = research_path.read_text(encoding="utf-8")
    research = research.replace("REPLACE_PROGRAM_NAME", title).replace("REPLACE_SCIENTIFIC_SCOPE", scope)

    citation_path = root / "CITATION.cff"
    citation = citation_path.read_text(encoding="utf-8")
    marker = 'title: "ARC REPLACE PROGRAM — TEMPLATE"'
    if marker not in citation:
        raise ValueError("Citation marker missing")
    citation = citation.replace(marker, "title: " + json.dumps(title, ensure_ascii=False))

    program.update(programme=programme, repository_full_name=repository, title=title,
                   owner=owner, scope=scope, repository_visibility=visibility,
                   scientific_state="planned")
    area_data = {"schema_version": 1, "lines": [
        {"id": key, "title": key.upper()} for key in areas]}
    payload = {
        program_path: json.dumps(program, ensure_ascii=False, indent=2) + "\n",
        area_path: json.dumps(area_data, ensure_ascii=False, indent=2) + "\n",
        state_path: state,
        readme_path: readme,
        research_path: research,
        citation_path: citation,
    }
    for target in payload:
        safe_target(root, target)
    if apply:
        write_batch(root, payload)
    return [str(x.relative_to(root)) for x in payload]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--programme", choices=sorted(PROGRAMMES), required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--visibility", choices=("public", "private"), required=True)
    parser.add_argument("--area", action="append", default=[])
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        paths = initialize(args.root, programme=args.programme, repository=args.repository,
                           title=args.title, owner=args.owner, scope=args.scope,
                           visibility=args.visibility, areas=args.area, apply=args.apply)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, "BLOCKED: " + str(exc) + "\n")
    print(("APPLIED" if args.apply else "DRY_RUN") + ": " + ", ".join(paths))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
