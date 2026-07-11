import json
import tempfile
import unittest
from pathlib import Path

from _loader import load_tool

ps = load_tool("preview_server")


class SubstituteVars(unittest.TestCase):
    def test_replaces_known_vars(self):
        out = ps.substitute_gophish_vars("Hi {{.FirstName}}", {"FirstName": "Dana"})
        self.assertIn("Hi Dana", out)

    def test_highlights_unsubstituted_vars(self):
        out = ps.substitute_gophish_vars("Go {{.URL}}", {"FirstName": "Dana"})
        self.assertIn("<mark", out)
        self.assertIn("{{.URL}}", out)


class GetAllTemplates(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "it-security" / "education").mkdir(parents=True)
        (self.root / "it-security" / "phish.html").write_text("<html></html>")
        (self.root / "it-security" / "education" / "edu.html").write_text("<html></html>")
        (self.root / "it-security" / "metadata.json").write_text(json.dumps({
            "templates": [{"filename": "phish.html", "name": "Phish Me",
                           "difficulty": "advanced", "attack_vector": "credential_harvest",
                           "estimated_click_rate": "40-60%", "tags": ["x"]}]
        }))

    def tearDown(self):
        self.tmp.cleanup()

    def test_discovers_and_enriches_from_metadata(self):
        templates = ps.get_all_templates(self.root)
        by_name = {t["filename"]: t for t in templates}
        self.assertEqual(by_name["phish.html"]["name"], "Phish Me")
        self.assertEqual(by_name["phish.html"]["difficulty"], "advanced")
        self.assertFalse(by_name["phish.html"]["is_education"])
        self.assertTrue(by_name["edu.html"]["is_education"])

    def test_render_gallery_smoke(self):
        templates = ps.get_all_templates(self.root)
        html = ps.render_gallery(templates, {"FirstName": "Dana"})
        self.assertIn("<html", html.lower())
        self.assertIn("Phish Me", html)


class ResolveSafePath(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "it-security").mkdir(parents=True)
        (self.root / "it-security" / "phish.html").write_text("<html></html>")
        (self.root.parent / "outside.txt").write_text("secret")
        self._orig_root = ps.ROOT
        ps.ROOT = self.root

    def tearDown(self):
        ps.ROOT = self._orig_root
        Path(self.root.parent / "outside.txt").unlink(missing_ok=True)
        self.tmp.cleanup()

    def _handler(self):
        return ps.PreviewHandler.__new__(ps.PreviewHandler)

    def test_rejects_parent_traversal(self):
        handler = self._handler()
        self.assertIsNone(handler.resolve_safe_path("../outside.txt"))

    def test_rejects_encoded_traversal(self):
        handler = self._handler()
        self.assertIsNone(handler.resolve_safe_path("../../../../../../etc/passwd"))

    def test_allows_file_within_root(self):
        handler = self._handler()
        resolved = handler.resolve_safe_path("it-security/phish.html")
        self.assertEqual(resolved, (self.root / "it-security" / "phish.html").resolve())


class ServerCanBind(unittest.TestCase):
    def test_handler_class_and_bind(self):
        from http.server import HTTPServer
        server = HTTPServer(("127.0.0.1", 0), ps.PreviewHandler)
        try:
            self.assertGreater(server.server_address[1], 0)
        finally:
            server.server_close()


if __name__ == "__main__":
    unittest.main()
