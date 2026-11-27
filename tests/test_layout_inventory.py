import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "inventory_layout", Path(__file__).resolve().parents[1] / "scripts/inventory_layout.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class LayoutInventoryTests(unittest.TestCase):
    def test_inventory_is_read_only_and_reports_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", tmp], check=True)
            (root / "portfolio").mkdir()
            (root / "portfolio/papers.json").write_text("{}", encoding="utf-8")
            (root / "reader.py").write_text('path = "portfolio/papers.json"\n', encoding="utf-8")
            (root / "untracked.py").write_text('path = "areas/index.json"\n', encoding="utf-8")
            subprocess.run(["git", "-C", tmp, "add", "portfolio", "reader.py"], check=True)
            before = subprocess.check_output(["git", "-C", tmp, "status", "--porcelain"])
            result = MODULE.inventory(root)
            self.assertEqual(result["legacy"]["portfolio"][0]["path"], "portfolio/papers.json")
            self.assertEqual(len(result["legacy"]["portfolio"][0]["sha256"]), 64)
            self.assertEqual(result["consumers"], [
                {"path": "reader.py", "line": 1, "references": ["portfolio/"]}
            ])
            self.assertEqual(result["blockers"], [])
            self.assertEqual(before, subprocess.check_output(["git", "-C", tmp, "status", "--porcelain"]))

    def test_missing_tracked_file_blocks_migration(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", tmp], check=True)
            path = root / "file.md"
            path.write_text("test", encoding="utf-8")
            subprocess.run(["git", "-C", tmp, "add", "file.md"], check=True)
            path.unlink()
            result = MODULE.inventory(root)
            self.assertEqual(result["blockers"][0]["path"], "file.md")


if __name__ == "__main__":
    unittest.main()
