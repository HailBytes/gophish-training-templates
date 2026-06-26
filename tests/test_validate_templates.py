import unittest
import sys
import tempfile
import json
from pathlib import Path

# Ensure repo root and tools directory are in sys.path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import validate_templates
from validate_templates import (
    ValidationResult,
    check_html_structure,
    check_gophish_variables,
    check_external_dependencies,
    check_tracker_placement,
    check_metadata,
)

class TestValidateTemplates(unittest.TestCase):
    def setUp(self):
        self.result = ValidationResult(path="test_template.html")

    def test_valid_template(self):
        content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Valid Template</title>
</head>
<body>
    <p>Hello {{.FirstName}} ({{.Email}}),</p>
    <p>Please click here: <a href="{{.URL}}">link</a></p>
    {{.Tracker}}
</body>
</html>"""
        check_html_structure(content, self.result)
        check_gophish_variables(content, self.result, is_education=False)
        check_external_dependencies(content, self.result, Path("test_template.html"))
        check_tracker_placement(content, self.result, is_education=False)
        
        self.assertEqual(len(self.result.errors), 0, f"Errors found: {self.result.errors}")
        self.assertEqual(len(self.result.warnings), 0, f"Warnings found: {self.result.warnings}")

    def test_external_image_hotlinks(self):
        # Case 1: External hotlink (should trigger error)
        content_hotlink = '<img src="https://example.com/logo.png" alt="logo">'
        check_external_dependencies(content_hotlink, self.result, Path("test_template.html"))
        self.assertTrue(any("hotlinked external image" in err for err in self.result.errors))

        # Reset result
        self.result = ValidationResult(path="test_template.html")
        
        # Case 2: Inline data URI image (should NOT trigger error)
        content_inline = '<img src="data:image/png;base64,iVBORw0KGgoAAAANS" alt="logo">'
        check_external_dependencies(content_inline, self.result, Path("test_template.html"))
        self.assertEqual(len(self.result.errors), 0)

    def test_missing_tracker(self):
        # Missing {{.Tracker}} should trigger error
        content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>No Tracker</title>
</head>
<body>
    <p>Hello {{.FirstName}}, please click: <a href="{{.URL}}">link</a></p>
</body>
</html>"""
        check_gophish_variables(content, self.result, is_education=False)
        self.assertTrue(any("Missing required GoPhish variable: {{.Tracker}}" in err for err in self.result.errors))

    def test_missing_viewport(self):
        # Missing viewport should trigger warning
        content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>No Viewport</title>
</head>
<body>
    <p>Hello</p>
</body>
</html>"""
        check_html_structure(content, self.result)
        self.assertTrue(any("Missing <meta name='viewport'> tag" in err for err in self.result.errors))
        # Ensure it is not a warning
        self.assertEqual(len(self.result.warnings), 0)

    def test_metadata_validation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            template_path = tmpdir_path / "test_template.html"
            metadata_path = tmpdir_path / "metadata.json"

            # Case 1: Missing metadata.json
            self.result = ValidationResult(path=str(template_path))
            check_metadata(template_path, self.result)
            self.assertTrue(any("No metadata.json found" in warn for warn in self.result.warnings))

            # Case 2: Invalid JSON metadata
            self.result = ValidationResult(path=str(template_path))
            metadata_path.write_text("invalid json")
            check_metadata(template_path, self.result)
            self.assertTrue(any("metadata.json is invalid JSON" in err for err in self.result.errors))

            # Case 3: Missing fields inside metadata.json
            self.result = ValidationResult(path=str(template_path))
            meta_data = {
                "templates": [
                    {
                        "filename": "test_template.html",
                        "name": "",  # missing name
                        "difficulty": "expert"  # invalid difficulty
                    }
                ]
            }
            metadata_path.write_text(json.dumps(meta_data))
            check_metadata(template_path, self.result)
            self.assertTrue(any("metadata.json missing 'name'" in warn for warn in self.result.warnings))
            self.assertTrue(any("Invalid difficulty" in err for err in self.result.errors))

if __name__ == "__main__":
    unittest.main()
