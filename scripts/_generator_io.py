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
    """Stage changes, then replace targets; restore files on ordinary write failures.

    Multiple os.replace calls cannot be crash-atomic. Failed rollback is reported.
    """
    import stat

    root = root.absolute()
    new = new or set()
    if not new.issubset(updates):
        raise ValueError("New files must belong to the write batch")
    before: dict[Path, bytes | None] = {}
    modes: dict[Path, int] = {}
    for path in updates:
        safe_target(root, path)
        if path in new and path.exists():
            raise FileExistsError(str(path))
        before[path] = path.read_bytes() if path.exists() else None
        if path.exists():
            modes[path] = stat.S_IMODE(path.stat().st_mode)

    staged: dict[Path, Path] = {}
    backups: dict[Path, Path] = {}
    written: list[Path] = []
    created_dirs: list[Path] = []
    try:
        for path, value in updates.items():
            # Create missing directories individually so failed writes can clean them.
            parent = root
            for part in path.parent.relative_to(root).parts:
                parent = parent / part
                if not parent.exists():
                    parent.mkdir()
                    created_dirs.append(parent)
            safe_target(root, path)
            with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", dir=path.parent,
                prefix=".arc-stage-", delete=False
            ) as handle:
                staged[path] = Path(handle.name)
                handle.write(value)
                handle.flush()
                os.fsync(handle.fileno())
            if before[path] is not None:
                os.chmod(staged[path], modes[path])
                with tempfile.NamedTemporaryFile(
                    "wb", dir=path.parent, prefix=".arc-restore-", delete=False
                ) as backup:
                    backups[path] = Path(backup.name)
                    backup.write(before[path])
                    backup.flush()
                    os.fsync(backup.fileno())
                os.chmod(backups[path], modes[path])

        for path, tmp in staged.items():
            safe_target(root, path)
            os.replace(tmp, path)
            written.append(path)
    except Exception as failure:
        restore_errors = []
        for path in reversed(written):
            try:
                if before[path] is None:
                    path.unlink(missing_ok=True)
                else:
                    os.replace(backups[path], path)
            except OSError as exc:
                restore_errors.append(f"{path}: {type(exc).__name__}")
        if restore_errors:
            raise RuntimeError("ROLLBACK_INCOMPLETE: " + ", ".join(restore_errors)) from failure
        raise
    finally:
        for temp in [*staged.values(), *backups.values()]:
            temp.unlink(missing_ok=True)
        for folder in reversed(created_dirs):
            try:
                folder.rmdir()
            except OSError:
                pass
