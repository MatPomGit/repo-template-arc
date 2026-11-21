"""Generate reviewed public article listing, without publishing or remote access."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

from validate_repository import github_repo_url, safe_public_page_url
from validate_pages import BANNED

ID = re.compile(r"^MSC-[A-Z0-9]+(?:-[A-Z0-9]+)*$")
STAGES = {"concept","protocol","preregistered","collection","analysis",
          "draft","submitted","accepted","published","archived","withdrawn"}


def clean(value: object, ident: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 320:
        raise ValueError("Missing or invalid public text: " + ident)
    if any(regex.search(value) for regex in BANNED):
        raise ValueError("Unsafe public text: " + ident)
    if any(ord(char) < 32 for char in value):
        raise ValueError("Control characters in public text: " + ident)
    return re.sub(r"([\\*_{}\[\]()!<>|\x60])", r"\\\1", value.strip())


def render(root: Path) -> str:
    program=json.loads((root/"program.json").read_text(encoding="utf-8"))
    papers=json.loads((root/"portfolio/papers.json").read_text(encoding="utf-8"))
    projects=json.loads((root/"portfolio/projects.json").read_text(encoding="utf-8"))
    lines=["# Artykuły naukowe","",
           "Publikacje i planowane badania prowadzone w programie.",""]
    if papers.get("schema_version")!=2 or program.get("repository_visibility")!="public":
        return "\n".join(lines+["Brak zatwierdzonych artykułów do prezentacji.",""])
    public_projects={x.get("id"):x for x in projects.get("projects",[])
                     if isinstance(x,dict) and x.get("visibility")=="public"}
    records=[]
    for paper in papers.get("papers",[]):
        if not isinstance(paper,dict) or paper.get("public_listing") is not True:
            continue
        ident=paper.get("id")
        if not isinstance(ident,str) or not ID.fullmatch(ident):
            raise ValueError("Invalid public MSC identifier")
        owner=paper.get("owner")
        if not isinstance(owner,dict):
            raise ValueError("Invalid public owner: "+ident)
        repository=owner.get("repository")
        if not isinstance(repository,str):
            raise ValueError("Missing public repository: "+ident)
        repo_url="https://github.com/"+repository
        if not github_repo_url(repository,repo_url):
            raise ValueError("Untrusted public repository: "+ident)
        if owner.get("mode")=="local":
            if repository!=program.get("repository_full_name"):
                raise ValueError("Local owner mismatch: "+ident)
        elif owner.get("mode")=="external":
            project=public_projects.get(owner.get("project_id"))
            if not project or project.get("repository")!=repository:
                raise ValueError("No public canonical external source: "+ident)
        else:
            raise ValueError("Unknown public ownership: "+ident)
        stage=paper.get("publication_stage")
        if stage not in STAGES:
            raise ValueError("Unknown publication stage: "+ident)
        title=clean(paper.get("title"),ident)
        summary=clean(paper.get("public_summary"),ident)
        link=paper.get("publication_url")
        if not safe_public_page_url(link):
            link=repo_url
        records.append((ident, "- **"+ident+" — "+title+"**. "+summary+
                        " Etap: "+stage+". [Źródło]("+link+")"))
    if records:
        lines.extend(text for _,text in sorted(records))
        lines.append("")
    else:
        lines.extend(["Brak zatwierdzonych artykułów do prezentacji.",""])
    return "\n".join(lines)


def write_catalog(root: Path) -> Path:
    root=Path(root).resolve()
    target=root/"pages/articles.md"
    policy=json.loads((root/"config/pages-policy.json").read_text(encoding="utf-8"))
    if (target.is_symlink() or not target.parent.is_dir() or
            target.parent.is_symlink() or "articles.md" not in policy.get("public_files",[])):
        raise ValueError("Article page not explicitly allowlisted")
    target.write_text(render(root),encoding="utf-8")
    return target


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    args=parser.parse_args(argv)
    try:
        path=write_catalog(args.root)
    except (OSError,ValueError,KeyError,TypeError) as error:
        parser.exit(2,"ARTICLE CATALOG BLOCKED: "+str(error)+"\n")
    print("Article catalog generated:",path)
    print("Deployment: NOT_RUN")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
