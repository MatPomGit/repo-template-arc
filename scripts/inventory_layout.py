"""Read-only inventory of legacy ARC layout and path consumers."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

LEGACY = ("areas", "portfolio", "equipment", "software", "examples", "reviews")
NEEDLES = tuple(name + "/" for name in LEGACY) + ("manuscripts/",)
TEXT_SUFFIXES = {".py", ".md", ".json", ".yaml", ".yml", ".toml", ".tex", ".sh", ".cff"}


def inventory(root: Path) -> dict:
    root = root.resolve(strict=True)
    raw = subprocess.check_output(
        ["git", "-C", str(root), "ls-files", "-z", "--cached"],
        timeout=30,
    )
    files = sorted(set(raw.decode("utf-8").split("\0")) - {""})
    legacy = {name: [] for name in LEGACY}
    consumers = []
    blockers = []
    for name in files:
        path = root / name
        if not path.resolve().is_relative_to(root) or any(
            p.is_symlink() for p in (path, *path.parents) if p != root and p.is_relative_to(root)
        ):
            blockers.append({"path": name, "reason": "unsafe path"})
            continue
        if not path.is_file():
            blockers.append({"path": name, "reason": "missing or nonregular tracked file"})
            continue
        group = name.split("/", 1)[0]
        if group in legacy:
            digest = hashlib.sha256()
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(65536), b""):
                    digest.update(chunk)
            legacy[group].append({"path": name, "sha256": digest.hexdigest()})
        if path.suffix not in TEXT_SUFFIXES and path.name not in {"Makefile", "AGENTS.md"}:
            continue
        if path.stat().st_size > 2_000_000:
            blockers.append({"path": name, "reason": "text exceeds scan limit"})
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError):
            blockers.append({"path": name, "reason": "unreadable text"})
            continue
        for number, line in enumerate(lines, 1):
            matches = [needle for needle in NEEDLES if needle in line]
            if matches:
                consumers.append({"path": name, "line": number, "references": matches})
    return {"legacy": legacy, "consumers": consumers, "blockers": blockers}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    report = inventory(args.root)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return int(bool(report["blockers"]))


if __name__ == "__main__":
    raise SystemExit(main())
