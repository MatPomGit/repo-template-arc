"""Read-only registry location adapter for incremental ARC layout migration."""
from pathlib import Path
import json

# Transitional local snapshots; authoritative scientific records will remain
# with manuscripts, and portfolio aggregation belongs to the central registry.
LOCATIONS = {
    "areas": ("areas/index.json", "docs/metadata/areas.json"),
    "projects": ("portfolio/projects.json", "docs/metadata/projects.json"),
    "papers": ("portfolio/papers.json", "docs/metadata/papers.json"),
    "dependencies": ("portfolio/dependencies.json", "docs/metadata/dependencies.json"),
}


def registry_path(root: Path, key: str) -> Path:
    """Resolve exactly one existing registry, rejecting ambiguous layouts."""
    root = root.absolute()
    legacy, candidate = (root / p for p in LOCATIONS[key])
    for path in (legacy, candidate):
        for part in (path, *path.parents):
            if part == root:
                break
            if part.is_symlink():
                raise ValueError(f"Unsafe registry path: {path}")
        if path.exists() and not path.is_file():
            raise ValueError(f"Not a regular registry file: {path}")
    present = [p for p in (legacy, candidate) if p.is_file()]
    if len(present) != 1:
        raise ValueError(f"Expected exactly one registry for {key}; found {len(present)}")
    return present[0]


def read_registry(root: Path, key: str) -> dict:
    value = json.loads(registry_path(root, key).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Registry {key} must be a JSON object")
    return value
