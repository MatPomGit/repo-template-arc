"""Dependency-free structural/referential validator for an ARC programme."""
from __future__ import annotations
import argparse
import configparser
import ipaddress
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

# Execute with python scripts/validate_repository.py or import in offline tests.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_documentation import check_documentation
from validate_pages import check_pages
from validate_state import check_state
from validate_registry_v2 import validate_registry_v2
from validate_study import validate_study

ALLOWED_PROGRAMMES = frozenset(("arc-neuro", "arc-ai", "arc-xr", "arc-robo"))
ALLOWED_ROLES = frozenset(("primary", "related"))
ALLOWED_VISIBILITY = frozenset(("public", "private"))
ALLOWED_STAGES = frozenset(("concept", "protocol", "preregistered", "collection", "analysis", "draft", "submitted", "accepted", "published", "archived", "withdrawn"))
ALLOWED_STATUSES = frozenset(("planned", "active", "paused", "archived"))
REQUIRED = (
    ".gitignore", ".gitattributes", ".github/ACTIONS_POLICY.md",
    ".github/PULL_REQUEST_TEMPLATE.md", ".github/ISSUE_TEMPLATE/portfolio-task.md",
    "README.md", "TEMPLATE_SETUP.md", "AGENTS.md", "ARCHITECTURE.md",
    "RESEARCH.md", "REPRODUCIBILITY.md", "PROJECT_STATE.yaml",
    "ROADMAP.md", "CHANGELOG.md", "CODE_OF_CONDUCT.md",
    "GOVERNANCE.md", "SUPPORT.md", "SECURITY.md", ".github/AGENT_WORKFLOW.md",
    "LICENSE", "CITATION.cff", "VERSION", "mkdocs.yml",
    "program.json", "areas/index.json", "areas/README.md",
    "portfolio/projects.json", "portfolio/papers.json",
    "portfolio/dependencies.json", "portfolio/README.md",
    "equipment/README.md", "software/README.md",
    "docs/index.md", "docs/scientific-scope.md", "docs/publication-policy.md",
    "docs/data-policy.md", "docs/submodules.md", "docs/pages.md",
    "docs/releases.md",
    "docs/documentation.md", "docs/architecture/README.md",
    "docs/architecture/portfolio-boundaries.md", "docs/architecture/data-flow.md",
    "docs/architecture/reproducibility.md", "docs/adr/README.md",
    "docs/adr/0001-canonical-ownership.md", "docs/adr/0002-publication-boundaries.md",
    "docs/security/threat-model.md", "docs/security/incident-response.md",
    "docs/operations/runbook.md", "config/documentation-policy.json",
    "config/pages-policy.json", "pages/index.md", "pages/projects.md",
    "scripts/validate_repository.py", "scripts/bootstrap.py",
    "scripts/build_public_catalog.py", "scripts/validate_pages.py",
    "scripts/validate_documentation.py", "scripts/validate_state.py",

    "scripts/validate_site.py", "tests/test_repository_contract.py",
    "tests/test_pages_policy.py", "tests/test_documentation_policy.py",
    "tests/test_agent_policy.py", "tests/test_state_policy.py",
    "tests/test_metadata_policy.py", "tests/test_site_policy.py",
)
IDENTIFIER = re.compile(r"^[a-z][a-z0-9-]{2,63}$")
PAPER_IDENTIFIER = re.compile(r"^(?:MSC-[A-Z0-9]+(?:-[A-Z0-9]+)*|[a-z][a-z0-9-]{2,63})$")
SHA256 = re.compile(r"^[a-f0-9]{64}$")
DOI = re.compile(r"^10\.\d{4,9}/\S+$")
PROJECT_FIELDS = frozenset(("id","title","repository","url","role","primary_program","line","status","visibility","public_listing","default_branch","snapshot_sha","pages_url","submodule_path"))
PAPER_FIELDS = frozenset(("id","title","owner_project_id","canonical_repository","manuscript_path","stage","doi","preprint_url","preregistration_url","publication_url","stage_evidence"))
PROGRAM_FIELDS = frozenset(("schema_version","template_version","type","programme","repository_full_name","manuscript_root","title","owner","scope","default_branch","license_spdx","pages_status","pages_url","public_catalog_policy","scientific_state","owner_of_raw_data","repository_visibility"))
AREA_LINE_FIELDS = frozenset(("id","title"))
DEPENDENCY_FIELDS = frozenset(("project_id","ref","version","sha","role","contract_path","validation_status","notes"))
STAGE_EVIDENCE_KINDS = {"submitted":"submission_receipt","accepted":"editorial_decision","published":"publication_record"}
SHA40 = re.compile(r"^[0-9a-f]{40}$")
REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def github_repo_url(repo: str, url: str) -> bool:
    if not REPOSITORY.fullmatch(repo) or not isinstance(url, str):
        return False
    parsed = urlparse(url)
    return (parsed.scheme == "https" and parsed.hostname == "github.com"
            and parsed.username is None and parsed.password is None
            and parsed.port is None and parsed.path.rstrip("/") == "/" + repo
            and not parsed.query and not parsed.fragment)


def safe_public_page_url(url: object) -> bool:
    """Syntactic check only: neither approval nor domain ownership is verified."""
    if not isinstance(url, str) or any(c.isspace() or c in "<>[]()\\" for c in url):
        return False
    try:
        parsed = urlparse(url)
        return (parsed.scheme == "https" and parsed.hostname is not None
                and parsed.username is None and parsed.password is None
                and parsed.port is None and not parsed.query and not parsed.fragment
                and not parsed.hostname.lower().endswith((".local", ".localhost", ".internal"))
                and parsed.hostname.lower() != "localhost"
                and _public_hostname(parsed.hostname))
    except ValueError:
        return False


def _public_hostname(host: str) -> bool:
    """Reject IP literals that resolve to private or special-use ranges."""
    try:
        return ipaddress.ip_address(host).is_global
    except ValueError:
        return True


def load_json(root: Path, relative: str, issues: list[str]):
    p = root / relative
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        issues.append(f"Invalid JSON in {relative}: {type(exc).__name__}")
        return {}


def safe_submodule_path(v: str) -> bool:
    if not isinstance(v, str) or not v.startswith("projects/"):
        return False
    p = Path(v)
    return v == p.as_posix() and not p.is_absolute() and len(p.parts) >= 2 and all(x not in ("..", ".", "") for x in p.parts)


def safe_relative_study_path(path: str) -> bool:
    return (not path.startswith("/") and "\\" not in path and
            all(part not in ("", ".", "..") for part in path.split("/")))


def validate(root: Path, phase: str = "scaffold", verified_repository: str | None = None) -> list[str]:
    issues: list[str] = []
    if not root.is_dir():
        return ["Missing repository root"]
    for rel in REQUIRED:
        f = root / rel
        if not f.is_file() or f.is_symlink() or not f.read_bytes().strip():
            issues.append(f"Missing or empty required regular file: {rel}")

    issues.extend(check_documentation(root))
    issues.extend(check_pages(root))
    if (root / "CONTRIBUTING.md").exists():
        issues.append("CONTRIBUTING.md is not part of the ARC template")

    meta = load_json(root, "program.json", issues)
    areas = load_json(root, "areas/index.json", issues)
    projects = load_json(root, "portfolio/projects.json", issues)
    papers = load_json(root, "portfolio/papers.json", issues)
    dependencies = load_json(root, "portfolio/dependencies.json", issues)
    if not all(isinstance(obj, dict) for obj in (meta, areas, projects, papers, dependencies)):
        return sorted(set(issues + ["Invalid ARC root JSON object type"]))
    if set(meta) - PROGRAM_FIELDS:
        issues.append("Undeclared programme metadata fields")
    if meta.get("schema_version") == 2 and set(meta) != PROGRAM_FIELDS:
        issues.append("Missing required programme v2 fields")
    for filename, obj, fields in (
        ("areas/index.json", areas, {"lines","schema_version"}),
        ("portfolio/projects.json", projects, {"projects","schema_version"}),
        ("portfolio/papers.json", papers, {"papers","schema_version"}),
        ("portfolio/dependencies.json", dependencies, {"tools","equipment","datasets","schema_version"}),
    ):
        if set(obj) - fields or ("schema_version" in obj and type(obj["schema_version"]) is not int):
            issues.append("Unexpected registry fields or schema type: " + filename)
    # v1 remains supported without v2-only schemas/tests, permitting audit before migration.
    if meta.get("schema_version") == 2:
        for rel in ("schemas/program.v2.schema.json", "schemas/projects.v2.schema.json",
                    "schemas/papers.v2.schema.json", "schemas/dependencies.v2.schema.json",
                    "schemas/study.v1.schema.json", "scripts/init_arc.py",
                    "scripts/new_manuscript.py", "scripts/validate_study.py",
                    "scripts/_generator_io.py", "requirements-research.txt",
                    "tests/test_generators.py", "scripts/build_article_catalog.py",
                    "scripts/migrate_arc.py", "tests/test_article_catalog.py",
                    "tests/test_migrations.py"):
            f = root / rel
            if not f.is_file() or f.is_symlink() or not f.read_bytes().strip():
                issues.append("Missing v2 schema: " + rel)
    schema_version = meta.get("schema_version")
    if type(schema_version) is not int or schema_version not in (1, 2) or meta.get("type") != "arc-program":
        issues.append("Invalid program.json schema_version/type")
    # A template release and the on-disk data schema are separate version axes.
    template_version = meta.get("template_version")
    if (not isinstance(template_version, str) or
            not re.fullmatch(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)", template_version)):
        issues.append("Unexpected program template version (expected numeric SemVer core)")
    if schema_version == 2:
        for rel, obj in (("portfolio/projects.json", projects),
                         ("portfolio/papers.json", papers),
                         ("portfolio/dependencies.json", dependencies)):
            if obj.get("schema_version") != 2:
                issues.append("Registry requires schema_version 2: " + rel)
    programme = meta.get("programme")
    if schema_version == 2:
        if meta.get("manuscript_root") not in ("manuscripts", "papers"):
            issues.append("Invalid manuscript_root (expected manuscripts or papers)")
        repo_name = meta.get("repository_full_name")
        if repo_name is not None and (not isinstance(repo_name, str) or
                                      not REPOSITORY.fullmatch(repo_name) or
                                      not isinstance(programme, str) or
                                      not repo_name.endswith("/" + programme)):
            issues.append("Invalid program canonical repository identity")
    declared_visibility = meta.get("repository_visibility", "unconfigured")
    if declared_visibility not in ("unconfigured", "public", "private"):
        issues.append("Invalid program.json repository_visibility")
    if phase == "publish" and declared_visibility == "unconfigured":
        issues.append("Set repository_visibility before publishing")
    if phase == "publish" and programme not in ALLOWED_PROGRAMMES:
        issues.append("Programme must be one of four approved ARC names")
    if meta.get("owner_of_raw_data") is not False or meta.get("public_catalog_policy") != "explicit_opt_in":
        issues.append("Unsafe programme data/catalog policy")
    if not isinstance(projects.get("projects"), list):
        issues.append("portfolio/projects.json requires projects array")
    if not isinstance(papers.get("papers"), list):
        issues.append("portfolio/papers.json requires papers array")
    if not isinstance(areas.get("lines"), list):
        issues.append("areas/index.json requires lines array")
    for key in ("tools", "equipment", "datasets"):
        if not isinstance(dependencies.get(key), list):
            issues.append(f"portfolio/dependencies.json requires {key} array")

    project_items = projects.get("projects", []) if isinstance(projects.get("projects"), list) else []
    paper_items = papers.get("papers", []) if isinstance(papers.get("papers"), list) else []
    if verified_repository is not None:
        if not REPOSITORY.fullmatch(verified_repository):
            issues.append("Invalid externally verified repository identity")
        elif not (programme=="arc-REPLACE" and declared_visibility=="unconfigured"
                  and not project_items and not paper_items):
            if meta.get("repository_full_name")!=verified_repository:
                issues.append("Canonical repository differs from verified GitHub repository")
    issues.extend(check_state(root, meta, project_items, paper_items))
    lines, project_ids, project_repos = set(), set(), {}
    for line in areas.get("lines", []) if isinstance(areas.get("lines"), list) else []:
        if isinstance(line, dict) and set(line) - AREA_LINE_FIELDS:
            issues.append("Undeclared research line metadata fields")
        if not isinstance(line, dict) or not IDENTIFIER.fullmatch(str(line.get("id", ""))):
            issues.append("Invalid research line identifier")
            continue
        if line["id"] in lines:
            issues.append(f"Duplicated line: {line['id']}")
        lines.add(line["id"])
        if not line.get("title"):
            issues.append(f"Missing line title: {line['id']}")

    registered_projects = projects.get("projects", []) if isinstance(projects.get("projects"), list) else []
    if registered_projects and declared_visibility == "unconfigured":
        issues.append("Set repository_visibility before registering projects")
    for p in registered_projects:
        if not isinstance(p, dict):
            issues.append("Invalid project record type"); continue
        if set(p) - PROJECT_FIELDS:
            issues.append("Undeclared project metadata fields: " + str(p.get("id", "?")))
        if schema_version == 2 and set(p) != PROJECT_FIELDS:
            issues.append("Missing required project v2 fields: " + str(p.get("id", "?")))
        if not isinstance(p.get("title"), str) or not p["title"].strip():
            issues.append("Missing project title")
        ident, repo, url = p.get("id", ""), p.get("repository", ""), p.get("url", "")
        if not IDENTIFIER.fullmatch(str(ident)) or ident in project_ids:
            issues.append(f"Invalid or duplicate project id: {ident}")
        project_ids.add(ident)
        if not github_repo_url(repo, url):
            issues.append(f"Invalid project repository URL: {ident}")
        if repo in project_repos:
            issues.append(f"Duplicated project repository: {repo}")
        project_repos[ident] = repo
        if p.get("role") not in ALLOWED_ROLES or p.get("status") not in ALLOWED_STATUSES:
            issues.append(f"Invalid role/status for project: {ident}")
        if p.get("role") == "primary" and p.get("primary_program") != programme:
            issues.append(f"Primary project assigned to other programme: {ident}")
        if p.get("primary_program") not in ALLOWED_PROGRAMMES:
            issues.append(f"Invalid primary programme: {ident}")
        if p.get("line") not in lines:
            issues.append(f"Project references unknown research line: {ident}")
        if p.get("visibility") not in ALLOWED_VISIBILITY or not isinstance(p.get("public_listing"), bool):
            issues.append(f"Invalid visibility/public_listing: {ident}")
        if declared_visibility != "private" and p.get("visibility") != "public":
            issues.append(f"Private project metadata unsafe in nonprivate ARC source: {ident}")
        if p.get("public_listing"):
            if p.get("visibility") != "public":
                issues.append(f"Private project marked for public listing: {ident}")
            if not safe_public_page_url(p.get("pages_url")):
                issues.append(f"Missing syntactically valid public Pages URL for listed project: {ident}")
        sha = p.get("snapshot_sha")
        if sha is not None and (not isinstance(sha, str) or not SHA40.fullmatch(sha)):
            issues.append(f"Invalid snapshot SHA: {ident}")
        branch = p.get("default_branch")
        if not isinstance(branch, str) or not re.fullmatch(r"[A-Za-z0-9._/-]{1,100}", branch) or ".." in branch or branch.startswith("-"):
            issues.append(f"Invalid default branch: {ident}")
        subpath = p.get("submodule_path")
        if subpath is not None and (not safe_submodule_path(subpath) or sha is None):
            issues.append(f"Invalid submodule path or missing SHA: {ident}")

    paper_ids = set()
    for p in papers.get("papers", []) if isinstance(papers.get("papers"), list) else []:
        if schema_version == 2:
            continue
        if not isinstance(p, dict):
            issues.append("Invalid paper record type"); continue
        if set(p) - PAPER_FIELDS:
            issues.append("Undeclared paper metadata fields: " + str(p.get("id", "?")))
        if not isinstance(p.get("title"), str) or not p["title"].strip():
            issues.append("Missing paper title")
        ident, owner = p.get("id", ""), p.get("owner_project_id")
        if not PAPER_IDENTIFIER.fullmatch(str(ident)) or ident in paper_ids:
            issues.append(f"Invalid or duplicate paper id: {ident}")
        paper_ids.add(ident)
        if owner not in project_ids:
            issues.append(f"Unknown canonical project for paper: {ident}")
        if p.get("canonical_repository") != project_repos.get(owner):
            issues.append(f"Canonical repository mismatch for paper: {ident}")
        if p.get("stage") not in ALLOWED_STAGES:
            issues.append(f"Unknown paper stage: {ident}")
        manuscript_path = p.get("manuscript_path")
        if not isinstance(manuscript_path, str) or not manuscript_path or "\\" in manuscript_path or ".." in Path(manuscript_path).parts or manuscript_path.startswith("/"):
            issues.append(f"Invalid manuscript path: {ident}")
        doi = p.get("doi")
        if doi is not None and (not isinstance(doi, str) or not DOI.fullmatch(doi)):
            issues.append(f"Invalid DOI syntax: {ident}")
        for field in ("preprint_url","preregistration_url","publication_url"):
            value = p.get(field)
            if value is not None and not safe_public_page_url(value):
                issues.append(f"Invalid public paper URL {field}: {ident}")
        if p.get("stage") in STAGE_EVIDENCE_KINDS:
            evidence = p.get("stage_evidence")
            expected_kind = STAGE_EVIDENCE_KINDS[p["stage"]]
            if (not isinstance(evidence, dict) or set(evidence) != {"kind", "sha256", "checked_on"}
                    or evidence.get("kind") != expected_kind
                    or not isinstance(evidence.get("sha256"), str) or not SHA256.fullmatch(evidence["sha256"])
                    or not isinstance(evidence.get("checked_on"), str)
                    or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", evidence["checked_on"])):
                issues.append(f"Missing or invalid status evidence: {ident}")
            if p["stage"] == "published" and doi is None and p.get("publication_url") is None:
                issues.append(f"Published paper lacks DOI/publication URL: {ident}")
        elif p.get("stage_evidence") is not None:
            issues.append(f"Unexpected stage evidence: {ident}")

    for group in ("tools", "equipment", "datasets"):
        group_records = dependencies.get(group, []) if isinstance(dependencies.get(group), list) else []
        for p in group_records:
            if schema_version == 2:
                continue
            if (not isinstance(p, dict) or set(p) - DEPENDENCY_FIELDS
                    or p.get("project_id") not in project_ids
                    or not isinstance(p.get("ref"), str) or not p["ref"].strip()):
                issues.append(f"Invalid {group} dependency reference")

    if schema_version == 2:
        issues.extend(validate_registry_v2(root, meta, paper_items, dependencies,
                                           project_repos, lines, safe_public_page_url))
        for manuscript in paper_items:
            if not isinstance(manuscript, dict):
                continue
            study = manuscript.get("study_plan")
            if (isinstance(study, str) and study.endswith(".yaml") and
                    safe_relative_study_path(study)):
                issues.extend(validate_study(root, study, str(manuscript.get("id", ""))))

    submodule_records = {
        p["submodule_path"]: p for p in registered_projects
        if isinstance(p, dict) and isinstance(p.get("submodule_path"), str)
    }
    subpaths = [p.get("submodule_path") for p in registered_projects
                if isinstance(p, dict) and p.get("submodule_path")]
    if len(subpaths) != len(set(subpaths)):
        issues.append("Duplicate submodule path")
    gmod = root / ".gitmodules"
    if gmod.is_symlink():
        issues.append("Unsafe .gitmodules symlink")
    elif gmod.exists() or subpaths:
        if not gmod.is_file():
            issues.append("Submodule entries exist but .gitmodules is absent")
        else:
            cfg = configparser.ConfigParser(interpolation=None, strict=True)
            try:
                cfg.read_string(gmod.read_text(encoding="utf-8"))
                found: set[str] = set()
                for section in cfg.sections():
                    match = re.fullmatch(r'submodule "([^"]+)"', section)
                    if not match or set(cfg[section]) != {"path", "url"}:
                        issues.append("Unrecognised .gitmodules section/options: " + section)
                        continue
                    path, url = cfg[section]["path"], cfg[section]["url"]
                    if not safe_submodule_path(path) or path in found:
                        issues.append("Invalid/duplicate .gitmodules path: " + path)
                    found.add(path)
                    record = submodule_records.get(path)
                    if record is None:
                        issues.append("Unregistered submodule path: " + path)
                    elif not github_repo_url(record.get("repository", ""), record.get("url", "")):
                        issues.append("Untrusted canonical submodule URL: " + path)
                    elif url not in {record["url"], record["url"] + ".git"}:
                        issues.append("Untrusted submodule URL: " + path)
                for path in set(subpaths) - found:
                    issues.append("Submodule missing from .gitmodules: " + path)
            except (configparser.Error, OSError, UnicodeError):
                issues.append("Invalid .gitmodules syntax")
    if subpaths and (root / ".git").exists():
        # Validate the *committed* gitlinks against registry snapshots (read-only).
        for p in registered_projects:
            if not isinstance(p, dict) or not p.get("submodule_path"):
                continue
            subpath = p["submodule_path"]
            if not safe_submodule_path(subpath):
                continue
            try:
                result = subprocess.run(
                    ["git", "-C", str(root), "ls-tree", "HEAD", "--", subpath],
                    capture_output=True, text=True, timeout=10, check=False,
                )
            except (OSError, subprocess.TimeoutExpired):
                issues.append(f"Submodule gitlink cannot be verified: {subpath}")
                continue
            match = re.fullmatch(
                r"160000 commit ([0-9a-f]{40})\t" + re.escape(subpath) + r"\n?",
                result.stdout,
            )
            if result.returncode != 0 or not match:
                issues.append(f"Submodule gitlink missing from committed HEAD: {subpath}")
            elif match.group(1) != p.get("snapshot_sha"):
                issues.append(f"Submodule gitlink SHA disagrees with registry: {subpath}")

    if phase == "publish":
        if not registered_projects or not lines:
            issues.append("Program publishing requires at least one project and research line")
        for key in ("title", "owner", "scope"):
            if not isinstance(meta.get(key), str) or "REPLACE" in meta.get(key, ""):
                issues.append(f"Unresolved program.json field: {key}")
        if meta.get("license_spdx") in (None, "UNDECIDED"):
            issues.append("Programme license not selected")
        if meta.get("pages_status") != "approved" or not meta.get("pages_url"):
            issues.append("No reviewed public Pages configuration")
        for f in ("README.md", "pages/index.md", "CITATION.cff", "LICENSE"):
            file = root / f
            if file.is_file() and ("REPLACE" in file.read_text(encoding="utf-8") or "NOT CONFIGURED" in file.read_text(encoding="utf-8")):
                issues.append(f"Unresolved template text: {f}")

    return sorted(set(issues))


def main(argv: list[str] | None = None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument("--phase",choices=("scaffold","publish"),default="scaffold")
    p.add_argument("--repo-visibility", choices=("unknown", "private", "public"),
                   default="unknown", help="Actual visibility established outside this repository")
    p.add_argument("--repo-full-name",default=None,
                   help="Trusted repository identity (GitHub Actions: GITHUB_REPOSITORY)")
    a=p.parse_args(argv)
    issues=validate(a.root,a.phase,verified_repository=a.repo_full_name)
    if a.repo_visibility != "unknown":
        import json
        try:
            meta=json.loads((a.root / "program.json").read_text(encoding="utf-8"))
            declared = meta.get("repository_visibility")
            is_empty_template = (
                declared == "unconfigured"
                and meta.get("programme") == "arc-REPLACE"
                and json.loads((a.root / "portfolio/projects.json").read_text(
                    encoding="utf-8")).get("projects") == []
            )
            if declared != a.repo_visibility and not is_empty_template:
                issues.append("Declared visibility disagrees with verified repository visibility")
        except (OSError, ValueError, TypeError, AttributeError):
            issues.append("Cannot independently check declared visibility")
    for issue in issues: print("FAIL:",issue)
    print(f"arc-program-contract: {'FAIL' if issues else 'PASS'}; phase={a.phase}; findings={len(issues)}")
    return 1 if issues else 0

if __name__=="__main__": sys.exit(main())
