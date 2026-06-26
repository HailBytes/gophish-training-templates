import unittest
import sys
import subprocess
import ast
from pathlib import Path

ROOT = Path(__file__).parent.parent

class TestImportToGoPhish(unittest.TestCase):
    def test_help_exit_code(self):
        script_path = ROOT / "tools" / "import_to_gophish.py"
        result = subprocess.run(
            [sys.executable, str(script_path), "--help"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0, f"Script failed with code {result.returncode}. Output: {result.stderr}")
        self.assertIn("GoPhish Template Importer", result.stdout)

    def test_no_requests_import(self):
        script_path = ROOT / "tools" / "import_to_gophish.py"
        with open(script_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
            
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    self.assertNotEqual(name.name, "requests", "import_to_gophish.py imports forbidden module 'requests'")
            elif isinstance(node, ast.ImportFrom):
                self.assertNotEqual(node.module, "requests", "import_to_gophish.py imports from forbidden module 'requests'")

if __name__ == "__main__":
    unittest.main()
