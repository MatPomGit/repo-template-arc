"""Dependency-free structural/referential validator for an ARC programme."""
from __future__ import annotations
import argparse
import configparser
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

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
    "ROADMAP.md", "CHANGELOG.md", "CONTRIBUTING.md", "SECURITY.md",
    "LICENSE", "CITATION.cff", "VERSION", "mkdocs.yml",
    "program.json", "areas/index.json", "areas/README.md",
    "portfolio/projects.json", "portfolio/papers.json",
    "portfolio/dependencies.json", "portfolio/README.md",
    "equipment/README.md", "software/README.md",
    "docs/index.md", "docs/projects.md", "docs/scientific-scope.md",
    "docs/publication-policy.md", "docs/data-policy.md", "docs/governance.md",
    "docs/submodules.md", "docs/pages.md", "docs/decisions.md",
    "scripts/validate_repository.py", "scripts/bootstrap.py",
    "scripts/build_public_catalog.py", "tests/test_repository_contract.py",
)
IDENTIFIER = re.compile(r"^[a-z][a-z0-9-]{2,63}$")
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
    """Accept a plain HTTPS URL, never embedded credentials or Markdown payloads."""
    if not isinstance(url, str) or any(c.isspace() or c in "<>[]()\\" for c in url):
        return False
    try:
        parsed = urlparse(url)
        return (parsed.scheme == "https" and parsed.hostname is not None
                and parsed.username is None and parsed.password is None
                and parsed.port is None and not parsed.query and not parsed.fragment
                and parsed.hostname.lower() not in ("localhost", "127.0.0.1"))
    except ValueError:
        return False


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


def validate(root: Path, phase: str = "scaffold") -> list[str]:
    issues: list[str] = []
    if not root.is_dir():
        return ["Missing repository root"]
    for rel in REQUIRED:
        f = root / rel
        if not f.is_file() or f.is_symlink() or not f.read_bytes().strip():
            issues.append(f"Missing or empty required regular file: {rel}")

    meta = load_json(root, "program.json", issues)
    areas = load_json(root, "areas/index.json", issues)
    projects = load_json(root, "portfolio/projects.json", issues)
    papers = load_json(root, "portfolio/papers.json", issues)
    dependencies = load_json(root, "portfolio/dependencies.json", issues)
    if meta.get("schema_version") != 1 or meta.get("type") != "arc-program":
        issues.append("Invalid program.json schema_version/type")
    if meta.get("template_version") != "1.0.0":
        issues.append("Unexpected program template version")
    programme = meta.get("programme")
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

    lines, project_ids, project_repos = set(), set(), {}
    for line in areas.get("lines", []) if isinstance(areas.get("lines"), list) else []:
        if not isinstance(line, dict) or not IDENTIFIER.fullmatch(str(line.get("id", ""))):
            issues.append("Invalid research line identifier")
            continue
        if line["id"] in lines:
            issues.append(f"Duplicated line: {line['id']}")
        lines.add(line["id"])
        if not line.get("title"):
            issues.append(f"Missing line title: {line['id']}")

    registered_projects = projects.get("projects", []) if isinstance(projects.get("projects"), list) else []
    for p in registered_projects:
        if not isinstance(p, dict):
            issues.append("Invalid project record type"); continue
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
        if p.get("public_listing"):
            if p.get("visibility") != "public":
                issues.append(f"Private project marked for public listing: {ident}")
            if not safe_public_page_url(p.get("pages_url")):
                issues.append(f"No verified public Pages URL for listed project: {ident}")
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
        if not isinstance(p, dict):
            issues.append("Invalid paper record type"); continue
        ident, owner = p.get("id", ""), p.get("owner_project_id")
        if not IDENTIFIER.fullmatch(str(ident)) or ident in paper_ids:
            issues.append(f"Invalid or duplicate paper id: {ident}")
        paper_ids.add(ident)
        if owner not in project_ids:
            issues.append(f"Unknown canonical project for paper: {ident}")
        if p.get("canonical_repository") != project_repos.get(owner):
            issues.append(f"Canonical repository mismatch for paper: {ident}")
        if p.get("stage") not in ALLOWED_STAGES:
            issues.append(f"Unknown paper stage: {ident}")
        if not isinstance(p.get("manuscript_path"), str) or ".." in p["manuscript_path"] or p["manuscript_path"].startswith("/"):
            issues.append(f"Invalid manuscript path: {ident}")

    for group in ("tools", "equipment", "datasets"):
        group_records = dependencies.get(group, []) if isinstance(dependencies.get(group), list) else []
        for p in group_records:
            if not isinstance(p, dict) or p.get("project_id") not in project_ids or not p.get("ref"):
                issues.append(f"Invalid {group} dependency reference")

    subpaths = [p.get("submodule_path") for p in registered_projects if isinstance(p, dict) and p.get("submodule_path")]
    if subpaths:
        gmod = root / ".gitmodules"
        if not gmod.is_file():
            issues.append("Submodule entries exist but .gitmodules is absent")
        else:
            text = gmod.read_text(encoding="utf-8")
            for s in subpaths:
                if not re.search(r"(?m)^\s*path\s*=\s*" + re.escape(s) + r"\s*$", text):
                    issues.append(f"Submodule missing from .gitmodules: {s}")
    if len(set(subpaths)) != len(subpaths):
        issues.append("Duplicate submodule path")
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
        for f in ("README.md", "docs/index.md", "docs/scientific-scope.md", "CITATION.cff", "LICENSE"):
            file = root / f
            if file.is_file() and ("REPLACE" in file.read_text(encoding="utf-8") or "NOT CONFIGURED" in file.read_text(encoding="utf-8")):
                issues.append(f"Unresolved template text: {f}")

    return sorted(set(issues))


def main(argv: list[str] | None = None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument("--phase",choices=("scaffold","publish"),default="scaffold")
    a=p.parse_args(argv)
    issues=validate(a.root,a.phase)
    for issue in issues: print("FAIL:",issue)
    print(f"arc-program-contract: {'FAIL' if issues else 'PASS'}; phase={a.phase}; findings={len(issues)}")
    return 1 if issues else 0

if __name__=="__main__": sys.exit(main())
