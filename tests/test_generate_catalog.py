import json
import tempfile
import unittest
from pathlib import Path

from _loader import load_tool

gc = load_tool("generate_catalog")


def write_metadata(root, category, data, filename="metadata.json"):
    d = root / category
    d.mkdir(parents=True, exist_ok=True)
    (d / filename).write_text(json.dumps(data))


class LoadCategories(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self._orig_root = gc.ROOT
        self._orig_output = gc.OUTPUT
        gc.ROOT = self.root
        gc.OUTPUT = self.root / "docs" / "CATALOG.md"

    def tearDown(self):
        gc.ROOT = self._orig_root
        gc.OUTPUT = self._orig_output
        self.tmp.cleanup()

    def test_skips_non_category_dirs(self):
        write_metadata(self.root, "tools", {"templates": []})
        write_metadata(self.root, "landing-pages", {"templates": []})
        write_metadata(self.root, "it-security", {"templates": []})
        names = [name for name, _ in gc.load_categories()]
        self.assertEqual(names, ["it-security"])

    def test_skips_invalid_json_with_warning(self):
        d = self.root / "broken"
        d.mkdir()
        (d / "metadata.json").write_text("{not valid json")
        write_metadata(self.root, "it-security", {"templates": []})
        names = [name for name, _ in gc.load_categories()]
        self.assertEqual(names, ["it-security"])

    def test_sorted_by_directory_name(self):
        write_metadata(self.root, "zebra", {"templates": []})
        write_metadata(self.root, "alpha", {"templates": []})
        names = [name for name, _ in gc.load_categories()]
        self.assertEqual(names, ["alpha", "zebra"])


class Render(unittest.TestCase):
    def test_summary_counts_templates_and_categories(self):
        categories = [
            ("it-security", {"templates": [{"name": "A"}, {"name": "B"}]}),
            ("financial", {"templates": [{"name": "C"}]}),
        ]
        out = gc.render(categories)
        self.assertIn("**Templates:** 3", out)
        self.assertIn("**Categories:** 2", out)

    def test_last_updated_is_max_across_categories(self):
        categories = [
            ("a", {"templates": [], "last_updated": "2026-01-01"}),
            ("b", {"templates": [], "last_updated": "2026-06-15"}),
        ]
        out = gc.render(categories)
        self.assertIn("**Most recent update:** 2026-06-15", out)

    def test_language_suffix_on_heading(self):
        categories = [
            ("latam-spanish", {"category": "LATAM Spanish", "language": "es-ES", "templates": []}),
        ]
        out = gc.render(categories)
        self.assertIn("### `latam-spanish` — LATAM Spanish (es-ES)", out)

    def test_no_language_suffix_when_absent(self):
        categories = [("it-security", {"category": "IT Security", "templates": []})]
        out = gc.render(categories)
        self.assertIn("### `it-security` — IT Security", out)
        self.assertNotIn("IT Security (", out)

    def test_missing_template_fields_render_as_dash(self):
        categories = [("it-security", {"templates": [{}]})]
        out = gc.render(categories)
        self.assertIn("| — | [`—`](it-security/—) | — | — | — | 0 |", out)

    def test_template_row_links_to_category_relative_file(self):
        categories = [("it-security", {"templates": [
            {"name": "VPN Alert", "filename": "vpn_alert.html", "attack_vector": "credential_harvest",
             "difficulty": "beginner", "estimated_click_rate": "20%",
             "suggested_subject_lines": ["Subj 1", "Subj 2"]},
        ]})]
        out = gc.render(categories)
        self.assertIn("[`vpn_alert.html`](it-security/vpn_alert.html)", out)
        self.assertIn("| VPN Alert | [`vpn_alert.html`](it-security/vpn_alert.html) "
                       "| credential_harvest | beginner | 20% | 2 |", out)

    def test_empty_categories_render_summary_with_no_recent_update(self):
        out = gc.render([])
        self.assertIn("**Templates:** 0", out)
        self.assertIn("**Categories:** 0", out)
        self.assertNotIn("Most recent update", out)

    def test_output_ends_with_single_trailing_newline(self):
        out = gc.render([("it-security", {"templates": []})])
        self.assertTrue(out.endswith("\n"))
        self.assertFalse(out.endswith("\n\n"))


class MainCheckMode(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self._orig_root = gc.ROOT
        self._orig_output = gc.OUTPUT
        gc.ROOT = self.root
        gc.OUTPUT = self.root / "docs" / "CATALOG.md"
        write_metadata(self.root, "it-security", {"templates": [{"name": "A", "filename": "a.html"}]})

    def tearDown(self):
        gc.ROOT = self._orig_root
        gc.OUTPUT = self._orig_output
        self.tmp.cleanup()

    def test_check_fails_when_catalog_missing(self):
        import sys
        old_argv = sys.argv
        try:
            sys.argv = ["generate_catalog.py", "--check"]
            with self.assertRaises(SystemExit) as cm:
                gc.main()
            self.assertNotEqual(cm.exception.code, 0)
        finally:
            sys.argv = old_argv

    def test_writes_and_then_check_passes(self):
        import sys
        old_argv = sys.argv
        try:
            sys.argv = ["generate_catalog.py"]
            gc.main()
            self.assertTrue(gc.OUTPUT.exists())

            sys.argv = ["generate_catalog.py", "--check"]
            gc.main()  # should not raise / exit non-zero
        finally:
            sys.argv = old_argv

    def test_check_exits_nonzero_when_stale(self):
        import sys
        gc.OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        gc.OUTPUT.write_text("stale content\n")
        old_argv = sys.argv
        try:
            sys.argv = ["generate_catalog.py", "--check"]
            with self.assertRaises(SystemExit) as cm:
                gc.main()
            self.assertNotEqual(cm.exception.code, 0)
        finally:
            sys.argv = old_argv


if __name__ == "__main__":
    unittest.main()
