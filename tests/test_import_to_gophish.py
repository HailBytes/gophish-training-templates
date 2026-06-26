import json
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path

from _loader import load_tool, TOOLS

imp = load_tool("import_to_gophish")


class PureHelpers(unittest.TestCase):
    def test_is_education_file(self):
        self.assertTrue(imp.is_education_file(Path("it-security/education/x.html")))
        self.assertFalse(imp.is_education_file(Path("it-security/x.html")))

    def test_is_landing_page(self):
        self.assertTrue(imp.is_landing_page(Path("landing-pages/x.html")))
        self.assertFalse(imp.is_landing_page(Path("it-security/x.html")))

    def test_make_template_name(self):
        root = Path("/repo")
        name = imp.make_template_name(root / "it-security" / "email_issues.html", root)
        self.assertEqual(name, "It Security — Email Issues")

    def test_process_html_strips(self):
        self.assertEqual(imp.process_html_for_gophish("  <p>x</p>\n"), "<p>x</p>")


class DiscoveryAndMetadata(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "it-security" / "education").mkdir(parents=True)
        (self.root / "landing-pages").mkdir()
        (self.root / "it-security" / "phish.html").write_text("<html></html>")
        (self.root / "it-security" / "education" / "edu.html").write_text("<html></html>")
        (self.root / "landing-pages" / "lp.html").write_text("<html></html>")
        (self.root / "it-security" / "metadata.json").write_text(json.dumps({
            "templates": [{"filename": "phish.html",
                           "suggested_subject_lines": ["Urgent: verify"]}]
        }))

    def tearDown(self):
        self.tmp.cleanup()

    def test_discover_excludes_education_and_landing(self):
        found = imp.discover_templates(self.root)
        names = [p.name for p in found]
        self.assertIn("phish.html", names)
        self.assertNotIn("edu.html", names)
        self.assertNotIn("lp.html", names)

    def test_discover_category_filter(self):
        self.assertEqual(imp.discover_templates(self.root, category="nonexistent"), [])
        self.assertEqual(len(imp.discover_templates(self.root, category="it-security")), 1)

    def test_load_metadata_subject(self):
        subj = imp.load_metadata_subject(self.root / "it-security" / "phish.html")
        self.assertEqual(subj, "Urgent: verify")

    def test_load_metadata_subject_missing(self):
        self.assertIsNone(imp.load_metadata_subject(self.root / "it-security" / "education" / "edu.html"))


class NoExternalDependencies(unittest.TestCase):
    """PR #32: the importer must rely on the standard library only."""

    def test_no_requests_import_in_source(self):
        src = (TOOLS / "import_to_gophish.py").read_text()
        self.assertNotIn("import requests", src)

    def test_help_runs_without_third_party_packages(self):
        proc = subprocess.run(
            [sys.executable, str(TOOLS / "import_to_gophish.py"), "--help"],
            capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("usage", proc.stdout.lower())


if __name__ == "__main__":
    unittest.main()
