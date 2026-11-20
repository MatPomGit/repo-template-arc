"""Read-only review of rendered MkDocs HTML; not proof of deployed privacy."""
from __future__ import annotations
import argparse
import re
from html.parser import HTMLParser
from pathlib import Path
from validate_pages import BANNED

INTERNAL = re.compile(r"(?:\.\./docs/|/\.github/|/AGENTS\.md|/CONTRIBUTING\.md|/research/|file://)", re.I)
SENSITIVE = {"docs","portfolio","research","equipment","private","raw","secrets"}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.references = []
    def handle_data(self, data):
        self.parts.append(data)
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {"href","src","action"} and value:
                self.references.append(value)


def check_site(site: Path) -> list[str]:
    site = Path(site).resolve()
    if not site.is_dir() or site.is_symlink():
        return ["SITE MISSING: generated site is required"]
    issues, html_count = [], 0
    for file in sorted(site.rglob("*")):
        rel = file.relative_to(site).as_posix()
        if file.is_symlink():
            issues.append("SITE SYMLINK: "+rel)
            continue
        if file.is_dir():
            continue
        if not file.is_file() or any(seg.startswith(".") or seg.lower() in SENSITIVE for seg in file.relative_to(site).parts):
            issues.append("SITE UNSAFE PATH: "+rel)
            continue
        if file.suffix.lower() == ".html":
            html_count += 1
            try:
                data = file.read_text(encoding="utf-8")
                parser = PageParser()
                parser.feed(data)
                visible = " ".join(parser.parts)
                if any(p.search(visible) for p in BANNED):
                    issues.append("SITE UNSAFE HTML TEXT: "+rel)
                if any(INTERNAL.search(url) for url in parser.references) or INTERNAL.search(data):
                    issues.append("SITE INTERNAL URL: "+rel)
            except (OSError, UnicodeError, ValueError):
                issues.append("SITE UNREADABLE HTML: "+rel)
        elif rel == "search/search_index.json":
            try:
                raw=file.read_text(encoding="utf-8")
                if any(p.search(raw) for p in BANNED):
                    issues.append("SITE UNSAFE SEARCH INDEX")
            except (OSError, UnicodeError):
                issues.append("SITE UNREADABLE SEARCH INDEX")
    if not html_count:
        issues.append("SITE EMPTY: no rendered HTML")
    if not (site/"index.html").is_file() or not (site/"projects/index.html").is_file():
        issues.append("SITE MISSING APPROVED PAGES")
    return sorted(set(issues))


def main():
    arg=argparse.ArgumentParser(description=__doc__)
    arg.add_argument("--site",type=Path,default=Path(__file__).resolve().parents[1]/"site")
    options=arg.parse_args()
    issues=check_site(options.site)
    for issue in issues:
        print("FAIL:",issue)
    print("arc-rendered-site:","FAIL" if issues else "PASS")
    return bool(issues)
if __name__=="__main__":
    raise SystemExit(main())
