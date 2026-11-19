"""Generate a deliberately minimal public Pages index from explicit opt-in entries."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path
from validate_repository import safe_public_page_url


def safe_text(text:str)->str:
    return re.sub(r"[\[\]<>|\n\r]", " ", text).strip()


def render(root:Path)->str:
    projects=json.loads((root/"portfolio/projects.json").read_text(encoding="utf-8")).get("projects",[])
    public=[]
    for p in projects:
        if p.get("visibility")!="public" or p.get("public_listing") is not True:
            continue
        url=p.get("pages_url")
        if not safe_public_page_url(url):
            continue
        public.append((safe_text(str(p.get("title","Projekt"))),url))
    lines=["# Publiczne projekty", "", "Ten katalog obejmuje wyłącznie projekty zatwierdzone do publikacji przez właściciela.",""]
    if not public:
        lines += ["Brak zatwierdzonych wpisów publicznych.",""]
    else:
        for title,url in sorted(public):
            lines.append(f"- [{title}]({url})")
        lines.append("")
    lines += ["Informacje o badaniach i wynikach znajdują się w kanonicznych repozytoriach projektów. Nie publikuje się tutaj danych uczestników.",""]
    return "\n".join(lines)


def main(argv:list[str]|None=None)->int:
    root=Path(__file__).resolve().parents[1]
    path=root/"docs/projects.md"
    path.write_text(render(root),encoding="utf-8")
    print("Public project catalog generated; private projects excluded")
    return 0

if __name__=="__main__": sys.exit(main())
