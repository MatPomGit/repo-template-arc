"""Generate a deliberately minimal public Pages index from explicit opt-in entries."""
from __future__ import annotations
import html
import json
import re
import sys
from pathlib import Path
from validate_repository import safe_public_page_url
from site_branding import approved_logo


def safe_text(text:str)->str:
    return re.sub(r"[\[\]<>|\n\r]", " ", text).strip()


def render(root:Path)->str:
    projects=json.loads((root/"portfolio/projects.json").read_text(encoding="utf-8")).get("projects",[])
    policy_file=root/"config/pages-policy.json"
    policy=(json.loads(policy_file.read_text(encoding="utf-8")) if policy_file.is_file()
            else {"public_files": [], "approved_image_sha256": {}})
    public=[]
    for p in projects:
        if p.get("visibility")!="public" or p.get("public_listing") is not True:
            continue
        url=p.get("pages_url")
        if not safe_public_page_url(url):
            continue
        name=safe_text(str(p.get("title","Projekt")))
        ident=p.get("id")
        logo=None
        if isinstance(ident,str) and re.fullmatch(r"[a-z][a-z0-9-]{2,63}",ident):
            logo=approved_logo(root,policy,"assets/projects/"+ident)
        public.append((name,url,logo))
    lines=["# Publiczne projekty", "", "Ten katalog obejmuje wyłącznie projekty zatwierdzone do publikacji przez właściciela.",""]
    if not public:
        lines += ["Brak zatwierdzonych wpisów publicznych.",""]
    else:
        for title,url,logo in sorted(public):
            if logo:
                # Locally reviewed image; no remote logo retrieval.
                alt=html.escape("Logo projektu "+title,quote=True)
                lines.append(f'- <img src="{logo}" alt="{alt}" width="48" height="48" loading="lazy"> [{title}]({url})')
            else:
                lines.append(f"- [{title}]({url})")
        lines.append("")
    lines += ["Informacje o badaniach i wynikach znajdują się w kanonicznych repozytoriach projektów. Nie publikuje się tutaj danych uczestników.",""]
    return "\n".join(lines)


def write_catalog(root:Path)->Path:
    """Write only the explicitly allowlisted public project catalog."""
    root=Path(root).resolve()
    path=root/"pages/projects.md"
    if path.is_symlink() or not path.parent.is_dir() or path.parent.is_symlink():
        raise SystemExit("UNAVAILABLE: public pages directory unsafe or missing")
    policy=json.loads((root/"config/pages-policy.json").read_text(encoding="utf-8"))
    if policy.get("public_files") is None or "projects.md" not in policy["public_files"]:
        raise SystemExit("UNAVAILABLE: projects.md not allowlisted for publication")
    path.write_text(render(root),encoding="utf-8")
    return path


def main(argv:list[str]|None=None)->int:
    root=Path(__file__).resolve().parents[1]
    path=write_catalog(root)
    print("Public catalog generated:", path.relative_to(root))
    print("Private projects excluded; publication NOT_RUN")
    return 0

if __name__=="__main__": sys.exit(main())
