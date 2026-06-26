import json
import tempfile
import unittest
from pathlib import Path

from _loader import load_tool

vt = load_tool("validate_templates")

GOOD_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Hi</title></head>
<body><a href="{{.URL}}">Click</a> {{.FirstName}} {{.Email}}
<div style="display:none">{{.Tracker}}</div></body></html>"""


def new_result():
    return vt.ValidationResult(path="test.html")


class ExternalDependencyChecks(unittest.TestCase):
    def test_external_image_is_error(self):
        r = new_result()
        vt.check_external_dependencies(
            '<img src="https://example.com/logo.png">', r, Path("x.html"))
        self.assertTrue(any("hotlinked external image" in e for e in r.errors))

    def test_data_uri_image_is_ok(self):
        r = new_result()
        vt.check_external_dependencies(
            '<img src="data:image/png;base64,AAAA">', r, Path("x.html"))
        self.assertEqual(r.errors, [])

    def test_cdn_is_warning(self):
        r = new_result()
        vt.check_external_dependencies(
            '<link href="https://cdn.jsdelivr.net/x.css">', r, Path("x.html"))
        self.assertTrue(any("CDN" in w for w in r.warnings))
        self.assertEqual(r.errors, [])


class GoPhishVariableChecks(unittest.TestCase):
    def test_missing_required_vars_error(self):
        r = new_result()
        vt.check_gophish_variables("<p>no vars</p>", r, is_education=False)
        self.assertTrue(any("{{.URL}}" in e for e in r.errors))
        self.assertTrue(any("{{.Tracker}}" in e for e in r.errors))

    def test_typo_detected(self):
        r = new_result()
        vt.check_gophish_variables("{{.URL}} {{.Tracker}} {{.url}}", r, is_education=False)
        self.assertTrue(any("Typo" in e for e in r.errors))

    def test_education_pages_skip_var_check(self):
        r = new_result()
        vt.check_gophish_variables("<p>no vars</p>", r, is_education=True)
        self.assertEqual(r.errors, [])


class HTMLStructureChecks(unittest.TestCase):
    def test_missing_viewport_is_error(self):
        r = new_result()
        vt.check_html_structure(
            "<!DOCTYPE html><html><head></head><body>x</body></html>", r)
        self.assertTrue(any("viewport" in e for e in r.errors))

    def test_good_structure_no_errors(self):
        r = new_result()
        vt.check_html_structure(GOOD_HTML, r)
        self.assertEqual(r.errors, [])


class AccessibilityChecks(unittest.TestCase):
    def test_missing_lang_warns(self):
        r = new_result()
        vt.check_accessibility("<html><body></body></html>", r)
        self.assertTrue(any("lang" in w for w in r.warnings))

    def test_lang_present_no_warning(self):
        r = new_result()
        vt.check_accessibility('<html lang="en"><body></body></html>', r)
        self.assertFalse(any("lang" in w for w in r.warnings))

    def test_img_without_alt_warns(self):
        r = new_result()
        vt.check_accessibility('<html lang="en"><img src="x.png"></html>', r)
        self.assertTrue(any("alt" in w for w in r.warnings))

    def test_img_with_alt_ok(self):
        r = new_result()
        vt.check_accessibility('<html lang="en"><img src="x.png" alt="logo"></html>', r)
        self.assertFalse(any("alt" in w for w in r.warnings))

    def test_empty_link_warns_but_image_link_ok(self):
        r = new_result()
        vt.check_accessibility('<html lang="en"><a href="#"></a></html>', r)
        self.assertTrue(any("aria-label" in w or "no text" in w for w in r.warnings))
        r2 = new_result()
        vt.check_accessibility('<html lang="en"><a href="#"><img src="x" alt="y"></a></html>', r2)
        self.assertFalse(any("no text" in w for w in r2.warnings))


class EmailCompatChecks(unittest.TestCase):
    def test_flex_is_info_not_warning(self):
        r = new_result()
        vt.check_email_compatibility('<div style="display:flex"></div>', r)
        self.assertEqual(r.warnings, [])
        self.assertTrue(any("flex" in i for i in r.info))

    def test_external_stylesheet_warns(self):
        r = new_result()
        vt.check_email_compatibility('<link rel="stylesheet" href="x.css">', r)
        self.assertTrue(any("stylesheet" in w for w in r.warnings))


class ClickRatePattern(unittest.TestCase):
    def test_valid_ranges(self):
        for ok in ("40-60%", "5-10%", "100-100%"):
            self.assertIsNotNone(vt.CLICK_RATE_PATTERN.match(ok), ok)

    def test_invalid_ranges(self):
        for bad in ("40 to 60", "40-60", "60%", "high"):
            self.assertIsNone(vt.CLICK_RATE_PATTERN.match(bad), bad)


class RelToRoot(unittest.TestCase):
    def test_outside_repo_falls_back(self):
        p = Path("/definitely/not/in/the/repo/x.html")
        self.assertEqual(vt.rel_to_root(p), str(p))

    def test_inside_repo_is_relative(self):
        p = vt.ROOT / "tools" / "validate_templates.py"
        self.assertEqual(vt.rel_to_root(p), "tools/validate_templates.py")


class MetadataSchemaChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        (self.dir / "good.html").write_text(GOOD_HTML)

    def tearDown(self):
        self.tmp.cleanup()

    def _write_meta(self, meta):
        (self.dir / "metadata.json").write_text(json.dumps(meta))

    def _good_entry(self, **over):
        entry = {
            "filename": "good.html", "name": "Good", "attack_vector": "credential_harvest",
            "difficulty": "intermediate", "estimated_click_rate": "40-60%",
            "gophish_variables": ["{{.URL}}", "{{.Tracker}}"],
            "suggested_subject_lines": ["a", "b"], "education_page": "education/e.html",
            "tags": ["t"], "notes": "n",
        }
        entry.update(over)
        return entry

    def test_good_metadata_passes(self):
        self._write_meta({"category": self.dir.name, "description": "d",
                          "gophish_version_tested": "0.12.1", "last_updated": "2026-01-01",
                          "templates": [self._good_entry()]})
        r = new_result()
        vt.check_metadata(self.dir / "good.html", r)
        self.assertEqual(r.errors, [])

    def test_bad_enums_and_format_are_errors(self):
        self._write_meta({"templates": [self._good_entry(
            attack_vector="phishing", difficulty="hard", estimated_click_rate="lots")]})
        r = new_result()
        vt.check_metadata(self.dir / "good.html", r)
        self.assertTrue(any("attack_vector" in e for e in r.errors))
        self.assertTrue(any("difficulty" in e for e in r.errors))
        self.assertTrue(any("estimated_click_rate" in e for e in r.errors))

    def test_missing_tracker_in_vars_is_error(self):
        self._write_meta({"templates": [self._good_entry(gophish_variables=["{{.URL}}"])]})
        r = new_result()
        vt.check_metadata(self.dir / "good.html", r)
        self.assertTrue(any("{{.Tracker}}" in e for e in r.errors))

    def test_missing_notes_is_warning_not_error(self):
        entry = self._good_entry()
        del entry["notes"]
        self._write_meta({"templates": [entry]})
        r = new_result()
        vt.check_metadata(self.dir / "good.html", r)
        self.assertEqual(r.errors, [])
        self.assertTrue(any("notes" in w for w in r.warnings))

    def test_orphan_and_duplicate_detected(self):
        self._write_meta({"category": self.dir.name,
                          "templates": [self._good_entry(),
                                        self._good_entry(),  # duplicate filename
                                        self._good_entry(filename="ghost.html")]})
        r = vt.validate_metadata_file(self.dir / "metadata.json")
        self.assertTrue(any("Duplicate" in e for e in r.errors))
        self.assertTrue(any("does not exist" in e for e in r.errors))

    def test_category_mismatch_is_warning(self):
        self._write_meta({"category": "somethingelse",
                          "templates": [self._good_entry()]})
        r = vt.validate_metadata_file(self.dir / "metadata.json")
        self.assertTrue(any("directory" in w for w in r.warnings))


if __name__ == "__main__":
    unittest.main()
