"""Apply or check optional, explicitly approved ARC header logo in MkDocs."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGO_EXTENSIONS = (".png", ".webp", ".jpg", ".jpeg")


def approved_logo(root: Path, policy: dict, stem: str) -> str | None:
    """Find a local logo only when its bytes have been approved for public Pages."""
    directory = root / "pages"
    candidates = [stem + ext for ext in LOGO_EXTENSIONS
                  if (directory / (stem + ext)).exists()
                  or (directory / (stem + ext)).is_symlink()]
    if len(candidates) > 1:
        raise ValueError("Multiple logo formats for: " + stem)
    if not candidates:
        return None
    relative = candidates[0]
    file = directory / relative
    if (file.is_symlink() or not file.is_file() or
            relative not in policy.get("public_files", []) or
            not isinstance(policy.get("approved_image_sha256"), dict)):
        raise ValueError("Unapproved public logo: " + relative)
    approved = policy["approved_image_sha256"].get(relative)
    if not isinstance(approved, str) or hashlib.sha256(file.read_bytes()).hexdigest() != approved:
        raise ValueError("Logo SHA-256 mismatch: " + relative)
    return relative


def expected_config(root: Path) -> tuple[str, str | None]:
    policy = json.loads((root / "config/pages-policy.json").read_text(encoding="utf-8"))
    logo = approved_logo(root, policy, "assets/brand/logo")
    current = (root / "mkdocs.yml").read_text(encoding="utf-8")
    if not re.search(r"(?m)^  highlightjs: false$", current):
        raise ValueError("Unsupported MkDocs theme configuration")
    # Only one local image may be used. Never load URLs or external resources.
    without_logo = re.sub(r"(?m)^  logo: [^\n]+\n", "", current)
    if logo is None:
        return without_logo, None
    return without_logo.replace("  highlightjs: false\n",
                                "  highlightjs: false\n  logo: " + logo + "\n", 1), logo


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--apply", action="store_true",
                        help="Update mkdocs.yml after the approved image is committed")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        expected, logo = expected_config(root)
        config = root / "mkdocs.yml"
        current = config.read_text(encoding="utf-8")
        if current != expected:
            if not args.apply:
                print("BRANDING_OUT_OF_SYNC: mkdocs.yml; run --apply after image approval")
                return 1
            config.write_text(expected, encoding="utf-8")
        print("BRANDING_OK: " + (logo or "text-only header"))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("BRANDING_BLOCKED: " + str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
