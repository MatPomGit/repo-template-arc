"""Static, fail-closed source allowlist for public ARC GitHub Pages (stdlib only).

Does not publish content, inspect remote Pages settings or certify privacy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_EXT = {".md", ".html", ".css", ".js", ".svg", ".png", ".jpg",
               ".jpeg", ".webp", ".avif", ".ico"}
TEXT_EXT = {".md", ".html", ".css", ".js", ".svg"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".avif", ".ico"}
UNSAFE_SEGMENTS = {"docs", "research", "manuscripts", "software",
                   "portfolio", "areas", "data", "results", "equipment",
                   "secrets", "credentials", "private", "raw", "students",
                   "participants", "agents.md", "contributing.md", "internal"}
BANNED = (
    re.compile(r"\b(?:AGENTS\.md|AGENT_WORKFLOW|CONTRIBUTING(?:\.md)?)\b", re.I),
    re.compile(r"\b(?:TODO|FIXME|REPLACE(?:_[A-Z0-9_]+)?|PLACEHOLDER|TBD|"
               r"NOT_RUN|NOT_VERIFIED|NOT_CONFIGURED|NOT_ASSESSED|NOT_COLLECTED)\b", re.I),
    re.compile(r"(?:instrukcj\w*\s+dla\s+agent\w*|poleceni\w*\s+dla\s+agent\w*|"
               r"dla\s+agenta\s*:|agent\s*:\s*(?:wykonaj|zmień|dodaj|popraw|sprawdź)|"
               r"agent instructions|system prompt|developer instructions)", re.I),
    re.compile(r"(?:uwagi?\s+redakcyjne|notatk\w*\s+(?:dla\s+)?(?:autora|redaktora)|"
               r"editorial notes?|notes? to (?:author|editor)|"
               r"przed publikacją|do uzupełnienia|wstaw tutaj)", re.I),
    re.compile(r"(?:jak\s+(?:pomóc|wspierać)\s+(?:projekt|repozytorium)|"
               r"how to contribute|contributing guidelines|"
               r"contribute to (?:this|the) (?:project|repository)|"
               r"send (?:a )?pull request)", re.I),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    re.compile(r"(?<![A-Za-z0-9])gh[pousr]_[A-Za-z0-9_]{36,}(?![A-Za-z0-9_])"),
    re.compile(r"(?<![A-Za-z0-9])AKIA[0-9A-Z]{16}(?![0-9A-Z])"),
    re.compile(r"\b(?:asystenc\w*\s+AI|ChatGPT|Copilot|AI\s+agent|AI\s+assistant)\b"
               r"\s*[,;:-]?\s*(?:wykonaj|zmień|popraw|zaktualizuj|usuń|dodaj|napisz|"
               r"create|update|ignore|rewrite|remove|edit|write)\b", re.I),
    re.compile(r"<\s*/?\s*(?:script|iframe|object|embed|form|meta|base)\b|"
               r"\bon[a-z]+\s*=|\b(?:javascript|vbscript)\s*:", re.I),
)


def safe_relative(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value or "\0" in value:
        return False
    if value.startswith(("/", "./")) or "//" in value:
        return False
    parts = PurePosixPath(value).parts
    return bool(parts) and all(
        item not in {".", "..", ""} and not item.startswith(".")
        and item.lower() not in UNSAFE_SEGMENTS for item in parts
    ) and PurePosixPath(value).suffix.lower() in ALLOWED_EXT


def parse_mkdocs(text: str) -> tuple[dict[str, str], list[str], list[str]]:
    """Only a transparent, offline MkDocs configuration is supported."""
    keys: dict[str, str] = {}
    navigation: list[str] = []
    errors: list[str] = []
    mode = ""
    theme: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        top = re.fullmatch(r"([a-z_]+):\s*(.*?)\s*", line)
        if top:
            key, value = top.groups()
            if key not in {"site_name", "docs_dir", "site_dir", "nav", "theme"} or key in keys:
                errors.append("PAGES CONFIG: unreviewed or duplicate config key")
            else:
                keys[key] = value.strip("\"'")
            mode = key if key in {"nav", "theme"} else ""
            continue
        if mode == "nav":
            item = re.fullmatch(r"  - [^:]+:\s*([A-Za-z0-9_./-]+\.md)\s*", line)
            if item:
                navigation.append(item.group(1))
                continue
        if mode == "theme":
            field = re.fullmatch(r"  (name|highlightjs|logo):\s*([A-Za-z0-9_./-]+)\s*", line)
            if field and field.group(1) not in theme:
                theme[field.group(1)] = field.group(2)
                continue
        errors.append("PAGES CONFIG: unreviewed YAML content")
    if keys.get("docs_dir") != "pages" or keys.get("site_dir") != "site":
        errors.append("PAGES CONFIG: isolated docs_dir/pages and site_dir/site required")
    if not keys.get("site_name") or "nav" not in keys or not navigation:
        errors.append("PAGES CONFIG: site name or navigation missing")
    base_theme = {key: value for key, value in theme.items() if key != "logo"}
    if keys.get("theme") != "" or base_theme != {"name": "mkdocs", "highlightjs": "false"}:
        errors.append("PAGES CONFIG: approved offline theme required")
    return keys, navigation, errors



def check_pages(root: Path = ROOT) -> list[str]:
    root = Path(root).resolve()
    errors: list[str] = []
    try:
        data = json.loads((root / "config/pages-policy.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return ["PAGES POLICY: missing or malformed JSON"]
    if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        return ["PAGES POLICY: unsupported schema_version"]
    if (data.get("source_dir"), data.get("output_dir"),
            data.get("mkdocs_config")) != ("pages", "site", "mkdocs.yml"):
        errors.append("PAGES POLICY: source, output and MkDocs paths must remain isolated")
    allowed = data.get("public_files")
    if not isinstance(allowed, list) or not allowed or any(not safe_relative(x) for x in allowed):
        return sorted(set(errors + ["PAGES POLICY: unsafe public file allowlist"]))
    if len(allowed) != len(set(allowed)) or "index.md" not in allowed or "projects.md" not in allowed:
        errors.append("PAGES POLICY: duplicate or missing index")
    approved_theme = data.get("approved_theme_assets")
    approved_images = data.get("approved_image_sha256")
    if (not isinstance(approved_theme, dict) or not approved_theme or
            not isinstance(approved_images, dict) or
            any(not isinstance(k, str) or not isinstance(v, str) or
                not re.fullmatch(r"[0-9a-f]{64}", v)
                for k, v in approved_theme.items()) or
            any(not isinstance(k, str) or k not in allowed or
                PurePosixPath(k).suffix.lower() not in IMAGE_EXT or
                not isinstance(v, str) or not re.fullmatch(r"[0-9a-f]{64}", v)
                for k, v in approved_images.items())):
        return sorted(set(errors + ["PAGES POLICY: invalid approved asset hashes"]))
    try:
        config = (root / "mkdocs.yml").read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return sorted(set(errors + ["PAGES CONFIG: missing or unreadable mkdocs.yml"]))
    _, nav, config_errors = parse_mkdocs(config)
    errors.extend(config_errors)
    logo_candidates = [
        "assets/brand/logo" + ext for ext in (".png", ".webp", ".jpg", ".jpeg")
        if (root / "pages" / ("assets/brand/logo" + ext)).exists()
        or (root / "pages" / ("assets/brand/logo" + ext)).is_symlink()
    ]
    if len(logo_candidates) > 1:
        errors.append("PAGES LOGO: multiple programme logo formats")
    expected_logo = logo_candidates[0] if len(logo_candidates) == 1 else None
    if expected_logo:
        logo_file = root / "pages" / expected_logo
        if (logo_file.is_symlink() or not logo_file.is_file() or
                expected_logo not in allowed or
                hashlib.sha256(logo_file.read_bytes()).hexdigest() !=
                approved_images.get(expected_logo)):
            errors.append("PAGES LOGO: missing approval or incorrect SHA")
    configured_logo = re.search(r"(?m)^  logo:\s*([^\n]+)\s*$", config)
    actual_logo = configured_logo.group(1).strip() if configured_logo else None
    if actual_logo != expected_logo:
        errors.append("PAGES LOGO: MkDocs header must match approved local logo")
    if not nav or "index.md" not in nav or any(x not in allowed for x in nav):
        errors.append("PAGES CONFIG: navigation contains unapproved source")

    folder = root / "pages"
    if not folder.is_dir() or folder.is_symlink():
        return sorted(set(errors + ["PAGES SOURCE: missing or unsafe directory"]))
    for file in sorted(folder.rglob("*")):
        rel = file.relative_to(folder).as_posix()
        if file.is_symlink():
            errors.append("PAGES SYMLINK: " + rel)
            continue
        if file.is_dir():
            continue
        if not file.is_file():
            errors.append("PAGES UNSUPPORTED: " + rel)
            continue
        if not safe_relative(rel) or rel not in allowed:
            errors.append("PAGES NOT APPROVED: " + rel)
            continue
        try:
            if not file.resolve(strict=True).is_relative_to(folder):
                errors.append("PAGES OUTSIDE SOURCE: " + rel)
                continue
            if file.stat().st_size > 2_000_000:
                errors.append("PAGES TOO LARGE: " + rel)
                continue
            if file.suffix.lower() in IMAGE_EXT:
                body = file.read_bytes()
                if hashlib.sha256(body).hexdigest() != approved_images.get(rel):
                    errors.append("PAGES IMAGE HASH UNAPPROVED: " + rel)
                # A conservative screen; EXIF/XMP/IPTC still require manual review.
                if (file.suffix.lower() != ".ico" and
                        any(marker in body for marker in
                            (b"Exif\x00\x00", b"eXIf", b"XMP_", b"<x:xmpmeta",
                             b"http://ns.adobe.com/xap/1.0/", b"tEXt", b"iTXt", b"zTXt"))):
                    errors.append("PAGES IMAGE METADATA: " + rel)
            if file.suffix.lower() in TEXT_EXT:
                content = file.read_text(encoding="utf-8")
                if any(regex.search(content) for regex in BANNED):
                    errors.append("PAGES EDITORIAL OR AGENT CONTENT: " + rel)
                if re.search(r"\.\./|file://|https?://\S*(?:/AGENTS\.md|/\.github/|/research/|/docs/)",
                             content, re.I):
                    errors.append("PAGES INTERNAL REFERENCE: " + rel)
        except (OSError, UnicodeError):
            errors.append("PAGES UNREADABLE: " + rel)
    for rel in allowed:
        file = folder / rel
        if not file.is_file() or file.is_symlink():
            errors.append("PAGES MISSING APPROVED FILE: " + rel)
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = check_pages(args.root)
    for error in errors:
        print("FAIL:", error)
    print("arc-pages:", "FAIL" if errors else "PASS")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
