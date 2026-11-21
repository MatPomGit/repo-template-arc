"""Basic integrity tests for ARC agent workflow and separation of research records."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AgentGovernanceTests(unittest.TestCase):
    def test_contract_and_workflow_present(self):
        contract = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        workflow = (ROOT / ".github/AGENT_WORKFLOW.md").read_text(encoding="utf-8")
        for item in ("R0", "R1", "R2", "R3", "DoR", "DoD", "exact",
                     "Research Autopilot", "pages/"):
            with self.subTest(item=item):
                self.assertIn(item.lower(), (contract + workflow).lower())

    def test_no_contribution_guide_and_no_public_agent_docs(self):
        self.assertFalse((ROOT / "CONTRIBUTING.md").exists())
        self.assertFalse((ROOT / "pages/AGENTS.md").exists())
        self.assertFalse((ROOT / "pages/CONTRIBUTING.md").exists())

    def test_hybrid_ownership_documentation_guardrails(self):
        documents = {
            "portfolio/README.md": ("local", "external"),
            "REPRODUCIBILITY.md": ("local", "external"),
            "docs/data-policy.md": ("local", "external", "publicznym ARC"),
            "docs/releases.md": ("local", "external", "manuskrypt"),
            "docs/adr/0003-hybrid-arc-ownership.md": ("local", "external", "v2"),
        }
        for path, phrases in documents.items():
            with self.subTest(path=path):
                content = (ROOT / path).read_text(encoding="utf-8")
                for phrase in phrases:
                    self.assertIn(phrase, content)

    def test_canonical_research_registries_preserved(self):
        for name in ("portfolio/projects.json", "portfolio/papers.json",
                     "portfolio/dependencies.json", "areas/index.json"):
            with self.subTest(name=name):
                self.assertTrue((ROOT / name).is_file())


if __name__ == "__main__":
    unittest.main()
