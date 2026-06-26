import unittest
import sys
import tempfile
import subprocess
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

try:
    import generate_catalog
except ImportError as e:
    generate_catalog = None
    import_error = e

class TestGenerateCatalog(unittest.TestCase):
    def test_import(self):
        self.assertIsNotNone(generate_catalog, f"Failed to import generate_catalog: {import_error if 'import_error' in locals() else 'Unknown error'}")

    def test_help_command(self):
        script_path = ROOT / "tools" / "generate_catalog.py"
        result = subprocess.run(
            [sys.executable, str(script_path), "--help"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Generate CATALOG.md template catalog", result.stdout)

    def test_catalog_generation(self):
        self.assertIsNotNone(generate_catalog, "generate_catalog module is not imported")
        
        # We test the generate_catalog_markdown helper function
        mock_categories = [
            {
                "dir": "mock-cat",
                "name": "Mock Category",
                "description": "Mock description.",
                "industry": "Mock Industry",
                "templates": [
                    {
                        "filename": "mock_template.html",
                        "name": "Mock Template",
                        "difficulty": "beginner",
                        "attack_vector": "credential_harvest",
                        "estimated_click_rate": "10-20%",
                        "education_page": "education/mock_education.html"
                    }
                ]
            }
        ]
        markdown = generate_catalog.generate_catalog_markdown(mock_categories)
        self.assertIn("# GoPhish Phishing Template Catalog", markdown)
        self.assertIn("## Mock Category", markdown)
        self.assertIn("🟢 beginner", markdown)
        self.assertIn("Credential Harvest", markdown)
        self.assertIn("[mock_template.html](mock-cat/mock_template.html)", markdown)
        self.assertIn("[Education](mock-cat/education/mock_education.html)", markdown)

if __name__ == "__main__":
    unittest.main()
