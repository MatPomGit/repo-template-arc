"""Offline file-writing helpers for deterministic ARC generators."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path


def safe_target(root: Path, target: Path) -> None:
    root = root.absolute()
    target = target.absolute()
    if root.is_symlink() or not target.is_relative_to(root) or target == root:
        raise ValueError("Path outside repository")
    current = root
    for part in target.relative_to(root).parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("Symlink in path")
    if target.exists() and not target.is_file():
        raise ValueError("Destination is not a regular file")


def write_batch(root: Path, updates: dict[Path, str], new: set[Path] | None = None) -> None:
    new = new or set()
    before: dict[Path, bytes | None] = {}
    for path in updates:
        safe_target(root, path)
        if path in new and path.exists():
            raise FileExistsError(str(path))
        before[path] = path.read_bytes() if path.exists() else None
    stage: dict[Path, Path] = {}
    written: list[Path] = []
    try:
        for path, value in updates.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                             prefix=".arc-stage-", delete=False) as handle:
                handle.write(value)
                stage[path] = Path(handle.name)
        for path, tmp in stage.items():
            os.replace(tmp, path)
            written.append(path)
    except Exception:
        for path in reversed(written):
            old = before[path]
            if old is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(old)
        raise
    finally:
        for tmp in stage.values():
            tmp.unlink(missing_ok=True)
