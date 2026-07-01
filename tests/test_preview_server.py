import json
import tempfile
import unittest
from pathlib import Path

from _loader import load_tool

ps = load_tool("preview_server")


class SafeJoin(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "it-security").mkdir(parents=True)
        (self.root / "it-security" / "phish.html").write_text("<html></html>")

    def tearDown(self):
        self.tmp.cleanup()

    def test_allows_path_inside_root(self):
        result = ps.safe_join(self.root, "it-security/phish.html")
        self.assertEqual(result, (self.root / "it-security" / "phish.html").resolve())

    def test_rejects_dotdot_traversal(self):
        self.assertIsNone(ps.safe_join(self.root, "../../../../etc/passwd"))

    def test_rejects_encoded_dotdot_traversal_after_unquote(self):
        # do_GET runs urllib.parse.unquote() before calling safe_join, so the
        # path arrives here already decoded — simulate that.
        self.assertIsNone(ps.safe_join(self.root, "it-security/../../../../etc/passwd"))

    def test_rejects_absolute_path_escaping_root(self):
        self.assertIsNone(ps.safe_join(self.root, "/etc/passwd"))


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
