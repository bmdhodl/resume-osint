"""Behavior of the checks in scripts/sync_skill.py. No network."""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import sync_skill  # noqa: E402

GOOD_SKILL = "---\nname: resume-osint\ndescription: Check a resume against public sources.\n---\n\n# Resume OSINT\n"


class FrontmatterTest(unittest.TestCase):
    def test_accepts_name_and_description(self):
        self.assertEqual(sync_skill.frontmatter_problems(GOOD_SKILL), [])

    def test_the_committed_skill_passes(self):
        self.assertEqual(sync_skill.frontmatter_problems(sync_skill.SKILL_PATH.read_text("utf-8")), [])

    def test_rejects_an_extra_key(self):
        skill = GOOD_SKILL.replace("---\n\n", "license: MIT\n---\n\n")
        self.assertIn("name and description only", " ".join(sync_skill.frontmatter_problems(skill)))

    def test_rejects_a_description_codex_would_refuse(self):
        skill = GOOD_SKILL.replace("Check a resume against public sources.", "x" * 501)
        self.assertIn("Codex allows 500", " ".join(sync_skill.frontmatter_problems(skill)))

    def test_rejects_a_description_that_is_not_plain_yaml(self):
        skill = GOOD_SKILL.replace("Check a resume", "Note: check a resume")
        self.assertIn("plain YAML", " ".join(sync_skill.frontmatter_problems(skill)))

    def test_rejects_a_file_without_frontmatter(self):
        self.assertTrue(sync_skill.frontmatter_problems("# Resume OSINT\n"))


class DriftTest(unittest.TestCase):
    def test_identical_bytes_pass(self):
        self.assertEqual(sync_skill.drift_problems(b"same\n", b"same\n"), [])

    def test_a_line_ending_change_fails(self):
        problems = sync_skill.drift_problems(b"line\r\n", b"line\n")
        self.assertIn("python scripts/sync_skill.py", problems[0])


class ManifestTest(unittest.TestCase):
    def committed(self):
        plugin = json.loads(sync_skill.PLUGIN_PATH.read_text("utf-8"))
        marketplace = json.loads(sync_skill.MARKETPLACE_PATH.read_text("utf-8"))
        return plugin, marketplace

    def test_the_committed_manifests_pass(self):
        self.assertEqual(sync_skill.manifest_problems(*self.committed()), [])

    def test_a_pinned_version_fails(self):
        plugin, marketplace = self.committed()
        plugin["version"] = "1.0.0"
        self.assertIn("follow new commits", " ".join(sync_skill.manifest_problems(plugin, marketplace)))

    def test_mismatched_names_fail(self):
        plugin, marketplace = self.committed()
        marketplace["plugins"][0]["name"] = "resume-check"
        self.assertIn("must both be", " ".join(sync_skill.manifest_problems(plugin, marketplace)))


if __name__ == "__main__":
    unittest.main()
