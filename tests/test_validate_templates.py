import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _loader import load_tool, TOOLS

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

    def test_recommended_var_warned_without_declared_vars(self):
        # Without metadata context, missing {{.Email}} produces a warning.
        r = new_result()
        vt.check_gophish_variables("{{.URL}} {{.Tracker}}", r, is_education=False)
        self.assertTrue(any("{{.Email}}" in w for w in r.warnings))

    def test_recommended_var_suppressed_when_not_in_declared_vars(self):
        # Smishing / SMS templates intentionally omit {{.Email}}; if metadata
        # declares gophish_variables without {{.Email}}, no warning should fire.
        r = new_result()
        declared = {"{{.FirstName}}", "{{.URL}}", "{{.Tracker}}"}
        vt.check_gophish_variables("{{.URL}} {{.Tracker}}", r,
                                   is_education=False, declared_vars=declared)
        self.assertFalse(any("{{.Email}}" in w for w in r.warnings))

    def test_recommended_var_still_warned_when_in_declared_vars_but_missing(self):
        # If metadata says {{.Email}} should be used but the template omits it, warn.
        r = new_result()
        declared = {"{{.FirstName}}", "{{.Email}}", "{{.URL}}", "{{.Tracker}}"}
        vt.check_gophish_variables("{{.URL}} {{.Tracker}}", r,
                                   is_education=False, declared_vars=declared)
        self.assertTrue(any("{{.Email}}" in w for w in r.warnings))


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

    def test_missing_doctype_warns(self):
        r = new_result()
        vt.check_html_structure(
            "<html><head><title>t</title></head><body>x</body></html>", r)
        self.assertTrue(any("DOCTYPE" in w for w in r.warnings))

    def test_missing_title_warns(self):
        r = new_result()
        vt.check_html_structure(
            "<!DOCTYPE html><html><head></head><body>x</body></html>", r)
        self.assertTrue(any("Missing <title>" in w for w in r.warnings))

    def test_empty_title_warns(self):
        r = new_result()
        vt.check_html_structure(
            "<!DOCTYPE html><html><head><title></title></head><body>x</body></html>", r)
        self.assertTrue(any("empty" in w for w in r.warnings))

    def test_missing_body_is_error(self):
        r = new_result()
        vt.check_html_structure("<!DOCTYPE html><html><head><title>t</title></head></html>", r)
        self.assertTrue(any("<body>" in e for e in r.errors))


class FormActionSafetyChecks(unittest.TestCase):
    def test_empty_action_is_ok(self):
        r = new_result()
        vt.check_form_action_safety('<form method="POST" action="">x</form>', r)
        self.assertEqual(r.errors, [])
        self.assertEqual(r.warnings, [])

    def test_hash_action_is_ok(self):
        r = new_result()
        vt.check_form_action_safety('<form action="#">x</form>', r)
        self.assertEqual(r.errors, [])

    def test_no_action_attribute_is_ok(self):
        r = new_result()
        vt.check_form_action_safety('<form method="POST">x</form>', r)
        self.assertEqual(r.errors, [])

    def test_external_absolute_url_is_error(self):
        r = new_result()
        vt.check_form_action_safety(
            '<form method="POST" action="https://evil.example.com/collect">x</form>', r)
        self.assertTrue(any("external host" in e for e in r.errors))

    def test_protocol_relative_url_is_error(self):
        r = new_result()
        vt.check_form_action_safety('<form action="//evil.example.com/collect">x</form>', r)
        self.assertTrue(any("external host" in e for e in r.errors))

    def test_relative_path_action_is_warning_not_error(self):
        r = new_result()
        vt.check_form_action_safety('<form action="/submit">x</form>', r)
        self.assertEqual(r.errors, [])
        self.assertTrue(any("non-empty" in w for w in r.warnings))


class LandingPageDiscoveryChecks(unittest.TestCase):
    def test_finds_html_files_in_landing_pages_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "landing-pages").mkdir()
            (base / "landing-pages" / "a.html").write_text(GOOD_HTML)
            (base / "landing-pages" / "b.html").write_text(GOOD_HTML)
            found = vt.find_landing_pages(base)
            self.assertEqual([p.name for p in found], ["a.html", "b.html"])

    def test_missing_landing_pages_dir_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(vt.find_landing_pages(Path(tmp)), [])

    def test_validate_landing_page_catches_external_form_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "landing-pages").mkdir()
            page = base / "landing-pages" / "bad.html"
            page.write_text(
                '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
                '<title>t</title></head><body>'
                '<form method="POST" action="https://evil.example.com/collect">'
                '<input name="username"></form></body></html>'
            )
            result = vt.validate_landing_page(page)
            self.assertFalse(result.passed)
            self.assertTrue(any("external host" in e for e in result.errors))


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


class TrackerPlacementChecks(unittest.TestCase):
    def test_no_tracker_is_noop(self):
        r = new_result()
        vt.check_tracker_placement("<body>no tracker here</body>", r, is_education=False)
        self.assertEqual(r.warnings, [])
        self.assertEqual(r.info, [])

    def test_education_page_skips_check(self):
        r = new_result()
        vt.check_tracker_placement(
            "<body>{{.Tracker}}</body></html>garbage after", r, is_education=True)
        self.assertEqual(r.warnings, [])

    def test_tracker_after_body_close_warns(self):
        r = new_result()
        vt.check_tracker_placement(
            "<html><body>hi</body></html>{{.Tracker}}", r, is_education=False)
        self.assertTrue(any("after </body>" in w for w in r.warnings))

    def test_tracker_inside_body_no_placement_warning(self):
        r = new_result()
        vt.check_tracker_placement(
            '<html><body>hi<div style="display:none">{{.Tracker}}</div></body></html>',
            r, is_education=False)
        self.assertFalse(any("after </body>" in w for w in r.warnings))

    def test_hidden_tracker_no_info_note(self):
        r = new_result()
        vt.check_tracker_placement(
            '<div style="display:none">{{.Tracker}}</div>', r, is_education=False)
        self.assertEqual(r.info, [])

    def test_visible_tracker_adds_info_note(self):
        r = new_result()
        vt.check_tracker_placement("<div>{{.Tracker}}</div>", r, is_education=False)
        self.assertTrue(any("not wrapped in a hidden element" in i for i in r.info))


class FileSizeChecks(unittest.TestCase):
    def test_small_file_no_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "small.html"
            f.write_text("<html></html>")
            r = new_result()
            vt.check_file_size(f, r)
            self.assertEqual(r.warnings, [])
            self.assertTrue(any("File size" in i for i in r.info))

    def test_large_file_warns(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "big.html"
            f.write_text("x" * (501 * 1024))
            r = new_result()
            vt.check_file_size(f, r)
            self.assertTrue(any("KB" in w for w in r.warnings))


class EducationPageChecks(unittest.TestCase):
    def test_missing_education_dir_warns(self):
        with tempfile.TemporaryDirectory() as tmp:
            category = Path(tmp) / "it-security"
            category.mkdir()
            template = category / "phish.html"
            template.write_text(GOOD_HTML)
            r = new_result()
            vt.check_education_page(template, r)
            self.assertTrue(any("No education/ directory" in w for w in r.warnings))

    def test_empty_education_dir_warns(self):
        with tempfile.TemporaryDirectory() as tmp:
            category = Path(tmp) / "it-security"
            (category / "education").mkdir(parents=True)
            template = category / "phish.html"
            template.write_text(GOOD_HTML)
            r = new_result()
            vt.check_education_page(template, r)
            self.assertTrue(any("no HTML files" in w for w in r.warnings))

    def test_populated_education_dir_no_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            category = Path(tmp) / "it-security"
            (category / "education").mkdir(parents=True)
            (category / "education" / "edu.html").write_text(GOOD_HTML)
            template = category / "phish.html"
            template.write_text(GOOD_HTML)
            r = new_result()
            vt.check_education_page(template, r)
            self.assertEqual(r.warnings, [])


class MetadataVariableChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.template = self.dir / "phish.html"

    def tearDown(self):
        self.tmp.cleanup()

    def _write_meta(self, gophish_variables):
        (self.dir / "metadata.json").write_text(json.dumps({
            "templates": [{"filename": "phish.html", "gophish_variables": gophish_variables}]
        }))

    def test_no_metadata_file_is_noop(self):
        r = new_result()
        vt.check_metadata_variables("{{.URL}} {{.Tracker}}", self.template, r)
        self.assertEqual(r.warnings, [])

    def test_used_but_undeclared_known_var_warns(self):
        self._write_meta(["{{.URL}}", "{{.Tracker}}"])
        r = new_result()
        vt.check_metadata_variables("{{.URL}} {{.Tracker}} {{.FirstName}}", self.template, r)
        self.assertTrue(any("{{.FirstName}}" in w and "not listed" in w for w in r.warnings))

    def test_used_unknown_var_warns_differently(self):
        self._write_meta(["{{.URL}}", "{{.Tracker}}"])
        r = new_result()
        vt.check_metadata_variables("{{.URL}} {{.Tracker}} {{.Bogus}}", self.template, r)
        self.assertTrue(any("not a standard GoPhish variable" in w for w in r.warnings))

    def test_declared_but_unused_var_warns(self):
        self._write_meta(["{{.URL}}", "{{.Tracker}}", "{{.Email}}"])
        r = new_result()
        vt.check_metadata_variables("{{.URL}} {{.Tracker}}", self.template, r)
        self.assertTrue(any("not used in the template" in w for w in r.warnings))

    def test_exact_match_no_warnings(self):
        self._write_meta(["{{.URL}}", "{{.Tracker}}", "{{.FirstName}}"])
        r = new_result()
        vt.check_metadata_variables("{{.URL}} {{.Tracker}} {{.FirstName}}", self.template, r)
        self.assertEqual(r.warnings, [])


class DiscoveryHelperChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "it-security").mkdir()
        (self.root / "it-security" / "phish.html").write_text(GOOD_HTML)
        (self.root / "it-security" / "metadata.json").write_text(json.dumps({
            "category": "it-security", "templates": [{"filename": "phish.html"}]}))
        (self.root / "tools").mkdir()
        (self.root / "tools" / "helper.html").write_text(GOOD_HTML)
        (self.root / "landing-pages").mkdir()
        (self.root / "landing-pages" / "lp.html").write_text(GOOD_HTML)

    def tearDown(self):
        self.tmp.cleanup()

    def test_find_templates_skips_excluded_dirs(self):
        found = [p.name for p in vt.find_templates(self.root)]
        self.assertIn("phish.html", found)
        self.assertNotIn("helper.html", found)
        self.assertNotIn("lp.html", found)

    def test_find_metadata_files_skips_excluded_dirs(self):
        found = vt.find_metadata_files(self.root)
        self.assertEqual([p.parent.name for p in found], ["it-security"])


class ValidateFileIntegration(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.category = self.root / "it-security"
        (self.category / "education").mkdir(parents=True)
        (self.category / "education" / "edu.html").write_text(GOOD_HTML)
        self.template = self.category / "phish.html"
        self.template.write_text(GOOD_HTML)
        (self.category / "metadata.json").write_text(json.dumps({
            "category": "it-security",
            "templates": [{
                "filename": "phish.html", "name": "Phish", "attack_vector": "credential_harvest",
                "difficulty": "intermediate", "estimated_click_rate": "40-60%",
                "gophish_variables": ["{{.URL}}", "{{.Tracker}}", "{{.FirstName}}", "{{.Email}}"],
                "suggested_subject_lines": ["a"], "education_page": "education/edu.html",
                "tags": ["t"], "notes": "n",
            }],
        }))

    def tearDown(self):
        self.tmp.cleanup()

    def test_well_formed_template_passes_full_pipeline(self):
        result = vt.validate_file(self.template)
        self.assertEqual(result.errors, [])

    def test_education_page_skips_companion_checks(self):
        edu_path = self.category / "education" / "edu.html"
        result = vt.validate_file(edu_path)
        self.assertEqual(result.errors, [])
        self.assertFalse(any("education" in w.lower() for w in result.warnings))


class CLIChecks(unittest.TestCase):
    """End-to-end checks of the command-line entry point."""

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, str(TOOLS / "validate_templates.py"), *args],
            capture_output=True, text=True)

    def test_json_output_is_parseable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            f = root / "phish.html"
            f.write_text(GOOD_HTML)
            proc = self._run("--dir", str(root), "--json")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            data = json.loads(proc.stdout)
            self.assertEqual(len(data), 1)
            self.assertTrue(data[0]["passed"])

    def test_strict_mode_fails_on_warnings_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            f = root / "phish.html"
            # Valid enough to avoid errors, but missing recommended {{.Email}} → warning.
            f.write_text(GOOD_HTML.replace("{{.Email}}", ""))
            lenient = self._run("--dir", str(root), "--json")
            self.assertEqual(lenient.returncode, 0, lenient.stdout + lenient.stderr)
            strict = self._run("--dir", str(root), "--json", "--strict")
            self.assertEqual(strict.returncode, 1, strict.stdout + strict.stderr)

    def test_no_templates_found_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = self._run("--dir", tmp)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


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
