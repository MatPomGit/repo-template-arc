"""Regression tests for the transitional registry layout."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from _registry_layout import LOCATIONS, read_registry, registry_path


class RegistryLayoutTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def put(self, rel, value):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_both_supported_layouts(self):
        for key, locations in LOCATIONS.items():
            for rel in locations:
                with self.subTest(key=key, rel=rel):
                    path = self.put(rel, {"schema_version": 2})
                    self.assertEqual(registry_path(self.root, key), path)
                    self.assertEqual(read_registry(self.root, key), {"schema_version": 2})
                    path.unlink()

    def test_duplicate_registry_rejected_even_when_equal(self):
        for rel in LOCATIONS["papers"]:
            self.put(rel, {"papers": []})
        with self.assertRaises(ValueError):
            read_registry(self.root, "papers")

    def test_missing_registry_rejected(self):
        with self.assertRaises(ValueError):
            read_registry(self.root, "projects")

    def test_non_object_rejected(self):
        self.put(LOCATIONS["projects"][0], [])
        with self.assertRaises(ValueError):
            read_registry(self.root, "projects")

    def test_symlink_rejected(self):
        target = self.put("target.json", {})
        path = self.root / LOCATIONS["papers"][0]
        path.parent.mkdir()
        path.symlink_to(target)
        with self.assertRaises(ValueError):
            read_registry(self.root, "papers")


if __name__ == "__main__":
    unittest.main()
